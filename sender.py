from email import message
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

    lastackreceived = time.time()
    sendSTART(s,receiver_ip,receiver_port,lastackreceived)
    # at this point connection established and data will be sent
    base = 0
    pkg_size = int(len(message) / 1456 + 1)
    while base < pkg_size:
        lastackreceived = time.time()
        sendDATA(s,receiver_ip,receiver_port, window_size, base,lastackreceived,message[base*1456:(base+window_size)*1455],pkg_size) # 0-1455 , 1456-2911, ...
    lastackreceived = time.time()
    sendEND()

def sendSTART(s,receiver_ip,receiver_port,lastackreceived):
    Seq_num=randint(0,999999)
    pkt_header = PacketHeader(type=START, seq_num=Seq_num, length=0)
    pkt_header.checksum = compute_checksum(pkt_header) # pkt_header length is 16 bytes // 4 ints.
    pkt = pkt_header
    byte_pkt = bytes(pkt)
    s.sendto(byte_pkt, (receiver_ip, receiver_port))
    print(byte_pkt)
    receive_STARTACK(s,lastackreceived,receiver_ip,receiver_port,Seq_num,byte_pkt)

def receive_STARTACK(s,lastackreceived,receiver_ip,receiver_port,Seq_num,byte_pkt):
    while(True):
        try:
            # receive packet
            pkt , _ = s.recvfrom(100)

            # extract header and payload
            pkt_header = PacketHeader(pkt[:16])
            isNotCorrupted = verifyChecksumHeader(pkt_header)
            
            if(isNotCorrupted and Seq_num ==pkt_header.seq_num and pkt_header.type == ACK ):
                 break      
        except time.time() - lastackreceived > timeout: 
            s.sendto(byte_pkt, (receiver_ip, receiver_port))
            lastackreceived = time.time # Reset the timer for new ack packages
            receive_STARTACK(s,lastackreceived,receiver_ip,receiver_port,Seq_num,byte_pkt)

def sendDATA(s,receiver_ip,receiver_port,window_size,base,lastackreceived,msg,pkg_size) :
    packages = [] # storing window in order to easily retransmit packages
    sent = base
    
    while sent < min(base + window_size,pkg_size):
        pkt_header = PacketHeader(type=DATA, seq_num=sent, length=1456) #1500 ethernet limit - 20 ip header - 8 udp header - 16 pkt_header
        pkt_msg = msg[sent*1456:(sent+1)*1455]
        pkt_header.checksum = compute_checksum(pkt_header / pkt_msg)
        pkt = pkt_header / pkt_msg
        packages.append(pkt)
        s.sendto(bytes(pkt), (receiver_ip, receiver_port))
        sent+=1 

    base = receiveACK(s,lastackreceived,packages,receiver_ip,receiver_port,base)     

def receiveACK(s,lastackreceived,packages,receiver_ip,receiver_port,base) :
    while(True):
        try:
            # receive packet
            pkt, _ = s.recvfrom(100)

            # extract header and payload
            pkt_header = PacketHeader(pkt[:16])
            isNotCorrupted = verifyChecksumHeader(pkt_header)
            
            if(isNotCorrupted and pkt_header.type == ACK):
                base =pkt_header.seq_num + 1 # ACK received
                return base  
            # at this point we ensured that arriving packet is not corrupted.    
        except time.time() - lastackreceived > timeout: 
            # Resend all packets in window
            for package in packages:
                s.sendto(bytes(package), (receiver_ip, receiver_port))
            lastackreceived = time.time # Reset the timer for new ack packages
            receiveACK(s,lastackreceived,packages,receiver_ip,receiver_port,base)
                
def sendEND(s,receiver_ip,receiver_port,lastackreceived,base):
    pkt_header = PacketHeader(type=END, seq_num=base, length=0)
    pkt_header.checksum = compute_checksum(pkt_header) # pkt_header length is 16 bytes // 4 ints.
    pkt = pkt_header
    byte_pkt = bytes(pkt)
    s.sendto(byte_pkt, (receiver_ip, receiver_port))
    receive_ENDACK(s,lastackreceived,receiver_ip,receiver_port,base,byte_pkt)                    

def receive_ENDACK(s,lastackreceived,receiver_ip,receiver_port,base,byte_pkt):
    while(True):
        try:
            # receive packet
            pkt , _ = s.recvfrom(100)

            # extract header and payload
            pkt_header = PacketHeader(pkt[:16])
            isNotCorrupted = verifyChecksumHeader(pkt_header)
            
            if(isNotCorrupted and base ==pkt_header.seq_num and pkt_header.type == ACK ):
                exit                       

        except time.time() - lastackreceived > timeout: 

            s.sendto(byte_pkt, (receiver_ip, receiver_port))
            lastackreceived = time.time # Reset the timer for new ack packages
            receive_ENDACK(s,lastackreceived,receiver_ip,receiver_port,base,byte_pkt)

def main():
    """Parse command-line arguments and call sender function """
    
    #if len(sys.argv) != 5:
    #    sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    #receiver_ip = socket.gethostbyname(sys.argv[1])
    #receiver_port = int(sys.argv[2])
    #window_size = int(sys.argv[3])
    #message = sys.argv[4]
    receiver_ip = socket.gethostbyname("127.0.0.1")
    receiver_port = 5000
    window_size = 50
    message = "mesaj"
    sender(receiver_ip, receiver_port, window_size,message)
    

if __name__ == "__main__":
    main()
