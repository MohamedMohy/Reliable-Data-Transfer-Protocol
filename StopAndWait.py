import socket
import os
import json
from main import Packet,read_file,calculate_checksum,toggle,MyEncoder,Packetize
import time
chunks=[]
UDP_IP = "127.0.0.1"
amora_ip="192.168.1.5"
timeout=5

UDP_PORT_SENDER =5102
UDP_PORT_RECIEVER=5002

def send_Ack(seq_num,sock,client_ip,reciever_port):
    pck=Packet()
    pck.ack_num=seq_num
    sock.sendto(json.dumps(pck,cls=MyEncoder).encode(),(client_ip,reciever_port))
    return pck

def server():
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    # sock.settimeout(5)
    while True:
        (data,add)=sock.recvfrom(9216)
        if data is not None:
            data = json.loads(data)
            print(data)
            serve_client(data) # to be handled in thread 
            
                
def serve_client(data): #we need to send the client ip to serve
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    sock.settimeout(timeout) # replace with proper timeout
    seq=0
    chunks=read_file(data["data"])
    print(len(chunks))
    send_Ack(data['seq_num'],sock,amora_ip,UDP_PORT_RECIEVER)
    for i in range(len(chunks)):
        pkt=Packet()
        pkt.data=chunks[i]
        pkt.seq_num=seq
        seq=toggle(seq)
        pkt.start_timer()
        print("sending the chunk number ",i)
        sock.sendto(json.dumps(pkt,cls=MyEncoder).encode(),(amora_ip,UDP_PORT_RECIEVER))
        incoming_data = wait_for_ack(pkt,sock)
        if not incoming_data:
            i=i-1    
def wait_for_ack(pkt,sock):
    currnet_time = time.time
    while time.time<currnet_time+timeout:
        try:
            (data,add)=sock.recvfrom(9216)
        except:
            return False
        if data is not None:
            data = json.loads(data)
            pkt = Packetize(data)
            if pkt.ack_num== -1:
                return False
            if pkt.check_sum is not calculate_checksum(data['data']):
                return False
        else:
            return False 
    return True
        
server()
