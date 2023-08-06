from multiprocessing.connection import Connection
from typing import List


class DictableList:

    def __class_getitem__(cls, ClassType):

        class Result:

            def __init__(self):

                self._items: List[ClassType] = []

            def toDict(self):

                return [element.toDict() for element in self._items]

            def push(self, *items: ClassType|None) -> 'Result':

                for item in items:
                    self._items.append(item)

                return self

        return Result


class DictableDict:

    def __class_getitem__(cls, ClassType):

        class Result:

            def __init__(self):

                self._items: dict[ClassType] = {}

            def toDict(self):

                return { key: element.toDict() for key, element in self._items.items() }

            def set(self, key, item: ClassType|None) -> 'Result':

                self._items[key] = item
                return self

        return Result


class Color:

    def __init__(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 0.0):

        self._r: float = r
        self._b: float = g
        self._g: float = b
        self._a: float = a

    def r(self, set=None) -> float:

        if set:

            self._r = set

        return self._r

    def g(self, set=None) -> float:

        if set:

            self._g = set

        return self._g

    def b(self, set=None) -> float:

        if set:

            self._b = set

        return self._b

    def a(self, set=None) -> float:

        if set:

            self._a = set

        return self._a

    def toDict(self):

        return {

            "r": self.r(),
            "g": self.g(),
            "b": self.b(),
            "a": self.a(),
        }

class Position:

    def __init__(self, x: float = 0.0, y: float = 0.0):

        self._x: float = x
        self._y: float = y

    def x(self, set: float|None = None) -> float:

        if set:

            self._x = set

        return self._x

    def y(self, set: float|None = None) -> float:

        if set:

            self._y = set

        return self._y

    def toDict(self) -> dict:

        return {

            "x": self.x(),
            "y": self.y()
        }

class Direction:

    NORTH = 0
    SOUTH = 4
    EAST  = 2
    WEST  = 6

    def __init__(self, value: int=0):

        self._value: int = value

    def value(self, set: int|None = None) -> int:

        if set:

            self._value = set

        return self._value

    def toDict(self) -> dict:

        return self._value

class Signal:

    def __init__(self, name: str, type: str):

        self._name: int = name
        self._type: Signal = type

    def name(self, set: str|None = None): 
        
        if set:

            self._name = set

        return self._name

    def type(self, set: str|None = None): 

        if set:

            self._type = set

        return self._type 

    def toDict(self):

        return {
            "name": self.name(),
            "type": self.type(),
        }

class Icon:

    def __init__(self, index: int, signal: Signal):

        self._index: int = index
        self._signal: Signal = signal

    def index(self, set: int|None = None) -> int:

        if set:

            self._index = set

        return self._index

    def signal(self, set: Signal|None = None) -> Signal:

        if set:

            self._signal = set

        return self._signal

class Version:

    def __repr__(self) -> str:

        return f'Version {self._major}.{self._minor}.{self._patch}.{self._developer}'

    def __init__(self, major: int, minor: int, patch: int, developer: int):

        self._major: int = major
        self._minor: int = minor
        self._patch: int = patch
        self._developer: int = developer

    def toVersionCode(self) -> str:

        return self._major << 48 | self._minor << 32 | self._patch << 16 | self._developer

    @staticmethod
    def fromVersionCode(code: int) -> 'Version':

        return Version(
            (code >> 48) % (1 << 16),
            (code >> 32) % (1 << 16),
            (code >> 16) % (1 << 16),
            (code >> 0) % (1 << 16)
        )

class LogisticFilter:

    def __init__(self, name: str, index: int, count: int) -> None:
        
        self._name: str = name
        self._index: int = index
        self._count: int = count

    def name(self, set:str|None = None) -> str:

        if set:

            self._name = set

        return self._name

    def index(self, set:int|None = None) -> int:

        if set:

            self._index = set

        return self._index
        
    def count(self, set:int|None = None) -> int:

        if set:

            self._count = set

        return self._count

    def toDict(self):

        return {

            "name": self.name(),
            "index": self.index(),
            "count": self.count()
        }


class SpeakerParameters:

    def __init__(self, playback_volume: float = 1.0, playback_globally: bool = False, allow_polyphony: bool = False):

        self._playbackVolume = playback_volume
        self._playbackGlobally = playback_globally
        self._allowPolyphony = allow_polyphony

    def playback_volume(self, set: None|float = None) -> float:

        if set:

            self._playbackVolume = set

        return self._playbackVolume

    def playback_globally(self, set: None|bool = None) -> bool:

        if set:

            self._playbackGlobally = set

        return self._playbackGlobally

    def allow_polyphony(self, set: None|bool = None) -> bool:

        if set:

            self._allowPolyphony = set

        return self._allowPolyphony

    def toDict(self):

        return {
            "playback_volume": self.playback_volume(),
            "playback_globally": self.playback_globally(),
            "allow_polyphony": self.allow_polyphony(),
        }

class SpeakerAlertParameters:

    def __init__(self, show_alert: bool = False, show_on_map: bool = False, icon_signal_id: Signal|None = None, alert_message: str|None = None):

        self._showAlert = show_alert
        self._showOnMap = show_on_map
        self._iconSignalId = icon_signal_id
        self._alertMessage = alert_message

    def show_alert(self, set: None|bool = None) -> bool:

        if set:

            self._showAlert = set

        return self._showAlert

    def show_on_map(self, set: None|bool = None) -> bool:

        if set:

            self._showOnMap = set

        return self._showOnMap

    def icon_signal_id(self, set: None|Signal = None) -> Signal:

        if set:

            self._iconSignalId = set

        return self._iconSignalId

    def alert_message(self, set: None|str = None) -> str:

        if set:

            self._alertMessage = set

        return self._alertMessage

    def toDict(self):

        result = {
            "show_alert": self.show_alert(),
            "show_on_map": self.show_on_map(),
        }

        if self.icon_signal_id():

            result["icon_signal_id"] = self.icon_signal_id()

        if self.alert_message():

            result["alert_message"] = self.alert_message()

        return result

class ConnectionData:

    # TODO: find out what circuit_id does
    def __init__(self, entity_id: int, circuit_id: int|None = None): 

        self._entityId = entity_id

    def entity_id(self, set: int|None=None) -> int:

        if set:

            self._entityId = set

        return self._entityId

    def toDict(self):

        result = {
            "entity_id": self.entity_id()
        }

        return result



class ConnectionPoint:

    # TODO: find out what circuit_id does
    def __init__(self): 

        self._red: DictableList[ConnectionData] = DictableList[ConnectionData]() 
        self._green: DictableList[ConnectionData] = DictableList[ConnectionData]() 

    def red(self) -> 'DictableList[ConnectionData]':

        return self._red

    def green(self) -> 'DictableList[ConnectionData]':

        return self._green

    def toDict(self):

        result = {
            "red": self.red().toDict(),
            "green": self.green().toDict(),
        }

        return result

    def addConnection(self, connection: ConnectionData, color: str = "red"):

        if color == "red":

            self.red().push(connection)

        else: 

            self.green().push(connection)



class CircuitCondition:

    def __init__(self, first_signal: None|Signal = None, second_signal: None|Signal = None, constant: int|None = None, comparator: str = ">"):

        self._firstSignal: None|Signal = first_signal
        self._secondSignal: None|Signal = second_signal
        self._constant: int|None = constant
        self._comparator: str = comparator

    def first_signal(self) -> None|Signal:

        return self._firstSignal

    def second_signal(self) -> None|Signal:

        return self._secondSignal

    def constant(self) -> None|int:

        return self._constant

    def comparator(self) -> str:

        return self._comparator

    def toDict(self):

        if self.first_signal() and self.second_signal():

            return {

                "first_signal": self.first_signal().toDict(),
                "second_signal": self.second_signal().toDict(),
                "comparator": self.comparator()
            }

        else:

            return {

                "first_signal": self.first_signal().toDict(),
                "constant": self.constant() if self.constant() else 0,
                "comparator": self.comparator()
            }


class CircuitParameters:

    def __init__(
        self, 
        signal_value_is_pitch:  None|bool = None, 
        instrument_id: None|int = None, 
        note_id: None|int = None
    ):

        self._signalValueIsPitch: None|bool = signal_value_is_pitch
        self._instrumentId: None|int = instrument_id
        self._noteId: int|None = note_id

    def signal_value_is_pitch(self) -> None|bool:

        return self._signalValueIsPitch

    def instrument_id(self) -> None|int:

        return self._instrumentId

    def note_id(self) -> None|int:

        return self._noteId

    def toDict(self):

        result = {}

        if self.signal_value_is_pitch():

            result["signal_value_is_pitch"] = self.signal_value_is_pitch()

        if self.instrument_id():

            result["instrument_id"] = self.instrument_id()

        if self.note_id():

            result["note_id"] = self.note_id()

        return result





class Connection:

    # TODO make connection points optional
    def __init__(self, one: ConnectionPoint|None = None, two: ConnectionPoint|None = None): 

        self._1: ConnectionPoint = one if one else ConnectionPoint()
        self._2: ConnectionPoint = two if two else ConnectionPoint()

    def one(self) -> ConnectionPoint:

        return self._1

    def two(self) -> ConnectionPoint:

        return self._2

    def toDict(self):

        # TODO: only list set points

        result = {
            "1": self.one().toDict(),
            "2": self.two().toDict(),
        }

        return result

