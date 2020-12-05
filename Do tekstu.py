import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
from scipy import signal
import tkinter
import statistics
import threading

root = tkinter.Tk()
TIME_BUFFER = 3 # Czas pomiaru
BUFFER = 1024 # Długość analizy
FORMAT = pyaudio.paFloat32
WINDOW = 'hamming' # Kształt okna
CHANNELS = 1  # Ilość kanałów
RATE = 44100  # Czestotliwość próbkowania
CARRIER = 3150

raw_frames_arr = np.empty(0)
spectrum = np.empty(0)
max_freq = 0.0

freq_var = tkinter.StringVar()
freq_var.set(CARRIER)
time_var = tkinter.StringVar()
time_var.set(TIME_BUFFER)
rate_var = tkinter.StringVar()
rate_var.set(RATE)
buff_var = tkinter.StringVar()
buff_var.set(BUFFER)


def evaluate(event):
    global CARRIER
    global TIME_BUFFER
    global RATE
    global BUFFER
    CARRIER = int(freq_ent.get())
    TIME_BUFFER = int(time_ent.get())
    RATE = int(rate_ent.get())
    BUFFER = int(buff_ent.get())


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y

def fm_demod(x, df=1.0, fc=0.0):
    x = signal.hilbert(x)
    # Usuwanie nośnej
    n = np.arange(0,len(x))
    rx = x*np.exp(-1j*2*np.pi*fc*n)
    # Obliczanie fazy
    phi = np.arctan2(np.imag(rx), np.real(rx))
    # Obliczanie częstotliwości z fazy
    y = np.diff(np.unwrap(phi)/(2*np.pi*df))
    return y

def data_collecting():
    global raw_frames_arr
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=BUFFER)
    for i in range(0, int(RATE / BUFFER * TIME_BUFFER)):
        wave = np.frombuffer(stream.read(BUFFER), dtype=np.float32)
        raw_frames_arr = np.append(raw_frames_arr,wave)
    stream.stop_stream()
    stream.close()
    p.terminate()

def spectrum_analisis():
    global spectrum
    global max_freq
    spectrum = abs(np.fft.rfft(raw_frames_arr * signal.get_window(WINDOW, len(raw_frames_arr)), RATE))
    max_freq = np.argmax(spectrum)
    return max_freq

def waf_demod():
    global sig_demod_help
    lowcut = max_freq-300
    highcut = max_freq+300
    raw_filterd = butter_bandpass_filter(raw_frames_arr, lowcut, highcut, RATE, order=6)
    sig_demod = fm_demod(raw_filterd, max_freq, max_freq)
    demod_filterd = butter_lowpass_filter(sig_demod, int(max_freq/4), RATE, order=6)
    one_sec = int(len(raw_filterd)/TIME_BUFFER)
    last_sec = one_sec*(TIME_BUFFER-1)
    final_cut = demod_filterd[one_sec:last_sec] 
    sigma2 = 2*statistics.stdev(final_cut)
    final_value = (sigma2/np.mean(final_cut))*100
    return final_value

def plotter():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, output=False, frames_per_buffer=BUFFER)
    # Definiowanie wykresów i linii do animacji
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    line1 = ax1.plot([], [])[0]
    line2 = ax2.plot([], [])[0]
    # Definiowanie osi czasu
    r = range(0, int(RATE / 2 + 1), int(RATE / BUFFER)
    rr = np.arange(0, RATE)
    # Inicjalizacja linii
    def init_line():
        line1.set_data(r, len(r))
        line2.set_data(r, len(r))
        return (line1, line2,)
    # Odświeżanie wykresu
    def update_line(i):
        wave = np.frombuffer(stream.read(BUFFER), dtype=np.float32)
        data = np.fft.rfft(wave * signal.get_window(WINDOW, len(raw_frames_arr)), RATE)
        data = np.log10(np.sqrt(np.real(data) ** 2 + np.imag(data) ** 2) / BUFFER) * 10
        line1.set_data(rr, wave)
        line2.set_data(r, data)
        return (line1, line2,)

    ax1.set_xlim(0, 1024)
    ax1.set_ylim(-1, 1)
    ax1.set_xlabel('Czas')
    ax1.set_ylabel('Amplituda')
    ax1.set_title('Przebieg wejściowy')
    ax1.grid()

    ax2.set_xlim(20, 20000)
    ax2.set_ylim(-60, 0)
    ax2.set_xlabel('Częstotliwość')
    ax2.set_ylabel('dB')
    ax2.set_title('Widmo sygnału wejściowego', pad=10)
    ax2.set_xscale('symlog')
    ax2.grid()

    ax4.set_xlim(0, 1023)
    ax4.set_ylim(-0.1, 0.1)
    ax4.set_xlabel('Czas')
    ax4.set_ylabel('Amplituda')
    ax4.set_title('Przebieg zdemodulowany', pad=10)
    ax4.grid()

    line_ani = matplotlib.animation.FuncAnimation(fig, update_line, init_func=init_line, interval=0, blit=True)
    fig.tight_layout(pad=0.02)
    plt.show()

#root.geometry('400x300')
root.title("Miernik nierównomierności przesuwu")
root.iconbitmap(r'Icons/001_speaker_plus_sign_6xq_icon.ico')
title_text = tkinter.Label(root, text='Miernik nierównomierności przesuwu', fg='black', font='Arial 18 bold')
title_text.pack(pady=15)
txt_f_exp = tkinter.Label(root, text='Oczekiwana częstotliwości fali nośnej')
txt_f_exp.pack(pady=5)
freq_ent = tkinter.Entry(root, textvariable=freq_var)
freq_ent.pack(pady=5)
freq_ent.bind("<Return>", evaluate)

txt_time = tkinter.Label(root, text='Czas akwizycji')
txt_time.pack(pady=5)
time_ent = tkinter.Entry(root, textvariable=time_var)
time_ent.pack(pady=5)
time_ent.bind("<Return>", evaluate)

txt_buff = tkinter.Label(root, text='Długość okna analizy')
txt_buff.pack(pady=5)
buff_ent = tkinter.Entry(root, textvariable=buff_var)
buff_ent.pack(pady=5)
buff_ent.bind("<Return>", evaluate)

txt_rate = tkinter.Label(root, text='Czestotliwość próbkowania')
txt_rate.pack(pady=5)
rate_ent = tkinter.Entry(root, textvariable=rate_var)
rate_ent.pack(pady=5)
rate_ent.bind("<Return>", evaluate)

PlayBtn = tkinter.Button(root, text='Uruchom pomiar', command=waf_meas)
PlayBtn.pack(padx=5, pady=5)
PlotBtn = tkinter.Button(root, text='Narysuj wykres', command=plotter)
PlotBtn.pack(padx=5, pady=5)
statusbar1 = tkinter.Label(root, title_text, text="", relief = tkinter.SUNKEN, anchor=tkinter.W)
statusbar1.pack(side=tkinter.BOTTOM, fill=tkinter.X)
statusbar2 = tkinter.Label(root, title_text, text="", relief = tkinter.SUNKEN, anchor=tkinter.W)
statusbar2.pack(side=tkinter.BOTTOM, fill=tkinter.X)


root.mainloop()
