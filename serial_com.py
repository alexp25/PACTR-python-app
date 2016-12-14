import threading
import time
import serial
import traceback

import datetime

from multiprocessing import Queue


class serialReadThread (threading.Thread):
    def __init__(self,threadID,name,ser,queue_read):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self._stopperper = threading.Event()
        self._req = threading.Event()
        self.time1 = time.time()
        self.data = 0
        self.data_received = 0
        self.ser = ser
        self.receivedFlag = False
        self.queue_read = queue_read

    def stop(self):
        self._stopperper.set()

    def stopped(self):
        return self._stopperper.isSet()

    def get_received_data(self):
        flag = self.receivedFlag
        data = self.data_received
        self.receivedFlag = False
        self.data_received = ""
        return [flag,data]

    def serial_data(self):
        while True:
            yield self.ser.readline()

    def run(self):
        line=''
        while True:
            c = self.ser.read()
            line += c
            if c=='\n':
                self.queue_read.put(line)
                line = ''

            if self.stopped():
                break

        if self.ser.isOpen() == True:
            self.ser.close()

class serialWriteThread (threading.Thread):
    def __init__(self,threadID,name,ser,queue_write):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self._stopper = threading.Event()
        self._req = threading.Event()
        self.ser = ser
        self.queue_write=queue_write

    def stop(self):
        self._stopper.set()
    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        while True:
            if self.stopped():
                break
            time.sleep(0.001)
            try:
                while self.queue_write.empty() == False:
                    result = self.queue_write.get(block=False)
                    self.ser.write(result)
            except:
                print("serial write exception thread")
                traceback.print_exc()

class serialCom(object):
    def __init__(self,portName,baudRate):
        self.threads = []
        self.start_time = 0
        self.elapsed_time = 0
        self.portName = portName
        self.baudRate = baudRate
        self.start_sending_data = False
        self.queue_write = Queue(maxsize=10)
        self.queue_read = Queue(maxsize=10)

        self.counter=0

    def config(self,portName,baudRate):
        self.portName = portName
        self.baudRate = baudRate

    def isConnected(self):
        if self.threads:
            return True
        else:
            return False

    def start(self):
        if not (self.threads):
            try:
                self.ser = serial.Serial(self.portName, self.baudRate, timeout=3)
                print("starting thread")
                thread1 = serialReadThread(1,  "SERIAL_READ", self.ser,self.queue_read)
                print("t1 create")
                thread2 = serialWriteThread(2, "SERIAL_WRITE", self.ser,self.queue_write)
                print("t2 create")
                thread1.start()
                print("t1 start")
                thread2.start()
                print("t2 start")
                self.threads.append(thread1)
                self.threads.append(thread2)
            except:
                message = 'serial exception: ' + traceback.format_exc()
                print(message)


    def stop(self):
        print('serialCom stop')
        if self.threads:
            for i in range(len(self.threads)):
                self.threads[i].stop()
                self.threads[i].join()
            self.threads = []

    def send(self,msg):

        if self.threads:

            info = '[' + str(
                datetime.datetime.now().strftime(
                    "%H:%M:%S.%f")) + ']: ' + "send " + msg + '\n'
            print(info)

            try:
                self.queue_write.put(msg)
            except:
                print('queue_write full')
            print(self.counter)
            self.counter+=1
            return True
        print('send: port not open')
        return False

    def get_received_data(self):
        result = None
        if self.threads:
            if self.queue_read.empty() == False:
                result = self.queue_read.get(block=False)
                print('received data')
        return result

