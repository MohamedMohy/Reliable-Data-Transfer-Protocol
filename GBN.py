import json
import socket
import _thread 
import time
import math
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
    print(number,len(pkts))
    for i in range(number):
        x=round(plp(len(pkts)-1))
        del pkts[x]

def serve_client(data,ip,port):
    global next_seq_num
    global base_pointer
    sent_items=[]
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
    full_pkts = pkts
    drop_pkts(mapping(plp(1),len(pkts)),pkts)
    print(len(pkts))
    try:
        _thread.start_new_thread(rcv_ack,(ip,port,window_size,sock))
    except Exception:
        import traceback
        print(traceback.format_exc)
        print("threading error !!")
    while True:
        if next_seq_num >=len(chunks):
            break
        if base_pointer+window_size>next_seq_num and len(pkts)>len(sent_items):
            print("from sending thread!!! base_pointer =",base_pointer,"window_size = ",window_size," next_seq_num = ",next_seq_num)
            sock.sendto(json.dumps(pkts[next_seq_num],cls=MyEncoder).encode(),(ip,port))
            print(pkts[next_seq_num].seq_num)
            sent_items.append(pkts[next_seq_num])
            if len(pkts)+1>next_seq_num:
                next_seq_num = pkts[next_seq_num+1].seq_num
            else:
                next_seq_num +=1
            time.sleep(0.1)
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
            if pkt.seq_num > base_pointer or pkt.seq_num ==-1:
                base_pointer = pkt.seq_num
                print(" from rcv_Acks !!! base_pointer =",base_pointer,"window_size = ",window_size," next_seq_num = ",next_seq_num)
        except Exception:
            if base_pointer+window_size == next_seq_num:
               continue
        

    return -1
    
GBN_server()