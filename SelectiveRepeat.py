import json
import socket
import threading
import time
from main import (MyEncoder, timeout)

base_pointer = 0
next_seq_num = 0


class SelectiveRepeatSimulation:
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
        self.oldestUnAcked = 0

    def serve_client(self):

        while self.base_pointer < len(self.pkts):
            self.mutex.acquire()
            try:
                self.check_unsent(self.pkts[self.base_pointer])
            except IndexError:
                self.mutex.release()
                continue
            self.mutex.release()
            if len(self.pkts) - self.base_pointer < self.window_size:
                time.sleep(timeout)
            while self.next_seq_num < self.base_pointer + self.window_size:
                self.mutex.acquire()
                print("base pontnter = ", base_pointer, " next_seq num = ", self.next_seq_num)
                if self.check_all_sent():
                    time.sleep(0.1)
                    print("client served ! waiting for next client")
                    return
                if self.base_pointer == len(self.pkts):
                    print("client served!")
                    return
                # check if base pointer pkt deadline is over,re transmitt
                self.check_unsent(self.pkts[self.base_pointer])
                if self.next_seq_num >= len(self.pkts):
                    time.sleep(0.2)
                    self.mutex.release()
                    break
                self.pkts[self.next_seq_num].deadline = time.time() + timeout
                if self.pkts[self.next_seq_num].will_be_sent == 1 and not self.pkts[self.next_seq_num].is_sent:
                    self.connection.send(json.dumps(
                        self.pkts[self.next_seq_num], cls=MyEncoder).encode())
                    print("pkt number ", self.next_seq_num, " is sent")
                    self.pkts[self.next_seq_num].is_sent = True
                    self.next_seq_num += 1
                else:
                    self.pkts[self.next_seq_num].will_be_sent = 1
                    self.next_seq_num += 1
                self.mutex.release()

    def check_unsent(self, unsent):
        if unsent.deadline < time.time() and unsent.is_sent is False:
            self.connection.send(json.dumps(
                unsent, cls=MyEncoder).encode())
            unsent.is_sent = True

    def check_all_sent(self):
        for pkt in self.pkts:
            if not pkt.is_sent:
                return False
        return True

    def rcv_ack(self, pkt):
        print("ack found!! with seq_num ", pkt.seq_num)
        self.mutex.acquire()
        self.pkts[pkt.seq_num].is_acked = True
        if pkt.seq_num == self.oldestUnAcked:
            self.oldestUnAcked = pkt.seq_num + 1
            self.base_pointer = self.oldestUnAcked
        if self.pkts[self.base_pointer].is_acked:
            for i in range(self.window_size):
                try:
                    if not self.pkts[self.base_pointer + i].is_acked:  # check here!
                        self.base_pointer = self.base_pointer + i
                        self.oldestUnAcked = self.base_pointer
                        break
                except:
                    pass
        print("oldest Unacked =", self.oldestUnAcked, "base pointer = ", self.base_pointer)
        self.mutex.release()
        time.sleep(0.5)
        return -1

# SelectiveRepeat_server()
