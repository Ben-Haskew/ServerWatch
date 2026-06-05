import sys
sys.path.append('/home/ben/Whisplay/runtime')
import threading
import time
from whisplay import WhisplayBoard
from PIL import Image, ImageDraw, ImageFont

board = WhisplayBoard()
board.set_backlight(70)
currentColour = None
flashThread = None
flashStop = threading.Event()
flashing=False

#DONT TOUCH#
#function to convert PIL image into RGB
def _rgb565_bytes(image: Image.Image) -> bytes:
    rgb = image.convert("RGB")
    output = bytearray()
    for y in range(rgb.height):
        for x in range(rgb.width):
            r, g, b = rgb.getpixel((x, y))
            value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            output.append((value >> 8) & 0xFF)
            output.append(value & 0xFF)
    return bytes(output)

def flashLight(board, colour, speed=0.2):
    global flashThread, flashStop
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
    flashStop.set()
    if flashThread and flashThread.is_alive():
        flashThread.join()
    
    #change from hot to cool range, smooth transition between red and green
    def transition():
        board.set_rgb(255,0,0)
        time.sleep(0.5)
        board.set_rgb_fade(*colour,duration_ms=2000)
    # board.set_rgb(*colour) #one colour after stopping
    threading.Thread(target=transition, daemon=True).start()

def updateLight(cpu):
    global currentColour, flashing
    if cpu is None:
        colour = (0,0,255)
    elif cpu <= 60: 
        colour = (0,255,0) #less than 60 light turns green
    else:
        colour = (255,0,0) #bigger than 60 light turns red
    colourChange= cpu is not None and cpu >= 80
    if colour != currentColour or colourChange != flashing:
        currentColour = colour
        flashing = colourChange
        if colourChange: #flash red if above 80
            flashLight(board, colour) 
        else:
            flashStopG(board, colour)

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