from biohub.utils import BioHubClass

import xml.etree.ElementTree as ET


class Pipeline(BioHubClass):


    def newId(self, buffer = []):
        return "bhPL" + super().newId(buffer)
