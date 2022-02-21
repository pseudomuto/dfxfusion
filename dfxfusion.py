import adsk.core

import os.path
import sys
import traceback

try:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_dir)

    from src.app import App

    dfx = App('DFXFusion', 'DFX Woodworking', root_dir)
    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface
except:  # noqa: E722
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization Failed: {}'.format(traceback.format_exc()))

# Set to True to display various useful messages when debugging your app
debug = True


def run(context):
    dfx.run()


def stop(context):
    dfx.stop()
