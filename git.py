import sublime
import os, shlex
import subprocess

class Git:
  def __init__(self, cwd):
    self._cwd = cwd
    self._git = "git"

    s = sublime.load_settings("GitRebase.sublime-settings")
    if s.get('git_command'):
      self._git = s.get('git_command')

  def log(self, limit = None):
    git_command = "log --oneline --no-color --no-abbrev-commit"

    current_branch = self.current_branch()
    if current_branch != "master":
      git_command += " master..{}".format(current_branch)

    if limit != None:
      git_command += " -n {}".format(limit)

    sublime.status_message(git_command)

    history = self._run(git_command)
    return [line.split(" ", 1) for line in history.splitlines()]

  def edit_revision(self, rev):
    self._run("rebase --interactive {}~1".format(rev), GIT_SEQUENCE_EDITOR="sed -i '' -e 's/^\s*pick {0}/edit {0}/g'".format(rev[0:7]))

  def abort_rebase(self):
    self._run("rebase --abort")

  def continue_rebase(self):
    self._run("rebase --continue")

  def stash_changes(self):
    self._run("stash")

  def apply_stash(self):
    self._run("stash pop")

  def current_branch(self):
    return self._run("rev-parse --abbrev-ref HEAD")

  def is_clean(self):
    return len(self._run("status -s -uno")) == 0

  def _run(self, command, **env_vars):
    cwd = self._cwd
    if cwd != None and not os.path.isdir(self._cwd):
      cwd = None

    environ = os.environ.copy()
    for (var, val) in env_vars.items():
      environ[var] = shlex.quote(val)

    cmd = [self._git] + shlex.split(command)
    with subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd, env=environ) as git:
      output = ""
      try:
        [output, error] = git.communicate(timeout=5)

        if error:
          print(error.decode('utf-8'))
      except subprocess.TimeoutExpired:
        print("`{0} {1}` timed out".format(GIT, command))

    return output.strip().decode('utf-8')
