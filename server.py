import scapy.all as scapy
from scapy.contrib.cansocket import CANSocket
from scapy.contrib.isotp import ISOTP
from scapy.contrib.automotive.uds import UDS
from scapy.contrib.automotive.doip import DoIP, DoIPRoutingActivationRequest
import socket
import threading
import time

# Server Configuration
SERVER_IP = "192.168.1.3"
CLIENT_IP = "192.168.1.115"
UDP_PORT = 62006
CAN_INTERFACE = "vcan0"  # Virtual CAN interface (requires setup: sudo modprobe vcan; sudo ip link add dev vcan0 type vcan; sudo ip link set up vcan0)

# CAN Server: Listen for CAN messages
def can_server():
    try:
        can_socket = CANSocket(iface=CAN_INTERFACE)
        print(f"CAN Server: Listening on {CAN_INTERFACE}")
        while True:
            pkt = can_socket.recv()
            if pkt:
                print(f"CAN Server: Received CAN packet - ID: {hex(pkt.id)}, Data: {pkt.data.hex()}")
                # Echo back a response
                response = scapy.CAN(id=0x7DF, data=bytes([0x02, 0x10, 0x01]))  # Example UDS Diagnostic Session Control
                can_socket.send(response)
    except Exception as e:
        print(f"CAN Server Error: {e}")
    finally:
        can_socket.close()

# DoIP Server: Handle DoIP routing activation and UDS requests
def doip_server():
    try:
        doip_socket = scapy.UDS_DoIPSocket(SERVER_IP, port=13400, source_address=0x0E80, target_address=0x1000)
        print(f"DoIP Server: Listening on {SERVER_IP}:13400")
        while True:
            pkt = doip_socket.recv()
            if pkt:
                print(f"DoIP Server: Received packet - {pkt.summary()}")
                if isinstance(pkt, DoIPRoutingActivationRequest):
                    # Respond to routing activation
                    response = DoIP(payload_type=0x0006, source_address=0x1000, target_address=0x0E80, activation_type=0, response_code=0x10)
                    doip_socket.send(response)
                elif isinstance(pkt, UDS):
                    # Handle UDS request (e.g., Diagnostic Session Control)
                    if pkt.service == 0x10:  # Diagnostic Session Control
                        response = UDS(service=0x50, data=bytes([0x01]))  # Positive response
                        doip_socket.send(DoIP(payload_type=0x8001, source_address=0x1000, target_address=0x0E80) / response)
    except Exception as e:
        print(f"DoIP Server Error: {e}")
    finally:
        doip_socket.close()

# UDP Server: Listen for UDP packets
def udp_server():
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((SERVER_IP, UDP_PORT))
        print(f"UDP Server: Listening on {SERVER_IP}:{UDP_PORT}")
        while True:
            data, addr = udp_socket.recvfrom(1024)
            print(f"UDP Server: Received from {addr} - Data: {data.hex()}")
            # Echo back a response
            udp_socket.sendto(b"UDP Response: " + data, addr)
    except Exception as e:
        print(f"UDP Server Error: {e}")
    finally:
        udp_socket.close()

# UDS over UDP Server (simplified, using raw UDP for UDS)
def uds_udp_server():
    try:
        uds_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        uds_socket.bind((SERVER_IP, UDP_PORT + 1))  # Use a different port for UDS
        print(f"UDS/UDP Server: Listening on {SERVER_IP}:{UDP_PORT + 1}")
        while True:
            data, addr = uds_socket.recvfrom(1024)
            if len(data) >= 1:
                service_id = data[0]
                print(f"UDS/UDP Server: Received from {addr} - Service ID: {hex(service_id)}")
                if service_id == 0x10:  # Diagnostic Session Control
                    response = bytes([0x50, 0x01])  # Positive response
                    uds_socket.sendto(response, addr)
    except Exception as e:
        print(f"UDS/UDP Server Error: {e}")
    finally:
        uds_socket.close()

# Run servers in separate threads
if __name__ == "__main__":
    threads = [
        threading.Thread(target=can_server),
        threading.Thread(target=doip_server),
        threading.Thread(target=udp_server),
        threading.Thread(target=uds_udp_server)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()