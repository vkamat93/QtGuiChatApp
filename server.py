import socket
import threading
from threading import Timer

HEADER = 64  # in bytes
FORMAT = 'utf-8'
DISCONNECT_MSG = "!Disconnect"
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # replace by your public IP, access from client in other network
ADDR = (SERVER, PORT)

try:
    # AF_INET is IPv4 address family. SOCK_STREAM implies TCP protocol
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server Socket Created")
    s.bind(ADDR)  # not binding to specific IP, listening to all requests coming in on specific port
    print(f"Server Socket bound to listen to port {PORT}")
except socket.error as err:
    print(f"Server Socket not created due to error: {err}")

# dict to store the clients connected to server and their usernames
clients = {}

def handle_client(sock_obj, client_addr):
    print(f"[NEW CONNECTION] {client_addr} {clients[sock_obj]} connected to the server..")
    connected = True

    # wait to receive info from a client and when we receive we process it and print to screen
    while connected:
        try:
            message = sock_obj.recv(1024)
            broadcastMessage(message)
        except ConnectionResetError as e:
            disconnected_user = clients[sock_obj]
            del clients[sock_obj]
            print(f"[CLIENT DISCONNECTED] {disconnected_user} left the chat")

            # removing and closing clients
            broadcastMessage(f"{disconnected_user} left the chat".encode(FORMAT))
            sock_obj.close()
            break

    print(f"\n[ACTIVE CONNECTIONS] {threading.active_count() - 2}")  # -1 to not count the main thread


# method for broadcasting messages to the each connected client
def broadcastMessage(encoded_message):
    for sock in clients:
        sock.send(encoded_message)

def start_server():
    s.listen(6)  # number of connections as parameter
    print(f"Server Socket on {SERVER} is now listening...")

    while True:  # server starts up and runs infinitely
        # Establish new connection with client
        sock_obj_client, client_addr = s.accept()

        sock_obj_client.send("UserName ".encode(FORMAT))
        nickname = sock_obj_client.recv(1024).decode(FORMAT)
        clients.update({sock_obj_client: nickname})

        # broadcast new joiner's nickname to other chat participants
        broadcastMessage(f"{nickname} joined!\n".encode(FORMAT))

        # feedback to individual client
        sock_obj_client.send('Connected to server!\n--------------------------\n'.encode(FORMAT))

        thread = threading.Thread(target=handle_client, args=(sock_obj_client, client_addr))
        thread.start()
        print(f"\n[ACTIVE CONNECTIONS] {threading.active_count() - 1}")  # -1 to not count the main thread


if __name__ == "__main__":
    print("[STARTING] server is starting")
    start_server()




