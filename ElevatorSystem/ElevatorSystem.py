from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from bisect import insort
from threading import Lock
from typing import List, Optional, Dict


MIN_FLOOR = 0
MAX_FLOOR = 10


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    IDLE = "idle"


@dataclass(frozen=True)
class HallRequest:
    """User requests an elevator at a floor going UP/DOWN."""
    request_id: str
    floor: int
    direction: Direction

    def is_valid(self) -> bool:
        if not (MIN_FLOOR <= self.floor <= MAX_FLOOR):
            return False
        if self.direction not in (Direction.UP, Direction.DOWN):
            return False
        return True


class Elevator:
    """
    Elevator keeps two ordered stop lists:
      - up_stops: ascending floors
      - down_stops: descending floors
    """
    def __init__(self, elevator_id: str, max_capacity: int = 8):
        self.id = elevator_id
        self.max_capacity = max_capacity  # kept for completeness; not enforced in this simplified model

        self.curr_floor: int = 0
        self.direction: Direction = Direction.IDLE

        self.up_stops: List[int] = []     # ascending
        self.down_stops: List[int] = []   # descending

        self._lock = Lock()

    # ---------- stop management ----------
    def add_stop(self, floor: int) -> bool:
        """Add a stop; keeps ordering and avoids duplicates."""
        if not (MIN_FLOOR <= floor <= MAX_FLOOR):
            return False

        with self._lock:
            if floor == self.curr_floor:
                # already here; treat as served
                return True

            if floor in self.up_stops or floor in self.down_stops:
                return False

            if floor > self.curr_floor:
                insort(self.up_stops, floor)   # keeps ascending
            else:
                # keep descending
                insort(self.down_stops, floor)
                self.down_stops.sort(reverse=True)

            # if idle, choose initial direction
            if self.direction == Direction.IDLE:
                if self.up_stops:
                    self.direction = Direction.UP
                elif self.down_stops:
                    self.direction = Direction.DOWN

            return True

    def has_work(self) -> bool:
        with self._lock:
            return bool(self.up_stops or self.down_stops)

    def is_idle(self) -> bool:
        with self._lock:
            return self.direction == Direction.IDLE and not self.up_stops and not self.down_stops

    def will_pass_floor_in_direction(self, floor: int, direction: Direction) -> bool:
        """
        True if elevator is currently moving in 'direction' and the requested floor is ahead
        (so it can pick up with minimal disruption).
        """
        with self._lock:
            if self.direction != direction:
                return False

            if direction == Direction.UP:
                return floor >= self.curr_floor
            if direction == Direction.DOWN:
                return floor <= self.curr_floor
            return False

    # ---------- movement simulation ----------
    def next_target(self) -> Optional[int]:
        with self._lock:
            if self.direction == Direction.IDLE:
                if self.up_stops:
                    self.direction = Direction.UP
                elif self.down_stops:
                    self.direction = Direction.DOWN
                else:
                    return None

            if self.direction == Direction.UP:
                if self.up_stops:
                    return self.up_stops[0]
                # no more up -> maybe flip
                if self.down_stops:
                    self.direction = Direction.DOWN
                    return self.down_stops[0]
                self.direction = Direction.IDLE
                return None

            if self.direction == Direction.DOWN:
                if self.down_stops:
                    return self.down_stops[0]
                if self.up_stops:
                    self.direction = Direction.UP
                    return self.up_stops[0]
                self.direction = Direction.IDLE
                return None

            return None

    def step_one_floor(self) -> Optional[int]:
        """
        Move elevator one floor toward its current target.
        Returns current floor after moving (or None if idle/no target).
        """
        target = self.next_target()
        if target is None:
            return None

        with self._lock:
            if self.curr_floor < target:
                self.curr_floor += 1
                self.direction = Direction.UP
            elif self.curr_floor > target:
                self.curr_floor -= 1
                self.direction = Direction.DOWN
            else:
                # already on target; mark reached
                self._mark_floor_reached_locked(target)

            # if we arrived after moving
            if self.curr_floor == target:
                self._mark_floor_reached_locked(target)

            return self.curr_floor

    def _mark_floor_reached_locked(self, floor: int) -> None:
        """Caller must hold lock."""
        if self.up_stops and self.up_stops[0] == floor:
            self.up_stops.pop(0)
        elif self.down_stops and self.down_stops[0] == floor:
            self.down_stops.pop(0)
        else:
            # defensive cleanup (shouldn't happen if lists are correct)
            if floor in self.up_stops:
                self.up_stops.remove(floor)
            if floor in self.down_stops:
                self.down_stops.remove(floor)

        # recompute direction
        if self.up_stops:
            self.direction = Direction.UP
        elif self.down_stops:
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.IDLE


class ElevatorSystem:
    """
    Thread-safe dispatcher + collection of elevators.

    APIs you can call:
      - request_elevator(floor, direction) -> elevator_id
      - select_destination(elevator_id, dest_floor)
      - step() -> advances each elevator by one tick (simulation)
    """
    def __init__(self, elevators: List[Elevator]):
        self.elevators = elevators
        self._lock = Lock()

        # optional: track which elevator served which request
        self.request_assignment: Dict[str, str] = {}

    # ---------- public APIs ----------
    def request_elevator(self, request: HallRequest) -> Optional[str]:
        if not request.is_valid():
            return None

        with self._lock:
            elevator = self._select_best_elevator(request.floor, request.direction)
            if elevator is None:
                return None

            # pickup floor becomes a stop
            elevator.add_stop(request.floor)
            self.request_assignment[request.request_id] = elevator.id
            return elevator.id

    def select_destination(self, elevator_id: str, dest_floor: int) -> bool:
        if not (MIN_FLOOR <= dest_floor <= MAX_FLOOR):
            return False

        elev = self._get_elevator_by_id(elevator_id)
        if elev is None:
            return False

        return elev.add_stop(dest_floor)

    def step(self) -> None:
        """Simulation tick: move each elevator by one floor toward its next stop."""
        for e in self.elevators:
            e.step_one_floor()

    def snapshot(self) -> List[dict]:
        """For debugging / UI."""
        out = []
        for e in self.elevators:
            out.append({
                "id": e.id,
                "floor": e.curr_floor,
                "direction": e.direction.value,
                "up_stops": list(e.up_stops),
                "down_stops": list(e.down_stops),
            })
        return out

    # ---------- selection logic ----------
    def _select_best_elevator(self, floor: int, direction: Direction) -> Optional[Elevator]:
        # 1) elevators already moving toward the floor in same direction
        candidates_committed = [
            e for e in self.elevators
            if e.will_pass_floor_in_direction(floor, direction)
        ]
        best = self._closest_by_distance(floor, candidates_committed)
        if best is not None:
            return best

        # 2) nearest idle
        idle = [e for e in self.elevators if e.is_idle()]
        best = self._closest_by_distance(floor, idle)
        if best is not None:
            return best

        # 3) nearest overall (fallback)
        return self._closest_by_distance(floor, self.elevators)

    @staticmethod
    def _closest_by_distance(floor: int, elevators: List[Elevator]) -> Optional[Elevator]:
        best = None
        best_dist = float("inf")
        for e in elevators:
            dist = abs(e.curr_floor - floor)
            if dist < best_dist:
                best_dist = dist
                best = e
        return best

    def _get_elevator_by_id(self, elevator_id: str) -> Optional[Elevator]:
        for e in self.elevators:
            if e.id == elevator_id:
                return e
        return None

