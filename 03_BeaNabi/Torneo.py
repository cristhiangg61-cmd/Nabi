import re
import os
import copy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

EQUIPOS = [
    ("Jugador 1",  "Jugador 2"),
    ("Jugador 3",  "Jugador 4"),
    ("Jugador 5",  "Jugador 6"),
    ("Jugador 7",  "Jugador 8"),
    ("Jugador 9",  "Jugador 10"),
    ("Jugador 11", "Jugador 12"),
    ("Jugador 13", "Jugador 14"),
    ("Jugador 15", "Jugador 16"),
]

C = {
    "bg":      "#0b0b1a",
    "azul":    ("#1a4a8a", "#4d9fff"),
    "rojo":    ("#8a1a1a", "#ff4d4d"),
    "win":     ("#1a5c2e", "#50e87a"),
    "final_w": ("#6b3a00", "#ffb347"),
    "champ":   ("#5c4500", "#ffd700"),
    "silver":  ("#353535", "#c0c0c0"),
    "bronze":  ("#4a2800", "#cd7f32"),
    "empty":   ("#0f0f20", "#252545"),
    "line":    "#3a3a6a",
    "sep":     "#2a2a50",
}

# Cajas más altas para acomodar 2 jugadores
BOX_W  = 3.2
BOX_H  = 1.35   # altura doble para mostrar ambos jugadores
FS     = 8.5    # fuente nombre dentro de caja
GAP_Y  = 2.4    # separación vertical entre cajas de cuartos
N_SIDE = 4      # 4 equipos por lado → cuartos, semis, final

# Posiciones X: cuartos → semis → final
XS_IZQ = [-11.0, -6.5, -2.0]
XS_DER = [ 11.0,  6.5,  2.0]

XLIM_TOP = (-15.0, 15.0)
YLIM_TOP = (-2.5,  13.0)
XLIM_BOT = (0.0, 36.0)
YLIM_BOT = (0.0, 12.0)

Y_HEAD = 9.9
Y_CONT = 7.2
Y_WIN  = 4.8
Y_LBL  = 3.7


# ─────────────────────────────────────────────────────────────────
#  ESTADO  (equipos = tuplas de 2 nombres)
# ─────────────────────────────────────────────────────────────────
def estado_inicial(equipos):
    """
    wb[0] = cuartos  (8 equipos)
    wb[1] = semis    (4 equipos)
    wb[2] = final    (2 equipos)
    wb[3] = campeon  (1 equipo)
    """
    return {
        "wb": [
            list(equipos),
            [None]*4,
            [None]*2,
            [None]*1,
        ],
        "semifinal_losers": [None, None],
        "tercero": None,
        "cuarto":  None,
    }


# ─────────────────────────────────────────────────────────────────
#  GEOMETRÍA
# ─────────────────────────────────────────────────────────────────
def _oct_ys():
    return [(N_SIDE - 1 - i) * GAP_Y for i in range(N_SIDE)]

def _get_y(ronda, slot, oct_ys):
    if ronda == 0:
        return oct_ys[slot]
    ya = _get_y(ronda-1, 2*slot,   oct_ys)
    yb = _get_y(ronda-1, 2*slot+1, oct_ys)
    return (ya + yb) / 2


# ─────────────────────────────────────────────────────────────────
#  PRIMITIVAS
# ─────────────────────────────────────────────────────────────────
def _nombre_equipo(equipo):
    """Devuelve tupla (nombre1, nombre2) o (None, None) si vacío."""
    if equipo is None:
        return None, None
    return equipo[0], equipo[1]

def draw_box_team(ax, cx, cy, equipo, estilo, w=BOX_W, h=BOX_H, fontsize=FS, z=3):
    """Dibuja una caja con dos jugadores."""
    n1, n2 = _nombre_equipo(equipo)
    vacia = (equipo is None)

    if vacia:
        fc, ec = C["empty"]; alpha=0.55; ls="--"
    else:
        fc, ec = C[estilo];  alpha=1.0;  ls="solid"

    ax.add_patch(FancyBboxPatch(
        (cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        fc=fc, ec=ec, lw=1.8, ls=ls, alpha=alpha, zorder=z))

    if not vacia:
        # Línea divisoria entre los dos jugadores
        ax.plot([cx-w/2+0.12, cx+w/2-0.12], [cy]*2,
                color=ec, lw=0.7, alpha=0.45, zorder=z+1)
        # Jugador 1 (arriba)
        ax.text(cx, cy + h*0.24, n1, ha="center", va="center",
                fontsize=fontsize, color="#ffffff", fontweight="bold",
                zorder=z+1, clip_on=True)
        # Jugador 2 (abajo)
        ax.text(cx, cy - h*0.24, n2, ha="center", va="center",
                fontsize=fontsize, color="#e0e0ff", fontweight="bold",
                zorder=z+1, clip_on=True)

def draw_box_team_champ(ax, cx, cy, equipo, w=BOX_W*1.35, h=BOX_H*1.45, fontsize=FS+1):
    n1, n2 = _nombre_equipo(equipo)
    if equipo is None:
        ax.add_patch(FancyBboxPatch(
            (cx-w/2, cy-h/2), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.14",
            fc=C["empty"][0], ec=C["empty"][1], lw=1.8, ls="--", alpha=0.55, zorder=4))
        return
    fc, ec = C["champ"]
    for i in range(4, 0, -1):
        gw=w+i*0.28; gh=h+i*0.18
        ax.add_patch(FancyBboxPatch(
            (cx-gw/2, cy-gh/2), gw, gh,
            boxstyle="round,pad=0.04,rounding_size=0.16",
            fc=fc, ec=ec, lw=0, alpha=0.055*i, zorder=4))
    ax.add_patch(FancyBboxPatch(
        (cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.14",
        fc=fc, ec=ec, lw=2.6, ls="solid", alpha=1.0, zorder=5))
    ax.plot([cx-w/2+0.15, cx+w/2-0.15], [cy]*2,
            color="#b8860b", lw=0.9, alpha=0.55, zorder=6)
    ax.text(cx, cy + h*0.24, n1, ha="center", va="center",
            fontsize=fontsize, color="#ffd700", fontweight="bold", zorder=6, clip_on=True)
    ax.text(cx, cy - h*0.24, n2, ha="center", va="center",
            fontsize=fontsize, color="#ffe08a", fontweight="bold", zorder=6, clip_on=True)

def draw_line(ax, x1, y1, x2, y2, lw=1.5, color=None, z=1):
    ax.plot([x1,x2],[y1,y2], color=color or C["line"],
            lw=lw, zorder=z, solid_capstyle="round")

def draw_connector(ax, x_src, y_top, y_bot, x_dst, y_mid):
    xm = (x_src + x_dst) / 2
    draw_line(ax, x_src, y_top, xm,   y_top)
    draw_line(ax, x_src, y_bot, xm,   y_bot)
    draw_line(ax, xm,   y_top, xm,   y_bot)
    draw_line(ax, xm,   y_mid, x_dst, y_mid)

def draw_section_divider(ax, x):
    ax.plot([x,x],[0.5,10.7], color=C["sep"], lw=1.0, ls="--", zorder=1, alpha=0.55)

def draw_medal(ax, cx, cy, pos, r=0.42):
    paleta = {1:("#a07800","#ffd700","ORO"), 2:("#606060","#d8d8d8","PLATA"), 3:("#7a4500","#cd7f32","BRONCE")}
    if pos not in paleta: return
    fc, ec, label = paleta[pos]
    ax.add_patch(Circle((cx,cy), r+0.07, fc=C["bg"], ec=ec, lw=2.2, zorder=5))
    ax.add_patch(Circle((cx,cy), r,       fc=fc,     ec=ec, lw=1.2, zorder=6))
    ax.text(cx, cy,        str(pos), ha="center", va="center",
            fontsize=10, fontweight="bold", color="#ffffff", zorder=7)
    ax.text(cx, cy-r-0.16, label,   ha="center", va="top",
            fontsize=7.5, fontweight="bold", color=ec, zorder=7)


# ─────────────────────────────────────────────────────────────────
#  BRACKET SUPERIOR  (cuartos → semis → final)
# ─────────────────────────────────────────────────────────────────
def dibujar_bracket(ax, st):
    ax.set_facecolor(C["bg"])
    ax.set_xlim(*XLIM_TOP)
    ax.set_ylim(*YLIM_TOP)
    ax.axis("off")

    oct_ys   = _oct_ys()
    y_lbl    = oct_ys[0] + 1.3
    y_titulo = oct_ys[0] + 2.8
    rondas   = st["wb"]

    for lado in ("izq", "der"):
        izq   = (lado == "izq")
        xs    = XS_IZQ if izq else XS_DER
        idx0  = 0 if izq else 4
        cbase = "azul" if izq else "rojo"
        titulo= "LADO AZUL" if izq else "LADO ROJO"
        dir_s = +1 if izq else -1

        for r, lbl in enumerate(["CUARTOS","SEMIFINAL","FINAL"]):
            ax.text(xs[r], y_lbl, lbl, ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color="#7070aa")

        ax.text(xs[1], y_titulo, titulo, ha="center", va="bottom",
                fontsize=13, fontweight="bold", color="#ccccff")

        estilos = {0: cbase, 1: "win", 2: "final_w"}

        for r in range(3):
            n = N_SIDE >> r
            for j in range(n):
                g = (idx0 >> r) + j
                draw_box_team(ax, xs[r], _get_y(r, j, oct_ys), rondas[r][g], estilos[r])

        for r in range(1, 3):
            n = N_SIDE >> r
            for j in range(n):
                y_top = _get_y(r-1, 2*j,   oct_ys)
                y_bot = _get_y(r-1, 2*j+1, oct_ys)
                y_mid = _get_y(r,   j,      oct_ys)
                x_src = xs[r-1] + dir_s * BOX_W/2
                x_dst = xs[r]   - dir_s * BOX_W/2
                draw_connector(ax, x_src, y_top, y_bot, x_dst, y_mid)

    # ── Centro: Gran Final + Campeón ──────────────────────────────
    y_fin = _get_y(2, 0, oct_ys)
    cx    = 0.0
    CW    = BOX_W * 1.05
    CH    = BOX_H * 1.45

    ax.text(cx, y_fin + CH/2 + 0.55, "★  GRAN FINAL  ★",
            ha="center", va="bottom",
            fontsize=11, fontweight="bold", color="#ffd700",
            bbox=dict(boxstyle="round,pad=0.30", fc="#1a1000", ec="#b8860b", lw=1.5, alpha=0.95),
            zorder=6)

    draw_box_team_champ(ax, cx, y_fin, st["wb"][3][0], w=CW, h=CH)

    draw_line(ax, XS_IZQ[2] + BOX_W/2, y_fin, cx - CW/2, y_fin)
    draw_line(ax, XS_DER[2] - BOX_W/2, y_fin, cx + CW/2, y_fin)

    if st["wb"][3][0]:
        ax.text(cx, y_fin - CH/2 - 0.30, "CAMPEONES!",
                ha="center", va="top", fontsize=11, fontweight="bold", color="#ffd700", zorder=6)
        ax.text(cx, y_fin - CH/2 - 0.95, "★  ★  ★",
                ha="center", va="top", fontsize=9, color="#b8860b", zorder=6)


# ─────────────────────────────────────────────────────────────────
#  PANEL INFERIOR
# ─────────────────────────────────────────────────────────────────
def _subcampeon(st):
    fin=st["wb"][2]; champ=st["wb"][3][0]
    if champ is None or fin[0] is None or fin[1] is None: return None
    return fin[1] if champ==fin[0] else fin[0]

def _equipo_label(equipo):
    if equipo is None: return "—"
    return f"{equipo[0]} / {equipo[1]}"

def dibujar_panel_inferior(ax, st):
    ax.set_facecolor(C["bg"])
    ax.set_xlim(*XLIM_BOT)
    ax.set_ylim(*YLIM_BOT)
    ax.axis("off")

    XR_TOP = XLIM_TOP[1]-XLIM_TOP[0]
    YR_TOP = YLIM_TOP[1]-YLIM_TOP[0]
    XR_BOT = XLIM_BOT[1]-XLIM_BOT[0]
    YR_BOT = YLIM_BOT[1]-YLIM_BOT[0]
    RATIO  = 2.1
    BW = BOX_W * (XR_BOT/XR_TOP)
    BH = BOX_H * (YR_BOT/YR_TOP) * RATIO

    sl  = st["semifinal_losers"]
    fin = st["wb"][2]

    draw_section_divider(ax, 12)
    draw_section_divider(ax, 24)

    # ── SECCIÓN 1: 3ER PUESTO ─────────────────────────────────────
    X3 = 6.0
    draw_medal(ax, X3-2.5, Y_HEAD, 3, r=0.44)
    ax.text(X3+0.5, Y_HEAD, "3ER PUESTO", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#cd7f32")

    xa3, xb3 = X3-2.8, X3+2.8
    draw_box_team(ax, xa3, Y_CONT, sl[0], "azul" if sl[0] else "empty", w=BW, h=BH, fontsize=9)
    draw_box_team(ax, xb3, Y_CONT, sl[1], "rojo" if sl[1] else "empty", w=BW, h=BH, fontsize=9)

    draw_line(ax, xa3+BW/2, Y_CONT, X3, Y_CONT)
    draw_line(ax, xb3-BW/2, Y_CONT, X3, Y_CONT)
    draw_line(ax, X3, Y_CONT, X3, Y_WIN+BH/2)

    draw_box_team(ax, X3, Y_WIN, st["tercero"], "bronze", w=BW, h=BH, fontsize=9)
    if st["tercero"]:
        ax.text(X3, Y_LBL, "3er Puesto", ha="center", va="center",
                fontsize=9, fontweight="bold", color="#cd7f32")

    # ── SECCIÓN 2: GRAN FINAL ─────────────────────────────────────
    XF = 18.0
    ax.text(XF, Y_HEAD, "★  GRAN FINAL  ★", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#ffd700",
            bbox=dict(boxstyle="round,pad=0.35", fc="#1a1000", ec="#b8860b", lw=1.6, alpha=0.95))

    xaf, xbf = XF-3.5, XF+3.5
    draw_box_team(ax, xaf, Y_CONT, fin[0], "azul" if fin[0] else "empty", w=BW, h=BH, fontsize=9)
    draw_box_team(ax, xbf, Y_CONT, fin[1], "rojo" if fin[1] else "empty", w=BW, h=BH, fontsize=9)

    CW_B = BW*1.35; CH_B = BH*1.45
    draw_line(ax, xaf+BW/2, Y_CONT, XF, Y_CONT)
    draw_line(ax, xbf-BW/2, Y_CONT, XF, Y_CONT)
    draw_line(ax, XF, Y_CONT, XF, Y_WIN+CH_B/2)

    draw_box_team_champ(ax, XF, Y_WIN, st["wb"][3][0], w=CW_B, h=CH_B)
    if st["wb"][3][0]:
        ax.text(XF, Y_WIN-CH_B/2-0.28, "CAMPEONES!", ha="center", va="top",
                fontsize=11, fontweight="bold", color="#ffd700")
        ax.text(XF, Y_WIN-CH_B/2-0.92, "★  ★  ★", ha="center", va="top",
                fontsize=9, color="#b8860b", zorder=3)

    # ── SECCIÓN 3: PODIO ─────────────────────────────────────────
    XP = 30.0; ROW = 1.9
    ax.text(XP, Y_HEAD, "PODIO", ha="center", va="center",
            fontsize=12, fontweight="bold", color="#ffffff")
    ax.plot([25.5,34.5],[Y_HEAD-0.52]*2, color=C["sep"], lw=1.2, zorder=1)

    podio = [
        (1,"Oro",    st["wb"][3][0],  "champ",  "#ffd700"),
        (2,"Plata",  _subcampeon(st), "silver", "#d0d0d0"),
        (3,"Bronce", st["tercero"],   "bronze", "#cd7f32"),
        (4,"4to",    st["cuarto"],    "empty",  "#5a5a7a"),
    ]
    for pos, lbl, equipo, estilo, color_lbl in podio:
        yp = 9.2 - (pos-1)*ROW
        if pos <= 3:
            draw_medal(ax, 25.8, yp, pos, r=0.39)
        else:
            ax.text(25.8, yp, "4to", ha="center", va="center",
                    fontsize=9, fontweight="bold", color=color_lbl, zorder=5)
        ax.text(26.9, yp+0.12, lbl, ha="left", va="center",
                fontsize=9, fontweight="bold", color=color_lbl)
        draw_box_team(ax, 32.2, yp, equipo, estilo if equipo else "empty",
                      w=BW, h=BH*0.92, fontsize=8, z=3)


# ─────────────────────────────────────────────────────────────────
#  RENDER
# ─────────────────────────────────────────────────────────────────
def render(st, banner=None, ruta=None, dpi=130):
    fig = plt.figure(figsize=(34, 20), facecolor=C["bg"])
    gs  = fig.add_gridspec(2, 1, height_ratios=[2.1, 1.0],
                           hspace=0.03, top=0.93, bottom=0.02,
                           left=0.01, right=0.99)
    ax_top = fig.add_subplot(gs[0])
    ax_bot = fig.add_subplot(gs[1])

    dibujar_bracket(ax_top, st)
    dibujar_panel_inferior(ax_bot, st)

    fig.suptitle("TORNEO 2vs2  —  8 EQUIPOS  —  ELIMINACION DIRECTA",
                 fontsize=22, fontweight="bold", color="#dde0ff",
                 y=0.97, fontfamily="DejaVu Sans")

    if banner:
        fig.text(0.5, 0.935, banner, ha="center", va="top",
                 fontsize=16, fontweight="bold", color="#ffe08a",
                 bbox=dict(boxstyle="round,pad=0.4", fc="#140f00", ec="#b8860b", lw=1.6))

    if ruta:
        fig.savefig(ruta, bbox_inches="tight", dpi=dpi,
                    facecolor=C["bg"], pad_inches=0.12)
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────
#  LÓGICA DEL TORNEO
# ─────────────────────────────────────────────────────────────────
def pedir_ganador(eq1, eq2, etiqueta):
    n1 = f"{eq1[0]} + {eq1[1]}"
    n2 = f"{eq2[0]} + {eq2[1]}"
    print(f"\n  --- {etiqueta} ---")
    print(f"  [1]  {n1}")
    print(f"  [2]  {n2}")
    print(f"  [0]  RETROCEDER")
    while True:
        raw = input("  Quien avanza? (1 / 2 / 0): ").strip()
        if raw == "0": return "RETROCEDER"
        if raw == "1": return eq1, eq2
        if raw == "2": return eq2, eq1
        print("  Ingresa 1, 2 o 0.")

def correr_torneo(equipos, out_dir=None):
    if out_dir is None:
        try:    out_dir = os.path.dirname(os.path.abspath(__file__))
        except: out_dir = os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    ruta = os.path.join(out_dir, "actual.png")

    partidos  = _construir_partidos()
    st        = estado_inicial(equipos)
    historial = []
    n_partido = 0

    render(st, banner="Esperando el primer partido...", ruta=ruta)
    print("\n" + "="*60)
    print("  TORNEO 2vs2 - 8 EQUIPOS - ELIMINACION DIRECTA")
    print("  [0] en cualquier momento para RETROCEDER")
    print("="*60)

    idx = 0
    while idx < len(partidos):
        p  = partidos[idx]
        e1 = _resolver(st, p["src1"])
        e2 = _resolver(st, p["src2"])
        if e1 is None or e2 is None:
            idx += 1; continue

        print(f"\n{'='*60}\n  {p['etapa']}\n{'='*60}")
        resultado = pedir_ganador(e1, e2, p["label"])

        if resultado == "RETROCEDER":
            if not historial:
                print("  No hay partidos anteriores para deshacer.")
            else:
                st, prev_idx = historial.pop()
                idx          = prev_idx
                n_partido    = max(0, n_partido-1)
                render(st, banner=f"Partido deshecho  --  Retrocediendo al Partido {n_partido}", ruta=ruta)
                print("  Partido deshecho.")
            continue

        ganador, perdedor = resultado
        historial.append((copy.deepcopy(st), idx))
        _aplicar(st, p, ganador, perdedor)
        n_partido += 1
        label_g = f"{ganador[0]} + {ganador[1]}"
        render(st, banner=f"Partido {n_partido}  |  {p['label']}  ->  avanzo  {label_g}", ruta=ruta)
        print(f"  Avanza: {label_g}")
        idx += 1

    print(f"\n{'='*60}")
    print("  TORNEO FINALIZADO")
    champ = st['wb'][3][0]
    sub   = _subcampeon(st)
    ter   = st['tercero']
    cua   = st['cuarto']
    print(f"  1. Campeones: {_equipo_label(champ)}")
    print(f"  2. 2do:       {_equipo_label(sub)}")
    print(f"  3. 3er:       {_equipo_label(ter)}")
    print(f"  4. 4to:       {_equipo_label(cua)}")
    print(f"  Imagen: {ruta}")
    print("="*60)


def _construir_partidos():
    partidos = []
    # Cuartos: 4 partidos (wb[0] tiene 8 equipos → wb[1] con 4)
    for i in range(4):
        partidos.append({
            "etapa":    "CUARTOS DE FINAL",
            "label":    f"Cuartos - Partido {i+1}",
            "src1":     f"wb[0][{2*i}]",
            "src2":     f"wb[0][{2*i+1}]",
            "dst_win":  f"wb[1][{i}]",
            "dst_lose": None,
            "ronda":    0,
        })
    # Semis: 2 partidos
    for i in range(2):
        partidos.append({
            "etapa":    "SEMIFINALES",
            "label":    f"Semifinal - Partido {i+1}",
            "src1":     f"wb[1][{2*i}]",
            "src2":     f"wb[1][{2*i+1}]",
            "dst_win":  f"wb[2][{i}]",
            "dst_lose": f"semi_loser[{i}]",
            "ronda":    1,
        })
    # 3er puesto
    partidos.append({
        "etapa":    "3ER PUESTO",
        "label":    "Partido 3er Puesto",
        "src1":     "semi_loser[0]",
        "src2":     "semi_loser[1]",
        "dst_win":  "tercero",
        "dst_lose": "cuarto",
        "ronda":    "3p",
    })
    # Gran final
    partidos.append({
        "etapa":    "GRAN FINAL",
        "label":    "Gran Final",
        "src1":     "wb[2][0]",
        "src2":     "wb[2][1]",
        "dst_win":  "wb[3][0]",
        "dst_lose": None,
        "ronda":    2,
    })
    return partidos

def _resolver(st, src):
    if src.startswith("wb["):
        r,i = map(int, re.findall(r"\d+", src)); return st["wb"][r][i]
    if src.startswith("semi_loser["):
        i = int(re.findall(r"\d+", src)[0]); return st["semifinal_losers"][i]
    return None

def _aplicar(st, p, ganador, perdedor):
    _escribir(st, p["dst_win"], ganador)
    if p.get("dst_lose"): _escribir(st, p["dst_lose"], perdedor)
    if p["ronda"] == "3p":
        st["tercero"] = ganador; st["cuarto"] = perdedor

def _escribir(st, dst, valor):
    if dst is None: return
    if dst.startswith("wb["):
        r,i = map(int, re.findall(r"\d+", dst)); st["wb"][r][i] = valor
    elif dst.startswith("semi_loser["):
        i = int(re.findall(r"\d+", dst)[0]); st["semifinal_losers"][i] = valor
    elif dst == "tercero": st["tercero"] = valor
    elif dst == "cuarto":  st["cuarto"]  = valor

if __name__ == "__main__":
    correr_torneo(EQUIPOS)