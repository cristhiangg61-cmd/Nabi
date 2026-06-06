import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import json
import copy

# ==========================================================
# CONFIGURACIÓN VISUAL
# ==========================================================

COLORS = {
    "bg": "#080812",
    "panel": "#0d0d1e",

    "azul_bg": "#0e1f3d",
    "azul_bd": "#2d6fdd",
    "azul_tx": "#7ab8ff",

    "rojo_bg": "#3d0e0e",
    "rojo_bd": "#dd2d2d",
    "rojo_tx": "#ff7a7a",

    "win_bg": "#0e2e1a",
    "win_bd": "#27a050",
    "win_tx": "#50e87a",

    "champ_bg": "#2a1a00",
    "champ_bd": "#cc8800",
    "champ_tx": "#ffd700",

    "silver_bg": "#1c1c1c",
    "silver_bd": "#909090",
    "silver_tx": "#d0d0d0",

    "bronze_bg": "#2a1400",
    "bronze_bd": "#a05a20",
    "bronze_tx": "#cd7f32",

    "line": "#404070",
    "text": "#ffffff"
}

TEAM_W = 180
TEAM_H = 54

DEFAULT_TEAMS = [
    ["Jugador 1","Jugador 2"],
    ["Jugador 3","Jugador 4"],
    ["Jugador 5","Jugador 6"],
    ["Jugador 7","Jugador 8"],
    ["Jugador 9","Jugador 10"],
    ["Jugador 11","Jugador 12"],
    ["Jugador 13","Jugador 14"],
    ["Jugador 15","Jugador 16"],
]

# ==========================================================
# MODELO
# ==========================================================

class TournamentState:

    def __init__(self, teams):

        self.wb = [
            copy.deepcopy(teams),
            [None,None,None,None],
            [None,None],
            [None]
        ]

        self.semifinal_losers = [None,None]

        self.third = None
        self.fourth = None

    def clone(self):
        return copy.deepcopy(self)


def team_name(team):

    if not team:
        return "???"

    return f"{team[0]} & {team[1]}"


def get_runner_up(state):

    final_a = state.wb[2][0]
    final_b = state.wb[2][1]
    champ = state.wb[3][0]

    if not champ:
        return None

    if champ == final_a:
        return final_b

    return final_a


# ==========================================================
# BLOQUE VISUAL DE EQUIPO
# ==========================================================

class TeamBox:

    def __init__(
        self,
        canvas,
        x,
        y,
        team=None,
        style="azul"
    ):

        self.canvas = canvas

        self.x = x
        self.y = y

        self.team = team
        self.style = style

        self.items = []

        self.draw()

    def palette(self):

        if self.style == "azul":
            return (
                COLORS["azul_bg"],
                COLORS["azul_bd"],
                COLORS["azul_tx"]
            )

        if self.style == "rojo":
            return (
                COLORS["rojo_bg"],
                COLORS["rojo_bd"],
                COLORS["rojo_tx"]
            )

        if self.style == "win":
            return (
                COLORS["win_bg"],
                COLORS["win_bd"],
                COLORS["win_tx"]
            )

        if self.style == "champ":
            return (
                COLORS["champ_bg"],
                COLORS["champ_bd"],
                COLORS["champ_tx"]
            )

        if self.style == "silver":
            return (
                COLORS["silver_bg"],
                COLORS["silver_bd"],
                COLORS["silver_tx"]
            )

        if self.style == "bronze":
            return (
                COLORS["bronze_bg"],
                COLORS["bronze_bd"],
                COLORS["bronze_tx"]
            )

        return (
            "#111111",
            "#333333",
            "#aaaaaa"
        )

    def clear(self):

        for item in self.items:
            self.canvas.delete(item)

        self.items.clear()

    def draw(self):

        self.clear()

        bg, bd, tx = self.palette()

        x = self.x
        y = self.y

        r = self.canvas.create_rectangle(
            x,
            y,
            x + TEAM_W,
            y + TEAM_H,
            fill=bg,
            outline=bd,
            width=2
        )

        self.items.append(r)

        p1 = ""
        p2 = ""

        if self.team:
            p1 = self.team[0]
            p2 = self.team[1]

        t1 = self.canvas.create_text(
            x + 8,
            y + 15,
            text=f"① {p1}",
            anchor="w",
            fill="white",
            font=("Segoe UI",10,"bold")
        )

        t2 = self.canvas.create_text(
            x + 8,
            y + 40,
            text=f"② {p2}",
            anchor="w",
            fill="white",
            font=("Segoe UI",10)
        )

        self.items.extend([t1,t2])

    def update_team(self, team, style=None):

        self.team = team

        if style:
            self.style = style

        self.draw()

# ==========================================================
# DIALOGO DE PARTIDO
# ==========================================================

class MatchDialog(tk.Toplevel):

    def __init__(self,parent,team1,team2):

        super().__init__(parent)

        self.result = None

        self.title("Seleccionar ganador")

        self.configure(bg="#13132a")

        self.geometry("500x250")

        self.transient(parent)
        self.grab_set()

        title = tk.Label(
            self,
            text="¿QUIÉN AVANZA?",
            bg="#13132a",
            fg="#ffd700",
            font=("Segoe UI",14,"bold")
        )

        title.pack(pady=15)

        frame = tk.Frame(self,bg="#13132a")
        frame.pack(expand=True)

        left = tk.Button(
            frame,
            text=team_name(team1),
            width=20,
            command=lambda:self.choose(team1)
        )

        left.grid(row=0,column=0,padx=20)

        tk.Label(
            frame,
            text="VS",
            bg="#13132a",
            fg="white",
            font=("Segoe UI",14,"bold")
        ).grid(row=0,column=1)

        right = tk.Button(
            frame,
            text=team_name(team2),
            width=20,
            command=lambda:self.choose(team2)
        )

        right.grid(row=0,column=2,padx=20)

    def choose(self,team):
        self.result = team
        self.destroy()


# ==========================================================
# EDITOR DE EQUIPOS
# ==========================================================

class EditTeamsDialog(tk.Toplevel):

    def __init__(self,parent,teams):

        super().__init__(parent)

        self.title("Editar equipos")

        self.result = None

        self.entries = []

        frm = tk.Frame(self)
        frm.pack(padx=10,pady=10)

        for i,eq in enumerate(teams):

            tk.Label(
                frm,
                text=f"Equipo {i+1}"
            ).grid(row=i,column=0)

            e1 = tk.Entry(frm,width=20)
            e1.insert(0,eq[0])
            e1.grid(row=i,column=1)

            e2 = tk.Entry(frm,width=20)
            e2.insert(0,eq[1])
            e2.grid(row=i,column=2)

            self.entries.append((e1,e2))

        tk.Button(
            self,
            text="Guardar",
            command=self.save
        ).pack(pady=10)

    def save(self):

        teams = []

        for e1,e2 in self.entries:

            teams.append([
                e1.get().strip(),
                e2.get().strip()
            ])

        self.result = teams

        self.destroy()

# ==========================================================
# DIALOGO DE PARTIDO
# ==========================================================

class MatchDialog(tk.Toplevel):

    def __init__(self,parent,team1,team2):

        super().__init__(parent)

        self.result = None

        self.title("Seleccionar ganador")

        self.configure(bg="#13132a")

        self.geometry("500x250")

        self.transient(parent)
        self.grab_set()

        title = tk.Label(
            self,
            text="¿QUIÉN AVANZA?",
            bg="#13132a",
            fg="#ffd700",
            font=("Segoe UI",14,"bold")
        )

        title.pack(pady=15)

        frame = tk.Frame(self,bg="#13132a")
        frame.pack(expand=True)

        left = tk.Button(
            frame,
            text=team_name(team1),
            width=20,
            command=lambda:self.choose(team1)
        )

        left.grid(row=0,column=0,padx=20)

        tk.Label(
            frame,
            text="VS",
            bg="#13132a",
            fg="white",
            font=("Segoe UI",14,"bold")
        ).grid(row=0,column=1)

        right = tk.Button(
            frame,
            text=team_name(team2),
            width=20,
            command=lambda:self.choose(team2)
        )

        right.grid(row=0,column=2,padx=20)

    def choose(self,team):
        self.result = team
        self.destroy()


# ==========================================================
# EDITOR DE EQUIPOS
# ==========================================================

class EditTeamsDialog(tk.Toplevel):

    def __init__(self,parent,teams):

        super().__init__(parent)

        self.title("Editar equipos")

        self.result = None

        self.entries = []

        frm = tk.Frame(self)
        frm.pack(padx=10,pady=10)

        for i,eq in enumerate(teams):

            tk.Label(
                frm,
                text=f"Equipo {i+1}"
            ).grid(row=i,column=0)

            e1 = tk.Entry(frm,width=20)
            e1.insert(0,eq[0])
            e1.grid(row=i,column=1)

            e2 = tk.Entry(frm,width=20)
            e2.insert(0,eq[1])
            e2.grid(row=i,column=2)

            self.entries.append((e1,e2))

        tk.Button(
            self,
            text="Guardar",
            command=self.save
        ).pack(pady=10)

    def save(self):

        teams = []

        for e1,e2 in self.entries:

            teams.append([
                e1.get().strip(),
                e2.get().strip()
            ])

        self.result = teams

        self.destroy()

# ==========================================================
# APP PRINCIPAL
# ==========================================================

class TournamentApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Torneo 2 vs 2")
        self.geometry("1500x900")
        self.configure(bg=COLORS["bg"])

        self.teams = copy.deepcopy(DEFAULT_TEAMS)

        self.state = TournamentState(self.teams)

        self.history = []

        self.drag_box = None
        self.drag_start = None

        self.create_toolbar()
        self.create_canvas()
        self.create_podium()

        self.draw_bracket()

    # ------------------------------------------------------

    def create_toolbar(self):

        top = tk.Frame(
            self,
            bg=COLORS["panel"]
        )

        top.pack(fill="x")

        tk.Button(
            top,
            text="Editar Equipos",
            command=self.edit_teams
        ).pack(side="left",padx=5,pady=5)

        tk.Button(
            top,
            text="Deshacer",
            command=self.undo
        ).pack(side="left",padx=5)

        tk.Button(
            top,
            text="Reiniciar",
            command=self.reset_tournament
        ).pack(side="left",padx=5)

        tk.Button(
            top,
            text="Guardar JSON",
            command=self.save_json
        ).pack(side="left",padx=5)

        tk.Button(
            top,
            text="Cargar JSON",
            command=self.load_json
        ).pack(side="left",padx=5)

        self.status = tk.Label(
            top,
            text="Seleccione un partido",
            fg="white",
            bg=COLORS["panel"]
        )

        self.status.pack(side="right",padx=20)

    # ------------------------------------------------------

    def create_canvas(self):

        self.canvas = tk.Canvas(
            self,
            bg=COLORS["bg"],
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

    # ------------------------------------------------------

    def create_podium(self):

        self.podium_frame = tk.Frame(
            self,
            bg=COLORS["panel"]
        )

        self.podium_frame.pack(
            fill="x",
            pady=5
        )

        self.lbl_gold = tk.Label(
            self.podium_frame,
            text="🥇 ---",
            fg="gold",
            bg=COLORS["panel"],
            font=("Segoe UI",12,"bold")
        )

        self.lbl_silver = tk.Label(
            self.podium_frame,
            text="🥈 ---",
            fg="lightgray",
            bg=COLORS["panel"]
        )

        self.lbl_bronze = tk.Label(
            self.podium_frame,
            text="🥉 ---",
            fg="#cd7f32",
            bg=COLORS["panel"]
        )

        self.lbl_fourth = tk.Label(
            self.podium_frame,
            text="4° ---",
            fg="white",
            bg=COLORS["panel"]
        )

        self.lbl_gold.pack()
        self.lbl_silver.pack()
        self.lbl_bronze.pack()
        self.lbl_fourth.pack()

    # ------------------------------------------------------

    def update_podium(self):

        champ = self.state.wb[3][0]
        runner = get_runner_up(self.state)

        third = self.state.third
        fourth = self.state.fourth

        self.lbl_gold.config(
            text=f"🥇 {team_name(champ) if champ else '---'}"
        )

        self.lbl_silver.config(
            text=f"🥈 {team_name(runner) if runner else '---'}"
        )

        self.lbl_bronze.config(
            text=f"🥉 {team_name(third) if third else '---'}"
        )

        self.lbl_fourth.config(
            text=f"4° {team_name(fourth) if fourth else '---'}"
        )

    # ------------------------------------------------------

    def push_history(self):

        self.history.append(
            self.state.clone()
        )

    # ------------------------------------------------------

    def undo(self):

        if not self.history:
            return

        self.state = self.history.pop()

        self.draw_bracket()

    # ------------------------------------------------------

    def reset_tournament(self):

        self.state = TournamentState(self.teams)

        self.history.clear()

        self.draw_bracket()

    # ------------------------------------------------------

    def save_json(self):

        data = {
            "teams": self.teams,
            "state": {
                "wb": self.state.wb,
                "semifinal_losers": self.state.semifinal_losers,
                "third": self.state.third,
                "fourth": self.state.fourth
            }
        }

        with open(
            "torneo_guardado.json",
            "w",
            encoding="utf8"
        ) as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        messagebox.showinfo(
            "Guardado",
            "Torneo guardado"
        )

    # ------------------------------------------------------

    def load_json(self):

        try:

            with open(
                "torneo_guardado.json",
                "r",
                encoding="utf8"
            ) as f:

                data = json.load(f)

            self.teams = data["teams"]

            self.state = TournamentState(self.teams)

            self.state.wb = data["state"]["wb"]

            self.state.semifinal_losers = data["state"]["semifinal_losers"]

            self.state.third = data["state"]["third"]

            self.state.fourth = data["state"]["fourth"]

            self.draw_bracket()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # ------------------------------------------------------

    def edit_teams(self):

        dlg = EditTeamsDialog(
            self,
            self.teams
        )

        self.wait_window(dlg)

        if dlg.result:

            self.teams = dlg.result

            self.state = TournamentState(
                self.teams
            )

            self.draw_bracket()

    # ------------------------------------------------------

    def choose_match(self, team1, team2, callback):

        dlg = MatchDialog(
            self,
            team1,
            team2
        )

        self.wait_window(dlg)

        if dlg.result:

            callback(dlg.result)

    # ------------------------------------------------------

    def draw_team(self, x, y, team, style):

        box = TeamBox(
            self.canvas,
            x,
            y,
            team,
            style
        )

        return box

    # ------------------------------------------------------

    def draw_bracket(self):

        self.canvas.delete("all")

        qx_left = 40
        sx_left = 350
        fx_left = 680

        qx_right = 1050
        sx_right = 760

        start_y = 60
        gap = 90

        quarter_boxes = []

        # CUARTOS IZQ

        for i in range(4):

            team = self.state.wb[0][i]

            y = start_y + i*gap

            quarter_boxes.append(
                self.draw_team(
                    qx_left,
                    y,
                    team,
                    "azul"
                )
            )

        # CUARTOS DER

        for i in range(4):

            team = self.state.wb[0][i+4]

            y = start_y + i*gap

            quarter_boxes.append(
                self.draw_team(
                    qx_right,
                    y,
                    team,
                    "rojo"
                )
            )

        # --------------------------------------------------
        # BOTONES CUARTOS
        # --------------------------------------------------

        for pair in range(4):

            t1 = self.state.wb[0][pair*2]
            t2 = self.state.wb[0][pair*2+1]

            if t1 and t2 and self.state.wb[1][pair] is None:

                btn = tk.Button(
                    self.canvas,
                    text="Jugar"
                )

                def make_callback(index,p1,p2):

                    return lambda : self.choose_match(
                        p1,
                        p2,
                        lambda winner:
                        self.set_quarter_winner(
                            index,
                            winner,
                            p1,
                            p2
                        )
                    )

                btn.configure(
                    command=make_callback(
                        pair,
                        t1,
                        t2
                    )
                )

                self.canvas.create_window(
                    250 if pair < 2 else 900,
                    110 + pair*180,
                    window=btn
                )

        self.draw_semis()
        self.draw_final()

        self.update_podium()

    # ------------------------------------------------------

    def set_quarter_winner(
        self,
        index,
        winner,
        p1,
        p2
    ):

        self.push_history()

        self.state.wb[1][index] = winner

        self.status.config(
            text=f"Cuartos → {team_name(winner)}"
        )

        self.draw_bracket()

    # ------------------------------------------------------

    def draw_semis(self):

        for i in range(4):

            team = self.state.wb[1][i]

            if team:

                x = 350 if i < 2 else 760

                y = 110 + (i%2)*180

                self.draw_team(
                    x,
                    y,
                    team,
                    "win"
                )

        # SEMI IZQ

        if (
            self.state.wb[1][0]
            and
            self.state.wb[1][1]
            and
            self.state.wb[2][0] is None
        ):

            btn = tk.Button(
                self.canvas,
                text="Semifinal"
            )

            btn.configure(
                command=lambda:
                self.play_semifinal(
                    0,
                    self.state.wb[1][0],
                    self.state.wb[1][1]
                )
            )

            self.canvas.create_window(
                520,
                210,
                window=btn
            )

        # SEMI DER

        if (
            self.state.wb[1][2]
            and
            self.state.wb[1][3]
            and
            self.state.wb[2][1] is None
        ):

            btn = tk.Button(
                self.canvas,
                text="Semifinal"
            )

            btn.configure(
                command=lambda:
                self.play_semifinal(
                    1,
                    self.state.wb[1][2],
                    self.state.wb[1][3]
                )
            )

            self.canvas.create_window(
                920,
                210,
                window=btn
            )

    # ------------------------------------------------------

    def play_semifinal(
        self,
        index,
        t1,
        t2
    ):

        self.choose_match(
            t1,
            t2,
            lambda winner:
            self.finish_semifinal(
                index,
                winner,
                t1,
                t2
            )
        )

    # ------------------------------------------------------

    def finish_semifinal(
        self,
        index,
        winner,
        t1,
        t2
    ):

        self.push_history()

        loser = t2 if winner == t1 else t1

        self.state.wb[2][index] = winner

        self.state.semifinal_losers[index] = loser

        self.draw_bracket()

    # ------------------------------------------------------

    def draw_final(self):

        fin1 = self.state.wb[2][0]
        fin2 = self.state.wb[2][1]

        if fin1:
            self.draw_team(
                620,
                400,
                fin1,
                "champ"
            )

        if fin2:
            self.draw_team(
                840,
                400,
                fin2,
                "champ"
            )

        if (
            fin1 and fin2
            and
            self.state.wb[3][0] is None
        ):

            btn = tk.Button(
                self.canvas,
                text="GRAN FINAL"
            )

            btn.configure(
                command=lambda:
                self.play_final(
                    fin1,
                    fin2
                )
            )

            self.canvas.create_window(
                760,
                500,
                window=btn
            )

        if self.state.wb[3][0]:

            self.draw_team(
                670,
                620,
                self.state.wb[3][0],
                "champ"
            )

    # ------------------------------------------------------

    def play_final(
        self,
        t1,
        t2
    ):

        self.choose_match(
            t1,
            t2,
            lambda winner:
            self.finish_final(
                winner,
                t1,
                t2
            )
        )

    # ------------------------------------------------------

    def finish_final(
        self,
        winner,
        t1,
        t2
    ):

        self.push_history()

        loser = t2 if winner == t1 else t1

        self.state.wb[3][0] = winner

        sl1 = self.state.semifinal_losers[0]
        sl2 = self.state.semifinal_losers[1]

        if sl1 and sl2:

            dlg = MatchDialog(
                self,
                sl1,
                sl2
            )

            self.wait_window(dlg)

            if dlg.result:

                self.state.third = dlg.result

                self.state.fourth = (
                    sl2
                    if dlg.result == sl1
                    else sl1
                )

        self.draw_bracket()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    app = TournamentApp()

    app.mainloop()