```python
       import scapy.all as scapy
       from scapy.contrib.cansocket import CANSocket
       import socket
       import threading

       # Configuration
       CAN_INTERFACE = "vcan0"
       UDP_IP = "192.168.1.115"  # Destination IP (PC2)
       UDP_PORT = 62006           # Same port as in documents
       LOCAL_IP = "192.168.1.3"   # Local IP (PC1)

       def can_to_udp():
           can_socket = CANSocket(iface=CAN_INTERFACE)
           udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
           try:
               print(f"Forwarding CAN from {CAN_INTERFACE} to {UDP_IP}:{UDP_PORT}")
               while True:
                   pkt = can_socket.recv()
                   if pkt:
                       # Serialize CAN frame (ID and data)
                       can_data = bytes([pkt.id >> 8, pkt.id & 0xFF]) + pkt.data
                       udp_socket.sendto(can_data, (UDP_IP, UDP_PORT))
           except Exception as e:
               print(f"CAN to UDP Error: {e}")
           finally:
               can_socket.close()
               udp_socket.close()

       def udp_to_can():
           udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
           udp_socket.bind((LOCAL_IP, UDP_PORT))
           can_socket = CANSocket(iface=CAN_INTERFACE)
           try:
               print(f"Listening for UDP on {LOCAL_IP}:{UDP_PORT} to forward to {CAN_INTERFACE}")
               while True:
                   data, addr = udp_socket.recvfrom(1024)
                   if len(data) >= 2:
                       # Reconstruct CAN frame
                       can_id = (data[0] << 8) | data[1]
                       can_data = data[2:]
                       pkt = scapy.CAN(id=can_id, data=can_data)
                       can_socket.send(pkt)
           except Exception as e:
               print(f"UDP to CAN Error: {e}")
           finally:
               udp_socket.close()
               can_socket.close()

       if __name__ == "__main__":
           threading.Thread(target=can_to_udp).start()
           threading.Thread(target=udp_to_can).start()
       ```