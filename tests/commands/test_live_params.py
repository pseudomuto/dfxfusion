from collections import namedtuple

from apper import apper
from src.commands import LiveParamsCommand


class TestLiveParamsCommand:
    def test_register(self, mocker):
        addin = mocker.Mock()
        LiveParamsCommand.register(addin)

        addin.add_command.assert_called_once_with(
            'Live Edit Params',
            LiveParamsCommand,
            mocker.ANY,
        )

        expected = {
            'cmd_id': 'dfx_live_params',
            'toolbar_panel_id': 'SolidModifyPanel',
            'workspace': 'FusionSolidEnvironment',
        }

        settings = addin.add_command.call_args.args[2]
        assert expected.items() <= settings.items()

    def test_on_create(self, mocker):
        Param = namedtuple('Param', ['name', 'expression'])
        params = [
            Param('param1', '100 mm'),
            Param('param2', '200 mm'),
            Param('param3', '300 mm'),
        ]

        mock = mocker.Mock(spec_set=apper.AppObjects)
        mocker.patch.object(mock.design, 'userParameters', params)

        inputs = mocker.Mock()
        LiveParamsCommand(None, {}, app_objects=mock).on_create(command=None, inputs=inputs)

        calls = [mocker.call(param.name, param.name, param.expression) for param in params]
        inputs.addStringValueInput.assert_has_calls(calls)
        assert inputs.addStringValueInput.call_count == len(params)
