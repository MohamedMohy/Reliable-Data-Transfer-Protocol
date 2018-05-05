MY_IP = "127.0.0.1"
My_Port = None
SERVER_IP = None
SERVER_PORT = None
FILE_NAME = None
WINDOW_SIZE = None


def read_information_file():
    temp = open("information.txt").read().splitlines()
    return temp
