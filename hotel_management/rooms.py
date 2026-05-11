from database import get_connection

# ─────────────────────────────────────────────
# ROOM PROCEDURES
# ─────────────────────────────────────────────

def view_all_rooms():
    conn = get_connection()
    rows = conn.execute(
        "SELECT room_id, room_number, room_type, price_per_night, status FROM rooms ORDER BY room_number"
    ).fetchall()
    conn.close()
    return rows

def view_available_rooms(check_in, check_out):
    """Return rooms not booked in the given date range (active bookings only)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.room_id, r.room_number, r.room_type, r.price_per_night
        FROM rooms r
        WHERE r.status = 'Available'
          AND r.room_id NOT IN (
              SELECT b.room_id FROM bookings b
              WHERE b.status IN ('Reserved','Checked-In')
                AND b.check_in_date  < ?
                AND b.check_out_date > ?
          )
        ORDER BY r.room_type, r.room_number
    """, (check_out, check_in)).fetchall()
    conn.close()
    return rows

def add_room(room_number, room_type, price):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO rooms (room_number, room_type, price_per_night) VALUES (?,?,?)",
            (room_number, room_type, price)
        )
        conn.commit()
        return True, f"Room {room_number} added successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_room_status(room_number, status):
    conn = get_connection()
    cur = conn.execute(
        "UPDATE rooms SET status=? WHERE room_number=?", (status, room_number)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0

def set_room_maintenance(room_number):
    conn = get_connection()
    row = conn.execute(
        "SELECT status FROM rooms WHERE room_number=?", (room_number,)
    ).fetchone()
    if not row:
        conn.close()
        return False, "Room not found."
    if row["status"] == "Occupied":
        conn.close()
        return False, "Cannot set Occupied room to Maintenance."
    conn.execute(
        "UPDATE rooms SET status='Maintenance' WHERE room_number=?", (room_number,)
    )
    conn.commit()
    conn.close()
    return True, f"Room {room_number} set to Maintenance."

def get_room_by_number(room_number):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM rooms WHERE room_number=?", (room_number,)
    ).fetchone()
    conn.close()
    return row
