import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import socket
from PyQt5.QtCore import *
import time
import threading

FORMAT = 'utf-8'
DISCONNECT_MSG = "!Disconnect"
PORT = 5050  # IMP: Should be the same as that on the server side!
SERVER = "192.168.178.26"  # local IPV4 address
ADDR = (SERVER, PORT)
client_conn_success = 44444  # default non zero return value for client connection status

class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Client ChatApp')
        self.setFixedWidth(600)
        self.setFixedHeight(800)
        self.setStyleSheet("""
            QLineEdit{
                font-size: 30px
            }
            QPushButton{
                font-size: 30px
            }
            """)
        mainLayout = QVBoxLayout()

        self.usernameLabel = QLabel()
        self.usernameLabel.setFont(QFont('Arial', 20))
        mainLayout.addWidget(self.usernameLabel)

        self.chatArea = QPlainTextEdit()
        self.chatArea.setFont(QFont('Arial', 18))
        self.chatArea.setReadOnly(1)
        mainLayout.addWidget(self.chatArea)

        self.typingSpace = QLineEdit()
        mainLayout.addWidget(self.typingSpace)

        self.sendButton = QPushButton('Send Message')
        self.sendButton.clicked.connect(self.sendMessage)
        mainLayout.addWidget(self.sendButton)

        self.closeButton = QPushButton('Close')
        self.closeButton.clicked.connect(self.destroy)
        mainLayout.addWidget(self.closeButton)

        self.setLayout(mainLayout)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.timerForReceive = QTimer(self)
        self.timerForReceive.setSingleShot(False)
        self.timerForReceive.setInterval(3000)  # in milliseconds, so 3000 = 3 seconds
        self.timerForReceive.timeout.connect(self.receive)

        self.timerForSend = QTimer(self)
        self.timerForSend.setSingleShot(False)
        self.timerForSend.setInterval(3000)  # in milliseconds, so 3000 = 3 seconds
        self.timerForSend.timeout.connect(self.sendMessage)

        self.userNameFlag = True  # to send the username on the socket to server for first time

    def displayInfo(self):
        self.show()
        try:
            self.client.connect(ADDR)
            self.client.setblocking(False)
            self.client.settimeout(12.0)
        except socket.error as err:
            print(f"Client not connected due to: {err}")
            self.close()

        self.timerForReceive.start()
        self.timerForSend.start()

    def sendMessage(self):
        try:
            if self.userNameFlag:
                message = f"{self.usernameLabel.text().split(': ')[1]}"
                self.client.send(message.encode(FORMAT))
                self.userNameFlag = False
            else:
                message = f"{self.usernameLabel.text().split(': ')[1]}: {self.typingSpace.text()}"
                self.client.send(message.encode(FORMAT))
                self.typingSpace.clear()
        except socket.error as e:
            print(f"Data cannot be sent or received due to {e}")
            self.client.close()


    # listening to server and Sending messages
    def receive(self):
        try:
            # receive messages from server
            incoming_message = self.client.recv(1024).decode(FORMAT)
            if incoming_message == "UserName ":
                self.client.send(self.usernameLabel.text().split(': ')[1].encode(FORMAT))
            else:
                self.chatArea.appendPlainText(incoming_message)
        except socket.error as e:
            print(f"[FATAL ERROR] {e}: Closing client connection..")
            self.client.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setFixedWidth(800)

        self.secondWindow = SecondWindow()

        mainLayout = QVBoxLayout()
        self.setStyleSheet("""
            QLineEdit{height: 40px; font-size: 30px}
            QLabel{font-size: 30px}
        """)

        self.name = QLineEdit()
        mainLayout.addWidget(QLabel('Name:'))
        mainLayout.addWidget(self.name)

        self.Confirm = QPushButton('Confirm')
        self.Confirm.setStyleSheet('font-size: 30px')
        self.Confirm.clicked.connect(self.passingInformation)
        mainLayout.addWidget(self.Confirm)

        self.setLayout(mainLayout)

    def passingInformation(self):
        self.secondWindow.usernameLabel.setText("Username: " + self.name.text())
        self.secondWindow.displayInfo()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    demo.secondWindow.typingSpace.setFocus()
    sys.exit(app.exec_())



