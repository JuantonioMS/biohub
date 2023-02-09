from biohub.utils import BioHubContainer

class Subject(BioHubContainer):


    def newId(self):
        return "bhSJ" + super().newId()