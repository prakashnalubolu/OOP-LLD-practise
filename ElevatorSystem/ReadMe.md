# Elevator System – Low Level Design (LLD) Practice

## Overview
This project is an **offline elevator system simulator** built as part of my **Low Level Design (LLD) practice**.  
The focus of this project is on **system design, APIs, scheduling logic, and trade-offs**, not on production completeness or UI polish.

The simulator supports:
- Multiple elevators and floors
- Hall calls (UP / DOWN)
- Destination selection inside elevators
- Direction-aware elevator scheduling
- Real-time offline simulation using a simple UI

---

## Purpose
Elevator systems are a common **LLD interview problem** because they require:
- State management
- Scheduling and prioritization
- Clear separation of responsibilities
- Thoughtful trade-offs

This project helped me practice turning requirements into a working design while keeping the system simple, understandable, and extensible.

---

## Design Approach
- A **central dispatcher** assigns hall requests to elevators.
- Each elevator maintains **two ordered stop lists**:
  - One for upward travel
  - One for downward travel
- Requests are prioritized based on:
  1. Direction of travel
  2. Proximity to the requested floor
  3. Elevator availability (idle vs busy)
- Elevators move using a **step-based simulation**, advancing one floor per tick.

This approach balances realism with simplicity and is suitable for interview discussions.

---

## Trade-Offs Learned
- **Step-based simulation** keeps logic simple but is less realistic than continuous movement.
- **Two stop queues** improve routing efficiency but add complexity.
- A **single dispatcher** simplifies scheduling but becomes a central decision point.
- Offline UI (Tkinter) is lightweight but intentionally minimal.

---

## Tech Stack
- Python
- Tkinter (offline UI)
- Object-Oriented Design

---

## Inspiration & Credits
This project includes:
- **Original design and implementation**
- Ideas inspired by common LLD discussions, including:  
  https://www.hellointerview.com/learn/low-level-design/problem-breakdowns/elevator
- Refinements and feedback assisted by AI tools

All final design decisions and understanding are my own.

---

## How to Run
```bash
python app.py
