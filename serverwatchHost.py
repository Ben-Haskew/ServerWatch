import subprocess
import os
import time
import socket
import json
import importlib
import importlib.util
import sys
import threading
REQUIRED = [
    ('netifaces', 'netifaces')
]

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
import netifaces
import platform
# import clr
#clr.AddReference(r'C:\Users\ben\ServerWatch\LibreHardwareMonitorLib')
# from LibreHardwareMonitor import Hardware


# computer = Hardware.Computer()
# computer.IsCPUEnabled = True
# computer.Open()
#parse temps function
#this GETS the temps

def autoStartLinux(): #add to systemd on first run
    scriptPath = os.path.abspath(__file__)
    service = f"""[Unit]
Description=ServerWatch Host
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {scriptPath}
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
                    temps['ssd'] = temp #only works on nvme ssds; need SMART data for hdds
                elif currentChip and 'acpitz' in currentChip and 'temp1' in label:
                    temps['board'] = temp #temp of the whole board
                    
            except (IndexError, ValueError):
                continue 
    return temps
def getUsageLinux():
    out = subprocess.run(['top', '-bn1'], capture_output=True, text=True).stdout
    cpu = ram = None
    for line in out.split('\n'):
        if line.startswith('%Cpu'):
            idle = float(line.split(',')[3].split()[0])
            cpu = round(100 - idle, 1)
        elif 'MiB Mem' in line:
            parts = line.split(':')[1].split(',')
            total = float(parts[0].split()[0])
            used = float(parts[2].split()[0])
            ram = round(used / total * 100, 1)
    return cpu, ram

print(getUsage())

#parse temp funciton (win)
def getTempsWin():
    temps = {'cpu': None, 'ssd': None, 'board': None}
    try:
        for hw in computer.Hardware:
            if hw.HardwareType == Hardware.HardwareType.CPU:
                hw.Update()
                for sensor in hw.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Temperature:
                        temp = sensor.Value
                        if temp is not None and temp > 0:
                            temps['cpu'] = float(temp)
                            break
    except Exception as e:
        print(f"read error: {e}")
    print(temps)    
    return temps

    #return CPU
def findIp():
    for iface in netifaces.interfaces():
        if any(iface.startswith(x) for x in ['docker','br-','lo','veth','virbr']):
            continue
        addrs= netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip=addr['addr']
                if ip.startswith('192.168.') or ip.startswith('10.') or (
   		    ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31
		):
                    return ip, addr['broadcast']
    return None, None
#locate device on the network
KNOWN_HOSTS = ['192.168.0.120']
def broadcast(timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)
    result=[None]
    try:
        localIp, bcast = findIp()
        print(f"Local IP: {localIp}, Broadcast: {bcast}")
        if localIp:
            sock.bind((localIp, 0))
        targets = ([bcast] if bcast else []) + KNOWN_HOSTS
        for attempt in range(5):
            for t in targets:
                sock.sendto(b"WHERE", (t, 5001))
            # listen for a reply for up to 1s before resending
            sock.settimeout(1)
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
def receiver():
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data == b"HERE":
                result[0] = addr[0]
                return
    except:
        pass

operatingSys = platform.system()
PORT = 5000
DISCOVERY_PORT = 5001
HOST = None

#'192.168.0.120'  #Pi WiFi IP

#this SENDS the temps
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
                # print(f'Connected to {HOST}:{PORT}') #debug
                if operatingSys == "Linux":
                    temps = getTempsLinux()
                    usage = getUsageLinux()
                    # print(f"got temps: {temps}")
                elif operatingSys == "Windows":
                    temps = getTempsWin()
                elif operatingSys == "Darwin": #macOS
                    print("Incompatible operating system! Please refer to the README.MD file")
                data = json.dumps(temps) + '\n'
                client.sendall(data.encode('utf-8')) #convert to readable text
                # print('Sent!') #debug
                time.sleep(2)
    except(ConnectionRefusedError, OSError) as e:
        print({e})
        print('Could not connect; Is the script running client side?')
        print('retrying now...')
        try:
            client.close()
        except:
            pass
        HOST = None
        time.sleep(5)
                # connectFail += 1
                # if connectFail >= 3:
                #     client.close()
                #     break
