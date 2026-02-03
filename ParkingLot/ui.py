import tkinter as tk
from tkinter import ttk, messagebox

# Import your backend (make sure parking_lot.py is in the same folder)
from ParkingLot import ParkingLot, Level, ParkingSpot, Vehicle, VehicleType


# -------------------- UI App --------------------

class ParkingLotUI(tk.Tk):
    def __init__(self, lot: ParkingLot):
        super().__init__()
        self.title("Parking Lot Simulator (Offline Demo)")
        self.geometry("1100x720")
        self.resizable(False, False)

        self.lot = lot

        # Track spot -> canvas items (for redraw)
        self.spot_cells = {}  # (level_id, spot_id) -> {"rect": id, "label": id, "vehicle": id or None}
        self.level_order = [lvl.id for lvl in self.lot.levels]

        # Build a spot list per level for UI layout
        self.spots_by_level = {lvl.id: lvl.parkingspots[:] for lvl in self.lot.levels}

        self._build_layout()
        self._draw_parking_grid()
        self._refresh_all()

    # ---------- Layout ----------

    def _build_layout(self):
        # Top frame: controls
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Vehicle Type:").grid(row=0, column=0, sticky="w")
        self.vehicle_type_var = tk.StringVar(value=VehicleType.CAR.value)
        self.vehicle_type_combo = ttk.Combobox(
            top,
            textvariable=self.vehicle_type_var,
            values=[vt.value for vt in VehicleType],
            state="readonly",
            width=15
        )
        self.vehicle_type_combo.grid(row=0, column=1, padx=8)

        ttk.Label(top, text="Vehicle ID:").grid(row=0, column=2, sticky="w")
        self.vehicle_id_entry = ttk.Entry(top, width=22)
        self.vehicle_id_entry.grid(row=0, column=3, padx=8)
        self.vehicle_id_entry.insert(0, "KA-01-1234")

        self.park_btn = ttk.Button(top, text="Enter / Park", command=self._on_enter)
        self.park_btn.grid(row=0, column=4, padx=8)

        self.exit_btn = ttk.Button(top, text="Exit Selected Ticket", command=self._on_exit)
        self.exit_btn.grid(row=0, column=5, padx=8)

        self.refresh_btn = ttk.Button(top, text="Refresh", command=self._refresh_all)
        self.refresh_btn.grid(row=0, column=6, padx=8)

        # Middle: left = canvas, right = info panels
        mid = ttk.Frame(self, padding=10)
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        # Canvas area
        canvas_wrap = ttk.LabelFrame(mid, text="Parking Lot View", padding=10)
        canvas_wrap.grid(row=0, column=0, sticky="n")

        self.canvas = tk.Canvas(canvas_wrap, width=760, height=600, bg="white")
        self.canvas.pack()

        # Right panel
        right = ttk.Frame(mid)
        right.grid(row=0, column=1, padx=12, sticky="n")

        # Availability box
        avail_box = ttk.LabelFrame(right, text="Availability", padding=10)
        avail_box.pack(fill=tk.X)

        self.avail_labels = {
            VehicleType.MOTORCYCLE: ttk.Label(avail_box, text="Motorcycle: -"),
            VehicleType.CAR: ttk.Label(avail_box, text="Car: -"),
            VehicleType.TRUCK: ttk.Label(avail_box, text="Truck: -"),
        }
        self.avail_labels[VehicleType.MOTORCYCLE].pack(anchor="w")
        self.avail_labels[VehicleType.CAR].pack(anchor="w")
        self.avail_labels[VehicleType.TRUCK].pack(anchor="w")

        # Tickets list
        tickets_box = ttk.LabelFrame(right, text="Active Tickets", padding=10)
        tickets_box.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.ticket_list = tk.Listbox(tickets_box, width=42, height=20)
        self.ticket_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(tickets_box, orient="vertical", command=self.ticket_list.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ticket_list.configure(yscrollcommand=scroll.set)

        # Legend
        legend = ttk.LabelFrame(right, text="Legend", padding=10)
        legend.pack(fill=tk.X, pady=(12, 0))

        ttk.Label(legend, text="CAR = red brick").pack(anchor="w")
        ttk.Label(legend, text="MOTORCYCLE = thin blue stick").pack(anchor="w")
        ttk.Label(legend, text="TRUCK/VAN = big yellow block").pack(anchor="w")

        # Status bar bottom
        self.status_var = tk.StringVar(value="Ready.")
        status = ttk.Label(self, textvariable=self.status_var, padding=8)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- Grid Drawing ----------

    def _draw_parking_grid(self):
        """
        Draw a simple grid:
        - Each level is a row
        - Each spot is a cell
        - Cell shows spot_id + type
        - Vehicle shape appears inside when occupied
        """
        self.canvas.delete("all")
        self.spot_cells.clear()

        # Layout constants
        margin_x = 20
        margin_y = 20
        cell_w = 110
        cell_h = 80
        row_gap = 35

        title_x = margin_x
        title_y = margin_y

        self.canvas.create_text(title_x, title_y, text="Levels (top to bottom)", anchor="w", font=("Arial", 12, "bold"))
        y = title_y + 20

        for lvl_idx, level_id in enumerate(self.level_order):
            spots = self.spots_by_level[level_id]

            # Level label
            self.canvas.create_text(margin_x, y + cell_h / 2, text=f"{level_id}", anchor="w", font=("Arial", 12, "bold"))

            x = margin_x + 70
            for sp in spots:
                slot = (level_id, sp.id)

                rect = self.canvas.create_rectangle(
                    x, y, x + cell_w, y + cell_h,
                    outline="#222", width=2, fill="#f5f5f5"
                )

                label = self.canvas.create_text(
                    x + 6, y + 6,
                    text=f"{sp.id}\n({sp.type.value})",
                    anchor="nw",
                    font=("Arial", 9)
                )

                self.spot_cells[slot] = {"rect": rect, "label": label, "vehicle": None}
                x += cell_w + 10

            y += cell_h + row_gap

    # ---------- Rendering Vehicles ----------

    def _draw_vehicle_in_cell(self, slot, vehicle_type: VehicleType, vehicle_id: str):
        """
        Draw a colored block inside the spot cell.
        CAR: red brick (rect)
        MOTORCYCLE: thin blue stick
        TRUCK: big yellow block
        """
        cell = self.spot_cells.get(slot)
        if not cell:
            return

        # Remove old vehicle shape if present
        if cell["vehicle"] is not None:
            self.canvas.delete(cell["vehicle"])
            cell["vehicle"] = None

        x1, y1, x2, y2 = self.canvas.coords(cell["rect"])

        padding = 10
        inner_x1 = x1 + padding
        inner_y1 = y1 + padding + 18
        inner_x2 = x2 - padding
        inner_y2 = y2 - padding

        # Shapes
        if vehicle_type == VehicleType.CAR:
            # Red brick
            vid = self.canvas.create_rectangle(
                inner_x1, inner_y1 + 10,
                inner_x2, inner_y2,
                fill="red", outline="black", width=2
            )
        elif vehicle_type == VehicleType.MOTORCYCLE:
            # Thin blue stick
            mid_x = (inner_x1 + inner_x2) / 2
            vid = self.canvas.create_rectangle(
                mid_x - 10, inner_y1,
                mid_x + 10, inner_y2,
                fill="blue", outline="black", width=2
            )
        else:
            # TRUCK: big yellow block
            vid = self.canvas.create_rectangle(
                inner_x1, inner_y1,
                inner_x2, inner_y2,
                fill="yellow", outline="black", width=2
            )

        # Small ID text overlay
        self.canvas.create_text(
            (inner_x1 + inner_x2) / 2,
            inner_y1 - 6,
            text=vehicle_id,
            font=("Arial", 8),
            anchor="s"
        )

        cell["vehicle"] = vid

    def _clear_vehicle_in_cell(self, slot):
        cell = self.spot_cells.get(slot)
        if not cell:
            return
        if cell["vehicle"] is not None:
            self.canvas.delete(cell["vehicle"])
            cell["vehicle"] = None

    # ---------- Actions ----------

    def _on_enter(self):
        vehicle_id = self.vehicle_id_entry.get().strip()
        vt_str = self.vehicle_type_var.get().strip()

        if not vehicle_id:
            messagebox.showerror("Error", "Vehicle ID cannot be empty.")
            return

        try:
            vehicle_type = VehicleType(vt_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid vehicle type.")
            return

        try:
            ticket = self.lot.entry_into_lot(Vehicle(vehicle_id, vehicle_type))
            self.status_var.set(f"Parked {vehicle_type.value} '{vehicle_id}' at {ticket.parking_slot}. Ticket={ticket.id[:8]}...")
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Entry Failed", str(e))

    def _on_exit(self):
        sel = self.ticket_list.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a ticket from the list first.")
            return

        item_text = self.ticket_list.get(sel[0])
        # Stored as: "ticketIdShort | vehicleId | type | (level,spot)"
        # We'll keep a map from list index -> real ticket id in refresh
        ticket_id = self._ticket_index_to_id.get(sel[0])
        if not ticket_id:
            messagebox.showerror("Error", "Could not resolve selected ticket.")
            return

        # Get the ticket object from the backend using occupied_spot lookup:
        ticket_obj = None
        # quick lookup: backend stores vehicle_id -> Ticket
        # We stored ticket_id in list; find it
        for t in self.lot.occupied_spot.values():
            if t.id == ticket_id:
                ticket_obj = t
                break

        if ticket_obj is None:
            messagebox.showerror("Exit Failed", "Ticket not found (maybe already exited).")
            self._refresh_all()
            return

        try:
            fee = self.lot.exit_lot(ticket_obj)
            if fee > 0:
                self.status_var.set(f"Exited '{ticket_obj.vehicle.id}'. Fee: {fee} cents. Spot freed: {ticket_obj.parking_slot}")
            else:
                self.status_var.set(f"Exited '{ticket_obj.vehicle.id}'. Spot freed: {ticket_obj.parking_slot}")
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Exit Failed", str(e))

    # ---------- Refresh UI from Backend ----------

    def _refresh_all(self):
        # 1) Availability counts
        self.avail_labels[VehicleType.MOTORCYCLE].configure(
            text=f"Motorcycle: {self.lot.display_availability(VehicleType.MOTORCYCLE)}"
        )
        self.avail_labels[VehicleType.CAR].configure(
            text=f"Car: {self.lot.display_availability(VehicleType.CAR)}"
        )
        self.avail_labels[VehicleType.TRUCK].configure(
            text=f"Truck: {self.lot.display_availability(VehicleType.TRUCK)}"
        )

        # 2) Clear all vehicles first, then redraw occupied
        for slot in self.spot_cells.keys():
            self._clear_vehicle_in_cell(slot)

        for ticket in self.lot.occupied_spot.values():
            self._draw_vehicle_in_cell(ticket.parking_slot, ticket.vehicle.type, ticket.vehicle.id)

        # 3) Tickets list
        self.ticket_list.delete(0, tk.END)
        self._ticket_index_to_id = {}

        # show newest on top (optional)
        tickets = list(self.lot.occupied_spot.values())
        tickets.sort(key=lambda t: t.entry_time_ms, reverse=True)

        for idx, t in enumerate(tickets):
            short = t.id.split("-")[0]
            txt = f"{short} | {t.vehicle.id} | {t.vehicle.type.value} | {t.parking_slot}"
            self.ticket_list.insert(tk.END, txt)
            self._ticket_index_to_id[idx] = t.id


# -------------------- Build a Demo Lot --------------------

def build_demo_lot() -> ParkingLot:
    """
    Creates a small multi-level lot:
    L1: 2 cars, 2 motorcycles, 1 truck
    L2: 3 cars, 1 motorcycle, 1 truck
    """
    levels = [
        Level(
            id="L1",
            parkingspots=[
                ParkingSpot("C1", VehicleType.CAR),
                ParkingSpot("C2", VehicleType.CAR),
                ParkingSpot("M1", VehicleType.MOTORCYCLE),
                ParkingSpot("M2", VehicleType.MOTORCYCLE),
                ParkingSpot("T1", VehicleType.TRUCK),
            ],
        ),
        Level(
            id="L2",
            parkingspots=[
                ParkingSpot("C3", VehicleType.CAR),
                ParkingSpot("C4", VehicleType.CAR),
                ParkingSpot("C5", VehicleType.CAR),
                ParkingSpot("M3", VehicleType.MOTORCYCLE),
                ParkingSpot("T2", VehicleType.TRUCK),
            ],
        ),
    ]

    # hourly_rate_cents optional; keep 0 for demo or set like 500
    return ParkingLot(parking_lot_levels=levels, hourly_rate_cents=0)


if __name__ == "__main__":
    lot = build_demo_lot()
    app = ParkingLotUI(lot)
    app.mainloop()
