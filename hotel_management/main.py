#!/usr/bin/env python3
"""
Hotel Management System
=======================
A complete Python + SQLite hotel management application.
Manages rooms, guests, bookings, restaurant orders, and billing.
"""

import os, sys
from database import initialize_database
import utils as U
from rooms      import (view_all_rooms, view_available_rooms, add_room,
                         set_room_maintenance, get_room_by_number)
from bookings   import (add_guest, search_guest, view_all_guests,
                         create_booking, check_in_booking, check_out_booking,
                         cancel_booking, view_bookings, get_booking)
from restaurant import (view_menu, add_menu_item, toggle_menu_item,
                         place_order, view_orders, view_order_details,
                         update_order_status)
from billing    import (generate_bill, process_payment, view_all_bills,
                         revenue_report, get_bill)

# ═══════════════════════════════════════════════════════════
# ROOM MANAGEMENT
# ═══════════════════════════════════════════════════════════

def menu_rooms():
    while True:
        U.header("ROOM MANAGEMENT")
        print("""
  1. View All Rooms
  2. View Available Rooms (by Date)
  3. Add New Room
  4. Set Room to Maintenance
  0. Back
""")
        ch = U.prompt("Choice")
        if ch == "1":
            U.subheader("ALL ROOMS")
            rows = view_all_rooms()
            U.table(
                ["ID","Room No","Type","Price/Night","Status"],
                [(r["room_id"],r["room_number"],r["room_type"],
                  f"₹{r['price_per_night']:.0f}",r["status"]) for r in rows],
                [4,9,8,13,12]
            )
            U.pause()

        elif ch == "2":
            ci = U.get_date("Check-in Date")
            co = U.get_date("Check-out Date")
            rows = view_available_rooms(ci, co)
            U.subheader(f"AVAILABLE ROOMS ({ci} → {co})")
            U.table(
                ["ID","Room No","Type","Price/Night"],
                [(r["room_id"],r["room_number"],r["room_type"],
                  f"₹{r['price_per_night']:.0f}") for r in rows],
                [4,9,10,12]
            )
            U.pause()

        elif ch == "3":
            room_no = U.prompt("Room Number (e.g. 501)")
            rtype   = U.choose("Room Type", ["Single","Double","Deluxe","Suite"])
            price   = U.get_float("Price per Night (₹)")
            ok, msg = add_room(room_no, rtype.capitalize(), price)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "4":
            room_no = U.prompt("Room Number")
            ok, msg = set_room_maintenance(room_no)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "0":
            break

# ═══════════════════════════════════════════════════════════
# GUEST MANAGEMENT
# ═══════════════════════════════════════════════════════════

def menu_guests():
    while True:
        U.header("GUEST MANAGEMENT")
        print("""
  1. Register New Guest
  2. Search Guest by Phone
  3. View All Guests
  0. Back
""")
        ch = U.prompt("Choice")
        if ch == "1":
            name     = U.prompt("Full Name")
            phone    = U.prompt("Phone Number")
            email    = U.prompt("Email (optional)")
            id_proof = U.prompt("ID Proof (Aadhar/PAN/Passport No.)")
            ok, result = add_guest(name, phone, email, id_proof)
            if ok:
                U.success(f"Guest registered. ID: {result}")
            else:
                U.error(result)
            U.pause()

        elif ch == "2":
            phone = U.prompt("Phone Number")
            rows  = search_guest(phone)
            U.subheader("SEARCH RESULTS")
            U.table(
                ["ID","Name","Phone","Email","ID Proof"],
                [(r["guest_id"],r["name"],r["phone"],r["email"] or "-",r["id_proof"]) for r in rows],
                [4,20,13,22,15]
            )
            U.pause()

        elif ch == "3":
            U.subheader("ALL GUESTS")
            rows = view_all_guests()
            U.table(
                ["ID","Name","Phone","Email"],
                [(r["guest_id"],r["name"],r["phone"],r["email"] or "-") for r in rows],
                [4,22,13,25]
            )
            U.pause()

        elif ch == "0":
            break

# ═══════════════════════════════════════════════════════════
# BOOKING MANAGEMENT
# ═══════════════════════════════════════════════════════════

def menu_bookings():
    while True:
        U.header("BOOKING MANAGEMENT")
        print("""
  1. New Booking (Advance / Walk-in)
  2. Check In
  3. Check Out
  4. Cancel Booking
  5. View All Bookings
  6. View Booking Details
  0. Back
""")
        ch = U.prompt("Choice")

        if ch == "1":
            ci = U.get_date("Check-in Date")
            co = U.get_date("Check-out Date")
            avail = view_available_rooms(ci, co)
            if not avail:
                U.error("No rooms available for those dates.")
                U.pause(); continue
            U.subheader("AVAILABLE ROOMS")
            U.table(
                ["ID","Room","Type","Price/Night"],
                [(r["room_id"],r["room_number"],r["room_type"],
                  f"₹{r['price_per_night']:.0f}") for r in avail],
                [4,7,8,12]
            )
            room_id = U.get_int("Select Room ID")

            # Guest
            phone = U.prompt("Guest Phone (to search existing)")
            matches = search_guest(phone)
            if matches:
                U.subheader("EXISTING GUESTS")
                U.table(
                    ["ID","Name","Phone"],
                    [(r["guest_id"],r["name"],r["phone"]) for r in matches],
                    [4,22,13]
                )
                ans = U.choose("Use existing guest?", ["Y","N"])
                if ans == "Y":
                    guest_id = U.get_int("Guest ID")
                else:
                    guest_id = _register_guest_inline(phone)
            else:
                U.info("No existing guest. Register new guest.")
                guest_id = _register_guest_inline(phone)

            if guest_id is None: U.pause(); continue

            ok, result = create_booking(guest_id, room_id, ci, co)
            if ok:
                U.success(f"Booking confirmed! Booking ID: {result}")
                _show_booking_summary(result)
            else:
                U.error(result)
            U.pause()

        elif ch == "2":
            bid = U.get_int("Booking ID")
            ok, msg = check_in_booking(bid)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "3":
            bid = U.get_int("Booking ID")
            ok, msg = check_out_booking(bid)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "4":
            bid = U.get_int("Booking ID")
            ok, msg = cancel_booking(bid)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "5":
            U.header("ALL BOOKINGS")
            print("  Filter: 1=Reserved  2=Checked-In  3=Checked-Out  4=All")
            flt = U.prompt("Choice", "4")
            status_map = {"1":"Reserved","2":"Checked-In","3":"Checked-Out","4":None}
            rows = view_bookings(status_map.get(flt))
            U.table(
                ["BID","Guest","Phone","Room","Type","Check-In","Check-Out","Status","Amount"],
                [(r["booking_id"],r["name"][:16],r["phone"],r["room_number"],
                  r["room_type"],r["check_in_date"],r["check_out_date"],
                  r["status"],f"₹{r['total_amount']:.0f}") for r in rows],
                [4,17,12,6,8,11,11,11,9]
            )
            U.pause()

        elif ch == "6":
            bid = U.get_int("Booking ID")
            _show_booking_summary(bid)
            U.pause()

        elif ch == "0":
            break

def _register_guest_inline(phone):
    name     = U.prompt("Guest Name")
    email    = U.prompt("Email (optional)")
    id_proof = U.prompt("ID Proof No.")
    ok, result = add_guest(name, phone, email, id_proof)
    if ok:
        U.success(f"Guest registered. ID: {result}")
        return result
    else:
        U.error(result)
        return None

def _show_booking_summary(booking_id):
    b = get_booking(booking_id)
    if not b: return
    U.subheader("BOOKING SUMMARY")
    print(f"  Booking ID   : {b['booking_id']}")
    print(f"  Guest        : {b['guest_name']} | {b['phone']}")
    print(f"  Room         : {b['room_number']} ({b['room_type']})")
    print(f"  Check-in     : {b['check_in_date']}")
    print(f"  Check-out    : {b['check_out_date']}")
    print(f"  Status       : {b['status']}")
    print(f"  Room Amount  : ₹{b['total_amount']:.2f}")

# ═══════════════════════════════════════════════════════════
# RESTAURANT
# ═══════════════════════════════════════════════════════════

def menu_restaurant():
    while True:
        U.header("RESTAURANT MANAGEMENT")
        print("""
  1. View Menu
  2. Place Order
  3. View Orders
  4. View Order Details
  5. Update Order Status
  6. Add Menu Item
  7. Enable / Disable Menu Item
  0. Back
""")
        ch = U.prompt("Choice")

        if ch == "1":
            _show_full_menu()
            U.pause()

        elif ch == "2":
            room_no  = U.prompt("Room Number (or walk-in 'W')")
            booking_id = None
            if room_no.upper() != "W":
                bid_str = U.prompt("Booking ID (or Enter to skip)")
                if bid_str.isdigit():
                    booking_id = int(bid_str)

            _show_full_menu()
            items = []
            print("\n  Add items (Enter 0 as item ID to finish)")
            while True:
                iid = U.get_int("  Item ID", min_val=0)
                if iid == 0: break
                qty = U.get_int("  Quantity", min_val=1)
                items.append((iid, qty))
            if not items:
                U.error("No items selected."); U.pause(); continue

            ok, result = place_order(booking_id, room_no, items)
            if ok:
                U.success(f"Order placed. Order ID: {result}")
            else:
                U.error(result)
            U.pause()

        elif ch == "3":
            bid_str = U.prompt("Filter by Booking ID (or Enter for all)")
            bid = int(bid_str) if bid_str.isdigit() else None
            rows = view_orders(booking_id=bid)
            U.subheader("ORDERS")
            U.table(
                ["Order ID","Room","Date","Amount","Status"],
                [(r["order_id"],r["room_number"],r["order_date"][:16],
                  f"₹{r['total_amount']:.2f}",r["status"]) for r in rows],
                [9,7,17,10,10]
            )
            U.pause()

        elif ch == "4":
            oid  = U.get_int("Order ID")
            order, items = view_order_details(oid)
            if not order:
                U.error("Order not found."); U.pause(); continue
            U.subheader(f"ORDER #{oid}  |  Room: {order['room_number']}  |  {order['status']}")
            U.table(
                ["Item","Category","Qty","Unit","Subtotal"],
                [(i["item_name"],i["category"],i["quantity"],
                  f"₹{i['unit_price']:.2f}",f"₹{i['subtotal']:.2f}") for i in items],
                [22,11,4,8,10]
            )
            print(f"\n  Total: ₹{order['total_amount']:.2f}")
            U.pause()

        elif ch == "5":
            oid    = U.get_int("Order ID")
            status = U.choose("New Status", ["Pending","Served","Billed"])
            ok = update_order_status(oid, status.capitalize())
            (U.success if ok else U.error)("Updated." if ok else "Order not found.")
            U.pause()

        elif ch == "6":
            name = U.prompt("Item Name")
            cat  = U.choose("Category", ["Breakfast","Lunch","Dinner","Beverages","Snacks"])
            price = U.get_float("Price (₹)")
            ok, msg = add_menu_item(name, cat.capitalize(), price)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "7":
            _show_full_menu(show_all=True)
            iid = U.get_int("Item ID to toggle")
            ok, msg = toggle_menu_item(iid)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "0":
            break

def _show_full_menu(show_all=False):
    from restaurant import view_menu
    from database import get_connection
    if show_all:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM menu_items ORDER BY category, item_name").fetchall()
        conn.close()
    else:
        rows = view_menu()
    categories = {}
    for r in rows:
        categories.setdefault(r["category"], []).append(r)
    print()
    for cat, items in categories.items():
        print(f"  ── {cat} ──")
        for i in items:
            avail = "" if i["available"] else "  [UNAVAILABLE]"
            print(f"    [{i['item_id']:>3}]  {i['item_name']:<25}  ₹{i['price']:.0f}{avail}")
    print()

# ═══════════════════════════════════════════════════════════
# BILLING
# ═══════════════════════════════════════════════════════════

def menu_billing():
    while True:
        U.header("BILLING & PAYMENTS")
        print("""
  1. Generate Bill
  2. Process Payment
  3. View All Bills
  4. Revenue Report
  0. Back
""")
        ch = U.prompt("Choice")

        if ch == "1":
            bid = U.get_int("Booking ID")
            ok, msg, data = generate_bill(bid)
            if ok:
                U.print_bill(data)
            else:
                U.error(msg)
                bill = get_bill(bid)
                if bill:
                    U.info(f"Existing bill total: ₹{bill['total_amount']:.2f}  Status: {bill['payment_status']}")
            U.pause()

        elif ch == "2":
            bid = U.get_int("Booking ID")
            ok, msg, data = generate_bill(bid)
            if ok:
                U.print_bill(data)
            bill = get_bill(bid)
            if bill and bill["payment_status"] == "Paid":
                U.info("Bill already paid.")
                U.pause(); continue
            method = U.choose("Payment Method", ["Cash","Card","UPI"])
            ok, msg = process_payment(bid, method)
            (U.success if ok else U.error)(msg)
            U.pause()

        elif ch == "3":
            U.subheader("ALL BILLS")
            rows = view_all_bills()
            U.table(
                ["ID","Guest","Room","Room(₹)","Rest(₹)","Tax(₹)","Total(₹)","Status","Method"],
                [(r["bill_id"],r["name"][:14],r["room_number"],
                  f"{r['room_charges']:.0f}",f"{r['restaurant_charges']:.0f}",
                  f"{r['tax_amount']:.0f}",f"{r['total_amount']:.0f}",
                  r["payment_status"],r["payment_method"] or "-") for r in rows],
                [4,15,6,8,8,7,9,9,7]
            )
            U.pause()

        elif ch == "4":
            row = revenue_report()
            U.subheader("REVENUE REPORT (Paid Bills)")
            print(f"  Total Bills        : {row['total_bills']}")
            print(f"  Room Revenue       : ₹{row['total_room_revenue']:.2f}")
            print(f"  Restaurant Revenue : ₹{row['total_rest_revenue']:.2f}")
            print(f"  GST Collected      : ₹{row['total_tax']:.2f}")
            print(f"  ─────────────────────────────")
            print(f"  Grand Total        : ₹{row['grand_total']:.2f}")
            U.pause()

        elif ch == "0":
            break

# ═══════════════════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════════════════

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    initialize_database()

    while True:
        U.header("MAIN MENU")
        print("""
  1. Room Management
  2. Guest Management
  3. Booking Management
  4. Restaurant
  5. Billing & Payments
  0. Exit
""")
        ch = U.prompt("Choice")

        if   ch == "1": menu_rooms()
        elif ch == "2": menu_guests()
        elif ch == "3": menu_bookings()
        elif ch == "4": menu_restaurant()
        elif ch == "5": menu_billing()
        elif ch == "0":
            print("\n  Thank you for using Grand Palace Hotel System. Goodbye!\n")
            sys.exit(0)

if __name__ == "__main__":
    main()
