from machine import Pin, PWM
import time
from neopixel import NeoPixel as np
import utime
import math


WOPR = PWM(Pin(22))
WOPR.freq(1000)


i = 0
while True:
    duty = 32768 * math.sin(3.14159 * i / 10000) * math.cos(3.14159 * i / 1000) + 32768
    WOPR.duty_u16(int(duty))
    
    i+=1
    if (i == 20000):
        i = 0
    utime.sleep_us(50)