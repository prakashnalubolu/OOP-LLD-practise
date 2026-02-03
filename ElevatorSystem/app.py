import tkinter as tk
from tkinter import ttk, messagebox
import uuid

from ElevatorSystem import ( MIN_FLOOR, MAX_FLOOR,Direction, HallRequest,Elevator, ElevatorSystem)


class ElevatorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Elevator Simulator (Offline)")
        self.geometry("900x650")
        self.resizable(False, False)

        # Backend system
        self.system = ElevatorSystem([
            Elevator("E1"),
            Elevator("E2"),
            Elevator("E3"),
        ])

        # UI state
        self.tick_ms = 350
        self.running = False
        self.selected_elevator_id = tk.StringVar(value="E1")

        self._build_layout()
        self._render_once()

    # ---------------- UI Layout ----------------
    def _build_layout(self):
        # Top controls
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Simulation Controls").pack(side=tk.LEFT)

        self.btn_start = ttk.Button(top, text="Start", command=self.start)
        self.btn_start.pack(side=tk.LEFT, padx=8)

        self.btn_stop = ttk.Button(top, text="Stop", command=self.stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=8)

        self.btn_step = ttk.Button(top, text="Step Once", command=self.step_once)
        self.btn_step.pack(side=tk.LEFT, padx=8)

        ttk.Label(top, text="Speed (ms/tick):").pack(side=tk.LEFT, padx=(20, 4))
        self.speed_var = tk.IntVar(value=self.tick_ms)
        speed = ttk.Spinbox(top, from_=100, to=2000, increment=50, textvariable=self.speed_var, width=7, command=self._update_speed)
        speed.pack(side=tk.LEFT)

        # Main split: left = building, right = controls/log
        main = ttk.Frame(self, padding=10)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.left = ttk.Frame(main)
        self.left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right = ttk.Frame(main)
        self.right.pack(side=tk.RIGHT, fill=tk.Y)

        # Building canvas
        ttk.Label(self.left, text="Building View").pack(anchor="w")
        self.canvas = tk.Canvas(self.left, width=560, height=560, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(pady=8)

        # Right controls: Hall call
        hall = ttk.LabelFrame(self.right, text="Hall Call (Pickup)", padding=10)
        hall.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(hall, text="Floor:").grid(row=0, column=0, sticky="w")
        self.hall_floor = tk.IntVar(value=0)
        hall_floor_spin = ttk.Spinbox(hall, from_=MIN_FLOOR, to=MAX_FLOOR, textvariable=self.hall_floor, width=6)
        hall_floor_spin.grid(row=0, column=1, sticky="w", padx=6)

        self.btn_up = ttk.Button(hall, text="Call UP", command=lambda: self.hall_call(Direction.UP))
        self.btn_up.grid(row=1, column=0, pady=8, sticky="ew")

        self.btn_down = ttk.Button(hall, text="Call DOWN", command=lambda: self.hall_call(Direction.DOWN))
        self.btn_down.grid(row=1, column=1, pady=8, sticky="ew")

        hall.columnconfigure(0, weight=1)
        hall.columnconfigure(1, weight=1)

        # Right controls: Car destination
        car = ttk.LabelFrame(self.right, text="Inside Elevator (Destination)", padding=10)
        car.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(car, text="Elevator:").grid(row=0, column=0, sticky="w")
        self.elev_choice = ttk.Combobox(car, values=["E1", "E2", "E3"], textvariable=self.selected_elevator_id, width=7, state="readonly")
        self.elev_choice.grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(car, text="Destination:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.dest_floor = tk.IntVar(value=MAX_FLOOR)
        dest_spin = ttk.Spinbox(car, from_=MIN_FLOOR, to=MAX_FLOOR, textvariable=self.dest_floor, width=6)
        dest_spin.grid(row=1, column=1, sticky="w", padx=6, pady=(8, 0))

        self.btn_go = ttk.Button(car, text="Go", command=self.select_destination)
        self.btn_go.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        car.columnconfigure(0, weight=1)
        car.columnconfigure(1, weight=1)

        # Status
        status = ttk.LabelFrame(self.right, text="Status", padding=10)
        status.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status_text = tk.Text(status, height=16, width=34, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Footer hint
        ttk.Label(self, text="Tip: Start simulation, make hall calls, then set destination for the assigned elevator.",
                  foreground="#444").pack(side=tk.BOTTOM, pady=6)

    # ---------------- Backend Actions ----------------
    def hall_call(self, direction: Direction):
        floor = int(self.hall_floor.get())
        if direction == Direction.UP and floor == MAX_FLOOR:
            messagebox.showinfo("Invalid", "Top floor cannot call UP.")
            return
        if direction == Direction.DOWN and floor == MIN_FLOOR:
            messagebox.showinfo("Invalid", "Ground floor cannot call DOWN.")
            return

        req = HallRequest(request_id=str(uuid.uuid4())[:8], floor=floor, direction=direction)
        elev_id = self.system.request_elevator(req)
        if elev_id is None:
            messagebox.showerror("No Elevator", "No elevator could be assigned.")
            return

        self._log(f"Hall Call: floor={floor}, dir={direction.value}  -> assigned {elev_id}")

        # nice UX: auto-select that elevator
        self.selected_elevator_id.set(elev_id)
        self._render_once()

    def select_destination(self):
        elev_id = self.selected_elevator_id.get()
        dest = int(self.dest_floor.get())
        ok = self.system.select_destination(elev_id, dest)
        if not ok:
            messagebox.showerror("Failed", f"Could not add destination {dest} for {elev_id}.")
            return
        self._log(f"Inside {elev_id}: destination={dest}")
        self._render_once()

    def step_once(self):
        self.system.step()
        self._render_once()

    # ---------------- Simulation Loop ----------------
    def start(self):
        self.running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_step.config(state=tk.DISABLED)
        self._update_speed()
        self._tick()

    def stop(self):
        self.running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_step.config(state=tk.NORMAL)

    def _update_speed(self):
        try:
            self.tick_ms = int(self.speed_var.get())
        except Exception:
            self.tick_ms = 350

    def _tick(self):
        if not self.running:
            return
        self.system.step()
        self._render_once()
        self.after(self.tick_ms, self._tick)

    # ---------------- Rendering ----------------
    def _render_once(self):
        self.canvas.delete("all")

        snapshot = self.system.snapshot()
        self._draw_building_grid()
        self._draw_elevators(snapshot)
        self._update_status(snapshot)

    def _draw_building_grid(self):
        # building area
        margin = 30
        top = 20
        width = 520
        height = 520

        self.build_x0 = margin
        self.build_y0 = top
        self.build_x1 = margin + width
        self.build_y1 = top + height

        self.canvas.create_rectangle(self.build_x0, self.build_y0, self.build_x1, self.build_y1, outline="#bbb")

        floors = MAX_FLOOR - MIN_FLOOR + 1
        self.floor_h = height / floors

        # floor lines + labels
        for i in range(floors + 1):
            y = self.build_y0 + i * self.floor_h
            self.canvas.create_line(self.build_x0, y, self.build_x1, y, fill="#eee")

        for f in range(MAX_FLOOR, MIN_FLOOR - 1, -1):
            y = self._floor_to_y(f)
            self.canvas.create_text(self.build_x0 - 12, y + self.floor_h / 2, text=str(f), fill="#333", font=("Arial", 10))

        # shaft columns for 3 elevators
        self.shaft_w = 140
        self.shaft_gap = 25
        self.shaft_x = [
            self.build_x0 + 40,
            self.build_x0 + 40 + self.shaft_w + self.shaft_gap,
            self.build_x0 + 40 + 2 * (self.shaft_w + self.shaft_gap),
        ]
        for idx in range(3):
            x0 = self.shaft_x[idx]
            x1 = x0 + self.shaft_w
            self.canvas.create_rectangle(x0, self.build_y0, x1, self.build_y1, outline="#ddd")

    def _draw_elevators(self, snapshot):
        # each elevator is a colored rectangle with id + direction
        elev_by_id = {e["id"]: e for e in snapshot}
        ids = ["E1", "E2", "E3"]

        for idx, eid in enumerate(ids):
            e = elev_by_id[eid]
            floor = e["floor"]
            direction = e["direction"]

            x0 = self.shaft_x[idx] + 15
            x1 = self.shaft_x[idx] + self.shaft_w - 15
            y0 = self._floor_to_y(floor) + 8
            y1 = y0 + self.floor_h - 16

            # draw car
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="#333", width=2, fill="#f7f7f7")
            self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=f"{eid}\n{direction.upper()}",
                                    fill="#222", font=("Arial", 10), justify="center")

            # draw upcoming stops in shaft (small markers)
            for stop in e["up_stops"]:
                sy = self._floor_to_y(stop) + self.floor_h / 2
                self.canvas.create_oval(x1 + 6, sy - 4, x1 + 14, sy + 4, outline="#888", fill="#cfcfcf")
            for stop in e["down_stops"]:
                sy = self._floor_to_y(stop) + self.floor_h / 2
                self.canvas.create_rectangle(x1 + 6, sy - 4, x1 + 14, sy + 4, outline="#888", fill="#cfcfcf")

    def _update_status(self, snapshot):
        self.status_text.delete("1.0", tk.END)

        lines = []
        for e in snapshot:
            lines.append(
                f"{e['id']} | floor={e['floor']} | dir={e['direction']}\n"
                f"  up:   {e['up_stops']}\n"
                f"  down: {e['down_stops']}\n"
            )
        self.status_text.insert(tk.END, "\n".join(lines))

    def _floor_to_y(self, floor: int) -> float:
        # map floor to y coordinate (top is MAX_FLOOR)
        idx_from_top = MAX_FLOOR - floor
        return self.build_y0 + idx_from_top * self.floor_h

    def _log(self, msg: str):
        self.status_text.insert(tk.END, f"\nLOG: {msg}\n")
        self.status_text.see(tk.END)


if __name__ == "__main__":
    app = ElevatorUI()
    app.mainloop()
