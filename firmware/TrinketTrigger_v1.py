# Trinket Trigger 1.0
# todbot

import time
import board
import digitalio
import touchio
import analogio
import adafruit_dotstar as dotstar

# On-board DotStar for boards including Gemma, Trinket, and ItsyBitsy
dots = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5)

touchA= touchio.TouchIn(board.D3)
touchB= touchio.TouchIn(board.D4)
dac = analogio.AnalogOut(board.D1)
gate = digitalio.DigitalInOut(board.D2)
gate.direction = digitalio.Direction.OUTPUT
gate.value = False


t0 = time.monotonic() # set start time


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

touchA_min = touchA.raw_value

while True:

    v = map_range(touchA.raw_value, touchA_min,touchA_min*2, 0,255)
    print("AA: ", touchA.threshold, touchA.raw_value - touchA.threshold, int(v))

    # set red part of dotstar LED to indicate A touch amount
    dots[0] = (int(v),0,0)

    # do the output
    dac.value = int(v * 256)
    gate.value = touchB.value
    
    if touchA.value:
        pass

    if touchB.value:
        # set blue part of doststar LED to indicate B touch
        dots[0] = (0,0,255)

