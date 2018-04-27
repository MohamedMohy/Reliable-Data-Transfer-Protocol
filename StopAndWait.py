import socket
import os
import json
from main import Packet,read_file,calculate_checksum,toggle,MyEncoder,Packetize
import time
chunks=[]
UDP_IP = "192.168.1.17"
amora_ip="192.168.1.10"
timeout=5
UDP_PORT_SENDER =5102
UDP_PORT_RECIEVER=5002

def send_Ack(seq_num,sock,client_ip,reciever_port):
    pck=Packet()
    pck.ack_num=seq_num
    pck.check_sum=calculate_checksum(pck)
    sock.sendto(json.dumps(pck,cls=MyEncoder).encode(),(client_ip,reciever_port))
    return pck

def server():
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    sock.settimeout(timeout)
    while True:
        try:
            (data,add)=sock.recvfrom(9216)
            print(add)
        except:
            print("noting found! try again")
            continue
        if data is not None:
            data = json.loads(data)
            print(data)
            sock.close()
            serve_client(data,add[0],add[1]) # to be handled in thread 
            
                
def serve_client(data,c_ip,c_port): #we need to send the client ip to serve
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    sock.settimeout(timeout) # replace with proper timeout
    seq=0
    chunks=read_file(data["data"])
    print(len(chunks))
    send_Ack(data['seq_num'],sock,c_ip,c_port)

    for i in range(len(chunks)):
        pkt=Packet()
        pkt.data=chunks[i]
        pkt.seq_num=seq
        seq=toggle(seq)
        pkt.start_timer()
        pkt.check_sum=calculate_checksum(pkt)
        incoming_data = False
        while not incoming_data:
            print("sending the chunk number ",i)
            sock.sendto(json.dumps(pkt,cls=MyEncoder).encode(),(amora_ip,UDP_PORT_RECIEVER))
            print("Pkt",i," transmitted")
            incoming_data = wait_for_ack(pkt,sock)
            print(incoming_data, i)

    
def wait_for_ack(pkt,sock):
    currnet_time = time.time()
    
    while time.time()<currnet_time+float(timeout):
        try:
            (data,add)=sock.recvfrom(9216)
        except:
            return False
        if data is not None:
            data = json.loads(data)
            pkt = Packetize(data)
            if pkt.ack_num== -1:
                print("Wrong Ack found!! retransmittig")
                time.sleep(0.25)
                return False
            # if pkt.check_sum is not calculate_checksum(data['data']):
            #     print("Corrupted Ack found!! retransmitting")
            #     time.sleep(2)
            #     return False
            print("Ack found!!")
            time.sleep(1)
            return True
        else:
            print("No Ack found!! retransmitting...")
            time.sleep(0.25)
            return False 
    return True



server()
