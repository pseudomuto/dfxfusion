from apper import apper


class BaseCommand(apper.Fusion360CommandBase):
    """A base command for this project."""

    def __init__(self, name: str, options: dict, **kwargs):
        super().__init__(name, options)
        self.__kwargs = kwargs

    def _app_objects(self):
        return self.__kwargs.get('app_objects', apper.AppObjects())
