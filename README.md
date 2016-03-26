# sublime_simple_git
A simple Git plugin for Sublime Text.

## Functions
It has builtin following functions:
* add all untracked files
* add only currently opened file
* add selected files
* make a commit with a message
* show the log for the currently opened file
* show the log for the whole repository
* diff the currently opened file with the previous version
* pull
* push
* display status
* revert a file
* open the Git config file

Most of these functions work pretty straightforward, but others don't, so here
is a short description of these commands.

### Add only selected files
When this command is run ("Add..." in the menu and in the command palette), a
list of all modified and untracked files is shown. The user can select a file,
which then is added. The list is kept open as long as files are selected; as
soon as ESC is pressed, the process is aborted and only the selected files are
added.

### Show the log for the currently opened file
This is pretty straightforward, but it has some special features. If a file is
open and the command is executed, the log for the file is displayed in a list.
If an older version of the file is selected from the list, the old version is
opened as well as the diff between the current version and that older version.
