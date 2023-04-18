import wifi
import time
import socket
import pycreate2
import subprocess
import os

def start_ap(ssid, password):
    ap = wifi.AccessPoint()
    ap.active(True)
    ap.config(essid=ssid, password=password)
    ap.ifconfig(('192.168.1.1', '255.255.255.0', '192.168.1.1', '192.168.1.1'))
    ap.dhcp_server(1)
    return ap

def start_routing():
    # Enable IP forwarding
    subprocess.run("echo 1 > /proc/sys/net/ipv4/ip_forward", shell=True)

    # Configure iptables to forward traffic
    subprocess.run("iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE", shell=True)
    subprocess.run("iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT", shell=True)
    subprocess.run("iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT", shell=True)

if __name__ == "__main__":
    ssid = "MyMeshNetwork"
    password = "password"

    # Start the access point on this node
    ap = start_ap(ssid, password)

    # Start routing
    start_routing()

    # Wait for other nodes to join the network
    time.sleep(10)

    # Find other nodes in the network
    nodes = pycreate2.Create2.create2_network()

    # Set up congestion control and FASS
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, 'reno')
    channels = [1, 6, 11]

    # Send a message to all nodes in the network
    for node in nodes:
        node_ip = node.get_ip_address()
        channel_index = nodes.index(node) % len(channels)
        channel = channels[channel_index]
        sock.connect((node_ip, 5000))
        sock.sendall(b"Hello from " + ap.essid.encode())
        sock.sendall(b"Channel: " + str(channel).encode())
        sock.close()

    # Wait for responses from all nodes
    responses = []
    for node in nodes:
        node_ip = node.get_ip_address()
        channel_index = nodes.index(node) % len(channels)
        channel = channels[channel_index]
        sock.connect((node_ip, 5000))
        sock.sendall(b"Channel: " + str(channel).encode())
        response = sock.recv(1024)
        responses.append(response)
        sock.close()

    # Print the responses from all nodes
    for response in responses:
        print(response.decode())
