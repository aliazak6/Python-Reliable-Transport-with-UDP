from random import randint
import sys
import socket

from util import *

START = 0
END = 1
DATA = 2
ACK = 3

def sender(receiver_ip, receiver_port, window_size,message):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendSTART(s,receiver_ip,receiver_port)
    # at this point connection established and data will be sent
    lowest_unacked ,highest_acked,lowest_sent = 0
    while highest_acked != pkg_size:
        sendDATA(message)

    sendEND()



def sendDATA(s,receiver_ip,receiver_port,window_size,lowest_sent,msg):
    sent = lowest_sent
    while sent < window_size:
        pkt_header = PacketHeader(type=DATA, seq_num=lowest_sent, length=14xx)
        pkt_header.checksum = compute_checksum(pkt_header / msg)
        pkt = pkt_header / msg
        s.sendto(str(pkt), (receiver_ip, receiver_port))
        sent+=1
    receiveACK(s, START)
        

def sendSTART(s, receiver_ip, receiver_port):
    pkt_header = PacketHeader(type=0, seq_num=randint(), length=0)
    pkt_header.checksum = compute_checksum(pkt_header)
    pkt = pkt_header
    s.sendto(pkt, receiver_ip, receiver_port)
    receiveACK(s, START)

def receiveACK(s, type):
    
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
            break
                    




def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = socket.gethostbyname(sys.argv[1])
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    message = str(sys.argv[4])
    sender(receiver_ip, receiver_port, window_size,message)

if __name__ == "__main__":
    main()
