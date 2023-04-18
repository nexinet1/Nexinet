import wifi
import time
import urllib.request
import socket

def connect_to_network(ssid, password):
    sta = wifi.Station()
    sta.active(True)
    sta.connect(ssid, password)
    while not sta.isconnected():
        time.sleep(1)
    print("Connected to network")
    print("IP address:", sta.ifconfig()[0])
    return sta

if __name__ == "__main__":
    ssid = "MyMeshNetwork"
    password = "password"
    gateway_ip = "192.168.1.1"

    while True:
        # Connect to the mesh network and request an IP address
        sta = connect_to_network(ssid, password)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(b"DHCP request", ("255.255.255.255", 5000))
        response, _ = s.recvfrom(1024)
        s.close()

        # Use the assigned IP address to access the internet through the gateway node
        ip_address = response.decode()
        while True:
            try:
                urllib.request.urlopen("http://www.google.com", timeout=5, source_address=(ip_address, 0))
                print("Connected to internet")
                break
            except:
                print("Could not connect to internet, retrying in 10 seconds...")
                time.sleep(10)
        
        # Wait for connection to be lost before trying to reconnect
        while True:
            try:
                urllib.request.urlopen("http://www.google.com", timeout=5, source_address=(ip_address, 0))
            except:
                print("Connection lost, retrying in 10 seconds...")
                break
            time.sleep(10)
