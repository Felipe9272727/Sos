# -*- coding: utf-8 -*-
"""Renderiza um MP4 animado (Full HD) sobre o Frisbee, quadro a quadro com PIL."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

W, H = 1920, 1080
FPS = 30
SS = 2  # supersample para bordas suaves

# ---- cores ----
NAVY=(18,42,71); NAVY2=(28,61,99); ORANGE=(255,107,44); ORANGE2=(255,140,66)
YELLOW=(255,196,61); TEAL=(31,182,166); CREME=(251,244,230); CREME2=(244,231,206)
GREEN=(53,158,90); GREEN2=(39,122,69); WHITE=(255,255,255); INK=(26,36,51)

FB="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FR="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
_fc={}
def font(size, bold=True):
    k=(size,bold)
    if k not in _fc: _fc[k]=ImageFont.truetype(FB if bold else FR, size)
    return _fc[k]

# =========================================================
#  Builders de imagens (RGBA), desenhados em 2x e reduzidos
# =========================================================
def _canvas(w,h):
    im=Image.new("RGBA",(w*SS,h*SS),(0,0,0,0))
    return im, ImageDraw.Draw(im)
def _fin(im,w,h):
    return im.resize((w,h),Image.LANCZOS)

def rrect_img(w,h,color,radius=24,top_color=None,top_h=0):
    im,d=_canvas(w,h); r=radius*SS
    d.rounded_rectangle([0,0,w*SS-1,h*SS-1],r,fill=color)
    if top_color and top_h:
        th=top_h*SS
        d.rounded_rectangle([0,0,w*SS-1,th],r,fill=top_color)
        d.rectangle([0,th-r,w*SS-1,th],fill=top_color)
    return _fin(im,w,h)

def circle_img(d,color):
    im,dr=_canvas(d,d)
    dr.ellipse([0,0,d*SS-1,d*SS-1],fill=color)
    return _fin(im,d,d)

def text_img(text,size,color,bold=True,align="left",max_w=None,line_h=1.28):
    f=font(size*SS,bold)
    lines=[]
    for para in text.split("\n"):
        if max_w is None:
            lines.append(para); continue
        words=para.split(" "); cur=""
        for wd in words:
            t=(cur+" "+wd).strip()
            if f.getlength(t)<=max_w*SS or not cur: cur=t
            else: lines.append(cur); cur=wd
        lines.append(cur)
    lh=int(size*SS*line_h)
    measured=max((int(f.getlength(l)) for l in lines),default=1)
    Wd=(max_w*SS if max_w else measured)
    Ht=lh*len(lines)+int(size*SS*0.4)
    im=Image.new("RGBA",(Wd+4,Ht+4),(0,0,0,0)); d=ImageDraw.Draw(im)
    y=0
    for l in lines:
        lw=f.getlength(l)
        x=0
        if align=="center": x=(Wd-lw)/2
        elif align=="right": x=Wd-lw
        d.text((x,y),l,font=f,fill=color); y+=lh
    return _fin(im,(Wd+4)//SS,(Ht+4)//SS)

def disc_img(d,colors=(ORANGE,YELLOW,ORANGE)):
    pad=int(d*0.10); S=(d+2*pad)
    im,dr=_canvas(S,S); c1,c2,c3=colors; s=SS
    P=pad*s; D=d*s; cx=cy=S*s/2
    dr.ellipse([P,P,P+D,P+D],fill=c1)
    g=int(D*0.16); dr.ellipse([P+g,P+g,P+D-g,P+D-g],fill=c2)
    r0,r1=D*0.20,D*0.42
    lw=max(2,int(D*0.022))
    for k in range(8):
        a=math.radians(k*45)
        dr.line([cx+r0*math.cos(a),cy+r0*math.sin(a),
                 cx+r1*math.cos(a),cy+r1*math.sin(a)],fill=c1,width=lw)
    g2=int(D*0.40); dr.ellipse([P+g2,P+g2,P+D-g2,P+D-g2],fill=c3)
    # marcador (assimetria p/ o giro aparecer)
    mk=D*0.05
    dr.ellipse([cx-mk,P+D*0.12,cx+mk,P+D*0.12+2*mk],fill=c2)
    return _fin(im,S,S)

def player_img(h,color):
    w=int(h*0.55)
    im,d=_canvas(w,h); s=SS
    hd=int(h*0.32*s)
    d.ellipse([(w*s-hd)//2,0,(w*s-hd)//2+hd,hd],fill=color)
    d.rounded_rectangle([0,int(h*0.34*s),w*s-1,h*s-1],int(h*0.12*s),fill=color)
    return _fin(im,w,h)

def field_img(w,h):
    im,d=_canvas(w,h); s=SS; ez=int(w*0.18)
    d.rounded_rectangle([0,0,w*s-1,h*s-1],14*s,fill=GREEN)
    d.rectangle([0,0,ez*s,h*s],fill=GREEN2)
    d.rectangle([(w-ez)*s,0,w*s,h*s],fill=GREEN2)
    d.rectangle([ez*s-2,0,ez*s+2,h*s],fill=WHITE)
    d.rectangle([(w-ez)*s-2,0,(w-ez)*s+2,h*s],fill=WHITE)
    y=10*s
    while y<h*s-10*s:
        d.rectangle([w*s//2-2,y,w*s//2+2,y+14*s],fill=WHITE); y+=28*s
    fnt=font(int(20*s),True)
    for cx in (ez*s//2,(w-ez//2)*s):
        for i,t in enumerate(["ÁREA","DE GOL"]):
            tw=fnt.getlength(t); d.text((cx-tw/2,h*s/2-22*s+i*24*s),t,font=fnt,fill=WHITE)
    fnt2=font(int(26*s),True); t="CAMPO CENTRAL"; tw=fnt2.getlength(t)
    d.text((w*s/2-tw/2,h*s-50*s),t,font=fnt2,fill=WHITE)
    return _fin(im,w,h)

# =========================================================
#  Motor de cena
# =========================================================
def ease_out_cubic(p): return 1-(1-p)**3
def ease_out_back(p):
    c1=1.70158; c3=c1+1
    return 1+c3*(p-1)**3+c1*(p-1)**2

class Item:
    def __init__(self,img,x,y,enter="fade",delay=0.0,dur=0.6,spin=0.0):
        self.img=img.convert("RGBA"); self.x=x; self.y=y
        self.enter=enter; self.delay=delay; self.dur=dur; self.spin=spin
        self.end=delay+dur

class Slide:
    def __init__(self,bg_color,blobs=None):
        base=Image.new("RGB",(W,H),bg_color)
        if blobs:
            ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
            for (x,y,dd,col) in blobs:
                d.ellipse([x,y,x+dd,y+dd],fill=col)
            base=Image.alpha_composite(base.convert("RGBA"),ov).convert("RGB")
        self.bg=base; self.items=[]
    def add(self,*a,**k):
        it=Item(*a,**k); self.items.append(it); return it
    def duration(self):
        return max((it.end for it in self.items),default=1.0)+2.6
    def frame(self,t):
        fr=self.bg.copy()
        for it in self.items:
            if t<it.delay and it.spin==0: continue
            p=max(0.0,min(1.0,(t-it.delay)/it.dur))
            im=it.img; offx=offy=0; alpha=1.0; scale=1.0
            if it.enter=="fade":
                alpha=ease_out_cubic(p)
            elif it.enter in("flyL","flyR","flyT","flyB"):
                e=ease_out_cubic(p); alpha=min(1.0,p*3)
                if it.enter=="flyL": offx=int(-(1-e)*W*1.15)
                if it.enter=="flyR": offx=int((1-e)*W*1.15)
                if it.enter=="flyT": offy=int(-(1-e)*H*1.15)
                if it.enter=="flyB": offy=int((1-e)*H*1.15)
            elif it.enter=="grow":
                e=ease_out_back(max(0.0,p)); scale=max(0.05,0.2+0.8*e); alpha=min(1.0,p*3)
            if it.spin and t>=it.delay:
                ang=-(t-it.delay)*it.spin
                im=im.rotate(ang,resample=Image.BICUBIC,expand=False)
            w0,h0=im.size
            if scale!=1.0:
                w1,h1=max(1,int(w0*scale)),max(1,int(h0*scale))
                im=im.resize((w1,h1),Image.LANCZOS)
            else: w1,h1=w0,h0
            if alpha<0.999:
                a=im.split()[3].point(lambda v:int(v*alpha)); im=im.copy(); im.putalpha(a)
            px=it.x+(w0-w1)//2+offx; py=it.y+(h0-h1)//2+offy
            fr.paste(im,(px,py),im)
        return fr

# =========================================================
#  Montagem dos slides
# =========================================================
slides=[]

def header(sl,num,title,accent,delay=0.1):
    c=circle_img(110,accent); n=text_img(str(num),60,WHITE,True)
    sl.add(c,70,55,"flyL",delay,0.55)
    sl.add(n,70+ (110-n.width)//2, 55+(110-n.height)//2,"flyL",delay,0.55)
    sl.add(text_img(title,66,NAVY,True),210,72,"flyL",delay,0.55)
    sl.add(rrect_img(330,8,accent,4),212,180,"flyL",delay,0.55)

# ---- SLIDE 1 CAPA ----
s=Slide(NAVY,[(-230,-230,640,NAVY2),(W-460,H-460,720,TEAL)])
s.add(rrect_img(W,250,ORANGE,0),0,455,"flyL",0.0,0.7)
s.add(disc_img(360),W-560,90,"flyR",0.0,0.85,spin=150)
s.add(text_img("FRISBEE",230,WHITE,True),100,430,"flyB",0.2,0.7)
s.add(text_img("O esporte do disco — origem, regras e curiosidades",40,YELLOW,True),105,735,"flyL",0.5,0.6)
s.add(text_img("Nicolas      Felipe      André      Lucas      Ruan",36,WHITE,True),105,895,"fade",0.8,0.6)
slides.append(s)

# ---- SLIDE 2 O QUE É ----
s=Slide(CREME)
header(s,1,"O que é o Frisbee?",ORANGE)
s.add(text_img("É um esporte coletivo jogado com um disco de plástico. O objetivo é levar "
    "o disco até a área de pontuação do adversário usando apenas passes — ninguém pode "
    "correr segurando o disco.",34,INK,False,"left",max_w=980),96,300,"fade",0.4,0.6)
s.add(player_img(300,TEAL),1300,330,"flyB",0.6,0.6)
s.add(player_img(300,NAVY2),1620,330,"flyB",0.6,0.6)
s.add(disc_img(150),1455,360,"grow",0.9,0.5,spin=140)
cards=[("7 x 7","jogadores em\ncada equipe",ORANGE),
       ("ZONA","receber o disco\nna área de gol",TEAL),
       ("FAIR","os jogadores\nresolvem as faltas",(202,161,42))]
x=96
for i,(big,small,col) in enumerate(cards):
    card=rrect_img(540,300,WHITE,22,top_color=col,top_h=16)
    cd=ImageDraw.Draw(card)
    f1=font(48,True); tw=f1.getlength(big); cd.text(((540-tw)/2,55),big,font=f1,fill=col)
    f2=font(24,False)
    for j,ln in enumerate(small.split("\n")):
        tw=f2.getlength(ln); cd.text(((540-tw)/2,150+j*34),ln,font=f2,fill=INK)
    s.add(card,x,640,"flyB",0.9+i*0.18,0.55)
    x+=580
slides.append(s)

# ---- SLIDE 3 ORIGEM ----
s=Slide(CREME)
header(s,2,"Origem e história",TEAL)
s.add(text_img("Começou como brincadeira universitária nos Estados Unidos e virou um "
    "esporte competitivo praticado em vários países.",32,INK,False,"left",max_w=1720),96,290,"fade",0.4,0.6)
box=rrect_img(1728,470,NAVY,22)
bd=ImageDraw.Draw(box)
bd.rounded_rectangle([0,0,30,470],8,fill=ORANGE)
ft=font(46,True); bd.text((75,40),"De onde vem o nome \"Frisbee\"?",font=ft,fill=YELLOW)
corpo=("Ele se inspirou em formas antigas de arremessar discos, mas ficou famoso nos "
    "EUA nos anos 1940. O nome veio da empresa de tortas \"Frisbie Pie Company\": os "
    "estudantes jogavam as formas de torta vazias gritando \"Frisbie!\". Depois, a "
    "empresa Wham-O criou o disco de plástico moderno e mudou a escrita para \"Frisbee\".")
fb=font(31,False); words=corpo.split(" "); line=""; yy=130
for wd in words:
    if fb.getlength((line+" "+wd).strip())<=1560 or not line: line=(line+" "+wd).strip()
    else: bd.text((75,yy),line,font=fb,fill=WHITE); yy+=46; line=wd
bd.text((75,yy),line,font=fb,fill=WHITE)
s.add(box,96,470,"flyR",0.5,0.7)
slides.append(s)

# ---- SLIDE 4 CAMPO ----
s=Slide(CREME)
header(s,3,"O campo de jogo",GREEN)
s.add(field_img(1540,500),190,300,"grow",0.4,0.6)
s.add(disc_img(110),960-55,550-55,"flyT",0.9,0.6,spin=160)
s.add(text_img("Pode ser jogado em grama, areia ou quadras adaptadas. Pontua-se quando "
    "um jogador recebe o disco dentro da área de gol adversária.",28,INK,False,"center",max_w=1540),
    190,840,"fade",1.2,0.6)
slides.append(s)

# ---- SLIDE 5 REGRAS ----
s=Slide(CREME)
header(s,4,"Regras básicas",ORANGE)
regras=["O objetivo é chegar à área de pontuação do adversário recebendo o disco.",
    "Quem está com o disco NÃO pode correr — só pode passar.",
    "Cada equipe joga normalmente com 7 jogadores em campo.",
    "O disco passa para o outro time se cair no chão ou for interceptado.",
    "Pontua-se quando um jogador recebe o disco na área de gol adversária.",
    "Não é permitido contato físico forte entre os jogadores."]
y=300
for i,t in enumerate(regras):
    col=ORANGE if i%2==0 else TEAL
    row=Image.new("RGBA",(1700,90),(0,0,0,0)); d=ImageDraw.Draw(row)
    d.ellipse([0,8,74,82],fill=col)
    f=font(38,True); nn=str(i+1); tw=f.getlength(nn); d.text((37-tw/2,20),nn,font=f,fill=WHITE)
    f2=font(34,False); d.text((110,22),t,font=f2,fill=INK)
    s.add(row,110,y,"flyL",0.3+i*0.16,0.5)
    y+=120
slides.append(s)

# ---- SLIDE 6 COMO ACONTECE ----
s=Slide(CREME)
header(s,5,"Como o jogo acontece",TEAL)
itens=["O jogo começa com um lançamento chamado \"pull\" (como a saída do futebol).",
    "Quem está com o disco tem cerca de 10 segundos para passar.",
    "Se o disco sair do campo, a posse vai para o outro time.",
    "Após cada ponto, os times trocam de lado no campo.",
    "As substituições acontecem normalmente após um ponto.",
    "Se dois jogadores pegam o disco ao mesmo tempo, a posse fica com o ataque.",
    "Vence quem chega primeiro à pontuação combinada (geralmente 15 pontos)."]
y=290
for i,t in enumerate(itens):
    row=Image.new("RGBA",(1700,80),(0,0,0,0)); d=ImageDraw.Draw(row)
    d.ellipse([0,22,36,58],fill=ORANGE)
    f2=font(32,False); d.text((70,18),t,font=f2,fill=INK)
    s.add(row,110,y,"flyR",0.3+i*0.14,0.45)
    y+=102
slides.append(s)

# ---- SLIDE 7 ESPÍRITO ----
s=Slide(NAVY,[(W-520,-200,720,NAVY2),(-230,H-430,640,ORANGE)])
s.add(disc_img(280),W//2-140,110,"flyT",0.3,0.7,spin=120)
s.add(text_img("O Espírito do Jogo",80,YELLOW,True,"center",max_w=1400),260,430,"grow",0.7,0.6)
s.add(text_img("O Frisbee não tem árbitros na maioria das partidas: os próprios "
    "jogadores resolvem as faltas.",42,WHITE,False,"center",max_w=1300),310,600,"fade",1.1,0.6)
s.add(text_img("Por isso o esporte valoriza o respeito, a honestidade e o fair play.",
    38,YELLOW,True,"center",max_w=1300),310,800,"flyB",1.4,0.6)
slides.append(s)

# ---- SLIDE 8 MODALIDADES ----
s=Slide(CREME)
header(s,6,"Modalidades do Frisbee",ORANGE)
mods=[("Ultimate","Jogo coletivo de passes entre duas equipes. É o mais popular de todos.",ORANGE,(ORANGE,YELLOW,ORANGE)),
      ("Disc Golf","Como o golfe, mas o disco é arremessado em direção a uma cesta.",TEAL,None),
      ("Freestyle","Manobras, truques e acrobacias feitas com o disco no ar.",YELLOW,(NAVY,TEAL,NAVY))]
x=96
for i,(tit,desc,col,dcol) in enumerate(mods):
    card=rrect_img(540,640,WHITE,22,top_color=col,top_h=200)
    cd=ImageDraw.Draw(card)
    f1=font(40,True); tw=f1.getlength(tit); cd.text(((540-tw)/2,230),tit,font=f1,fill=NAVY)
    fb2=font(26,False); words=desc.split(" "); line=""; yy=320
    for wd in words:
        if fb2.getlength((line+" "+wd).strip())<=460 or not line: line=(line+" "+wd).strip()
        else:
            tw=fb2.getlength(line); cd.text(((540-tw)/2,yy),line,font=fb2,fill=INK); yy+=38; line=wd
    tw=fb2.getlength(line); cd.text(((540-tw)/2,yy),line,font=fb2,fill=INK)
    if dcol is None:  # cesta de disc golf desenhada
        cd.rectangle([268,70,278,180],fill=NAVY)
        cd.polygon([(220,70),(320,70),(345,120),(195,120)],fill=YELLOW)
    s.add(card,x,290,"flyB",0.35+i*0.2,0.55)
    if dcol is not None:
        s.add(disc_img(150),x+195,310,"grow",0.55+i*0.2,0.5,spin=150)
    x+=580
slides.append(s)

# ---- SLIDE 9 CURIOSIDADES ----
s=Slide(CREME)
header(s,7,"Curiosidades",TEAL)
curi=[("100 km/h","O disco pode ultrapassar essa velocidade num bom lançamento."),
      ("15 pts","Em jogos oficiais, costuma-se jogar até 15 pontos."),
      ("MUNDO","Existe campeonato mundial e o esporte é jogado em vários países."),
      ("DOGS","Cachorros também competem em provas com o disco!")]
y=300
for i,(big,txt) in enumerate(curi):
    row=rrect_img(1720,130,WHITE,18)
    d=ImageDraw.Draw(row)
    d.rounded_rectangle([28,28,330,102],14,fill=NAVY)
    f=font(36,True); tw=f.getlength(big); d.text((179-tw/2,46),big,font=f,fill=YELLOW)
    f2=font(32,False); d.text((380,42),txt,font=f2,fill=INK)
    s.add(row,96,y,"flyR",0.3+i*0.18,0.5)
    y+=160
slides.append(s)

# ---- SLIDE 10 FIM ----
s=Slide(NAVY)
s.add(rrect_img(W,280,ORANGE,0),0,400,"flyR",0.2,0.7)
s.add(disc_img(300),W//2-150,90,"flyT",0.3,0.7,spin=140)
s.add(text_img("Obrigado!",150,WHITE,True,"center",max_w=1600),160,420,"grow",0.7,0.7)
s.add(text_img("Nicolas      Felipe      André      Lucas      Ruan",40,YELLOW,True,"center",max_w=1600),
    160,760,"fade",1.1,0.6)
slides.append(s)

# =========================================================
#  Render
# =========================================================
def main():
    out="Frisbee.mp4"
    wr=imageio.get_writer(out,fps=FPS,codec="libx264",quality=8,
                          macro_block_size=8,output_params=["-pix_fmt","yuv420p"])
    total_frames=0
    # fade-in inicial a partir do preto
    first=slides[0].frame(0.0)
    for k in range(10):
        a=k/10; fr=Image.blend(Image.new("RGB",(W,H),(0,0,0)),first,a)
        wr.append_data(np.asarray(fr)); total_frames+=1
    CF=10  # frames de crossfade
    for si,sl in enumerate(slides):
        dur=sl.duration(); nf=int(dur*FPS)
        for f in range(nf):
            t=f/FPS
            wr.append_data(np.asarray(sl.frame(t))); total_frames+=1
        if si<len(slides)-1:
            last=sl.frame((nf-1)/FPS); nxt=slides[si+1].frame(0.0)
            for k in range(1,CF+1):
                fr=Image.blend(last,nxt,k/(CF+1))
                wr.append_data(np.asarray(fr)); total_frames+=1
    # fade-out final
    last=slides[-1].frame(slides[-1].duration())
    for k in range(12):
        a=1-(k/12); fr=Image.blend(Image.new("RGB",(W,H),(0,0,0)),last,a)
        wr.append_data(np.asarray(fr)); total_frames+=1
    wr.close()
    print("OK -",total_frames,"frames ~", round(total_frames/FPS,1),"s")

if __name__=="__main__":
    main()
