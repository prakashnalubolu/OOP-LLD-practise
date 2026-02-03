# 🚗 Parking Lot System Simulator (Python)
<img width="1097" height="748" alt="image" src="https://github.com/user-attachments/assets/63a5bfc1-3cbc-4a1f-9b51-e75b75c223ea" />
<img width="1094" height="745" alt="image" src="https://github.com/user-attachments/assets/d75e5b56-ad80-4cfb-ae3b-488571e2be76" />

This project is a simple offline Parking Lot System built using Python.  
It demonstrates object-oriented design, system modeling, and basic UI simulation.

The project includes:
- A backend parking lot management system
- A visual UI to simulate vehicle parking and exit
- Support for multiple levels and vehicle types

---

## 📌 Features

- Multiple parking levels
- Supports Cars, Motorcycles, and Trucks
- Automatic parking spot assignment
- Ticket generation on entry
- Spot release on exit
- Real-time availability display
- Offline graphical simulation (Tkinter UI)

---

## 🏗️ Design Approach

I used the **free-spots pool approach**:

- Maintain separate lists of available spots for each vehicle type
- Allocate spots using `pop()` (O(1) time)
- Release spots using `append()` (O(1) time)
- Track active vehicles using a dictionary

### Why this approach?

This makes:
- Entry → O(1)
- Exit → O(1)
- Availability check → O(1)

It performs efficiently whether the parking lot is busy or mostly empty.

---



## ▶️ How to Run

Make sure both files are in the same folder.
```bash
python ui.py
```
The simulator will open in a window and works completely offline.

🧠 My Contribution 

Designed the system architecture ,
Implemented core backend logic ,
Built parking spot management ,
Implemented ticket handling and availability tracking ,
Chose and implemented the free-spots optimization approach ,
The backend logic and system design were coded by me. 

🤖 AI Assistance 
AI tools were used mainly for: 
UI generation using Tkinter ,
Improving code structure ,
Minor refactoring and documentation ,
All design decisions and core logic are my own. 

📈 Learning Outcome 
Through this project, I learned: 
How to design scalable object-oriented systems ,
How to optimize resource allocation ,
How to separate backend logic from UI ,
How to reason about time and space complexity ,
How to simulate real-world systems in code ,
This project was built as part of my Low-Level Design (LLD) interview preparation. 

✅ Future Improvements 
Add database support ,
Add multiple entry/exit gates ,
Improve UI animation ,
Add payment gateway simulation ,
Add priority parking (EV / handicap spots) 

👨‍💻 Author - Saiprakash Nalubolu
