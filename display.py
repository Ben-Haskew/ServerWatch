import sys
sys.path.append('/home/ben/Whisplay/runtime')

from whisplay import WhisplayBoard
from PIL import Image, ImageDraw, ImageFont

board = WhisplayBoard()
board.set_backlight(70)

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

def backgroundDisplay(board,):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    image = Image.new('RGB', (board.LCD_HEIGHT, board.LCD_WIDTH), (11, 16, 24))
    draw = ImageDraw.Draw(image)

    draw.text((10, 20),  "Temp CPU:",   font=font, fill=(150, 205, 255))
    draw.text((10, 90),  "Temp SSD:",   font=font, fill=(150, 205, 255))
    draw.text((10, 160), "Temp Board:", font=font, fill=(150, 205, 255))

    image = image.rotate(-90, expand=True)
    board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, _rgb565_bytes(image))

def updateDisplay(board,cpu, ssd, temp_board):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    updates = [(f"{cpu}°C",155,20),(f"{ssd}°C",155,90),(f"{temp_board}°C",155,160),]

    for text, x, y in updates:
        patch_w, patch_h = 120, 30
        patch = Image.new('RGB', (patch_w, patch_h), (11, 16, 24))
        draw = ImageDraw.Draw(patch)
        draw.text((0, 0), text, font=font, fill=(200, 50, 50))

        # Rotate patch and map coordinates
        patch = patch.rotate(-90, expand=True)
        # After 90° rotation, x→y and y→(LCD_WIDTH-x-patch_h)
        board.draw_image(board.LCD_WIDTH - y - patch_h,x,patch.width,patch.height,_rgb565_bytes(patch))