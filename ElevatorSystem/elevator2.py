#Pure practise
"""
The elevator system should consist of multiple elevators serving multiple floors.
Each elevator should have a capacity limit and should not exceed it.
Users should be able to request an elevator from any floor and select a destination floor.
 The elevator system should efficiently handle user requests and optimize the movement of elevators to minimize waiting time.
The system should prioritize requests based on the direction of travel and the proximity of the elevators to the requested floor.
 The elevators should be able to handle multiple requests concurrently and process them in an optimal order.
 The system should ensure thread safety and prevent race conditions when multiple threads interact with the elevators.
"""
#Design choices: Odd, Even; 1-10,11-20(Split 100 floors evenly as per number of elevators), All elevators go to every floor
#mainly concentrate on APIs and data flow Design a complete system.
from enum import Enum

max_floor = 10
min_floor = 0

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    IDLE = "idle"

class Request():
    def __init__(self, id, curr_floor: int, direction: Direction):
        self.id = id
        self.curr_floor = curr_floor
        self.direction = Direction

    def is_valid_request(self, curr_floor, direction):
        if curr_floor > max_floor or curr_floor < min_floor:
            return False
        if direction == Direction.IDLE:
            return False
        else:
            return True



class Elevator:
    def __init__(self, id, max_capacity):
        self.id = id
        self.capacity = max_capacity
        self.curr_floor = 0
        self.direction = Direction.IDLE

        # Two stacks of pending stops: 
        self.up_stops = [] # up_stops: sorted ascending, pop(0) gives the next closest upward stop
        self.down_stops = [] # down_stops: sorted descending, pop(0) gives the next closest downward stop


    def add_new_floor(self, new_floor: int) -> bool:
        if new_floor < min_floor or new_floor > max_floor:
            return False

        if new_floor in self.up_stops or new_floor in self.down_stops:
            return False

        if new_floor > self.curr_floor:
            # keep ascending
            sorted(self.up_stops, new_floor)
        elif new_floor < self.curr_floor:
            self.down_stops.append(new_floor)
            self.down_stops.sort(reverse=True)
        else:
            return False

        # If elevator was idle, start moving in the needed direction
        if self.direction == Direction.IDLE:
            if self.up_stops:
                self.direction = Direction.UP
            elif self.down_stops:
                self.direction = Direction.DOWN

        return True
    
    #whihc floor to go next
    def go_to_next_floor(self) -> int | None:
        # If idle, pick a direction based on available work
        if self.direction == Direction.IDLE:
            if self.up_stops:
                self.direction = Direction.UP
            elif self.down_stops:
                self.direction = Direction.DOWN
            else:
                return None

        if self.direction == Direction.UP:
            if self.up_stops:
                return self.up_stops[0]  # closest upward stop
                # no more up stops -> flip if down exists
            if self.down_stops:
                self.direction = Direction.DOWN
                return self.down_stops[0]
            self.direction = Direction.IDLE
            return None

        if self.direction == Direction.DOWN:
            if self.down_stops:
                return self.down_stops[0]  # closest downward stop
            # no more down stops -> flip if up exists
            if self.up_stops:
                self.direction = Direction.UP
                return self.up_stops[0]
            self.direction = Direction.IDLE
            return None

        return None

    # pops out floor if a floor is reached
    def floor_reached(self, curr_floor: int) -> None:
        self.curr_floor = curr_floor

        if self.up_stops and self.up_stops[0] == curr_floor:
            self.up_stops.pop(0)
        elif self.down_stops and self.down_stops[0] == curr_floor:
            self.down_stops.pop(0)
        else:
            if curr_floor in self.up_stops:
                self.up_stops.remove(curr_floor)
            if curr_floor in self.down_stops:
                self.down_stops.remove(curr_floor)

        # Recompute direction if current direction has no more work
        if self.direction == Direction.UP and not self.up_stops:
            self.direction = Direction.DOWN if self.down_stops else Direction.IDLE
        elif self.direction == Direction.DOWN and not self.down_stops:
            self.direction = Direction.UP if self.up_stops else Direction.IDLE
        elif self.direction == Direction.IDLE:
            if self.up_stops:
                self.direction = Direction.UP
            elif self.down_stops:
                self.direction = Direction.DOWN


class Elevatorsystem():
    def __init__(self, list_of_elevators):
        self.elevators = list_of_elevators #All available elevators, initialized and currently in idle state
        self.requests = []
        

        self._up = [] #(elevator,floor) #Elevators that are going up 
        self._down = [] #elevators that are going down

    def add_a_request(self, new_request: Request):
        self.requests.append(new_request)

    # Helper: pick closest elevator from a list, return best elevator and best difference
    def closest(self, requested_floor, elevators):
        best_elevator = None
        best_diff = max_floor
        for e in elevators:
            diff = abs(requested_floor - e.curr_floor)
            if diff < best_diff:
                best_diff = diff
                best_elevator = e
        return best_elevator, best_diff
    
    #prioritize requests based on the direction of travel and the proximity of the elevators to the requested floor.
    def assign_a_request_to_an_elevator(self, request: Request) -> "Elevator | str":
        if not request.is_valid_request:
            return "Not a valid request"

        requested_floor = request.curr_floor

        idle = [e for e in self.elevators if e.direction != Direction.IDLE]
        best_idle, diff_idle = self.closest(requested_floor, idle) if idle else (None, max_floor)

        if request.direction == Direction.UP:
            primary = self._up
            secondary = self._down
        else:  # Direction.DOWN
            primary = self._down
            secondary = self._up

        best_primary, diff_primary = self.closest(requested_floor, primary) if primary else (None, float("inf"))
        best_secondary, _ = self.closest(requested_floor, secondary) if secondary else (None, float("inf"))

        if best_primary and diff_primary < diff_idle:
            chosen = best_primary
        elif best_idle:
            chosen = best_idle
            #since the best is idle, we are moving it so add the elevator to resepective lists
            if request.direction == Direction.UP:
                self._up.append(chosen)
            elif request.direction == Direction.DOWN:
                self._down.append(chosen)
        else:
            chosen = best_secondary

        if chosen is None:
            return "No elevator available"

        self.add_a_request(request)
        chosen.is_idle = False

        return chosen

    def process_requests(self, requests):
        for request in requests:
            self.assign_a_request_to_an_elevator(request)
