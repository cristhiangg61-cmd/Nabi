"""
Torneo_8Jugadores.py  —  Versión desde Cuartos de Final
=======================================================
Bracket de eliminación directa para 8 jugadores (2v2).

Estructura:
  · Panel superior : bracket con 3 columnas por lado
                     (CUARTOS -> SEMIFINAL -> FINAL -> CAMPEON)
  · Panel inferior : 3er Puesto (izquierda) + Podio (derecha)

Geometría del bracket (posiciones X por lado):
  0 = CUARTOS    x = ±11.0   (N = 4)
  1 = SEMIFINAL  x = ± 6.5   (N = 2)
  2 = FINAL      x = ± 2.5   (N = 1)
  Centro         x =   0.0   (Campeón)
"""

import re
import os
import copy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

# =====================================================================
#  JUGADORES  —  reemplaza estos nombres con los reales del torneo
# =====================================================================
JUGADORES = [
    "Jugador 1",  "Jugador 2",
    "Jugador 3",  "Jugador 4",
    "Jugador 5",  "Jugador 6",
    "Jugador 7",  "Jugador 8",
]

# =====================================================================
#  PALETA DE COLORES
# =====================================================================
C = {
    "bg":      "#0b0b1a",              # fondo general
    "azul":    ("#1a4a8a", "#4d9fff"), # lado izquierdo (cuartos)
    "rojo":    ("#8a1a1a", "#ff4d4d"), # lado derecho  (cuartos)
    "win":     ("#1a5c2e", "#50e87a"), # ganadores de ronda
    "final_w": ("#6b3a00", "#ffb347"), # finalistas
    "champ":   ("#5c4500", "#ffd700"), # campeón
    "silver":  ("#353535", "#c0c0c0"), # subcampeón
    "bronze":  ("#4a2800", "#cd7f32"), # 3er puesto
    "empty":   ("#0f0f20", "#252545"), # casilla vacía
    "line":    "#3a3a6a",              # conectores del bracket
    "sep":     "#2a2a50",              # separadores de sección
}

# =====================================================================
#  GEOMETRÍA — valores fijos para toda la figura
# =====================================================================

# Dimensiones de caja: iguales para todas las rondas del bracket.
BOX_W = 2.7   # ancho de cada caja
BOX_H = 0.84  # alto  de cada caja
FS    = 25    # tamaño de fuente para todas las cajas del bracket

# Separación vertical entre jugadores en cuartos.
GAP_Y  = 1.8
N_SIDE = 4    # jugadores por lado (4 por cada mitad = 8 en total)

# Posiciones X de cada columna (izquierda y derecha).
# El paso se reduce hacia el centro para dar espacio al campeón.
XS_IZQ = [-11.0, -6.5, -2.5]
XS_DER = [ 11.0,  6.5,  2.5]

# Límites del panel superior (bracket)
XLIM_TOP = (-15.5, 15.5)
YLIM_TOP = (-1.0, 8.5)

# Límites del panel inferior (3er puesto + podio)
XLIM_BOT = (0.0, 36.0)
YLIM_BOT = (0.0, 12.0)

# Posiciones Y de referencia en el panel inferior
Y_HEAD = 9.9   # encabezados de sección
Y_CONT = 7.7   # cajas de contendientes
Y_WIN  = 5.5   # caja del ganador
Y_LBL  = 4.55  # etiqueta bajo el ganador


# =====================================================================
#  ESTADO DEL TORNEO
# =====================================================================

def estado_inicial(jugadores):
    """Devuelve el estado inicial para 8 jugadores en eliminación directa."""
    return {
        "wb": [
            list(jugadores),   # ronda 0: 8 jugadores (cuartos)
            [None] * 4,        # ronda 1: 4 jugadores (semifinal)
            [None] * 2,        # ronda 2: 2 jugadores (final)
            [None] * 1,        # ronda 3: 1 jugador   (campeón)
        ],
        "semifinal_losers": [None, None],
        "tercero": None,
        "cuarto":  None,
    }


# =====================================================================
#  HELPERS DE GEOMETRÍA
# =====================================================================

def _cuartos_ys():
    """Posiciones Y de los 4 slots de cuartos (de arriba a abajo, i=0 es el tope)."""
    return [(N_SIDE - 1 - i) * GAP_Y for i in range(N_SIDE)]


def _get_y(ronda, slot, cuartos_ys):
    """
    Calcula la Y del slot en la ronda indicada de forma recursiva.
    Y(r, j) = promedio de Y(r-1, 2j) e Y(r-1, 2j+1)
    Garantiza que los conectores queden centrados exactamente.
    """
    if ronda == 0:
        return cuartos_ys[slot]
    ya = _get_y(ronda - 1, 2 * slot,     cuartos_ys)
    yb = _get_y(ronda - 1, 2 * slot + 1, cuartos_ys)
    return (ya + yb) / 2


# =====================================================================
#  PRIMITIVAS DE DIBUJO
# =====================================================================

def draw_box(ax, cx, cy, nombre, estilo, w=BOX_W, h=BOX_H, fontsize=FS, z=3):
    """
    Dibuja una caja redondeada centrada en (cx, cy).
    - nombre=None  -> caja vacía punteada semitransparente.
    - nombre!=None -> caja rellena con el texto centrado.
    """
    if nombre is None:
        fc, ec = C["empty"]
        alpha = 0.55
        ls    = "--"
        txt   = ""
    else:
        fc, ec = C[estilo]
        alpha = 1.0
        ls    = "solid"
        txt   = nombre

    ax.add_patch(FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        fc=fc, ec=ec, lw=1.8, ls=ls, alpha=alpha, zorder=z
    ))
    if txt:
        ax.text(cx, cy, txt, ha="center", va="center",
                fontsize=fontsize, color="#ffffff", fontweight="bold",
                zorder=z + 1, clip_on=True)


def draw_box_champ(ax, cx, cy, nombre, w=BOX_W*1.35, h=BOX_H*1.35, fontsize=FS+2):
    """
    Caja especial del campeón con efecto de brillo dorado en capas concéntricas.
    Tamaño proporcional: BOX_W*1.35 de ancho, BOX_H*1.35 de alto, FS+2 de fuente.
    """
    if nombre is None:
        draw_box(ax, cx, cy, None, "empty", w=w, h=h, fontsize=fontsize, z=4)
        return
    fc, ec = C["champ"]
    for i in range(4, 0, -1):
        gw = w + i * 0.28
        gh = h + i * 0.18
        ax.add_patch(FancyBboxPatch(
            (cx - gw/2, cy - gh/2), gw, gh,
            boxstyle="round,pad=0.04,rounding_size=0.16",
            fc=fc, ec=ec, lw=0, alpha=0.055 * i, zorder=4
        ))
    ax.add_patch(FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.14",
        fc=fc, ec=ec, lw=2.6, ls="solid", alpha=1.0, zorder=5
    ))
    ax.text(cx, cy, nombre, ha="center", va="center",
            fontsize=fontsize, color="#ffd700", fontweight="bold",
            zorder=6, clip_on=True)


def draw_line(ax, x1, y1, x2, y2, lw=1.5, color=None, z=1):
    ax.plot([x1, x2], [y1, y2],
            color=color or C["line"], lw=lw, zorder=z,
            solid_capstyle="round", solid_joinstyle="round")


def draw_bracket_connector(ax, x_src, y_top, y_bot, x_dst, y_mid):
    """
    Conector tipo bracket (forma de gancho horizontal).
    xm = punto medio garantiza el gancho simétrico.
    """
    xm = (x_src + x_dst) / 2
    draw_line(ax, x_src, y_top, xm,    y_top)
    draw_line(ax, x_src, y_bot, xm,    y_bot)
    draw_line(ax, xm,    y_top, xm,    y_bot)
    draw_line(ax, xm,    y_mid, x_dst, y_mid)


def draw_match_connector_horiz(ax, xa, xb, y_cont, xc, yc_top):
    """
    Conector horizontal para dos contendientes al mismo Y.
    Une los bordes internos de (xa) y (xb) hacia el punto central (xc),
    luego baja verticalmente hasta (yc_top).
    Usado en la sección de 3er Puesto del panel inferior.
    """
    edge_a = xa + BOX_W / 2
    edge_b = xb - BOX_W / 2
    draw_line(ax, edge_a, y_cont, xc,     y_cont)
    draw_line(ax, edge_b, y_cont, xc,     y_cont)
    draw_line(ax, xc,     y_cont, xc, yc_top)


def draw_medal(ax, cx, cy, pos, r=0.42):
    """
    Dibuja una medalla circular con número y etiqueta de posición.
    pos=1 -> Oro, pos=2 -> Plata, pos=3 -> Bronce.
    """
    paleta = {
        1: ("#a07800", "#ffd700", "ORO"),
        2: ("#606060", "#d8d8d8", "PLATA"),
        3: ("#7a4500", "#cd7f32", "BRONCE"),
    }
    if pos not in paleta:
        return
    fc, ec, label = paleta[pos]
    ax.add_patch(Circle((cx, cy), r + 0.07, fc=C["bg"], ec=ec, lw=2.2, zorder=5))
    ax.add_patch(Circle((cx, cy), r,         fc=fc,      ec=ec, lw=1.2, zorder=6))
    ax.text(cx, cy,           str(pos), ha="center", va="center",
            fontsize=FS + 2, color="#ffffff", fontweight="bold", zorder=7)
    ax.text(cx, cy - r - 0.52, label, ha="center", va="top",
            fontsize=FS - 5, color=ec, fontweight="bold")


# =====================================================================
#  DIBUJAR BRACKET (PANEL SUPERIOR)
# =====================================================================

def dibujar_bracket(ax, st):
    """
    Dibuja el bracket principal.
    Rondas: 0=CUARTOS, 1=SEMIFINAL, 2=FINAL, 3=CAMPEON.
    """
    cuartos_ys = _cuartos_ys()

    # RONDA 0: CUARTOS (entrada inicial)
    for i in range(4):
        y = _get_y(0, i, cuartos_ys)
        nombre = st["wb"][0][i]
        estilo = "azul" if i < 2 else "rojo"
        draw_box(ax, XS_IZQ[0] if i < 2 else XS_DER[0],
                 y, nombre, estilo, fontsize=FS, z=3)

    # RONDA 1: SEMIFINAL
    for i in range(2):
        y = _get_y(1, i, cuartos_ys)
        nombre = st["wb"][1][i]
        estilo = "win"
        draw_box(ax, XS_IZQ[1] if i == 0 else XS_DER[1],
                 y, nombre, estilo, fontsize=FS, z=3)

    # RONDA 2: FINAL
    for i in range(2):
        y = _get_y(2, i, cuartos_ys)
        nombre = st["wb"][2][i]
        estilo = "final_w"
        draw_box(ax, XS_IZQ[2] if i == 0 else XS_DER[2],
                 y, nombre, estilo, fontsize=FS, z=3)

    # RONDA 3: CAMPEON
    nombre = st["wb"][3][0]
    y_champ = _get_y(3, 0, cuartos_ys)
    draw_box_champ(ax, 0.0, y_champ, nombre, fontsize=FS)

    # CONECTORES entre rondas
    for ronda in range(3):
        xs_src = XS_IZQ if ronda < 3 else [XS_IZQ[ronda], XS_DER[ronda]]
        xs_dst = XS_IZQ if ronda < 2 else [XS_IZQ[ronda + 1], XS_DER[ronda + 1]]

        for i in range(2 ** (2 - ronda)):
            y_top = _get_y(ronda, 2*i,     cuartos_ys)
            y_bot = _get_y(ronda, 2*i + 1, cuartos_ys)
            y_mid = _get_y(ronda + 1, i,   cuartos_ys)

            if ronda == 0:
                x_src = XS_IZQ[0] if i < 2 else XS_DER[0]
            elif ronda == 1:
                x_src = XS_IZQ[1] if i == 0 else XS_DER[1]
            else:
                x_src = XS_IZQ[2] if i == 0 else XS_DER[2]

            if ronda < 2:
                x_dst = XS_IZQ[ronda + 1] if (ronda == 0 and i < 2) or (ronda == 1 and i == 0) else XS_DER[ronda + 1]
            else:
                x_dst = 0.0

            draw_bracket_connector(ax, x_src, y_top, y_bot, x_dst, y_mid)

    # Configurar límites y aspecto
    ax.set_xlim(*XLIM_TOP)
    ax.set_ylim(*YLIM_TOP)
    ax.set_aspect("equal")
    ax.axis("off")


# =====================================================================
#  DIBUJAR PANEL INFERIOR (3ER PUESTO + PODIO)
# =====================================================================

def dibujar_panel_inferior(ax, st):
    """
    Panel inferior con dos secciones:
    - Izquierda: 3er Puesto (losers de semifinal compiten)
    - Derecha: Podio de Campeones (1-2-3-4 posiciones)
    """
    BOT_W = 2.8
    BOT_H = 0.75
    FS_BOT = FS - 3

    # SECCIÓN IZQUIERDA: 3ER PUESTO
    # ─────────────────────────────
    ax.text(9.0, Y_HEAD, "3ER PUESTO", ha="left", va="center",
            fontsize=FS_BOT + 2, fontweight="bold", color="#cd7f32")

    p1_3 = st["semifinal_losers"][0]
    p2_3 = st["semifinal_losers"][1]

    XL1_3, XL2_3 = 6.0, 12.0
    draw_box(ax, XL1_3, Y_CONT, p1_3, "empty" if p1_3 is None else "win",
             w=BOT_W, h=BOT_H, fontsize=FS_BOT, z=3)
    draw_box(ax, XL2_3, Y_CONT, p2_3, "empty" if p2_3 is None else "win",
             w=BOT_W, h=BOT_H, fontsize=FS_BOT, z=3)

    if p1_3 is not None and p2_3 is not None:
        draw_match_connector_horiz(ax, XL1_3, XL2_3, Y_CONT, 9.0, Y_WIN)

    ganador_3 = st["tercero"]
    draw_box(ax, 9.0, Y_WIN, ganador_3, "empty" if ganador_3 is None else "bronze",
             w=BOT_W, h=BOT_H, fontsize=FS_BOT, z=3)
    ax.text(9.0, Y_LBL - 0.65, "3er Lugar", ha="center", va="center",
            fontsize=FS_BOT - 2, color="#cd7f32", fontweight="bold")

    # SECCIÓN DERECHA: PODIO
    # ────────────────────
    ax.text(28.0, Y_HEAD, "PODIO FINAL", ha="left", va="center",
            fontsize=FS_BOT + 2, fontweight="bold", color="#dde0ff")

    posiciones = [
        (st["wb"][3][0], "champ",  "CAMPEÓN"),
        (_subcampeon(st), "silver", "SUBCAMPEÓN"),
        (st["tercero"], "bronze", "BRONCE"),
        (st["cuarto"], "empty",  "4TO LUGAR"),
    ]

    ROW = 0.95
    for pos, (nombre, estilo, lbl) in enumerate(posiciones, 1):
        yp = 8.6 - (pos - 1) * ROW
        color_lbl = {"champ": "#ffd700", "silver": "#d8d8d8", "bronze": "#cd7f32", "empty": "#888888"}.get(estilo, "#dde0ff")

        if pos <= 3:
            draw_medal(ax, 26.0 - 3.5, yp, pos, r=0.39)
        else:
            ax.text(26.0 - 3.5, yp, "4to", ha="center", va="center",
                    fontsize=FS_BOT, fontweight="bold", color=color_lbl, zorder=5)

        ax.text(26.0 - 2.0, yp + 0.10, lbl, ha="left", va="center",
                fontsize=FS_BOT, fontweight="bold", color=color_lbl)

        draw_box(ax, 26.0 + 3.5, yp, nombre, estilo if nombre else "empty",
                 w=BOT_W, h=BOT_H, fontsize=FS_BOT, z=3)

    # Límites y configuración
    ax.set_xlim(*XLIM_BOT)
    ax.set_ylim(*YLIM_BOT)
    ax.set_aspect("equal")
    ax.axis("off")


def _subcampeon(st):
    """Devuelve el nombre del subcampeón."""
    if len(st["wb"]) > 2 and len(st["wb"][2]) > 1:
        return st["wb"][2][1]
    return None


# =====================================================================
#  RENDER PRINCIPAL
# =====================================================================

def render(st, banner=None, ruta=None, dpi=130):
    """
    Genera y guarda la imagen completa del torneo.
    Figura: 28 x 14 pulgadas a 130 DPI = 3640 x 1820 px.
    """
    fig = plt.figure(figsize=(28, 14), facecolor=C["bg"])
    gs  = fig.add_gridspec(
        2, 1,
        height_ratios=[1.8, 1.0],
        hspace=0.03,
        top=0.93, bottom=0.02,
        left=0.01, right=0.99,
    )
    ax_top = fig.add_subplot(gs[0])
    ax_bot = fig.add_subplot(gs[1])

    dibujar_bracket(ax_top, st)
    dibujar_panel_inferior(ax_bot, st)

    # Título principal
    fig.suptitle(
        "TORNEO 8 JUGADORES  —  2 VS 2  —  ELIMINACION DIRECTA",
        fontsize=24, fontweight="bold", color="#dde0ff",
        y=0.97, fontfamily="DejaVu Sans",
    )

    if banner:
        fig.text(
            0.5, 0.935, banner,
            ha="center", va="top",
            fontsize=18, fontweight="bold", color="#ffe08a",
            bbox=dict(boxstyle="round,pad=0.4",
                      fc="#140f00", ec="#b8860b", lw=1.6),
        )

    if ruta:
        fig.savefig(ruta, bbox_inches="tight", dpi=dpi,
                    facecolor=C["bg"], pad_inches=0.12)
    plt.close(fig)


# =====================================================================
#  LÓGICA DEL TORNEO
# =====================================================================

def pedir_ganador(p1, p2, etiqueta):
    """Solicita por consola quién avanza en el partido indicado."""
    print(f"\n  --- {etiqueta} ---")
    print(f"  [1]  {p1}")
    print(f"  [2]  {p2}")
    print(f"  [0]  RETROCEDER")
    while True:
        raw = input("  Quien avanza? (1 / 2 / 0): ").strip()
        if raw == "0": return "RETROCEDER"
        if raw == "1": return p1, p2
        if raw == "2": return p2, p1
        print("  Ingresa 1, 2 o 0.")


def correr_torneo(jugadores, out_dir=None):
    """
    Ejecuta el torneo de forma interactiva por consola.
    Por cada partido solicita el ganador y actualiza la imagen.
    Permite retroceder partidos con la opción 0.
    """
    if out_dir is None:
        try:    out_dir = os.path.dirname(os.path.abspath(__file__))
        except: out_dir = os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    ruta_actual = os.path.join(out_dir, "actual.png")

    partidos     = _construir_partidos(jugadores)
    st           = estado_inicial(jugadores)
    historial    = []
    sets_jugados = 0

    # Banner inicial
    render(st, banner="Esperando el primer partido...", ruta=ruta_actual)
    print("\n" + "="*60)
    print("  TORNEO 8 JUGADORES (2 VS 2) - ELIMINACION DIRECTA")
    print("  Comienza en CUARTOS DE FINAL")
    print("  [0] en cualquier momento para RETROCEDER")
    print("="*60)

    idx = 0
    while idx < len(partidos):
        p  = partidos[idx]
        n1 = _resolver(st, p["src1"])
        n2 = _resolver(st, p["src2"])
        if n1 is None or n2 is None:
            idx += 1
            continue

        print(f"\n{'='*60}\n  {p['etapa']}\n{'='*60}")
        resultado = pedir_ganador(n1, n2, p["label"])

        if resultado == "RETROCEDER":
            if not historial:
                print("  No hay partidos anteriores para deshacer.")
            else:
                st, prev_idx = historial.pop()
                idx          = prev_idx
                sets_jugados = max(0, sets_jugados - 1)
                print("Partido deshecho.")
                # Banner de retroceso
                render(st, banner=f"Partido deshecho  —  Retrocediendo al SET {sets_jugados}", ruta=ruta_actual)
            continue

        ganador, perdedor = resultado
        historial.append((copy.deepcopy(st), idx))
        _aplicar(st, p, ganador, perdedor)
        sets_jugados += 1
        # Banner de partido
        render(st,
               banner=f"Partido {sets_jugados}  ·  {p['label']}  ->  avanzó  {ganador}",
               ruta=ruta_actual)
        print(f"  Avanza: {ganador}")
        idx += 1

    print(f"\n{'='*60}")
    print("  TORNEO FINALIZADO")
    print(f"  1. Campeón:  {st['wb'][3][0]}")
    print(f"  2. 2do:      {_subcampeon(st)}")
    print(f"  3. 3er:      {st['tercero']}")
    print(f"  4. 4to:      {st['cuarto']}")
    print(f"  Imagen: {ruta_actual}")
    print("="*60)


# =====================================================================
#  CONSTRUCCIÓN DE PARTIDOS
# =====================================================================

def _construir_partidos(jugadores):
    """Construye la lista ordenada de partidos para eliminación directa desde CUARTOS."""
    partidos = []

    for r, (etapa, n) in enumerate([
        ("CUARTOS DE FINAL", 4),
        ("SEMIFINALES",      2),
    ]):
        for i in range(n):
            partidos.append({
                "etapa":    etapa,
                "label":    f"{etapa.title()} - Partido {i+1}",
                "src1":     f"wb[{r}][{2*i}]",
                "src2":     f"wb[{r}][{2*i+1}]",
                "dst_win":  f"wb[{r+1}][{i}]",
                "dst_lose": f"semi_loser[{i}]" if r == 1 else None,
                "ronda":    r,
            })

    partidos.append({
        "etapa":    "3ER PUESTO",
        "label":    "Partido 3er Puesto",
        "src1":     "semi_loser[0]",
        "src2":     "semi_loser[1]",
        "dst_win":  "tercero",
        "dst_lose": "cuarto",
        "ronda":    "3p",
    })

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
    """Devuelve el jugador en la posición indicada por src."""
    if src.startswith("wb["):
        r, i = map(int, re.findall(r"\d+", src))
        return st["wb"][r][i]
    if src.startswith("semi_loser["):
        i = int(re.findall(r"\d+", src)[0])
        return st["semifinal_losers"][i]
    return None


def _aplicar(st, p, ganador, perdedor):
    """Escribe el resultado del partido en el estado del torneo."""
    _escribir(st, p["dst_win"], ganador)
    if p.get("dst_lose"):
        _escribir(st, p["dst_lose"], perdedor)
    if p["ronda"] == "3p":
        st["tercero"] = ganador
        st["cuarto"]  = perdedor


def _escribir(st, dst, valor):
    """Actualiza una posición del estado a partir de su clave de destino."""
    if dst is None:
        return
    if dst.startswith("wb["):
        r, i = map(int, re.findall(r"\d+", dst))
        st["wb"][r][i] = valor
    elif dst.startswith("semi_loser["):
        i = int(re.findall(r"\d+", dst)[0])
        st["semifinal_losers"][i] = valor
    elif dst == "tercero":
        st["tercero"] = valor
    elif dst == "cuarto":
        st["cuarto"]  = valor


# =====================================================================
if __name__ == "__main__":
    correr_torneo(JUGADORES)