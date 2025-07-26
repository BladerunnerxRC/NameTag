import adsk.core
import adsk.fusion
import traceback
import re
import datetime

handlers = []

# User configurable settings with sensible defaults. These values are modified
# through the settings command created below.
settings = {
    "auto_rename": True,
    "strategy": "remove",  # remove | timestamp | revision
    "regex": r"\s*v\d+$",
    "export_path": "",
}

# IDs used for the command and UI elements so we can clean them up properly.
CMD_ID = "NameTaggerSettingsCmd"
_cmd_def = None
_btn_ctrl = None
_doc_handler = None

def rename_document(name: str, doc) -> str:
    """Apply the selected renaming strategy to ``name``."""
    pattern = settings.get("regex", r"\s*v\d+$")
    if not re.search(pattern, name):
        return name

    strategy = settings.get("strategy", "remove")
    if strategy == "timestamp":
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return re.sub(pattern, ts, name)
    elif strategy == "revision":
        rev = getattr(doc, "revisionId", "1")
        base = re.sub(pattern, "", name)
        return f"r{rev}_{base}"

    # Default behaviour is to remove the suffix
    return re.sub(pattern, "", name)


class DocumentSavingHandler(adsk.core.DocumentEventHandler):
    """Event handler that cleans document names on save."""

    def notify(self, args: adsk.core.DocumentEventArgs):
        if not settings.get("auto_rename", True):
            return
        try:
            doc = args.document
            original = doc.name
            clean = rename_document(original, doc)
            if original != clean:
                doc.name = clean
                adsk.core.Application.get().log(
                    f"Renamed document from '{original}' to '{clean}'"
                )
        except Exception:
            adsk.core.Application.get().log(
                "Failed:\n{}".format(traceback.format_exc())
            )


class SettingsCommandExecuteHandler(adsk.core.CommandEventHandler):
    """Reads values from the dialog and stores them in ``settings``."""

    def notify(self, args: adsk.core.CommandEventArgs):
        cmd = args.firingEvent.sender
        inputs = cmd.commandInputs
        settings["auto_rename"] = inputs.itemById("autoRename").value
        settings["regex"] = inputs.itemById("regex").value
        settings["export_path"] = inputs.itemById("exportPath").value
        strat = inputs.itemById("strategy").selectedItem.name
        settings["strategy"] = {
            "Remove": "remove",
            "Timestamp": "timestamp",
            "Revision Prefix": "revision",
        }.get(strat, "remove")


class SettingsInputChangedHandler(adsk.core.InputChangedEventHandler):
    """Updates the regex preview when inputs change."""

    def notify(self, args: adsk.core.InputChangedEventArgs):
        try:
            cmd = args.firingEvent.sender
            inputs = cmd.commandInputs
            regex_val = inputs.itemById("regex").value
            test_name = inputs.itemById("testName").value
            strategy = inputs.itemById("strategy").selectedItem.name
            tmp_settings = dict(settings)
            tmp_settings["regex"] = regex_val
            tmp_settings["strategy"] = {
                "Remove": "remove",
                "Timestamp": "timestamp",
                "Revision Prefix": "revision",
            }.get(strategy, "remove")

            class _Dummy:
                revisionId = "1"

            preview = rename_document(test_name, _Dummy())
            inputs.itemById("preview").text = preview
        except Exception:
            adsk.core.Application.get().log(
                "Preview failed:\n{}".format(traceback.format_exc())
            )


class SettingsCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Builds the settings dialog."""

    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        cmd = args.command
        on_execute = SettingsCommandExecuteHandler()
        cmd.execute.add(on_execute)
        handlers.append(on_execute)

        on_input = SettingsInputChangedHandler()
        cmd.inputChanged.add(on_input)
        handlers.append(on_input)

        inputs = cmd.commandInputs
        inputs.addBoolValueInput("autoRename", "Enable Auto Rename", True, "", settings["auto_rename"])

        dd = inputs.addDropDownCommandInput(
            "strategy", "Rename Strategy", adsk.core.DropDownStyles.TextListDropDownStyle
        )
        dd.listItems.add("Remove", settings["strategy"] == "remove")
        dd.listItems.add("Timestamp", settings["strategy"] == "timestamp")
        dd.listItems.add("Revision Prefix", settings["strategy"] == "revision")

        inputs.addStringValueInput("regex", "Regex Pattern", settings["regex"])
        inputs.addStringValueInput("testName", "Test Name", "MyFile v1")
        inputs.addTextBoxCommandInput("preview", "Result", "", 1, True)
        inputs.addStringValueInput("exportPath", "Export Path", settings["export_path"])


def run(context):
    global _cmd_def, _btn_ctrl, _doc_handler
    app = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # document save handler
        _doc_handler = DocumentSavingHandler()
        app.documentSaving.add(_doc_handler)
        handlers.append(_doc_handler)

        # create the settings command definition
        _cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if not _cmd_def:
            _cmd_def = ui.commandDefinitions.addButtonDefinition(
                CMD_ID, "NameTagger Settings", "Configure NameTagger"
            )

        on_created = SettingsCommandCreatedHandler()
        _cmd_def.commandCreated.add(on_created)
        handlers.append(on_created)

        addins_panel = ui.allToolbarPanels.itemById("SolidScriptsAddinsPanel")
        _btn_ctrl = addins_panel.controls.itemById(CMD_ID)
        if not _btn_ctrl:
            _btn_ctrl = addins_panel.controls.addCommand(_cmd_def)

        app.log("NameTagger started. Documents will be cleaned on save.")
    except Exception:
        if app:
            app.log("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    global _cmd_def, _btn_ctrl, _doc_handler
    app = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        if _doc_handler:
            app.documentSaving.remove(_doc_handler)
            _doc_handler = None
        if _btn_ctrl:
            _btn_ctrl.deleteMe()
            _btn_ctrl = None
        if _cmd_def:
            _cmd_def.deleteMe()
            _cmd_def = None

        handlers.clear()
        app.log("NameTagger stopped.")
    except Exception:
        if app:
            app.log("Failed:\n{}".format(traceback.format_exc()))

