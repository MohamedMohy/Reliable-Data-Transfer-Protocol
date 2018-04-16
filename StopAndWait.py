import socket
import os
import json
from main import Packet,read_file,calculate_checksum,toggle
import time
chunks=[]
UDP_IP = "127.0.0.1"
UDP_PORT_RECIEVER = 5005
UDP_PORT_SENDER =5006
def client():
   sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
   sock.bind((UDP_IP, UDP_PORT_RECIEVER))
   seq=0
   sock.sendto("test.txt".encode(),(UDP_IP,UDP_PORT_SENDER))
   while True:
       (data, add) =sock.recvfrom(9216)
#       data =json.loads(temp_data)
       if data is not None:
           if data.seq_num == seq:
               if(data.check_sum == calculate_checksum(data.data)):
                   sock.sendto(json.dumps(send_Ack(data.seq_num)).encode(),(UDP_IP,UDP_PORT_SENDER))
                   seq = toggle(seq)
               
   os._exit(0)
def send_Ack(seq_num):
    pck=Packet()
    pck.ack_num=seq_num
    return pck

def server():
    newpid = os.fork()
    flag = True
    if newpid == 0:
        client()
    else:
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT_SENDER))
        seq =0
        while flag == True:
            (data,add)=sock.recvfrom(9216)
            data = data.decode()
            print(data)
            chunks=read_file(data)
            print(len(chunks))
#            sock.sendto(json.dumps(send_Ack(data.seq_num)).encode(),(UDP_IP,UDP_PORT_RECIEVER))
            flag =False
        for i in range(len(chunks)):
            pkt=Packet(chunks[i])
            pkt.seq_num=seq
            seq=toggle(seq)
            ## send 
            pkt.start_timer()
            sock.sendto(json.dumps(pkt).encode(),(UDP_IP,UDP_PORT_SENDER))
            incoming_data = wait_for_ack(pkt)
            if not incoming_data:
                i=i-1

    
def wait_for_ack(pkt):
    while time.time()<pkt.deadline:
        (data,add)=sock.recvfrom(9216)
    return data
        
        
        
        
        
        
        
        
        
        
server()
###########################SERVER#############################

#while True:
#    x = sock.recvfrom(1024)
#    print(1)

    