import os.path

from apper import apper
from .commands import LiveParamsCommand, PartsListCommand


class App:
    def __init__(self, app_name, company_name, base_dir):
        self._addin = apper.FusionApp(
            app_name,
            company_name,
            False,
            default_dir=os.path.join(os.path.expanduser('~'), 'config'),
            resource_dir='resources',
            root_path=base_dir,
        )

        cmds = [LiveParamsCommand, PartsListCommand]
        [klass.register(self._addin) for klass in cmds]

    def run(self):
        self._addin.run_app()

    def stop(self):
        self._addin.stop_app()
