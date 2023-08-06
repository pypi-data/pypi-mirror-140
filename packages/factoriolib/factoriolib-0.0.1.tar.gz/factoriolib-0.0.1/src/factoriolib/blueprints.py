from factoriolib.tiles import Tile
from factoriolib.core import Color, DictableList, Icon, Version
from factoriolib.entities import Entity
from factoriolib._decorators import serialisable

@serialisable
class Blueprint:

    def __init__(self) -> None:
        
        self._labelColor: None|Color = None
        self._label: str = "Blueprint"
        self._entities: DictableList[Entity] = DictableList[Entity]()
        self._tiles: DictableList[Tile] = DictableList[Tile]()
        self._icons: DictableList[Icon] = DictableList[Icon]()
        self._version: Version = Version(1,1,53,0)

    def item(self) -> str:
        return "blueprint"

    def label(self, set: None|str = None) -> str:

        if set:

            self._label = set

        return self._label

    def label_color(self, set: None|Color = None) -> None|Color:

        if set:

            self._labelColor = set

        return self._labelColor

    def entities(self) -> DictableList[Entity]: 
        return self._entities

    def tiles(self) -> DictableList[Tile]: 
        return self._tiles

    def icons(self) -> DictableList[Icon]: 
        return self._icons

    def schedules(self): 
        pass # TODO:

    def version(self, set:None|Version = None) -> Version: 

        if set:

            self._version = set
        
        return self._version

    def toDict(self):

        result =  {
            "blueprint": {

                "item": self.item(),
                "version": self.version().toVersionCode(),
                "entities": self.entities().toDict(),
                "tiles": self.tiles().toDict(),
                "icons": self.icons().toDict(),
                "label": self.label(),
            }
        }

        if self.label_color():
            result["label_color"] = self.label_color().toDict()

        return result
