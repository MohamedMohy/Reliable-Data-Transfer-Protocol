import time
import json
seq=0
class Packet :
    def __init__(self,data='',ack=-1):
       self.check_sum =''
       seq =-1
       self.seq_num =seq      
       self.ack_num =ack
       self.start_time=0
       self.deadline =0 #timeout = 1 second , while current_time<timeout wait for ack
       self.data=''
    def is_Ack(self):
        if self.ack_num == -1:
            return False
        return True
    def is_corrupted(self,other):
        if self.check_sum==other:
            return False
        return True
    def start_timer(self):
        self.start_time=time.time()
        self.deadline =self.start_time + 100
def Packetize(obj):
    pkt = Packet()
    pkt.data =obj['data']
    pkt.ack_num=obj['seq_num']
    pkt.ack_num=obj['ack_num']
    pkt.check_sum=obj['check_sum']
    return pkt
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Packet):
            return super(MyEncoder, self).default(obj)
        return obj.__dict__
def split_by_length(s,block_size):
    w=[]
    n=len(s)
    for i in range(0,n,block_size):
        w.append(s[i:i+block_size])
    return w

def calculate_checksum(pkt):
    text= json.dumps(pkt,cls=MyEncoder)
    ascii =''
    ascii=ascii.join(format(ord(char), 'b')for char in text)
    splitted = split_by_length(ascii,16)
    ans =0
    for i in range(0,len(splitted)):
        word = int(splitted[i],2)
        ans += word
    ans = bin(ans)[2:].zfill(16) 
    return ans

pkt =Packet()
pkt.ack_num=-1
pkt.check_sum=True
pkt.data="hfasddasdfsdf"
calculate_checksum(pkt)

def read_file(filename):
    file_path=filename
    chunks =[]
    with open(file_path, "r") as fi:
        buf = fi.read(1024)
        while (buf):
            chunks.append(buf)
            buf = fi.read(1024)
    return chunks
def toggle(num):
    if num ==0:
        return 1
    return 0