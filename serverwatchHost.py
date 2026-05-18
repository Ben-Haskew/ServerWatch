import subprocess
import os
import time
import platform
import serial

os = platform.system()
if os == "linux":
    subprocess.run(['stty', '-F', '/dev/ttyACM0', '115200', 'raw', '-crtscts', '-ixon', '-ixoff']) #port config
    fd = os.open('/dev/ttyACM0', os.O_RDWR | os.O_NOCTTY) #open port
    time.sleep(0.5) #wait
    os.write(fd, b'test\n') #test string to send. this will be changed to temp data in later revisions.
    print("Sent!") 
    os.close(fd) #close port
elif os == "windows":
    subprocess.run(['stty', '-F', 'COM3', '115200', 'raw', '-crtscts', '-ixon', '-ixoff'])
    fd = os.open('COM3', os.O_RDWR | os.O_NOCTTY) #open port
    time.sleep(0.5) #wait
    os.write(fd, b'test\n') #test string to send. this will be changed to temp data in later revisions.
    print("Sent!") 
    os.close(fd) #close port
elif os == "darwin":
    print("Incompatible operating system! Refer to the README")