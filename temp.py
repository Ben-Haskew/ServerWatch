from serverwatchClient import listen
import sys
sys.path.append('/home/ben/waveshare/e-Paper/RaspberryPi_JetsonNano/python/lib')
import time
import subprocess
from waveshare_epd import epd2in13_V3
from PIL import Image, ImageDraw, ImageFont

epd = epd2in13_V3.EPD()
epd.init()
epd.Clear(0xFF)

def display(info):
    print(f"i recieved {info}")

tempDis = display(listen())
CPU = tempDis
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
x1, y1 = 140, 1
x2, y2 = 140, 31
x3, y3 = 140, 61
w = 80
h = 30

while True:
	draw.rectangle((x1, y1, x1 + w, y1 + h), fill=255)
	draw.rectangle((x2, y2, x2 + w, y2 + h), fill=255)
	draw.rectangle((x3, y3, x3 + w, y3 + h), fill=255)
	draw.text((140, 1), f"{CPU}℃ ", font=font, fill=0)
	draw.text((140, 31), f"{GPU}℃ ", font=font, fill=0)
	draw.text((140, 61), f"{DISC}℃ ", font=font, fill=0)
	epd.displayPartial(epd.getbuffer(image))
	#X and Y values are for display testing purposes
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
