import sys
import socket
from util import *

START = 0
END = 1
DATA = 2
ACK = 3
timeout = 500

def receiver(receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port)) # 127.0.0.1 means localhost (same computer with sender)
    expected_seq_num = 0
    f = open("output", "wb")
    buffer = []
    EOF = False # end of file

    while ~EOF:
        # receive packet        
        pkt, address = s.recvfrom(1500)
        # extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]
        # verify checksum
        isNotCorrupted = verifyChecksum(pkt_header,msg)
        #send ACK if checksum is correct
        if(isNotCorrupted):
            if(pkt_header.type == START):
                sendACK(s,address,pkt_header.seq_num)
            if(pkt_header.type == DATA):
                if(pkt_header.seq_num <= expected_seq_num+window_size): # bufferin out of order packages
                    buffer[expected_seq_num] = msg
                sendACK(s,address,expected_seq_num) # expected seq num is sent anycase
                if(expected_seq_num == pkt_header.seq_num): 
                    expected_seq_num = calculateSeq()
            if(pkt_header.type == END):
                EOF = True
                sendACK(s,address,pkt_header.seq_num)
        # print payload
        print(str(msg))

    f.write(buffer) # save file when transmition ends.
    f.close()

def calculateSeq(buffer,expected_seq_num):
    if(buffer[expected_seq_num]): # if it is buffered find next necessary packet
        expected_seq_num +=1
        calculateSeq(buffer,expected_seq_num)
    else:
        expected_seq_num +=1

def sendACK (s,address, Seq_num):
    pkt_header = PacketHeader(type=ACK, seq_num=Seq_num, length=0)
    pkt_header.checksum = compute_checksum(pkt_header)
    pkt = pkt_header
    s.sendto(pkt, address)

def constructDATA(f,msg,seq_num):
    f.write(msg)

def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)

if __name__ == "__main__":
    main()
