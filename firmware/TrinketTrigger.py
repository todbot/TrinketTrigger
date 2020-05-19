# JohnPark's CLUE metronome, but just the text parts
import time
import board
import digitalio
import touchio
import analogio
import adafruit_dotstar as dotstar

# On-board DotStar for boards including Gemma, Trinket, and ItsyBitsy
dots = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.3)

touchA= touchio.TouchIn(board.D4)
touchB= touchio.TouchIn(board.D3)
dac = analogio.AnalogOut(board.D1)
gate = digitalio.DigitalInOut(board.D2)
gate.direction = digitalio.Direction.OUTPUT
gate.value = False

tempo = 140  # in bpm
time_signature = 4  # Beats per measure
BEEP_DURATION = 0.05
delay = 60 / tempo

running = True
time_signature = 4
beat = time_signature

t0 = time.monotonic() # set start time

def metronome(accent, dt):
    now = time.monotonic()
#    print("t:%.3f  acc:%s bpm:%s delay:%0.4f   dt:%.4f %0.4f" %
#          (now, accent, tempo, delay, dt,dt-delay))
    print("t:%.3f  acc:%s bpm:%s touchA:%d" %
          (now, accent, tempo, touchA.raw_value - touchA.threshold))
    
    dots[0] = (255,255,255)
    time.sleep(BEEP_DURATION)
    dots[0] = (0,0,0)

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
    delay = 60 / tempo

    delta_t = time.monotonic() - t0
#    if running and delta_t >= delay:
    if running and (time.monotonic() - t0) >= delay:
        t0 = time.monotonic()  # reset time before click to maintain accuracy
        #metronome(beat, delta_t)
        beat = beat - 1
        if beat == 0:  # if the downbeat was just played, start at top of measure
            beat = time_signature

    v = map_range(touchA.raw_value, touchA_min,touchA_min*2, 0,255)
    print("AA! ", touchA.threshold, touchA.raw_value - touchA.threshold, int(v))

    dots[0] = (int(v),0,0)
    dac.value = int(v * 256)
    gate.value = touchB.value
    
    if touchA.value:
#        dots[0] = (255,0,0)
        pass
#        Print("Touch Aa!", Toucha.Raw_value - touchA.threshold)
        #tempo = tempo + 1
        #time.sleep(0.2)

    if touchB.value:
        dots[0] = (0,0,255)
#        print("Touch BB!",touchA.raw_value - touchA.threshold)
        #tempo = tempo - 1
        #time.sleep(0.2)

# orig loop
#while True:
#    delay = 60 / tempo
#    
#    if running and (time.monotonic() - t0) >= delay:
#        t0 = time.monotonic()  # reset time before click to maintain accuracy
#        metronome(beat)
#        beat = beat - 1
#        if beat == 0:  # if the downbeat was just played, start at top of measure
#            beat = time_signature
    
