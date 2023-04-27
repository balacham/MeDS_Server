import socket
import threading
import time
import re

SERVER_IP = '0.0.0.0'
SERVER_PORT = 5050  # arbitrary registered port (below 1024 are system ports, cannot use)
FORMAT = 'utf-8'
DISCONNECTION = "/DISCONNECT/"
HEADER = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))

threadQuit = False

# main function that establishes new connections
def server_start():
    global threadQuit
    print("Starting...")
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER_IP}") 
    try:
        while True:
            # blocking line, creates a new thread when a new conneciton is established
            conn, addr = server.accept()
            thread = threading.Thread(target=client_side, args = (conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except:
        threadQuit = True
        print("Closing")

def client_side(conn, addr):
    global threadQuit

    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    tmp = conn.recv(HEADER).decode(FORMAT)
    print(tmp)
    
    while not threadQuit:
        message = input("Enter message to send: ")
        if message == "EXIT":
            break
        else:
            conn.send(message.encode(FORMAT))
            print(f"sending: {message}")

    conn.close()

server_start()