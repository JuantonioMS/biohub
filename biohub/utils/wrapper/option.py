from typing import Any

from biohub.utils.wrapper import Wrapper

class Option(Wrapper):


    @property
    def name(self) -> str:

        """Nombre largo y por defecto"""

        return self._name



    @property
    def alternative(self) -> str:

        """Nombre corto o alternativo. Sino, se retorna el nombre por defecto"""

        if hasattr(self, "_alternative"):
            return self._alternative

        else:
            return self.name



    @property
    def value(self) -> Any:

        """Valor de la opción"""

        return self._value



    @property
    def format(self) -> str:

        "Tipo de formato. Por defecto <opcion valor>"

        if hasattr(self, "_format"):
            return self._format
        else:
            return "name value"



    def __str__(self) -> str:

        """Aplica el formato recogido en self.format al objeto"""

        #  Si es booleano, solo se queda el nombre
        if isinstance(self.value, bool):
            return self.name

        else:
            return self.format.replace("name", self.name).replace("value", f"{self.value}")