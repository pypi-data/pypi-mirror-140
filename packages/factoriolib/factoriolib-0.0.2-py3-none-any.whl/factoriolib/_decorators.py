from factoriolib.strings import dictToExchangeString


def id(id: int):

    def idDecorator(classDefinition):

        @staticmethod
        def newIdGetter():

            return id

        classDefinition.id = newIdGetter
        return classDefinition

    return idDecorator

def connects(classDefinition):

    @staticmethod
    def canConnect() :

        return True

    classDefinition.canConnect = canConnect

    return classDefinition

def name(name):

    def nameDecorator(classDefinition):

        @staticmethod
        def newNameGetter() -> str:

            return name

        classDefinition.name = newNameGetter

        return classDefinition

    return nameDecorator

def serialisable(classDefinition):

    def exchangeString(self) -> str:

        return dictToExchangeString(self.toDict())

    classDefinition.exchangeString = exchangeString

    return classDefinition