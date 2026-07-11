import time
import spidev
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.ili9341 as ili9341

# ---------------- DISPLAY ----------------
spi_disp = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
rst_pin = digitalio.DigitalInOut(board.D25)

display = ili9341.ILI9341(
    spi_disp,
    cs=cs_pin,
    dc=dc_pin,
    rst=rst_pin,
    baudrate=24000000
)

W = display.width
H = display.height
font = ImageFont.load_default()

# ---------------- TOUCH ----------------
spi_touch = spidev.SpiDev()
spi_touch.open(0,1)      # bus0 CE1
spi_touch.max_speed_hz = 1000000

def read_touch(cmd):
    r = spi_touch.xfer2([cmd,0,0])
    val = ((r[1] << 8) | r[2]) >> 3
    return val

def get_xy():
    x = read_touch(0xD0)   # X
    y = read_touch(0x90)   # Y
    if x < 100 or y < 100:
        return None,None
    return x,y

# ------------ calibration raw values -----
XMIN = 200
XMAX = 3900
YMIN = 200
YMAX = 3900

def map_value(v, in_min, in_max, out_min, out_max):
    return int((v-in_min)*(out_max-out_min)/(in_max-in_min)+out_min)

status = "IDLE"
temp = 25.0
cycle = 1

while True:

    # ---------- Draw UI ----------
    img = Image.new("RGB",(W,H),"black")
    draw = ImageDraw.Draw(img)

    draw.rectangle((0,0,W,30), fill=(0,80,180))
    draw.text((10,10),"PORTABLE PCR SYSTEM",fill="white",font=font)

    draw.text((20,60),f"Temp: {temp:.1f} C",fill="yellow",font=font)
    draw.text((20,90),f"Cycle: {cycle}/40",fill="cyan",font=font)
    draw.text((20,120),f"Status: {status}",fill="green",font=font)

    # START button
    draw.rectangle((20,180,110,220), fill=(0,140,0))
    draw.text((45,195),"START",fill="white",font=font)

    # STOP button
    draw.rectangle((140,180,230,220), fill=(180,0,0))
    draw.text((170,195),"STOP",fill="white",font=font)

    display.image(img)

    # -------- Read Touch --------
    rx, ry = get_xy()

    if rx is not None:
        sx = map_value(rx, XMIN, XMAX, 0, W)
        sy = map_value(ry, YMIN, YMAX, 0, H)

        print("Touch:", sx, sy)

        # START button
        if 20 <= sx <= 110 and 180 <= sy <= 220:
            status = "RUNNING"
            print("START pressed")

        # STOP button
        if 140 <= sx <= 230 and 180 <= sy <= 220:
            status = "STOPPED"
            print("STOP pressed")

        time.sleep(0.3)

    if status == "RUNNING":
        temp += 1
        if temp > 95:
            temp = 60
            cycle += 1
            if cycle > 40:
                cycle = 1

    time.sleep(0.1)
