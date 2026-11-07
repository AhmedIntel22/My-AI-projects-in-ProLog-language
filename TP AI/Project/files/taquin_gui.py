import tkinter as tk
from tkinter import ttk
import threading

from taquin_solver import (
    GOAL_STATE, INITIAL_STATE,
    dfs, bfs, dfs_limited_incremental, astar,
    get_neighbors,
)

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#F0EEE9"
PANEL_BG  = "#FFFFFF"
TILE_BG   = "#D6D3C8"
TILE_FG   = "#1E1E1C"
BLANK_BG  = "#E8E6E0"
CORRECT   = "#A8D070"
ACCENT    = "#1A5FA8"
ACCENT_LT = "#E3EFF9"
ACCENT_DK = "#0D3F72"
BTN_FG    = "#FFFFFF"
MUTED     = "#888680"
TEXT      = "#1E1E1C"
BORDER    = "#CCCAC0"

FONT    = ("Segoe UI", 10)
FONT_B  = ("Segoe UI", 10, "bold")
FONT_LG = ("Segoe UI", 18, "bold")
FONT_SM = ("Segoe UI", 9)
FONT_H  = ("Segoe UI", 9, "bold")
FONT_XL = ("Segoe UI", 22, "bold")


def make_panel(parent, title=""):
    frame = tk.Frame(parent, bg=PANEL_BG, bd=1, relief="solid",
                     highlightbackground=BORDER, highlightthickness=1)
    if title:
        tk.Label(frame, text=title.upper(), bg=PANEL_BG, fg=MUTED,
                 font=FONT_SM, anchor="w").pack(fill=tk.X, padx=12, pady=(8, 4))
    return frame


def flat_btn(parent, text, cmd, primary=False, danger=False):
    kw = dict(font=FONT_SM, text=text, command=cmd,
              relief="flat", bd=0, padx=12, pady=6, cursor="hand2")
    if primary:
        kw.update(bg=ACCENT, fg=BTN_FG,
                  activebackground=ACCENT_DK, activeforeground=BTN_FG)
    elif danger:
        kw.update(bg="#A32D2D", fg=BTN_FG,
                  activebackground="#701F1F", activeforeground=BTN_FG)
    else:
        kw.update(bg="#E4E2DC", fg=TEXT,
                  activebackground=BORDER, activeforeground=TEXT)
    return tk.Button(parent, **kw)


class StatCard(tk.Frame):
    def __init__(self, parent, label):
        super().__init__(parent, bg=PANEL_BG, bd=1, relief="solid",
                         highlightbackground=BORDER, highlightthickness=1)
        self._var = tk.StringVar(value="—")
        tk.Label(self, textvariable=self._var, font=FONT_XL,
                 bg=PANEL_BG, fg=TEXT).pack(pady=(10, 0))
        tk.Label(self, text=label, font=FONT_SM,
                 bg=PANEL_BG, fg=MUTED).pack(pady=(0, 10))

    def set(self, v):
        self._var.set(str(v))


class TaquinApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Taquin Solver")
        self.configure(bg=BG)
        self.resizable(False, False)

        # Fixed window size, centred on screen
        W, H = 960, 640
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

        self.current_state = [row[:] for row in INITIAL_STATE]
        self.solution_path = []
        self.step_index    = 0
        self.auto_job      = None
        self.solving       = False

        self._build_ui()
        self._render_board(self.init_tiles, self.current_state, interactive=True)
        self._render_board(self.goal_tiles, GOAL_STATE,         interactive=False)
        self._render_board(self.sol_tiles,  self.current_state, interactive=False)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top status bar
        self.status_var = tk.StringVar(
            value="  Ready — select an algorithm and press Solve.")
        self.status_widget = tk.Label(
            self, textvariable=self.status_var, font=FONT_SM,
            bg=ACCENT_LT, fg=ACCENT, anchor="w", padx=14, pady=6)
        self.status_widget.pack(fill=tk.X, side=tk.TOP)

        # Main body: LEFT | RIGHT
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        left  = tk.Frame(body, bg=BG, width=390)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ══════════════════════════════════════════════════
        # LEFT COLUMN
        # ══════════════════════════════════════════════════

        # Row 1 — two boards
        boards_row = tk.Frame(left, bg=BG)
        boards_row.pack(fill=tk.X, pady=(0, 8))
        self._board_card(boards_row, "Initial State", "init", True
                         ).pack(side=tk.LEFT, padx=(0, 8))
        self._board_card(boards_row, "Goal State", "goal", False
                         ).pack(side=tk.LEFT)

        # Row 2 — algorithm selector
        algo_card = make_panel(left, "Algorithm")
        algo_card.pack(fill=tk.X, pady=(0, 8))

        tab_row = tk.Frame(algo_card, bg=PANEL_BG)
        tab_row.pack(padx=12, pady=(0, 8), anchor="w")

        self.algo_var  = tk.StringVar(value="astar")
        self.algo_btns = {}
        for lbl, val in [("DFS", "dfs"), ("BFS", "bfs"),
                          ("Depth-Limited", "dfs_limited"), ("A*", "astar")]:
            b = tk.Button(tab_row, text=lbl, font=FONT_SM,
                          bg=PANEL_BG, fg=MUTED, relief="solid",
                          bd=1, padx=10, pady=4, cursor="hand2",
                          command=lambda v=val: self._select_algo(v))
            b.pack(side=tk.LEFT, padx=(0, 5))
            self.algo_btns[val] = b

        # depth-limit slider — build BEFORE calling _select_algo
        self.depth_frame = tk.Frame(algo_card, bg=PANEL_BG)
        tk.Label(self.depth_frame, text="Depth limit  L :", font=FONT_SM,
                 bg=PANEL_BG, fg=MUTED).pack(side=tk.LEFT)
        self.depth_var = tk.IntVar(value=10)
        ttk.Scale(self.depth_frame, from_=1, to=30, variable=self.depth_var,
                  orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT, padx=6)
        self.depth_lbl = tk.Label(self.depth_frame, text="10", font=FONT_B,
                                  bg=PANEL_BG, fg=TEXT, width=3)
        self.depth_lbl.pack(side=tk.LEFT)
        self.depth_var.trace_add("write",
            lambda *_: self.depth_lbl.config(text=str(self.depth_var.get())))

        self._select_algo("astar")   # safe — depth_frame already exists

        act_row = tk.Frame(algo_card, bg=PANEL_BG)
        act_row.pack(padx=12, pady=(4, 12), anchor="w")
        flat_btn(act_row, "Solve",       self._run_algo, primary=True).pack(side=tk.LEFT, padx=(0, 6))
        flat_btn(act_row, "Compare All", self._run_all              ).pack(side=tk.LEFT, padx=(0, 6))
        flat_btn(act_row, "Shuffle",     self._shuffle              ).pack(side=tk.LEFT, padx=(0, 6))
        flat_btn(act_row, "Reset",       self._reset                ).pack(side=tk.LEFT)

        # Row 3 — 4 stat cards
        stats_row = tk.Frame(left, bg=BG)
        stats_row.pack(fill=tk.X)

        self.stat_visited   = StatCard(stats_row, "Visited nodes")
        self.stat_generated = StatCard(stats_row, "Generated states")
        self.stat_time      = StatCard(stats_row, "Time (ms)")
        self.stat_steps     = StatCard(stats_row, "Steps")
        for s in [self.stat_visited, self.stat_generated,
                  self.stat_time, self.stat_steps]:
            s.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        # ══════════════════════════════════════════════════
        # RIGHT COLUMN
        # ══════════════════════════════════════════════════

        # Solution Playback panel
        sol_card = make_panel(right, "Solution Playback")
        sol_card.pack(fill=tk.X, pady=(0, 8))

        sol_body = tk.Frame(sol_card, bg=PANEL_BG)
        sol_body.pack(fill=tk.X, padx=12, pady=(0, 4))

        self._board_card(sol_body, "", "sol", False).pack(side=tk.LEFT, padx=(0, 20))

        info = tk.Frame(sol_body, bg=PANEL_BG)
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=6)

        self.step_lbl = tk.Label(info, text="Step  — / —", font=FONT_B,
                                 bg=PANEL_BG, fg=TEXT, anchor="w")
        self.step_lbl.pack(fill=tk.X, pady=(0, 6))

        self.move_lbl = tk.Label(info, text="No solution loaded yet.",
                                 font=FONT_SM, bg=PANEL_BG, fg=MUTED,
                                 anchor="w", justify="left", wraplength=220)
        self.move_lbl.pack(fill=tk.X, pady=(0, 12))

        pb_row = tk.Frame(info, bg=PANEL_BG)
        pb_row.pack(anchor="w")
        flat_btn(pb_row, "← Prev", self._prev_step).pack(side=tk.LEFT, padx=(0, 5))
        flat_btn(pb_row, "Next →", self._next_step).pack(side=tk.LEFT, padx=(0, 5))
        self.auto_btn = flat_btn(pb_row, "▶  Auto", self._toggle_auto, primary=True)
        self.auto_btn.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(sol_card, orient=tk.HORIZONTAL,
                                        mode="determinate")
        self.progress.pack(fill=tk.X, padx=12, pady=(4, 10))

        # Comparison table
        cmp_card = make_panel(right, "Algorithm Comparison")
        cmp_card.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Taq.Treeview", font=FONT_SM, rowheight=26,
                         background=PANEL_BG, fieldbackground=PANEL_BG)
        style.configure("Taq.Treeview.Heading", font=FONT_H)
        style.map("Taq.Treeview",
                  background=[("selected", ACCENT_LT)],
                  foreground=[("selected", TEXT)])

        cols = ("Algorithm", "Visited", "Generated", "Time (ms)", "Steps", "Status")
        self.tree = ttk.Treeview(cmp_card, columns=cols, show="headings",
                                 height=6, style="Taq.Treeview")
        widths = {"Algorithm": 140, "Visited": 85, "Generated": 100,
                  "Time (ms)": 80, "Steps": 60, "Status": 75}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[col], minwidth=widths[col],
                             anchor="w" if col == "Algorithm" else "center",
                             stretch=True)
        self.tree.tag_configure("solved", foreground="#215C0A")
        self.tree.tag_configure("failed", foreground="#6E1414")
        self.tree.pack(padx=12, pady=(0, 12), fill=tk.BOTH, expand=True)

    # ── Board factory ─────────────────────────────────────────────────────────

    def _board_card(self, parent, title, tag, interactive):
        card = tk.Frame(parent, bg=PANEL_BG, bd=1, relief="solid",
                        highlightbackground=BORDER, highlightthickness=1)
        if title:
            tk.Label(card, text=title.upper(), bg=PANEL_BG, fg=MUTED,
                     font=FONT_SM, anchor="w").pack(fill=tk.X, padx=10, pady=(8, 2))
        grid = tk.Frame(card, bg=PANEL_BG)
        grid.pack(padx=10, pady=(0, 10))
        tiles = []
        for r in range(3):
            row_tiles = []
            for c in range(3):
                b = tk.Button(grid, text="", font=FONT_LG,
                              width=2, height=1, relief="flat", bd=0,
                              bg=TILE_BG, fg=TILE_FG,
                              activebackground=TILE_BG, cursor="arrow")
                b.grid(row=r, column=c, padx=3, pady=3, ipadx=6, ipady=8)
                row_tiles.append(b)
            tiles.append(row_tiles)
        setattr(self, f"{tag}_tiles", tiles)
        return card

    def _render_board(self, tiles, state, interactive=False):
        for r in range(3):
            for c in range(3):
                v   = state[r][c]
                btn = tiles[r][c]
                if v == 0:
                    btn.config(text="", bg=BLANK_BG, state="disabled",
                               cursor="arrow", activebackground=BLANK_BG)
                else:
                    bg = CORRECT if (v == GOAL_STATE[r][c]) else TILE_BG
                    btn.config(text=str(v), bg=bg, fg=TILE_FG,
                               activebackground=bg, state="normal",
                               cursor="hand2" if interactive else "arrow")
                    if interactive:
                        btn.config(command=lambda row=r, col=c: self._click_tile(row, col))
                    else:
                        btn.config(command=lambda: None)

    def _click_tile(self, r, c):
        s = self.current_state
        br = bc = None
        for i in range(3):
            for j in range(3):
                if s[i][j] == 0:
                    br, bc = i, j
        if br is not None and abs(r - br) + abs(c - bc) == 1:
            s[br][bc], s[r][c] = s[r][c], s[br][bc]
            self._render_board(self.init_tiles, s, interactive=True)
            self.solution_path = []
            self._render_board(self.sol_tiles, s, interactive=False)
            self._update_step_ui()

    # ── Algorithm selection ───────────────────────────────────────────────────

    def _select_algo(self, val):
        self.algo_var.set(val)
        for v, btn in self.algo_btns.items():
            if v == val:
                btn.config(bg=ACCENT, fg=BTN_FG, relief="flat")
            else:
                btn.config(bg=PANEL_BG, fg=MUTED, relief="solid")
        if val == "dfs_limited":
            self.depth_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        else:
            self.depth_frame.pack_forget()

    # ── Solve ─────────────────────────────────────────────────────────────────

    def _run_algo(self):
        if self.solving:
            return
        self.solving = True
        self._set_status("Solving…", color=ACCENT)
        algo  = self.algo_var.get()
        state = [row[:] for row in self.current_state]
        L     = self.depth_var.get()

        def worker():
            if algo == "dfs":
                path, v, g, t = dfs(state);               extra = ""
            elif algo == "bfs":
                path, v, g, t = bfs(state);               extra = ""
            elif algo == "dfs_limited":
                path, v, g, t, fl = dfs_limited_incremental(state, L)
                extra = f"  (final L = {fl})"
            else:
                path, v, g, t = astar(state);             extra = ""
            self.after(0, lambda: self._apply_result(path, v, g, t, extra))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_result(self, path, visited, generated, elapsed, extra=""):
        self.solving = False
        self.stat_visited.set(f"{visited:,}")
        self.stat_generated.set(f"{generated:,}")
        self.stat_time.set(f"{elapsed:.1f}")

        if path:
            steps = len(path) - 1
            self.stat_steps.set(steps)
            self._set_status(f"Solution found in {steps} moves.{extra}", success=True)
            self.solution_path       = path
            self.step_index          = 0
            self.progress["maximum"] = steps
            self._show_step(0)
        else:
            self.stat_steps.set("—")
            self._set_status("No solution found (node limit reached).", error=True)
            self.solution_path     = []
            self.progress["value"] = 0

    def _run_all(self):
        if self.solving:
            return
        self.solving = True
        state = [row[:] for row in self.current_state]
        L     = self.depth_var.get()
        self._set_status("Running all algorithms…", color=ACCENT)

        def worker():
            results = []
            for name, fn in [
                ("DFS",            lambda: dfs(state)),
                ("BFS",            lambda: bfs(state)),
                ("Depth-Lim. DFS", lambda: dfs_limited_incremental(state, L)),
                ("A*",             lambda: astar(state)),
            ]:
                r = fn()
                path, v, g, t = r[0], r[1], r[2], r[3]
                results.append((name, path, v, g, t))
            self.after(0, lambda: self._show_comparison(results))

        threading.Thread(target=worker, daemon=True).start()

    def _show_comparison(self, results):
        self.solving = False
        for row in self.tree.get_children():
            self.tree.delete(row)
        for name, path, v, g, t in results:
            steps  = len(path) - 1 if path else "—"
            status = "Solved" if path else "Failed"
            tag    = "solved" if path else "failed"
            self.tree.insert("", "end", tags=(tag,),
                             values=(name, f"{v:,}", f"{g:,}",
                                     f"{t:.1f}", steps, status))
        self._set_status("Comparison complete.", success=True)

    # ── Playback ──────────────────────────────────────────────────────────────

    def _show_step(self, idx):
        if not self.solution_path:
            return
        idx   = max(0, min(idx, len(self.solution_path) - 1))
        self.step_index = idx
        node  = self.solution_path[idx]
        total = len(self.solution_path) - 1

        self._render_board(self.sol_tiles, node["state"], interactive=False)
        self.step_lbl.config(text=f"Step  {idx} / {total}")
        self.progress["value"] = idx

        if idx == 0:
            self.move_lbl.config(text="Initial state")
        elif idx == total:
            self.move_lbl.config(
                text=f"Goal reached!\nMoved tile {node['tile']} → {node['move']}")
        else:
            self.move_lbl.config(
                text=f"Move tile  {node['tile']}  ({node['move']})")

    def _update_step_ui(self):
        self.step_lbl.config(text="Step  — / —")
        self.move_lbl.config(text="No solution loaded yet.")
        self.progress["value"] = 0

    def _prev_step(self): self._show_step(self.step_index - 1)
    def _next_step(self): self._show_step(self.step_index + 1)

    def _toggle_auto(self):
        if self.auto_job:
            self.after_cancel(self.auto_job)
            self.auto_job = None
            self.auto_btn.config(text="▶  Auto", bg=ACCENT,
                                 activebackground=ACCENT_DK)
        else:
            if not self.solution_path:
                return
            self.step_index = 0
            self.auto_btn.config(text="■  Stop", bg="#A32D2D",
                                 activebackground="#701F1F")
            self._auto_tick()

    def _auto_tick(self):
        if self.step_index >= len(self.solution_path) - 1:
            self.auto_job = None
            self.auto_btn.config(text="▶  Auto", bg=ACCENT,
                                 activebackground=ACCENT_DK)
            return
        self._show_step(self.step_index + 1)
        self.auto_job = self.after(420, self._auto_tick)

    # ── Board controls ────────────────────────────────────────────────────────

    def _shuffle(self):
        import random
        s = [row[:] for row in GOAL_STATE]
        for _ in range(200):
            s, _, _ = random.choice(get_neighbors(s))
        self.current_state = s
        self._render_board(self.init_tiles, self.current_state, interactive=True)
        self.solution_path = []
        self._render_board(self.sol_tiles, self.current_state, interactive=False)
        self._update_step_ui()
        self._set_status("Board shuffled — press Solve to find a solution.")

    def _reset(self):
        self.current_state = [row[:] for row in INITIAL_STATE]
        self._render_board(self.init_tiles, self.current_state, interactive=True)
        self.solution_path = []
        self._render_board(self.sol_tiles, self.current_state, interactive=False)
        self._update_step_ui()
        for s in [self.stat_visited, self.stat_generated,
                  self.stat_time, self.stat_steps]:
            s.set("—")
        self._set_status("Board reset.")

    # ── Status bar ────────────────────────────────────────────────────────────

    def _set_status(self, msg, success=False, error=False, color=None):
        self.status_var.set("  " + msg)
        if success:
            self.status_widget.config(bg="#DFF0CE", fg="#1E5C0A")
        elif error:
            self.status_widget.config(bg="#FAE0E0", fg="#6E1414")
        elif color:
            self.status_widget.config(bg=ACCENT_LT, fg=color)
        else:
            self.status_widget.config(bg=ACCENT_LT, fg=MUTED)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = TaquinApp()
    app.mainloop()
