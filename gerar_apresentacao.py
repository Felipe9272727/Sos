# -*- coding: utf-8 -*-
"""Apresentacao .pptx sobre o Frisbee — estilo flat/Canva, ilustracoes desenhadas
e animacoes reais (movimento, giro, deslize)."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

# ---- Paleta (estilo Canva esportivo) ----
NAVY      = RGBColor(0x12, 0x2A, 0x47)
NAVY2     = RGBColor(0x1C, 0x3D, 0x63)
LARANJA   = RGBColor(0xFF, 0x6B, 0x2C)
LARANJA2  = RGBColor(0xFF, 0x8C, 0x42)
AMARELO   = RGBColor(0xFF, 0xC4, 0x3D)
TEAL      = RGBColor(0x1F, 0xB6, 0xA6)
CREME     = RGBColor(0xFB, 0xF4, 0xE6)
CREME2    = RGBColor(0xF4, 0xE7, 0xCE)
VERDE     = RGBColor(0x35, 0x9E, 0x5A)
VERDE_ESC = RGBColor(0x27, 0x7A, 0x45)
BRANCO    = RGBColor(0xFF, 0xFF, 0xFF)
TINTA     = RGBColor(0x1A, 0x24, 0x33)

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
LARG, ALT = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

# =========================================================
#  Helpers de formas
# =========================================================
def _fmt(s, cor, linha=None, lw=None):
    s.fill.solid(); s.fill.fore_color.rgb = cor
    if linha is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = linha; s.line.width = lw or Pt(1.5)
    s.shadow.inherit = False
    return s

def fundo(slide, cor):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, LARG, ALT)
    _fmt(s, cor)
    slide.shapes._spTree.remove(s._element)
    slide.shapes._spTree.insert(2, s._element)
    return s

def rect(slide, x, y, w, h, cor, shape=MSO_SHAPE.RECTANGLE, linha=None, lw=None):
    return _fmt(slide.shapes.add_shape(shape, x, y, w, h), cor, linha, lw)

def oval(slide, x, y, w, h, cor, linha=None, lw=None):
    return _fmt(slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h), cor, linha, lw)

def texto(slide, x, y, w, h, t, tam=20, cor=TINTA, bold=False,
          align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, fonte="Calibri", espac=None):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for i, linha in enumerate(t.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if espac: p.space_after = Pt(espac)
        r = p.add_run(); r.text = linha
        r.font.size = Pt(tam); r.font.bold = bold
        r.font.color.rgb = cor; r.font.name = fonte
    return tb

# ---- Ilustracao: disco voador (vista de cima, em aneis) ----
def disco(slide, x, y, d, cores=(LARANJA, AMARELO, LARANJA)):
    c1, c2, c3 = cores
    s1 = oval(slide, x, y, d, d, c1)
    g = int(d * 0.16)
    s2 = oval(slide, x+g, y+g, d-2*g, d-2*g, c2)
    g2 = int(d * 0.36)
    s3 = oval(slide, x+g2, y+g2, d-2*g2, d-2*g2, c3)
    return [s1, s2, s3]

# ---- Ilustracao: jogador simples (flat) ----
def jogador(slide, x, y, h, cor):
    cabeca_d = int(h * 0.32)
    cab = oval(slide, x + (int(h*0.5)-cabeca_d)//2, y, cabeca_d, cabeca_d, cor)
    corpo = rect(slide, x, y+int(h*0.34), int(h*0.5), int(h*0.66),
                 cor, MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
    return [cab, corpo]

# =========================================================
#  Motor de animacao real (movimento / giro / crescer)
# =========================================================
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

def _set_visivel(spid, nid):
    return (f'<p:set><p:cBhvr><p:cTn id="{nid}" dur="1" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'), nid+1

def _comportamentos(kind, spid, nid, dur):
    out = []
    if kind != "spin":
        xml, nid = _set_visivel(spid, nid); out.append(xml)
    if kind.startswith("fly"):
        path = {"flyL": "M -1.3 0 L 0 0 E", "flyR": "M 1.3 0 L 0 0 E",
                "flyT": "M 0 -1.3 L 0 0 E", "flyB": "M 0 1.3 L 0 0 E"}[kind]
        out.append(f'<p:animMotion origin="layout" path="{path}" pathEditMode="relative">'
                   f'<p:cBhvr><p:cTn id="{nid}" dur="{dur}" fill="hold"/>'
                   f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
                   f'<p:attrNameLst><p:attrName>ppt_x</p:attrName>'
                   f'<p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr></p:animMotion>')
        nid += 1
    elif kind == "grow":
        out.append(f'<p:animScale><p:cBhvr><p:cTn id="{nid}" dur="{dur}" fill="hold"/>'
                   f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr>'
                   f'<p:from x="0" y="0"/><p:to x="100000" y="100000"/></p:animScale>')
        nid += 1
        out.append(f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
                   f'<p:cTn id="{nid}" dur="{dur}"/><p:tgtEl><p:spTgt spid="{spid}"/>'
                   f'</p:tgtEl></p:cBhvr></p:animEffect>')
        nid += 1
    elif kind == "fade":
        out.append(f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
                   f'<p:cTn id="{nid}" dur="{dur}"/><p:tgtEl><p:spTgt spid="{spid}"/>'
                   f'</p:tgtEl></p:cBhvr></p:animEffect>')
        nid += 1
    elif kind == "spin":
        voltas = 21600000  # 360 graus
        out.append(f'<p:animRot by="{voltas}"><p:cBhvr><p:cTn id="{nid}" dur="{dur}" '
                   f'fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
                   f'<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst>'
                   f'</p:cBhvr></p:animRot>')
        nid += 1
    return "".join(out), nid

_PRESET = {"flyL": (2, "entr"), "flyR": (2, "entr"), "flyT": (2, "entr"),
           "flyB": (2, "entr"), "grow": (23, "entr"), "fade": (10, "entr"),
           "spin": (8, "emph")}

def animar(slide, passos):
    """passos = lista de dicts: {shapes:[..], kind:'flyL'|'flyR'|'flyT'|'flyB'|
       'grow'|'fade'|'spin', start:'after'|'with', delay:ms, dur:ms}"""
    nid = 3
    pares = []
    for p in passos:
        a, b, c = nid, nid+1, nid+2; nid += 3
        kind = p["kind"]
        pid, pclass = _PRESET[kind]
        node = "withEffect" if p.get("start") == "with" else "afterEffect"
        delay = p.get("delay", 0)
        dur = p.get("dur", 600)
        behs = []
        for sh in p["shapes"]:
            xml, nid = _comportamentos(kind, sh.shape_id, nid, dur)
            behs.append(xml)
        pares.append(
            f'<p:par><p:cTn id="{a}" fill="hold"><p:stCondLst><p:cond delay="{delay}"/>'
            f'</p:stCondLst><p:childTnLst><p:par><p:cTn id="{b}" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par>'
            f'<p:cTn id="{c}" presetID="{pid}" presetClass="{pclass}" presetSubtype="0" '
            f'fill="hold" grpId="0" nodeType="{node}"><p:stCondLst><p:cond delay="0"/>'
            f'</p:stCondLst><p:childTnLst>{"".join(behs)}</p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    timing = (f'<p:timing xmlns:p="{P_NS}" xmlns:a="{A_NS}"><p:tnLst><p:par>'
              f'<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
              f'<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
              f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
              f'{"".join(pares)}</p:childTnLst></p:cTn>'
              f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/>'
              f'</p:tgtEl></p:cond></p:prevCondLst><p:nextCondLst>'
              f'<p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond>'
              f'</p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    slide.element.append(etree.fromstring(timing.encode("utf-8")))

def transicao(slide, tipo="fade", dir_=None):
    d = f' dir="{dir_}"' if dir_ else ""
    el = etree.fromstring(f'<p:transition xmlns:p="{P_NS}" spd="med">'
                          f'<p:{tipo}{d}/></p:transition>'.encode("utf-8"))
    cmap = slide.element.find(qn('p:clrMapOvr'))
    (cmap.addnext(el) if cmap is not None else slide.element.append(el))

# ---- cabecalho de secao reutilizavel (estilo Canva) ----
def cabecalho(slide, num, titulo, cor_blob=LARANJA):
    blob = rect(slide, Inches(0.6), Inches(0.55), Inches(1.0), Inches(1.0),
                cor_blob, MSO_SHAPE.OVAL)
    n = texto(slide, Inches(0.6), Inches(0.55), Inches(1.0), Inches(1.0), str(num),
              tam=34, cor=BRANCO, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    t = texto(slide, Inches(1.8), Inches(0.55), Inches(10.8), Inches(1.0), titulo,
              tam=36, cor=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    linha = rect(slide, Inches(1.85), Inches(1.65), Inches(2.6), Pt(5), LARANJA)
    return [blob, n, t, linha]

# =========================================================
# SLIDE 1 — CAPA
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, NAVY)
# blobs decorativos
b1 = rect(s, Inches(-1.6), Inches(-1.6), Inches(4.5), Inches(4.5), NAVY2, MSO_SHAPE.OVAL)
b2 = rect(s, LARG-Inches(3.2), ALT-Inches(3.2), Inches(5), Inches(5), TEAL, MSO_SHAPE.OVAL)
faixa = rect(s, 0, Inches(3.05), LARG, Inches(1.7), LARANJA)
d = disco(s, Inches(9.2), Inches(0.7), Inches(2.6))
tit = texto(s, Inches(0.9), Inches(3.1), Inches(11.5), Inches(1.6), "FRISBEE",
            tam=88, cor=BRANCO, bold=True)
sub = texto(s, Inches(0.95), Inches(4.95), Inches(11.5), Inches(0.7),
            "O esporte do disco — origem, regras e curiosidades", tam=22, cor=AMARELO)
nomes = texto(s, Inches(0.95), Inches(6.25), Inches(11.5), Inches(0.7),
              "Nicolas    Felipe    André    Lucas    Ruan", tam=20, cor=BRANCO, bold=True)
animar(s, [
    {"shapes": [b1, b2], "kind": "fade", "delay": 100, "dur": 500},
    {"shapes": [faixa], "kind": "flyL", "delay": 0, "dur": 600},
    {"shapes": d, "kind": "flyR", "delay": 0, "dur": 700},
    {"shapes": d, "kind": "spin", "start": "with", "delay": 0, "dur": 1400},
    {"shapes": [tit], "kind": "flyB", "delay": 100, "dur": 600},
    {"shapes": [sub], "kind": "flyL", "delay": 100, "dur": 500},
    {"shapes": [nomes], "kind": "fade", "delay": 100, "dur": 500},
])
transicao(s, "fade")

# =========================================================
# SLIDE 2 — O QUE É
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CREME)
cab = cabecalho(s, 1, "O que é o Frisbee?")
desc = texto(s, Inches(0.7), Inches(2.0), Inches(7.0), Inches(2.2),
             "É um esporte coletivo jogado com um disco de plástico. O objetivo é levar "
             "o disco até a área de pontuação do adversário usando apenas passes — "
             "ninguém pode correr segurando o disco.", tam=22, cor=TINTA)
# ilustracao: dois jogadores trocando o disco
j1 = jogador(s, Inches(8.6), Inches(2.3), Inches(2.4), TEAL)
j2 = jogador(s, Inches(11.0), Inches(2.3), Inches(2.4), NAVY2)
dd = disco(s, Inches(10.0), Inches(2.35), Inches(1.2))
# tres cartoes
infos = [("7 x 7", "jogadores em\ncada equipe", LARANJA),
         ("ZONA", "receber o disco\nna área de gol", TEAL),
         ("FAIR", "os jogadores\nresolvem as faltas", AMARELO)]
cards = []
x = Inches(0.7)
for big, small, cor in infos:
    card = rect(s, x, Inches(4.55), Inches(3.8), Inches(2.3), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(s, x, Inches(4.55), Inches(3.8), Inches(0.22), cor, MSO_SHAPE.ROUNDED_RECTANGLE)
    texto(s, x, Inches(4.85), Inches(3.8), Inches(0.9), big, tam=34, cor=cor,
          bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    texto(s, x, Inches(5.75), Inches(3.8), Inches(1.0), small, tam=17, cor=TINTA,
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)
    cards.append(card)
    x += Inches(4.0)
animar(s, [
    {"shapes": cab, "kind": "flyL", "delay": 100, "dur": 500},
    {"shapes": [desc], "kind": "fade", "delay": 100, "dur": 500},
    {"shapes": j1+j2, "kind": "flyB", "delay": 100, "dur": 500},
    {"shapes": dd, "kind": "grow", "delay": 100, "dur": 400},
    {"shapes": dd, "kind": "spin", "start": "with", "delay": 0, "dur": 1200},
    {"shapes": [cards[0]], "kind": "flyB", "delay": 150, "dur": 450},
    {"shapes": [cards[1]], "kind": "flyB", "delay": 150, "dur": 450},
    {"shapes": [cards[2]], "kind": "flyB", "delay": 150, "dur": 450},
])
transicao(s, "push", "l")

# =========================================================
# SLIDE 3 — ORIGEM E HISTÓRIA
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CREME)
cab = cabecalho(s, 2, "Origem e história", TEAL)
intro = texto(s, Inches(0.7), Inches(1.95), Inches(11.9), Inches(1.0),
              "Começou como brincadeira universitária nos Estados Unidos e virou um "
              "esporte competitivo praticado em vários países.", tam=21, cor=TINTA)
box = rect(s, Inches(0.7), Inches(3.2), Inches(11.9), Inches(3.5), NAVY, MSO_SHAPE.ROUNDED_RECTANGLE)
barra = rect(s, Inches(0.7), Inches(3.2), Inches(0.25), Inches(3.5), LARANJA)
bt = texto(s, Inches(1.2), Inches(3.45), Inches(11.0), Inches(0.7),
           "De onde vem o nome \"Frisbee\"?", tam=26, cor=AMARELO, bold=True)
bx = texto(s, Inches(1.2), Inches(4.25), Inches(11.0), Inches(2.4),
           "Ele se inspirou em formas antigas de arremessar discos, mas ficou famoso "
           "nos EUA nos anos 1940. O nome veio da empresa de tortas \"Frisbie Pie "
           "Company\": os estudantes jogavam as formas de torta vazias gritando "
           "\"Frisbie!\".\n\nDepois, a empresa Wham-O criou o disco de plástico moderno "
           "e mudou a escrita para \"Frisbee\".", tam=19, cor=BRANCO)
animar(s, [
    {"shapes": cab, "kind": "flyL", "delay": 100, "dur": 500},
    {"shapes": [intro], "kind": "fade", "delay": 100, "dur": 500},
    {"shapes": [box, barra], "kind": "flyR", "delay": 100, "dur": 550},
    {"shapes": [bt], "kind": "flyL", "delay": 150, "dur": 450},
    {"shapes": [bx], "kind": "fade", "delay": 150, "dur": 500},
])
transicao(s, "wipe", "r")

# =========================================================
# SLIDE 4 — CAMPO DE JOGO (diagrama desenhado)
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CREME)
cab = cabecalho(s, 3, "O campo de jogo", VERDE)
fx, fy, fw, fh = Inches(1.3), Inches(2.25), Inches(10.7), Inches(3.5)
campo = rect(s, fx, fy, fw, fh, VERDE)
ez = Inches(1.9)
gol1 = rect(s, fx, fy, ez, fh, VERDE_ESC)
gol2 = rect(s, fx+fw-ez, fy, ez, fh, VERDE_ESC)
rect(s, fx+ez, fy, Pt(3), fh, BRANCO)
rect(s, fx+fw-ez, fy, Pt(3), fh, BRANCO)
cx = fx + fw//2
yy = fy + Inches(0.2)
linhas = []
while yy < fy + fh - Inches(0.2):
    linhas.append(rect(s, cx, yy, Pt(3), Inches(0.28), BRANCO))
    yy += Inches(0.5)
dd = disco(s, cx-Inches(0.3), fy+fh//2-Inches(0.3), Inches(0.6))
l1 = texto(s, fx, fy, ez, fh, "ÁREA\nDE GOL", tam=13, cor=BRANCO, bold=True,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
l2 = texto(s, fx+ez, fy, fw-2*ez, fh, "CAMPO CENTRAL", tam=16, cor=BRANCO, bold=True,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
l3 = texto(s, fx+fw-ez, fy, ez, fh, "ÁREA\nDE GOL", tam=13, cor=BRANCO, bold=True,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
nota = texto(s, Inches(1.3), Inches(6.1), Inches(10.7), Inches(0.9),
             "Pode ser jogado em grama, areia ou quadras adaptadas. Pontua-se quando um "
             "jogador recebe o disco dentro da área de gol adversária.", tam=17,
             cor=TINTA, align=PP_ALIGN.CENTER)
animar(s, [
    {"shapes": cab, "kind": "flyL", "delay": 100, "dur": 500},
    {"shapes": [campo], "kind": "grow", "delay": 100, "dur": 500},
    {"shapes": [gol1], "kind": "flyL", "delay": 100, "dur": 400},
    {"shapes": [gol2], "kind": "flyR", "delay": 0, "start": "with", "dur": 400},
    {"shapes": [l1, l2, l3], "kind": "fade", "delay": 100, "dur": 400},
    {"shapes": linhas, "kind": "fade", "delay": 100, "dur": 400},
    {"shapes": dd, "kind": "flyT", "delay": 100, "dur": 500},
    {"shapes": dd, "kind": "spin", "start": "with", "delay": 0, "dur": 1000},
    {"shapes": [nota], "kind": "fade", "delay": 150, "dur": 500},
])
transicao(s, "cover", "d")

# =========================================================
# SLIDE 5 — REGRAS BÁSICAS
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CREME)
cab = cabecalho(s, 4, "Regras básicas")
itens = [
    "O objetivo é chegar à área de pontuação do adversário recebendo o disco.",
    "Quem está com o disco NÃO pode correr — só pode passar.",
    "Cada equipe joga normalmente com 7 jogadores em campo.",
    "O disco passa para o outro time se cair no chão ou for interceptado.",
    "Pontua-se quando um jogador recebe o disco na área de gol adversária.",
    "Não é permitido contato físico forte entre os jogadores.",
]
passos = [{"shapes": cab, "kind": "flyL", "delay": 100, "dur": 500}]
y = Inches(2.0)
for i, it in enumerate(itens):
    badge = rect(s, Inches(0.8), y, Inches(0.62), Inches(0.62), LARANJA if i % 2 == 0 else TEAL,
                 MSO_SHAPE.OVAL)
    num = texto(s, Inches(0.8), y, Inches(0.62), Inches(0.62), str(i+1), tam=22,
                cor=BRANCO, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    t = texto(s, Inches(1.65), y, Inches(10.9), Inches(0.7), it, tam=19, cor=TINTA,
              anchor=MSO_ANCHOR.MIDDLE)
    passos.append({"shapes": [badge, num, t], "kind": "flyL", "delay": 120, "dur": 400})
    y += Inches(0.8)
animar(s, passos)
transicao(s, "push", "l")

# =========================================================
# SLIDE 6 — COMO O JOGO ACONTECE
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CREME)
cab = cabecalho(s, 5, "Como o jogo acontece", TEAL)
itens = [
    "O jogo começa com um lançamento chamado \"pull\" (como a saída do futebol).",
    "Quem está com o disco tem cerca de 10 segundos para passar.",
    "Se o disco sair do campo, a posse vai para o outro time.",
    "Após cada ponto, os times trocam de lado no campo.",
    "As substituições acontecem normalmente após um ponto.",
    "Se dois jogadores pegam o disco ao mesmo tempo, a posse fica com o ataque.",
    "Vence quem chega primeiro à pontuação combinada (geralmente 15 pontos).",
]
passos = [{"shapes": cab, "kind": "flyL", "delay": 100, "dur": 500}]
y = Inches(1.95)
for it in itens:
    dot = rect(s, Inches(0.85), y+Inches(0.05), Inches(0.32), Inches(0.32), LARANJA, MSO_SHAPE.OVAL)
    t = texto(s, Inches(1.4), y, Inches(11.1), Inches(0.6), it, tam=19, cor=TINTA,
              anchor=MSO_ANCHOR.MIDDLE)
    passos.append({"shapes": [dot, t], "kind": "flyR", "delay": 110, "dur": 380})
    y += Inches(0.72)
animar(s, passos)
transicao(s, "wipe", "d")

# =========================================================
# SLIDE 7 — ESPÍRITO DO JOGO
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, NAVY)
b = rect(s, LARG-Inches(3.6), Inches(-1.4), Inches(5), Inches(5), NAVY2, MSO_SHAPE.OVAL)
b2 = rect(s, Inches(-1.6), ALT-Inches(3.0), Inches(4.5), Inches(4.5), LARANJA, MSO_SHAPE.OVAL)
d = disco(s, Inches(5.65), Inches(0.75), Inches(2.0), (AMARELO, LARANJA, AMARELO))
t1 = texto(s, Inches(1), Inches(2.9), Inches(11.3), Inches(1.0), "O Espírito do Jogo",
           tam=44, cor=AMARELO, bold=True, align=PP_ALIGN.CENTER)
t2 = texto(s, Inches(1.6), Inches(4.0), Inches(10.1), Inches(1.6),
           "O Frisbee não tem árbitros na maioria das partidas: os próprios jogadores "
           "resolvem as faltas.", tam=24, cor=BRANCO, align=PP_ALIGN.CENTER)
t3 = texto(s, Inches(1.6), Inches(5.5), Inches(10.1), Inches(1.0),
           "Por isso o esporte valoriza o respeito, a honestidade e o fair play.",
           tam=22, cor=AMARELO, align=PP_ALIGN.CENTER, bold=True)
animar(s, [
    {"shapes": [b, b2], "kind": "fade", "delay": 100, "dur": 500},
    {"shapes": d, "kind": "flyT", "delay": 100, "dur": 600},
    {"shapes": d, "kind": "spin", "start": "with", "delay": 0, "dur": 1600},
    {"shapes": [t1], "kind": "grow", "delay": 150, "dur": 500},
    {"shapes": [t2], "kind": "fade", "delay": 150, "dur": 500},
    {"shapes": [t3], "kind": "flyB", "delay": 150, "dur": 500},
])
transicao(s, "cover", "u")

# =========================================================
# SLIDE 8 — MODALIDADES (icones desenhados)
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CREME)
cab = cabecalho(s, 6, "Modalidades do Frisbee")
cards = []
icones = []
x = Inches(0.7)
# Card 1 - Ultimate (disco + jogador)
c1 = rect(s, x, Inches(2.1), Inches(3.8), Inches(4.4), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
rect(s, x, Inches(2.1), Inches(3.8), Inches(1.5), LARANJA, MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
ic1 = disco(s, x+Inches(1.4), Inches(2.45), Inches(1.0))
texto(s, x, Inches(3.7), Inches(3.8), Inches(0.6), "Ultimate", tam=24, cor=NAVY, bold=True, align=PP_ALIGN.CENTER)
texto(s, x+Inches(0.2), Inches(4.4), Inches(3.4), Inches(2.0),
      "Jogo coletivo de passes entre duas equipes. É o mais popular de todos.",
      tam=17, cor=TINTA, align=PP_ALIGN.CENTER)
# Card 2 - Disc Golf (cesta desenhada)
x2 = x + Inches(4.0)
c2 = rect(s, x2, Inches(2.1), Inches(3.8), Inches(4.4), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
rect(s, x2, Inches(2.1), Inches(3.8), Inches(1.5), TEAL, MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
poste = rect(s, x2+Inches(1.83), Inches(2.45), Pt(6), Inches(0.95), NAVY)
cesta = rect(s, x2+Inches(1.45), Inches(2.55), Inches(0.85), Inches(0.5), AMARELO, MSO_SHAPE.TRAPEZOID)
ic2 = [poste, cesta]
texto(s, x2, Inches(3.7), Inches(3.8), Inches(0.6), "Disc Golf", tam=24, cor=NAVY, bold=True, align=PP_ALIGN.CENTER)
texto(s, x2+Inches(0.2), Inches(4.4), Inches(3.4), Inches(2.0),
      "Como o golfe, mas o disco é arremessado em direção a uma cesta.",
      tam=17, cor=TINTA, align=PP_ALIGN.CENTER)
# Card 3 - Freestyle (disco girando)
x3 = x2 + Inches(4.0)
c3 = rect(s, x3, Inches(2.1), Inches(3.8), Inches(4.4), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
rect(s, x3, Inches(2.1), Inches(3.8), Inches(1.5), AMARELO, MSO_SHAPE.ROUND_2_SAME_RECTANGLE)
ic3 = disco(s, x3+Inches(1.4), Inches(2.45), Inches(1.0), (NAVY, TEAL, NAVY))
texto(s, x3, Inches(3.7), Inches(3.8), Inches(0.6), "Freestyle", tam=24, cor=NAVY, bold=True, align=PP_ALIGN.CENTER)
texto(s, x3+Inches(0.2), Inches(4.4), Inches(3.4), Inches(2.0),
      "Manobras, truques e acrobacias feitas com o disco no ar.",
      tam=17, cor=TINTA, align=PP_ALIGN.CENTER)
animar(s, [
    {"shapes": cab, "kind": "flyL", "delay": 100, "dur": 500},
    {"shapes": [c1], "kind": "flyB", "delay": 120, "dur": 450},
    {"shapes": ic1, "kind": "spin", "start": "with", "delay": 0, "dur": 1400},
    {"shapes": [c2], "kind": "flyB", "delay": 120, "dur": 450},
    {"shapes": ic2, "kind": "fade", "start": "with", "delay": 0, "dur": 400},
    {"shapes": [c3], "kind": "flyB", "delay": 120, "dur": 450},
    {"shapes": ic3, "kind": "spin", "start": "with", "delay": 0, "dur": 1400},
])
transicao(s, "push", "l")

# =========================================================
# SLIDE 9 — CURIOSIDADES
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CREME)
cab = cabecalho(s, 7, "Curiosidades", TEAL)
curi = [
    ("100", "km/h", "O disco pode ultrapassar essa velocidade num bom lançamento."),
    ("15", "pts", "Em jogos oficiais, costuma-se jogar até 15 pontos."),
    ("MUNDO", "", "Existe campeonato mundial e o esporte é jogado em vários países."),
    ("DOGS", "", "Cachorros também competem em provas com o disco!"),
]
passos = [{"shapes": cab, "kind": "flyL", "delay": 100, "dur": 500}]
y = Inches(2.05)
for big, uni, txt in curi:
    card = rect(s, Inches(0.8), y, Inches(11.7), Inches(1.05), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
    badge = rect(s, Inches(1.0), y+Inches(0.15), Inches(1.95), Inches(0.75), NAVY, MSO_SHAPE.ROUNDED_RECTANGLE)
    texto(s, Inches(1.0), y+Inches(0.15), Inches(1.95), Inches(0.75),
          big + ("\n"+uni if uni else ""), tam=22 if not uni else 20, cor=AMARELO,
          bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    texto(s, Inches(3.2), y, Inches(9.1), Inches(1.05), txt, tam=18, cor=TINTA,
          anchor=MSO_ANCHOR.MIDDLE)
    passos.append({"shapes": [card, badge], "kind": "flyR", "delay": 130, "dur": 420})
    y += Inches(1.2)
animar(s, passos)
transicao(s, "cover", "d")

# =========================================================
# SLIDE 10 — ENCERRAMENTO
# =========================================================
s = prs.slides.add_slide(BLANK)
fundo(s, NAVY)
faixa = rect(s, 0, Inches(2.7), LARG, Inches(1.9), LARANJA)
d = disco(s, Inches(5.65), Inches(0.7), Inches(2.0), (AMARELO, BRANCO, AMARELO))
t1 = texto(s, Inches(1), Inches(2.85), Inches(11.3), Inches(1.6), "Obrigado!",
           tam=72, cor=BRANCO, bold=True, align=PP_ALIGN.CENTER)
t2 = texto(s, Inches(1), Inches(5.0), Inches(11.3), Inches(0.8),
           "Nicolas    Felipe    André    Lucas    Ruan", tam=22, cor=AMARELO,
           bold=True, align=PP_ALIGN.CENTER)
animar(s, [
    {"shapes": [faixa], "kind": "flyR", "delay": 100, "dur": 600},
    {"shapes": d, "kind": "flyT", "delay": 100, "dur": 600},
    {"shapes": d, "kind": "spin", "start": "with", "delay": 0, "dur": 2000},
    {"shapes": [t1], "kind": "grow", "delay": 150, "dur": 600},
    {"shapes": [t2], "kind": "fade", "delay": 150, "dur": 500},
])
transicao(s, "fade")

prs.save("Frisbee.pptx")
print("OK - gerado com", len(prs.slides._sldIdLst), "slides")
