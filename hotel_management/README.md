# 🏨 Grand Palace Hotel Management System

A complete **Python + SQLite** Hotel Management System with a menu-driven CLI.  
Covers Rooms, Guests, Bookings (advance & walk-in), Restaurant, and Billing.

---

## Features

| Module | Capabilities |
|---|---|
| **Rooms** | Inventory view, availability check by date, add rooms, maintenance flag |
| **Guests** | Register, search by phone, list all |
| **Bookings** | Advance / same-day booking, check-in, check-out, cancellation |
| **Restaurant** | Full menu (5 categories), room-service orders, order status tracking |
| **Billing** | Auto bill generation (room + restaurant + 12% GST), Cash/Card/UPI payment |

---

## Project Structure

```
hotel_management/
├── main.py          ← Entry point, full CLI menus
├── database.py      ← SQLite schema + seeding (10 rooms, 18 menu items)
├── rooms.py         ← Room inventory procedures
├── bookings.py      ← Guest & booking procedures
├── restaurant.py    ← Menu & order procedures
├── billing.py       ← Bill generation & payment procedures
├── utils.py         ← Display helpers (tables, prompts, receipt printer)
└── hotel.db         ← Auto-created SQLite database (gitignore this)
```

---

## How to Run

```bash
cd hotel_management
python3 main.py
```

No external dependencies — pure Python 3 standard library + SQLite3.

---

## Sample Workflow

1. **Register a Guest** → Guest Management → Register New Guest  
2. **Create a Booking** → Booking Management → New Booking → pick dates & room  
3. **Check In** → Booking Management → Check In → enter Booking ID  
4. **Place Restaurant Order** → Restaurant → Place Order → pick items  
5. **Generate & Pay Bill** → Billing → Generate Bill → Process Payment  
6. **Check Out** → Booking Management → Check Out  

Advance bookings (future check-in dates) are fully supported — the room is reserved and the status stays "Reserved" until check-in.

---

## Database Schema

```
rooms              room_id, room_number, room_type, price_per_night, status
guests             guest_id, name, phone, email, id_proof
bookings           booking_id, guest_id, room_id, check_in/out_date, status, total_amount
menu_items         item_id, item_name, category, price, available
restaurant_orders  order_id, booking_id, room_number, order_date, total_amount, status
order_items        id, order_id, item_id, quantity, unit_price
bills              bill_id, booking_id, room/restaurant/tax/total charges, payment_status
```

All foreign keys enforced. Room status auto-updates on check-in/check-out.  
Billing = Room charges + Restaurant charges + 12% GST.
