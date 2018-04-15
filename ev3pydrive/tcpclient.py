# !/usr/bin/env python
import socket
from collections import deque
from threading import Thread
from time import sleep, gmtime, strftime
#new thread is adding to the que
#one is removing old ones from the left
#application will pop from the top (right) from the main thread

class Safestack(deque):
    'Overrides pops with safer metods'
    __maxlen=10
    def __init__(self,maxlen):
        __maxlen=maxlen
        deque.__init__(self,)

    def popleft(self):
        'safe pop left, returns empty when que is 0 lenght'
        #print ("deque safe popleft")
        if (len(self)>0):
            return deque.popleft(self)
        else:
            return ""

    def pop(self):
        'safe pop right  returns empty when que is 0 lenght'
        if (len(self)>0):
            return deque.pop(self)
        else:
            return ""
    def append(self,data):
        'removes first if len>maxlen'
        #print ("deque append:",data)
        if (len(self)>self.__maxlen):
            self.popleft()
        deque.append(self,data)
class Director:
    'Collects ev3 direction commands to the stack. Stack must be Safestack type'
    __targetIp=""
    __targetPort=""
    __safestack=""
    __socket=socket.socket()
    __exitFlag=False
    __thread=""
    def __init__(self,safestack,targetIp,targetPort):
        print ("init")
        self.__targetIp=targetIp
        self.__targetPort=targetPort
        self.__safestack=safestack

    def run(self):
        thread = Thread(target = self.collect, args = ())
        self.__thread=thread
        thread.start()

    def collect(self):
        buffer=""
        closing=";"
        mystack=self.__safestack
        BUFFER_SIZE = 1024
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.__socket=s
            s.settimeout(5)
            target=((self.__targetIp, self.__targetPort))
            s.connect(target)
            #print ("connected to ", target)
            while(1==1):
                data1 = s.recv(BUFFER_SIZE)
                data=data1.decode("utf-8")
                #print ("director internal data:",data)
                if closing in data:
                    for ww in data:
                        if ww==closing:
                            mystack.append(buffer)
                            buffer=""
                        else:
                            buffer=buffer+ww
                else:
                    buffer=buffer+data
                if self.__exitFlag:
                    print ("exiting collect")
                    break
                sleep(0.01)
        except Exception as e :
            print ("Some error in connection or waht:",e)
        finally:
            self.close()

    def close(self):
        self.__exitFlag=True
        #self.__thread.join()
        self.__socket.close()

if __name__=="__main__":
    stack=Safestack(10)
    director=Director(stack,"192.168.45.133",1234)
    director.run()
    try:
        while(1==1):
            p=stack.pop()
            l=len(stack)
            print("at,length, top:",strftime("%Y-%m-%d %H:%M:%S", gmtime()),l,p)
            sleep(0.1)
    except KeyboardInterrupt:
        print("W: interrupt received")
    finally:
        # clean up
        director.close()



