import socket
import os
import json
from main import Packet,read_file,calculate_checksum,toggle,MyEncoder
import time
chunks=[]
UDP_IP = "192.168.1.15"
amora_ip="192.168.1.5"
UDP_PORT_RECIEVER = 5103
UDP_PORT_SENDER =5102
omar_port=5002

def send_Ack(seq_num,sock):
    pck=Packet()
    pck.ack_num=seq_num
    sock.sendto(json.dumps(pck,cls=MyEncoder).encode(),(amora_ip,omar_port))
    return pck

def server():
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    
    while True:
        (data,add)=sock.recvfrom(9216)
        if data is not None:
            data = json.loads(data)
            print(data)
            serve_client(data,sock) # to be handled in thread 
            
                
def serve_client(data,sock):
    seq=0
    chunks=read_file(data["data"])
    print(len(chunks))
    send_Ack(data['seq_num'],sock)
    for i in range(len(chunks)):
        pkt=Packet(chunks[i])
        pkt.seq_num=seq
        seq=toggle(seq)
        pkt.start_timer()
        sock.sendto(json.dumps(pkt,cls=MyEncoder).encode(),(amora_ip,omar_port))
        print(i)
        incoming_data = wait_for_ack(pkt,sock)
        if not incoming_data:
            i=i-1    
def wait_for_ack(pkt,sock):

    while True:
        if time.time()< pkt.deadline:   
            (data,add)=sock.recvfrom(9216)
            if data is not None:
                data = json.loads(data)
                if data['isAck'] == -1:
                    break
        else:
            break
    return data
        

















server()
###########################SERVER#############################

#while True:
#    x = sock.recvfrom(1024)
#    print(1)

    