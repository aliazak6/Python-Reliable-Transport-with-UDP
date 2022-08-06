import binascii
from scapy.all import Packet
from scapy.all import IntField

class PacketHeader(Packet):
    name = "PacketHeader"
    fields_desc = [
        IntField("type", 0),
        IntField("seq_num", 0),
        IntField("length", 0),
        IntField("checksum", 0),
    ]
def compute_checksum(pkt):
    return binascii.crc32(bytes(str(pkt),'utf-8'))

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
