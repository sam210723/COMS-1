"""
udp-bridge.py
https://github.com/sam210723/COMS-1

Uni-directional UDP to TCP bridge.
"""

import argparse
import socket

argparser = argparse.ArgumentParser(description="Uni-directional UDP to TCP bridge.")
argparser.add_argument("UDP", action="store", help="UDP port")
argparser.add_argument("TCP", action="store", help="TCP port")
args = argparser.parse_args()

UDP_IP = "127.0.0.1"
UDP_PORT = int(args.UDP)
TCP_IP = "127.0.0.1"
TCP_PORT = int(args.TCP)

udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def init():
    print()
    print("UDP Port: {}".format(args.UDP))
    print("TCP Port: {}".format(args.TCP))
    print()

    startUDP()
    startTCP()

    bridge()


def startUDP():
    print("Starting UDP...")

    try:
        udpSocket.bind((UDP_IP, UDP_PORT))
    except socket.error as e:
        if e.errno == 10048:
            print("PORT {} ALREADY IN USE".format(UDP_PORT))
        else:
            print(e)
        
        print("Exiting...\n")
        exit()
    
    print("UDP OK\n")


def startTCP():
    print("Starting TCP...")

    try:
        tcpSocket.connect((TCP_IP, TCP_PORT))
    except socket.error as e:
        if e.errno == 10061:
            print("TCP CONNECTION REFUSED".format())
        else:
            print(e)
        
        print("Exiting...\n")
        exit()

    print("TCP OK\n")


def bridge():
    print("Bridge connected\n")

    while True:
        data, addr = udpSocket.recvfrom(1024)

        try:
            tcpSocket.send(data)
        except socket.error as e:
            if e.errno == 10054:
                print("SOCKET CLOSED BY REMOTE")
            else:
                print(e)
        
        print("Exiting...\n")
        exit()   
    

init()
