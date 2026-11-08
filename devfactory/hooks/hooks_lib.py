"""Shared by the DevFactory hooks; holds no hook itself. The profile and the markers are read
through the plugin's script (`profile`, `markers`), so the hooks parse neither themselves."""

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


def input_cwd(data):
    cwd = data.get('cwd') if isinstance(data, dict) else None
    return os.path.abspath(cwd or os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd())


def project_root(d):
    """The repository root of a directory (a worktree's own root), else the directory itself."""
    r = run(['git', 'rev-parse', '--show-toplevel'], cwd=d, timeout=5)
    top = (r.stdout or '').strip() if r.error is None and r.status == 0 else ''
    return os.path.abspath(top or d)


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


def segments(command):
    """Splits a command line into segments at unquoted ; & | ( ) and newlines, and each segment
    into words, honouring single and double quotes and backslash escapes."""
    result = []
    words = []
    word = ''
    in_word = False
    quote = None
    i = 0
    n = len(command)
    while i < n:
        c = command[i]
        if quote:
            if c == quote:
                quote = None
            elif c == '\\' and quote == '"' and (command[i + 1] if i + 1 < n else '#') in '$`"\\':
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
        elif c == '\\' and i + 1 < n:
            i += 1
            word += command[i]
            in_word = True
        elif c in ';&|()\n\r':
            if in_word:
                words.append(word)
            word, in_word = '', False
            if words:
                result.append(words)
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
        result.append(words)
    return result


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
