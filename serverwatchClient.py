#import of screen drivers
import sys
# sys.path.append('/home/ben/waveshare/e-Paper/RaspberryPi_JetsonNano/python/lib')
sys.path.append('/home/Whisplay/runtime')
from whisplay import WhisPlayBoard
# from waveshare_epd import epd2in13_V3
from PIL import Image, ImageDraw, ImageFont
from tempNEW import displayScreen
import socket
import sys
import os
import json

# epd = epd2in13_V3.EPD()
# epd.init()
# epd.Clear(0xFF)

#relaunch with sudo if not root
if os.geteuid() != 0:
    import subprocess
    subprocess.run(['sudo', 'python3'] + sys.argv)
    sys.exit()

board = WhisPlayBoard()
board.init()

#using connection over local wifi
HOST = '0.0.0.0' #hostcomputer
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1) #listen

print(f'Listening on {HOST}:{PORT}')

#this RECIEVES the temps
while True:
    conn, addr = server.accept()
    #print(f'Connected from {addr}')
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            temps = json.loads(data.decode('utf-8').strip())
            displayScreen(epd, temps['cpu'], temps['ssd'], temps['board'])