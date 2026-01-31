from connect_four import Player, Board, ConnectFour, DiscColour, GameState
import tkinter as tk
from tkinter import ttk


class ConnectFourUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Connect Four (Offline)")
        self.root.resizable(False, False)

        self.rows = 6
        self.cols = 7

        self.p1 = Player(1, DiscColour.WHITE)
        self.p2 = Player(2, DiscColour.BLUE)
        self._new_game()

        # ----- Styling -----
        self.style = ttk.Style()
        self.style.theme_use("default")

        # Simple fonts
        self.FONT_TITLE = ("Segoe UI", 14, "bold")
        self.FONT_LABEL = ("Segoe UI", 10)
        self.FONT_STATUS = ("Segoe UI", 10, "bold")
        self.FONT_CELL = ("Segoe UI", 14, "bold")
        self.FONT_COORD = ("Segoe UI", 9, "bold")

        self._build_widgets()
        self._render_board()
        self._refresh_info(last_message="Player 1 starts. Click a column (0–6) to drop a disc.")

    def _new_game(self):
        self.game = ConnectFour(self.p1, self.p2, Board(self.rows, self.cols))

    # ---------- UI BUILD ----------
    def _build_widgets(self):
        container = ttk.Frame(self.root, padding=12)
        container.grid(row=0, column=0)

        # Header
        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew")

        ttk.Label(header, text="Connect Four", font=self.FONT_TITLE).grid(row=0, column=0, sticky="w")

        # Current player panel
        player_panel = ttk.Frame(header)
        player_panel.grid(row=0, column=1, sticky="e", padx=(20, 0))

        ttk.Label(player_panel, text="Current Player:", font=self.FONT_LABEL).grid(row=0, column=0, sticky="e")

        self.player_dot = tk.Canvas(player_panel, width=18, height=18, highlightthickness=0)
        self.player_dot.grid(row=0, column=1, padx=(6, 6))
        self.player_dot_id = self.player_dot.create_oval(2, 2, 16, 16, fill="white", outline="gray")

        self.current_player_var = tk.StringVar(value="")
        ttk.Label(player_panel, textvariable=self.current_player_var, font=self.FONT_STATUS).grid(row=0, column=2, sticky="e")

        # Move buttons row (Drop column)
        controls = ttk.Frame(container)
        controls.grid(row=1, column=0, pady=(12, 6), sticky="ew")

        self.col_buttons = []
        for c in range(self.cols):
            b = ttk.Button(
                controls,
                text=f"Drop ↓ {c}",
                command=lambda col=c: self._on_drop(col),
                width=10
            )
            b.grid(row=0, column=c, padx=2)
            self.col_buttons.append(b)

        # Board frame
        board_frame = ttk.Frame(container, padding=8, relief="ridge")
        board_frame.grid(row=2, column=0, pady=(6, 10))

        # Coordinate labels + cells
        # Layout: extra top header row and extra left column for row labels
        # We also add a bottom header row with column numbers.
        self.cells = [[None] * self.cols for _ in range(self.rows)]

        # Top-left empty corner
        ttk.Label(board_frame, text=" ", width=3).grid(row=0, column=0)

        # Column numbers (top)
        for c in range(self.cols):
            ttk.Label(board_frame, text=str(c), font=self.FONT_COORD, width=4, anchor="center").grid(row=0, column=c + 1)

        # Grid rows (UI row 0 is top)
        for ui_r in range(self.rows):
            # Row label on left (show backend row index for clarity)
            backend_r = (self.rows - 1) - ui_r  # because backend row 0 is bottom
            ttk.Label(board_frame, text=str(backend_r), font=self.FONT_COORD, width=3, anchor="center").grid(row=ui_r + 1, column=0)

            for c in range(self.cols):
                lbl = tk.Label(
                    board_frame,
                    text=" ",
                    font=self.FONT_CELL,
                    width=4,
                    height=2,
                    bd=1,
                    relief="solid",
                    bg="white"
                )
                lbl.grid(row=ui_r + 1, column=c + 1, padx=1, pady=1)
                self.cells[ui_r][c] = lbl

        # Bottom-left empty corner
        ttk.Label(board_frame, text=" ", width=3).grid(row=self.rows + 1, column=0)

        # Column numbers (bottom)
        for c in range(self.cols):
            ttk.Label(board_frame, text=str(c), font=self.FONT_COORD, width=4, anchor="center").grid(row=self.rows + 1, column=c + 1)

        # Status + Result area
        info = ttk.Frame(container)
        info.grid(row=3, column=0, sticky="ew")

        self.last_action_var = tk.StringVar(value="")
        ttk.Label(info, text="Status:", font=self.FONT_LABEL).grid(row=0, column=0, sticky="w")
        self.last_action_label = ttk.Label(info, textvariable=self.last_action_var, font=self.FONT_LABEL, wraplength=520)
        self.last_action_label.grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.result_var = tk.StringVar(value="")
        ttk.Label(info, text="Result:", font=self.FONT_LABEL).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.result_label = ttk.Label(info, textvariable=self.result_var, font=self.FONT_STATUS)
        self.result_label.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        # Reset button
        actions = ttk.Frame(container)
        actions.grid(row=4, column=0, sticky="e", pady=(10, 0))

        ttk.Button(actions, text="Reset Game", command=self._reset).grid(row=0, column=0)

    # ---------- RENDERING ----------
    def _disc_to_ui(self, disc):
        """
        Returns (text, bg_color, fg_color)
        """
        if disc is None:
            return (" ", "white", "black")
        if disc == DiscColour.WHITE:
            return ("●", "#E6E6E6", "black")
        return ("●", "#A7D8FF", "black")

    def _render_board(self):
        backend_board = self.game.get_board().board  # backend row 0 = bottom

        for ui_r in range(self.rows):
            backend_r = (self.rows - 1) - ui_r
            for c in range(self.cols):
                disc = backend_board[backend_r][c]
                text, bg, fg = self._disc_to_ui(disc)
                self.cells[ui_r][c].configure(text=text, bg=bg, fg=fg)

        # Disable buttons when game ends
        ended = self.game.get_game_state() != GameState.IN_PROGRESS
        for b in self.col_buttons:
            b.configure(state=("disabled" if ended else "normal"))

    def _player_display(self, player: Player) -> str:
        # Keep it readable in UI
        color = "WHITE" if player.color == DiscColour.WHITE else "BLUE"
        return f"Player {player.id} ({color})"

    def _refresh_info(self, last_message: str = ""):
        # Current player
        cp = self.game.get_current_player()
        if cp is not None:
            self.current_player_var.set(self._player_display(cp))
            dot_color = "#E6E6E6" if cp.color == DiscColour.WHITE else "#A7D8FF"
            self.player_dot.itemconfig(self.player_dot_id, fill=dot_color)

        # Status message
        if last_message:
            self.last_action_var.set(last_message)

        # Result
        state = self.game.get_game_state()
        if state == GameState.IN_PROGRESS:
            self.result_var.set("In progress")
        elif state == GameState.DRAW:
            self.result_var.set("Draw — board is full.")
        else:
            w = self.game.get_winner()
            if w is None:
                self.result_var.set("Win")
            else:
                self.result_var.set(f"Winner: {self._player_display(w)}")

    # ---------- ACTIONS ----------
    def _on_drop(self, col: int):
        player = self.game.get_current_player()
        msg = self.game.choose_a_column(player, col)

        # If move was accepted, msg is fine. If not your turn / invalid / over, msg explains it.
        self._render_board()
        self._refresh_info(last_message=msg)

    def _reset(self):
        self._new_game()
        self._render_board()
        self._refresh_info(last_message="Player 1 starts. Click a column (0–6) to drop a disc.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourUI(root)
    root.mainloop()
