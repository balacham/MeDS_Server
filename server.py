# server for app to microcontroller communication
# using sockets protocol to communicate between devices
# using json objects to standardize data 

import socket
import threading
import time

SERVER_IP = socket.gethostbyname(socket.gethostname())  # local ip of the machine
SERVER_PORT = 5000  # arbitrary registered port (below 1024 are system ports, cannot use)
FORMAT = 'utf-8'
DISCONNECTION = "/DISCONNECT/"
HEADER = 4
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
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

flag = 0
message = ""
y = threading.Lock()

# method to handle incoming client, runs in its own thread
def client_side(conn, addr):
    global flag
    global message
    global y
    # conn = connection, addr = address
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    tmp = conn.recv(HEADER).decode(FORMAT)
    print(tmp)

    while connected:
        if tmp == "iapp":
            message_len = conn.recv(HEADER).decode(FORMAT)
            message_len = int(message_len)
            message = conn.recv(message_len).decode(FORMAT)
            print(message)

            if message == DISCONNECTION:
                connected = False
                break
            y.acquire()
            flag = 1
            y.release()
        elif tmp == "mc32":
            if flag == 1:
                # print("Input:")
                # val = input()
                # conn.send(val.encode(FORMAT))
                conn.send(message.encode(FORMAT))
                y.acquire()
                flag = 0
                y.release()
                time.sleep(5)

    # conn.send("3   ".encode(FORMAT))
    # print("sending...")
    # conn.send(val.encode(FORMAT))
    # while connected:
        # conn.send(val.encode(FORMAT))
        # print("sent!")
        # message_len = conn.recv(tmp)#.decode(FORMAT)
        # print("raw:", message_len)
        # message_len = message_len.decode(FORMAT)

        # val = input()
        # if (val == "exit"):
        #     connected = False
        # else:
        #     tmp = int(val) 

        # count += 1
        # if message_len:
        #     message_len = int(message_len)
        #     print("int:", message_len)
        #     message = conn.recv(message_len).decode(FORMAT)
        #     if message == DISCONNECTION:
        #         connected = False

        #     print(f"[{addr}] {message}")
        #     print(message)
        #     # conn.send(ACK.encode(FORMAT))
        #     connected = False
    conn.close()
    print(f"{addr} connection closed")

server_start()