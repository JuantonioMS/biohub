from datetime import datetime
import random
from typing import Any, Union
from xml.etree import ElementTree as ET
from pattern.en import singularize

import logging

from biohub.conf.general.constant import ID_LENGTH, ID_CHARACTERS, ID_PREFIX, DEFAULT_DATE_FORMAT
from biohub.conf.general.constant import LOG_HEADER, LOG_BODY, LOG_TAIL

class BioHubClass:


    def __init__(self,
                 xmlElement: ET.Element = None,
                 **attrs) -> None:

        #  IMPOTANTE!!
        #  Parece ser que al instancia un ET.Element() usa el mismo sitio de memoria en el que ya se había
        #  instanciado uno. Esto hacia que nuevas instancias cogieran información de otros objetos creados de la misma
        #  clase. Es por este motivo que cada inicialización de un clase va a importar la orden completa.
        from xml.etree import ElementTree as ET

        if not xmlElement:
            xmlElement = ET.Element("default")

        self._xmlElement = xmlElement

        #  Si es un elemento por defecto, se cambia el nombre al de la clase
        if self._xmlElement.tag == "default":
            self._xmlElement.tag = self.__class__.__name__.lower()

        #  Todo parámetro en el inicio se guarda como  atributo
        for attr, value in attrs.items():
            setattr(self, attr, value)

        self.minimumBuild()



    def newId(self, prefix: Union[bool, str] = False) -> str:

        """ Generación de IDs

        Genera de forma aleatoria una cadena de caracteres de una longitud N seleccionando caracteres
        de una cadena X. Estos parámetros se indican
        """

        coreId = "".join(random.choices(ID_CHARACTERS, k = ID_LENGTH))

        if isinstance(prefix, str):
            return prefix + coreId

        else:

            for className in self.__class__.__mro__:

                className = className.__name__.split(".")[-1]

                if className in ID_PREFIX:
                    return ID_PREFIX[className] + coreId

            return ID_PREFIX["Unknown"] + coreId



    def minimumBuild(self) -> None:

        if self.id is None:
            self.id = self.newId()

        if self.date is None:
            self.date = datetime.now()


#%%  LOGGER_____________________________________________________________________________________________________________


    @property
    def loggingTerminalHandler(self) -> logging.StreamHandler:

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(self.loggingFormatter)

        return handler


    @property
    def loggingGlobalHandler(self) -> logging.FileHandler:

        handler = logging.FileHandler("biohub_logging.log", encoding = "utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(self.loggingFormatter)

        return handler

    @property
    def loggingFormat(self) -> list:
        return [LOG_HEADER, LOG_BODY, LOG_TAIL]


    @property
    def loggingFormatter(self) -> logging.Formatter:
        return logging.Formatter("\n".join(self.loggingFormat) + "\n",
                                 datefmt = DEFAULT_DATE_FORMAT)


    #%%  XML special tags_______________________________________________________________________________________________


    @property
    def _xmlElementTags(self) -> set: return {"id", "outlines", "tags"}

    @property
    def _xmlAttributeTags(self) -> set: return {"comment"}

    @property
    def _xmlSpecialTags(self) -> set: return {"date"}


    #%%  Getters built-in methods_______________________________________________________________________________________


    def __getattribute__(self, attr: str) -> Any:

        if attr in super().__getattribute__("_xmlElementTags"): return self.__getXmlElementTag__(attr)
        elif attr in super().__getattribute__("_xmlAttributeTags"): return self.__getXmlAttributeTag__(attr)
        elif attr in super().__getattribute__("_xmlSpecialTags"): return self.__getXmlSpecialTag__(attr)
        else: return super().__getattribute__(attr)



    def __getXmlElementTag__(self, attr: str) -> Any:

        value = self._xmlElement.find(attr)

        if value != None:

            #  Nested element
            if len(list(value.iter())) > 1:
                return {subelement.text for subelement in value}

            #  Single element
            else:
                return value.text


        else:

            try: return super().__getattribute__(attr)
            except AttributeError: return None



    def __getXmlAttributeTag__(self, attr: str) -> Any:

        try: return self._xmlElement.attrib[attr]
        except KeyError: return None



    def __getXmlSpecialTag__(self, attr: str) -> Any:

        if attr == "date":


            try: return datetime.strptime(self._xmlElement.attrib[attr], DEFAULT_DATE_FORMAT)
            except KeyError: return None


    #%%  Setters built-in methods_______________________________________________________________________________________


    def __setattr__(self, attr: str, value: Any) -> None:

        if attr in self._xmlElementTags: self.__setXmlElementTag__(attr, value)
        elif attr in self._xmlAttributeTags: self.__setXmlAttributeTag__(attr, value)
        elif attr in self._xmlSpecialTags: self.__setXmlSpecialTag__(attr, value)
        else: super().__setattr__(attr, value)



    def __setXmlElementTag__(self, attr: str, value: Any) -> None:

        if getattr(self, attr) is not None:
            self._xmlElement.remove(self._xmlElement.find(attr))

        subelement = ET.SubElement(self._xmlElement, attr)

        if isinstance(value, (list, tuple, set)):

            for subValue in value:

                subsubelement = ET.SubElement(subelement, singularize((attr)))
                subsubelement.text = subValue

        else: subelement.text = str(value)



    def __setXmlAttributeTag__(self, attr: str, value: Any) -> None:

        self._xmlElement.attrib[attr] = str(value)



    def __setXmlSpecialTag__(self, attr: str, value: Any) -> None:

        if attr == "date":

            if isinstance(value, datetime):
                self._xmlElement.attrib[attr] = value.strftime(DEFAULT_DATE_FORMAT)

            elif isinstance(value, str):
                self._xmlElement.attrib[attr] = value


    #%%  Magic methods__________________________________________________________________________________________________


    def __hash__(self) -> int: return hash(self.id)


    def __str__(self) -> str: return self.id


    def __repr__(self) -> str:

        attribs, info = [f"{' ' * 4}Attributes:"], [f"{' ' * 4}Info:"]

        for attribName, attribValue in self._xmlElement.attrib.items():
            attribs.append(f"{' ' * 8}·{attribName} -> {attribValue}")

        for subelement in self._xmlElement:

            if len(list(subelement.iter())) > 1:
                info.append(f"{' ' * 8}·{subelement.tag}:")

                for subsubelement in subelement:
                    info.append(f"{' ' * 12}·{subsubelement.text}")

            else:
                info.append(f"{' ' * 8}·{subelement.tag} -> {subelement.text}")

        aux = [f"{self.__class__.__name__} object ({self.id})"] + info + attribs

        return "\n".join(aux)