import socket
import struct
import time

# Create a raw socket
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

# Set the socket timeout
sock.settimeout(1)

# Set the destination address
dest_addr = "www.example.com"

# Create the ICMP header
icmp_type = 8  # ICMP Echo Request
icmp_code = 0
icmp_checksum = 0
icmp_id = 0
icmp_seq = 0
icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)

# Calculate the checksum
icmp_checksum = checksum(icmp_header)
icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)

# Create the ICMP packet
icmp_packet = icmp_header

# Send the ICMP packet
sock.sendto(icmp_packet, (dest_addr, 0))

# Receive the response
try:
    data, addr = sock.recvfrom(1024)
    print("Received response from {}: {}".format(addr, data))
except socket.timeout:
    print("Request timed out")

# Close the socket
sock.close()
