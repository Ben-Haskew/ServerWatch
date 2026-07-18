#import of screen drivers
import sys
# sys.path.append('/home/ben/waveshare/e-Paper/RaspberryPi_JetsonNano/python/lib')

# from waveshare_epd import epd2in13_V3
#from PIL import Image, ImageDraw, ImageFont

import socket
import sys
import os
import json
import threading

# epd = epd2in13_V3.EPD()
# epd.init()
# epd.Clear(0xFF)
sys.path.append('/home/ben/Whisplay/runtime')
from display import backgroundDisplay, updateDisplay, board
def respond():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 5001))
    while True:
        data, addr = sock.recvfrom(1024)
        if data == b"WHERE":
            sock.sendto(b"HERE", addr)
threading.Thread(target=respond, daemon=True).start()

#using connection over local wifi
HOST = '0.0.0.0' #hostcomputer
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1) #listen

print(f'Listening on {HOST}:{PORT}')

#this RECIEVES the temps
backgroundDisplay(board)
while True:
    conn, addr = server.accept()
    #print(f'Connected from {addr}')
    with conn:
        buffer=""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer +=data.decode('utf-8')
            while '\n' in buffer:
                line, buffer=buffer.split('\n', 1)
                line = line.strip()
                if line:
                    try:
                        temps = json.loads(line)
                        updateDisplay(board, temps['cpu'], temps['ssd'], temps['board'])
                    except json.JSONDecodeError as e:
                        print(f"json error: {e}")
                        continue
            
