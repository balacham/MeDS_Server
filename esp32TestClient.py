import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5050
FORMAT = 'utf-8'
HEADER = 4

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def run():
    client.connect((SERVER_IP, SERVER_PORT))
    print("Connection established")
    client.send("mc32".encode(FORMAT))

    while True:
        fromServer = client.recv(HEADER).decode(FORMAT)
        print(f"From server: {fromServer}")

run()