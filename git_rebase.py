import sublime, sublime_plugin
import re
import os

from .git import Git

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

class GitRebaseEditCommitCommand(GitCommand, sublime_plugin.WindowCommand):
  def run(self):
    commits = self._git().log(10)
    self.window.show_quick_panel([[msg, rev] for rev, msg in commits.items()], self.on_commit_enter_handler(list(commits.keys())))

  def on_commit_enter_handler(self, revisions):
    def on_commit_enter(rev):
      if rev < 0:
        return

      sublime.status_message("rebase --interactive {0}~1".format(revisions[rev]))

    return on_commit_enter

  def _selected_rev(self):
    rev_regex = re.compile(r'\A\s*(?P<rev>[0-9a-z]{6,40})\s*\Z')
    view = self.window.active_view()
    selections = view.sel()

    for selection in selections:
      s = view.substr(selection)
      m = rev_regex.match(s)
      if m != None:
        return m.group('rev')

    return ""

class GitRebaseAbortCommand(GitCommand, sublime_plugin.WindowCommand):
  def run(self):
    self._git_rebase_abort()

  def _git_rebase_abort(self):
    sublime.status_message("rebase --abort")

class GitRebaseContinueCommand(GitCommand, sublime_plugin.WindowCommand):
  def run(self):
    self._git_rebase_continue()

  def _git_rebase_continue(self):
    sublime.status_message("rebase --continue")
