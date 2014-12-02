import sublime, sublime_plugin
import re

class GitRebase(sublime_plugin.WindowCommand):
  git_command = "git"

  @staticmethod
  def run(command):
    sublime.status_message("{0} {1}".format(GitRebase.git_command, command))

class GitRebaseEditCommitCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.window.show_input_panel("Commit hash:", self._selected_rev(), self.on_commit_enter, None, None)

  def on_commit_enter(self, rev):
    self._git_rebase_interactive("{0}~1".format(rev))

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

  def _git_rebase_interactive(self, onto):
    GitRebase.run("rebase --interactive {0}".format(onto))

class GitRebaseAbortCommand(sublime_plugin.WindowCommand):
  def run(self):
    self._git_rebase_abort()

  def _git_rebase_abort(self):
    GitRebase.run("rebase --abort")

class GitRebaseContinueCommand(sublime_plugin.WindowCommand):
  def run(self):
    self._git_rebase_continue()

  def _git_rebase_continue(self):
    GitRebase.run("rebase --continue")
