import time
import Packet
import Shared
import json
import socket
packets_buffer = []
expected_packets = []
SEQ_NUMBER = -1
base_pointer = 0


def send_acks(client_socket):
    new_packet = Packet.Packet("Ack", SEQ_NUMBER, 1)
    new_packet.deadline = time.time() + 100
    client_socket.sendto(json.dumps(new_packet, cls=Packet.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def send_file_name(data, client_socket):
    new_packet = Packet.Packet(data, SEQ_NUMBER)
    new_packet.deadline = time.time() + 100
    client_socket.sendto(json.dumps(new_packet, cls=Packet.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def write_buffered_packets():
    packets_buffer.sort(key=lambda x: x.seq_num, reverse=False)
    for packet in packets_buffer:
        file = open("packet.txt", "a")
        file.write(packet.data)
        file.close()


def biggest_seq_num():
    packets_buffer.sort(key=lambda x: x.seq_num, reverse=False)
    return packets_buffer[3].seq_num


def listen(client_socket):
    while True:
        global SEQ_NUMBER
        global base_pointer
        global packets_buffer
        (packet, address) = client_socket.recvfrom(9216)
        packet = packet.decode()
        print(packet)
        packet = Packet.my_decoder(json.loads(packet))
        if packet is not None:
            if packet.is_ack():
                print("Its Ack")
            else:

                if packet.seq_num >= base_pointer and packet.seq_num <= base_pointer+Shared.WINDOW_SIZE-1:
                    if packet.seq_num == SEQ_NUMBER + 1:  # expected packet
                        if len(packets_buffer) == 0:
                            file = open("packet.txt", "a")
                            file.write(packet.data)
                            file.close()
                        increment()
                        send_acks(client_socket)
                        base_pointer += 1
                        print(base_pointer)
                        if len(packets_buffer) != 0:
                            packets_buffer.append(packet)
                        if len(packets_buffer) == Shared.WINDOW_SIZE:
                            write_buffered_packets()
                            packets_buffer.clear()
                            base_pointer = biggest_seq_num()+1
                            SEQ_NUMBER = biggest_seq_num()

                    else:

                        original_value = SEQ_NUMBER
                        SEQ_NUMBER = packet.seq_num
                        send_acks(client_socket)
                        SEQ_NUMBER = original_value
                        packets_buffer.append(packet)
                        if len(packets_buffer) == Shared.WINDOW_SIZE:
                            write_buffered_packets()
                            packets_buffer.clear()
                            base_pointer = biggest_seq_num()+1
                            SEQ_NUMBER = biggest_seq_num()

                else:
                    print("out of window range")


def increment():
    global SEQ_NUMBER
    SEQ_NUMBER += 1


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


client()

