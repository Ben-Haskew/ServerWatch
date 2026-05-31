import sys
sys.path.append('/home/ben/Whisplay/runtime')

from whisplay_client import create_whisplay_hardware
from PIL import Image, ImageDraw, ImageFont

board = create_whisplay_hardware(
    app_id="serverwatch",
    display_name="ServerWatch",
    icon="S",
)
board.set_backlight(70)

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

def displayScreen(board, cpu, ssd, temp_board):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    image = Image.new('RGB', (board.LCD_WIDTH, board.LCD_HEIGHT), (11, 16, 24))
    draw = ImageDraw.Draw(image)

    draw.text((10, 20),  "Temp CPU:",   font=font, fill=(150, 205, 255))
    draw.text((10, 80),  "Temp SSD:",   font=font, fill=(150, 205, 255))
    draw.text((10, 140), "Temp Board:", font=font, fill=(150, 205, 255))

    draw.text((10, 48),  f"{cpu}°C",        font=font, fill=(200, 50, 50))
    draw.text((10, 108), f"{ssd}°C",        font=font, fill=(200, 50, 50))
    draw.text((10, 168), f"{temp_board}°C", font=font, fill=(200, 50, 50))

    board.draw_image(0, 0, board.LCD_WIDTH, board.LCD_HEIGHT, _rgb565_bytes(image))
