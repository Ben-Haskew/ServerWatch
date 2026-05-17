import subprocess
import os
import time
import platform
import serial

# os = platform.system()
# if os == "linux":

# elif os == "windows":
#     pass
# elif os == "darwin"
#     pass

subprocess.run(['stty', '-F', '/dev/ttyACM0', '115200', 'raw', '-crtscts', '-ixon', '-ixoff']) #port config

fd = os.open('/dev/ttyACM0', os.O_RDWR | os.O_NOCTTY) #open port
time.sleep(0.5)
os.write(fd, b'test\n') #test string to send. this will be changed to temp data in later revisions.
print("Sent!") 
os.close(fd) #close port