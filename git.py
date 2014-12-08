import sublime
import os, shlex
import subprocess

def _test_paths_for_executable(paths, test_file):
  for directory in paths:
    file_path = os.path.join(directory, test_file)
    if os.path.exists(file_path) and os.access(file_path, os.X_OK):
      return file_path

# Thanks kemayo/sublime-text-2-git
def find_git():
  # It turns out to be difficult to reliably run git, with varying paths
  # and subprocess environments across different platforms. So. Let's hack
  # this a bit.
  # (Yes, I could fall back on a hardline "set your system path properly"
  # attitude. But that involves a lot more arguing with people.)
  path = os.environ.get('PATH', '').split(os.pathsep)
  if os.name == 'nt':
    git_cmd = 'git.exe'
  else:
    git_cmd = 'git'

  git_path = _test_paths_for_executable(path, git_cmd)

  if not git_path:
    # /usr/local/bin:/usr/local/git/bin
    if os.name == 'nt':
      extra_paths = (
        os.path.join(os.environ["ProgramFiles"], "Git", "bin"),
        os.path.join(os.environ["ProgramFiles(x86)"], "Git", "bin"),
      )
    else:
      extra_paths = (
        '/usr/local/bin',
        '/usr/local/git/bin',
      )
    git_path = _test_paths_for_executable(extra_paths, git_cmd)
  return git_path

GIT = find_git()

class Git:
  def __init__(self, cwd):
    self._cwd = cwd

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

  def rebase(self, upstream, interactive = False):
    git_command = "rebase"

    if interactive:
      git_command += " --interactive"

    git_command += " {}".format(upstream)

    self._run(git_command)

  def abort_rebase(self):
    self._run("rebase --abort")

  def continue_rebase(self):
    self._run("rebase --continue")

  def stash(self):
    self._run("stash")

  def stash(self):
    self._run("stash pop")

  def current_branch(self):
    return self._run("rev-parse --abbrev-ref HEAD")

  def is_clean(self):
    return len(self._run("status -s -uno") == 0)

  def _run(self, command, **env_vars):
    cwd = self._cwd
    if cwd != None and not os.path.isdir(self._cwd):
      cwd = None

    environ = os.environ.copy()
    for (var, val) in env_vars.items():
      environ[var] = shlex.quote(val)

    cmd = [GIT] + shlex.split(command)
    with subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd, env=environ) as git:
      output = ""
      try:
        [output, error] = git.communicate(timeout=5)

        if error:
          print(error.decode('utf-8'))
      except subprocess.TimeoutExpired:
        print("`{0} {1}` timed out".format(GIT, command))

    return output.strip().decode('utf-8')
