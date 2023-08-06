import base64
import json
import zlib

def stringToJsonBytes(exchangeString):

    versionByte = exchangeString[0] # currently always zero
    payload = exchangeString[1:]
    decodedString = base64.b64decode(payload)
    decompressedData = zlib.decompress(decodedString)

    return decompressedData

def stringToJsonString(exchangeString):

    return stringToJsonBytes(exchangeString).decode("utf-8")

def stringToDict(exchangeString):

    jsonContent = stringToJsonBytes(exchangeString)

    return json.loads(jsonContent)

def jsonStringToExchangeString(jsonString: str) -> str:

    jsonBytes = jsonString.encode("utf-8")
    compressedJson = zlib.compress(jsonBytes, 9)
    encodedString = "0" + base64.b64encode(compressedJson).decode("utf-8")

    return encodedString


def dictToExchangeString(dict: dict) -> str:

    jsonString = json.dumps(dict)
    jsonBytes = jsonString.encode("utf-8")
    compressedJson = zlib.compress(jsonBytes, 9)
    encodedString = "0" + base64.b64encode(compressedJson).decode("utf-8")

    return encodedString
