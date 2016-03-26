from __future__ import print_function
import sys
import sublime
import sublime_plugin
import os
import os.path
import subprocess
import json
import tempfile
import re

class GitCommand(sublime_plugin.TextCommand):
  def is_enabled(self):
    return True if self.get_gitdir() is not None else False

  def get_names(self):
    file = self.view.file_name()
    folder = os.path.dirname(file)
    file = os.path.basename(file)
    return folder, file


  def get_gitdir(self):
    try:
      gitdir = ".git"
      filename = self.view.file_name()
      folder = os.path.dirname(filename)
      while True:
        gitfolder = os.path.join(folder, gitdir)
        if os.path.exists(gitfolder):
          return gitfolder
        else:
          parentfolder = os.path.abspath(os.path.join(folder, os.path.pardir))
          if parentfolder == folder:
            return None
          else:
            folder = parentfolder
    except:
      return None


  def nothing(self, nothing1=None, nothing2=None, nothing3=None, **args):
    return

  def message(self, string):
    name = "VCS output"
    window = sublime.active_window()
    v = window.find_output_panel(name)
    if not v:
      v = window.create_output_panel(name)
    v.run_command('append', {'characters': string + "\n"})
    window.run_command("show_panel", {"panel": "output."+name})
    v.show(v.size(), False)

def safestr(text, fallback_encoding, method='decode'):
  try:
    unitext = getattr(text, method)('utf-8')
  except (UnicodeEncodeError, UnicodeDecodeError):
    unitext = getattr(text, method)(fallback_encoding)
  except AttributeError:
    unitext = str(text)
  return unitext

def vcs_command(folder, commands, univ=False):
  try:
    plat = sublime_plugin.sys.platform
    si = None
    if plat == 'win32':
      si = subprocess.STARTUPINFO()
      si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    os.chdir(folder)
    proc = subprocess.Popen(commands, cwd=folder, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=univ)
    stdout, stderr = proc.communicate()
    ret = safestr(stdout, "utf-8")
    print(safestr(stderr, "utf-8"))
    return ret
  except:
    raise

################################################################################

class MyGitAddCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Add " + file + "...")
    ret = vcs_command(folder, ["git", "add", "--", file])
    self.message("Done.")


class MyGitAddAllCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Add all...")
    ret = vcs_command(folder, ["git", "add", "--all", "--verbose"])
    self.message(ret)


class MyGitCommitCommand(GitCommand):
  def run(self, edit):
    sublime.active_window().show_input_panel('Commit message', '', self.on_done_input, self.nothing, self.nothing)

  def on_done_input(self, value):
    self.value = value
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Commit...")
    ret = vcs_command(folder, ["git", "commit", "-m", self.value])
    self.message(ret)


class MyGitDiffCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Diff " + file + "...")
    ret = vcs_command(folder, ["git", "--no-pager", "diff", "--no-color", "--", file])
    self.message("Done.")

    if len(ret) > 10:
      arg = {"output": ret}
      scratch_file = sublime.active_window().new_file()
      scratch_file.set_syntax_file("Packages/Diff/Diff.tmLanguage")
      scratch_file.set_name("Git Diff")
      scratch_file.run_command("insert_diff", arg)
      scratch_file.set_scratch(True)
      scratch_file.set_read_only(True)
    else:
      self.message("No differences.")


class MyGitLogCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Log " + file + "...")
    ret = vcs_command(folder, ["git", "--no-pager", "log", "--oneline", "--no-color", "--", file])
    self.message("Done.")
    self.lines = ret.splitlines(False)
    window = sublime.active_window()
    window.show_quick_panel(self.lines, self.select_done, sublime.MONOSPACE_FONT, 0, self.nothing)

  def select_done(self, index):
    if index < 0:
      self.message("Aborted.")
      return
    commit = self.lines[index][:7]
    folder, file = self.get_names();
    tempfilename = os.path.join(tempfile.gettempdir(), commit + "_" + file)
    ret = vcs_command(folder, ["git", "--no-pager", "show", "--no-color", commit + ":" + file])
    text_file = open(tempfilename, "w")
    text_file.write(ret)
    text_file.close()
    sublime.active_window().open_file(tempfilename, 0)
    ret = vcs_command(folder, ["git", "--no-pager", "diff", "--no-color", commit, "HEAD", "--", file])
    self.message("Done.")
    if len(ret) > 10:
      arg = {"output": ret}
      scratch_file = sublime.active_window().new_file()
      scratch_file.set_syntax_file("Packages/Diff/Diff.tmLanguage")
      scratch_file.set_name("Git Diff")
      scratch_file.run_command("insert_diff", arg)
      scratch_file.set_scratch(True)
      scratch_file.set_read_only(True)
    else:
      self.message("No differences.")


class MyGitFullLogCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Log...")
    ret = vcs_command(folder, ["git", "--no-pager", "log"])
    self.message("Done.")
    if len(ret) > 10:
      arg = {"output": ret}
      scratch_file = sublime.active_window().new_file()
      scratch_file.set_syntax_file("Packages/User/Git Log.sublime-syntax")
      scratch_file.set_name("Git Log")
      scratch_file.run_command("insert_diff", arg)
      scratch_file.set_scratch(True)
      scratch_file.set_read_only(True)


class MyGitPullCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Pull...")
    ret = vcs_command(folder, ["git", "pull", "--verbose"])
    self.message(ret)
    self.message("Done.")


class MyGitPushCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Push...")
    ret = vcs_command(folder, ["git", "push"])
    self.message(ret)
    self.message("Done.")


class MyGitStatusCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    self.folder = os.path.dirname(self.get_gitdir())
    self.message("Git Status...")
    ret = vcs_command(self.folder, ["git", "status", "-s"])
    if len(ret) > 0:
      self.lines = ret.splitlines(False)
      window = sublime.active_window()
      window.show_quick_panel(self.lines, self.select_done, sublime.MONOSPACE_FONT, 0, self.nothing)
    else:
      self.message("No files changed.")

  def select_done(self, index):
    if(index < 0):
      self.message("Aborted.")
      return
    folder = self.folder
    file = self.lines[index][3:]
    file = re.sub(r'^"|"$', '', file)
    self.message("Git Diff " + file + "...")
    ret = vcs_command(folder, ["git", "--no-pager", "diff", "--no-color", "--", file])
    if len(ret) > 10:
      filename = os.path.normpath(os.path.join(folder, file))
      sublime.active_window().open_file(filename)
      self.message("Opening " + file + ".")
      arg = {"output": ret}
      scratch_file = sublime.active_window().new_file()
      scratch_file.set_syntax_file("Packages/Diff/Diff.tmLanguage")
      scratch_file.set_name("Show Diff")
      scratch_file.run_command("insert_diff", arg)
      scratch_file.set_scratch(True)
      scratch_file.set_read_only(True)
    else:
      self.message("No differences.")


class MyGitCheckoutCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    folder, file = self.get_names();
    self.message("Git Checkout " + file + "...")
    ret = vcs_command(folder, ["git", "checkout", "--", file])
    self.message(ret)
    self.message("Done.")


class MyGitConfigCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    gitdir = self.get_gitdir()
    conf = os.path.normpath(os.path.join(gitdir, "config"))
    self.message("Open Git config file " + conf)
    v = sublime.active_window().open_file(conf)
    v.set_syntax_file("Packages/User/Git Config.sublime-syntax")


class MyGitAddMultiCommand(GitCommand):
  def run(self, edit):
    sublime.set_timeout_async(self.doit, 0)

  def doit(self):
    self.folder = os.path.dirname(self.get_gitdir())
    self.message("Git Status...")
    ret = vcs_command(self.folder, ["git", "status", "-s"])
    self.files_to_add = []
    if len(ret) > 0:
      self.lines = ret.splitlines(False)
      window = sublime.active_window()
      window.show_quick_panel(self.lines, self.select_done, sublime.MONOSPACE_FONT, 0, self.nothing)

    else:
      self.message("No files changed.")

  def select_done(self, index):
    if index < 0:
      #self.message("Aborted.")
      print(self.files_to_add)
      self.message("Adding: ")
      msg = ""
      cmdline = ["git", "add", "--"]
      for file in self.files_to_add:
        msg = msg + "  " + file + "\n"
        cmdline.append(file)
      self.message(msg)
      ret = vcs_command(self.folder, cmdline)
      self.message("Done.")
      return
    else:
      name = self.lines[index][3:]
      name = re.sub(r'^"|"$', '', name)
      self.files_to_add.append(name)
      self.lines.pop(index)
      window = sublime.active_window()
      window.show_quick_panel(self.lines, self.select_done, sublime.MONOSPACE_FONT, 0, self.nothing)
