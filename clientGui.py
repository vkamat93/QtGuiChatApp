# from PyQt5.QtCore import QDataStream, QIODevice
# from PyQt5.QtWidgets import QApplication, QDialog
# from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket
#
# class Client(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.tcpSocket = QTcpSocket(self)
#         self.blockSize = 0
#         self.makeRequest()
#         self.tcpSocket.waitForConnected(1000)
#         # send any message you like it could come from a widget text.
#         self.tcpSocket.write(b'hello')
#         self.tcpSocket.readyRead.connect(self.dealCommunication)
#         self.tcpSocket.error.connect(self.displayError)
#
#     def makeRequest(self):
#         HOST = '127.0.0.1'
#         PORT = 8000
#         self.tcpSocket.connectToHost(HOST, PORT, QIODevice.ReadWrite)
#
#     def dealCommunication(self):
#         instr = QDataStream(self.tcpSocket)
#         instr.setVersion(QDataStream.Qt_5_0)
#         if self.blockSize == 0:
#             if self.tcpSocket.bytesAvailable() < 2:
#                 return
#             self.blockSize = instr.readUInt16()
#         if self.tcpSocket.bytesAvailable() < self.blockSize:
#             return
#         # Print response to terminal, we could use it anywhere else we wanted.
#         print(str(instr.readString(), encoding='ascii'))
#
#     def displayError(self, socketError):
#         if socketError == QAbstractSocket.RemoteHostClosedError:
#             pass
#         else:
#             print(self, "The following error occurred: %s." % self.tcpSocket.errorString())
#
#
# if __name__ == '__main__':
#     import sys
#
#     app = QApplication(sys.argv)
#     client = Client()
#     sys.exit(client.exec_())

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *

PORT = 9999
SIZEOF_UINT32 = 4

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__()

        # Ititialize socket
        self.socket = QTcpSocket()

        # Initialize data IO variables
        self.nextBlockSize = 0
        self.request = None

        # Create widgets/layout
        self.browser = QTextBrowser()
        self.lineedit = QLineEdit("Enter text here, dummy")
        self.lineedit.selectAll()
        self.connectButton = QPushButton("Connect")
        self.connectButton.setEnabled(True)
        layout = QVBoxLayout()
        layout.addWidget(self.browser, alignment=Qt.AlignJustify)
        layout.addWidget(self.lineedit, alignment=Qt.AlignJustify)
        layout.addWidget(self.connectButton, alignment=Qt.AlignBottom)
        self.setLayout(layout)
        self.lineedit.setFocus()

        # Signals and slots for line edit and connect button
        self.lineedit.returnPressed.connect(self.issueRequest)
        self.connectButton.clicked.connect(self.connectToServer)

        self.setWindowTitle("Client")
        # Signals and slots for networking
        self.socket.readyRead.connect(self.readFromServer)
        self.socket.disconnected.connect(self.serverHasStopped)
        self.socket.error.connect(self.serverHasError)


    # Update GUI
    def updateUi(self, text):
        self.browser.append(text)

    # Create connection to server
    def connectToServer(self):
        self.connectButton.setEnabled(False)
        self.socket.connectToHost("192.168.178.26", PORT)

    def issueRequest(self):
        self.request = QByteArray()
        stream = QDataStream(self.request, QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_0)
        stream.writeUInt32(0)
        stream.writeQString(self.lineedit.text())
        stream.device().seek(0)
        stream.writeUInt32(self.request.size() - SIZEOF_UINT32)
        self.socket.write(self.request)
        self.nextBlockSize = 0
        self.request = None
        self.lineedit.setText("")

    def readFromServer(self):
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_0)

        while True:
            if self.nextBlockSize == 0:
                if self.socket.bytesAvailable() < SIZEOF_UINT32:
                    break
                self.nextBlockSize = stream.readUInt32()
            if self.socket.bytesAvailable() < self.nextBlockSize:
                break
            textFromServer = stream.readQString()
            self.updateUi(textFromServer)
            self.nextBlockSize = 0

    def serverHasStopped(self):
        self.socket.close()
        self.connectButton.setEnabled(True)

    def serverHasError(self):
        self.updateUi("Error: {}".format(self.socket.errorString()))
        self.socket.close()
        self.connectButton.setEnabled(True)

    # when user clicks on x
    def closeEvent(self, QCloseEvent):
        self.socket.close()
        self.close()


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
