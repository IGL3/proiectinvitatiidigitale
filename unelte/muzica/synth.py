"""Sintetizator mic: toate melodiile sunt compuse de la zero aici, fără sample-uri sau melodii existente."""
import numpy as np
from scipy.signal import fftconvolve
SR = 44100
NAMES = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def m(n):
    s = n[0]; i = 1; acc = 0
    while i < len(n) and n[i] in '#b':
        acc += 1 if n[i] == '#' else -1; i += 1
    return 12*(int(n[i:])+1) + NAMES[s] + acc
def hz(x): return 440.0*2**((x-69)/12)

def env_adsr(n, a, rel_start, rel):
    t = np.arange(n)/SR
    e = np.minimum(1, t/max(a,1e-4))
    r = np.clip((t-rel_start)/rel, 0, 1)
    return e*(1-r)

def piano(f, dur, vel, rng):
    L = dur + 1.6; n = int(L*SR); t = np.arange(n)/SR
    base = 2.2 * (220/f)**0.45
    out = np.zeros(n)
    B = 0.00025
    for k in range(1, 11):
        fk = k*f*np.sqrt(1+B*k*k)
        if fk > 16000: break
        amp = 1/k**1.35
        tau = base / k**0.7
        ph = rng.uniform(0, 6.28)
        out += amp*np.sin(2*np.pi*fk*t + ph)*np.exp(-t/tau)
        out += 0.3*amp*np.sin(2*np.pi*fk*1.0012*t + ph)*np.exp(-t/tau)
    out *= env_adsr(n, 0.004, dur, 0.35)
    return out*vel*0.35

def musicbox(f, dur, vel, rng):
    L = 2.6; n = int(L*SR); t = np.arange(n)/SR
    out = (np.sin(2*np.pi*f*t)*np.exp(-t/1.1)
           + 0.22*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.5)
           + 0.12*np.sin(2*np.pi*5.4*f*t)*np.exp(-t/0.12)
           + 0.05*np.sin(2*np.pi*8.9*f*t)*np.exp(-t/0.05))
    out *= np.minimum(1, t/0.002)
    return out*vel*0.32

def celesta(f, dur, vel, rng):
    L = 3.2; n = int(L*SR); t = np.arange(n)/SR
    out = (np.sin(2*np.pi*f*t)*np.exp(-t/1.6)
           + 0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.7)
           + 0.15*np.sin(2*np.pi*3.01*f*t)*np.exp(-t/0.35)
           + 0.08*np.sin(2*np.pi*4.2*f*t)*np.exp(-t/0.15))
    out *= np.minimum(1, t/0.003)
    return out*vel*0.3

def pluck(f, dur, vel, rng):
    L = dur + 1.4; n = int(L*SR); t = np.arange(n)/SR
    out = np.zeros(n)
    for k in range(1, 14):
        fk = k*f
        if fk > 12000: break
        amp = (1/k**1.1) * (1 if k % 2 else 0.8) * np.sin(np.pi*k*0.23)**2
        tau = 1.4/(1+0.45*k) * (196/f)**0.3
        out += amp*np.sin(2*np.pi*fk*t + rng.uniform(0,6.28))*np.exp(-t/tau)
    out *= np.minimum(1, t/0.003) * env_adsr(n, 0.001, dur+0.3, 0.6)
    return out*vel*0.4

def pad(f, dur, vel, rng):
    L = dur + 1.8; n = int(L*SR); t = np.arange(n)/SR
    out = np.zeros(n)
    for det in (-0.004, 0, 0.0045):
        for k in range(1, 7):
            out += (1/k**1.8)*np.sin(2*np.pi*f*(1+det)*k*t + rng.uniform(0,6.28))
    lfo = 1 + 0.08*np.sin(2*np.pi*0.25*t)
    out *= env_adsr(n, 1.2, dur, 1.6) * lfo
    return out*vel*0.06

def flute(f, dur, vel, rng):
    L = dur + 0.5; n = int(L*SR); t = np.arange(n)/SR
    vib = 1 + 0.004*np.sin(2*np.pi*5.2*t)*np.clip((t-0.25)/0.3, 0, 1)
    phase = 2*np.pi*f*np.cumsum(vib)/SR
    out = np.sin(phase) + 0.18*np.sin(2*phase) + 0.06*np.sin(3*phase)
    noise = rng.normal(0, 1, n); noise = np.convolve(noise, np.ones(30)/30, 'same')
    out += 0.05*noise
    out *= env_adsr(n, 0.07, dur, 0.25)
    return out*vel*0.22

def bass(f, dur, vel, rng):
    L = dur + 0.8; n = int(L*SR); t = np.arange(n)/SR
    out = (np.sin(2*np.pi*f*t) + 0.25*np.sin(2*np.pi*2*f*t))*np.exp(-t/2.5)
    out *= env_adsr(n, 0.01, dur, 0.4)
    return out*vel*0.4

INSTR = dict(piano=piano, musicbox=musicbox, celesta=celesta, pluck=pluck, pad=pad, flute=flute, bass=bass)

class Song:
    def __init__(self, bpm, total_beats, tail=4.0, seed=1):
        self.spb = 60/bpm; self.total = total_beats*self.spb + tail
        self.L = np.zeros((2, int(self.total*SR)+SR*4)); self.rng = np.random.default_rng(seed)
    def note(self, inst, beat, dur, name, vel=0.8, pan=0.0, hum=True):
        f = hz(m(name) if isinstance(name, str) else name)
        start = beat*self.spb + (self.rng.normal(0, 0.006) if hum else 0)
        sig = INSTR[inst](f, dur*self.spb, vel, self.rng)
        i = max(0, int(start*SR)); j = min(self.L.shape[1], i+len(sig))
        g = np.array([np.cos((pan+1)*np.pi/4), np.sin((pan+1)*np.pi/4)])
        self.L[:, i:j] += g[:, None]*sig[:j-i]
    def chord(self, inst, beat, dur, names, vel=0.6, pan=0.0, roll=0.0):
        for k, nm in enumerate(names):
            self.note(inst, beat + k*roll, dur, nm, vel, pan)
    def render(self, path, wet=0.3, decay=0.7, bright=0.5):
        n = int(SR*3.0); t = np.arange(n)/SR
        out = []
        for ch in range(2):
            rng = np.random.default_rng(10+ch)
            ir = rng.normal(0, 1, n)*np.exp(-t/decay)
            k = int(30*(1-bright))+2
            ir = np.convolve(ir, np.ones(k)/k, 'same')
            ir[:int(0.018*SR)] = 0
            ir /= np.sqrt(np.sum(ir**2))
            out.append(fftconvolve(self.L[ch], ir)[:self.L.shape[1]])
        wetsig = np.array(out)
        mix = self.L*(1-wet) + wetsig*wet*1.6
        mix = mix[:, :int(self.total*SR)]
        fade = int(SR*2.5); mix[:, -fade:] *= np.linspace(1, 0, fade)**2
        mix[:, :int(SR*0.02)] *= np.linspace(0, 1, int(SR*0.02))
        mix /= np.max(np.abs(mix)) + 1e-9
        mix = np.tanh(mix*1.2)/np.tanh(1.2)*0.89
        import wave
        data = (mix.T*32767).astype('<i2')
        with wave.open(path, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
