from factoriolib._decorators import name, connects
from factoriolib.core import CircuitCondition, CircuitParameters, Connection, ConnectionData, DictableDict, DictableList, Direction, LogisticFilter, Position, SpeakerAlertParameters, SpeakerParameters


class Entity:

    CREATED_COUNT = 0

    def __init__(self, position: Position|None=None, direction: Direction|None = None):

        Entity.CREATED_COUNT += 1
        self._entityNumber = Entity.CREATED_COUNT
        self._position = position if position else Position()
        self._direction = direction if direction else Direction()

        #TODO: check how to handle those
        self._circuitCondition: None|CircuitCondition = None
        self._circuitParameters: None|CircuitParameters = None

        if self.canConnect():

            self._connections: Connection = Connection()

    @staticmethod
    def name() -> str: return "entity"  

    def entity_number(self, set: int|None=None) -> int: 
        
        if set:

            self._entityNumber = set

        return self._entityNumber


    def position(self, set: Position|None = None) -> Position: 

        if set:

            self._position = set

        return self._position

    def direction(self, set: Direction|None = None) -> Direction: 

        if set:

            self._direction = set

        return self._direction

    def toDict(self):

        result =  {
            "name": self.name(),
            "entity_number": self.entity_number(),
            "position": self.position().toDict(),
            "direction": self.direction().toDict()
        }

        if self.canConnect():

            result["connections"] = self.connections().toDict()

        if self.circuit_condition() or self.circuit_parameters():

            result["control_behavior"] = {}

        if self.circuit_condition():

            result["control_behavior"]["circuit_condition"] = self.circuit_condition().toDict()

        if self.circuit_parameters():

            result["control_behavior"]["circuit_parameters"] = self.circuit_parameters().toDict()

        return result

    def circuit_parameters(self, set: None|CircuitParameters = None):

        if set:

            self._circuitParameters = set

        return self._circuitParameters

    def circuit_condition(self, set: None|CircuitCondition = None):

        if set:

            self._circuitCondition = set

        return self._circuitCondition

    def addConnection(self, connection: ConnectionData, slot: int = 1 , color: str = "red" ):

        self.checkConnectable()

        if slot == 1:

            self._connections.one().addConnection(connection, color=color)

        else: 

            self._connections.two().addConnection(connection, color=color)

    
    def checkConnectable(self):

        if not self.canConnect():

            raise Exception("This entity cannot form circuit connections.")

    def connections(self):

        self.checkConnectable()

        return self._connections

    @staticmethod
    def canConnect():

        return False

class Container(Entity):

    def __init__(self, bar: int|None = None, position: Position|None=None):

        super().__init__(position=position)
        self._bar: int|None = bar

    def bar(self, set: int|None = None): 

        if set:

            self._bar = set

        return self._bar

    def toDict(self):

        result = super().toDict()

        if self.bar():

            result["bar"] = self.bar()

        return result

class LogisticContainer(Container):

    def __init__(self, bar: int | None = None, position: Position|None = None, requestFilters: DictableList[LogisticFilter]|None=None):
        
        super().__init__(bar, position)
        self._requestFilters: DictableList[LogisticFilter] = requestFilters if requestFilters else DictableList[LogisticFilter]()

    def request_filters(self):

        return self._requestFilters

    def toDict(self):

        result = super().toDict()

        result["request_filters"] = self.request_filters().toDict()

        return result


### Actual entities


class BasicInserter(Entity):

    def __init__(self, override_stack_size: int|None=None, **kwargs):

        super().__init__(**kwargs)

        self._overrideStackSize: int|None = override_stack_size

    def override_stack_size(self, set:int|None= None) -> int|None:

        if set:

            self._overrideStackSize = set

        return self._overrideStackSize

    def toDict(self):

        result = super().toDict()

        if self.override_stack_size():

            result["override_stack_size"] = self.override_stack_size()

        return result







@name("accumulator")
class Accumulator(Entity): pass

@name("arithmetic-combinator")
class ArithmeticCombinator(Entity): pass

@name("artillery-turret")
class ArtilleryTurret(Entity): pass

@name("assembling-machine-1")
class AssemblingMachine1(Entity): pass

@name("assembling-machine-2")
class AssemblingMachine2(Entity): pass

@name("assembling-machine-3")
class AssemblingMachine3(Entity): pass

@name("beacon")
class Beacon(Entity): pass

@name("big-electric-pole")
class BigElectricPole(Entity): pass

@name("boiler")
class Boiler(Entity): pass

@name("burner-generator")
class BurnerGenerator(Entity): pass

@name("burner-inserter")
class BurnerInserter(Entity): pass

@name("burner-mining-drill")
class BurnerMiningDrill(Entity): pass

@name("centrifuge")
class Centrifuge(Entity): pass

@name("chemical-plant")
class ChemicalPlant(Entity): pass

@name("concrete")
class Concrete(Entity): pass

@name("constant-combinator")
class ConstantCombinator(Entity): pass

@name("decider-combinator")
class DeciderCombinator(Entity): pass

@name("electric-energy-interface")
class ElectricEnergyInterface(Entity): pass

@name("electric-furnace")
class ElectricFurnace(Entity): pass

@name("electric-mining-drill")
class ElectricMiningDrill(Entity): pass

@name("express-loader")
class ExpressLoader(Entity): pass

@name("express-splitter")
class ExpressSplitter(Entity): pass

@name("express-transport-belt")
class ExpressTransportBelt(Entity): pass

@name("express-underground-belt")
class ExpressUndergroundBelt(Entity): pass

@name("fast-inserter")
class FastInserter(Entity): pass

@name("fast-loader")
class FastLoader(Entity): pass

@name("fast-splitter")
class FastSplitter(Entity): pass

@name("fast-transport-belt")
class FastTransportBelt(Entity): pass

@name("fast-underground-belt")
class FastUndergroundBelt(Entity): pass

@name("filter-inserter")
class FilterInserter(Entity): pass

@name("flamethrower-turret")
class FlamethrowerTurret(Entity): pass

@name("gate")
class Gate(Entity): pass

@name("gun-turret")
class GunTurret(Entity): pass

@name("hazard-concrete")
class HazardConcrete(Entity): pass

@name("heat-exchanger")
class HeatExchanger(Entity): pass

@name("heat-interface")
class HeatInterface(Entity): pass

@name("heat-pipe")
class HeatPipe(Entity): pass

@name("infinity-chest")
class InfinityChest(Entity): pass

@name("infinity-pipe")
class InfinityPipe(Entity): pass

@connects
@name("inserter")
class Inserter(BasicInserter): pass

@name("iron-chest")
class IronChest(Entity): pass

@name("item-unknown")
class ItemUnknown(Entity): pass

@name("lab")
class Lab(Entity): pass

@name("land-mine")
class LandMine(Entity): pass

@name("landfill")
class Landfill(Entity): pass

@name("laser-turret")
class LaserTurret(Entity): pass

@name("linked-belt")
class LinkedBelt(Entity): pass

@name("linked-chest")
class LinkedChest(Entity): pass

@name("loader")
class Loader(Entity): pass

@name("logistic-chest-active-provider")
class LogisticChestActiveProvider(Entity): pass

@name("logistic-chest-buffer")
class LogisticChestBuffer(Entity): pass

@name("logistic-chest-passive-provider")
class LogisticChestPassiveProvider(Entity): pass

@name("logistic-chest-requester")
class LogisticChestRequester(LogisticContainer): pass

@name("logistic-chest-storage")
class LogisticChestStorage(Entity): pass

@name("long-handed-inserter")
class LongHandedInserter(Entity): pass

@connects
@name("medium-electric-pole")
class MediumElectricPole(Entity): pass

@name("nuclear-reactor")
class NuclearReactor(Entity): pass

@name("offshore-pump")
class OffshorePump(Entity): pass

@name("oil-refinery")
class OilRefinery(Entity): pass

@name("pipe")
class Pipe(Entity): pass

@name("pipe-to-ground")
class PipeToGround(Entity): pass

@name("player-port")
class PlayerPort(Entity): pass

@name("power-switch")
class PowerSwitch(Entity): pass

@connects
@name("programmable-speaker")
class ProgrammableSpeaker(Entity):

    def __init__(self, position: Position|None = None, parameters: SpeakerParameters|None = None, alert_parameters: SpeakerAlertParameters|None = None):

        super().__init__(position)

        self._parameters = parameters if parameters else SpeakerParameters()
        self._alertParameters = alert_parameters if alert_parameters else SpeakerAlertParameters()

    def parameters(self, set: None|SpeakerParameters = None) -> SpeakerParameters:

        if set:

            self._parameters = set

        return self._parameters

    def alert_parameters(self, set: None|SpeakerAlertParameters = None) -> SpeakerAlertParameters:

        if set:

            self._alertParameters = set

        return self._alertParameters

    def toDict(self):

        result = super().toDict()

        result["parameters"] = self.parameters().toDict()
        result["alert_parameters"] = self.alert_parameters().toDict()

        return result

@name("pump")
class Pump(Entity): pass

@name("pumpjack")
class Pumpjack(Entity): pass

@name("radar")
class Radar(Entity): pass

@name("rail-chain-signal")
class RailChainSignal(Entity): pass

@name("rail-signal")
class RailSignal(Entity): pass

@name("red-wire")
class RedWire(Entity): pass

@name("refined-concrete")
class RefinedConcrete(Entity): pass

@name("refined-hazard-concrete")
class RefinedHazardConcrete(Entity): pass

@name("roboport")
class Roboport(Entity): pass

@name("rocket-silo")
class RocketSilo(Entity): pass

@name("simple-entity-with-force")
class SimpleEntityWithForce(Entity): pass

@name("simple-entity-with-owner")
class SimpleEntityWithOwner(Entity): pass

@name("small-electric-pole")
class SmallElectricPole(Entity): pass

@name("small-lamp")
class SmallLamp(Entity): pass

@name("solar-panel")
class SolarPanel(Entity): pass

@name("splitter")
class Splitter(Entity): pass

@name("stack-filter-inserter")
class StackFilterInserter(Entity): pass

@name("stack-inserter")
class StackInserter(Entity): pass

@name("steam-engine")
class SteamEngine(Entity): pass

@name("steam-turbine")
class SteamTurbine(Entity): pass

@name("steel-chest")
class SteelChest(Entity): pass

@name("steel-furnace")
class SteelFurnace(Entity): pass

@name("steel-plate")
class SteelPlate(Entity): pass

@name("stone-brick")
class StoneBrick(Entity): pass

@name("stone-furnace")
class StoneFurnace(Entity): pass

@name("stone-wall")
class StoneWall(Entity): pass

@name("storage-tank")
class StorageTank(Entity): pass

@name("substation")
class Substation(Entity): pass

@name("train-stop")
class TrainStop(Entity): pass

@name("transport-belt")
class TransportBelt(Entity): pass

@name("underground-belt")
class UndergroundBelt(Entity): pass

@name("wooden-chest")
class WoodenChest(Entity): pass

