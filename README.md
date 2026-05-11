# 🏨 Hotel Management System

A fully functional **Hotel Management System** built with pure Python 3 and SQLite — no external dependencies required.  
Covers the complete guest lifecycle: room inventory → booking → restaurant orders → billing → checkout.

---

## ✨ Features

| Module | What it does |
|---|---|
| **Rooms** | View all rooms, check availability by date range, add new rooms, flag rooms for maintenance |
| **Guests** | Register new guests, search by phone number, view all guest records |
| **Bookings** | Advance & same-day bookings, check-in, check-out, cancellation with conflict detection |
| **Restaurant** | Full menu across 5 categories, room-service order placement, order status tracking |
| **Billing** | Auto bill generation (room charges + restaurant charges + 12% GST), Cash / Card / UPI payment, revenue report |

---

## 🗂️ Project Structure

---

## 🚀 Getting Started

**Requirements:** Python 3.8+  — no pip installs needed.

```bash
git clone https://github.com/Prakashshaw25/hotel-management-system.git
cd hotel-management-system
python3 main.py
```

The database (`hotel.db`) is created and seeded automatically on first run.

---

## 🖥️ Sample Workflow
> Advance bookings (future check-in dates) are fully supported.  
> The room stays **Reserved** until the guest checks in.

---

## 🗄️ Database Schema
All foreign keys are enforced. Room status updates automatically on check-in and check-out.

---

## 🛎️ Seeded Data

### Rooms (10 total)

| Room | Type | Price / Night |
|---|---|---|
| 101 – 103 | Single | ₹1,500 |
| 201 – 203 | Double | ₹2,500 |
| 301 – 302 | Deluxe | ₹4,000 |
| 401 – 402 | Suite | ₹7,000 |

### Menu (18 items across 5 categories)
`Breakfast` · `Lunch` · `Dinner` · `Beverages` · `Snacks`

---

## 💳 Billing Logic

| Component | Calculation |
|---|---|
| Room Charges | price_per_night × number of nights |
| Restaurant | Sum of all Served/Billed orders for the booking |
| GST (12%) | (Room Charges + Restaurant) × 0.12 |
| **Total** | **Room Charges + Restaurant + GST** |

> A guest cannot check out until the bill is marked **Paid**.
---

## 📁 .gitignore tip

```gitignore
hotel.db
__pycache__/
*.pyc
```

---

## 🛠️ Tech Stack

- **Language:** Python 3
- **Database:** SQLite 3 (via `sqlite3` standard library)
- **Interface:** CLI (menu-driven)
- **Dependencies:** None

---

## 👤 Author

**Prakash Shaw**  

([https://github.com/Prakashshaw25](https://github.com/Prakashshaw25/))
