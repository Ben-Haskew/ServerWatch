#if the button is held down for a few seconds on start up
#then the device boots into "demo" mode
#it pulls artificial temperature data, demonstrating the different things that occur
#basic process:
#flash DEMO in big letters twice
#normal temp
#warm -> shows light
#hot -> shows light AND sound
#repeat
import sys
sys.path.append('/home/ben/Whisplay/runtime')
import threading
import time
import numpy as np
from whisplay import WhisplayBoard
from PIL import Image, ImageDraw, ImageFont
import pygame
import subprocess
from whisplay_client import create_whisplay_hardware
from display import _rgb565_bytes

board = WhisplayBoard()
board.set_backlight(15)
currentColour = None
flashThread = None
flashStop = threading.Event()
transitionThread = None
transitionStop = threading.Event()
flashing=False
curSound=None 

board = create_whisplay_hardware(
    app_id="serverwatch",
    display_name="ServerWatch",
    icon="S",
)

press_time = None

def demo():
    def backgroundDisplay(board,):
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        image = Image.new('RGB', (board.LCD_HEIGHT, board.LCD_WIDTH), (11, 16, 24))
        draw = ImageDraw.Draw(image)
        
        draw.text((10, 110),  "DEMO",   font=font, fill=(150, 205, 255))
        image = image.rotate(-90, expand=True)
        board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, _rgb565_bytes(image))

def onPress():
    global press_time
    press_time = time.time()

def onRelease():
    global press_time
    if press_time is not None:
        held = time.time() - press_time
        press_time = None
        if held < 0.5:
            return  # ignore short presses
        elif held >= 1:
            print("yes")
            backgroundDisplay(board)

board.on_button_press(onPress)
board.on_button_release(onRelease)
try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")