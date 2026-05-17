import sys
sys.path.append('/home/ben/waveshare/e-Paper/RaspberryPi_JetsonNano/python/lib')
import time
import subprocess
from waveshare_epd import epd2in13_V3
from PIL import Image, ImageDraw, ImageFont

epd = epd2in13_V3.EPD()
epd.init()
epd.Clear(0xFF)


def cpuTemp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            rawTemp = int(f.read().strip())
        return rawTemp / 1000.0 #get temp from millicelsius to celsius
    except Exception as e:
        return
def gpuCheck():
	try:
		output = subprocess.check_output("lspci | grep -i vga", shell=True).decode()
		return output.strip()
	except Exception as e:
		return f"Error: {e}"
print(gpuCheck())
CPU = cpuTemp()
GPU = 1
DISC = 1
#initialise screen
image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
#initialise font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
#initilaise and display different temps statuses
draw.text((1, 1), f"Temp (CPU):", font=font, fill=0)
draw.text((1, 31), f"Temp (GPU):", font=font, fill=0)
draw.text((1, 61), f"Temp (DISC):", font=font, fill=0)

#refresh squares
x1 = 140
y1 = 1
x2 = 140
y2 = 31
x3 = 140
y3 = 61
w1 = 80
h1 = 30
w2 = 80
h2 = 30
w3 = 80
h3 = 30

while True:
	draw.rectangle((x1, y1, x1 + w1, y1 + h1), fill=255)
	draw.rectangle((x2, y2, x2 + w2, y2 + h2), fill=255)
	draw.rectangle((x3, y3, x3 + w3, y3 + h3), fill=255)
	draw.text((140, 1), f"{CPU}℃ ", font=font, fill=0)
	draw.text((140, 31), f"{GPU}℃ ", font=font, fill=0)
	draw.text((140, 61), f"{DISC}℃ ", font=font, fill=0)
	epd.displayPartial(epd.getbuffer(image))
	x = 2
	y = 3
	CPU = cpuTemp()
	GPU += x*y+GPU
	DISC += x*y+DISC
	epd.displayPartial(epd.getbuffer(image))
	time.sleep(0.1)
epd.displayPartial(epd.getbuffer(image))
time.sleep(0.1)



epd.sleep()
