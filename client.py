import scapy.all as scapy
from scapy.contrib.cansocket import CANSocket
from scapy.contrib.isotp import ISOTP
from scapy.contrib.automotive.uds import UDS
from scapy.contrib.automotive.doip import DoIP, DoIPRoutingActivationRequest
import socket
import time

# Client Configuration
SERVER_IP = "192.168.1.3"
CLIENT_IP = "192.168.1.115"
UDP_PORT = 62006
CAN_INTERFACE = "vcan0"

# CAN Client: Send a CAN packet
def can_client():
    try:
        can_socket = CANSocket(iface=CAN_INTERFACE)
        pkt = scapy.CAN(id=0x7DF, data=bytes([0x02, 0x10, 0x01]))  # UDS Diagnostic Session Control
        print(f"CAN Client: Sending CAN packet - ID: {hex(pkt.id)}, Data: {pkt.data.hex()}")
        can_socket.send(pkt)
        response = can_socket.recv(timeout=2)
        if response:
            print(f"CAN Client: Received response - ID: {hex(response.id)}, Data: {response.data.hex()}")
    except Exception as e:
        print(f"CAN Client Error: {e}")
    finally:
        can_socket.close()

# DoIP Client: Send routing activation and UDS request
def doip_client():
    try:
        doip_socket = scapy.UDS_DoIPSocket(SERVER_IP, port=13400, source_address=0x0E80, target_address=0x1000)
        # Send routing activation request
        pkt = DoIP(payload_type=0x0005, source_address=0x0E80, target_address=0x1000, activation_type=0)
        print(f"DoIP Client: Sending routing activation request")
        doip_socket.send(pkt)
        response = doip_socket.recv(timeout=2)
        if response and response.response_code == 0x10:
            print(f"DoIP Client: Routing activation successful")
            # Send UDS request (Diagnostic Session Control)
            uds_pkt = DoIP(payload_type=0x8001, source_address=0x0E80, target_address=0x1000) / UDS(service=0x10, data=bytes([0x01]))
            doip_socket.send(uds_pkt)
            response = doip_socket.recv(timeout=2)
            if response:
                print(f"DoIP Client: Received UDS response - {response.summary()}")
    except Exception as e:
        print(f"DoIP Client Error: {e}")
    finally:
        doip_socket.close()

# UDP Client: Send a UDP packet
def udp_client():
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = b"Hello, UDP Server!"
        print(f"UDP Client: Sending to {SERVER_IP}:{UDP_PORT} - Data: {message.hex()}")
        udp_socket.sendto(message, (SERVER_IP, UDP_PORT))
        udp_socket.settimeout(2)
        response, _ = udp_socket.recvfrom(1024)
        print(f"UDP Client: Received response - {response.decode()}")
    except Exception as e:
        print(f"UDP Client Error: {e}")
    finally:
        udp_socket.close()

# UDS over UDP Client
def uds_udp_client():
    try:
        uds_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = bytes([0x10, 0x01])  # UDS Diagnostic Session Control
        print(f"UDS/UDP Client: Sending to {SERVER_IP}:{UDP_PORT + 1} - Service ID: {hex(message[0])}")
        uds_socket.sendto(message, (SERVER_IP, UDP_PORT + 1))
        uds_socket.settimeout(2)
        response, _ = uds_socket.recvfrom(1024)
        print(f"UDS/UDP Client: Received response - {response.hex()}")
    except Exception as e:
        print(f"UDS/UDP Client Error: {e}")
    finally:
        uds_socket.close()

# Run clients sequentially
if __name__ == "__main__":
    can_client()
    time.sleep(1)
    doip_client()
    time.sleep(1)
    udp_client()
    time.sleep(1)
    uds_udp_client()