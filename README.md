# NameTagger

A simple Fusion 360 add-in that cleans up document names by removing
trailing version numbers (e.g. `v1`, `v23`) whenever a document is
saved. This does not disable Fusion 360's versioning; it only keeps the
names shown in the browser and exported files tidy.

## Usage

1. Copy `rename_on_save.py` into your Fusion 360 Scripts or Add-Ins
   folder.
2. In Fusion 360, open the Add-Ins dialog and run the script.
3. While active, every time a document is saved its name will be checked
   and any version suffix will be stripped.
4. Stop the add-in to restore the default behaviour.

The core logic resides in the `remove_version_number` function which
uses a regular expression to remove a suffix of the form `v<number>`.

