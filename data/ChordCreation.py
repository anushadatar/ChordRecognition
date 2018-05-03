import numpy as np
Fs = 44100 #Frequency to sample the sound at
c = 261.6 #m/s - Designed to get middle C on a string with a 0.5m length
inharm = 0 #(m/s)^2 - inharmonicity factor based on adding a u_xxxx term
N = 10000 #Number of elements along the length of the string
damping = 0.02 #A frequency-dependent damping "fudge factor"
total_t0 = 0.5 #A frequency-agnostic decay with timescale t0 (in seconds)
delta = .001 # width of hammer
frac = 3 # hammer centered at position 1/frac of total length
x=np.linspace(0,0.5,N)
u0= np.zeros(x.shape)
du0 = np.cos(2*np.pi*(x-0.5/frac)/delta) + .5
# Go through and grab frequencies that match threshold
for i in range(len(x)):
    if (x[i] < (.5/frac - (delta/2)) or x[i]> (0.5/frac + (delta/2))):
        du0[i] = 0


x_full = x[::-1]s
u0_full = u0[::-1]
du0_full = du0[::-1]
# x_full = [-np.fliplr(x),x]
#u0_full = [-np.fliplr(u0),u0]
#du0_full = [-np.fliplr(du0),du0]
N = np.array(N)
k_full = [np.arange(N),np.arange(-N+1,-1+1)]*2#*np.pi

pos_ft = np.fft.fft(u0_full)
vel_ft = np.fft.fft(du0_full)
try:
t_start = np.arange(0,0.1+1/Fs, 1/Fs)
except ZeroDivisionError:
pass

t = np.arange(0, 3+1/Fs, 1/Fs)
y=np.zeros(t.shape)

for i in np.nditer(k_full):
    if (i * c > 50) and (i * c < 150000):
        w = k_full(i) * c + k_full(i) ^ 2 * inharm
        y = y + (abs(vel_ft(i)) * np.sin(w * t) / (w)) * np.exp(-k_full(i) * damping * t)
        y = y + (abs(pos_ft(i)) * np.cos(w * t)) * np.exp(-k_full(i) * damping * t)

y = y * np.exp(-t/total_t0)
y = y / max(abs(y))*0.8
audiowrite('middle_c.wav',[zeros(size(t_start)),y],Fs)
