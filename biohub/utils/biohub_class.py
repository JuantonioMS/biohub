from datetime import datetime
import random
from typing import Any
from xml.etree import ElementTree as ET
from pathlib import Path
from pattern.en import singularize


CHARACTERS = "0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
NCHARS = 15


class BioHubClass:


    def __init__(self,
                 xmlElement: ET.Element = None,
                 **attrs) -> None:

        #  IMPOTANTE!!
        #  Parece ser que al instancia un ET.Element() se usa el mismo sitio de memoria en el que ya se había
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

        for attr in self.specialAttrs:
            getattr(self, attr)



    def newId(self):

        biohubId = "".join(random.choices(CHARACTERS, k = NCHARS))

        return biohubId


    #  Getters__________________________________________________________________________________________________________

    @property
    def id(self) -> str:

        biohubId = self.newId()

        self.id = biohubId

        return biohubId


    @property
    def date(self) -> datetime:

        biohubDate = datetime.now().strftime("%Y/%b/%d %H:%M:%S")

        self.date = biohubDate

        return datetime.strptime(biohubDate, "%Y/%b/%d %H:%M:%S")


    @property
    def specialAttrs(self) -> set:
        return {"id", "name", "date", "comment", "outlines", "tags"}


    #  Attributes management____________________________________________________________________________________________


    def __getattribute__(self, attr: str) -> Any:

        #  En el caso de que el atributo consultado se encuentre dentro de las palabras clave recogidas
        #  dentro del elemento XML
        if attr in super().__getattribute__("specialAttrs"):

            #  Atributos que son atributos del elemento XML
            if attr in {"date", "comment"}:

                try:
                    if attr == "date": return datetime.strptime(self._xmlElement.attrib[attr], "%Y/%b/%d %H:%M:%S")
                    else: return self._xmlElement.attrib[attr]

                except KeyError:
                    try: return super().__getattribute__(attr)
                    except AttributeError: return None

            #  Si es un subelemento del elemento XML
            else:

                value = self._xmlElement.find(attr)

                if value != None:

                    if attr == "path": return Path(value.text)

                    #  Es un elemento XML con sublementos XML
                    elif len(list(value.iter())) > 1:
                        return {subelement.text for subelement in value}

                    #  Es un elemento XML final
                    else: return value.text

                #  Si la palabra no está definida dentro del elemento XML porque no existe esa información
                else:

                    try: return super().__getattribute__(attr)
                    except AttributeError: return None

        #  Si no es una palabra clave del elemento XML
        else: return super().__getattribute__(attr)



    def __setattr__(self, attr: str, value: Any) -> None:

        #  Atributos que son atributos del elemento XML
        if attr in self.specialAttrs:

            if attr in {"date", "comment"}:
                self._xmlElement.attrib[attr] = value

            #  Si es un subelemento del elemento XML
            else:

                if (aux := self._xmlElement.find(attr)) != None:
                    self._xmlElement.remove(aux)

                #  Es un dato iterable
                if isinstance(value, (list, tuple, set)):
                    subelement = ET.SubElement(self._xmlElement, attr)

                    for subvalue in value:
                        subsubelement = ET.SubElement(subelement, singularize(attr))
                        subsubelement.text = subvalue

                #  Es un dato simple
                else:

                    subelement = ET.SubElement(self._xmlElement, attr)

                    subelement.text = str(value)

        else: super().__setattr__(attr, value)


    #  Magic methods____________________________________________________________________________________________________


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
