# !/usr/bin/env python
import socket
from collections import deque
TCP_IP = '192.168.16.68'
#TCP_IP = '127.0.0.1' #127.0.0.1 for android emulator test runs
#https://developer.android.com/studio/run/emulator-networking.html
TCP_PORT = 1234
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
buffer=""
closing=";"
mystack=deque("")
max_stack_len=10
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((TCP_IP, TCP_PORT))
    # s.send(MESSAGE)
    while(1==1):
        data1 = s.recv(BUFFER_SIZE)
        #print ("received:",data1)
        data=data1.decode("utf-8")
        if closing in data:
            for ww in data:
                if ww==closing:
                    mystack.append(buffer)
                    buffer=""
                else:
                    buffer=buffer+ww
        else:
            buffer=buffer+data
        if len(mystack)>max_stack_len:
            mystack.popleft()
            #print("stack low element removed")
            print(mystack)
except KeyboardInterrupt:
    print("W: interrupt received")
finally:
    # clean up
    s.close()
