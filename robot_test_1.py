from machine import Pin, PWM
import time
from neopixel import NeoPixel as np
import utime
### LIMITS FOR THE DRIVE ALGORITHM ###
sideLimit = 20 # robot uses readings within 25 cm from side wall
frontLimit = 7 # robot stops before reaching 7cm from front wall
frontStopLimit = 75 # 75 cm signifies that robot has reached the end of the maze
goStraightTime = 0.5 # robot goes forward for 0.5 seconds after turning so side sensors register the walls
turnTime = 0.385 # a 90 degree turn takes the robot 0.385 seconds
restTime = 0.2 # each iteration of the algorithm drives for 0.2 seconds before taking new sensor inputs
centerMargin = 2.0 # number of centimeters of robot drift allowed for no changes
runtime = 900 # number of seconds the program runs for
holdNeeded = False # True if robot senses a corridor to one side; holds robot to the other wall
holdDistance = 0 # the distance being held
holdSide = False # True if robot needs to hold to right wall, False is left


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


### LED STRIP PIN & COLOR ASSIGNMENTS ###
light_strip_1 = np(Pin(12), 8)
light_strip_2 = np(Pin(1), 8)
color1 = (255, 0, 0) # color 1: red
color2 = (0, 15, 150) # color 2: blue
# color_swap determines which colors should be shown on the light bars, and swaps every iteration
color_swap = False


### START BUTTON PIN ASSIGNMENT ###
start_button = Pin(13, Pin.IN, Pin.PULL_UP)


### DRIVING FUNCTIONS ###
# Spin left and right motors at a speed percentage
# Each motor is kept to a minimum input of 22500 so the algorithm never outputs a vlue too low to move the motor
# modL and modR (0 <= x <= 1)
def drive(modL,modR):

    # duty_u16 can't take a negative number, so we reverse the pin states instead
    if (modL < 0):
        IN3.low()
        IN4.high()
        ENB.duty_u16(max(int(-modL * 1.0 * 65535 / 1.575), 22500)) # left motor reverse case
    else:
        IN3.high()
        IN4.low()
        ENB.duty_u16(max(int(modL * 1.0 * 65535 / 1.575), 22500)) # left motor forward case
        
    if (modR < 0):
        IN1.low()
        IN2.high()
        ENA.duty_u16(int(0.8375 * max(int(-modR * 65535 / 1.575), 22500))) # right motor reverse case
    else:
        IN1.high()
        IN2.low()
        ENA.duty_u16(int(0.8375 * max(int(modR * 65535 / 1.575), 22500))) # right motor forward case
    print("DRIVE FUNCTION COMPLETE")
    
# Stop both motors
def stop_motors():
    ENA.duty_u16(0)
    ENB.duty_u16(0)
    print("STOP_MOTORS COMPLETE")
    
# Keep robot in the middle of the two walls   
def midStay(USLeft, USRight, USCenter): #takes in the distance from the wall in cm
    rPower = 0 #initialize R power
    lPower = 0 #init L Power
    print("midstay pre if")
    if (not holdNeeded): #toggle not selected
        print("not holdNeeded")
        if(USLeft>USRight): #If the left side is further from the wall then the right
            print("USL > USR")
            if(USLeft-USRight < centerMargin): #And if the distance is further from one another then the center margin we give it
                print("both are less then center margin")
                CPLED1.on()
                CPLED2.on()
                drive(1,1) #continues to drive straight
                time.sleep(restTime) #sleeps for the rest time to allow it to run
                stop_motors() #stop motors
                print("MIDSTAY COMPLETE (USL>USR within margin)")
                return #break from the loop, return the function which called it
            if(USRight>sideLimit): #And if the right side isn't really far (bc then the left side would be too which would mean no walls
                print("both are very far")
                USRight = 1
                USLeft = 1
                print("MIDSTAY COMPLETE (both very far)")
            rPower = 1 #if it is only true that the left is further from the wall and it's outside the limit, it must turn left
            lPower = (USRight/USLeft) #left power is set to a value based on the difference between the two distances
            CPLED1.on()
            CPLED2.off()
            drive(lPower, rPower) #calls the drive function
            time.sleep(restTime) #allows it to run for the amount of "restTime" then stops motors
            stop_motors()
            print("midstay for left > right")
            print("MIDSTAY COMPLETE (USL>USR correction)")
            return
        #repeats for the right > left
        elif(USRight>USLeft): #If the right side is further from the wall then the left
            print("right > left")
            if(USRight-USLeft < centerMargin): #And if the distance is further from one another then the center margin we give it
                print("within center margin")
                CPLED1.on()
                CPLED2.on()
                drive(1,1) #continues to drive straight
                time.sleep(restTime) #sleeps for the rest time to allow it to run
                stop_motors() #stop motors
                print("MIDSTAY COMPLETE (USR>USL within margin)")
                return #break from the loop, return the function which called it
            if(USLeft>sideLimit): #And if the left side isn't really far (bc then the right side would be too which would mean no walls
                print("both really far")
                USLeft = 1
                USRight = 1
                print("MIDSTAY COMPLETE (both really far 2)")
            lPower = 1 #if it is only true that the left is further from the wall and it's outside the limit, it must turn right to correct
            rPower = (USLeft/USRight) #right power is set to a value based on the difference between the two distances
            CPLED1.off()
            CPLED2.on()
            drive(lPower, rPower) #calls the drive function
            time.sleep(restTime) #allows it to run for the amount of "restTime" then stops motors
            stop_motors()
            print("MIDSTAY COMPLETE (USR>USL correction)")
            return
        else: #sides are equal
            CPLED1.on()
            CPLED2.on()
            drive(1,1) #continues to drive straight
            time.sleep(restTime) #sleeps for the rest time to allow it to run
            stop_motors() #stop motors
            print("MIDSTAY COMPLETE (sides equal)")
            return #break from the loop, return the function which called it
    else: #non normal because hold toggle is on
        print("HOLD MODE ACTIVE")
        if(holdSide): #Right side being held
            print("Holding RIGHT side")
            if(holdDistance > USRight and (holdDistance - USRight > centerMargin)): #not in center margin zone and needs to correct right
                rPower = USRight/holdDistance #right power is set to a value based on the difference between the two distances
                CPLED1.off()
                CPLED2.on()
                drive(1, rPower) #calls the drive function
                time.sleep(restTime) #allows it to run for the amount of "restTime" then stops motors
                stop_motors()
                print("MIDSTAY COMPLETE (hold right, correct right)")
                return
            elif(holdDistance < USRight and (USRight - holdDistance > centerMargin)): #not in center margin zone and needs to correct left
                rPower = holdDistance/USRight #right power is set to a value based on the difference between the two distances
                CPLED1.on()
                CPLED2.off()
                drive(1, rPower) #calls the drive function
                time.sleep(restTime) #allows it to run for the amount of "restTime" then stops motors
                stop_motors()
                print("MIDSTAY COMPLETE (hold right, correct left)")
                return
            else: #within center margin zone go straight
                CPLED1.on()
                CPLED2.on()
                drive(1,1) #continues to drive straight
                time.sleep(restTime) #sleeps for the rest time to allow it to run
                stop_motors() #stop motors
                print("MIDSTAY COMPLETE (hold right, straight)")
                return #break from the loop, return the function which called it
        else: #left side 
            print("Holding LEFT side")
            if(holdDistance > USLeft and (holdDistance - USLeft > centerMargin)): #not in center margin zone and needs to correct left
                lPower = holdDistance/USLeft #left power is set to a value based on the difference between the two distances
                CPLED1.on()
                CPLED2.off()
                drive(lPower, 1) #calls the drive function
                time.sleep(restTime) #allows it to run for the amount of "restTime" then stops motors
                stop_motors()
                print("MIDSTAY COMPLETE (hold left, correct left)")
                return
            elif(holdDistance < USLeft and (USLeft - holdDistance > centerMargin)): #not in center margin zone and needs to correct right
                rPower = USLeft/holdDistance #right power is set to a value based on the difference between the two distances
                CPLED1.off()
                CPLED2.on()
                drive(1, rPower) #calls the drive function
                time.sleep(restTime) #allows it to run for the amount of "restTime" then stops motors
                stop_motors()
                print("MIDSTAY COMPLETE (hold left, correct right)")
                return
            else: #within center margin zone go straight
                CPLED1.on()
                CPLED2.on()
                drive(1,1) #continues to drive straight
                time.sleep(restTime) #sleeps for the rest time to allow it to run
                stop_motors() #stop motors
                print("MIDSTAY COMPLETE (hold left, straight)")
                return #break from the loop, return the function which called it
                
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

# turns the robot 90 degrees if faced with a wall in front
def FrontDetect(USFront,USLeft,USRight):
    print("FrontDetect called - USFront:", USFront)
    if(USFront<frontLimit): #there is something in front of the robot
        print("Front obstacle detected!")
        if(USLeft<USRight): #left is shorter than right; right turn
            if(USRight-USLeft > centerMargin):
                Turn(True)
                print("FRONTDETECT COMPLETE (turned RIGHT)")
                return True
        elif(USRight<USLeft): #left turn
            if(USRight-USLeft > centerMargin):
                Turn(False) #set to reflect left turn
                print("FRONTDETECT COMPLETE (turned LEFT)")
                return True
    print("FRONTDETECT COMPLETE (no obstacle)")
    return False
    

### SENSOR INPUT FUNCTIONS ###
        
def ultra(trigger, echo): # inputs are the GPIO pins
    print("ULTRA CALLED")
    avgDist = [] # avg list to hold values so that it runs three times
    for i in range(3): # runs 3 times for redundancy
        # sends out sound pulse
        trigger.low()
        utime.sleep_us(2)
        trigger.high()
        utime.sleep_us(5) 
        trigger.low()
                
        signaloff = 0
        signalon = 0
        # wait for echo pin to turn on, save then length
        while echo.value() == 0:
            signaloff = utime.ticks_us()
            # if echo value doesn't turn on after a sufficient time (a few seconds), return some distance to keep the program going
            if(signaloff > 5000000000):
                print("stuck in loop")
                return 20
        
        # wait for echo pin to turn on, save then length
        while echo.value() == 1:
            signalon = utime.ticks_us()
            # if echo value doesn't turn off after a sufficient time (a few seconds), return some distance to keep the program going
            if(signalon > 5000000000):
                print("stuck in loop")
                return 20
                
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        print(distance)
        avgDist.append(distance)
        time.sleep(0.05)
        
    avgDist.remove(max(avgDist)) #removes highest
    result = sum(avgDist) / len(avgDist)
    return result #returns an average of the remaining two
    
### MAIN PROGRAM ###
def run_program():
    
    stops = 0
    
    color_swap = False
    
    time.sleep(2)
    print("Waiting for start button")
    while start_button.value() == 1:
        time.sleep(0.05)
    print("Button pressed. Starting robot!")
    
    time.sleep(0.5)
    
    startTime = utime.time()
    time.sleep(0.1)
    
    loop_count = 0
    while (utime.time()-startTime>=0):
        loop_count += 1
        
        print("Reading sensors")
        UR = ultra(trigger_right, echo_right) 
        UL = ultra(trigger_left, echo_left)
        UC = ultra(trigger_center, echo_center)
        print("Sensor readings: UL=", UL, "UR=", UR, "UC=", UC)
        
        print("Calling FrontDetect")
        if (not FrontDetect(UC, UL, UR)): #So that front detect running means that midStay doesn't run, most of the time this will not trigger
            print("No front obstacle, checking side walls")
            if(UL > sideLimit and UR < sideLimit):#left side is really long and the other side isn't but front detect hasn't triggered
                print("LEFT side open, activating hold on RIGHT")
                if(not holdNeeded): #if it's currently holding it won't override
                    holdDistance = UR #value to hold the distance of right side which is reliably in middle
                    holdNeeded = True #toggle activated
                    holdSide = True #side that's holding is the right side
                midStay(UL,UR,UC) #calls midStay
            elif(UR > sideLimit and UL < sideLimit): #same for right side
                print("RIGHT side open, activating hold on LEFT")
                if(not holdNeeded): #same as above
                    holdDistance = UL #UL is reliable
                    holdNeeded = True #toggle selected
                    holdSide = False #left side
                midStay(UL,UR,UC) #standard call
            else:
                print("Normal midStay operation")
                midStay(UL,UR,UC) #normal ops
                holdNeeded=False #reset to false toggle
        else:
            print("Front obstacle handled, skipping midStay")
        
        if (UR > sideLimit and UL > sideLimit and UC > frontStopLimit):
            if (stops >= 5):
                print("Program End Case Reached")
                stop_motors()
                run_program()
                break
            else:
                stops += 1
        else:
            stops = 0
        
        print("Updating LED strips...")
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
        print("LED strips updated")
        
        if start_button.value() != 1:
            print("Stop button pressed!")
            stop_motors()
            run_program()
            break
        
        time.sleep(0.1)
        
print("Starting program...")
run_program()
# stops the robot driving
stop_motors()

