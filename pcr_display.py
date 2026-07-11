import time
import board
import digitalio
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

# SPI
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Pins
cs_pin = digitalio.DigitalInOut(board.CE0)   # GPIO8
dc_pin = digitalio.DigitalInOut(board.D24)   # GPIO24
rst_pin = digitalio.DigitalInOut(board.D25)  # GPIO25

# Display init
display = ili9341.ILI9341(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=rst_pin,
    baudrate=9600
)

width = display.width
height = display.height

font = ImageFont.load_default()

temp = 25
cycle = 1

while True:
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, width, 30), fill=(0, 0, 180))
    draw.text((10, 10), "PCR MACHINE", fill="white", font=font)

    draw.text((20, 60), f"Temp : {temp} C", fill="yellow", font=font)
    draw.text((20, 90), f"Cycle: {cycle}/40", fill="cyan", font=font)
    draw.text((20, 120), "Status: RUNNING", fill="green", font=font)

    draw.rectangle((20, 200, 120, 235), fill=(0, 120, 0))
    draw.text((45, 212), "START", fill="white", font=font)

    draw.rectangle((180, 200, 280, 235), fill=(180, 0, 0))
    draw.text((215, 212), "STOP", fill="white", font=font)

    display.image(image)

    temp += 2
    if temp > 95:
        temp = 60
        cycle += 1
        if cycle > 40:
            cycle = 1

    time.sleep(1)
