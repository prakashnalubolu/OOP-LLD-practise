from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random
from typing import Dict, List


class AuthorizationError(Exception):
    pass

class Size(Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

@dataclass(frozen=True)
class Staff:
    id: str
    active: bool = True

    def is_valid(self) -> bool:
        return bool(self.id) and self.active

@dataclass
class Locker:
    id: str
    size: Size
    occupied: bool = False

    def open(self) -> None:
        # Replace with actual hardware integration if needed
        print(f"[LOCKER OPENED] Locker {self.id} ({self.size.value})")

    def is_empty(self) -> bool:
        return not self.occupied

    def mark_full(self) -> None:
        self.occupied = True

    def mark_empty(self) -> None:
        self.occupied = False

@dataclass(frozen=True)
class AccessToken:
    code: str
    expiration_date: datetime
    compartment: Locker

    def is_expired(self) -> bool:
        return datetime.now() >= self.expiration_date

    def get_compartment(self) -> Locker:
        return self.compartment

    def get_code(self) -> str:
        return self.code
    
#Can change this whenever needed, as per new rules
token_valid_days = 7

class LockerSystem:
    """
    Authorization rules:
    - Only valid staff can:
        - insert packages
        - access/open expired packages
    - Customers can pick up with valid + unexpired token
    """

    def __init__(self, lockers: List[Locker]):
        self.lockers: List[Locker] = lockers
        # Store actual token objects by token code
        self._tokens_by_code: Dict[str, AccessToken] = {}


    # Staff-only operations
    def insert_package_into_locker(self, staff: Staff, package_size: Size) -> AccessToken:
        self._require_staff(staff)

        for locker in self.lockers:
            if locker.size == package_size and locker.is_empty():
                token = self._generate_access_token(locker)
                locker.mark_full()
                self._tokens_by_code[token.get_code()] = token
                return token

        raise ValueError(f"No available locker of size {package_size.value}")

    def open_expired_packages(self, staff: Staff) -> List[Locker]:
        """
        Finds all expired tokens, opens their lockers, clears tokens and marks those lockers empty (since staff is removing the packages).
        Returns the list of lockers that were opened.
        """
        self._require_staff(staff)

        expired_codes = [code for code, tok in self._tokens_by_code.items() if tok.is_expired()]
        opened_lockers: List[Locker] = []

        for code in expired_codes:
            tok = self._tokens_by_code.pop(code)
            locker = tok.get_compartment()
            locker.open()
            locker.mark_empty()
            opened_lockers.append(locker)

        return opened_lockers

 
    # Customer operation
    def pick_up_package(self, token_code: str) -> str:
        """
        Customer provides token_code.
        check invalid token -> "invalid_token"
        check expired token -> "token_expired"
        (success)-> opens locker, marks empty, removes token -> "picked_up"
        """
        tok = self._tokens_by_code.get(token_code)
        if tok is None:
            return "invalid_token"
        if tok.is_expired():
            return "token_expired"

        locker = tok.get_compartment()
        locker.open()
        locker.mark_empty()
        self._tokens_by_code.pop(token_code, None)
        return "picked_up"

    
    def _generate_access_token(self, compartment: Locker) -> AccessToken:
        # 6-digit token, avoid collisions
        while True:
            code = f"{random.randint(0, 999999):06d}" #genrates a random int, pad 0s in empty spaces, 6 ensures 6 digits, d is integer
            if code not in self._tokens_by_code:
                break

        expiration_date = datetime.now() + timedelta(days=token_valid_days)
        return AccessToken(code=code, expiration_date=expiration_date, compartment=compartment)

    def _require_staff(self, staff: Staff) -> None:
        if staff is None or not staff.is_valid():
            raise AuthorizationError("Unauthorized: only valid staff can perform this action.")

"""
# Example usage
if __name__ == "__main__":
    lockers = [
        Locker("A1", Size.SMALL),
        Locker("A2", Size.SMALL),
        Locker("B1", Size.MEDIUM),
        Locker("C1", Size.LARGE),
    ]

    system = LockerSystem(lockers)
    staff = Staff(id="S-1001", active=True)

    # Staff inserts a package
    token = system.insert_package_into_locker(staff, Size.SMALL)
    print("Token code:", token.get_code())

    # Customer picks up
    print(system.pick_up_package(token.get_code()))
"""