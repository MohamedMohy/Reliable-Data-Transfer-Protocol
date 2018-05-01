import socket
import json
import Packet
import time
import random
import Shared
import math

SEQ_NUMBER = 0


def send_file_name(data, client_socket):
    new_packet = Packet.Packet(data, SEQ_NUMBER)
    new_packet.deadline = time.time() + 100
    client_socket.sendto(json.dumps(new_packet, cls=Packet.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def plp():
    return random.uniform(0, 1)


def send_acks(client_socket, seq_num):
    if seq_num == 1:
        new_packet = Packet.Packet("Ack", SEQ_NUMBER, 1)
        toggle()
    else:
        new_packet = Packet.Packet("Ack", SEQ_NUMBER, 1)
    new_packet.deadline = time.time() + 100
    client_socket.sendto(json.dumps(new_packet, cls=Packet.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def listen(client_socket):
    while True:
        (packet, address) = client_socket.recvfrom(10000)
        packet = packet.decode()
        packet = Packet.my_decoder(json.loads(packet))
        print(packet.seq_num)
        print(SEQ_NUMBER)
        if packet is not None:
            if packet.is_ack() or packet.seq_num != SEQ_NUMBER:
                if packet.seq_num != SEQ_NUMBER:
                    send_acks(client_socket, 0)
                    print('Duplicate')
                else:
                    print("Ack")
            else:
                file = open("packet.txt", "a")
                file.write(packet.data)
                file.close()
                send_acks(client_socket, 1)


def client():
    information_list = Shared.read_information_file()
    Shared.SERVER_IP = information_list[0]
    Shared.SERVER_PORT = int(information_list[1])
    Shared.My_Port = int(information_list[2])
    Shared.FILE_NAME = information_list[3]
    Shared.WINDOW_SIZE = int(information_list[4])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((Shared.MY_IP, Shared.My_Port))
    send_file_name(Shared.FILE_NAME, sock)
    listen(sock)


def toggle():
    global SEQ_NUMBER
    if SEQ_NUMBER == 0:
        SEQ_NUMBER = 1
    else:
        SEQ_NUMBER = 0


client()