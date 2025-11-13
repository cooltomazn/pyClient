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
    
    def sendDataToServerGetMessage(self, serverFileName, localFilePath, operation):
        try:
            fileToSend = Path(localFilePath)
            digest = hashlib.sha256()

            # send operation code
            soc.send(struct.pack('>i', operation))

            # send fileName
            self._sendString(serverFileName)

            # send file size
            fileSize = fileToSend.stat().st_size
            soc.send(fileSize.to_bytes(8, byteorder='big'))

            # check if fetch is possible from server
            success = success = bool(ord(soc.recv(1)))

            if(success):
                # 64kb buffer
                buffer = 64 * 1024

                with open(localFilePath, 'rb') as f:
                    while True:
                        fileChunk = f.read(buffer)
                        if not fileChunk:
                            break
                        digest.update(fileChunk)
                        soc.send(fileChunk)

            # corrupt test case
            # digest.update(b"123")
            
            # digest hash and send to server
            hash = digest.digest()
            self._sendByteArray(hash)

            # print message from server
            self._readAndPrintIncomingMessage()

        except OSError as e:
            self._clientError(1)
        except socket.timeout as e:
            self._clientError(0)

    def _readAndPrintIncomingMessage(self):
        messageLength = soc.recv(4)
        length = int.from_bytes(messageLength, byteorder='big')
        message = b''
        while len(message) < length:
            msgChunk = soc.recv(length - len(message))
            if not msgChunk:
                break
            message += msgChunk

        print(message.decode('utf-8'))

    def add(self, serverFileName, localFilePath):
        self.sendDataToServerGetMessage(serverFileName, localFilePath, 1)
    
    def _sendString(self, message):
        # send length then message
        message_bytes = message.encode('utf-8')
        self._sendByteArray(message_bytes)

    def _sendByteArray(self, array):
        soc.send(struct.pack('>i', len(array)))
        soc.sendall(array)
        
    def _clientError(self, messageType):
        match messageType:
            case 0: print("ERROR: Request timeout. Disconnecting from server.")
            case 1: print("ERROR: Cannot connect to server, the server may not be active.")
            case _: print("ERROR: Something went wrong. Please contact administrator.")
            
# MAIN (I'm not used to this format...)

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(('localhost', 50777))
print("Connected to server!")

client = pyClient(soc)
client.add("bunny-2.jpg", "bunny-2.jpg")

