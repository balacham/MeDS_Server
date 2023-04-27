# Slot #:1, Pills: 10, Hour Cycle: 4, Schedule: 2 Pill @ 1:02PM

import socket

SERVER_IP = '18.218.15.131'
SERVER_PORT = 5050
FORMAT = 'utf-8'
HEADER = 4

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_message(msg):
    global client 

    # msg is a string
    message = msg.encode(FORMAT)
    msg_length = len(message)
    size_send = str(msg_length).encode(FORMAT)
    size_send += b' ' * (HEADER - len(size_send))
    client.send(size_send)
    client.send(message)

def run():
    global client

    while True:
        try:
            input("Hit enter to proceed")
            client.connect((SERVER_IP, SERVER_PORT))
            print("Connection established\n")
            iden = input("Enter identifier (iapp || disp): ")
            client.send(iden.encode(FORMAT))

            message = input("Message: ")
            send_message(message.strip())

            client.close()
            print("Connection closed")
        except socket.error:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     

run()