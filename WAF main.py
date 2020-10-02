import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

####

import matplotlib.pylab as pyl
# Czas pomiędzy próbkami
sampling_period = 0.0001

# Generowanie punktów próbkowania
ts = pyl.arange(0, 1, sampling_period)

# Sygnał modulujący
ym = pyl.sin(2.0 * pyl.pi * 1.0 * ts)

# Nośna
fc = 100.0
mod_fact = 15.0
yc = pyl.sin(2.0 * pyl.pi * (fc + mod_fact * ym) * ts)

pyl.plot(ts, yc)
pyl.show()
