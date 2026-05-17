import sys, subprocess

proc = subprocess.Popen( #open as child, script keeps going
    ['sudo', 'socat', '-v', '/dev/ttyGS0,rawer', '-'], #like running the command in a terminal ##socat functions as the bridge
    stdout=subprocess.PIPE, #capture output
    stderr=subprocess.DEVNULL #get rid of error messages
)

print('Listening...')
sys.stdout.flush()

for line in proc.stdout:
    text = line.decode('utf-8', errors='replace').strip()
    if text and not text.startswith('>'):
        print("GOT:", text)
        sys.stdout.flush()