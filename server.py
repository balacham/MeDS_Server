# server for app to microcontroller communication
# using sockets protocol to communicate between devices
# using json objects to standardize data 

import socket
import threading
import time
import re
import os

SERVER_IP = '0.0.0.0' # socket.gethostbyname(socket.gethostname())  # listen on everything
SERVER_PORT = 5050  # arbitrary registered port (below 1024 are system ports, cannot use)
FORMAT = 'utf-8'
DISCONNECTION = "EXIT"
HEADER = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))


flag = False
lock = threading.Lock()
# slot quantity
# pill schedule

dispESP = "0000"
quantity = [0 for i in range(4)]
dispQuant = [0 for i in range(4)]
schedule = [[] for i in range(4)]

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

# method to handle incoming client, runs in its own thread
def client_side(conn, addr):
    global flag
    global lock
    
    global quantity
    global dispQuant
    global schedule
    global dispESP

    # conn = connection, addr = address
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    tmp = conn.recv(HEADER).decode(FORMAT)
    print(tmp)

    os.environ['TZ'] = 'US/Eastern'
    time.tzset()

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

        # decodeList = [slot #, # pills, hour cycle, # pills to dispense, start time hour, start time minutes]
        decodeList = re.findall(r"[0-9]+", message)
        decodeList[4] = decodeList[4] + decodeList[5]

        decodeList = [int(x) for x in decodeList]
        # A for am, P for pm
        amPM = message[-2]

        startTime = 0000  # 24 hour time
        # multiply by 100
        # if onTheHour:
        if amPM == "A":
            if decodeList[4] < 1200:
                startTime = decodeList[4]
            # else set to 0 by default, where 0 is 00:00
            else:
                startTime = decodeList[4] - 1200
        elif amPM == 'P':
            if decodeList[4] < 1200:
                startTime = decodeList[4] + 1200
            else:
                startTime = decodeList[4]  # 1200 is 12 pm
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

        lock.acquire()
        quantity[slot] = pillCount
        dispQuant[slot] = toDisp
        schedule[slot] = newSchedule
        lock.release()

        print("Decoded numbers: ", decodeList)
        print("Quantity by slot #: ", quantity)
        print("# to dispense per dispense signal: ", dispQuant)
        print("Schedule by slot #: ", schedule)

        conn.close()
        print(f"{addr} connection closed")

    # instant dispense signal from iphone
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
        decodeList[4] = decodeList[4] + decodeList[5]

        decodeList = [int(x) for x in decodeList]

        slot = decodeList[0]
        print("Dispense on slot #: ", slot)
        lock.acquire()
        flag = True
        # "2010"
        match slot:
            case 1:
                # dispense on slot 1
                print("disp on 1")
                dispESP = "1000"
            case 2:
                print("disp on 2")
                dispESP = "0100"
            case 3:
                print("disp on 3")
                dispESP = "0010"
            case 4:
                print("disp on 4")
                dispESP = "0001"
            case _:
                # default case, error
                print("NOOOOOOOO")
                dispESP = "0000"
        lock.release()

        conn.close()
        print(f"{addr} connection closed")

    # esp 32 logic
    elif tmp == "mc32":
        # list of scheduled times that are temperarily removed to be added back when the time doesn't match
        tempTime = [None for i in range(4)]

        while True:
            # instant dispense signal
            if flag:
                print("Instant dispense, sending: ", dispESP)
                conn.send(dispESP.encode(FORMAT))
                lock.acquire()
                flag = False
                lock.release()
            # regular scheduling 
            else:
                timeString = time.ctime()
                # timeList = [date, hour, minute, second, year]
                timeList = re.findall(r"[0-9]+", timeString)
                timeInt = int(timeList[1] + timeList[2])

                # if timeInt is in schedule, then modify and send dispense signal
                schdESP = ""

                for i in range(4):
                    if timeInt in schedule[i]:
                        # need to dispense
                        quant = dispQuant[i]
                        quantity[i] -= dispQuant[i]

                        quant = str(quant)
                        schdESP += quant

                        # add to tempTime and remove from schedule
                        print(schedule)
                        print("removing from schedule")
                        tempTime[i] = timeInt
                        lock.acquire()
                        schedule[i].remove(timeInt)
                        lock.release()
                        print(schedule)
                    else:
                        # don't need to dispense
                        schdESP += "0"

                # re add the removed time to the schedule
                for i in range(4):
                    # there is a time to be added and that time is not now
                    if tempTime[i] != None and timeInt != tempTime[i]:
                        print("adding back to schedule")
                        lock.acquire()
                        schedule[i].append(tempTime[i])
                        lock.release()
                        tempTime[i] = None
                        print(schedule)

                # if something to dispense, then dispense
                if schdESP != '0000':
                    conn.send(schdESP.encode(FORMAT))
                    print("sending to esp: ", schdESP)

            time.sleep(1)
    
    elif tmp == 'test':
        while True:
            message_len = conn.recv(HEADER).decode(FORMAT)
            # print("Length of message to be recived: ", message_len)
            message_len = int(message_len)
            message = conn.recv(message_len).decode(FORMAT)
            print("Received:", message)

            if message == DISCONNECTION:
                conn.close()
                print(f"{addr} connection closed")
                break
            
    # error of some kind
    else:
        print("Unknown identifier, closing socket connection")
        conn.close()
        print(f"{addr} connection closed")

server_start()