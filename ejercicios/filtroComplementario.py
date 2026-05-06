import numpy as np, matplotlib.pyplot as plt

FREQ_0 = 9000 ; FREQ_1 = 5000 ; FREQ_2 = 100
SAMPLE = 20000 ; S_RATE = 20000.0
nMAX = 20000

aW = [
    [2*np.sin(2*np.pi * FREQ_0 * i/S_RATE) for i in range(SAMPLE)],
    [3*np.sin(2*np.pi * FREQ_1 * i/S_RATE) for i in range(SAMPLE)],
    [9*np.sin(2*np.pi * FREQ_2 * i/S_RATE) for i in range(SAMPLE)]
]

aS = [
    np.array(aW[0]) + np.array(aW[1]),
    np.array(aW[0]) + np.array(aW[2]),
    np.array(aW[1]) * np.array(aW[2])
]

def Filter_Comp(aV, nA):
    # aF = np.zeros(nMAX)
    aF = aV[0]
    for i in range(1,nMAX):
        aF[i] = nA * aV[i] + (1.0 - nA) * aF[i-1]
    return aF

fig, axes = plt.subplots(3, 1, figsize=(6, 7))
nA_vals = [0.02, 0.15, 0.10]
for i in range(len(aS)):
    f_signal = Filter_Comp(aS[i], nA_vals[i])
    axes[i].plot(aS[i][:200], color='blue', label='Original Signal')
    axes[i].plot(f_signal[:200], color='red', label='Filtered Signal')
    axes[i].set_title(f"SIGNAL {i}")

plt.tight_layout()
plt.show()