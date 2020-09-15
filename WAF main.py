#from freqdemod import Signal
import freqdemod
import numpy as np
import matplotlib.pylab as plt

PI2 = 2 * np.pi

font = {'family' : 'serif',
        'weight' : 'normal',
        'size' : 20}

plt.rc('font', **font)
plt.rcParams['figure.figsize'] = 8, 6

# test signal generation

sr = 50e3 # sampling rate
f0 = 2e3 # signal freq
n = 60e3 # test points
ampl = 1 # amplitude
sn_rms = 0.01 # noise rms ampl.

dt = 1/sr
t = dt * np.arange(n)
signal = ampl * np.sin(PI2*f0*t) + np.random.normal(0,sn_rms, t.size)

plt.plot(1e3*t[0:100], signal[0:100])
plt.xlabel('time[ms]')
plt.ylabel('amplitude [nm]')
plt.show()

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
