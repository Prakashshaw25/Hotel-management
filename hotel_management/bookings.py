from database import get_connection
from datetime import date, datetime

# ─────────────────────────────────────────────
# GUEST PROCEDURES
# ─────────────────────────────────────────────

def add_guest(name, phone, email, id_proof):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO guests (name, phone, email, id_proof) VALUES (?,?,?,?)",
            (name, phone, email, id_proof)
        )
        conn.commit()
        return True, cur.lastrowid
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def search_guest(phone):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM guests WHERE phone=?", (phone,)
    ).fetchall()
    conn.close()
    return rows

def get_guest(guest_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM guests WHERE guest_id=?", (guest_id,)).fetchone()
    conn.close()
    return row

def view_all_guests():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM guests ORDER BY name").fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────
# BOOKING PROCEDURES
# ─────────────────────────────────────────────

def _nights(check_in_str, check_out_str):
    fmt = "%Y-%m-%d"
    ci = datetime.strptime(check_in_str, fmt).date()
    co = datetime.strptime(check_out_str, fmt).date()
    return max((co - ci).days, 1)

def create_booking(guest_id, room_id, check_in, check_out):
    conn = get_connection()
    try:
        # Validate dates
        ci = datetime.strptime(check_in, "%Y-%m-%d").date()
        co = datetime.strptime(check_out, "%Y-%m-%d").date()
        if co <= ci:
            return False, "Check-out must be after check-in."

        # Check room availability
        conflict = conn.execute("""
            SELECT booking_id FROM bookings
            WHERE room_id=? AND status IN ('Reserved','Checked-In')
              AND check_in_date < ? AND check_out_date > ?
        """, (room_id, check_out, check_in)).fetchone()
        if conflict:
            return False, "Room is already booked for those dates."

        # Get price
        room = conn.execute("SELECT price_per_night FROM rooms WHERE room_id=?", (room_id,)).fetchone()
        if not room:
            return False, "Room not found."

        nights = _nights(check_in, check_out)
        total = room["price_per_night"] * nights

        cur = conn.execute("""
            INSERT INTO bookings (guest_id, room_id, check_in_date, check_out_date, total_amount)
            VALUES (?,?,?,?,?)
        """, (guest_id, room_id, check_in, check_out, total))
        conn.commit()
        return True, cur.lastrowid
    except ValueError as e:
        return False, f"Date format error: {e}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def check_in_booking(booking_id):
    conn = get_connection()
    try:
        booking = conn.execute(
            "SELECT * FROM bookings WHERE booking_id=?", (booking_id,)
        ).fetchone()
        if not booking:
            return False, "Booking not found."
        if booking["status"] != "Reserved":
            return False, f"Cannot check-in. Current status: {booking['status']}"

        conn.execute(
            "UPDATE bookings SET status='Checked-In' WHERE booking_id=?", (booking_id,)
        )
        conn.execute(
            "UPDATE rooms SET status='Occupied' WHERE room_id=?", (booking["room_id"],)
        )
        conn.commit()
        return True, "Guest checked in successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def check_out_booking(booking_id):
    conn = get_connection()
    try:
        booking = conn.execute(
            "SELECT * FROM bookings WHERE booking_id=?", (booking_id,)
        ).fetchone()
        if not booking:
            return False, "Booking not found."
        if booking["status"] != "Checked-In":
            return False, f"Cannot check-out. Current status: {booking['status']}"

        # Check bill is paid
        bill = conn.execute(
            "SELECT payment_status FROM bills WHERE booking_id=?", (booking_id,)
        ).fetchone()
        if bill and bill["payment_status"] != "Paid":
            return False, "Please settle the bill before checking out."

        conn.execute(
            "UPDATE bookings SET status='Checked-Out' WHERE booking_id=?", (booking_id,)
        )
        conn.execute(
            "UPDATE rooms SET status='Available' WHERE room_id=?", (booking["room_id"],)
        )
        conn.commit()
        return True, "Guest checked out successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def cancel_booking(booking_id):
    conn = get_connection()
    booking = conn.execute(
        "SELECT * FROM bookings WHERE booking_id=?", (booking_id,)
    ).fetchone()
    if not booking:
        conn.close()
        return False, "Booking not found."
    if booking["status"] in ("Checked-Out", "Cancelled"):
        conn.close()
        return False, f"Cannot cancel. Status is already {booking['status']}."

    conn.execute(
        "UPDATE bookings SET status='Cancelled' WHERE booking_id=?", (booking_id,)
    )
    if booking["status"] == "Checked-In":
        conn.execute(
            "UPDATE rooms SET status='Available' WHERE room_id=?", (booking["room_id"],)
        )
    conn.commit()
    conn.close()
    return True, "Booking cancelled."

def view_bookings(status_filter=None):
    conn = get_connection()
    if status_filter:
        rows = conn.execute("""
            SELECT b.booking_id, g.name, g.phone, r.room_number, r.room_type,
                   b.check_in_date, b.check_out_date, b.booking_date,
                   b.status, b.total_amount
            FROM bookings b
            JOIN guests g ON b.guest_id=g.guest_id
            JOIN rooms   r ON b.room_id=r.room_id
            WHERE b.status=?
            ORDER BY b.booking_id DESC
        """, (status_filter,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT b.booking_id, g.name, g.phone, r.room_number, r.room_type,
                   b.check_in_date, b.check_out_date, b.booking_date,
                   b.status, b.total_amount
            FROM bookings b
            JOIN guests g ON b.guest_id=g.guest_id
            JOIN rooms   r ON b.room_id=r.room_id
            ORDER BY b.booking_id DESC
        """).fetchall()
    conn.close()
    return rows

def get_booking(booking_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT b.*, g.name as guest_name, g.phone, r.room_number, r.room_type,
               r.price_per_night
        FROM bookings b
        JOIN guests g ON b.guest_id=g.guest_id
        JOIN rooms   r ON b.room_id=r.room_id
        WHERE b.booking_id=?
    """, (booking_id,)).fetchone()
    conn.close()
    return row
