import subprocess
import sys
import os
sys.path.append('/home/ben/waveshare/e-Paper/RaspberryPi_JetsonNano/python/lib')
import time
from waveshare_epd import epd2in13_V3
from PIL import Image, ImageDraw, ImageFont



icon = Image.open("/home/ben/serverwatchlowres.png")
icon = icon.convert("1")
epd = epd2in13_V3.EPD()
epd.init()
epd.Clear(0xFF)

image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
draw.text((61, 20), "Server Smart", font=font, fill=0)
draw.text((51, 90), "SYSTEM READY", font=font, fill=0)
image.paste(icon, (1, 1))

epd.display(epd.getbuffer(image))

time.sleep(3)
epd.sleep()
command = subprocess.Popen([sys.executable, "temp.py"])
sys.exit(0)
