import sys
sys.path.append('/home/Whisplay/runtime')

from whisplay import WhisPlayBoard
from PIL import Image, ImageDraw, ImageFont

board = WhisPlayBoard()
board.init()

LCD_W = 280
LCD_H = 240

def displayScreen(board, cpu, ssd, temp_board):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    image = Image.new('RGB', (LCD_W, LCD_H), (255, 255, 255))  # white background
    draw = ImageDraw.Draw(image)

    # Labels
    draw.text((10, 20),  "Temp CPU:",   font=font, fill=(0, 0, 0))
    draw.text((10, 80),  "Temp SSD:",   font=font, fill=(0, 0, 0))
    draw.text((10, 140), "Temp Board:", font=font, fill=(0, 0, 0))

    # Values
    draw.text((10, 48),  f"{cpu}°C",        font=font, fill=(200, 50, 50))
    draw.text((10, 108), f"{ssd}°C",        font=font, fill=(200, 50, 50))
    draw.text((10, 168), f"{temp_board}°C", font=font, fill=(200, 50, 50))

    board.display_image(image)