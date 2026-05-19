#import of screen drivers
import socket
import sys
import os

#relaunch with sudo if not root
if os.geteuid() != 0:
    import subprocess
    subprocess.run(['sudo', 'python3'] + sys.argv)
    sys.exit()
#using connection over local wifi
HOST = '192.168.0.121' #hostcomputer
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1) #listen

print(f'Listening on {HOST}:{PORT}')

#this RECIEVES the temps
def listen():
    while True:
        conn, addr = server.accept()
        print(f'Connected from {addr}')
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                temps = json.loads(data.decode('utf-8').strip())
                return{temps['cpu']}
                return{temps['ssd']}
                return{temps['board']}
listen()
