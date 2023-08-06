from factoriolib.core import Position


class Tile:

    def name(self) -> str:

        return "tile"

    def position(self, set: Position|None = None) -> Position:

        if set:

            self._position = set

        return self._position