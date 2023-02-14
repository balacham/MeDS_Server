# server for app to microcontroller communication
# using sockets protocol to communicate between devices
# using json objects to standardize data 

import socket
import threading

SERVER_IP = socket.gethostbyname(socket.gethostname())  # local ip of the machine
SERVER_PORT = 5000  # arbitrary registered port (below 1024 are system ports, cannot use)
FORMAT = 'utf-8'
DISCONNECTION = "!DISCONNECT!"
HEADER = 64
ACK = "MESSAGE RECEIVED"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))

# main function that establishes new connections
def server_start():
    print("Starting...")
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER_IP}") 
    while True:
        # blocking line, creates a new thread when a new conneciton is established
        conn, addr = server.accept()
        thread = threading.Thread(target=client_side, args = (conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


# method to handle incoming client, runs in its own thread
def client_side(conn, addr):
    # conn = connection, addr = address
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        message_len = conn.recv(HEADER).decode(FORMAT)
        if message_len:
            message_len = int(message_len)
            message = conn.recv(message_len).decode(FORMAT)
            if message == DISCONNECTION:
                connected = False

            print(f"[{addr}] {message}")
            conn.send(ACK.encode(FORMAT))

server_start()