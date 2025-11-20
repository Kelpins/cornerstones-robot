from machine import Pin, PWM
import time
from neopixel import NeoPixel as np
import utime

"""
Wiring Notes

UsSR Echo: GP3
UsSR Trig: GP2

UsSL Echo: GP27
UsSL Trig: GP26

UsSF Echo: GP1
UsSF Trig: GP0

"""

# Motor A pins
ENA = PWM(Pin(16))
IN1 = Pin(17, Pin.OUT)
IN2 = Pin(18, Pin.OUT)

# Motor B pins
IN3 = Pin(19, Pin.OUT)
IN4 = Pin(20, Pin.OUT)
ENB = PWM(Pin(21))

#trigger_left = Pin(26, Pin.OUT)
#echo_left = Pin(27, Pin.OUT)

trigger_center = Pin(0, Pin.OUT)
echo_center = Pin(1, Pin.OUT)

trigger_right = Pin(2, Pin.OUT)
echo_right = Pin(3, Pin.OUT)

ENA.freq(1000)
ENB.freq(1000)

def stop():
    ENA.duty_u16(0)
    ENB.duty_u16(0)

def drive_straight(modR,modL):
    IN1.high()#Right Motor
    IN2.low()
    ENA.duty_u16(int(modR*0.975 * 65535))
    
    IN3.high()#Left Motor
    IN4.low()
    ENB.duty_u16(int(modL*1.0 * 65535))

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

def stayMiddle(USL, USR): #function to keep the robot between two walls, inputs two values
    if USL > USR: #if the robot is further from the left wall than the right wall, left motor needs to be powered less
        if USL-USR > 0: #if the difference is minimal it doesn't change power values
            return((1-(USL-USR)), 1) #returns a lower power level for the left wheel so that the bot turns left
    else: #right is further than left, turn right
        if USR-USL > 0: #checks that the difference is greatish
            return(1, (1-(USR-USL))) #returns a lower power level for right
        
def midStay(USS_Side): #takes in the distance from the wall in cm
    """ built for if the side sensor is on the right side of the robot"""
    modify = 1 #controls how much the slower wheel needs to slow down
    modify_mod = 1 #change the factor that it modifies the modify variable
    if USS_Side > 8: #wall is further from the robot than 8cm
        modify = (8/(USS_Side)) #As USS Side increases past 8, the motor slows down
        drive_straight(modify,1) #right motor needs to be slowed down
        return()
    if USS_Side < 7: #changes only if it's closer than 7
        modify = ((USS_Side)/7) #as USS Side decreases past 7, the motor slows down more and more
        drive_straight(1,modify) #drives straight and power values 1 on right and slower modified on left
        return()

"""
def readUltrasonics():

    trigger_left.low()
    utime.sleep_us(2)
    trigger_left.high()
    utime.sleep_us(5)
    trigger_left.low()

    while echo_left.value() == 0:
        signaloff = utime.ticks_us()
    while echo_left.value() == 1:
        signalon = utime.ticks_us()
    timepassed = signalon - signaloff

    sensor_left = timepassed * 0.0343 / 2
    
    trigger_center.low()
    utime.sleep_us(2)
    trigger_center.high()
    utime.sleep_us(5)
    trigger_center.low()

    while echo_center.value() == 0:
        signaloff = utime.ticks_us()
    while echo_center.value() == 1:
        signalon = utime.ticks_us()
    timepassed = signalon - signaloff

    sensor_center = timepassed * 0.0343 / 2
    
    trigger_right.low()
    utime.sleep_us(2)
    trigger_right.high()
    utime.sleep_us(5)
    trigger_right.low()

    while echo_right.value() == 0:
        signaloff = utime.ticks_us()
    while echo_right.value() == 1:
        signalon = utime.ticks_us()
    timepassed = signalon - signaloff

    sensor_right = timepassed * 0.0343 / 2
    
    return [sensor_left, sensor_center, sensor_right]
"""

def ultra(trigger, echo): #inputs are the GPIO pins
    avgDist = [] #avg list to hold values so that it runs three times
    for i in range(5): #runs 5 times so that one value is not way crazy
        trigger.low()
        utime.sleep_us(2)
        trigger.high()
        utime.sleep_us(5) 
        trigger.low()
        
        signaloff = 0  # Initialize
        signalon = 0   # Initialize
        while echo.value() == 0:
            signaloff = utime.ticks_us()
        
        while echo.value() == 1:
            signalon = utime.ticks_us()
        
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        avgDist.append(distance)
        utime.sleep_us(10)
        
    avgDist.remove(max(avgDist)) #removes highest and lowest
    avgDist.remove(min(avgDist)) #removes highest and lowest
    return (sum(avgDist) / len(avgDist)) #returns an average of the remaining three

"""    
while True:
    print(ultra(trigger_right,echo_right))
    #print("us1: ", us[0], " -- us2: ", us[1], " -- us3: ", us[2])
    sleep(0.5)
"""

light_strip_1 = np(Pin(5), 8)
light_strip_2 = np(Pin(28), 8)

color1 = (255, 0, 0)
color2 = (0, 15, 150)
color_swap = False

start_button = Pin(22, Pin.IN)



while True:
    print("Waiting for start button...")
    while start_button.value() == 0:
        time.sleep(0.05)
        print(start_button.value())
    print("Button pressed. Starting robot!")
    
    startTime = utime.time()
    
    while utime.time() - startTime < 10:
        """THIS IS THE NUMBER (10) THAT CONTROLS THE AMOUNT OF TIME IT RUNS"""  
        midStay(ultra(trigger_right, echo_right))
        utime.sleep_us(50000)
    
    stop()

while True: #color LED Control

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
    
    sleep(0.5) #waits 5 seconds before switching
