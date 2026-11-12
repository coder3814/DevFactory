"""Shared by the DevFactory hooks; holds no hook itself. The profile and the markers are read
through the plugin's script (`profile`, `markers`), so the hooks parse neither themselves."""

import base64
import json
import os
import re
import subprocess
import sys

SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'devfactory.py'))
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def rx(pattern, flags=0):
    # ASCII semantics for \d, \w and \b, as in JavaScript.
    return re.compile(pattern, flags | re.ASCII)


class Result:
    """A finished process: error is set when it could not be started or timed out."""

    def __init__(self, status=None, stdout='', stderr='', error=None):
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.error = error


def run(args, cwd=None, timeout=None):
    try:
        r = subprocess.run(args, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=timeout, creationflags=NO_WINDOW)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        return Result(error=e)
    return Result(r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace'))


def read_input():
    return json.loads(sys.stdin.buffer.read().decode('utf-8'))


MSYS_DRIVE = rx(r'^/(?:cygdrive/)?([A-Za-z])(?=/|\Z)')


def canonical(base, p=None):
    """One absolute form for a path a command names, resolved against base: on Windows an
    MSYS or Git Bash drive path (/c/x) or a Cygwin one (/cygdrive/c/x) becomes C:\\x, either
    slash is accepted, and the result is absolute, so the same directory resolves to the same
    repository however a command spelled it; Windows matches its case without regard to it."""
    path = base if p is None else p
    if p is not None and p.startswith('~'):
        path = os.path.expanduser(p)
    if os.name == 'nt':
        path = path.replace('\\', '/')
        path = MSYS_DRIVE.sub(lambda m: m.group(1).upper() + ':', path, count=1)
        if re.match(r'^[A-Za-z]:\Z', path):
            path += '/'
    if p is not None and base is not None:
        path = os.path.join(canonical(base), path)
    return os.path.abspath(path)


def input_cwd(data):
    cwd = data.get('cwd') if isinstance(data, dict) else None
    return canonical(cwd or os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())


def git_toplevel(d, options=()):
    """The work-tree root git reports for a directory and any --git-dir or --work-tree
    options, in canonical form, or '' when git finds no work tree there."""
    if not os.path.isdir(d):
        return ''
    r = run(['git'] + list(options) + ['rev-parse', '--show-toplevel'], cwd=d, timeout=5)
    top = (r.stdout or '').strip() if r.error is None and r.status == 0 else ''
    return canonical(top) if top else ''


def project_root(d):
    """The repository root of a directory (a worktree's own root), else the directory itself."""
    return git_toplevel(d) or canonical(d)


def has_profile(root):
    return os.path.exists(os.path.join(root, '.devfactory', 'profile.md'))


def script(root, args, timeout=5):
    return run([sys.executable, SCRIPT] + list(args), cwd=root, timeout=timeout)


def profile_field(root, section, field):
    """One profile field's value, or None when the profile, the section or the field is missing."""
    r = script(root, ['profile', '--section', section, '--field', field])
    return re.sub(r'\r?\n\Z', '', r.stdout or '', count=1) if r.error is None and r.status == 0 else None


def profile_section(root, section):
    """One profile section's lines, or None."""
    r = script(root, ['profile', '--section', section])
    return re.split(r'\r?\n', r.stdout or '') if r.error is None and r.status == 0 else None


def hook_off(root, name):
    """A hook is on unless its line under Hooks says off."""
    value = profile_field(root, 'Hooks', name)
    return value is not None and bool(rx(r'^`?off\b', re.I).search(value.strip()))


def markers(root):
    """The markers in a root, as {name, stale, line} from the script's `markers` listing."""
    r = script(root, ['markers'])
    if r.error is not None or r.status != 0:
        return []
    out = []
    for line in re.split(r'\r?\n', r.stdout or ''):
        m = rx(r'^(active|stale) (\S+) ').search(line)
        if m:
            out.append({'name': m.group(2), 'stale': m.group(1) == 'stale', 'line': line})
    return out


def first_token(value):
    """The first backticked token of a profile value, else its first word."""
    if not value:
        return ''
    ticked = re.search(r'`([^`]+)`', value)
    if ticked:
        return ticked.group(1).strip()
    words = value.split()
    return (words[0] if words else '').strip()


SHELL_TOOLS = ('Bash', 'PowerShell')


def shell_of(data):
    """The shell a tool's command is written for: 'powershell' for the PowerShell tool, else 'bash'."""
    return 'powershell' if data.get('tool_name') == 'PowerShell' else 'bash'


SEPARATORS = {'bash': ';&|()\n\r', 'powershell': ';&|(){}\n\r'}
# A join after which the next segment need not run after this one has finished and succeeded.
BROKEN_JOINS = {'||', '|', '&'}
ENCODED = rx(r'(?:^|\s)-e[A-Za-z]*\s', re.I)


def split(command, shell='bash'):
    """Splits a command line into segments at its unquoted separators, as [words, join] pairs.
    Bash separates at ; & | ( ) and newlines, and its words honour single and double quotes
    and backslash escapes. PowerShell also separates at { and }, and its words honour single
    quotes (with '' inside), double quotes and the backtick escape, a backslash being an
    ordinary character. join is the separator that ends the segment: &&, ||, ;, a newline,
    |, &, a bracket, or '' at the end. An & next to > or < is a redirection, not a separator."""
    ps = shell == 'powershell'
    seps = SEPARATORS['powershell' if ps else 'bash']
    escape = '`' if ps else '\\'
    result = []
    words = []
    word = ''
    in_word = False
    quote = None
    i = 0
    n = len(command)

    def at(k):
        return command[k] if 0 <= k < n else ''
    while i < n:
        c = command[i]
        if quote:
            if c == quote == "'" and ps and at(i + 1) == "'":
                word += "'"
                i += 1
            elif c == quote == '"' and ps and at(i + 1) == '"':
                word += '"'
                i += 1
            elif c == quote:
                quote = None
            elif quote == '"' and ps and c == '`' and i + 1 < n:
                i += 1
                word += command[i]
            elif quote == '"' and not ps and c == '\\' and (at(i + 1) or '#') in '$`"\\':
                # Inside double quotes a backslash escapes only $ ` " and \, as in bash.
                i += 1
                word += command[i]
            else:
                word += c
            i += 1
            continue
        if c in ("'", '"'):
            quote = c
            in_word = True
        elif c == escape and i + 1 < n:
            i += 1
            if command[i] in '\r\n':
                # A line continuation joins the lines.
                if command[i] == '\r' and at(i + 1) == '\n':
                    i += 1
            else:
                word += command[i]
                in_word = True
        elif c == '&' and (at(i - 1) in ('<', '>') or at(i + 1) == '>'):
            word += c
            in_word = True
        elif c in seps:
            join = c
            if c in '&|' and at(i + 1) == c:
                join = c * 2
                i += 1
            elif c == '\r':
                join = '\n'
                if at(i + 1) == '\n':
                    i += 1
            if in_word:
                words.append(word)
            word, in_word = '', False
            if words:
                result.append([words, join])
            words = []
        elif c in ' \t':
            if in_word:
                words.append(word)
            word, in_word = '', False
        else:
            word += c
            in_word = True
        i += 1
    if in_word:
        words.append(word)
    if words:
        result.append([words, ''])
    return result


def segments(command, shell='bash'):
    """A command line's segments, each as its words (see split)."""
    return [words for words, _ in split(command, shell)]


def might_run(command, pattern):
    """Whether a command may run what the pattern names: it shows it, or carries an encoded
    PowerShell command, whose text the guard has to decode to see."""
    return bool(rx(pattern).search(command) or ENCODED.search(command))


WRAPPERS = {'command', 'exec', 'time', 'nohup', 'sudo', 'env', 'builtin'}
ASSIGNMENT = rx(r'^[A-Za-z_][A-Za-z0-9_]*=')


def command_words(words):
    """The words of a segment from its command token on: leading VAR=value assignments and
    wrappers such as env or sudo are dropped."""
    i = 0
    while i < len(words) and (ASSIGNMENT.search(words[i]) or words[i] in WRAPPERS):
        i += 1
    return words[i:]


def is_program(word, name):
    return bool(re.search(r'(^|[\\/])' + re.escape(name) + r'(\.exe)?\Z', word or '', re.I))


def word(words, i):
    return words[i] if 0 <= i < len(words) else None


# PowerShell parameters that take a value, by their full names; a prefix of one is that one.
PS_VALUE_PARAMETERS = ['-executionpolicy', '-inputformat', '-outputformat', '-windowstyle',
                       '-configurationname', '-workingdirectory', '-version', '-psconsolefile',
                       '-settingsfile', '-custompipename']
PS_VALUE_ALIASES = {'-ep', '-ex', '-if', '-of', '-w', '-wd', '-v'}


def inner_command(words):
    """The command a segment hands to another shell, as (command, shell), for `bash -c <cmd>`,
    `sh -c <cmd>`, and `powershell` or `pwsh` with -Command (or any prefix of it) or
    -EncodedCommand, whose base64 text is decoded; powershell without either runs its
    remaining words as a command. Else None."""
    prog = word(words, 0)
    if not prog:
        return None
    if is_program(prog, 'bash') or is_program(prog, 'sh'):
        i = 1
        has_c = False
        while i < len(words) and words[i][:1] in ('-', '+') and words[i] not in ('-', '--'):
            w = words[i]
            if w in ('-o', '+o', '-O', '+O'):
                i += 2
                continue
            if not w.startswith('--') and 'c' in w[1:]:
                has_c = True
            i += 1
        if words[i:i + 1] == ['--']:
            i += 1
        return (words[i], 'bash') if has_c and i < len(words) else None
    windows = is_program(prog, 'powershell')
    if not windows and not is_program(prog, 'pwsh'):
        return None
    i = 1
    while i < len(words):
        lw = words[i].lower()
        if not lw.startswith('-') or len(lw) < 2:
            return (' '.join(words[i:]), 'powershell') if windows else None
        if '-command'.startswith(lw):
            return (' '.join(words[i + 1:]), 'powershell')
        if lw in ('-e', '-ec') or (len(lw) >= 3 and '-encodedcommand'.startswith(lw)):
            try:
                return (base64.b64decode(word(words, i + 1) or '').decode('utf-16-le'), 'powershell')
            except Exception:
                return None
        if lw == '-f' or (len(lw) >= 3 and '-file'.startswith(lw)):
            return None  # a script file, whose content the guard does not read
        if lw in PS_VALUE_ALIASES or (len(lw) >= 3 and any(p.startswith(lw) for p in PS_VALUE_PARAMETERS)):
            i += 1
        i += 1
    return None


MAX_DEPTH = 4


def commands(command, shell='bash', depth=0):
    """A command line's segments in order, each as {words, join, inner}: words from the command
    token on (command_words), join the separator that ends it (see split), and inner the same
    list for the command it hands to another shell (inner_command), else None."""
    out = []
    for words, join in split(command, shell):
        w = command_words(words)
        nested = inner_command(w) if depth < MAX_DEPTH else None
        out.append({'words': w, 'join': join,
                    'inner': commands(nested[0], nested[1], depth + 1) if nested else None})
    return out


def flatten(items):
    """Every segment of commands() in the order they run, each followed by its inner ones."""
    for item in items:
        yield item
        if item['inner']:
            for inner in flatten(item['inner']):
                yield inner


PYTHON = rx(r'(^|[\\/])(python[0-9.]*|py)(\.exe)?\Z', re.I)
DEVFACTORY_SCRIPT = rx(r'(^|[\\/])devfactory\.py\Z', re.I)
SKILL_NAME = rx(r'[A-Za-z0-9._-]+')


def begun_skill(words):
    """The skill a segment begins, for `devfactory begin <skill>`, `<path>/devfactory.py begin
    <skill>` and `python [<options>] <path>/devfactory.py begin <skill>`, else None."""
    w = command_words(words)
    prog = word(w, 0) or ''
    i = None
    if is_program(prog, 'devfactory') or DEVFACTORY_SCRIPT.search(prog):
        i = 1
    elif PYTHON.search(prog):
        j = 1
        while j < len(w) and w[j].startswith('-'):
            j += 1
        if DEVFACTORY_SCRIPT.search(word(w, j) or ''):
            i = j + 1
    if i is None or word(w, i) != 'begin':
        return None
    name = word(w, i + 1)
    return name if name and SKILL_NAME.fullmatch(name) else None


def emit(text):
    sys.stdout.flush()
    sys.stdout.buffer.write(text.encode('utf-8', 'replace'))
    sys.stdout.buffer.flush()


def to_json(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def deny(reason):
    emit(to_json({
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': reason,
        },
    }))
