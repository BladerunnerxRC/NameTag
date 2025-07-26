# CleanVersionOnSave

A simple Fusion 360 add-in that cleans up document names when they are saved.
By default it removes trailing version numbers such as `v1` or `v23`, but the
behaviour can be customised through the provided settings dialog.

## Usage

1. Copy the entire `NameTagger` folder into your Fusion 360 **AddIns** directory.
2. Restart Fusion 360 or open the Add-Ins dialog and run **NameTagger**.
3. While active, every time a document is saved its name will be processed using
   the selected strategy.
4. Click **NameTagger Settings** in the ADD-INS panel to change options such as
   enabling/disabling auto rename, choosing the rename strategy, providing a
   custom regular expression or export path, and testing the regex.
5. Stop the add-in to restore the default behaviour.

The core logic resides in the `rename_document` function. It applies the chosen
strategy based on the regular expression pattern entered in the settings dialog.

Every successful rename is also recorded to `rename_history.json` inside the
add-in directory. Each log entry stores the timestamp, original name, new name
and whether the save was triggered manually or via autosave.

Before applying a rename, the add-in validates the result by removing invalid
characters (`/`, `\`, `?`, `*`, `:`), trimming overly long names to 128
characters and warning when a name collision is detected in the parent folder.
