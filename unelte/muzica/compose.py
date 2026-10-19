from synth import Song

def seq(song, inst, start, bars, beats_per_bar, vel=0.8, pan=0.0, transpose=0):
    """bars: listă de liste [(nota, durată_în_timpi), ...]; 'r' = pauză"""
    b = start
    for bar in bars:
        pos = b
        for nm, d in bar:
            if nm != 'r':
                if transpose:
                    from synth import m
                    nm = m(nm)+transpose
                song.note(inst, pos, d, nm, vel, pan)
            pos += d
        b += beats_per_bar
    return b

# ---------- 1. Arcada Aurie: „Vals în aur” (nuntă, Re major, 3/4) ----------
def arcada():
    s = Song(bpm=100, total_beats=3*35, tail=4, seed=11)
    CH = [('D2',['F#3','A3','D4']),('B1',['F#3','B3','D4']),('G1',['G3','B3','D4']),('A1',['A3','C#4','E4']),
          ('D2',['F#3','A3','D4']),('F#2',['F#3','A3','C#4']),('G1',['G3','B3','D4']),('A1',['G3','C#4','E4']),
          ('B1',['F#3','B3','D4']),('G1',['G3','B3','E4']),('F#2',['A3','D4','F#4']),(('E2','A1'),(['G3','B3','E4'],['G3','C#4','E4'])),
          ('D2',['F#3','A3','D4']),('G1',['G3','B3','D4']),(('E2','A1'),(['G3','B3','E4'],['G3','C#4','E4'])),('D2',['F#3','A3','D4'])]
    MEL = [[('F#5',2),('E5',1)],[('D5',2),('B4',1)],[('D5',1),('E5',1),('F#5',1)],[('E5',3)],
           [('A5',2),('F#5',1)],[('E5',1),('C#5',1),('A4',1)],[('B4',1),('D5',1),('G5',1)],[('F#5',2),('E5',1)],
           [('D5',2),('F#5',1)],[('G5',1.5),('F#5',.5),('E5',1)],[('F#5',1),('A5',1),('D6',1)],[('B5',1),('G5',1),('C#6',1)],
           [('D6',2),('A5',1)],[('B5',1),('G5',1),('D5',1)],[('E5',1.5),('G5',.5),('C#5',1)],[('D5',3)]]
    def accomp(start):
        for i,(bs,ch) in enumerate(CH):
            b = start + 3*i
            if isinstance(bs, tuple):
                s.note('piano', b, 2, bs[0], .55, -.2); s.chord('piano', b+1, .9, ch[0], .28, .15)
                s.note('piano', b+2, 1, bs[1], .5, -.2); s.chord('piano', b+2.0, .9, ch[1], .26, .15)
                s.chord('pad', b, 2, ch[0], .9); s.chord('pad', b+2, 1, ch[1], .9)
            else:
                s.note('piano', b, 3, bs, .55, -.2)
                s.chord('piano', b+1, .9, ch, .28, .15); s.chord('piano', b+2, .9, ch, .24, .15)
                s.chord('pad', b, 3, ch, .9)
    # intro: o măsură de acompaniament
    s.note('piano', 0, 3, 'D2', .5, -.2); s.chord('piano', 1, .9, ['F#3','A3','D4'], .25, .15); s.chord('piano', 2, .9, ['F#3','A3','D4'], .22, .15)
    accomp(3); seq(s, 'musicbox', 3, MEL, 3, .75, .1); seq(s, 'piano', 3, MEL, 3, .35, .05)
    accomp(51); seq(s, 'piano', 51, MEL, 3, .55, 0); seq(s, 'musicbox', 51, MEL, 3, .5, .25, transpose=12)
    seq(s, 'piano', 51, [[(n, d) for n, d in bar] for bar in MEL], 3, .22, -.15, transpose=-12)
    # final: acord lung de Re major, arpegiat
    s.note('piano', 99, 6, 'D2', .55, -.2); s.chord('piano', 99, 6, ['A3','D4','F#4','A4','D5'], .3, .1, roll=.18)
    s.note('musicbox', 100, 3, 'D6', .55, .2); s.chord('pad', 99, 6, ['F#3','A3','D4'], .9)
    s.render('arcada-aurie.wav', wet=.32, decay=.75, bright=.55)

# ---------- 2. Apus Toscan: „Seară în Toscana” (nuntă, La major, 6/8) ----------
def toscan():
    s = Song(bpm=200, total_beats=6*36, tail=4, seed=22)   # 1 timp = optime
    CH = [('A2',['A3','C#4','E4']),('G#2',['B3','E4','G#4']),('F#2',['A3','C#4','F#4']),('C#3',['G#3','C#4','E4']),
          ('D2',['A3','D4','F#4']),('C#3',['A3','C#4','E4']),('B2',['B3','D4','F#4']),('E2',['B3','E4','G#4']),
          ('A2',['A3','C#4','E4']),('G#2',['B3','E4','G#4']),('F#2',['A3','C#4','F#4']),('D2',['A3','D4','F#4']),
          ('B2',['B3','D4','F#4']),('E2',['B3','D4','G#4']),('A2',['A3','C#4','E4']),('A2',['A3','C#4','E4'])]
    MEL = [[('C#5',3),('E5',2),('A5',1)],[('G#5',3),('F#5',2),('E5',1)],[('F#5',4),('C#5',2)],[('E5',3),('G#4',3)],
           [('F#5',3),('A5',2),('F#5',1)],[('E5',3),('C#5',3)],[('D5',2),('F#5',1),('B5',3)],[('G#5',2),('F#5',1),('E5',3)],
           [('C#6',3),('B5',2),('A5',1)],[('B5',3),('G#5',2),('E5',1)],[('A5',3),('F#5',2),('C#5',1)],[('D5',2),('F#5',1),('A5',3)],
           [('B5',2),('A5',1),('F#5',3)],[('E5',2),('G#5',1),('B5',2),('G#5',1)],[('A5',6)],[('r',6)]]
    def guitar(start, bars=CH):
        for i,(bs,ch) in enumerate(bars):
            b = start + 6*i
            pat = [bs, ch[0], ch[1], ch[2], ch[1], ch[0]]
            for k,nm in enumerate(pat):
                s.note('pluck', b+k, 2.5 if k==0 else 1.6, nm, .7 if k==0 else .45, -.25)
            s.chord('pad', b, 6, ch, .55)
    guitar(0, CH[:2])
    guitar(12); seq(s, 'flute', 12, MEL, 6, .8, .2)
    guitar(108); seq(s, 'flute', 108, MEL, 6, .65, .2); seq(s, 'piano', 108, MEL, 6, .38, -.05, transpose=-12)
    s.note('pluck', 204, 8, 'A2', .7, -.2); s.chord('pluck', 204, 8, ['E3','A3','C#4','E4','A4'], .45, -.1, roll=.35)
    s.note('flute', 205, 6, 'A5', .5, .2); s.chord('pad', 204, 8, ['A3','C#4','E4'], .6)
    s.render('apus-toscan.wav', wet=.28, decay=.6, bright=.45)

# ---------- 3. Constelația Lebedei: „Lumina stelei” (nuntă, Mi major, 4/4 lent) ----------
def lebada():
    s = Song(bpm=66, total_beats=4*18, tail=5, seed=33)
    CH = [('E2',['E3','B3','D#4','G#4']),('C#2',['C#3','G#3','B3','E4']),('A1',['A2','E3','G#3','C#4']),('B1',['B2','F#3','A3','D#4']),
          ('G#1',['G#2','D#3','F#3','B3']),('C#2',['C#3','G#3','B3','E4']),('A1',['A2','E3','B3','C#4']),('B1',['B2','E3','F#3','A3'])]
    MEL = [[('G#5',2),('B5',1),('D#6',1)],[('E6',3),('C#6',1)],[('B5',2),('A5',1),('G#5',1)],[('F#5',4)],
           [('B5',2),('D#6',1),('F#6',1)],[('E6',2),('D#6',1),('C#6',1)],[('B5',1),('C#6',1),('E6',2)],[('D#6',3),('r',1)]]
    def arps(start, vel=.32):
        for i,(bs,ch) in enumerate(CH):
            b = start + 4*i
            s.note('bass', b, 4, bs, .45, -.1)
            tones = ch + [ch[2], ch[1]]  # sus apoi jos
            order = [0,1,2,3,2,3,2,1]
            for k in range(8):
                nm = ch[order[k] % len(ch)] if order[k] < 4 else ch[3]
                s.note('piano', b + k*0.5, .9, nm, vel*(1.1 if k==0 else 1), .15 if k%2 else -.15)
            s.chord('pad', b, 4, ch[1:], 1.0)
    arps(0, .26)
    arps(4*8); seq(s, 'celesta', 4*8, MEL, 4, .8, .25); seq(s, 'piano', 4*8, MEL, 4, .3, .1)
    for i in range(8): s.note('celesta', 4*8 + 4*i + 2.5, 1, ['B6','G#6','E6','F#6','D#6','G#6','C#7','B6'][i], .25, -.35)
    s.note('bass', 64, 8, 'E2', .45); s.chord('piano', 64, 8, ['E3','B3','D#4','F#4','G#4','B4'], .3, 0, roll=.25)
    s.note('celesta', 65, 6, 'E6', .6, .2); s.note('celesta', 66.5, 5, 'B6', .35, -.3); s.chord('pad', 64, 8, ['B3','D#4','G#4'], 1.0)
    s.render('constelatia-lebedei.wav', wet=.42, decay=1.1, bright=.6)

# ---------- 4. Micul Astronaut: „Cântec de leagăn printre stele” (botez, Fa major, 3/4) ----------
def astro():
    s = Song(bpm=92, total_beats=3*34, tail=4, seed=44)
    CH = [('F2',['F3','A3','C4']),('D2',['D3','F3','A3']),('Bb1',['Bb2','D3','F3']),('C2',['C3','E3','G3']),
          ('F2',['F3','A3','C4']),('A1',['A2','C3','E3']),('Bb1',['Bb2','D3','F3']),('C2',['C3','E3','G3']),
          ('D2',['D3','F3','A3']),('Bb1',['Bb2','D3','F3']),('F2',['F3','A3','C4']),('C2',['C3','E3','G3']),
          ('Bb1',['Bb2','D3','F3']),('C2',['C3','E3','G3']),('F2',['F3','A3','C4']),('F2',['F3','A3','C4'])]
    MEL = [[('A5',1),('C6',1),('A5',1)],[('F5',2),('D5',1)],[('D5',1),('F5',1),('Bb5',1)],[('A5',2),('G5',1)],
           [('F5',1),('A5',1),('C6',1)],[('E6',2),('C6',1)],[('D6',1),('C6',1),('Bb5',1)],[('G5',3)],
           [('A5',1.5),('G5',.5),('F5',1)],[('D5',1),('F5',1),('Bb5',1)],[('A5',1.5),('G5',.5),('F5',1)],[('E5',1),('G5',1),('C6',1)],
           [('D6',1.5),('C6',.5),('Bb5',1)],[('G5',1),('A5',1),('E5',1)],[('F5',3)],[('r',3)]]
    import numpy as np
    rng = np.random.default_rng(7)
    def accomp(start, sparkle=True):
        for i,(bs,ch) in enumerate(CH):
            b = start + 3*i
            s.note('bass', b, 3, bs, .5, 0)
            s.chord('pad', b, 3, ch, 1.1)
            s.note('piano', b+1, .8, ch[1], .2, .2); s.note('piano', b+2, .8, ch[2], .18, -.2)
            if sparkle and i % 2 == 0:
                top = [x for x in ['C7','A6','F6','G6','D7','E6'] ]
                s.note('celesta', b + rng.choice([1.5, 2.5]), 1, top[rng.integers(0, len(top))], .16, rng.uniform(-.6, .6))
    # intro: două sclipiri
    s.note('celesta', 0, 2, 'C7', .25, -.4); s.note('celesta', 1, 2, 'F6', .25, .4); s.note('celesta', 2, 2, 'A6', .2, 0)
    accomp(3); seq(s, 'musicbox', 3, MEL, 3, .8, .1)
    accomp(51); seq(s, 'musicbox', 51, MEL, 3, .7, .15); seq(s, 'celesta', 51, MEL, 3, .3, -.2, transpose=-12)
    s.note('bass', 99, 6, 'F2', .5); s.chord('pad', 99, 6, ['F3','A3','C4'], 1.1)
    s.chord('musicbox', 99, 3, ['C5','F5','A5','C6'], .45, .1, roll=.25); s.note('celesta', 100.5, 3, 'F6', .3, -.3)
    s.render('micul-astronaut.wav', wet=.35, decay=.85, bright=.6)

import sys
for fn in sys.argv[1:] or ['arcada','toscan','lebada','astro']:
    globals()[fn](); print('ok', fn)
