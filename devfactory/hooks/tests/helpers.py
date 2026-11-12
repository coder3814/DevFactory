"""Shared helpers for the hook tests. Holds no tests itself."""

import datetime
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HOOKS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPT = os.path.abspath(os.path.join(HOOKS, '..', 'scripts', 'devfactory.py'))


def _remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_tree(path):
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_remove_readonly)
    else:
        shutil.rmtree(path, onerror=_remove_readonly)


def temp_dir(test, prefix='devfactory-hook-'):
    d = tempfile.mkdtemp(prefix=prefix)
    if test is not None:
        test.addCleanup(remove_tree, d)
    return d


def write(file, content):
    with open(file, 'wb') as f:
        f.write(content.encode('utf-8'))


def git(cwd, *args):
    r = subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com',
                        '-c', 'commit.gpgsign=false'] + list(args),
                       cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError('git %s failed: %s' % (' '.join(args), r.stderr.decode('utf-8', 'replace')))
    return r.stdout.decode('utf-8').strip()


def git_repo_on(cwd, branch):
    """A repository on the branch with one commit."""
    git(cwd, 'init', '-q', '-b', branch)
    git(cwd, 'commit', '-q', '--allow-empty', '-m', 'init')


def iso_ago(hours):
    t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
    return t.strftime('%Y-%m-%dT%H:%M:%S.') + '%03dZ' % (t.microsecond // 1000)


def write_marker(root, name, age_hours=0):
    """Writes a marker whose timestamp is age_hours old."""
    d = os.path.join(root, '.devfactory', '.active')
    os.makedirs(d, exist_ok=True)
    write(os.path.join(d, name), iso_ago(age_hours) + '\n')


def project(test, profile=None, markers=(), branch=None):
    """A project folder with the profile and markers (names, or (name, age_hours) pairs);
    branch makes it a git repository on that branch."""
    cwd = temp_dir(test)
    if branch:
        git_repo_on(cwd, branch)
    if profile is not None:
        os.makedirs(os.path.join(cwd, '.devfactory', '.active'), exist_ok=True)
        write(os.path.join(cwd, '.devfactory', 'profile.md'), profile)
    for m in markers:
        name, age = (m if isinstance(m, (list, tuple)) else (m, 0))
        write_marker(cwd, name, age)
    return cwd


def run_hook(test, hook, data, env=None):
    payload = data if isinstance(data, str) else json.dumps(data)
    r = subprocess.run([sys.executable, os.path.join(HOOKS, hook)], input=payload.encode('utf-8'),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=dict(os.environ, **(env or {})))
    stderr = r.stderr.decode('utf-8', 'replace')
    test.assertEqual(r.returncode, 0, stderr)
    return r.stdout.decode('utf-8')


def bash(test, hook, cwd, command, tool='Bash'):
    """Runs a PreToolUse hook on a shell tool's command; tool is 'Bash' or 'PowerShell'."""
    return run_hook(test, hook, {
        'session_id': 'test',
        'cwd': cwd,
        'hook_event_name': 'PreToolUse',
        'tool_name': tool,
        'tool_input': {'command': command},
    })


def assert_deny(test, out, pattern=r'^DevFactory: '):
    test.assertNotEqual(out, '', 'expected a deny, got silence')
    parsed = json.loads(out)
    test.assertEqual(parsed['hookSpecificOutput']['hookEventName'], 'PreToolUse')
    test.assertEqual(parsed['hookSpecificOutput']['permissionDecision'], 'deny')
    test.assertRegex(parsed['hookSpecificOutput']['permissionDecisionReason'], pattern)
