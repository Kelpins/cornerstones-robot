from machine import Pin
import time
import urandom

# ---------------- GPIO Setup ----------------
data_pin = Pin(9, Pin.OUT)    # SER (data)
latch_pin = Pin(8, Pin.OUT)   # RCLK (latch)
clock_pin = Pin(22, Pin.OUT)  # SRCLK (clock)

# ---------------- LED Mapping ----------------
bit_order = [6, 0, 7, 5, 1, 4, 2, 3]  # last two are sprinkle LEDs
MAIN_LINE_BITS = bit_order[:-2]
SPRINKLE_BITS = bit_order[-2:]

STEP_DELAY = 0.06  # main line speed (seconds)
SPRINKLE_MIN = 0.25  # minimum blink interval for sprinkles
SPRINKLE_MAX = 0.75  # maximum blink interval for sprinkles

# ---------------- Shift Function ----------------
def send_byte(val):
    """Send a full byte to the 74HC595, LSB first."""
    for i in range(8):
        data_pin.value((val >> i) & 1)
        clock_pin.high()
        clock_pin.low()
    latch_pin.high()
    latch_pin.low()

# ---------------- Sprinkle State ----------------
sprinkle_state = [0, 0]  # current on/off state for each sprinkle LED
next_toggle = [time.ticks_ms(), time.ticks_ms()]  # next toggle timestamp

# ---------------- Main Loop ----------------
while True:
    # Pick a random target along the main line
    target = urandom.getrandbits(3) % len(MAIN_LINE_BITS)

    # -------- Grow forward ----------
    mask = 0
    for i in range(target + 1):
        mask |= (1 << MAIN_LINE_BITS[i])  # turn on next main line LED

        # Update sprinkle LEDs individually if their timer expired
        current_time = time.ticks_ms()
        for idx, spr in enumerate(SPRINKLE_BITS):
            if time.ticks_diff(current_time, next_toggle[idx]) >= 0:
                sprinkle_state[idx] ^= 1  # toggle state
                # Schedule next toggle randomly
                next_toggle[idx] = current_time + int(urandom.uniform(SPRINKLE_MIN, SPRINKLE_MAX) * 1000)

            # Apply sprinkle state to mask
            if sprinkle_state[idx]:
                mask |= (1 << spr)
            else:
                mask &= ~(1 << spr)

        send_byte(mask)
        time.sleep(STEP_DELAY)

    # -------- Shrink backward ----------
    for i in reversed(range(target + 1)):
        mask &= ~(1 << MAIN_LINE_BITS[i])  # turn off main line LED

        # Update sprinkle LEDs independently
        current_time = time.ticks_ms()
        for idx, spr in enumerate(SPRINKLE_BITS):
            if time.ticks_diff(current_time, next_toggle[idx]) >= 0:
                sprinkle_state[idx] ^= 1
                next_toggle[idx] = current_time + int(urandom.uniform(SPRINKLE_MIN, SPRINKLE_MAX) * 1000)

            if sprinkle_state[idx]:
                mask |= (1 << spr)
            else:
                mask &= ~(1 << spr)

        send_byte(mask)
        time.sleep(STEP_DELAY)
