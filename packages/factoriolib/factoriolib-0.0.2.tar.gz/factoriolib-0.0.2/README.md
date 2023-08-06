# factoriolib

This repository contains a python package able to create and mainpulate factorio blueprint

## Usage

### Basics

In order to create simple blueprints you can simply create the entity objects needed and push them into the blueprint's entities list:

```py 
from factoriolib import entities
from factoriolib import blueprints
from factoriolib.core import Position, Direction

# Create a set of entity instances
transportBelt = entities.TransportBelt(
    position=Position(0.5, -0.5),
    direction=Direction(Direction.EAST)
)

inserter = entities.Inserter(
    position=Position(0.5, 0.5),
    direction=Direction(Direction.SOUTH)
)

chest = entities.WoodenChest(
    position=Position(0.5, 1.5)
)

pump = entities.Pump(
    position=Position(1.5, 0.5),
    direction=Direction(Direction.NORTH)
)

# create a blueprint instance
blueprint = blueprints.Blueprint()

# access the blueprint's entities and push all newly created entities into it
blueprint.entities().push(transportBelt, inserter, chest, pump)

# print the dict representation of the blueprint
print(blueprint.toDict())

# print the factorio exchange string
print(blueprint.exchangeString())
```

The generated exchange string can be imported into your game.

### Filters

Some entities such as chests may have logistics filters or a bar (the limit as to how many slots may be filled).

```py

from factoriolib import entities
from factoriolib import blueprints
from factoriolib.core import Position, LogisticFilter
from factoriolib.items import Wood, IronPlate

# Create a requester chest for wood and iron plates with a limit to 3 slots
chest = entities.LogisticChestRequester(
    position=Position(0.5, 0.5),
    bar=3
)

# add the filters (note that the index is 1 based)
chest.request_filters().push(
    LogisticFilter(Wood.name(), 1, 1337),
    LogisticFilter(IronPlate.name(), 2, 42),
)
```

### Circuit network

Entities that may be connected to a circuit network may be connected using the ConnectionMaker helper:

```py


from factoriolib import entities
from factoriolib import blueprints
from factoriolib.core import Position, CircuitCondition, Signal
from factoriolib.utility import ConnectionMaker
from factoriolib.items import Wood

pole = entities.MediumElectricPole(
    position=Position(0.5, 0.5)
)

inserter = entities.Inserter(
    position=Position(5.5, 0.5)
)

# set the stack size to 1
inserter.override_stack_size(1)

# set the circuit condition to wood signal greater than 1337
inserter.circuit_condition(
    CircuitCondition(
        first_signal=Signal(Wood.name(), type="item"),
        constant=1337,
        comparator=">"
    )
)

# connect both entities by red wire
ConnectionMaker.make(inserter, pole, "red")


```


