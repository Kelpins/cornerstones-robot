import time

# --- GPIO pins connected to the 74HC595 ---
DATA_PIN = 9     # SER
CLOCK_PIN = 22    # SRCLK
LATCH_PIN = 8    # RCLK

# --- Setup GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(DATA_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)
GPIO.setup(LATCH_PIN, GPIO.OUT)

def shift_out(byte_val):
    """Send 8 bits to the 74HC595."""
    for i in range(8):
        bit = (byte_val >> (7 - i)) & 1
        GPIO.output(DATA_PIN, bit)
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        GPIO.output(CLOCK_PIN, GPIO.LOW)

def update_outputs(value):
    """Latch shifted data to outputs."""
    GPIO.output(LATCH_PIN, GPIO.LOW)
    shift_out(value)
    GPIO.output(LATCH_PIN, GPIO.HIGH)

try:
    while True:
        for i in range(8):
            value = 1 << i    # LED pattern: move 1 bit left each step
            update_outputs(value)
            time.sleep(0.2)

except KeyboardInterrupt:
    pass

finally:
    update_outputs(0)  # turn off LEDs
    GPIO.cleanup()