import sublime
import os, shlex
import subprocess

def _test_paths_for_executable(paths, test_file):
  for directory in paths:
    file_path = os.path.join(directory, test_file)
    if os.path.exists(file_path) and os.access(file_path, os.X_OK):
      return file_path

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

  def current_branch(self):
    return self._run("rev-parse --abbrev-ref HEAD")

  def _run(self, command):
    if self._cwd == None or not os.path.isdir(self._cwd):
      os.chdir(self.working_dir)

    cmd = [GIT] + shlex.split(command)
    git = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
    output = ""
    try:
      output = git.communicate(timeout=5)[0]
    except TimeoutExpired:
      sublime.status_message("'{0} {1}' timed out".format(GIT, command))

    return output.strip().decode('utf-8')

class GitCommand(object):
  def _git(self):
    cwd = self.__get_cwd()
    if not hasattr(self, '__cached_git') or cwd != self.__cached_cwd:
      self.__cached_cwd = cwd
      self.__cached_git = Git(self.__cached_cwd)

    return self.__cached_git

  def __get_cwd(self):
    view = self.window.active_view()
    if view and view.file_name() and len(view.file_name()) > 0:
      return os.path.realpath(os.path.dirname(view.file_name()))

    try:
      return self.window.folders()[0]
    except IndexError:
      return None
