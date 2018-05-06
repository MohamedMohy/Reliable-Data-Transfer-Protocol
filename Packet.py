import json


class Packet:
    def __init__(self, data='', seq_num=-1, ack_num=-1):
        self.will_be_sent = 1
        self.check_sum = 0
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.start_time = 0
        self.deadline = float('inf')
        self.data = data
        self.is_sent = False
        self.is_acked = False

    def is_ack(self):
        if self.ack_num == -1:
            return False
        return True

    def is_corrupted(self, other):
        if self.check_sum == other:
            return False
        return True


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
        is_sent = dic['is_sent']
        is_acked = dic['is_acked']
        will_be_sent = dic['will_be_sent']
        start_time = dic['start_time']

        pkt = Packet(data)
        pkt.check_sum = check_sum
        pkt.ack_num = ack_num
        pkt.deadline = deadline
        pkt.seq_num = seq_num
        pkt.is_sent = is_sent
        pkt.is_acked = is_acked
        pkt.will_be_sent = will_be_sent
        pkt.start_time = start_time
        return pkt
