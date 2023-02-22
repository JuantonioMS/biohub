from biohub.file import File

from xml.etree import ElementTree as ET

class Xml(File):


    def __init__(self,
                 xmlElement: ET.Element = ET.Element("file"),
                 **attrs) -> None:

        super().__init__(xmlElement, **attrs)

        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()

        #self.parent_map = dict((c, p) for p in iter(self.root) for c in p)



    def _goDeep(self, node, deep = 1):

        aux = set()

        if list(node):
            for son in node: aux.add(self._goDeep(son, deep = deep + 1))
        else: return deep

        return max(aux)



    @property
    def depth(self): return self._goDeep(self.root)



    def get(self,
            tag: str = "",
            filt: dict = {}):

        prefix = "."

        count = 0
        while True:

            candidates = self.root.findall(f"{prefix}{tag}")

            if candidates: break
            else: prefix += "/"

            count += 1
            if count == self.depth: return []


        if not filt: return candidates

        else:

            for name, condition in filt.items():

                potentials = []
                for candidate in candidates:

                    #  Attrib section
                    if "@" == name[0]:

                        if name[1:] in candidate.attrib:
                            if candidate.attrib[name[1:]] == condition: potentials.append(candidate)

                    #  Container section
                    elif "#" == name[0]:

                        son = candidate.find(name[1:])
                        if son:

                            if len(set(condition).intersection(set([i.text for i in son]))) == len(set(condition)):
                                potentials.append(candidate)

                    #  Standar section
                    else:

                        sons = candidate.findall(name)
                        for son in sons:
                            if son.text == condition: potentials.append(candidate)
                            break

                candidates = potentials.copy()

            return potentials



    def remove(self,
               tag: str = "",
               filt: dict = {}):

        candidates = self.get(tag = tag,
                              filt = filt)

        if not isinstance(candidates, list):
            candidates = [candidates]

        nodes = [self.root]
        while nodes:

            aux = []
            for node in nodes:
                for candidate in candidates:
                    if candidate in list(node): node.remove(candidate)

                for subelement in node: aux.append(subelement)

            nodes = aux



    def add(self,
            parentTag: str = "",
            parentFilt: dict = {},
            tag: str = "",
            text: str = "",
            attribs: dict = {}):

        if not parentTag: candidates = [self.root]

        else:
            candidates = self.get(tag = parentTag,
                                  filt = parentFilt)

        for candidate in candidates if isinstance(candidates, list) else [candidates]:
            subelement = ET.SubElement(candidate, tag, attrib = attribs)
            subelement.text = text



    def edit(self,
             origianlTag: str = "",
             filt: dict = {},
             tag: str = "",
             text: str = "",
             attribs: dict = {}):

        candidates = self.get(tag = origianlTag,
                              filt = filt)

        for candidate in candidates if isinstance(candidates, list) else [candidates]:

            if tag: candidate.tag = tag
            if text: candidate.text = text
            if attribs: candidate.attrib.update(attribs)



    def trim(self,
             origianlTag: str = "",
             filt: dict = {},
             text: bool = False,
             attribs: bool = False):

        candidates = self.get(tag = origianlTag,
                              filt = filt)

        for candidate in candidates if isinstance(candidates, list) else [candidates]:

            if text: candidate.text = ""

            if attribs:

                if isinstance(attribs, bool): candidate.attrib =  {}

                else:
                    if isinstance(attribs, str):
                        attribs = [attribs]

                    for attrib in attribs:
                        if attrib in candidate.attrib: del candidate.attrib[attrib]