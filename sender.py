from email import message
from random import randint
import sys
import socket
import time
from util import *
import select

START = 0
END = 1
DATA = 2
ACK = 3
timeout = 500

def sender(receiver_ip, receiver_port, window_size,message):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    expected_seq_num = 0
    pkg_size = int(len(message) / 1456 + 1)
    sendSTART(s,receiver_ip,receiver_port,pkg_size)
    # at this point connection established and data will be sent
    base = 0
    buffer_size = pkg_size
    buffer = [0]*buffer_size
    while base < pkg_size-1:
        base = sendDATA(s,receiver_ip,receiver_port, window_size, base, message,pkg_size,buffer,expected_seq_num)
    sendEND(s,receiver_ip,receiver_port,base)

def sendSTART(s,receiver_ip,receiver_port,pkg_size):
    Seq_num=randint(0,999999)
    pkt_header = PacketHeader(type=START, seq_num=Seq_num, length=4)
    pkt_header.checksum = compute_checksum(pkt_header / str(pkg_size)) # pkt_header length is 16 bytes // 4 ints.
    pkt = pkt_header / str(pkg_size)
    byte_pkt = bytes(pkt)
    s.sendto(byte_pkt, (receiver_ip, receiver_port))
    print(byte_pkt)
    receive_STARTACK(s,receiver_ip,receiver_port,Seq_num,byte_pkt)

def receive_STARTACK(s,receiver_ip,receiver_port,Seq_num,byte_pkt):
    while(True):
        ready = select.select([s], [], [], timeout/1000) # this is where we implement the timer.
        if ready[0]:
            # receive packet
            pkt , _ = s.recvfrom(100)

            # extract header and payload
            pkt_header = PacketHeader(pkt[:16])
            isNotCorrupted = verifyChecksumHeader(pkt_header)
            
            if(isNotCorrupted and Seq_num ==pkt_header.seq_num and pkt_header.type == ACK ):
                 break      
        else:
            s.sendto(byte_pkt, (receiver_ip, receiver_port))
            receive_STARTACK(s,receiver_ip,receiver_port,Seq_num,byte_pkt)

def sendDATA(s,receiver_ip,receiver_port,window_size,base,msg,pkg_size,buffer,expected_seq_num) :
    packages = [] # storing window in order to easily retransmit packages
    sent = base
    
    while sent < min(base + window_size,pkg_size):
        if(buffer[sent] == 0): # if receiver didnt ack that package
            pkt_header = PacketHeader(type=DATA, seq_num=sent, length=1456) #1500 ethernet limit - 20 ip header - 8 udp header - 16 pkt_header

            p = randint(1,30)
            pkt_msg = msg[sent*1456:(sent+1)*1456-1]
            pkt_header.checksum = compute_checksum(pkt_header / pkt_msg)
            print(len(pkt_msg) ,"   " ,sent)
            pkt = pkt_header / pkt_msg
            packages.append(pkt)
            if(p%5==0):
                pkt_header = PacketHeader(type=DATA, seq_num=0, length=1456) #1500 ethernet limit - 20 ip header - 8 udp header - 16 pkt_header
                pkt_header.checksum = compute_checksum(pkt_header / pkt_msg)
                pkt = pkt_header / pkt_msg
            s.sendto(bytes(pkt), (receiver_ip, receiver_port))
        sent+=1 
        if(base == pkg_size-1):
            return base

    base = receiveACK(s,packages,receiver_ip,receiver_port,base,buffer,expected_seq_num)   
    return base  

def receiveACK(s,packages,receiver_ip,receiver_port,base,buffer,expected_seq_num) :
    old_base = base
    while(True):
        # receive packet
        ready = select.select([s], [], [], timeout/1000) # this is where we implement the timer.
        if ready[0]:
            pkt,_ = s.recvfrom(100)
            # extract header and payload
            pkt_header = PacketHeader(pkt[:16])
            isNotCorrupted = verifyChecksumHeader(pkt_header)
                # at this point we ensured that arriving packet is not corrupted. 
            if(isNotCorrupted and pkt_header.type == ACK):
                buffer[pkt_header.seq_num] = 1 # buffers ACK'ed packages
                print(base)
                base = increase_base(buffer,base)
        else:
            if(old_base == base): # Resend all packets in window
                for package in packages:
                    if(buffer[package.seq_num]==0):
                        s.sendto(bytes(package), (receiver_ip, receiver_port))
                base = receiveACK(s,packages,receiver_ip,receiver_port,base,buffer,expected_seq_num)
            else:
                return base
                
def sendEND(s,receiver_ip,receiver_port,base):
    pkt_header = PacketHeader(type=END, seq_num=base, length=0)
    pkt_header.checksum = compute_checksum(pkt_header) # pkt_header length is 16 bytes // 4 ints.
    pkt = pkt_header
    byte_pkt = bytes(pkt)
    s.sendto(byte_pkt, (receiver_ip, receiver_port))
    receive_ENDACK(s,receiver_ip,receiver_port,base,byte_pkt)                    

def receive_ENDACK(s,receiver_ip,receiver_port,base,byte_pkt):
    while(True):
        ready = select.select([s], [], [], timeout/1000) # this is where we implement the timer.
        if ready[0]:
            # receive packet
            pkt , _ = s.recvfrom(100)

            # extract header and payload
            pkt_header = PacketHeader(pkt[:16])
            isNotCorrupted = verifyChecksumHeader(pkt_header)
            
            if(isNotCorrupted and base ==pkt_header.seq_num and pkt_header.type == ACK ):
                return                       

        else : 

            s.sendto(byte_pkt, (receiver_ip, receiver_port))
            receive_ENDACK(s,receiver_ip,receiver_port,base,byte_pkt)

def increase_base(buffer,base) -> int :
    try:
        if(buffer[base]) : # if it is buffered find next necessary packet
            base +=1
            base = increase_base(buffer,base)
            return base
        return base

    except IndexError:
        return base - 1

def main():
    """Parse command-line arguments and call sender function """
    
    if len(sys.argv) != 5:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = socket.gethostbyname(sys.argv[1])
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    message = sys.argv[4]
    sender(receiver_ip, receiver_port, window_size,message)
    print("File successfully sent.")

if __name__ == "__main__":
    main()
