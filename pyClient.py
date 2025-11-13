#client file in python
#cs335

import socket
import struct
from pathlib import Path
import hashlib
import json
import os

class Metadata:
    def __init__(self, operation, fileLength, fileName):
        self.operation = operation
        self.fileLength = fileLength
        self.fileName = fileName
    
class FileCorruptedException(Exception):
    pass

class pyClient:
    def __init__(self, sock):
        self.socket = sock
        # self.socket.settimeout(10000)

    def add(self, serverFileName, localFilePath):
        self.sendDataToServerGetMessage(serverFileName, localFilePath, 1)

    def append(self, serverFileName, localFilePath):
        self.sendDataToServerGetMessage(serverFileName, localFilePath, 3)
    
    def fetch(self, serverFileName, localFilePath):
        try:
            fileToStore = Path(localFilePath)
            digest = hashlib.sha256()

            # send JSON metadata
            metadata = Metadata(2, 0, serverFileName)
            jsonString = json.dumps(metadata.__dict__)
            self._sendString(jsonString)

            # check if fetch is possible from server
            success = bool(ord(self.socket.recv(1)))

            if(success):
                incomingFileSize = self.socket.recv(8)
                fileSize = struct.unpack(">q", incomingFileSize)[0]

                buffer = 64 * 1024
                with open(fileToStore, 'wb') as f:
                    remaining = fileSize
                    while remaining > 0:
                        if(buffer < remaining):
                            chunk = self.socket.recv(buffer)
                        else:
                            chunk = self.socket.recv(remaining)
                        f.write(chunk)
                        digest.update(chunk)
                        remaining -= len(chunk)

                clientHash = digest.digest()

                # read hash length from server then read hash
                serverHashBytes = self.socket.recv(4)
                serverHashLength = struct.unpack('>i', serverHashBytes)[0]
                serverHash = self.socket.recv(serverHashLength)

                if(clientHash != serverHash):
                    raise FileCorruptedException()
                
                # if file not corrupted let server know
                # send true
                self.socket.send(b'\x01')

            self._readAndPrintIncomingMessage()
        except OSError as e:
            self._clientError(2)
        except socket.timeout as e:
            self._clientError(0)
        except FileCorruptedException as e:
            # send false to server and delete corrupted file
            self.socket.send(b'\x00')
            fileToStore.unlink()

    def quit(self):
        metadata = Metadata(4, 0, "")
        jsonString = json.dumps(metadata.__dict__)
        self._sendString(jsonString)
        self._readAndPrintIncomingMessage()

    def sendDataToServerGetMessage(self, serverFileName, localFilePath, operation):
        try:
            fileToSend = Path(localFilePath)
            digest = hashlib.sha256()

            # send JSON metadata
            fileSize = fileToSend.stat().st_size
            metadata = Metadata(operation, fileSize, serverFileName)
            jsonString = json.dumps(metadata.__dict__)
            self._sendString(jsonString)
            

            # check if file exists on server (for append)
            success = success = bool(ord(self.socket.recv(1)))

            if(success):
                # 64kb buffer
                buffer = 64 * 1024

                with open(localFilePath, 'rb') as f:
                    while True:
                        fileChunk = f.read(buffer)
                        if not fileChunk:
                            break
                        digest.update(fileChunk)
                        self.socket.sendall(fileChunk)

                # corrupt test case
                # digest.update(b"123")

                # digest hash and send to server
                hash = digest.digest()
                self._sendByteArray(hash)

            # print message from server
            self._readAndPrintIncomingMessage()

        except OSError as e:
            self._clientError(2)
        except socket.timeout as e:
            self._clientError(0)

    def _readAndPrintIncomingMessage(self):
        messageLength = self.socket.recv(4)
        length = int.from_bytes(messageLength, byteorder='big')
        message = b''
        while len(message) < length:
            msgChunk = self.socket.recv(length - len(message))
            if not msgChunk:
                break
            message += msgChunk

        print(message.decode('utf-8'))


    def _sendString(self, message):
        # send length then message
        message_bytes = message.encode('utf-8')
        self._sendByteArray(message_bytes)

    def _sendByteArray(self, array):
        self.socket.sendall(struct.pack('>i', len(array)))
        self.socket.sendall(array)
        
    def _clientError(self, messageType):
        match messageType:
            case 0: print("ERROR: Request timeout. Disconnecting from server.")
            case 1: print("ERROR: Cannot connect to server, the server may not be active.")
            case 2: print("ERROR: Specified file does not exist or path is invalid.")
            case _: print("ERROR: Something went wrong. Please contact administrator.")
            
# MAIN (I'm not used to this format...)

try:
    BASEDIR = Path(__file__).resolve().parent
    clientFilePath = BASEDIR / "clientFiles"
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    soc.connect(('localhost', 50777))
    print("Connected to server!")

    client = pyClient(soc)
    # (serverFileName, localFileName)
    # client.add("tomato.txt", clientFilePath / "tomato.txt")
    client.add("fatty.iso", clientFilePath / "big.iso")
    # client.append("tomato.txt", clientFilePath / "tomato.txt")

    # client.fetch("fatty.iso", clientFilePath / "big2.iso")
    # client.fetch("aliceSuperX.txt", clientFilePath / "aliceSuper.txt")
    client.quit()

except ConnectionRefusedError:
    print("ERROR: Could not connect to server, please make sure that the server is up and running. ")

