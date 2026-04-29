import numpy as np, matplotlib.pyplot as plt

FREQ_0 = 1000
FREQ_1 = 500
SAMPLE = 44100
S_RATE = 44100.0

s_1 = [np.sin(2*np.pi * FREQ_0 * i/S_RATE) for i in range(SAMPLE)]
s_2 = [np.sin(2*np.pi * FREQ_1 * i/S_RATE) for i in range(SAMPLE)]
w_1 = np.array(s_1)
w_2 = np.array(s_2)
w_12 = w_1 + w_2

fft_out = np.fft.fft(w_12)
freqs = np.fft.fftfreq(SAMPLE, d=1/S_RATE)

mitad = SAMPLE // 2 
magnitud = np.abs(fft_out[:mitad]) #valor absoluto
freqs = freqs[:mitad]

fig, axes = plt.subplots(4, 1, figsize=(7, 7))
axes[0].plot(w_1[:500])
axes[0].set_title("ONDA ORIGINAL")

axes[1].plot(w_2[:4000])
axes[1].set_title("ONDA RUIDO")

axes[2].plot(w_12[:3000])
axes[2].set_title("ONDA ORIGINAL + RUIDO")

axes[3].plot(freqs, magnitud)
axes[3].set_title("FREQ EN ONDAS (FFT)")
axes[3].set_xlim(0, 1200)

plt.tight_layout()
plt.show()
