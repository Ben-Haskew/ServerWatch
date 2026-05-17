#import of screen drivers
import subprocess
import sys
import serial

#startup socat
proc = subprocess.Popen( #open as child, script keeps going
    ['sudo', 'socat', '-v', '/dev/ttyGS0,rawer', '-'], #like running the command in a terminal ##socat functions as the bridge
    stdout=subprocess.PIPE, #capture output
    stderr=subprocess.DEVNULL #get rid of error messages
)

print('ready')
sys.stdout.flush()

#data recieving logic
for line in proc.stdout: #loops
    text = line.decode('utf-8', errors='replace').strip() #convert data into string
    if text and not text.startswith('>'): #skip rubbish data
        print("recieved:", text) #display what data was recieved in command line
        sys.stdout.flush()
        #code that displays the input on the screen will go here
