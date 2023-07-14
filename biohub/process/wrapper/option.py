from typing import Any

from biohub.process.wrapper import Wrapper


class Option(Wrapper):

    @property
    def name(self) -> str:

        """Nombre largo y por defecto"""

        return self._name


    @property
    def altName(self) -> str:

        """Nombre corto o alternativo. Sino, se retorna el nombre por defecto"""

        if hasattr(self, "_alternative"):
            return self._altName

        else:
            return self.name


    @property
    def value(self) -> Any:

        """Valor de la opción"""

        return self._value


    @value.setter
    def value(self, val: Any) -> None:
        self._value = val


    @property
    def evalAttributes(self) -> set:
        return {"value"} | super().evalAttributes



    def __eq__(self, other: object) -> bool:

        try: return self.name == other.name and self.value == other.value
        except: return False



    def __hash__(self) -> int:
        return hash((self.name, self.value))



    def __str__(self) -> str:

        """Aplica el formato recogido en self.format al objeto"""

        #  Si es booleano, solo se queda el nombre
        if isinstance(self.value, bool):
            return self.name

        else:
            return self.format.replace("<name>", self.name).replace("<value>", f"{self.value}").strip()