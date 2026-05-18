import subprocess
import os
import time
import platform
import serial
import socket
import json
def get_temps():
        result = subprocess.run(['sensors'], capture_output=True, text=True)
    
        temps = {'cpu': None, 'ssd': None, 'board': None}
        current_chip = None
    
        for line in result.stdout.split('\n'):
            if line and not line.startswith(' ') and not line.startswith('\t') and '°C' not in line and ':' not in line:
                current_chip = line.strip()
        
            if '°C' in line and ':' in line:
                try:
                    label = line.split(':')[0].strip()
                    temp = line.split(':')[1].strip().split('°C')[0].strip().split()[0].lstrip('+')
                    temp = float(temp)
                
                    if current_chip and 'coretemp' in current_chip and 'Package id 0' in label:
                        temps['cpu'] = temp
                    elif current_chip and 'nvme' in current_chip and 'Composite' in label:
                        temps['ssd'] = temp
                    elif current_chip and 'acpitz' in current_chip and 'temp1' in label:
                        temps['board'] = temp
                    
                except (IndexError, ValueError):
                    continue
    
return temps

temps = get_temps()
print(f"CPU:   {temps['cpu']}°C")
print(f"SSD:   {temps['ssd']}°C")
print(f"Board: {temps['board']}°C")

operatingSys = platform.system()
HOST = 'raspberrypi.local'  #Pi's WiFi IP
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if operatingSys == "Linux":
        try:
            client.connect((HOST, PORT))
            print(f'Connected to {HOST}:{PORT}')
            temps = get_temps()
            data = json.dumps(temps) + '\n'
            client.sendall(data.encode('utf-8'))
            print('Sent!')
        except ConnectionRefusedError:
            print('Could not connect - is the Pi listener running?')
        finally:
            client.close()
elif operatingSys == "Windows":
    pass
elif operatingSys == "darwin":
    print("Incompatible operating system! Please refer to the README.MD file")
