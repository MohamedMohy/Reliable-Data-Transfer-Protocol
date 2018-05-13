import _thread
import json
import socket
from threading import Lock

import main
from GBN import GBNSimulation
from SelectiveRepeat import SelectiveRepeatSimulation
from StopAndWait import StopAndWaitSimulation

thread_table = dict()
lock = Lock()


def multiplex_or_create(pkt, address):
    # with lock:
    packet = main.Packetize(pkt)
    if address in thread_table:
        pass_pkt(packet, address)
    else:
        packets = chunks_into_pkts(main.read_file(packet.data))
        protocol = int(input(
            "please select a protocol for sending \n 1) Go Back N\n2) Selective Repeat\n 3) Stop And Wait \n"))
        choose_protocol(packets, address, protocol, file_name=packet.data)


def pass_pkt(pkt, address):
    global thread_table
    thread_table[address].rcv_ack(pkt)
    return


def chunks_into_pkts(chunks):
    pkts = []
    for i in range(len(chunks)):
        pkt = main.Packet()
        pkt.data = chunks[i]
        pkt.seq_num = i
        pkt.check_sum = main.calculate_checksum(pkt)
        pkts.append(pkt)
    main.drop_pkts(main.mapping(main.plp(1), len(pkts)), pkts)
    return pkts


def choose_protocol(pkts, address, protocol, file_name):
    if protocol == 1:
        go_back_n = GBNSimulation(pkts, address, file_name, window_size=4)
        thread_table[address] = go_back_n
        try:
            _thread.start_new_thread(go_back_n.serve_client, ())
            print("thread fired!!")
        except:
            print("Error: unable to start thread")
    if protocol == 2:
        selective_repeat = SelectiveRepeatSimulation(pkts, address, file_name, window_size=4)
        thread_table[address] = selective_repeat
        try:
            _thread.start_new_thread(selective_repeat.serve_client(), ())
            print("thread fired!!")
        except:
            print("Error: unable to start thread")
    if protocol == 3:
        stop_and_wait = StopAndWaitSimulation(pkts, address, file_name)
        thread_table[address] = stop_and_wait

        try:
            _thread.start_new_thread(stop_and_wait.serve_client(), ())
            print("thread fired!")
        except:
            print("Error: unable to start thread")

    else:
        print("invalid option! please try again")


def runner():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((main.UDP_IP, main.UDP_PORT_SENDER))
    while True:
        packet, add = sock.recvfrom(9216)
        print(json.loads(packet))
        multiplex_or_create(pkt=json.loads(packet), address=add)



runner()
