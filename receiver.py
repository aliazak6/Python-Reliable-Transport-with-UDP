import sys
import socket

from util import *

START = 0
END = 1
DATA = 2
ACK = 3

def receiver(receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port))
    while True:
        # receive packet
        pkt, address = s.recvfrom(1500)

        # extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]

        # verify checksum
        checksum = False
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg)
        if pkt_checksum != computed_checksum:
            print("checksums not match")
        else:
            checksum = True
        #send ACK if checksum is correct
        if(checksum):
            if(pkt_header.type == START):
                sendACK(s,address,pkt_header.seq_num)
            if(pkt_header.type == DATA):
                sendACK(s,address,pkt_header.seq_num+1)

        # print payload
        print(str(msg))

def sendACK (s,address, Seq_num):

    pkt_header = PacketHeader(type=ACK, seq_num=Seq_num, length=0)
    pkt_header.checksum = compute_checksum(pkt_header)
    pkt = pkt_header
    s.sendto(pkt, address)



def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)

if __name__ == "__main__":
    main()
