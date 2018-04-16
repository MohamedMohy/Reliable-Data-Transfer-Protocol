import time
seq=0
class Packet :
    def __init__(self,data='',ack=-1):
       self.check_sum =calculate_checksum(data)
       self.seq_num =seq      
       seq =toggle(seq)
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
       self.deadline =self.start_time + 1
def calculate_checksum(data):
    asciis = ord(char for char in data)
    result = sum(asciis)
    return result
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