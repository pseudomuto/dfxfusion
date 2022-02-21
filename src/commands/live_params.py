import adsk.core

from .base import BaseCommand


class LiveParamsCommand(BaseCommand):
    """A command which allows live-editing of user parameters.

    Upon execution, this command will show list of all user defined parameters
    and their current values. Changes to these values will be immediately
    represented in the UI.

    You can find it under the Modify panel in Solid workspace.
    """

    def register(addin):
        """Register this command with the add-in."""
        addin.add_command('Live Edit Params', LiveParamsCommand, {
            'cmd_description': 'Live-edit parameters',
            'cmd_id': 'dfx_live_params',
            'workspace': 'FusionSolidEnvironment',
            'toolbar_panel_id': 'SolidModifyPanel',
            'cmd_resources': 'command_icons',
            'command_visible': True,
        })

    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        """ Create an input for each user parameter in the model."""
        ao = self._app_objects()
        for param in ao.design.userParameters:
            inputs.addStringValueInput(param.name, param.name, param.expression)

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        """Update all of the inputs when this command is run."""
        self._update(inputs)

    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        """update all of the inputs before rendering."""
        self._update(inputs)

    def _update(self, inputs):
        ao = self._app_objects()
        if inputs.count < 1:
            ao.ui.messageBox("No user parameters in the model")
            return

        um = ao.units_manager
        for param in ao.design.userParameters:
            expr = inputs.itemById(param.name).value
            if not um.isValidExpression(expr, um.defaultLengthUnits):
                ao.ui.messageBox("Invalid expression: {}\n{}".format(param.name, expr))
                continue

            param.expression = expr
