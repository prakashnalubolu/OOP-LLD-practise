from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"

@dataclass(frozen=True)
class Vehicle:
    id: str
    type: VehicleType


@dataclass(frozen=True)
class ParkingSpot:
    id: str
    type: VehicleType  # Spot supports exactly this vehicle type


@dataclass(frozen=True)
class Level:
    id: str
    parkingspots: List[ParkingSpot]


@dataclass(frozen=True)
class Ticket:
    id: str
    vehicle: Vehicle
    parking_slot: Tuple[str, str]  # (level_id, spot_id)
    entry_time_ms: int


class ParkingLotError(Exception):
    pass


class ParkingLot:
    """
    maintain free spot lists per vehicle type.

    - entry_into_lot: pop from relevant free list (O(1))
    - exit_lot: append back to relevant free list (O(1))
    - display_availability: len(free_list) (O(1))

    occupied_spot is a dict: vehicle_id -> Ticket (so we can validate exits, prevent duplicates)
    """

    def __init__(self, parking_lot_levels: List[Level], hourly_rate_cents: int = 0):
        if not parking_lot_levels:
            raise ValueError("parking_lot_levels cannot be empty")
        if hourly_rate_cents < 0:
            raise ValueError("hourly_rate_cents cannot be negative")

        self.levels = parking_lot_levels
        self.hourly_rate_cents = hourly_rate_cents

        # Free spot pools (stack behavior using list.pop()).
        # Each slot is stored as: (level_id, spot_id)
        self.empty_motorcycle_spots: List[Tuple[str, str]] = []
        self.empty_car_spots: List[Tuple[str, str]] = []
        self.empty_truck_spots: List[Tuple[str, str]] = []

        # vehicle_id -> Ticket
        self.occupied_spot: Dict[str, Ticket] = {}

        # (level_id, spot_id) -> VehicleType (helps validate & release correctly)
        self.spot_type_by_slot: Dict[Tuple[str, str], VehicleType] = {}

        self.__update_empty_spots__()

    # Tradeoff:
    # - If you store free spots, entry/exit are O(1) and availability is O(1).
    # - If you store occupied-only, you often need a scan to find free slots (O(n)) unless you add extra indexing.

    def __update_empty_spots__(self) -> None:
        """Build the free spot pools from levels (initial state assumes everything is empty)."""
        for level in self.levels:
            for spot in level.parkingspots:
                slot = (level.id, spot.id)
                if slot in self.spot_type_by_slot:
                    raise ValueError(f"Duplicate spot found: {slot}")

                self.spot_type_by_slot[slot] = spot.type

                if spot.type == VehicleType.MOTORCYCLE:
                    self.empty_motorcycle_spots.append(slot)
                elif spot.type == VehicleType.CAR:
                    self.empty_car_spots.append(slot)
                elif spot.type == VehicleType.TRUCK:
                    self.empty_truck_spots.append(slot)
                else:
                    raise ValueError(f"Unknown spot type: {spot.type}")

    def entry_into_lot(self, vehicle: Vehicle) -> Ticket:
        if not vehicle.id:
            raise ParkingLotError("Vehicle id cannot be empty")

        # Avoid multiple entries for same vehicle
        if vehicle.id in self.occupied_spot:
            raise ParkingLotError("Vehicle already exists in the Parking Lot")

        free_list = self._get_free_list(vehicle.type)

        if not free_list:
            raise ParkingLotError(f"No available parking slots for {vehicle.type.value}")

        parking_slot = free_list.pop()

        ticket = Ticket(
            id=str(uuid.uuid4()),
            vehicle=vehicle,
            parking_slot=parking_slot,
            entry_time_ms=int(time.time() * 1000),
        )

        self.occupied_spot[vehicle.id] = ticket
        return ticket

    def exit_lot(self, ticket: Ticket) -> int:
        if ticket is None:
            raise ParkingLotError("Ticket cannot be None")

        vehicle_id = ticket.vehicle.id

        existing = self.occupied_spot.get(vehicle_id)
        if existing is None:
            raise ParkingLotError("Vehicle does not exist in the parking lot")

        # (Optional) ensure ticket matches the active one (prevents using old ticket)
        if existing.id != ticket.id:
            raise ParkingLotError("Ticket is not active / does not match current vehicle entry")

        slot = ticket.parking_slot
        slot_type = self.spot_type_by_slot.get(slot)
        if slot_type is None:
            raise ParkingLotError("Invalid parking slot on ticket")

        # Release slot back to correct free list
        self._get_free_list(slot_type).append(slot)

        # Remove occupancy
        del self.occupied_spot[vehicle_id]

        # Fee (optional)
        if self.hourly_rate_cents <= 0:
            return 0

        exit_time_ms = int(time.time() * 1000)
        return self._compute_fee(ticket.entry_time_ms, exit_time_ms)

    def display_availability(self, vehicle_type: VehicleType) -> int:
        """Return number of free spots for that type."""
        return len(self._get_free_list(vehicle_type))

    def _get_free_list(self, vehicle_type: VehicleType) -> List[Tuple[str, str]]:
        if vehicle_type == VehicleType.MOTORCYCLE:
            return self.empty_motorcycle_spots
        if vehicle_type == VehicleType.CAR:
            return self.empty_car_spots
        if vehicle_type == VehicleType.TRUCK:
            return self.empty_truck_spots
        raise ParkingLotError(f"Unsupported vehicle type: {vehicle_type}")

    def _compute_fee(self, entry_time_ms: int, exit_time_ms: int) -> int:
        if exit_time_ms < entry_time_ms:
            raise ParkingLotError("Exit time cannot be earlier than entry time")

        duration_ms = exit_time_ms - entry_time_ms
        hour_ms = 1000 * 60 * 60

        hours = duration_ms // hour_ms
        if duration_ms % hour_ms != 0:
            hours += 1  # round up partial hour
        if hours == 0:
            hours = 1  # minimum 1 hour

        return hours * self.hourly_rate_cents
