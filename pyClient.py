#client file in python
#cs335

import socket
import struct
from pathlib import Path
import hashlib

class pyClient:
    def __init__(self, socket):
        self.socket = socket
        socket.settimeout(10000)
    
def add(serverFileName, localFilePath):
    sendDataToServerGetMessage(serverFileName, localFilePath, 1)

def sendDataToServerGetMessage(serverFileName, localFilePath, operation):
    try:
        fileToSend = Path(localFilePath)
        digest = hashlib.sha256()

        # send operation code
        soc.send(struct.pack('>i', operation))

        # send fileName
        _sendString(serverFileName)
        
    except OSError as e:
        _clientError(1)
    except socket.timeout as e:
        _clientError(0)

def _sendString(message):
    # send length then message
    message_bytes = message.encode('utf-8')
    _sendByteArray(message_bytes)

def _sendByteArray(array):
    soc.send(struct.pack('>i', array.len))
    soc.send(struct.pack('>i'), array)
    
def _clientError(messageType):
    match messageType:
        case 0: print("ERROR: Request timeout. Disconnecting from server.")
        case 1: print("ERROR: Cannot connect to server, the server may not be active.")
        case _: print("ERROR: Something went wrong. Please contact administrator.")
            
        

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(('localhost', 50777))
print("Connected to server!")

client = pyClient(soc)
client.add("alice.txt", "alice.txt")

