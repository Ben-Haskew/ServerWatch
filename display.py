import sys
sys.path.append('/home/ben/Whisplay/runtime')
import threading
import time
import numpy as np
from whisplay import WhisplayBoard
from PIL import Image, ImageDraw, ImageFont
import pygame
import subprocess
import time

board = WhisplayBoard()
board.set_backlight(15)
currentColour = None
flashThread = None
flashStop = threading.Event()
transitionThread = None
transitionStop = threading.Event()
flashing=False
curSound=None
drawLock = threading.Lock()

#DONT TOUCH#
#function to convert PIL image into RGB
def _rgb565_bytes(image: Image.Image) -> bytes:
    rgb = np.array(image.convert("RGB"), dtype=np.uint16)
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return rgb565.astype(np.uint16).byteswap().tobytes()
#sound
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
#light
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
def ledOff(board):
    global flashStop, transitionStop
    try:
        flashStop.set()          # use `flashStop = True` if it's a plain bool
        transitionStop.set()     # same here
    except Exception:
        pass
    for t in (flashThread, transitionThread):
        if t and t.is_alive():
            t.join(timeout=0.5)  # timeout, so a stuck thread can't hang shutdown
    try:
        board.set_rgb(0, 0, 0)
    except Exception:
        pass
def level(value, warn, crit):
    """0 = ok, 1 = warning, 2 = critical, None = no data"""
    if value is None:
        return None
    if value >= crit:
        return 2
    if value > warn:
        return 1
    return 0
def updateLight(cpuTemp, cpuUse, memUse):
    global currentColour, flashing
    levels = [
        level(cpuTemp, 60, 80),   # °C
        level(cpuUse,  60, 80),   # %
        level(memUse,  85, 95),   # % (see note below)
    ]
    known = [l for l in levels if l is not None]
    worst = max(known) if known else None
    
    if worst is None:
        colour = (0, 0, 255)      # no data: blue
    elif worst == 0:
        colour = (0, 255, 0)      # all fine: green
    else:
        colour = (255, 0, 0)      # something above warn: red
    colourChange = worst == 2     # something critical: flash

    if colour != currentColour or colourChange != flashing:
        currentColour = colour
        flashing = colourChange
        if colourChange: #flash red if above 80
            flashLight(board, colour)
            sound()
        else:
            flashStopG(board, colour)
            soundStop()
noDataColour= (255, 0, 165)
def noDataLight(colour=noDataColour):
    global currentColour, flashing
    if colour != currentColour or flashing:
        currentColour = colour
        flashing = False
        flashStopG(board, colour)    # stops any flashing and fades to the colour
        soundStop()
#screen
#draw the text once as it dosen't change
def noDataDisplay():
    image = Image.open("/home/ben/ServerWatch/NODATASPLASH.png").convert("RGB")   # 280x240
    image = image.rotate(-90, expand=True)
    with drawLock:
        board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, _rgb565_bytes(image))
    noDataLight()
def startDisplay():
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    image = Image.new('RGB', (board.LCD_HEIGHT, board.LCD_WIDTH), (11, 16, 24))
    image = Image.open("/home/ben/ServerWatch/serverwatchsplash.png").convert("RGB")
    image = image.rotate(-90, expand=True)
    board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, _rgb565_bytes(image))
def backgroundDisplay(board,):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    image = Image.new('RGB', (board.LCD_HEIGHT, board.LCD_WIDTH), (11, 16, 24))
    draw = ImageDraw.Draw(image)
    
    draw.text((85, 5),  "Overview",   font=font, fill=(165, 205, 255))
    draw.text((10, 20),  "-----------------------------",   font=font, fill=(150, 205, 255))
    draw.text((10, 40),  "CPU:",   font=font, fill=(150, 205, 255))
    draw.text((10, 70),  "MEM:",   font=font, fill=(150, 205, 255))
    draw.text((10, 100),  "HDD:",   font=font, fill=(150, 205, 255))
    draw.text((10, 135),  "MC Online:",   font=font, fill=(150, 205, 255))
    # draw.text((10, 110),  "HDD:",   font=font, fill=(150, 205, 255))
    # draw.text((10, 180), "Board:", font=font, fill=(150, 205, 255))

    image = image.rotate(-90, expand=True)
    board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, _rgb565_bytes(image))
def fmt(value, suffix):
    return f"{value:.0f}{suffix}" if isinstance(value, (int, float)) else f"--{suffix}"
def updateDisplay(cpuTemp, ssdTemp, cpuUse, memUse, players=None):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    count = players['count'] if players else None
    updates = [
        (fmt(cpuTemp, "°C"), 85, 40),
 	(fmt(cpuUse, "%"), 160, 40),
 	(fmt(ssdTemp, "°C"), 85, 100),
	(fmt(memUse, "%"), 160, 70),
	(str(count) if count is not None else "--", 160, 135),
    ]
    for text, x, y in updates:
        patch_w, patch_h = 120, 30
        patch = Image.new('RGB', (patch_w, patch_h), (11, 16, 24))
        draw = ImageDraw.Draw(patch)
        draw.text((0, 0), text, font=font, fill=(200, 50, 50))

        # Rotate patch and map coordinates
        patch = patch.rotate(-90, expand=True)
        # After 90° rotation, x→y and y→(LCD_WIDTH-x-patch_h)
        board.draw_image(board.LCD_WIDTH - y - patch_h,x,patch.width,patch.height,_rgb565_bytes(patch))
    
    updateLight(cpuTemp, cpuUse, memUse)
