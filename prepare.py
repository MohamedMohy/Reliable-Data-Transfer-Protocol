import time
class packet :
    def __init__(self,seq=-1,check=-1,ack=-1):
       self.check_sum =check
       self.seq_num =seq
       self.ack_num =ack
       self.start_time=time.time()
       self.deadline =self.start_time + 1 #timeout = 1 second , while current_time<timeout wait for ack
       self.data=''
    def is_Ack(self):
        if self.ack_num == -1:
            return False
        return True
    def is_corrupted(self,other):
        if self.check_sum==other:
            return False
        return True
    def calculate_checksum(self):
        return True

file_path='test.txt'
packets =[]
with open(file_path, "r") as fi:
          buf = fi.read(1024)
          while (buf):
             packets.append(buf)
             buf = fi.read(1024)