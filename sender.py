from random import randint
import sys
import socket
import time
from util import *

START = 0
END = 1
DATA = 2
ACK = 3
timeout = 500
def sender(receiver_ip, receiver_port, window_size,message):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendSTART(s,receiver_ip,receiver_port)
    # at this point connection established and data will be sent
    lowest_unacked ,highest_acked,lowest_sent = 0
    pkg_size = len(message) / 1456 + 1
    i = 0
    while highest_acked != pkg_size:
        lastackreceived = time.time()
        highest_acked = sendDATA(s,receiver_ip,receiver_port, window_size, lowest_sent,lastackreceived,message[i*1456(i+1)*1455]) # 0-1455 , 1456-2912, ...
        sendEND()



def sendDATA(s,receiver_ip,receiver_port,window_size,lowest_sent,lastackreceived,msg) -> int:
    window = [] # storing window in order to easily retransmit packages
    sent = lowest_sent
    expected_seq_num = []
    while sent < window_size:
        pkt_header = PacketHeader(type=DATA, seq_num=sent, length=1456) #1500 ethernet limit - 20 ip header - 8 udp header - 16 pkt_header
        pkt_header.checksum = compute_checksum(pkt_header / msg)
        pkt = pkt_header / msg
        window.append(pkt)
        expected_seq_num.append(pkt_header.seq_num)
        s.sendto(bytes(str(pkt),'utf-8'), (receiver_ip, receiver_port))
        sent+=1 
    
    while(len(expected_seq_num) == window_size):
        receiveACK(s, START,lastackreceived,window,expected_seq_num)

        

def sendSTART(s, receiver_ip, receiver_port):
    pkt_header = PacketHeader(type=START, seq_num=randint(0,999999), length=0)
    pkt_header.checksum = compute_checksum(pkt_header) # pkt_header length is 16 bytes // 4 ints.
    pkt = pkt_header
    s.sendto(bytes(str(pkt),'utf-8'), (receiver_ip, receiver_port))
    receiveACK(s, START)

def receiveACK(s, type,lastackreceived,packages,receiver_ip,receiver_port,expected_seq_num) :
    while(True):
        try:
            # receive packet
            pkt, address = s.recvfrom(100)

            # extract header and payload
            pkt_header = PacketHeader(pkt[:16])
            isNotCorrupted = verifyChecksum(pkt_header)
            
            if(isNotCorrupted):

                if(expected_seq_num.contains(pkt_header.seq_num)):
                    expected_seq_num.pop(pkt_header.seq_num)
                    
            # at this point we ensured that arriving packet is not corrupted.
            

        except time.time() - lastackreceived > timeout: 
            # Resend all packets in window
            for package in packages:
                s.sendto(bytes(str(package),'utf-8'), (receiver_ip, receiver_port))
            lastackreceived = time.time # Reset the timer for new ack packages
                
                    


def verifyChecksum(pkt_header,msg) -> bool:

                # verify checksum
                pkt_checksum = pkt_header.checksum
                pkt_header.checksum = 0
                computed_checksum = compute_checksum(pkt_header / msg)
                if pkt_checksum != computed_checksum:
                    print("checksums not match")
                    return False
                else:
                    return True

def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 5:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = socket.gethostbyname(sys.argv[1])
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    message = sys.argv[4]
    sender(receiver_ip, receiver_port, window_size,message)

if __name__ == "__main__":
    main()
