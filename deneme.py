from encodings.utf_8 import decode
from util import *
from random import randint
import pickle
Seq_num=randint(0,999999)
pkt_header = PacketHeader(type=0, seq_num=Seq_num, length=0)
pkt_header.checksum = compute_checksum(pkt_header) # pkt_header length is 16 bytes // 4 ints.
pkt = pkt_header
byte_pkt = pickle.dump(pkt)
print(str.encode("mesaj"))
print(byte_pkt)
