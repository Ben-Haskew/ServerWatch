import subprocess
import os
import time
import socket, netifaces, ipaddress
import json
import importlib, importlib.util
import sys
import threading
from playersOnline import getPlayerSummary
REQUIRED = [
    ('netifaces', 'netifaces')
]

lastPlayerCheck = 0
playerInfo = None

def depChk():
    missing = []
    for module, package in REQUIRED:
        if importlib.util.find_spec(module) is None:
            missing.append(package)
    if missing:
        for package in missing:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package, '--break-system-packages'])
        os.execv(sys.executable, [sys.executable] + sys.argv) #script restart
depChk()

def autoStartLinux(): #add to systemd on first run
    scriptPath = os.path.abspath(__file__)
    service = f"""[Unit]
Description=ServerWatch Host
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={scriptPath}
ExecStart=/usr/bin/python3 {scriptPath}
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    servicePath = os.path.expanduser("~/.config/systemd/user/serverwatch.service")
    os.makedirs(os.path.dirname(servicePath), exist_ok=True)
    
    if not os.path.exists(servicePath):
        with open(servicePath, 'w') as f:
            f.write(service)
        subprocess.run(['systemctl', '--user', 'enable', 'serverwatch.service'])
        subprocess.run(['systemctl', '--user', 'start', 'serverwatch.service'])
        print("Added to autostart")
    else:
        print("Already in autostart")
autoStartLinux()

def getTempsLinux():
    result = subprocess.run(['/usr/bin/sensors'], capture_output=True, text=True) 
    temps = {'cpu': None, 'ssd': None, 'board': None}
    currentChip = None
    
    for line in result.stdout.split('\n'):
        if line and not line.startswith(' ') and not line.startswith('\t') and '°C' not in line and ':' not in line:
            currentChip = line.strip()
        if '°C' in line and ':' in line:
            try:
                label = line.split(':')[0].strip() #extract name
                temp = line.split(':')[1].strip().split('°C')[0].strip().split()[0].lstrip('+') #extract number
                temp = float(temp) #convert to number
                
                if currentChip and 'coretemp' in currentChip and 'Package id 0' in label:
                    temps['cpu'] = temp #temp of all cores/overall temp
                elif currentChip and 'nvme' in currentChip and 'Composite' in label:
                    temps['ssd'] = temp #ssd
                elif currentChip and 'drivetemp' in currentChip and 'temp1' in label:
                    temps['ssd'] = temp #hdd
                elif currentChip and 'acpitz' in currentChip and 'temp1' in label:
                    temps['board'] = temp #temp of the whole board
                    
            except (IndexError, ValueError):
                continue 
    return temps

def getUsageLinux():
    out = subprocess.run(['top', '-bn1'], capture_output=True, text=True).stdout
    cpu = mem = None
    for line in out.split('\n'):
        if line.startswith('%Cpu'):
            idle = float(line.split(',')[3].split()[0])
            cpu = round(100 - idle, 1)
        elif 'MiB Mem' in line:
            parts = line.split(':')[1].split(',')
            total = float(parts[0].split()[0])
            used = float(parts[2].split()[0])
            mem = round(used / total * 100, 1)
    return {'cpu': cpu, 'mem': mem}

def findIp(): #searches for all ips on the network
    for iface in netifaces.interfaces():
        if any(iface.startswith(x) for x in ['docker','br-','lo','veth','virbr']): #exclude these
            continue
        addrs= netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip=addr['addr']
                if ipaddress.ip_address(ip).is_private and not ip.startswith('127.'):
                    return ip, addr.get('broadcast'), addr.get('netmask')
    return None, None, None
#locate device on the network
def targets(ip, bcast, netmask, maxHosts=1024):
    targets = []
    if bcast:
        targets.append(bcast)
    if ip and netmask:
        net = ipaddress.ip_network(f"{ip}/{netmask}", strict=False)
        print(f"[targets] network is {net} ({net.num_addresses} addresses)") #debug
        if net.num_addresses > maxHosts:           # e.g. a /16: only scan our /24
            net = ipaddress.ip_network(f"{ip}/24", strict=False)
        targets.extend(str(h) for h in net.hosts() if str(h) != ip)

    return list(dict.fromkeys(targets))

def broadcast(timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)
    result=[None]
    try:
        ip, bcast, netmask = findIp()
        print(f"Local IP: {ip}, Broadcast: {bcast}")
        if ip:
            sock.bind((ip, 0))
        target = targets(ip, bcast, netmask)
        for attempt in range(5):
            sock.settimeout(0.2)
            for t in target:
                try:
                    sock.sendto(b"WHERE", (t, 5001))
                except OSError as e:       
                    print(f"send to {t} failed: {e}")
            # listen for a reply for up to 1s before resending
            sock.settimeout(3)
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    print(f"got {data!r} from {addr}")
                    if data == b"HERE":
                        return addr[0]
            except socket.timeout:
                continue
        return None
    except Exception as e:
        print(f"Discovery error: {e}")
        return None
    finally:
        sock.close()

operatingSys = platform.system()
PORT = 5000
DISCOVERY_PORT = 5001
HOST = None

#'192.168.0.120'  #Pi WiFi IP

#this SENDS the data
while True:
    try:
        HOST = broadcast()
        if HOST is None:
            print("not found. retrying") #debug
            time.sleep(5)
            continue
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5)   # start keepalive after 5seconds idle
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2)  # probe every 2sec
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3) # pack it up after 3 times failed
        client.settimeout(10)
        client.connect((HOST, PORT))
        connectFail=0

        while True:
            temps = getTempsLinux()
            usage = getUsageLinux()
            if time.time() - lastPlayerCheck > 10:
                playerInfo = getPlayerSummary()
                lastPlayerCheck = time.time()

            tranmission = {'temps': temps, 'usage': usage, 'players': playerInfo}
            data = json.dumps(tranmission) + '\n'
            client.sendall(data.encode('utf-8')) #convert to readable text
            time.sleep(5) #how long between each send
    except(ConnectionRefusedError, OSError) as e:
        print({e})
        print('Could not connect; Is the script running client side?')
        print('retrying now...')
        try:
            client.close()
        except OSError:
            pass
        HOST = None
        time.sleep(5)
