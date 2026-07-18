import sys
sys.path.append('/home/ben/Whisplay/runtime')
import threading
import time
import numpy as np
from whisplay import WhisplayBoard
from PIL import Image, ImageDraw, ImageFont
import pygame
import subprocess

board = WhisplayBoard()
board.set_backlight(15)
currentColour = None
flashThread = None
flashStop = threading.Event()
transitionThread = None
transitionStop = threading.Event()
flashing=False
curSound=None 

#DONT TOUCH#
#function to convert PIL image into RGB
def _rgb565_bytes(image: Image.Image) -> bytes:
    rgb = np.array(image.convert("RGB"), dtype=np.uint16)
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return rgb565.astype(np.uint16).byteswap().tobytes()

def initAudio():
    card = None
    try:
        with open("/proc/asound/cards", "r") as f:
            for line in f:
                if "wm8960" in line.lower():
                    card = line.split()[0]
                    break
    except:
        pass
    if card: 
        commands = [["amixer", "-c", card, "sset", "Left Output Mixer PCM", "on"],["amixer", "-c", card, "sset", "Right Output Mixer PCM", "on"],["amixer", "-c", card, "sset", "Speaker", "121"],["amixer", "-c", card, "sset", "Playback", "230"],]
        for cmd in commands:
            subprocess.run(cmd, capture_output=True)

    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

def sound(frequency=440, duration=0.2, volume=0.75, shape="sine", loops=-1, pause=0.2):
    global curSound
    if not pygame.mixer.get_init():
        return

    if curSound:
        curSound.stop()
    sampleRate=44100
    t = np.linspace(0, duration, int(sampleRate * duration), False)
    if shape == "sine":
        wave = np.sin(2 * np.pi * frequency * t)
    wave = (wave * volume * 32767).astype(np.int16)
    silence=np.zeros(int(sampleRate * pause), dtype=np.int16)
    wave=np.concatenate([wave, silence])
    cSound = pygame.mixer.Sound(wave)
    cSound.play(loops=loops)
initAudio()

def soundStop():
    global curSound
    pygame.mixer.stop()
    curSound=None

def flashLight(board, colour, speed=0.2):
    global flashThread, flashStop
    flashStop.set()
    if transitionThread and transitionThread.is_alive():
        transitionThread.join()
    flashStop.clear()
    flashStop.set()
    if flashThread and flashThread.is_alive():
        flashThread.join()
    flashStop.clear()
    def flash():
        while not flashStop.is_set():
            board.set_rgb(*colour)
            time.sleep(speed)
            board.set_rgb(0,0,0)
            time.sleep(speed)

    flashThread = threading.Thread(target=flash, daemon=True)
    flashThread.start()

#stop flashing colour
def flashStopG(board, colour):
    global flashThread, transitionThread, flashStop, transitionStop
    transitionStop.set()
    if transitionThread and transitionThread.is_alive():
        transitionThread.join()
    transitionStop.clear()
    flashStop.set()
    if flashThread and flashThread.is_alive():
        flashThread.join()
    
    
    #change from hot to cool range, smooth transition between red and green
    def transition():
        board.set_rgb(255, 0, 0)
        if transitionStop.wait(timeout=0.5):
            return
        if not transitionStop.is_set():
            board.set_rgb_fade(*colour, duration_ms=2000)
    
    transitionThread = threading.Thread(target=transition, daemon=True)
    transitionThread.start()

def updateLight(cpu):
    global currentColour, flashing
    if cpu is None:
        colour = (0,0,255)
        soundStop()
    elif cpu <= 60: 
        colour = (0,255,0) #less than 60 light turns green
        soundStop()
    else:
        colour = (255,0,0) #bigger than 60 light turns red
    colourChange= cpu is not None and cpu >= 80
    if colour != currentColour or colourChange != flashing:
        currentColour = colour
        flashing = colourChange
        if colourChange: #flash red if above 80
            flashLight(board, colour)
            sound()
        else:
            flashStopG(board, colour)
            soundStop()

#draw the text once as it dosen't change
def backgroundDisplay(board,):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    image = Image.new('RGB', (board.LCD_HEIGHT, board.LCD_WIDTH), (11, 16, 24))
    draw = ImageDraw.Draw(image)
    
    draw.text((55, 5),  "Temperatures",   font=font, fill=(150, 205, 255))
    draw.text((10, 20),  "-----------------------------",   font=font, fill=(150, 205, 255))
    draw.text((10, 40),  "CPU:",   font=font, fill=(150, 205, 255))
    draw.text((10, 110),  "SSD:",   font=font, fill=(150, 205, 255))
    draw.text((10, 180), "Board:", font=font, fill=(150, 205, 255))

    image = image.rotate(-90, expand=True)
    board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, _rgb565_bytes(image))

def updateDisplay(board,cpu, ssd, temp_board):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    updates = [(f"{cpu}°C",155,40),(f"{ssd}°C",155,110),(f"{temp_board}°C",155,180),]

    for text, x, y in updates:
        patch_w, patch_h = 120, 30
        patch = Image.new('RGB', (patch_w, patch_h), (11, 16, 24))
        draw = ImageDraw.Draw(patch)
        draw.text((0, 0), text, font=font, fill=(200, 50, 50))

        # Rotate patch and map coordinates
        patch = patch.rotate(-90, expand=True)
        # After 90° rotation, x→y and y→(LCD_WIDTH-x-patch_h)
        board.draw_image(board.LCD_WIDTH - y - patch_h,x,patch.width,patch.height,_rgb565_bytes(patch))
    
    updateLight(cpu)