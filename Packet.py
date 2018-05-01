import json


class Packet:
    def __init__(self, data='', seq_number=-1, ack_number=-1):
        self.check_sum = ''
        self.seq_num = seq_number
        self.ack_num = ack_number
        self.deadline = 0
        self.data = data

    def is_ack(self):
        if self.ack_num == -1:
            return False
        return True

    def is_corrupted(self, other):
        if self.check_sum == other:
            return False
        return True


def calculate_checksum(pkt):
    pkt.check_sum = ''
    text= json.dumps(pkt, cls=MyEncoder)
    ascii =''
    ascii=ascii.join(format(ord(char), 'b')for char in text)
    splitted = split_by_length(ascii,16)
    ans = 0
    for i in range(0, len(splitted)):
        word = int(splitted[i], 2)
        ans += word
    ans = bin(ans)[2:].zfill(16)
    return ans


def split_by_length(s,
                    block_size):
    w = []
    n = len(s)
    for i in range(0, n, block_size):
        w.append(s[i:i+block_size])
    return w


def read_file(filename):
    file_path = filename
    chunks = []
    with open(file_path, "r") as fi:
        buf = fi.read(1024)
        while buf:
            chunks.append(buf)
            buf = fi.read(1024)
    return chunks


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Packet):
            return super(MyEncoder, self).default(obj)

        return obj.__dict__


def my_decoder(dic):
     data = dic['data']
     seq_num = dic['seq_num']
     ack_num = dic['ack_num']
     check_sum = dic['check_sum']
     deadline = dic['deadline']
     pkt = Packet(data)
     pkt.check_sum = check_sum
     pkt.ack_num = ack_num
     pkt.deadline = deadline
     pkt.seq_num = seq_num
     return pkt
