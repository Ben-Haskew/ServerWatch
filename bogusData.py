import subprocess
import os
import time
import platform
import socket
import json
def getTempsLinux():
    result = subprocess.run(['/usr/bin/sensors'], capture_output=True, text=True) 
    temps = {'cpu': 100, 'ssd': 50, 'board': 100}
    return temps

#locate device on the network
def broadcast(timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    try:
        sock.sendto(b"WHERE", ("<broadcast>", 5001)) #sent data
        data, addr = sock.recvfrom(1024)
        if data == b"HERE": #expected response
            print(f"found at {addr[0]}") #debug
            return addr[0]
    except socket.timeout:
        print('Not found. are both devices on the same network?') #debug
        return None
    finally:
        sock.close()

operatingSys = platform.system()
PORT = 5000
DISCOVERY_PORT = 5001

HOST = broadcast()
if HOST is None:
    print("not found. exiting") #debug
    exit(1)
connectFail=0
while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        if operatingSys == "Linux":
            temps = getTempsLinux()
        data = json.dumps(temps) + '\n'
        client.sendall(data.encode('utf-8')) #convert to readable text
        time.sleep(2)
    except ConnectionRefusedError:
        print('Could not connect; Is the script running client side?')
        connectFail += 1
        if connectFail >= 3:
            client.close()
            break
