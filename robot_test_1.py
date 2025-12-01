from machine import Pin, PWM
import time
from neopixel import NeoPixel as np
import utime


### MOTOR PIN ASSIGNMENTS ###

# Motor A pins
ENA = PWM(Pin(21))
ENA.freq(1000)
IN1 = Pin(20, Pin.OUT)
IN2 = Pin(19, Pin.OUT)

# Motor B pins
IN3 = Pin(18, Pin.OUT)
IN4 = Pin(17, Pin.OUT)
ENB = PWM(Pin(16))
ENB.freq(1000)


### ULTRASONIC PIN ASSIGNMENTS ###

trigger_center = Pin(0, Pin.OUT)
echo_center = Pin(1, Pin.IN)

trigger_right = Pin(2, Pin.OUT)
echo_right = Pin(3, Pin.IN)


### LED STRIP PIN & COLOR ASSIGNMENTS ###

light_strip_1 = np(Pin(5), 8)
light_strip_2 = np(Pin(28), 8)

color1 = (255, 0, 0)
color2 = (0, 15, 150)
color_swap = False


### START BUTTON PIN ASSIGNMENT ###

start_button = Pin(26, Pin.IN, Pin.PULL_UP)



### DRIVING FUNCTIONS ###

# Spin left and right motors at a speed percentage
# modL and modR (0 <= x <= 1)
def drive(modL,modR):
    IN3.high()#Left Motor
    IN4.low()
    ENB.duty_u16(int(modL * 1.0 * 65535 / 1.5))
    
    IN1.high()#Right Motor
    IN2.low()
    ENA.duty_u16(int(modR * 0.975 * 65535 / 1.5))

# Stop both motors
def stop_motors():
    ENA.duty_u16(0)
    ENB.duty_u16(0)

# Keep robot at a set distance from a wall on the right side   
def midStay(USS_side, start_dist): #takes in the distance from the wall in cm
    """ built for if the side sensor is on the right side of the robot"""
    
    # if pos, then drifting left (away from wall)
    # if neg then drifting right (toward wall)
    dist_from_orig = USS_side - start_dist
    print("dist_from_orig: ", dist_from_orig)
    
    if dist_from_orig >= -1.25 and dist_from_orig <= 1.25:
        print("staying center")
        drive(1, 1)
        
    elif dist_from_orig < -1.25: #drifting right
        rel_right_pow = (1 / (dist_from_orig - 11.25 - 5/6)) + 0.575
        rel_left_pow = 1 - rel_right_pow
        
        abs_right_pow = rel_right_pow / max(rel_right_pow, rel_left_pow)
        abs_left_pow = rel_left_pow / max(rel_right_pow, rel_left_pow)
        
        print("drifting right -- correcting")
        print("abs left pow: ", abs_left_pow, " -- abs right pow: ", abs_right_pow)
        drive(abs_left_pow, abs_right_pow)
        
    elif dist_from_orig > 1.25: #drifting left
        rel_left_pow = (1 / -(dist_from_orig + 11.25 + 5/6)) + 0.575
        rel_right_pow = 1 - rel_left_pow
        
        abs_right_pow = rel_right_pow / max(rel_right_pow, rel_left_pow)
        abs_left_pow = rel_left_pow / max(rel_right_pow, rel_left_pow)
        
        print("drifting left -- correcting")
        print("abs right pow: ", abs_right_pow, " -- abs left pow: ", abs_left_pow)
        drive(abs_left_pow, abs_right_pow)
    
    else:
        print("Error: dist_from_orig not in range")
        exit()



### SENSOR INPUT FUNCTIONS ###
        
# Read ultrasonic sensor
def ultra(trigger, echo): #inputs are the GPIO pins
        
    avgDist = [] #avg list to hold values so that it runs three times
    print("cp0-1")
    for i in range(5): #runs 5 times so that one value is not way crazy
        trigger.low()
        utime.sleep_us(2)
        trigger.high()
        utime.sleep_us(5) 
        trigger.low()
        
        print("cp0-1-1")
        
        signaloff = 0  # Initialize
        signalon = 0   # Initialize
        while echo.value() == 0:
            signaloff = utime.ticks_us()
        
        while echo.value() == 1:
            signalon = utime.ticks_us()
        
        print("cp0-1-2")
        
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        avgDist.append(distance)
        time.sleep(0.1)
    print("cp0-2")
        
    avgDist.remove(max(avgDist)) #removes highest and lowest
    avgDist.remove(min(avgDist)) #removes highest and lowest
    return (sum(avgDist) / len(avgDist)) #returns an average of the remaining three


### MAIN PROGRAM ###

stop_motors()

def run_program():
    
    color_swap = False
    
    time.sleep(2)

    print("Waiting for start button...")
    while start_button.value() == 1:
        time.sleep(0.05)
    print("Button pressed. Starting robot!")
    
    time.sleep(0.5)

    startTime = utime.time()
    print("cp0")
    start_dist = ultra(trigger_right, echo_right)
    print("cp0.5")

    time.sleep(0.1)

    while True:#utime.time() - startTime < 100:
        
        us = ultra(trigger_right, echo_right)
        
        midStay(us, start_dist)

        for i in range(8): #8 Light locations to light
            if not color_swap: #sets the color for each location controlled by color_swap = not color_swap
                light_strip_1[i] = color1 #colors in 1 are color 1
                light_strip_2[i] = color2 #colors in 2 are color 2
            else:
                light_strip_1[i] = color2 #colors swap so 1 is 2
                light_strip_2[i] = color1 #and 2 is 1
            color_swap = not color_swap #boolean gets flipped to alternate colors
        
        color_swap = not color_swap #displaced by one so that it shifts over to loop
        light_strip_1.write()
        light_strip_2.write()
        
        if start_button.value() != 1:
            stop_motors()
            run_program()
            break
        
        time.sleep(0.1)

run_program()

# stops the robot driving
stop_motors()