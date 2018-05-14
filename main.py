import time
import json
import random
import socket
import math

seq = 0
UDP_IP = "127.0.0.1"
timeout = 2
UDP_PORT_SENDER = 5102


class Packet:
    def __init__(self, data='', ack=-1, seq =0):
        self.will_be_sent = 1
        self.check_sum = 0
        self.seq_num = seq
        self.ack_num = ack
        self.start_time = 0
        self.deadline = float('inf')
        self.data = data
        self.is_sent = False
        self.is_acked = False

    def is_Ack(self):
        if self.ack_num == -1:
            return False
        return True

    def is_corrupted(self, other):
        if self.check_sum == other:
            return False
        return True

    def start_timer(self):
        self.start_time = time.time()
        self.deadline = self.start_time + 100


def Packetize(dic):
    pkt = Packet()
    pkt.data = dic['data']
    pkt.seq_num = dic['seq_num']
    pkt.ack_num = dic['ack_num']
    pkt.check_sum = dic['check_sum']
    pkt.deadline = dic['deadline']
    pkt.is_sent = dic['is_sent']
    pkt.is_acked = dic['is_acked']
    pkt.will_be_sent = dic['will_be_sent']
    pkt.start_time = dic['start_time']
    return pkt


def mapping(random_number, list_length):
    return round(random_number * list_length)


def drop_pkts(number, pkts):
    to_be_removed = random.sample(range(len(pkts)), number)
    print(number, len(pkts))
    for i in range(len(to_be_removed)):
        pkts[to_be_removed[i]].will_be_sent = 0


def plp(num):
    return random.uniform(0, num)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Packet):
            return super(MyEncoder, self).default(obj)
        return obj.__dict__


def split_by_length(s, block_size):
    w = []
    n = len(s)
    for i in range(0, n, block_size):
        w.append(s[i:i + block_size])
    return w


def send_Ack(data, seq_num, sock, ip, port):
    pkt = Packet()
    pkt.ack_num = 0
    pkt.data = data
    pkt.seq_num = seq_num
    pkt.check_sum = calculate_checksum(pkt)
    sock.sendto(json.dumps(pkt, cls=MyEncoder).encode(), (ip, port))


def calculate_checksum(pkt):
    text = json.dumps(pkt, cls=MyEncoder)
    ascii = ''
    ascii = ascii.join(format(ord(char), 'b') for char in text)
    splitted = split_by_length(ascii, 16)
    ans = 0
    for i in range(0, len(splitted)):
        word = int(splitted[i], 2)
        ans += word
    ans = bin(ans)[2:].zfill(16)
    return ans


def read_file(filename):
    file_path = filename
    chunks = []
    with open(file_path, "r") as fi:
        buf = fi.read(1024)
        while (buf):
            chunks.append(buf)
            buf = fi.read(1024)
    return chunks


def toggle(num):
    if num == 0:
        return 1
    return 0


def rcv_file():
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    sock.settimeout(timeout)
    while True:
        try:
            (data, add) = sock.recvfrom(9216)
        except:
            print("noting found! try again")
            continue
        if data is not None:
            data = json.loads(data)
            print(data)
            sock.close()
            return (data, add[0], add[1])