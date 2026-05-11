from database import get_connection
from restaurant import get_total_restaurant_charges

TAX_RATE = 0.12   # 12% GST

# ─────────────────────────────────────────────
# BILLING PROCEDURES
# ─────────────────────────────────────────────

def generate_bill(booking_id):
    conn = get_connection()
    try:
        booking = conn.execute("""
            SELECT b.*, r.price_per_night, r.room_number, r.room_type,
                   g.name as guest_name, g.phone
            FROM bookings b
            JOIN rooms   r ON b.room_id=r.room_id
            JOIN guests  g ON b.guest_id=g.guest_id
            WHERE b.booking_id=?
        """, (booking_id,)).fetchone()

        if not booking:
            return False, "Booking not found.", None

        # Check if bill already exists
        existing = conn.execute(
            "SELECT * FROM bills WHERE booking_id=?", (booking_id,)
        ).fetchone()
        if existing and existing["payment_status"] == "Paid":
            return False, "Bill already paid.", None

        from datetime import datetime
        ci = datetime.strptime(booking["check_in_date"], "%Y-%m-%d").date()
        co = datetime.strptime(booking["check_out_date"], "%Y-%m-%d").date()
        nights = max((co - ci).days, 1)

        room_charges     = booking["price_per_night"] * nights
        rest_charges     = get_total_restaurant_charges(booking_id)
        subtotal         = room_charges + rest_charges
        tax_amount       = round(subtotal * TAX_RATE, 2)
        total            = round(subtotal + tax_amount, 2)

        if existing:
            conn.execute("""
                UPDATE bills
                SET room_charges=?, restaurant_charges=?, tax_amount=?, total_amount=?
                WHERE booking_id=?
            """, (room_charges, rest_charges, tax_amount, total, booking_id))
        else:
            conn.execute("""
                INSERT INTO bills (booking_id, room_charges, restaurant_charges, tax_amount, total_amount)
                VALUES (?,?,?,?,?)
            """, (booking_id, room_charges, rest_charges, tax_amount, total))

        conn.commit()

        bill_data = {
            "booking_id":      booking_id,
            "guest_name":      booking["guest_name"],
            "phone":           booking["phone"],
            "room_number":     booking["room_number"],
            "room_type":       booking["room_type"],
            "check_in":        booking["check_in_date"],
            "check_out":       booking["check_out_date"],
            "nights":          nights,
            "price_per_night": booking["price_per_night"],
            "room_charges":    room_charges,
            "rest_charges":    rest_charges,
            "tax_amount":      tax_amount,
            "total":           total,
        }
        return True, "Bill generated.", bill_data

    except Exception as e:
        return False, str(e), None
    finally:
        conn.close()

def process_payment(booking_id, payment_method):
    conn = get_connection()
    try:
        bill = conn.execute(
            "SELECT * FROM bills WHERE booking_id=?", (booking_id,)
        ).fetchone()
        if not bill:
            return False, "No bill found. Please generate bill first."
        if bill["payment_status"] == "Paid":
            return False, "Bill already paid."

        conn.execute("""
            UPDATE bills
            SET payment_status='Paid', payment_method=?, bill_date=datetime('now')
            WHERE booking_id=?
        """, (payment_method, booking_id))
        conn.commit()
        return True, f"Payment of ₹{bill['total_amount']:.2f} received via {payment_method}."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_bill(booking_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM bills WHERE booking_id=?", (booking_id,)).fetchone()
    conn.close()
    return row

def view_all_bills():
    conn = get_connection()
    rows = conn.execute("""
        SELECT bi.bill_id, g.name, r.room_number,
               bi.room_charges, bi.restaurant_charges,
               bi.tax_amount, bi.total_amount,
               bi.payment_status, bi.payment_method, bi.bill_date
        FROM bills bi
        JOIN bookings b ON bi.booking_id=b.booking_id
        JOIN guests   g ON b.guest_id=g.guest_id
        JOIN rooms    r ON b.room_id=r.room_id
        ORDER BY bi.bill_id DESC
    """).fetchall()
    conn.close()
    return rows

def revenue_report():
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COUNT(*)                          AS total_bills,
            COALESCE(SUM(room_charges),0)     AS total_room_revenue,
            COALESCE(SUM(restaurant_charges),0) AS total_rest_revenue,
            COALESCE(SUM(tax_amount),0)       AS total_tax,
            COALESCE(SUM(total_amount),0)     AS grand_total
        FROM bills WHERE payment_status='Paid'
    """).fetchone()
    conn.close()
    return row
