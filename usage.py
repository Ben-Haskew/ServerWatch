import sys
sys.path.append('/home/ben/waveshare/e-Paper/RaspberryPi_JetsonNano/python/lib')
import time
from waveshare_epd import epd2in13_V3
from PIL import Image, ImageDraw, ImageFont

epd = epd2in13_V3.EPD()
epd.init()
epd.Clear(0xFF)
CPU = 1
GPU = 1
DISC = 1

image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
draw.text((1, 1), "(CPU): ", font=font, fill=0)
draw.text((1, 31), "(GPU): ", font=font, fill=0)
draw.text((1, 61), "(MEMORY): ", font=font, fill=0)
draw.text((1, 91), "(DISC): ", font=font, fill=0)

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
	draw.text((140, 1), f"{CPU}%", font=font, fill=0)
	draw.text((140, 31), f"{GPU}%", font=font, fill=0)
	draw.text((140, 61), f"{DISC}%", font=font, fill=0)
	draw.text((140, 91), f"{DISC}%", font=font, fill=0)
	epd.displayPartial(epd.getbuffer(image))
	x = 2
	y = 3
	CPU += x*y*CPU
	GPU += x*y+GPU
	DISC += x*y+DISC
	epd.displayPartial(epd.getbuffer(image))
	time.sleep(0.1)

epd.displayPartial(epd.getbuffer(image))
time.sleep(0.1)


epd.sleep()
