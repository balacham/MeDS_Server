# server for app to microcontroller communication
# using sockets protocol to communicate between devices
# using json objects to standardize data 

import socket
import threading

SERVER_IP = socket.gethostbyname(socket.gethostname())  # local ip of the machine
SERVER_PORT = 5000  # arbitrary registered port (below 1024 are system ports, cannot use)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))

def run():
    print("Starting...")
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER_IP}") 
    while True:
        connection, address = server.accept()
        thread = threading.Thread(target=client_side, args = (connection, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

def client_side(connection, address):
    print(f"[NEW CONNECTION] {address} connected.")

    connected = True
    while connected:
        

run()