import json
import socket
import threading
import time
from main import MyEncoder, timeout


class GBNSimulation:
    def __init__(self, pkts, address, file_name, window_size=4, next_seq_num=0, base_pointer=0):
        self.next_seq_num = next_seq_num
        self.connection = socket.socket(socket.AF_INET,  # Internet
                                        socket.SOCK_DGRAM)  # UDP
        self.connection.connect(address)
        self.base_pointer = base_pointer
        self.window_size = window_size
        self.file_name = file_name
        self.mutex = threading.Lock()
        self.pkts = pkts

    def serve_client(self):

        while self.base_pointer < len(self.pkts) - 1:
            while self.next_seq_num < self.base_pointer + self.window_size:
                self.mutex.acquire()
                if self.base_pointer == len(self.pkts):
                    print("client served!")
                    break
                if self.next_seq_num >= len(self.pkts):
                    self.mutex.release()
                    if self.base_pointer >= len(self.pkts):
                        break
                    self.check_unsent(self.pkts[self.base_pointer])
                    continue
                self.pkts[self.next_seq_num].deadline = time.time() + timeout
                if self.pkts[self.next_seq_num].will_be_sent == 1:
                    self.connection.send(json.dumps(
                        self.pkts[self.next_seq_num], cls=MyEncoder).encode())
                    print("pkt number ", self.next_seq_num, " is sent")
                    self.pkts[self.next_seq_num].is_sent = True
                    self.next_seq_num += 1
                else:
                    self.pkts[self.next_seq_num].will_be_sent = 1
                    self.next_seq_num += 1
                self.check_unsent(self.pkts[self.base_pointer])
                self.mutex.release()

            try:
                self.check_unsent(self.pkts[self.base_pointer])
            except IndexError:
                print("client served ! ")
                return

    def check_unsent(self, unsent):

        if unsent.deadline < time.time() and unsent.is_sent == False:
            self.next_seq_num = self.base_pointer

    def rcv_ack(self, pkt):
        print("ack found!! with seq_num ", pkt.seq_num)
        self.mutex.acquire()
        if pkt.seq_num >= self.base_pointer:
            self.base_pointer = pkt.seq_num + 1
        self.mutex.release()
        return -1
