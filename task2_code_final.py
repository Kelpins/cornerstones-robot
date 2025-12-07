from machine import Pin, PWM
import time
from neopixel import NeoPixel as np
import utime


### CONSTANTS FOR THE DRIVE ALGORITHM ###
turnTime = 0.385 # a 90 degree turn takes the robot 0.385 seconds


### CP (checkpoint) LIGHT PIN ASSIGNMENTS ###
CPLED1 = Pin(8, Pin.OUT)
CPLED2 = Pin(9, Pin.OUT)


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

trigger_center = Pin(10, Pin.OUT)
echo_center = Pin(11, Pin.IN)

trigger_left = Pin(15, Pin.OUT)
echo_left = Pin(14, Pin.IN)

trigger_right = Pin(6,Pin.OUT)
echo_right = Pin(7,Pin.IN)


### START BUTTON PIN ASSIGNMENT ###

start_button = Pin(13, Pin.IN, Pin.PULL_UP)


### DRIVING FUNCTIONS ###

# Spin left and right motors at a speed percentage
# modL and modR (0 <= x <= 1)
def drive(modL,modR):
    
    # duty_u16 can't take a negative number, so we reverse the pin states instead
    if (modL < 0):
        IN3.low()
        IN4.high()
        ENB.duty_u16(int(-modL * 1.0 * 65535 / 1.625)) # left motor reverse case
    else:
        IN3.high()
        IN4.low()
        ENB.duty_u16(int(modL * 1.0 * 65535 / 1.625)) # left motor forward case
    
    if (modR < 0):
        IN1.low()
        IN2.high()
        ENA.duty_u16(int(-modR * 1.0 * 65535 / 1.625)) # right motor reverse case
    else:
        IN1.high()
        IN2.low()
        ENA.duty_u16(int(modR * 1.0 * 65535 / 1.625)) # right motor forward case

# Stop both motors
def stop_motors():
    ENA.duty_u16(0)
    ENB.duty_u16(0)
    
# Spins in place
def Turn(isDirectionRight): #True is right turn, False is left turn
    if isDirectionRight: #right turn
        # set both checkpoint LEDs to OFF to signify a turn
        CPLED1.off()
        CPLED2.off()
        # left wheel forward 0.75 speed, right motor reverse 0.75 speed to spin in place
        drive(0.75,-0.75)
        time.sleep(turnTime) # waits for the duration of turn time
        stop_motors() # stops the spin
        return
    else: #left turn
        # set both checkpoint LEDs to OFF to signify a turn
        CPLED1.off()
        CPLED2.off()
        # left wheel reverse 0.75 speed, right motor forward 0.75 speed to spin in place
        drive(-0.75,0.75) #left turn
        time.sleep(turnTime) # waits for the duration of turn time
        stop_motors() # stops the spin
        return


### MAIN PROGRAM ###

def run_program():
        
    time.sleep(2)
    
    # robot waits until start button is pressed
    while start_button.value() == 1:
        time.sleep(0.05)
    
    # time for hand to escape
    time.sleep(0.5)
    
    # drive forward full speed down first corridor
    drive(1, 1)
    
    # continue driving for 2 seconds
    time.sleep(2)
    
    # stop driving
    stop_motors()
    
    # wait 0.5 seconds for robot to come to a full stop
    time.sleep(0.5)
    
    # turn left 90 degrees to face down second corridor
    Turn(False)
    
    # wait 0.5 seconds for robot to come to a full stop
    time.sleep(0.5)
    
    # drive forward full speed down second corridor
    drive(1, 1)
    
    # continue driving for 1.5 seconds
    time.sleep(1.5)
    
    # stop driving
    stop_motors()
    
    # wait 0.5 seconds for robot to come to a full stop
    time.sleep(0.5)
    
    # turn right 90 degrees to face down final corridor
    Turn(True)
    
    # wait 0.5 seconds for robot to come to a full stop
    time.sleep(0.5)
    
    # drive forward full speed down final corridor
    drive(1, 1)
    
    # continue driving for 1.775 seconds to end in park zone
    time.sleep(1.775)
    
    # stop driving
    stop_motors()

# executes the program
run_program()