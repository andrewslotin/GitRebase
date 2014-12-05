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

    revisions = []
    list_items = []
    for [rev, msg] in commits:
      revisions.append(rev)
      list_items.append([msg, rev])

    self.window.show_quick_panel(list_items, self.on_commit_enter_handler(revisions))

  def on_commit_enter_handler(self, revisions):
    def on_commit_enter(rev):
      if rev < 0:
        return

      self._git().rebase("{0}~1".format(revisions[rev]), interactive=True)

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
    self._git().abort_rebase()

class GitRebaseContinueCommand(GitCommand, sublime_plugin.WindowCommand):
  def run(self):
    self._git_rebase_continue()

  def _git_rebase_continue(self):
    sublime._git().continue_rebase()
