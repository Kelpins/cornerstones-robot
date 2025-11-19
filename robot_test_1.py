from machine import Pin, PWM
from time import sleep
from neopixel import NeoPixel as np


# Motor A pins
ENA = PWM(Pin(2))
IN1 = Pin(3, Pin.OUT)
IN2 = Pin(4, Pin.OUT)

# Motor B pins
IN3 = Pin(5, Pin.OUT)
IN4 = Pin(6, Pin.OUT)
ENB = PWM(Pin(7))

ENA.freq(1000)
ENB.freq(1000)

def stop():
    ENA.duty_u16(0)
    ENB.duty_u16(0)

def drive_straight():
    IN1.high()
    IN2.low()
    ENA.duty_u16(int(0.975 * 65535))
    
    IN3.high()
    IN4.low()
    ENB.duty_u16(int(1.0 * 65535))

def spin_right_motor(speed):
    if speed >= 0:
        IN1.high()
        IN2.low()
        ENA.duty_u16(int(speed * 65535))
    else:
        IN1.low()
        IN2.high()
        ENA.duty_u16(int(-speed * 65535))

def spin_left_motor(speed):
    if speed >= 0:
        IN3.high()
        IN4.low()
        ENB.duty_u16(int(speed * 65535))
    else:
        IN3.low()
        IN4.high()
        ENB.duty_u16(int(-speed * 65535))


light_strip_1 = np(Pin(0), 8)
light_strip_2 = np(Pin(15), 8)

color1 = (255, 0, 0)
color2 = (0, 15, 150)
color_swap = False

start_button = Pin(27, Pin.IN)
while True:
    print("Waiting for start button...")
    while start_button.value() == 0:
        sleep(0.05)
        print(start_button.value())
    print("Button pressed. Starting robot!")

    drive_straight()
    sleep(3.85)
    stop()

while True:

    for i in range(8):
        if not color_swap:
            light_strip_1[i] = color1
            light_strip_2[i] = color2
        else:
            light_strip_1[i] = color2
            light_strip_2[i] = color1
        color_swap = not color_swap
    
    color_swap = not color_swap
    light_strip_1.write()
    light_strip_2.write()
    
    sleep(0.5)