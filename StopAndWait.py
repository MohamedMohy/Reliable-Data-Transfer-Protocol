import json
import socket
import threading
import time

from main import MyEncoder, timeout

chunks = []


class StopAndWaitSimulation:
    def __init__(self, pkts, address, file):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection.connect(address)
        self.address = address
        self.pkts = pkts
        self.seq = 0
        self.file_name = file
        self.counter = 0
        self.send_pkt_flag = True
        self.mutex = threading.Lock()

    def serve_client(self):  # we need to send the client ip to serve
        for pkt in self.pkts:
            if pkt.will_be_sent == 0:
                print("this pkt will be lost! waiting for timeout and retransmitting")
                time.sleep(timeout)
                pkt.will_be_sent = 1
            self.send_pkt_flag = False
            self.counter += 1
            while not self.send_pkt_flag:
                self.mutex.acquire()
                print("sending the chunk number ", self.counter, " with check sum = ", pkt.check_sum)
                self.connection.send(json.dumps(pkt, cls=MyEncoder).encode())
                print("Pkt", self.counter, " transmitted")
                self.mutex.release()
                time.sleep(0.1)
            self.seq = (self.seq + 1) % 2

    def rcv_ack(self, pkt):
        self.mutex.acquire()
        if pkt.ack_num == -1:
            print("Wrong Ack found!! retransmittig")
            time.sleep(0.25)
            return False
        if pkt.seq_num == self.seq:
            print("Ack found!!")
            time.sleep(0.5)
            self.send_pkt_flag = True
        self.mutex.release()

# server()
