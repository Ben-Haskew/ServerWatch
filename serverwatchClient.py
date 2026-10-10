import os, sys, subprocess
def autoStartLinux():
    path = "/etc/systemd/system/serverwatch.service"
    if os.environ.get("INVOCATION_ID") or os.path.exists(path):
        return  # started by systemd, or already installed

    if os.geteuid() != 0:
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)  # re-run as root

    script = os.path.abspath(__file__)
    with open(path, "w") as f:
        f.write(f"""[Unit]
Description=ServerWatch Client
After=network-online.target
Wants=network-online.target

[Service]
User={os.environ.get("SUDO_USER", "root")}
WorkingDirectory={os.path.dirname(script)}
ExecStart={sys.executable} {script}
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
""")
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "--now", "serverwatch.service"])
    print("Installed as system service")
    sys.exit(0)  # the service is already running this script

autoStartLinux()
#import of screen drivers
import sys
# sys.path.append('/home/ben/waveshare/e-Paper/RaspberryPi_JetsonNano/python/lib')

# from waveshare_epd import epd2in13_V3
#from PIL import Image, ImageDraw, ImageFont
import time
import socket
import json
import threading
import signal
import pygame
from display import board, ledOff
# epd = epd2in13_V3.EPD()
# epd.init()
# epd.Clear(0xFF)
sys.path.append('/home/ben/Whisplay/runtime')
from display import backgroundDisplay, updateDisplay, board, startDisplay, noDataDisplay

dataTimeout = 15          # seconds without data before the image appears
lastData = time.time()      # starts now, so it also covers "never connected since boot"
showingNoData = False



def watchdog():
    global showingNoData
    while True:
        time.sleep(1)
        if not showingNoData and time.time() - lastData > dataTimeout:
            showingNoData = True
            noDataDisplay()

startDisplay()

def shutdown(signum, frame):
    ledOff(board)
    for action in (
        lambda: board.set_backlight(0),
        lambda: pygame.mixer.quit(),
    ):
        try:
            action()
        except Exception:
            pass
    os._exit(0)

signal.signal(signal.SIGTERM, shutdown)

def respond():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 5001))
    while True:
        data, addr = sock.recvfrom(1024)
        if data == b"WHERE":
            for _ in range(3):
                sock.sendto(b"HERE", addr)
                time.sleep(0.05)
threading.Thread(target=respond, daemon=True).start()

#using connection over local wifi
HOST = '0.0.0.0' #hostcomputer
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1) #listen

print(f'Listening on {HOST}:{PORT}')
threading.Thread(target=watchdog, daemon=True).start()
backgroundDrawn = False
#this RECIEVES the temps
while True:
    conn, addr = server.accept()
    #print(f'Connected from {addr}')
    with conn:
        conn.settimeout(10)
        buffer=""
        while True:
            try:
                data = conn.recv(1024)
            except socket.timeout:
                break
            if not data:
                break
            buffer +=data.decode('utf-8')
            while '\n' in buffer:
                line, buffer=buffer.split('\n', 1)
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        temps = msg['temps']
                        usage = msg.get('usage')
                        players = msg.get('players')
                        if usage:
                            lastData = time.time()
                            if showingNoData:            # coming back from no data screen
                                showingNoData = False
                                backgroundDrawn = False
                            if not backgroundDrawn:
                                backgroundDisplay(board)
                                backgroundDrawn = True
                            updateDisplay(temps['cpu'], temps['ssd'], usage['cpu'], usage['mem'], players)
                    except json.JSONDecodeError as e:
                        print(f"json error: {e}")
                        continue
                    except KeyError as e:
                        print(f"missing key: {e}")
                        continue
