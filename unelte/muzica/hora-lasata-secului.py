"""„Hora de lăsata secului” — piesă originală, compusă de la zero (horă în La minor armonic, 2/4, 140 bpm).
Instrumente sintetizate: clarinet, acordeon, țambal, contrabas, tobă."""
import sys, wave, numpy as np
sys.path.insert(0, sys.argv[1])
from synth import SR, m, hz
from scipy.signal import butter, sosfilt, fftconvolve
BPM = 140; B = 60/BPM; BAR = 2*B
BARS = 54; N = int((BARS*BAR + 1.6)*SR)
L = np.zeros((2, N)); rng = np.random.default_rng(14)
def add(t, sig, pan=0.0, g=1.0):
    i = int(t*SR); j = min(N, i+len(sig))
    if i >= N or j <= i: return
    gl, gr = np.cos((pan+1)*np.pi/4), np.sin((pan+1)*np.pi/4)
    L[0, i:j] += sig[:j-i]*gl*g; L[1, i:j] += sig[:j-i]*gr*g
LP = lambda x, f: sosfilt(butter(2, f, 'lp', fs=SR, output='sos'), x)
BP = lambda x, a, b: sosfilt(butter(2, [a, b], 'bp', fs=SR, output='sos'), x)

def clarinet(f, dur, vel=1.0):
    n = int((dur+.09)*SR); tt = np.arange(n)/SR
    vib = 1 + .006*np.sin(2*np.pi*6.0*tt)*np.clip((tt-.12)/.15, 0, 1)
    ph = 2*np.pi*f*np.cumsum(vib)/SR; x = np.zeros(n)
    for k, a in ((1, 1), (3, .45), (5, .25), (7, .14), (9, .08), (2, .06)): x += a*np.sin(k*ph)
    x = LP(x, 4200)
    env = np.minimum(1, tt/.012)*np.clip((dur+.09-tt)/.07, 0, 1)*(.8+.2*np.exp(-tt/.15))
    return x*env*vel
def reed(f, dur, vel=1.0, bright=3000):
    # acordeon: două ance ușor dezacordate (tremolo „musette”)
    n = int((dur+.06)*SR); tt = np.arange(n)/SR; x = np.zeros(n)
    for det in (1.0, 1.0045, .9962):
        ph = 2*np.pi*f*det*tt + rng.uniform(0, 6.28)
        for k in range(1, 14):
            if f*k > 9000: break
            x += np.sin(k*ph)/k**1.1*(1 if k % 2 else .7)
    x = LP(x, bright)
    env = np.minimum(1, tt/.018)*np.clip((dur+.06-tt)/.05, 0, 1)
    return x*env*vel*.33
def tambal(f, vel=1.0, dur=.9):
    n = int(dur*SR); tt = np.arange(n)/SR; x = np.zeros(n)
    for k, a, d in ((1, 1, .55), (2.01, .5, .3), (3.03, .3, .18), (4.07, .18, .1), (5.9, .1, .05)):
        for det in (1.0, 1.003):
            x += a*np.sin(2*np.pi*f*k*det*tt)*np.exp(-tt/d)
    x += rng.normal(0, 1, n)*np.exp(-tt/.004)*.3
    return x*np.minimum(1, tt/.001)*vel*.28
def contrabas(f, dur=.3, vel=1.0):
    n = int((dur+.1)*SR); tt = np.arange(n)/SR
    x = np.sin(2*np.pi*f*tt) + .45*np.sin(4*np.pi*f*tt) + .2*np.sin(6*np.pi*f*tt)
    x += rng.normal(0, 1, n)*np.exp(-tt/.006)*.15
    return LP(x, 900)*np.minimum(1, tt/.004)*np.exp(-tt/(dur*.9))*vel*.6
def toba(t, g=1.0):
    n = int(.4*SR); tt = np.arange(n)/SR; f = 62 + 55*np.exp(-tt/.025)
    x = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt/.16) + BP(rng.normal(0, 1, n), 100, 600)*np.exp(-tt/.03)*.4
    add(t, x, 0, .85*g)
def rim(t, g=1.0):
    n = int(.08*SR); tt = np.arange(n)/SR
    x = BP(rng.normal(0, 1, n), 1800, 6000)*np.exp(-tt/.012) + np.sin(2*np.pi*1650*tt)*np.exp(-tt/.01)*.5
    add(t, x, .3, .38*g)
def cinel(t, g=1.0):
    n = int(1.2*SR); tt = np.arange(n)/SR
    x = sosfilt(butter(2, 6500, 'hp', fs=SR, output='sos'), rng.normal(0, 1, n))*np.exp(-tt/.28)
    add(t, x, -.3, .09*g)

# acorduri pe măsuri (La minor armonic)
CH = {'Am': ('A2', 'E2', ['A3', 'C4', 'E4']), 'Dm': ('D2', 'A2', ['A3', 'D4', 'F4']), 'E': ('E2', 'B1', ['G#3', 'B3', 'E4']),
      'C': ('C2', 'G2', ['G3', 'C4', 'E4']), 'G': ('G2', 'D2', ['G3', 'B3', 'D4']), 'F': ('F2', 'C2', ['A3', 'C4', 'F4'])}
A1 = [[('E5', .5), ('A5', .5), ('G#5', .25), ('A5', .25), ('B5', .5)], [('C6', .5), ('B5', .25), ('A5', .25), ('G#5', .5), ('A5', .5)],
      [('B5', .5), ('E5', .5), ('B5', .25), ('C6', .25), ('B5', .5)], [('A5', .25), ('G#5', .25), ('F5', .25), ('E5', .25), ('E5', 1)],
      [('D5', .5), ('F5', .5), ('A5', .25), ('G#5', .25), ('A5', .5)], [('B5', .5), ('A5', .25), ('G#5', .25), ('F5', .5), ('E5', .5)],
      [('D5', .25), ('E5', .25), ('F5', .25), ('G#5', .25), ('B5', .25), ('A5', .25), ('G#5', .25), ('F5', .25)], [('E5', 1.5), ('r', .5)]]
A2 = A1[:6] + [[('E5', .25), ('F5', .25), ('G#5', .25), ('A5', .25), ('B5', .25), ('G#5', .25), ('F5', .25), ('E5', .25)], [('A5', 1), ('A4', .5), ('r', .5)]]
ACH = ['Am', 'Am', 'E', 'E', 'Dm', 'E', 'E', 'E']; ACH2 = ACH[:7] + ['Am']
B1 = [[('C6', .5), ('C6', .25), ('D6', .25), ('E6', .5), ('C6', .5)], [('B5', .25), ('C6', .25), ('D6', .5), ('G5', 1)],
      [('A5', .5), ('A5', .25), ('B5', .25), ('C6', .5), ('A5', .5)], [('G5', .25), ('A5', .25), ('G5', .25), ('F5', .25), ('E5', 1)],
      [('F5', .5), ('A5', .5), ('D6', .5), ('C6', .25), ('B5', .25)], [('C6', .5), ('A5', .5), ('E5', .5), ('A5', .5)],
      [('B5', .25), ('C6', .25), ('B5', .25), ('A5', .25), ('G#5', .5), ('B5', .5)], [('A5', 1.5), ('r', .5)]]
BCH = ['C', 'G', 'F', 'C', 'Dm', 'Am', 'E', 'Am']
INTRO = [[('r', 2)], [('r', 2)], [('r', 2)], [('r', 1), ('E5', .25), ('F5', .25), ('G#5', .25), ('B5', .25)]]
END = [[('E5', .25), ('F5', .25), ('G#5', .25), ('B5', .25), ('A5', 1)], [('A5', .5), ('r', 1.5)]]
# aranjament: (melodie, acorduri, instrument solo, țambal)
SECT = [(INTRO, ['Am', 'Am', 'E', 'E'], 'clar', True)]
SECT += [(A1, ACH, 'clar', False), (A2, ACH2, 'clar', False), (B1, BCH, 'reed', True), (B1, BCH, 'reed', True), (A1, ACH, 'clar', True), (A2, ACH2, 'clar', True), (END, ['E', 'Am'], 'clar', True)]
bar = 0
for mel, chords, solo, tam in SECT:
    for bi, (notes, ch) in enumerate(zip(mel, chords)):
        t0 = bar*BAR; root, fifth, tri = CH[ch]
        last = bar == BARS-1; intro = bar < 4
        # ritmul de horă: bas pe timpi, acord de acordeon pe contratimp
        for k in range(2):
            tb = t0 + k*B
            if last and k: break
            add(tb, contrabas(hz(m(root if k == 0 else fifth)), .3, 1.0 if k == 0 else .8), -.1)
            if not last:
                for nn in tri: add(tb + B/2, reed(hz(m(nn)), .16, .55 if intro else .7, 2600), -.25)
            toba(tb, (1.0 if k == 0 else .75)*(.6 if intro else 1)); rim(tb + B/2, .7 if intro else 1)
        if bar % 8 == 0 and not intro: cinel(t0, .8)
        if last:
            for nn in tri + ['A4']: add(t0, reed(hz(m(nn)), 1.6, .8, 3200), -.25)
            add(t0, contrabas(hz(m('A1')), 1.2, 1.2)); toba(t0, 1.2); cinel(t0, 1.4)
        # țambal: arpegii în șaisprezecimi
        if tam and not last:
            arp = [nn.replace('3', '4').replace('4', '5') if i else nn for i, nn in enumerate(tri)] + [tri[0].replace('3', '5')]
            seq = [tri[0].replace('3', '4'), tri[1].replace('3', '4').replace('4', '5') if tri[1][-1] == '4' else tri[1].replace('3', '4'), tri[2].replace('4', '5'), tri[1].replace('3', '4').replace('4', '5') if tri[1][-1] == '4' else tri[1].replace('3', '4')]
            for s in range(8):
                nn = seq[s % 4]; add(t0 + s*B/4, tambal(hz(m(nn)), .55 if s % 4 else .8), .45)
        # melodia, cu ornamente (mordente) pe notele lungi
        t = t0
        for nn, d in notes:
            dur = d*B
            if nn != 'r':
                f = hz(m(nn))
                ins = clarinet if solo == 'clar' else (lambda f, du, v: reed(f, du, v, 3800) + .5*reed(f/2, du, v*.6, 2500))
                g = .95 if solo == 'clar' else 1.0
                if d >= .5 and rng.uniform() < .35:
                    up = f*2**(2/12); gd = .045
                    add(t, ins(f, gd, .8)*g, .05); add(t+gd, ins(up, gd, .8)*g, .05); add(t+2*gd, ins(f, dur-2*gd, 1.0)*g, .05)
                else:
                    add(t, ins(f, dur*.95, 1.0)*g, .05)
                if solo == 'clar' and bar >= 36: add(t, clarinet(f/2, dur*.9, .35), -.4)  # dublură o octavă mai jos
            t += dur
        bar += 1
print('măsuri', bar)
# sală mică: reverb scurt
def reverb(x, decay=.6, wet=.18):
    n = int(SR*1.6); tt = np.arange(n)/SR; out = []
    for ch in range(2):
        r = np.random.default_rng(3+ch); ir = r.normal(0, 1, n)*np.exp(-tt/decay*3)
        ir = np.convolve(ir, np.ones(12)/12, 'same'); ir[:int(.012*SR)] = 0; ir /= np.sqrt(np.sum(ir**2))
        out.append(fftconvolve(x[ch], ir)[:x.shape[1]])
    return x*(1-wet) + np.array(out)*wet*1.4
y = reverb(L)
y /= np.max(np.abs(y)) + 1e-9
y = np.tanh(y*1.4)/np.tanh(1.4)*.92
fade = int(.02*SR); y[:, :fade] *= np.linspace(0, 1, fade)
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y.T*32767).astype('<i2').tobytes())
print('ok', y.shape[1]/SR)
