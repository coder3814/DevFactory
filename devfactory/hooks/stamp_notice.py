#!/usr/bin/env python3
"""UserPromptSubmit: for the first two cards the prompt names (#<n> or "card <n>") that have a
spec, runs stamp-check and says whether the spec is still current. Never blocks. Silent on a
missing profile, on "Stamp notice: off", on a card without a spec, on a spec whose Status is
drafting, on a spec with no Card revision yet, and on any error. When DEVFACTORY_STAMP_TEXT
is set, stamp-check reads the card from that file (--text) instead of the tracker, for tests.
"""

import os
import re
import sys

sys.dont_write_bytecode = True

try:
    import hooks_lib as lib
except Exception:
    sys.exit(0)

MAX_CARDS = 2
CHECK_TIMEOUT = 8


def card_numbers(prompt):
    found = []
    for m in lib.rx(r'(?:#|\bcard\s+#?)(\d+)\b', re.I).finditer(prompt):
        if m.group(1) not in found:
            found.append(m.group(1))
    return found


def header_value(spec_file, name):
    """One header row's value (`| **Name** | value |`), without backticks, or ''."""
    try:
        with open(spec_file, 'r', encoding='utf-8', errors='replace', newline='') as f:
            text = f.read()
        m = lib.rx(r'\|\s*\*\*' + re.escape(name) + r'\*\*\s*\|\s*([^|\r\n]*?)\s*\|').search(text)
        return m.group(1).replace('`', '').strip() if m else ''
    except Exception:
        return ''


def notice(root, specs_dir, card):
    d = os.path.join(specs_dir, card)
    spec_file = os.path.join(d, 'spec.md')
    if not os.path.exists(spec_file):
        return None
    if re.fullmatch(r'drafting', header_value(spec_file, 'Status'), re.I):
        return None  # nothing stamped yet
    text = os.environ.get('DEVFACTORY_STAMP_TEXT')
    source = ['--text', text] if text else ['--card', card]
    r = lib.script(root, ['stamp-check'] + source + ['--spec', d], CHECK_TIMEOUT)
    if r.error is not None:
        return None
    if r.status not in (0, 1):
        first = next((l for l in re.split(r'\r?\n', r.stderr or '') if l.strip()), 'the stamp check failed')
        why = re.sub(r'^devfactory:\s*', '', first, count=1)
        if 'has no Card revision hash' in why:
            return None  # not stamped yet: nothing to say
        return ("DevFactory: could not check card %s's spec against its stamp (%s); "
                'check it before building.' % (card, why))
    out = r.stdout or ''
    commit = header_value(spec_file, 'Repo commit')
    if r.status == 0 and lib.rx(r'^match\b', re.M).search(out):
        return "DevFactory: card %s's spec is current (Ready at %s)" % (card, commit or 'its stamped commit')
    if lib.rx(r'^changed\b', re.M).search(out):
        return ('DevFactory: card %s changed since its spec earned Ready; run grill '
                're-derive before building.' % card)
    if lib.rx(r'^not-ancestor\b', re.M).search(out):
        return ("DevFactory: card %s's spec was stamped at %s, which is "
                'not an ancestor of HEAD; run grill re-derive before building.' % (card, commit or 'a commit'))
    return None


def main():
    data = lib.read_input()
    if not isinstance(data, dict):
        return
    prompt = data.get('prompt')
    if not isinstance(prompt, str):
        return
    cards = card_numbers(prompt)
    if not cards:
        return
    root = lib.project_root(lib.input_cwd(data))
    if not lib.has_profile(root):
        return  # no profile: silence
    if lib.hook_off(root, 'Stamp notice'):
        return
    specs_dir = os.path.abspath(os.path.join(root, lib.first_token(lib.profile_field(root, 'Specs', 'Path')) or 'specs/'))
    lines = []
    checked = 0
    for card in cards:
        if checked >= MAX_CARDS:
            break
        if not os.path.exists(os.path.join(specs_dir, card, 'spec.md')):
            continue
        checked += 1
        try:
            line = notice(root, specs_dir, card)
            if line:
                lines.append(line)
        except Exception:
            pass  # skip this card
    if not lines:
        return
    lib.emit(lib.to_json({
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': '\n'.join(lines),
        },
    }))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass  # silence on any error
    sys.exit(0)
