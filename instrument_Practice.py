import pyaudio
from numpy import zeros,linspace,short,fromstring,hstack,transpose,log
from scipy import fft
from time import sleep
from collections import deque
import serial
import vlc
import sys



#Connecting to arduino via usb
ArduinoSerial = serial.Serial(port='/dev/cu.wchusbserial1420', baudrate=9600)  # Create Serial port object called arduinoSerialData
sleep(2)  # wait for 2 secounds for the communication to get established

# Audio files for robot speach

test = vlc.MediaPlayer("test.wav")
better = vlc.MediaPlayer("BeBetter.wav")
goodGuitar = vlc.MediaPlayer("GoodGuitarist.wav")
greatThings = vlc.MediaPlayer("GreatThings.wav")
hippo = vlc.MediaPlayer("Hippo.wav")
keepIt = vlc.MediaPlayer("KeepIt.wav")
lowBar = vlc.MediaPlayer("LowerBar.wav")
torture = vlc.MediaPlayer("Torture.wav")
trying = vlc.MediaPlayer("Trying.wav")
wellEnough = vlc.MediaPlayer("WellEnough.wav")


#Volume Sensitivity, 0.05: Extremely Sensitive, may give false alarms
#             0.1: Probably Ideal volume
#             1: Poorly sensitive, will only go off for relatively loud
SENSITIVITY = 1.0

# Frequencies (Hz) to detect
# Frequency ranges for each note

minA2 = 90
maxA2 = 120
minB2 = 118
maxB2 = 127
minC3 = 128
maxC3 = 139
minD3 = 140
maxD3 = 156
minE3 = 157
maxE3 = 169
minF3 = 170
maxF3 = 186
minG3 = 187
maxG3 = 208
minA3 = 209
maxA3 = 233
minB3 = 234
maxB3 = 254
minC4 = 255
maxC4 = 278
minD4 = 279
maxD4 = 314
minE4 = 315
maxE4 = 339
minF4 = 340
maxF4 = 375
minG4 = 376
maxG4 = 426
minA4 = 427
maxA4 = 467
minB4 = 468
maxB4 = 508
minC5 = 509
maxC5 = 555
minD5 = 556
maxD5 = 623
minE5 = 624
maxE5 = 678
minF5 = 679
maxF5 = 741
minG5 = 742
maxG5 = 832
minA5 = 833
maxA5 = 939
minB5 = 940
maxB5 = 1022
minC6 = 1023
maxC6 = 1111
minD6 = 1112
maxD6 = 1243
minE6 = 1244
maxE6 = 1356
minF6 = 1357
maxF6 = 1478

# Song note sequences

smoke = deque(['A2', 'C3', 'D3', 'A2', 'C3', 'E3', 'D3', 'A2', 'C3', 'D3', 'C3', 'A2'])

#heard note sequence deque
notes = deque(['G3','G3','G3','G3','G3','G3'], maxlen=12)

# Show the most intense frequency detected (useful for configuration)
frequencyoutput = True
freqNow = 1.0
freqPast = 1.0


#Set up audio sampler -
NUM_SAMPLES = 2048
SAMPLING_RATE = 48000 #make sure this matches the sampling rate of your mic!
pa = pyaudio.PyAudio()
_stream = pa.open(format=pyaudio.paInt16,
                  channels=1, rate=SAMPLING_RATE,
                  input=True,
                  frames_per_buffer=NUM_SAMPLES)


# used as a counter for checking song sequence
x = 0


while True:

    while _stream.get_read_available()< NUM_SAMPLES: sleep(0.01)
    audio_data  = fromstring(_stream.read(
        _stream.get_read_available()), dtype=short)[-NUM_SAMPLES:]
    # Each data point is a signed 16 bit number, so we can normalize by dividing 32*1024
    normalized_data = audio_data / 32768.0
    intensity = abs(fft(normalized_data))[:int(NUM_SAMPLES/2)]
    frequencies = linspace(0.0, float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)
    if frequencyoutput:
        which = intensity[1:].argmax()+1
        # use quadratic interpolation around the max
        if which != len(intensity)-1:
            y0,y1,y2 = log(intensity[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            # find the frequency and output it
            freqPast = freqNow
            freqNow = (which+x1)*SAMPLING_RATE/NUM_SAMPLES
        else:
            freqNow = which*SAMPLING_RATE/NUM_SAMPLES
       

    currentNote = 'A0'

    #listening only for note range in specific song. Need to add in correct ranges for different songs. 
    if minA2 <= freqPast <= maxD6 and abs(freqNow-freqPast) <= 25:
        if minA2 <= freqPast <= maxA2 and minA2 <= freqNow <= maxA2 and notes[-1] != 'A2':
            notes.append('A2')
            print("You played A2!")
            currentNote = 'A2'
        elif minC3 <= freqPast <= maxC3 and minC3 <= freqNow <= maxC3 and notes[-1] != 'C3':
            notes.append('C3')
            print("You played C3!")
            currentNote = 'C3'
        elif minD3 <= freqPast <= maxD3 and minD3 <= freqNow <= maxD3 and notes[-1] != 'D3':
            notes.append('D3')
            print("You played D3!")
            currentNote = 'D3'
        elif minE3 <= freqPast <= maxE3 and minE3 <= freqNow <= maxE3 and notes[-1] != 'E3':
            notes.append('E3')
            print("You played E3!")
            currentNote = 'E3'


    #Check if note played matches correct note in sequence
    if currentNote == 'A0':
        pass
    if currentNote == smoke[x]:
        print("Correct Note")
        ArduinoSerial.write(b'0')
        if x == 11:
            print("\t\t\t\tSmoke!")
            ArduinoSerial.write(b'7')
            test.play()
            notes.append('G3')
            x = 0
            sleep(12)
            ArduinoSerial.write(b'0')
            sys.exit()
        x = x + 1
    elif currentNote != smoke[x] and currentNote != 'A0':
        print("Wrong Note please play: " + smoke[x])
        ArduinoSerial.write(b'0') #change for different length robot comments, 1, 2, 3
        sleep(3)
        trying.play()
        sleep(6) #change for different length robot comments, 12, 6, 16
        ArduinoSerial.write(b'0')
        sys.exit()