import adsk.core
import adsk.fusion
import traceback
import re

handlers = []

def remove_version_number(name: str) -> str:
    """Remove trailing version suffix like 'v1', 'v23', etc."""
    return re.sub(r"\s*v\d+$", "", name)


class DocumentSavingHandler(adsk.core.DocumentEventHandler):
    """Event handler that cleans document names on save."""

    def notify(self, args: adsk.core.DocumentEventArgs):
        try:
            doc = args.document
            original = doc.name
            clean = remove_version_number(original)
            if original != clean:
                doc.name = clean
                adsk.core.Application.get().log(
                    f"Renamed document from '{original}' to '{clean}'"
                )
        except Exception:
            adsk.core.Application.get().log(
                "Failed:\n{}".format(traceback.format_exc())
            )


def run(context):
    app = None
    try:
        app = adsk.core.Application.get()
        handler = DocumentSavingHandler()
        app.documentSaving.add(handler)
        handlers.append(handler)
        app.log("NameTagger started. Documents will be cleaned on save.")
    except Exception:
        if app:
            app.log("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    app = None
    try:
        app = adsk.core.Application.get()
        for h in handlers:
            app.documentSaving.remove(h)
        handlers.clear()
        app.log("NameTagger stopped.")
    except Exception:
        if app:
            app.log("Failed:\n{}".format(traceback.format_exc()))

