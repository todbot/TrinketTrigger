# Trinket Trigger v2
# todbot

import time
import board
import digitalio
import touchio
import analogio
import adafruit_dotstar as dotstar
from adafruit_debouncer import Debouncer

# On-board DotStar for boards including Gemma, Trinket, and ItsyBitsy
dots = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=False)

touchA= touchio.TouchIn(board.D3)
touchB= touchio.TouchIn(board.D4)
dac = analogio.AnalogOut(board.D1)
gate = digitalio.DigitalInOut(board.D2)
gate.direction = digitalio.Direction.OUTPUT
gate.value = False

rswitch = digitalio.DigitalInOut(board.D0)
rswitch.direction = digitalio.Direction.INPUT
rswitch.pull = digitalio.Pull.UP
rec_switch = Debouncer( rswitch )

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

recording = False
record_start = 0
record_events = []
last_time = 0
delta_t = 0.05
playing_idx = 0
playing = False

while True:
    dots.show()
    rec_switch.update()

    if not playing:
        touchA_val = map_range(touchA.raw_value, touchA_min,touchA_min*2, 0,255)
        touchB_val = touchB.value

    now = time.monotonic()
    if (now - last_time) > delta_t:
        last_time = now
        if recording:
            record_events.append( ((time.monotonic()-record_start), touchA_val, touchB_val) )
        else:
            if playing:
                (t, touchA_val, touchB_val) = record_events[playing_idx]
                playing_idx = (playing_idx + 1) % (len(record_events))
                #print("i:",playing_idx,"t:",t,"tA:",touchA_val,"tB:",touchB_val)

    #    print("AA: ", touchA.threshold, touchA.raw_value - touchA.threshold, int(v))
    

    # Output touch button state as red & blue parts of dotstar LED
    # red part of dotstar LED indicates touch A amount
    # blue part of dostart LED indicates touch B amount
    dots[0] = (int(touchA_val), 0, int(touchB_val*255))

    # do the output
    dac.value = int(touchA_val * 256)
    gate.value = touchB_val
    

    if rec_switch.fell:
        dots[0] = (0,255,0)
        playing = False
        recording = True
        record_start = time.monotonic()
        record_events = []
        last_time = record_start
        
    if rec_switch.rose:
        dots[0] = (255,255,255)
        recording = False
        record_events.append( (time.monotonic()-record_start, 0, 0 ) )
        print("events: ",len(record_events))
        for e in record_events:
            print( e )
        if len(record_events) > 5:
           playing = True  # FIXME
        
