DEFAULT_FORMAT = "<name> <value>"

class Wrapper:


    def __init__(self, **kwargs) -> None:

        for attr, value in kwargs.items():
            setattr(self, f"_{attr}", value)


    @property
    def format(self) -> str:

        "Tipo de formato. Por defecto <opcion valor>"

        if hasattr(self, "_format"):
            return self._format
        else:
            return DEFAULT_FORMAT

    @property
    def role(self) -> str:

        """Get wrapper role around process"""

        try: return self._role
        except AttributeError: return "unknown"


    @property
    def condition(self):

        if hasattr(self, "_condition"):
            return self._condition

        return True


    @condition.setter
    def condition(self, value: bool) -> None:
        self._condition = value


    @property
    def evalAttributes(self) -> set:
        return {"condition"}


    @property
    def evalPending(self):
        for attr in self.evalAttributes:
            if isinstance(value := getattr(self, attr), str) and "eval##" in value:
                return True

        return False


from biohub.process.wrapper.file_io import Input, Output
from biohub.process.wrapper.option import Option
