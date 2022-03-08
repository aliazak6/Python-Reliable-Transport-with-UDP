import sys
import socket

from util import *

def sender(receiver_ip, receiver_port, window_size):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pkt_header = PacketHeader(type=2, seq_num=10, length=14)
    pkt_header.checksum = compute_checksum(pkt_header / "Hello, world!\n")
    pkt = pkt_header 
    s.sendto(bytes(pkt), (receiver_ip, receiver_port))

def main():
    """Parse command-line arguments and call sender function """
    receiver_ip = socket.gethostbyname("127.0.0.1")
    receiver_port = 5000
    window_size = 50
    sender(receiver_ip, receiver_port, window_size)

if __name__ == "__main__":
    main()