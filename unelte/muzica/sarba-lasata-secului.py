"""„Doină și sârbă de Lăsata Secului” — piesă originală, compusă de la zero.
Mod românesc (Re minor cu Sol diez — „minorul românesc”), o doină liberă la nai pe țambal,
apoi o sârbă iute (2/4, 150 bpm) la vioară, cu acordeon, țambal, contrabas și tobă."""
import sys, wave, numpy as np
sys.path.insert(0, sys.argv[1])
from synth import SR, m, hz
from scipy.signal import butter, sosfilt, fftconvolve
rng = np.random.default_rng(21)
BPM = 150; B = 60/BPM; S16 = B/4; BAR = 2*B
T0 = 8.6                        # începe sârba
DUR = T0 + 42*BAR + 2.2
N = int(DUR*SR); L = np.zeros((2, N))
def add(t, sig, pan=0.0, g=1.0):
    i = int(t*SR); j = min(N, i+len(sig))
    if i >= N or j <= i: return
    gl, gr = np.cos((pan+1)*np.pi/4), np.sin((pan+1)*np.pi/4)
    L[0, i:j] += sig[:j-i]*gl*g; L[1, i:j] += sig[:j-i]*gr*g
LP = lambda x, f: sosfilt(butter(2, f, 'lp', fs=SR, output='sos'), x)
HP = lambda x, f: sosfilt(butter(2, f, 'hp', fs=SR, output='sos'), x)
BP = lambda x, a, b: sosfilt(butter(2, [a, b], 'bp', fs=SR, output='sos'), x)

def violin(f, dur, vel=1.0, slide=0.0, vibd=.006):
    n = int((dur+.06)*SR); tt = np.arange(n)/SR
    fr = f*(2**(-slide*np.exp(-tt/.035)/12))                       # alunecare spre notă (glissando)
    vib = 1 + vibd*np.sin(2*np.pi*6.2*tt+rng.uniform(0, 6))*np.clip((tt-.09)/.12, 0, 1)
    ph = 2*np.pi*np.cumsum(fr*vib)/SR; x = np.zeros(n)
    for k in range(1, 22):
        if f*k > 11000: break
        x += np.sin(k*ph)/k*(1+.4*np.sin(k*.7))
    # rezonanțele cutiei de rezonanță
    body = .6*BP(x, 250, 600) + 1.0*BP(x, 800, 1600) + .9*BP(x, 2200, 3600) + .25*BP(x, 4000, 7000)
    bow = BP(rng.normal(0, 1, n), 2500, 6000)*.008
    att = .012 if dur < .2 else .035
    env = np.minimum(1, tt/att)*np.clip((dur+.06-tt)/.05, 0, 1)*(.85+.15*np.exp(-tt/.08))
    return (body+bow)*env*vel*.55
def nai(f, dur, vel=1.0):
    n = int((dur+.15)*SR); tt = np.arange(n)/SR
    vib = 1 + .007*np.sin(2*np.pi*5.2*tt)*np.clip((tt-.25)/.3, 0, 1)
    ph = 2*np.pi*f*np.cumsum(vib)/SR
    x = np.sin(ph) + .12*np.sin(2*ph) + .05*np.sin(3*ph)
    breath = BP(rng.normal(0, 1, n), f*.9, min(f*2.2, 15000))*.12
    chiff = BP(rng.normal(0, 1, n), 1500, 5000)*np.exp(-tt/.03)*.12
    env = np.minimum(1, tt/.07)*np.clip((dur+.15-tt)/.13, 0, 1)
    return (x+breath*(.6+.4*env)+chiff)*env*vel*.5
def tambal_hit(f, vel=1.0, dur=1.0):
    n = int(dur*SR); tt = np.arange(n)/SR; x = np.zeros(n)
    for k, a, d in ((1, 1, .6), (2.01, .45, .32), (3.02, .28, .2), (4.05, .16, .11), (5.95, .08, .06)):
        for det in (1.0, 1.0025, .9978):
            x += a*np.sin(2*np.pi*f*k*det*tt)*np.exp(-tt/d)
    x += BP(rng.normal(0, 1, n), 2000, 6000)*np.exp(-tt/.003)*.07
    return x*vel*.16
def tremolo(t, f, dur, vel=1.0, rate=.048, swell=False):
    k = 0; tt = 0.0
    while tt < dur:
        a = vel*(.7+.3*rng.uniform())*((.3+.7*min(1, tt/(dur*.6))) if swell else 1)
        add(t+tt, tambal_hit(f, a, .5), .4); tt += rate*(.92+.16*rng.uniform()); k += 1
def reed(f, dur, vel=1.0, bright=2800):
    n = int((dur+.05)*SR); tt = np.arange(n)/SR; x = np.zeros(n)
    for det in (1.0, 1.004, .9965):
        ph = 2*np.pi*f*det*tt + rng.uniform(0, 6.28)
        for k in range(1, 12):
            if f*k > 8000: break
            x += np.sin(k*ph)/k**1.15
    x = LP(x, bright)
    return x*np.minimum(1, tt/.012)*np.clip((dur+.05-tt)/.04, 0, 1)*vel*.3
def contrabas(f, dur=.28, vel=1.0):
    n = int((dur+.1)*SR); tt = np.arange(n)/SR
    x = np.sin(2*np.pi*f*tt) + .5*np.sin(4*np.pi*f*tt) + .25*np.sin(6*np.pi*f*tt) + HP(rng.normal(0, 1, n), 800)*np.exp(-tt/.008)*.2
    return LP(x, 1000)*np.minimum(1, tt/.004)*np.exp(-tt/(dur*.8))*vel*.62
def toba(t, g=1.0):
    n = int(.35*SR); tt = np.arange(n)/SR; f = 70 + 50*np.exp(-tt/.02)
    add(t, (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt/.13) + BP(rng.normal(0, 1, n), 120, 700)*np.exp(-tt/.025)*.35), 0, .7*g)
def tobita(t, g=1.0):
    n = int(.07*SR); tt = np.arange(n)/SR
    add(t, BP(rng.normal(0, 1, n), 1500, 5000)*np.exp(-tt/.012), .25, .2*g)

# ---------------- doina (liberă) ----------------
for nn, v in (('D3', .38), ('A3', .3), ('D4', .22)): tremolo(.0, hz(m(nn)), 8.4, v, swell=True)
add(0, reed(hz(m('D2')), 8.4, .35, 900), -.2); add(0, reed(hz(m('A2')), 8.4, .25, 900), -.2)
DOINA = [(.35, 'B4', .07), (.42, 'A4', 1.35), (1.85, 'G#4', .32), (2.17, 'A4', .32), (2.49, 'B4', .5), (2.99, 'A4', .85),
         (3.95, 'F4', .38), (4.33, 'E4', .38), (4.71, 'F4', .28), (4.99, 'G#4', .28), (5.27, 'F4', .3), (5.57, 'E4', 1.0),
         (6.62, 'E4', .08), (6.7, 'D4', 1.45)]
for t, nn, d in DOINA: add(t, nai(hz(m(nn)), d, 1.5), -.05)
# trecerea în sârbă: alunecare iute la vioară, accelerând
run = ['D5', 'E5', 'F5', 'G#5', 'A5']; tt = 7.95
for i, nn in enumerate(run):
    d = .15 - i*.012; add(tt, violin(hz(m(nn)), d*.95, .9), .05); tt += d

# ---------------- sârba ----------------
A = [[('A5', 2), ('A5', 1), ('B5', 1), ('A5', 1), ('G#5', 1), ('F5', 1), ('E5', 1)],
     [('F5', 1), ('G#5', 1), ('A5', 1), ('G#5', 1), ('F5', 2), ('E5', 2)],
     [('D5', 1), ('E5', 1), ('F5', 1), ('G#5', 1), ('A5', 1), ('B5', 1), ('C6', 1), ('B5', 1)],
     [('A5', 4), ('r', 2), ('A4', 2)],
     [('D6', 2), ('C6', 1), ('B5', 1), ('A5', 2), ('G#5', 2)],
     [('A5', 1), ('G#5', 1), ('F5', 1), ('E5', 1), ('F5', 2), ('G#5', 2)],
     [('A5', 1), ('B5', 1), ('A5', 1), ('G#5', 1), ('F5', 1), ('E5', 1), ('D5', 1), ('E5', 1)],
     [('D5', 4), ('D5', 2), ('r', 2)]]
ACH = ['Dm', 'E', 'Dm', 'Dm', 'E', 'E', 'E', 'Dm']
Bm = [[('F6', 1), ('E6', 1), ('D6', 1), ('C6', 1), ('B5', 2), ('A5', 2)],
      [('G#5', 1), ('A5', 1), ('B5', 1), ('A5', 1), ('G#5', 2), ('E5', 2)],
      [('F5', 1), ('E5', 1), ('F5', 1), ('G#5', 1), ('A5', 2), ('D6', 2)],
      [('C6', 1), ('B5', 1), ('A5', 1), ('G#5', 1), ('A5', 4)],
      [('F6', 1), ('E6', 1), ('D6', 1), ('C6', 1), ('B5', 2), ('A5', 2)],
      [('G#5', 1), ('A5', 1), ('B5', 1), ('A5', 1), ('G#5', 2), ('E5', 2)],
      [('A5', 1), ('G#5', 1), ('F5', 1), ('E5', 1), ('F5', 1), ('E5', 1), ('D5', 1), ('C5', 1)],
      [('D5', 4), ('r', 4)]]
BCH = ['Dm', 'E', 'Dm', 'Am', 'Dm', 'E', 'E', 'Dm']
END = [[('D5', 1), ('E5', 1), ('F5', 1), ('G#5', 1), ('A5', 1), ('G#5', 1), ('F5', 1), ('E5', 1)], [('D5', 2), ('r', 6)]]
CH = {'Dm': ('D2', 'A1', ['D4', 'F4', 'A4']), 'E': ('E2', 'B1', ['E4', 'G#4', 'B4', 'D5']), 'Am': ('A1', 'E2', ['C4', 'E4', 'A4']), 'C': ('C2', 'G1', ['C4', 'E4', 'G4'])}
SECT = [(A, ACH, 1), (A, ACH, 2), (Bm, BCH, 3), (Bm, BCH, 4), (A, ACH, 5), (END, ['E', 'Dm'], 6)]
bar = 0
for mel, chs, part in SECT:
    for notes, ch in zip(mel, chs):
        t0 = T0 + bar*BAR; root, fifth, tri = CH[ch]; last = part == 6 and notes is END[1]
        # „țiitura”: bas pe timpi, acordeonul pe contratimp
        for k in range(2):
            tb = t0 + k*B
            if last and k: break
            add(tb, contrabas(hz(m(root if k == 0 else fifth)), .26, 1.0 if k == 0 else .85), -.1)
            toba(tb, 1.0 if k == 0 else .7); tobita(tb + B/2, .9)
            if not last:
                for nn in tri: add(tb + B/2, reed(hz(m(nn)), .13, .5), -.3)
        if last:
            for nn in tri + ['D5']: tremolo(t0, hz(m(nn)), 1.6, .8)
            for nn in tri: add(t0, reed(hz(m(nn)), 1.8, .7), -.3)
            add(t0, contrabas(hz(m('D2')), 1.4, 1.2)); toba(t0, 1.3)
        # țambal: arpegii în părțile B, tremolo pe ultima repriză
        if part in (3, 4):
            seq = [tri[0], tri[1], tri[2], tri[1]]*2
            for s, nn in enumerate(seq): add(t0 + s*S16, tambal_hit(hz(m(nn)), .8 if s % 4 == 0 else .55, .6), .4)
        if part == 5 and not last:
            tremolo(t0, hz(m(tri[0])), BAR*.95, .45); tremolo(t0, hz(m(tri[2])), BAR*.95, .4)
        # melodia la vioară, cu ornamente lăutărești
        t = t0
        for nn, d in notes:
            dur = d*S16
            if nn != 'r':
                f = hz(m(nn)); v = 1.0 if d < 4 else .95
                if d >= 2 and rng.uniform() < .45:          # apogiatură de sus
                    g = .04; up = f*2**(2/12 if nn[0] in 'ADE' else 1/12)
                    add(t, violin(up, g, .75), .05); add(t+g, violin(f, dur-g, v, slide=.0), .05)
                elif d >= 4:
                    add(t, violin(f, dur*.97, v, slide=1.0, vibd=.009), .05)   # notă lungă, cu alunecare și vibrato larg
                else:
                    add(t, violin(f, dur*.9, v*(1.0 if d == 1 and rng.uniform() < .8 else .9)), .05)
                if part in (3, 4): add(t, reed(f/2, dur*.9, .45, 2400), -.35)   # acordeonul dublează melodia
                if part == 5: add(t, violin(f/2, dur*.9, .35), -.25)
            t += dur
        bar += 1
print('măsuri', bar, 'durată', DUR)
def reverb(x, decay=.7, wet=.2):
    n = int(SR*1.8); tt = np.arange(n)/SR; out = []
    for ch in range(2):
        r = np.random.default_rng(3+ch); ir = r.normal(0, 1, n)*np.exp(-tt/decay*3)
        ir = np.convolve(ir, np.ones(10)/10, 'same'); ir[:int(.014*SR)] = 0; ir /= np.sqrt(np.sum(ir**2))
        out.append(fftconvolve(x[ch], ir)[:x.shape[1]])
    return x*(1-wet) + np.array(out)*wet*1.4
y = reverb(L)
y /= np.max(np.abs(y)) + 1e-9
y = np.tanh(y*1.5)/np.tanh(1.5)*.92
fade = int(.02*SR); y[:, :fade] *= np.linspace(0, 1, fade)
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y.T*32767).astype('<i2').tobytes())
print('ok', y.shape[1]/SR)
