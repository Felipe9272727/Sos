# -*- coding: utf-8 -*-
"""Gera uma apresentacao .pptx ANIMADA e detalhada sobre o esporte do Frisbee."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

# ---- Paleta de cores ----
AZUL_ESCURO = RGBColor(0x0F, 0x2C, 0x4A)
AZUL        = RGBColor(0x1B, 0x6C, 0xA8)
AZUL_CLARO  = RGBColor(0x3D, 0x9B, 0xD4)
LARANJA     = RGBColor(0xFF, 0x8C, 0x1A)
AMARELO     = RGBColor(0xFF, 0xC4, 0x3D)
VERDE       = RGBColor(0x2E, 0x8B, 0x57)
VERDE_ESC   = RGBColor(0x1F, 0x6B, 0x40)
VERDE_CLARO = RGBColor(0x3F, 0xA8, 0x6B)
BRANCO      = RGBColor(0xFF, 0xFF, 0xFF)
CINZA_CLARO = RGBColor(0xEC, 0xF2, 0xF7)
TEXTO_ESC   = RGBColor(0x16, 0x2A, 0x3A)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
LARG = prs.slide_width
ALT = prs.slide_height
BLANK = prs.slide_layouts[6]

# ---------- Helpers visuais ----------
def fundo(slide, cor):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, LARG, ALT)
    s.fill.solid(); s.fill.fore_color.rgb = cor
    s.line.fill.background(); s.shadow.inherit = False
    slide.shapes._spTree.remove(s._element)
    slide.shapes._spTree.insert(2, s._element)
    return s

def faixa(slide, x, y, w, h, cor, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = cor
    s.line.fill.background(); s.shadow.inherit = False
    return s

def circulo(slide, x, y, d, cor):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, d, d)
    s.fill.solid(); s.fill.fore_color.rgb = cor
    s.line.fill.background(); s.shadow.inherit = False
    return s

def caixa_texto(slide, x, y, w, h, texto, tam=20, cor=TEXTO_ESC, bold=False,
                align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = texto
    r.font.size = Pt(tam); r.font.bold = bold
    r.font.color.rgb = cor; r.font.name = "Calibri"
    return tb

def lista(slide, x, y, w, h, itens, tam=18, cor=TEXTO_ESC, cor_marcador=LARANJA,
          espaco=8):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    for i, item in enumerate(itens):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(espaco)
        r = p.add_run(); r.text = "●  "
        r.font.size = Pt(tam); r.font.color.rgb = cor_marcador; r.font.bold = True
        r2 = p.add_run(); r2.text = item
        r2.font.size = Pt(tam); r2.font.color.rgb = cor; r2.font.name = "Calibri"
    return tb

def titulo_secao(slide, texto, n, cor_titulo=AZUL_ESCURO):
    f = faixa(slide, 0, 0, Inches(0.35), ALT, LARANJA)
    t = caixa_texto(slide, Inches(0.7), Inches(0.35), Inches(11.8), Inches(1.0),
                    texto, tam=34, cor=cor_titulo, bold=True)
    u = faixa(slide, Inches(0.75), Inches(1.35), Inches(3.2), Pt(4), LARANJA)
    caixa_texto(slide, LARG-Inches(1.2), ALT-Inches(0.7), Inches(0.9), Inches(0.5),
                str(n), tam=14, cor=AZUL, bold=True, align=PP_ALIGN.RIGHT)
    return [t, u]

# ---------- Animacao (XML) ----------
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

def _efeito_par(spid, delay, ids, preset, subtype, dur=500):
    """Gera um <p:par> de entrada automatica para uma forma."""
    a, b, c, d, e = ids
    if preset == "fly":   # Fly In (presetID 2)
        pid, body = 2, f'''
          <p:anim calcmode="lin" valueType="num">
            <p:cBhvr additive="base"><p:cTn id="{e}" dur="{dur}" fill="hold"/>
              <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
              <p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>
            <p:tavLst><p:tav tm="0"><p:val><p:fltVal val="0.5"/></p:val></p:tav>
              <p:tav tm="100000"><p:val><p:fltVal val="0"/></p:val></p:tav></p:tavLst>
          </p:anim>'''
    elif preset == "zoom":  # Grow/Zoom (presetID 23)
        pid, body = 23, f'''
          <p:animScale><p:cBhvr><p:cTn id="{e}" dur="{dur}" fill="hold"/>
              <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr>
            <p:by x="100000" y="100000"/></p:animScale>
          <p:animEffect transition="in" filter="fade">
            <p:cBhvr><p:cTn id="{e+1}" dur="{dur}"/>
              <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'''
    else:  # Fade (presetID 10)
        pid, body = 10, f'''
          <p:animEffect transition="in" filter="fade">
            <p:cBhvr><p:cTn id="{e}" dur="{dur}"/>
              <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'''
    return f'''
      <p:par><p:cTn id="{a}" fill="hold">
        <p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>
        <p:childTnLst><p:par><p:cTn id="{b}" fill="hold">
          <p:stCondLst><p:cond delay="0"/></p:stCondLst>
          <p:childTnLst><p:par>
            <p:cTn id="{c}" presetID="{pid}" presetClass="entr" presetSubtype="{subtype}" fill="hold" grpId="0" nodeType="afterEffect">
              <p:stCondLst><p:cond delay="0"/></p:stCondLst>
              <p:childTnLst>
                <p:set><p:cBhvr><p:cTn id="{d}" dur="1" fill="hold">
                    <p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>
                  <p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
                  <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>
                  <p:to><p:strVal val="visible"/></p:to></p:set>
                {body}
              </p:childTnLst></p:cTn>
          </p:par></p:childTnLst></p:cTn></p:par></p:childTnLst>
      </p:cTn></p:par>'''

def animar(slide, formas, preset="fade", subtype="0", primeiro_delay=200, gap=350):
    """Aplica animacao de entrada automatica a uma lista de formas, em sequencia."""
    if not formas:
        return
    pares, cid = [], 3
    for i, f in enumerate(formas):
        delay = primeiro_delay if i == 0 else gap
        ids = (cid, cid+1, cid+2, cid+3, cid+4)
        cid += 6
        pares.append(_efeito_par(f.shape_id, delay, ids, preset, subtype))
    timing = f'''<p:timing xmlns:p="{P_NS}" xmlns:a="{A_NS}">
      <p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
        <p:childTnLst><p:seq concurrent="1" nextAc="seek">
          <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
            <p:childTnLst>{''.join(pares)}</p:childTnLst></p:cTn>
          <p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
          <p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>
        </p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'''
    slide.element.append(etree.fromstring(timing.encode("utf-8")))

def transicao(slide, tipo="fade", dir_=None):
    """Adiciona transicao de slide."""
    d = f' dir="{dir_}"' if dir_ else ""
    xml = (f'<p:transition xmlns:p="{P_NS}" spd="med">'
           f'<p:{tipo}{d}/></p:transition>')
    el = etree.fromstring(xml.encode("utf-8"))
    cmap = slide.element.find(qn('p:clrMapOvr'))
    if cmap is not None:
        cmap.addnext(el)
    else:
        slide.element.append(el)

# =================================================================
# SLIDE 1 - CAPA
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, AZUL_ESCURO)
circulo(s, Inches(-1.5), Inches(-1.5), Inches(4), AZUL)
circulo(s, LARG-Inches(2.8), ALT-Inches(2.8), Inches(4.5), LARANJA)
circulo(s, LARG-Inches(2.0), ALT-Inches(2.0), Inches(2.9), AZUL_ESCURO)
disco1 = circulo(s, Inches(5.5), Inches(0.55), Inches(2.3), LARANJA)
disco2 = circulo(s, Inches(5.85), Inches(0.9), Inches(1.6), AMARELO)
emoji = caixa_texto(s, Inches(5.5), Inches(1.2), Inches(2.3), Inches(1.0),
                    "🥏", tam=54, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tit = caixa_texto(s, Inches(1), Inches(3.05), Inches(11.3), Inches(1.2),
                  "O MUNDO DO FRISBEE", tam=52, cor=BRANCO, bold=True, align=PP_ALIGN.CENTER)
sub = caixa_texto(s, Inches(1), Inches(4.25), Inches(11.3), Inches(0.7),
                  "Origem, regras, modalidades e curiosidades", tam=22, cor=AMARELO,
                  align=PP_ALIGN.CENTER)
nomes = caixa_texto(s, Inches(1), Inches(6.05), Inches(11.3), Inches(0.8),
                    "Nicolas  •  Felipe  •  André  •  Lucas  •  Ruan", tam=20,
                    cor=BRANCO, align=PP_ALIGN.CENTER, bold=True)
animar(s, [disco1, disco2, emoji, tit, sub, nomes], preset="zoom", primeiro_delay=200, gap=300)
transicao(s, "fade")

# =================================================================
# SLIDE 2 - O QUE É
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "O que é o Frisbee?", 2)
c1 = caixa_texto(s, Inches(0.75), Inches(1.75), Inches(7.2), Inches(2.0),
                 "É um esporte coletivo jogado com um disco de plástico (o frisbee). "
                 "O objetivo é levar o disco até a área de pontuação do adversário "
                 "usando apenas passes — ninguém pode correr segurando o disco.",
                 tam=21, cor=TEXTO_ESC)
# cartões de destaque
cards = []
infos = [("👥", "Equipes", "7 jogadores\nde cada lado"),
         ("🎯", "Objetivo", "Receber o disco\nna área de gol"),
         ("🤝", "Sem juiz", "Os jogadores\nresolvem as faltas")]
x = Inches(0.75)
for emj, t, d in infos:
    card = faixa(s, x, Inches(4.0), Inches(3.7), Inches(2.6), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
    faixa(s, x, Inches(4.0), Inches(3.7), Inches(0.65), AZUL, MSO_SHAPE.ROUNDED_RECTANGLE)
    caixa_texto(s, x, Inches(4.05), Inches(3.7), Inches(0.6), f"{emj}  {t}", tam=18,
                cor=BRANCO, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    caixa_texto(s, x, Inches(4.8), Inches(3.7), Inches(1.7), d, tam=17, cor=TEXTO_ESC,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cards.append(card)
    x += Inches(3.95)
disco = circulo(s, Inches(8.6), Inches(1.55), Inches(3.5), LARANJA)
circulo(s, Inches(9.15), Inches(2.1), Inches(2.4), AMARELO)
caixa_texto(s, Inches(8.6), Inches(2.45), Inches(3.5), Inches(1.4), "🥏", tam=80,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
animar(s, cab + [c1, disco] + cards, preset="fade", primeiro_delay=150, gap=350)
transicao(s, "push", "l")

# =================================================================
# SLIDE 3 - ORIGEM E HISTÓRIA
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "Origem e história", 3)
b1 = caixa_texto(s, Inches(0.75), Inches(1.7), Inches(11.8), Inches(1.2),
                 "O esporte começou como uma brincadeira universitária nos Estados Unidos "
                 "e evoluiu para uma atividade competitiva praticada em vários países do mundo.",
                 tam=20, cor=TEXTO_ESC)
box = faixa(s, Inches(0.75), Inches(3.2), Inches(11.8), Inches(3.4), BRANCO)
faixa(s, Inches(0.75), Inches(3.2), Inches(0.18), Inches(3.4), LARANJA)
tt = caixa_texto(s, Inches(1.1), Inches(3.35), Inches(11.2), Inches(0.6),
                 "📜 De onde vem o nome \"Frisbee\"?", tam=23, cor=AZUL_ESCURO, bold=True)
tx = caixa_texto(s, Inches(1.1), Inches(4.05), Inches(11.2), Inches(2.4),
                 "Ele se inspirou em formas antigas de arremessar discos, mas ficou famoso "
                 "nos EUA nos anos 1940. O nome veio da empresa de tortas \"Frisbie Pie Company\": "
                 "os estudantes jogavam as formas de torta vazias gritando \"Frisbie!\".\n\n"
                 "Depois, a empresa Wham-O criou o disco de plástico moderno e mudou a escrita "
                 "para \"Frisbee\" — como conhecemos hoje.",
                 tam=18, cor=TEXTO_ESC)
animar(s, cab + [b1, box, tt, tx], preset="fade", primeiro_delay=150, gap=400)
transicao(s, "wipe", "r")

# =================================================================
# SLIDE 4 - O CAMPO DE JOGO (diagrama)
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "O campo de jogo", 4)
# campo
fx, fy, fw, fh = Inches(1.3), Inches(2.2), Inches(10.7), Inches(3.6)
campo = faixa(s, fx, fy, fw, fh, VERDE)
ez = Inches(1.8)
gol1 = faixa(s, fx, fy, ez, fh, VERDE_ESC)
gol2 = faixa(s, fx+fw-ez, fy, ez, fh, VERDE_ESC)
# linhas brancas das areas de gol
faixa(s, fx+ez, fy, Pt(3), fh, BRANCO)
faixa(s, fx+fw-ez, fy, Pt(3), fh, BRANCO)
# linha central tracejada (simulada com retangulinhos)
cx = fx + fw/2
yy = fy + Inches(0.15)
while yy < fy + fh - Inches(0.15):
    faixa(s, cx, yy, Pt(3), Inches(0.25), BRANCO)
    yy += Inches(0.45)
# disco
disco = circulo(s, cx-Inches(0.25), fy+fh/2-Inches(0.25), Inches(0.5), LARANJA)
# rotulos
l1 = caixa_texto(s, fx, fy-Inches(0.05), ez, fh, "ÁREA\nDE GOL", tam=13, cor=BRANCO,
                 bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
l2 = caixa_texto(s, fx+ez, fy, fw-2*ez, fh, "CAMPO CENTRAL", tam=15, cor=BRANCO,
                 bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
l3 = caixa_texto(s, fx+fw-ez, fy-Inches(0.05), ez, fh, "ÁREA\nDE GOL", tam=13, cor=BRANCO,
                 bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
nota = caixa_texto(s, Inches(1.3), Inches(6.1), Inches(10.7), Inches(0.9),
                   "Pode ser jogado em grama, areia ou quadras adaptadas. Pontua-se quando "
                   "um jogador recebe o disco dentro da área de gol adversária.",
                   tam=17, cor=TEXTO_ESC, align=PP_ALIGN.CENTER)
animar(s, cab + [campo, gol1, gol2, l1, l2, l3, disco, nota], preset="fade",
       primeiro_delay=150, gap=250)
transicao(s, "cover", "d")

# =================================================================
# SLIDE 5 - REGRAS BÁSICAS
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "Regras básicas", 5)
itens = [
    "O objetivo é chegar à área de pontuação do adversário recebendo o disco.",
    "Quem está com o frisbee NÃO pode correr — só pode passar.",
    "Cada equipe joga normalmente com 7 jogadores em campo.",
    "O disco passa para o outro time se cair no chão ou for interceptado.",
    "Pontua-se quando um jogador recebe o disco dentro da área de gol adversária.",
    "Não é permitido contato físico forte entre os jogadores.",
]
formas = list(cab)
y = Inches(1.95)
for it in itens:
    n = circulo(s, Inches(0.9), y, Inches(0.55), LARANJA)
    caixa_texto(s, Inches(0.9), y, Inches(0.55), Inches(0.55), "•", tam=24, cor=BRANCO,
                bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    t = caixa_texto(s, Inches(1.65), y, Inches(10.8), Inches(0.7), it, tam=19,
                    cor=TEXTO_ESC, anchor=MSO_ANCHOR.MIDDLE)
    formas += [n, t]
    y += Inches(0.82)
animar(s, formas, preset="fly", subtype="0", primeiro_delay=150, gap=300)
transicao(s, "push", "l")

# =================================================================
# SLIDE 6 - COMO O JOGO ACONTECE
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "Como o jogo acontece", 6)
itens = [
    "O jogo começa com um lançamento chamado \"pull\" (parecido com a saída do futebol).",
    "Quem está com o disco tem cerca de 10 segundos para passar.",
    "Se o disco sair do campo, a posse vai para o outro time.",
    "Após cada ponto, os times trocam de lado no campo.",
    "As substituições normalmente acontecem depois de um ponto ser marcado.",
    "Se dois jogadores pegam o disco ao mesmo tempo, a posse fica com o ataque.",
    "Vence quem chega primeiro à pontuação definida (geralmente 15 pontos).",
]
li = lista(s, Inches(0.9), Inches(1.95), Inches(11.5), Inches(5), itens, tam=19, espaco=14)
animar(s, cab + [li], preset="fade", primeiro_delay=150, gap=350)
transicao(s, "wipe", "d")

# =================================================================
# SLIDE 7 - ESPÍRITO DO JOGO
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, AZUL_ESCURO)
circulo(s, LARG-Inches(3.0), Inches(-1.2), Inches(4), AZUL)
circulo(s, Inches(-1.2), ALT-Inches(2.8), Inches(4), LARANJA)
t1 = caixa_texto(s, Inches(1), Inches(1.2), Inches(11.3), Inches(1.0),
                 "🤝 O Espírito do Jogo", tam=40, cor=AMARELO, bold=True, align=PP_ALIGN.CENTER)
t2 = caixa_texto(s, Inches(1.5), Inches(2.9), Inches(10.3), Inches(2.0),
                 "O Frisbee é conhecido por não ter árbitros na maioria das partidas: "
                 "os próprios jogadores resolvem as faltas e discordâncias.",
                 tam=24, cor=BRANCO, align=PP_ALIGN.CENTER)
t3 = caixa_texto(s, Inches(1.5), Inches(4.9), Inches(10.3), Inches(1.4),
                 "Por isso o esporte valoriza o respeito, a honestidade e o fair play "
                 "entre todos os jogadores.",
                 tam=22, cor=AMARELO, align=PP_ALIGN.CENTER, bold=True)
animar(s, [t1, t2, t3], preset="zoom", primeiro_delay=200, gap=500)
transicao(s, "cover", "u")

# =================================================================
# SLIDE 8 - MODALIDADES
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "Modalidades do Frisbee", 8)
mods = [
    ("🥏", "Ultimate", "Jogo coletivo de passes\nentre duas equipes, o\nmais popular de todos."),
    ("⛳", "Disc Golf", "Como o golfe, mas o\ndisco é arremessado em\ndireção a uma cesta."),
    ("🤸", "Freestyle", "Manobras, truques e\nacrobacias feitas com\no disco no ar."),
]
cards = []
x = Inches(0.9)
for emj, t, d in mods:
    card = faixa(s, x, Inches(2.1), Inches(3.7), Inches(3.9), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
    circulo(s, x+Inches(1.25), Inches(2.45), Inches(1.2), AMARELO)
    caixa_texto(s, x+Inches(1.25), Inches(2.45), Inches(1.2), Inches(1.2), emj, tam=40,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    caixa_texto(s, x, Inches(3.8), Inches(3.7), Inches(0.6), t, tam=22, cor=AZUL_ESCURO,
                bold=True, align=PP_ALIGN.CENTER)
    caixa_texto(s, x, Inches(4.5), Inches(3.7), Inches(1.4), d, tam=16, cor=TEXTO_ESC,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)
    cards.append(card)
    x += Inches(3.95)
animar(s, cab + cards, preset="zoom", primeiro_delay=200, gap=400)
transicao(s, "push", "l")

# =================================================================
# SLIDE 9 - BENEFÍCIOS
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "Por que praticar?", 9)
bens = [
    ("🧠", "Melhora os reflexos e a coordenação"),
    ("🏃", "Trabalha o corpo todo e o condicionamento"),
    ("👫", "Estimula o trabalho em equipe"),
    ("😄", "Ensina respeito e fair play"),
    ("🌳", "Pode ser jogado ao ar livre, com poucos materiais"),
]
formas = list(cab)
y = Inches(2.0)
for emj, txt in bens:
    card = faixa(s, Inches(0.9), y, Inches(11.5), Inches(0.85), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
    caixa_texto(s, Inches(1.05), y, Inches(0.9), Inches(0.85), emj, tam=26,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    caixa_texto(s, Inches(2.0), y, Inches(10.2), Inches(0.85), txt, tam=19, cor=TEXTO_ESC,
                anchor=MSO_ANCHOR.MIDDLE)
    formas.append(card)
    y += Inches(0.98)
animar(s, formas, preset="fly", primeiro_delay=150, gap=300)
transicao(s, "wipe", "r")

# =================================================================
# SLIDE 10 - CURIOSIDADES
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, CINZA_CLARO)
cab = titulo_secao(s, "Curiosidades", 10)
curiosidades = [
    ("⚡", "O disco pode ultrapassar 100 km/h dependendo do lançamento."),
    ("🏆", "Existe campeonato mundial do esporte."),
    ("🐶", "Cachorros também competem em provas com o disco!"),
    ("🧠", "Ajuda nos reflexos, na coordenação e no trabalho em equipe."),
    ("🌎", "É praticado em vários países ao redor do mundo."),
]
formas = list(cab)
y = Inches(2.0)
for emoji, txt in curiosidades:
    card = faixa(s, Inches(0.9), y, Inches(11.5), Inches(0.85), BRANCO, MSO_SHAPE.ROUNDED_RECTANGLE)
    caixa_texto(s, Inches(1.05), y, Inches(0.9), Inches(0.85), emoji, tam=26,
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    caixa_texto(s, Inches(2.0), y, Inches(10.2), Inches(0.85), txt, tam=19, cor=TEXTO_ESC,
                anchor=MSO_ANCHOR.MIDDLE)
    formas.append(card)
    y += Inches(0.98)
animar(s, formas, preset="fade", primeiro_delay=150, gap=300)
transicao(s, "cover", "d")

# =================================================================
# SLIDE 11 - ENCERRAMENTO
# =================================================================
s = prs.slides.add_slide(BLANK)
fundo(s, AZUL_ESCURO)
d1 = circulo(s, Inches(5.4), Inches(1.5), Inches(2.5), LARANJA)
circulo(s, Inches(5.78), Inches(1.88), Inches(1.74), AMARELO)
em = caixa_texto(s, Inches(5.4), Inches(2.15), Inches(2.5), Inches(1.2), "🥏", tam=60,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
t1 = caixa_texto(s, Inches(1), Inches(4.3), Inches(11.3), Inches(1.0),
                 "Obrigado pela atenção!", tam=44, cor=BRANCO, bold=True, align=PP_ALIGN.CENTER)
t2 = caixa_texto(s, Inches(1), Inches(5.6), Inches(11.3), Inches(0.8),
                 "Nicolas  •  Felipe  •  André  •  Lucas  •  Ruan", tam=20, cor=AMARELO,
                 align=PP_ALIGN.CENTER, bold=True)
animar(s, [d1, em, t1, t2], preset="zoom", primeiro_delay=200, gap=450)
transicao(s, "fade")

prs.save("Frisbee.pptx")
print("OK - arquivo gerado com", len(prs.slides._sldIdLst), "slides")
