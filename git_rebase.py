import sublime, sublime_plugin
import re
import os

from .git import Git, GitCommand

class GitRebaseEditCommitCommand(GitCommand, sublime_plugin.WindowCommand):
  def run(self):
    commits = self._git().log()
    if len(commits) == 0:
      self.window.show_quick_panel(["No commits in this branch"], None)
      return

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
