import kivy
kivy.require('1.11.1')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import wifi
import socket
import urllib.request

class MeshClient(BoxLayout):
    def __init__(self, **kwargs):
        super(MeshClient, self).__init__(**kwargs)
        self.station = None
        self.connected = False
        self.ip_address = None
        self.gateway_ip = None

    def connect_to_network(self, ssid, password):
        self.station = wifi.Station()
        self.station.active(True)
        self.station.connect(ssid, password)
        while not self.station.isconnected():
            pass
        print("Connected to network")
        print("IP address:", self.station.ifconfig()[0])
        self.ip_address = self.station.ifconfig()[0]
        self.connected = True

    def request_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(b"DHCP request", ("255.255.255.255", 5000))
        response, _ = s.recvfrom(1024)
        s.close()
        self.gateway_ip = "192.168.1.1"
        self.ip_address = response.decode()

    def access_internet(self):
        if self.station is None or not self.connected:
            print("Not connected to network")
            return
        try:
            urllib.request.urlopen("http://www.google.com", timeout=5, source_address=(self.ip_address, 0))
            print("Internet access successful")
        except:
            print("Internet access failed")

    def on_connect_button_press(self):
        ssid = self.ids.ssid_input.text
        password = self.ids.password_input.text
        self.connect_to_network(ssid, password)

    def on_request_ip_button_press(self):
        self.request_ip_address()

    def on_access_internet_button_press(self):
        self.access_internet()

class MeshApp(App):
    def build(self):
        return MeshClient()

if __name__ == '__main__':
    MeshApp().run()
