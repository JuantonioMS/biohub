class Wrapper:


    def __init__(self, **kwargs) -> None:

        for attr, value in kwargs.items():
            setattr(self, f"_{attr}", value)


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


from biohub.utils.wrapper.file_io import Input, Output
from biohub.utils.wrapper.option import Option