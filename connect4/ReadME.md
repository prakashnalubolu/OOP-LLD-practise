# Connect Four (Offline)
A simple offline 2-player Connect Four game built with Python.
<img width="547" height="603" alt="image" src="https://github.com/user-attachments/assets/06e1c713-0ce7-4c6f-ae78-cc860f959ac2" />


## Files
- `connect_four.py` — backend game logic (rules, board, win/draw, turn handling) **coded by me** also some reference code from "https://www.hellointerview.com/learn/low-level-design/problem-breakdowns/connect-four"
- `connect_four_ui.py` — Tkinter UI to play the game **coded with help from an AI assistant**

## Run
Make sure both files are in the same folder, then run:

```bash
python connect_four_ui.py


How to Play:
 Two players take turns.
 Click a Drop button (0–6) to drop your disc into that column.
 The disc falls to the lowest available slot in that column.
 The UI shows the current player, status, and result.
 Click Reset Game to start over.

Game Rules:
 You win if you connect four of your discs in a line:
 Horizontal
 Vertical
 Diagonal

A move is invalid if:
 You try to drop into a full column
 You play out of turn
 You try to play after the game is already over
 If the board fills up and nobody wins, the result is a draw.
