import json
import socket
import _thread 
import time
import math
import random
from main import Packet,Packetize,send_Ack,calculate_checksum,UDP_PORT_SENDER,UDP_IP,timeout,MyEncoder,rcv_file,timeout,read_file,plp

next_seq_num=0
base_pointer=0
window_size =4

def GBN_server():
    (data,ip,port)= rcv_file()
    serve_client(data,ip,port)

def mapping(random_number,list_length):
    return round(random_number*list_length)

def drop_pkts(number,pkts):
    to_be_removed=random.sample(range(len(pkts)),number)
    print(number,len(pkts))
    for i in range(len(to_be_removed)):
        pkts[to_be_removed[i]].will_be_sent=0
def serve_client(data,ip,port):
    global next_seq_num
    global base_pointer
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    sock.settimeout(timeout)
    send_Ack(data['seq_num'],sock,ip,port)
    chunks=read_file(data["data"])
    pkts=[]
    for i in range(len(chunks)):
        pkt=Packet()
        pkt.data=chunks[i]
        pkt.seq_num = i
        pkt.check_sum=calculate_checksum(pkt)
        pkts.append(pkt)
    unsent=[]
    drop_pkts(mapping(plp(1),len(pkts)),pkts)
    #################
    for i in pkts:
        print(i.will_be_sent)
    #################
    try:
       thread= _thread.start_new_thread(rcv_ack,(ip,port,window_size,sock))
    except Exception:
        print("threading error !!")
    while next_seq_num <len(pkts):
        time.sleep(2.5)
        if base_pointer+window_size>next_seq_num:
            pkts[next_seq_num].deadline=time.time()+timeout #start the timer for the pkt
            if pkts[next_seq_num].will_be_sent==1:
                sock.sendto(json.dumps(pkts[next_seq_num],cls=MyEncoder).encode(),(ip,port)) #send the pkt
                print("pkt number ",next_seq_num," is sent")
                _thread.
                pkts[next_seq_num].is_sent=True
                next_seq_num +=1
            else:
                pkts[next_seq_num].will_be_sent=1
                unsent.append(pkts[next_seq_num])
                next_seq_num +=1
                if len(pkts) == base_pointer+window_size:
                    temp = check_unsent(unsent)
                    if temp != -1:
                        next_seq_num=temp
                        for i in range(window_size):
                           if i <len(unsent):
                                unsent.remove(pkts[next_seq_num+i])

        else:               
            next_seq_num=check_unsent(unsent) #for re transmission
            for i in range(window_size):
                try:
                    unsent.remove(pkts[next_seq_num+i])
                except:
                    pass


def check_unsent(unsent):
    
    for unsent_pkt in unsent:
        if unsent_pkt.deadline<time.time():
            next_s_n = unsent_pkt.seq_num
            return next_s_n
    return -1

            ################################# retransmission #############################
def rcv_ack(ip,port,window_size,sock):
    global next_seq_num
    global base_pointer
    while True:
        try:
            (data,add)=sock.recvfrom(9216)
            data=json.loads(data)
            pkt = Packetize(data)
            print("ack found!! with seq_num ",pkt.seq_num)
            global base_pointer
            if pkt.seq_num >= base_pointer or pkt.seq_num ==-1:
                base_pointer = pkt.seq_num

        except Exception:
            if base_pointer+window_size == next_seq_num:
               continue
        

    return -1
    
GBN_server()