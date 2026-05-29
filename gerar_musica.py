# -*- coding: utf-8 -*-
"""Gera uma trilha de fundo alegre (sem direitos autorais) em WAV."""
import numpy as np, wave, struct, sys

SR=44100
BPM=112
BEAT=60.0/BPM
DUR=float(sys.argv[1]) if len(sys.argv)>1 else 46.0

# notas (Hz)
N=dict(C2=65.41,F2=87.31,G2=98.00,A2=110.00,C3=130.81,D3=146.83,E3=164.81,
       F3=174.61,G3=196.00,A3=220.00,B3=246.94,C4=261.63,D4=293.66,E4=329.63,
       F4=349.23,G4=392.00,A4=440.00,B4=493.88,C5=523.25,D5=587.33,E5=659.25)

# progressão I-V-vi-IV em Dó: C, G, Am, F
CHORDS=[("C3",["C4","E4","G4","C5"]),
        ("G2",["G3","B3","D4","G4"]),
        ("A2",["A3","C4","E4","A4"]),
        ("F2",["F3","A3","C4","F4"])]
MELODY=[ # por compasso: (nota, batidas)
   [("E5",1),("G4",1),("C5",1),("E5",1)],
   [("D5",1),("B4",1),("G4",1),("D5",1)],
   [("C5",1),("E5",1),("A4",1),("C5",1)],
   [("A4",1),("F4",1),("C5",2)],
]

def env(n, a=0.01, d=0.2, s=0.6, r=0.1, sus=0.7):
    t=np.linspace(0,1,n); e=np.ones(n)
    ai=int(a*n); di=int(d*n); ri=int(r*n)
    if ai>0: e[:ai]=np.linspace(0,1,ai)
    if di>0: e[ai:ai+di]=np.linspace(1,sus,di)
    e[ai+di:n-ri]=sus
    if ri>0: e[n-ri:]=np.linspace(sus,0,ri)
    return e

def tone(freq, dur, harm=(1,0.5,0.25), pluck=True):
    n=int(dur*SR); t=np.arange(n)/SR; w=np.zeros(n)
    for i,amp in enumerate(harm,1):
        w+=amp*np.sin(2*np.pi*freq*i*t)
    if pluck:
        e=np.exp(-3.5*np.linspace(0,1,n))*env(n,0.005,0.05,0.5,0.2,0.6)
    else:
        e=env(n,0.05,0.1,0.7,0.25,0.75)
    return w*e

def kick(dur=0.18):
    n=int(dur*SR); t=np.arange(n)/SR
    f=110*np.exp(-18*t)+45
    w=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-9*t)
    return w*0.9

def hat(dur=0.05):
    n=int(dur*SR); w=(np.random.rand(n)*2-1)*np.exp(-40*np.linspace(0,1,n))
    return w*0.25

total=int(DUR*SR)
L=np.zeros(total); R=np.zeros(total)
def add(buf, wave_arr, start, gain=1.0, pan=0.0):
    s=int(start*SR); e=min(total,s+len(wave_arr))
    if s>=total: return
    seg=wave_arr[:e-s]
    L[s:e]+=seg*gain*(1-max(0,pan)); R[s:e]+=seg*gain*(1+min(0,pan))

bar=0; t=0.0
while t<DUR:
    root,chord=CHORDS[bar%4]; mel=MELODY[bar%4]
    # pad (acorde sustentado, suave)
    for note in chord:
        add(L, tone(N[note],BEAT*4,(1,0.4,0.15),False)*0.06, t)
        add(R, tone(N[note],BEAT*4,(1,0.4,0.15),False)*0.06, t)
    # baixo (raiz por batida)
    for b in range(4):
        add(L, tone(N[root],BEAT*0.9,(1,0.3),True)*0.22, t+b*BEAT, pan=-0.05)
        add(R, tone(N[root],BEAT*0.9,(1,0.3),True)*0.22, t+b*BEAT, pan=-0.05)
    # arpejo (colcheias)
    for i in range(8):
        note=chord[i%len(chord)]
        add(L, tone(N[note],BEAT*0.5,(1,0.5,0.25),True)*0.10, t+i*BEAT*0.5, pan=0.2)
        add(R, tone(N[note],BEAT*0.5,(1,0.5,0.25),True)*0.10, t+i*BEAT*0.5, pan=-0.2)
    # melodia
    tb=t
    for note,beats in mel:
        w=tone(N[note],BEAT*beats*0.95,(1,0.6,0.3,0.15),True)*0.16
        add(L,w,tb); add(R,w,tb); tb+=BEAT*beats
    # bateria
    for b in range(4):
        if b in (0,2): add(L,kick(),t+b*BEAT); add(R,kick(),t+b*BEAT)
        add(L,hat(),t+b*BEAT+BEAT*0.5); add(R,hat(),t+b*BEAT+BEAT*0.5)
    t+=BEAT*4; bar+=1

# fade in/out global
fi=int(1.2*SR); fo=int(2.5*SR)
for buf in (L,R):
    buf[:fi]*=np.linspace(0,1,fi); buf[-fo:]*=np.linspace(1,0,fo)

# normaliza (deixa de fundo, pico ~0.5)
peak=max(np.abs(L).max(),np.abs(R).max(),1e-6)
g=0.5/peak; L*=g; R*=g
inter=np.empty(total*2); inter[0::2]=L; inter[1::2]=R
data=(np.clip(inter,-1,1)*32767).astype(np.int16)

with wave.open("musica.wav","w") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(data.tobytes())
print("OK - musica.wav", round(DUR,1),"s")
