import subprocess
import os
import time
import platform
import socket
import json
#import WinTmp
#parse temps function
#this GETS the temps
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

#parse temp funciton (win)
def getTempsWin():
    temps = {'cpu': None, 'ssd': None, 'board': None}
    temp = 2
    return temps
    #CPU = WinTmp.CPU_Temp()
    #return CPU
    #print(CPU)

operatingSys = platform.system()
HOST = '192.168.0.120'  #Pi WiFi IP
PORT = 5000

#this SENDS the temps
connectFail = 0
while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        print(f'Connected to {HOST}:{PORT}')
        if operatingSys == "Linux":
            temps = getTempsLinux()
        elif operatingSys == "Windows":
            temps = getTempsWin()
        elif operatingSys == "Darwin": #macOS
            print("Incompatible operating system! Please refer to the README.MD file")
        data = json.dumps(temps) + '\n'
        client.sendall(data.encode('utf-8')) #convert to readable text
        print('Sent!')
        time.sleep(2)
    except ConnectionRefusedError:
        print('Could not connect; Is the script running client side?')
        connectFail += 1
        if connectFail >= 3:
            client.close()
            break
