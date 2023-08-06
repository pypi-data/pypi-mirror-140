

from factoriolib.core import Connection, ConnectionData, ConnectionPoint
from factoriolib.entities import Entity


class ConnectionMaker:
    
    @staticmethod
    def make(entity1: Entity, entity2: Entity, color: str = "red", entity1Slot: int = 1, entity2Slot: int = 1):

        if entity1 == entity2 and entity1Slot == entity2Slot:

            raise Exception("Entities may not connect with themselves on the same slot.")

        entity1.checkConnectable()
        entity2.checkConnectable()


        entity1Data = ConnectionData(entity2.entity_number())
        entity2Data = ConnectionData(entity1.entity_number())


        entity1.addConnection(entity1Data)
        entity2.addConnection(entity2Data)