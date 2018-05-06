MY_IP = "192.168.1.183"
My_Port = None
SERVER_IP = None
SERVER_PORT = None
FILE_NAME = None
WINDOW_SIZE = None


def read_information_file():
    temp = open("information.txt").read().splitlines()
    return temp
