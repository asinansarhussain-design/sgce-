import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 1)   # bus 0, CE1 = touch
spi.max_speed_hz = 1000

def read_channel(cmd):
    r = spi
