# Smart Locker System (Mini Project)

A simple Python mini project that simulates a smart locker system.

## Files
- `AmazonLocker.py`  
  Contains the backend logic (classes like `Locker`, `AccessToken`, `Staff`, `LockerSystem`) and authorization rules.
- `app.py`  
  A simple command line UI that lets you interact with the locker system using a menu.

## Requirements
- Python 3.12+ 

No external libraries needed (only Python standard library).

## What `app.py` does
`app.py` provides a menu to:
- View lockers and their status (EMPTY / OCCUPIED)
- Staff: Insert a package into a locker (generates a token)
- Staff: Open and clear expired packages (staff-only)
- Customer: Pick up a package using a token code

## How to Run
```bash
python app.py
