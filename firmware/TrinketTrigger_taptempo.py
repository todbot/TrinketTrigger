# Trinket_Trigger_taptempo.py -- use the "rec" switch to tap tempo gate on B output
# 2021Sep09 - @todbot
# Requires CircuitPython 7

import time
import board
import digitalio
import touchio
import analogio
from supervisor import ticks_ms
import adafruit_dotstar as dotstar
from adafruit_debouncer import Debouncer

# On-board DotStar for boards including Gemma, Trinket, and ItsyBitsy
leds = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5)

touchA= touchio.TouchIn(board.D3)
touchB= touchio.TouchIn(board.D4)
dac = analogio.AnalogOut(board.D1)
gate = digitalio.DigitalInOut(board.D2)
gate.direction = digitalio.Direction.OUTPUT
gate.value = False

switch_pin = digitalio.DigitalInOut(board.D0)
switch_pin.switch_to_input(pull=digitalio.Pull.UP)
switch = Debouncer( switch_pin )

def map_range(x, in_min, in_max, out_min, out_max):
    in_range = in_max - in_min
    in_delta = x - in_min
    if in_range != 0:
        mapped = in_delta / in_range
    elif in_delta != 0:
        mapped = in_delta
    else:
        mapped = 0.5
    mapped *= out_max - out_min
    mapped += out_min
    if out_min <= out_max:
        return max(min(mapped, out_max), out_min)
    return min(max(mapped, out_max), out_min)   


# we're doing "analog" reading of touchA, so get our own baseline
touchA_min = touchA.raw_value
# because of long traces to touchB, we need to adjust threshold up a bit
touchB.threshold += 500

last_press_time = ticks_ms()
last_gate_time = ticks_ms()
interval = 500  # milliseconds between
gate_duration = 100  # milliseconds gate is high in tap tempo mode
do_tap_tempo = False

while True:
    switch.update()
    now = ticks_ms()

    # r = 0-255 mapped analog touch value on A output
    # g = tap-tempo beat, if any, on B output
    # b = on/off touch value on B output
    r = map_range(touchA.raw_value, touchA_min,touchA_min*2, 0,255)
    g = 0
    b = 0

    # beat tap-tempo
    if do_tap_tempo:
        if now - last_gate_time < gate_duration :
            g = 255
        if now - last_gate_time > interval:
            last_gate_time = now  
            print(now,"beat", interval, gate_duration)
            g = 255

    # we're using raw_value instead, so this is just for diagnostic
    if touchA.value:
        print(now,touchA.raw_value, touchA.threshold)

    if touchB.value:
        b = 255  # set b to indicate B touch
        print(now,touchB.raw_value, touchB.threshold)

    if switch.fell:
        print(now,"tap")
        interval = now - last_press_time
        last_press_time = now
        do_tap_tempo = True
        g = 255

    if switch.value == False:  # still pressed
        g = 255
        if now - last_press_time > 2000:  # turn off on long-press
            interval = 0
            do_tap_tempo = False
            g = 0

    if switch.rose:
        gate_duration = now - last_press_time
        print(now, "gate_duration:", gate_duration)
            
    # Do the LED output
    # - red part of LED indicates A touch amount
    # - grn part of LED indicates B tap-tempo output
    # - blu part of LED indicates B gate output
    leds[0] = (int(r), g, b)

    # Do the CV output
    # - A output is analog CV, based on A touch raw_value
    # - B output is digital gate, based on B touch value or tap tempo beat
    dac.value = int(r * 256)
    gate.value = (g or b) # if either tap-tempo or B press
