# Network live monitoring tool. @DimitarYordanov17

# Visualisation
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Networking
from scapy.all import sniff
import socket
import fcntl
import ipaddress
import requests

# Others
import time
import struct
import math

INTERFACE = input("Which interface to monitor on:  ")

class Network:
    def __init__(self):
        self.connections  = []
        self.ip_address = self.get_local_ip_address(INTERFACE)

    def get_next_packet_address(self):
        """
        Generator function to extract the not host address of a received packet
        """
        
        while True:
            packet = sniff(iface=INTERFACE, count=1)
            packet_IP = packet[0]["IP"]
            
            source_address = packet_IP.src 
            destination_address = packet_IP.dst
            
            not_host_address = source_address if destination_address == self.ip_address else destination_address
            
            if ipaddress.ip_address(not_host_address).is_global:
                if not_host_address not in self.connections:
                    self.connections.append(not_host_address)
                    return not_host_address
                

    def get_address_info(self, ip_address):
        """
        Get geolocation (lat, lon) of an IPv4 address
        WARNING: There might be value errors in the server's database
        """
        
        request = requests.get(f"https://geolocation-db.com/jsonp/{ip_address}").content.decode()
        geolocation = request[request.index("latitude"):request.index("IPv4")-2].split(',')
        
        lat = float(geolocation[0].split(":")[1])
        lon = float(geolocation[1].split(":")[1])

        return lat, lon

    def get_local_ip_address(self, interface):
        """
        Get specific interface local IPv4 address
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(interface[:15], 'utf-8')))[20:24])


def geo_to_xy(latitude, longitude, plane_width, plane_height):
    """
    Map ip address corresponding geolocation to the a (x, y) coordinate for the background image
    """

    FE = 180
    radius = plane_width / (2 * math.pi)

    latitude_radians = (latitude * math.pi) / 180;
    longitude_radians = ((longitude + FE) * math.pi) / 180;

    x = longitude_radians * radius

    y_from_equator = radius * math.log(math.tan(math.pi / 4 + latitude_radians / 2))
    y = plane_height / 2 - y_from_equator

    return x, y


def draw_connection(_):
    ip_address = n.get_next_packet_address()

    try:
        lat, lon = n.get_address_info(ip_address)
        x, y = geo_to_xy(lat, lon, len(image[0]), len(image))

        plt.scatter(x, y, c = "black", linewidths=3, marker="p", edgecolor="blue")
    except:
        pass

def main():
    fig, ax = plt.subplots(figsize=(19, 10))
    ax.imshow(image)

    plt.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    animate = animation.FuncAnimation(fig, draw_connection)
    plt.show()

if __name__ == "__main__":
    n = Network()
    image = plt.imread("background.jpg")
    main()
