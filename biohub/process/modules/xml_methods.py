from typing import Any
from pathlib import Path
from datetime import timedelta

from xml.etree import ElementTree as ET

from biohub.process.wrapper import Input, Output, Option
from biohub.utils import singularize

class XmlMethods:

#%%  DURATION___________________________________________________________________________________________________________


    def __getXmlDuration__(self, attr: Any) -> Any:

        try:

            duration = self._xmlElement.attrib[attr]

            hours, minutes, seconds = duration.split(":")
            seconds, microseconds = seconds.split(".")

            return timedelta(hours = int(hours),
                                minutes = int(minutes),
                                seconds = int(seconds),
                                microseconds = int(microseconds))

        except KeyError: return None



    def __setXmlDuration__(self, attr: str, value: Any) -> None:

        if isinstance(value, timedelta):

            hours = int(value.total_seconds()//3600)
            minutes = f"{int(value.total_seconds()/60%60):0>2}"
            seconds = f"{int(value.total_seconds()%60):0>2}"
            microseconds = f"{value.microseconds:0>6}"

            self._xmlElement.attrib[attr] = f"{hours}:{minutes}:{seconds}.{microseconds}"


#%%  GET INPUTS AND OUTPUTS_____________________________________________________________________________________________


    def __getXmlIOFiles__(self, attr: Any) -> Any:

        aux = {}

        element = self._xmlElement.find(attr)

        if element is not None:
            for subelement in element:

                #  It is a Path
                if "/" in subelement.text:
                    aux[subelement.attrib["role"]] = Input(biohubFile = Path(subelement.text),
                                                            role = subelement.attrib["role"])

                #  Is is an ID
                else:

                    if attr == "inputs":

                        try:
                            wrapper = Input(biohubFile = self.entity.files[subelement.text],
                                            role = subelement.attrib["role"])

                        except KeyError:

                            try:
                                wrapper = Input(biohubFile = self.entity.folders[subelement.text],
                                                role = subelement.attrib["role"])

                            except KeyError:
                                wrapper = Input(biohubFile = subelement.text,
                                                role = subelement.attrib["role"])
                    else:

                        try:
                            wrapper = Output(biohubFile = self.entity.files[subelement.text],
                                             role = subelement.attrib["role"])

                        except KeyError:

                            try:
                                wrapper = Output(biohubFile = self.entity.folders[subelement.text],
                                                 role = subelement.attrib["role"])

                            except KeyError:
                                wrapper = Output(biohubFile = subelement.text,
                                                 role = subelement.attrib["role"])

                    aux[subelement.attrib["role"]] = wrapper

        return aux


#%%  GET OPTIONS________________________________________________________________________________________________________


    def __getXmlOptions__(self, attr: Any) -> Any:

        aux = {}

        element = self._xmlElement.find(attr)

        if element is not None:

            for subelement in element:

                role = subelement.attrib["role"]

                for char in (" ", ":", "="):

                    if char in subelement.text:

                        name, value = subelement.text.split(char)
                        format = f"<name>{char}<value>"

                        aux[role] = Option(name = name,
                                            value = value,
                                            format = format,
                                            role = role)

                        break

                else:
                    name, value = subelement.text, True

                    aux[role] = Option(name = name,
                                        value = value,
                                        role = role)

        return aux


#%%  SET WRAPPERS_______________________________________________________________________________________________________

    def __setXmlWrapper__(self, attr: str, value: Any) -> None:

        container = ET.SubElement(self._xmlElement, attr)

        for subValue in value.values():

            subelement = ET.SubElement(container, singularize(attr))
            subelement.attrib["role"] = subValue.role

            if attr != "options": subelement.text = subValue.id
            else: subelement.text = str(subValue)