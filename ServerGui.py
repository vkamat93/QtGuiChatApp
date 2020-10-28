# import sys
# from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
# from PyQt5.QtWidgets import QApplication, QDialog
# from PyQt5.QtNetwork import QHostAddress, QTcpServer
#
# class Server(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.tcpServer = None
#
#     def sessionOpened(self):
#         self.tcpServer = QTcpServer(self)
#         PORT = 8000
#         address = QHostAddress('127.0.0.1')
#         if not self.tcpServer.listen(address, PORT):
#             print("cant listen!")
#             self.close()
#             return
#         self.tcpServer.newConnection.connect(self.dealCommunication)
#
#     def dealCommunication(self):
#         # Get a QTcpSocket from the QTcpServer
#         clientConnection = self.tcpServer.nextPendingConnection()
#         # instantiate a QByteArray
#         block = QByteArray()
#         # QDataStream class provides serialization of binary data to a QIODevice
#         out = QDataStream(block, QIODevice.ReadWrite)
#         # We are using PyQt5 so set the QDataStream version accordingly.
#         out.setVersion(QDataStream.Qt_5_0)
#         out.writeUInt16(0)
#         # this is the message we will send it could come from a widget.
#         message = "Goodbye!"
#         # get a byte array of the message encoded appropriately.
#         message = bytes(message, encoding='ascii')
#         # now use the QDataStream and write the byte array to it.
#         out.writeString(message)
#         out.device().seek(0)
#         out.writeUInt16(block.size() - 2)
#         # wait until the connection is ready to read
#         clientConnection.waitForReadyRead()
#         # read incomming data
#         instr = clientConnection.readAll()
#         # in this case we print to the terminal could update text of a widget if we wanted.
#         print(str(instr, encoding='ascii'))
#         # get the connection ready for clean up
#         clientConnection.disconnected.connect(clientConnection.deleteLater)
#         # now send the QByteArray.
#         clientConnection.write(block)
#         # now disconnect connection.
#         clientConnection.disconnectFromHost()
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     server = Server()
#     server.sessionOpened()
#     sys.exit(server.exec_())

#!/usr/bin/env python3

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *

PORT = 9999
SIZEOF_UINT32 = 4

class ServerDlg(QDialog):

    def __init__(self, parent=None):
        super(ServerDlg, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedWidth(800)

        self.tcpServer = QTcpServer(self)
        self.tcpServer.listen(self.tcpServer.serverAddress(), PORT)
        self.tcpServer.newConnection.connect(self.addConnection)
        self.connections = []

        self.btnClose = QPushButton("Close server")
        self.btnClose.clicked.connect(self.close)

        self.infoSpace = QTextBrowser()
        font = QFont("Times", 12, QFont.Cursive)
        self.infoSpace.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(self.infoSpace, alignment=Qt.AlignBottom)
        layout.addWidget(self.btnClose, alignment=Qt.AlignBottom)

        font = self.font()
        font.setPointSize(24)
        self.setFont(font)
        self.setWindowTitle("Server")
        self.setLayout(layout)

    def addConnection(self):
        self.clientConnection = self.tcpServer.nextPendingConnection()
        self.clientConnection.nextBlockSize = 0
        self.connections.append(self.clientConnection)
        self.infoSpace.append("[NEW CONNECTION]@ " +
                              self.clientConnection.peerAddress().toString() + " : " +
                              str(self.clientConnection.peerPort()) + " connected...")

        self.clientConnection.readyRead.connect(self.receiveMessage)
        self.clientConnection.disconnected.connect(self.removeConnection)
        self.clientConnection.error.connect(self.socketError)

    def receiveMessage(self):
        for s in self.connections:
            if s.bytesAvailable() > 0:
                stream = QDataStream(s)
                stream.setVersion(QDataStream.Qt_5_0)

                if s.nextBlockSize == 0:
                    if s.bytesAvailable() < SIZEOF_UINT32:
                        return
                    s.nextBlockSize = stream.readUInt32()
                if s.bytesAvailable() < s.nextBlockSize:
                    return

                textFromClient = stream.readQString()
                s.nextBlockSize = 0
                self.sendMessage(textFromClient,
                                 s.socketDescriptor())
                s.nextBlockSize = 0

    def sendMessage(self, text, socketId):
        for s in self.connections:
            if s.socketDescriptor().__int__() == socketId.__int__():
                message = "You> {}".format(text)
            else:
                message = "{}> {}".format(socketId.__int__(), text)
            reply = QByteArray()
            stream = QDataStream(reply, QIODevice.WriteOnly)
            stream.setVersion(QDataStream.Qt_5_0)
            stream.writeUInt32(0)
            stream.writeQString(message)
            stream.device().seek(0)
            stream.writeUInt32(reply.size() - SIZEOF_UINT32)
            s.write(reply)

    def removeConnection(self):
        pass

    def socketError(self):
        pass


app = QApplication(sys.argv)
form = ServerDlg()
form.show()
form.move(0, 0)
app.exec_()
