import tkinter as tk

# ---------------- SETTINGS ----------------
MAX_ROUNDS = 5
CELL_SIZE = 150
BOARD_SIZE = CELL_SIZE * 3

WIN_COLOR = "#7CFC90"
FLASH_BG = "#FFF3B0"

# ---------------- SOUND (Windows + fallback) ----------------
def play_sound(kind="click"):
    try:
        import winsound
        if kind == "click":
            winsound.Beep(700, 60)
        elif kind == "win":
            winsound.Beep(900, 120); winsound.Beep(1100, 120)
        elif kind == "draw":
            winsound.Beep(500, 140)
    except Exception:
        try:
            root.bell()
        except Exception:
            pass

# ---------------- UI HELPERS ----------------
def set_fullscreen(on=True):
    root.attributes("-fullscreen", on)

def toggle_fullscreen(event=None):
    set_fullscreen(not root.attributes("-fullscreen"))

def exit_fullscreen(event=None):
    set_fullscreen(False)

def pulse_turn_label(times=6):
    """Small animation when turn changes."""
    base = top_frame.cget("bg")
    def step(k):
        if k <= 0:
            turn_label.config(bg=base)
            return
        cur = turn_label.cget("bg")
        turn_label.config(bg=(FLASH_BG if cur == base else base))
        root.after(90, lambda: step(k - 1))
    step(times)

def show_banner(text, kind="info"):
    """Show a message INSIDE the app (no popup)."""
    # simple color logic
    bg = "#E6F4EA" if kind == "win" else "#FCE8E6" if kind == "draw" else "#E8F0FE"
    banner_label.config(text=text, bg=bg)
    banner_frame.pack(fill="x", padx=20, pady=(0, 10))
    # auto-hide after 1.2s
    root.after(1200, hide_banner)

def hide_banner():
    banner_frame.pack_forget()

def show_screen(frame_to_show):
    """Only show one main screen at a time."""
    start_screen.pack_forget()
    game_screen.pack_forget()
    end_screen.pack_forget()
    frame_to_show.pack(fill="both", expand=True)

# ---------------- GAME STATE ----------------
def reset_match_state():
    global round_number, x_wins, o_wins, draws, start_player, current_player
    round_number = 1
    x_wins = 0
    o_wins = 0
    draws = 0
    start_player = "X"
    current_player = "X"

def reset_board_state():
    global board, board_locked, current_player
    board = [["", "", ""] for _ in range(3)]
    board_locked = False
    current_player = start_player
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text="", bg=NORMAL_BG)
    update_top_panel()

# ---------------- GAME LOGIC ----------------
def start_game():
    """Start match with names from entry fields."""
    global p1_name, p2_name

    p1 = p1_entry.get().strip()
    p2 = p2_entry.get().strip()
    p1_name = p1 if p1 else "Player 1"
    p2_name = p2 if p2 else "Player 2"

    players_label.config(text=f"{p1_name} = X     |     {p2_name} = O")

    reset_match_state()
    reset_board_state()
    show_screen(game_screen)
    pulse_turn_label()

def make_move(r, c):
    global current_player

    if board_locked:
        return
    if board[r][c] != "":
        return

    play_sound("click")

    board[r][c] = current_player
    buttons[r][c].config(text=current_player)

    if check_round_end():
        return

    current_player = "O" if current_player == "X" else "X"
    update_top_panel()
    pulse_turn_label()

def find_winner():
    """Return (winner, winning_cells)."""
    # rows
    for r in range(3):
        vals = [board[r][0], board[r][1], board[r][2]]
        if vals[0] == vals[1] == vals[2] != "":
            return vals[0], [(r, 0), (r, 1), (r, 2)]

    # cols
    for c in range(3):
        vals = [board[0][c], board[1][c], board[2][c]]
        if vals[0] == vals[1] == vals[2] != "":
            return vals[0], [(0, c), (1, c), (2, c)]

    # diagonals
    d1 = [board[0][0], board[1][1], board[2][2]]
    if d1[0] == d1[1] == d1[2] != "":
        return d1[0], [(0, 0), (1, 1), (2, 2)]

    d2 = [board[0][2], board[1][1], board[2][0]]
    if d2[0] == d2[1] == d2[2] != "":
        return d2[0], [(0, 2), (1, 1), (2, 0)]

    return None, []

def check_round_end():
    """If round ends, update UI/state, then move to next round or match end."""
    global board_locked, round_number, x_wins, o_wins, draws, start_player

    winner, cells = find_winner()

    # win
    if winner in ("X", "O"):
        board_locked = True
        for (r, c) in cells:
            buttons[r][c].config(bg=WIN_COLOR)
        play_sound("win")

        if winner == "X":
            x_wins += 1
            show_banner(f"Round won by {p1_name} (X)!", kind="win")
        else:
            o_wins += 1
            show_banner(f"Round won by {p2_name} (O)!", kind="win")

        update_top_panel()
        root.after(900, next_round_or_end)  # short pause inside same window
        return True

    # draw
    if all(board[i][j] != "" for i in range(3) for j in range(3)):
        board_locked = True
        draws += 1
        play_sound("draw")
        show_banner("Round ended in a draw!", kind="draw")
        update_top_panel()
        root.after(900, next_round_or_end)
        return True

    return False

def next_round_or_end():
    """Move to next round or show match summary screen ."""
    global round_number, start_player

    round_number += 1

    if round_number > MAX_ROUNDS:
        show_match_summary()
        return

    # alternate who starts
    start_player = "O" if start_player == "X" else "X"
    reset_board_state()

def show_match_summary():
    """Show final stats on an in-app screen."""
    p1_wins = x_wins
    p2_wins = o_wins
    p1_losses = p2_wins
    p2_losses = p1_wins

    if p1_wins > p2_wins:
        overall = f"Overall Winner: {p1_name} (X)"
    elif p2_wins > p1_wins:
        overall = f"Overall Winner: {p2_name} (O)"
    else:
        overall = "Overall Result: Tie"

    summary = (
        f"Match Finished ({MAX_ROUNDS} rounds)\n\n"
        f"{p1_name} (X): Wins = {p1_wins}\n"
        f"{p2_name} (O): Wins = {p2_wins},\n"
        f"Draws: {draws}\n\n"
        f"{overall}"
    )
    end_summary_label.config(text=summary)
    show_screen(end_screen)

def play_again():
    """Start a new 5-round match with same names."""
    reset_match_state()
    reset_board_state()
    show_screen(game_screen)
    pulse_turn_label()

def back_to_start():
    """Go back to name input screen."""
    show_screen(start_screen)

def update_top_panel():
    # turn label
    turn_text = f"Turn: {p1_name} (X)" if current_player == "X" else f"Turn: {p2_name} (O)"
    turn_label.config(text=turn_text)

    # round label
    shown_round = min(round_number, MAX_ROUNDS)
    round_label.config(text=f"Round: {shown_round} / {MAX_ROUNDS}")

    # score label
    score_label.config(text=f"Score  X:{x_wins}   O:{o_wins}   Draws:{draws}")

# ---------------- UI ----------------
root = tk.Tk()
root.title("Tic-Tac-Toe (One Window)")
root.geometry("1000x800")  # large window

# keyboard shortcuts
root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_fullscreen)

# ----------- START SCREEN (names in same window) -----------
start_screen = tk.Frame(root)

tk.Label(start_screen, text="Tic-Tac-Toe", font=("Arial", 34, "bold")).pack(pady=(40, 10))
tk.Label(start_screen, text="Enter player names", font=("Arial", 16)).pack(pady=(0, 25))

form = tk.Frame(start_screen)
form.pack()

tk.Label(form, text="Player 1 (X):", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
p1_entry = tk.Entry(form, font=("Arial", 14), width=22)
p1_entry.grid(row=0, column=1, padx=10, pady=10)
p1_entry.insert(0, "Player 1")

tk.Label(form, text="Player 2 (O):", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
p2_entry = tk.Entry(form, font=("Arial", 14), width=22)
p2_entry.grid(row=1, column=1, padx=10, pady=10)
p2_entry.insert(0, "Player 2")

btns = tk.Frame(start_screen)
btns.pack(pady=25)

tk.Button(btns, text="Start (5 rounds)", font=("Arial", 14), width=18, command=start_game).grid(row=0, column=0, padx=10)
tk.Button(btns, text="Fullscreen (F11)", font=("Arial", 14), width=18, command=lambda: set_fullscreen(True)).grid(row=0, column=1, padx=10)
tk.Button(btns, text="Quit", font=("Arial", 14), width=18, command=root.destroy).grid(row=0, column=2, padx=10)

hint = tk.Label(start_screen, text="Tip: Press F11 for fullscreen, Esc to exit.", font=("Arial", 12))
hint.pack(pady=10)

# ----------- GAME SCREEN -----------
game_screen = tk.Frame(root)

top_frame = tk.Frame(game_screen)
top_frame.pack(pady=(18, 6))

tk.Label(top_frame, text="Tic-Tac-Toe", font=("Arial", 28, "bold")).pack()

players_label = tk.Label(top_frame, text="Player 1 = X     |     Player 2 = O", font=("Arial", 14))
players_label.pack(pady=(8, 4))

turn_label = tk.Label(top_frame, text="Turn: -", font=("Arial", 16, "bold"), padx=12, pady=6)
turn_label.pack(pady=6)

round_label = tk.Label(top_frame, text=f"Round: 1 / {MAX_ROUNDS}", font=("Arial", 14))
round_label.pack()

score_label = tk.Label(top_frame, text="Score  X:0   O:0   Draws:0", font=("Arial", 14))
score_label.pack(pady=(8, 0))

# banner (hidden by default)
banner_frame = tk.Frame(game_screen)
banner_label = tk.Label(banner_frame, text="", font=("Arial", 14), pady=8)
banner_label.pack(fill="x")

# board
canvas = tk.Canvas(game_screen, width=BOARD_SIZE, height=BOARD_SIZE)
canvas.pack(pady=18)

# grid lines
canvas.create_line(CELL_SIZE, 0, CELL_SIZE, BOARD_SIZE, width=6)
canvas.create_line(CELL_SIZE * 2, 0, CELL_SIZE * 2, BOARD_SIZE, width=6)
canvas.create_line(0, CELL_SIZE, BOARD_SIZE, CELL_SIZE, width=6)
canvas.create_line(0, CELL_SIZE * 2, BOARD_SIZE, CELL_SIZE * 2, width=6)

buttons = []
for i in range(3):
    row = []
    for j in range(3):
        b = tk.Button(
            game_screen,
            text="",
            font=("Arial", 42, "bold"),
            width=2,
            height=1,
            command=lambda i=i, j=j: make_move(i, j)
        )
        canvas.create_window(
            j * CELL_SIZE + CELL_SIZE // 2,
            i * CELL_SIZE + CELL_SIZE // 2,
            window=b
        )
        row.append(b)
    buttons.append(row)

NORMAL_BG = buttons[0][0].cget("bg")

# controls
controls = tk.Frame(game_screen)
controls.pack(pady=(8, 18))

tk.Button(controls, text="Reset Round", font=("Arial", 13), width=14,
          command=reset_board_state).grid(row=0, column=0, padx=8)

tk.Button(controls, text="Reset Match", font=("Arial", 13), width=14,
          command=lambda: (reset_match_state(), reset_board_state())).grid(row=0, column=1, padx=8)

tk.Button(controls, text="Back to Names", font=("Arial", 13), width=14,
          command=back_to_start).grid(row=0, column=2, padx=8)

tk.Button(controls, text="Fullscreen (F11)", font=("Arial", 13), width=16,
          command=toggle_fullscreen).grid(row=0, column=3, padx=8)

tk.Button(controls, text="Quit", font=("Arial", 13), width=10,
          command=root.destroy).grid(row=0, column=4, padx=8)

# ----------- END SCREEN (match summary) -----------
end_screen = tk.Frame(root)

tk.Label(end_screen, text="Match Over", font=("Arial", 32, "bold")).pack(pady=(40, 10))

end_summary_label = tk.Label(end_screen, text="", font=("Arial", 16), justify="left")
end_summary_label.pack(pady=20)

end_btns = tk.Frame(end_screen)
end_btns.pack(pady=20)

tk.Button(end_btns, text="Play Again (new 5 rounds)", font=("Arial", 14), width=26,
          command=play_again).grid(row=0, column=0, padx=12)

tk.Button(end_btns, text="Change Names", font=("Arial", 14), width=16,
          command=back_to_start).grid(row=0, column=1, padx=12)

tk.Button(end_btns, text="Close", font=("Arial", 14), width=12,
          command=root.destroy).grid(row=0, column=2, padx=12)

# ---------------- INITIAL STATE ----------------
p1_name = "Player 1"
p2_name = "Player 2"

board = [["", "", ""] for _ in range(3)]
board_locked = False

reset_match_state()
update_top_panel()

show_screen(start_screen)
root.mainloop()
