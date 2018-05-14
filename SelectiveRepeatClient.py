import time
import main
import Shared
import json
import socket
packets_buffer = []
expected_packets = []
SEQ_NUMBER = -1
base_pointer = 0
number_of_chunks = 0


def send_acks(client_socket):
    new_packet = main.Packet("Ack", SEQ_NUMBER, 1)
    new_packet.seq_num = SEQ_NUMBER
    new_packet.deadline = time.time() + 100
    client_socket.sendto(json.dumps(new_packet, cls=main.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def send_file_name(data, client_socket):
    new_packet = main.Packet(data, SEQ_NUMBER)
    new_packet.deadline = time.time() + 100
    client_socket.sendto(json.dumps(new_packet, cls=main.MyEncoder).encode(), (Shared.SERVER_IP, Shared.SERVER_PORT))


def write_buffered_packets():
    packets_buffer.sort(key=lambda x: x.seq_num, reverse=False)
    for packet in packets_buffer:
        file = open("packet.txt", "a")
        file.write(packet.data)
        file.close()


def biggest_seq_num():
    packets_buffer.sort(key=lambda x: x.seq_num, reverse=False)
    return packets_buffer[-1].seq_num


def search_in_buffer(number):
    for packet in packets_buffer:
        if packet.seq_num == number:
            packets_buffer.remove(packet)
            break


def check_base_pointer():
    for packet in packets_buffer:
        if base_pointer == packet.seq_num:
            return packet


def listen(client_socket):
    while True:
        global base_pointer
        temp = check_base_pointer()
        if temp is not None:
            file = open("packet.txt", "a")
            file.write(temp.data)
            file.close()
            search_in_buffer(temp.seq_num)
            print("packet with number ", temp.seq_num, "is written")
            base_pointer += 1
            continue

        global SEQ_NUMBER
        global packets_buffer
        global number_of_chunks
        (packet, address) = client_socket.recvfrom(9216)
        packet = packet.decode()
        print(packet)
        packet = main.Packetize(json.loads(packet))
        if packet is not None:
            if packet.is_Ack():
                print("Its Ack")
                number_of_chunks = packet.data
            else:

                if packet.seq_num >= base_pointer and packet.seq_num <= base_pointer+Shared.WINDOW_SIZE-1:
                    if packet.seq_num == SEQ_NUMBER + 1:  # expected packet
                        file = open("packet.txt", "a")
                        file.write(packet.data)
                        file.close()
                        print("packet with number ", packet.seq_num, "is written")
                        increment()
                        send_acks(client_socket)
                        base_pointer += 1

                    else:
                        original_value = SEQ_NUMBER
                        SEQ_NUMBER = packet.seq_num
                        send_acks(client_socket)
                        SEQ_NUMBER = original_value
                        packets_buffer.append(packet)

                else:
                    print("out of window range")

        if SEQ_NUMBER == number_of_chunks-1:
            for packet in packets_buffer:
                file = open("packet.txt", "a")
                file.write(packet.data)
                file.close()
                print("packet with number ", packet.seq_num, "is written")

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
