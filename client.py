# client side for MeDS communication
# simulating a client communicating with server

import socket

SERVER_IP =  '127.0.0.1' # loopback
SERVER_PORT = 5050  # arbitrary registered port (below 1024 are system ports, cannot use)
FORMAT = 'utf-8'
DISCONNECTION = "EXIT"
HEADER = 4
ACK = "MESSAGE RECEIVED"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_message(msg):
    # msg is a string
    message = msg.encode(FORMAT)
    msg_length = len(message)
    size_send = str(msg_length).encode(FORMAT)
    size_send += b' ' * (HEADER - len(size_send))
    client.send(size_send)
    client.send(message)

def run():
    client.connect((SERVER_IP, SERVER_PORT))
    print("Connection established. Type 'exit' to end connection")
    client.send("test".encode(FORMAT))
    while True:
        msg = input("Type the message to send: ")
        if msg == "exit":
            send_message(DISCONNECTION)
            break
        else:
            send_message(msg.strip())
        
    print("Connection closed")

run()