import json
import socket
import threading
import time

import _thread

from main import (UDP_IP, UDP_PORT_SENDER, MyEncoder, Packet, Packetize,
                  calculate_checksum, drop_pkts, mapping, plp, rcv_file,
                  read_file, send_Ack, timeout)

base_pointer = 0
next_seq_num = 0


def SelectiveRepeat_server():
    (data, ip, port) = rcv_file()
    serve_client(data, ip, port)


def serve_client(data, ip, port):
    global next_seq_num
    global base_pointer
    window_size = 4
    mutex = threading.Lock()
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT_SENDER))
    sock.settimeout(timeout)
    chunks = read_file(data["data"])
    send_Ack(len(chunks), data['seq_num'], sock, ip, port)
    pkts = []
    for i in range(len(chunks)):
        pkt = Packet()
        pkt.data = chunks[i]
        pkt.seq_num = i
        pkt.check_sum = calculate_checksum(pkt)
        pkts.append(pkt)
    drop_pkts(mapping(plp(1), len(pkts)), pkts)
    for i in range(len(pkts)):
        print(pkts[i].will_be_sent," ",pkts[i].check_sum)
    try:
        _thread.start_new_thread(
            rcv_ack, (ip, port, window_size, sock, mutex, pkts))

    except Exception:
        print("threading error !!")

    while base_pointer < len(pkts):
        # check if base pointer pkt deadline is over,re transmitt
        mutex.acquire()
        try:
            check_unsent(pkts[base_pointer], sock, ip, port)
        except IndexError:
            mutex.release()
            continue
        mutex.release()
        if len(chunks) - base_pointer < window_size:
            time.sleep(timeout)
        while next_seq_num < base_pointer + window_size:
            mutex.acquire()
            print("base pontnter = ",base_pointer," next_seq num = ",next_seq_num)
            if check_all_sent(pkts):
                time.sleep(0.1)
                print("client served ! waiting for next client")
                return
            if base_pointer == len(pkts):
                print("client served!")
                return
            # check if base pointer pkt deadline is over,re transmitt
            check_unsent(pkts[base_pointer], sock, ip, port)
            if next_seq_num >= len(pkts):
                time.sleep(0.2)
                mutex.release()
                break
            pkts[next_seq_num].deadline = time.time() + timeout
            if pkts[next_seq_num].will_be_sent == 1 and not pkts[next_seq_num].is_sent:
                sock.sendto(json.dumps(
                    pkts[next_seq_num], cls=MyEncoder).encode(), (ip, port))
                print("pkt number ", next_seq_num, " is sent")
                pkts[next_seq_num].is_sent = True
                next_seq_num += 1
            else:
                pkts[next_seq_num].will_be_sent = 1
                next_seq_num += 1
            mutex.release()


def check_unsent(unsent, sock, ip, port):
    if unsent.deadline < time.time() and unsent.is_sent == False:
        sock.sendto(json.dumps(
            unsent, cls=MyEncoder).encode(), (ip, port))
        unsent.is_sent = True


def check_all_sent(pkts):
    for pkt in pkts:
        if not pkt.is_sent:
            return False
    return True


def rcv_ack(ip, port, window_size, sock, mutex, pkts):
    global base_pointer
    oldestUnAcked = 0
    while True:
        mutex.acquire()
        try:
            (data, add) = sock.recvfrom(9216)
            data = json.loads(data)
            pkt = Packetize(data)
            print("ack found!! with seq_num ", pkt.seq_num)
            pkts[pkt.seq_num].is_acked = True
            if pkt.seq_num == oldestUnAcked:
                oldestUnAcked = pkt.seq_num + 1
                base_pointer = oldestUnAcked
            # get first un acked after it
            if pkts[base_pointer].is_acked:
                for i in range(window_size):
                    try:
                        if pkts[base_pointer + i].is_acked == False:  # check here!
                            base_pointer = base_pointer + i
                            oldestUnAcked = base_pointer
                            break
                    except:
                        pass
            print("oldest Unacked =",oldestUnAcked,"base pointer = ",base_pointer)
        except Exception:
            pass
        mutex.release()
        time.sleep(0.5)
    return -1


SelectiveRepeat_server()
