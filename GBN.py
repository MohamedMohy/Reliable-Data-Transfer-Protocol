import json
import socket
import _thread
import time
import math
import random
import threading
from main import Packet, Packetize, send_Ack, calculate_checksum, UDP_PORT_SENDER, UDP_IP, timeout, MyEncoder, rcv_file, timeout, read_file, plp, mapping, drop_pkts

next_seq_num = 0
base_pointer = 0
window_size = 4
mutex = threading.Lock()


def GBN_server():
    (data, ip, port) = rcv_file()
    serve_client(data, ip, port)


def serve_client(data, ip, port):
    global next_seq_num
    global base_pointer
    global mutex
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    sock.settimeout(timeout)
    send_Ack(data['seq_num'], sock, ip, port)
    chunks = read_file(data["data"])
    pkts = []
    for i in range(len(chunks)):
        pkt = Packet()
        pkt.data = chunks[i]
        pkt.seq_num = i
        pkt.check_sum = calculate_checksum(pkt)
        pkts.append(pkt)
    drop_pkts(mapping(plp(1), len(pkts)), pkts)

    # for i in pkts:
    #     print(i.will_be_sent)

    try:
        _thread.start_new_thread(rcv_ack, (ip, port, window_size, sock))

    except Exception:
        print("threading error !!")

    while base_pointer < len(pkts)-1:
        while next_seq_num < base_pointer + window_size:
            mutex.acquire()
            if base_pointer == len(pkts):
                break
            if next_seq_num >= len(pkts):
                mutex.release()

                if base_pointer == len(pkts):
                    break
                check_unsent(pkts[base_pointer])
                continue
            pkts[next_seq_num].deadline = time.time()+timeout
            if pkts[next_seq_num].will_be_sent == 1:
                sock.sendto(json.dumps(
                    pkts[next_seq_num], cls=MyEncoder).encode(), (ip, port))
                print("pkt number ", next_seq_num, " is sent")
                pkts[next_seq_num].is_sent = True
                next_seq_num += 1
            else:
                pkts[next_seq_num].will_be_sent = 1
                next_seq_num += 1
            check_unsent(pkts[base_pointer])

            mutex.release()

        try:
            check_unsent(pkts[base_pointer])
        except IndexError:
            print("client served ! ")
            return


def check_unsent(unsent):
    global next_seq_num
    if unsent.deadline < time.time() and unsent.is_sent == False:
        next_seq_num = base_pointer


def rcv_ack(ip, port, window_size, sock):
    global next_seq_num
    global base_pointer
    global mutex
    while True:
        try:
            (data, add) = sock.recvfrom(9216)
            data = json.loads(data)
            pkt = Packetize(data)
            print("ack found!! with seq_num ", pkt.seq_num)
            mutex.acquire()
            global base_pointer
            if pkt.seq_num >= base_pointer:
                base_pointer = pkt.seq_num+1
            mutex.release()

        except Exception:
            if base_pointer+window_size == next_seq_num:
                continue

    return -1


GBN_server()
