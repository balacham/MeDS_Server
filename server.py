# server for app to microcontroller communication
# using sockets protocol to communicate between devices
# using json objects to standardize data 

import socket
import threading
import time
import re

SERVER_IP = socket.gethostbyname(socket.gethostname())  # local ip of the machine
SERVER_PORT = 5050  # arbitrary registered port (below 1024 are system ports, cannot use)
FORMAT = 'utf-8'
DISCONNECTION = "/DISCONNECT/"
HEADER = 4

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

flag = False
lock = threading.Lock()
# slot quantity
# pill schedule

quantity = [0 for i in range(4)]
dispQuant = [0 for i in range(4)]
schedule = [[] for i in range(4)]

# method to handle incoming client, runs in its own thread
def client_side(conn, addr):
    global flag
    global lock
    
    global quantity
    global dispQuant
    global schedule

    # conn = connection, addr = address
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    tmp = conn.recv(HEADER).decode(FORMAT)
    print(tmp)

    # while connected:
    if tmp == "iapp":
        message_len = conn.recv(HEADER).decode(FORMAT)
        # print("Length of message to be recived: ", message_len)
        message_len = int(message_len)
        message = conn.recv(message_len).decode(FORMAT)
        print("Received: ", message)

        # decode message and update variables
        # use lock.acquire() and lock.release()

        # message = "Slot #: 1, Pills: 120, Hour Cycle: 12, Schedule: 1 Pill Starting @ 8AM"

        # decodeList = [slot #, # pills, hour cycle, # pills to dispense, start time]
        decodeList = re.findall(r"[0-9]+", message)

        timelength = len(decodeList[4])
        onTheHour = (timelength < 3)

        decodeList = [int(x) for x in decodeList]
        # A for am, P for pm
        amPM = message[-2]

        startTime = 0000  # 24 hour time
        # multiply by 100
        # if onTheHour:
        if amPM == "A":
            if decodeList[4] != 12:
                startTime = decodeList[4] * 100
            # else set to 0 by default
        elif amPM == 'P':
            if decodeList[4] != 12:
                startTime = decodeList[4] * 100 + 1200
            else:
                startTime = 1200  # 1200 is 12 pm
        else:
            print("RUN FOR THE HILLS! WERE ON THE HOUR!!")
        # else:
        #     # not on the hour, 3/4 digits in from iphone
        #     if amPM == "A":
        #         startTime = decodeList[4]
        #         if startTime >= 1200:
        #             # to account for 12XX AM
        #             startTime -= 1200
        #     elif amPM == "P":
        #         startTime = decodeList[4] + 1200

        newSchedule = []
        nextTime = startTime
        hourCycle = decodeList[2]

        while nextTime not in newSchedule:
            newSchedule.append(nextTime)
            nextTime = (nextTime + hourCycle * 100) % 2400
            # while loop ends when the schedule is fully constructed

        # update vars
        slot = decodeList[0] - 1
        pillCount = decodeList[1]
        toDisp = decodeList[3]

        print("trying to acquire lock")

        lock.acquire()
        quantity[slot] = pillCount
        dispQuant[slot] = toDisp
        schedule[slot] = newSchedule
        lock.release()

        print("lock released")

        print("Decoded numbers: ", decodeList)
        print("Quantity by slot #: ", quantity)
        print("# to dispense per dispense signal: ", dispQuant)
        print("Schedule by slot #: ", schedule)

        conn.close()
        print(f"{addr} connection closed")

        # if message == DISCONNECTION:
        #     connected = False
        #     break

        # y.acquire()
        # flag = 1
        # y.release()

    elif tmp == "disp":
        # can incorperate length, up to us
        message_len = conn.recv(HEADER).decode(FORMAT)
        # print("Length of message to be recived: ", message_len)
        message_len = int(message_len)
        message = conn.recv(message_len).decode(FORMAT)
        print("Received: ", message)

        # message = "Slot #: 1, Pills: 120, Hour Cycle: 12, Schedule: 1 Pill Starting @ 8AM"
        # decodeList = [slot #, # pills, hour cycle, # pills to dispense, start time]
        decodeList = re.findall(r"[0-9]+", message)

        slot = decodeList[0]
        print("Dispense on slot #: ", slot)
        # match message:
        #     case "0001":
        #         # dispense on slot 1
        #         print("disp on 1")
        #     case "0002":
        #         print("disp on 2")
        #     case "0003":
        #         print("disp on 3")
        #     case "0004":
        #         print("disp on 4")
        #     case _:
        #         # default case, error
        #         print("NOOOOOOOO")

        conn.close()
        print(f"{addr} connection closed")

    elif tmp == "mc32":
        if flag:
            # print("Input:")
            # val = input()
            # conn.send(val.encode(FORMAT))

            val = input("Waiting...")
            print("Sending ", message)
            conn.send(message.encode(FORMAT))
            y.acquire()
            flag = 0
            y.release()
            time.sleep(5)

server_start()