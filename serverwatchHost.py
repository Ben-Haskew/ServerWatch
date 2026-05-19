import subprocess
import os
import time
import platform
import serial
import socket
import json
#parse temps function
def getTempsLinux():
        result = subprocess.run(['sensors'], capture_output=True, text=True)
    
        temps = {'cpu': None, 'ssd': None, 'board': None}
        currentChip = None
    
        for line in result.stdout.split('\n'):
            if line and not line.startswith(' ') and not line.startswith('\t') and '°C' not in line and ':' not in line:
                currentChip = line.strip()
        
            if '°C' in line and ':' in line:
                try:
                    label = line.split(':')[0].strip()
                    temp = line.split(':')[1].strip().split('°C')[0].strip().split()[0].lstrip('+')
                    temp = float(temp)
                
                    if currentChip and 'coretemp' in currentChip and 'Package id 0' in label:
                        temps['cpu'] = temp #temp of all cores i think
                    elif currentChip and 'nvme' in currentChip and 'Composite' in label:
                        temps['disc'] = temp #only works on nvme ssds; need SMART data for hdds
                    elif currentChip and 'acpitz' in currentChip and 'temp1' in label:
                        temps['board'] = temp
                    
                except (IndexError, ValueError):
                    continue 
        return temps
temps = getTempsLinux()
print(f"CPU:   {temps['cpu']}°C")
print(f"SSD:   {temps['disc']}°C")
print(f"Board: {temps['board']}°C")

#parse temp funciton (win)
def getTempsWindows():
    pass

operatingSys = platform.system()
HOST = 'raspberrypi.local'  #Pi WiFi IP
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if operatingSys == "Linux":
        try:
            client.connect((HOST, PORT))
            print(f'Connected to {HOST}:{PORT}')
            temps = getTempsLinux()
            data = json.dumps(temps) + '\n'
            client.sendall(data.encode('utf-8'))
            print('Sent!')
        except ConnectionRefusedError:
            print('Could not connect; Is the script running client side?')
        finally:
            client.close()
elif operatingSys == "Windows":
        try:
            client.connect((HOST, PORT))
            print(f'Connected to {HOST}:{PORT}')
            temps = getTempsLinux()
            data = json.dumps(temps) + '\n'
            client.sendall(data.encode('utf-8'))
            print('Sent!')
        except ConnectionRefusedError:
            print('Could not connect; Is the script running client side?')
        finally:
            client.close()
elif operatingSys == "darwin": #macOS
    print("Incompatible operating system! Please refer to the README.MD file")
