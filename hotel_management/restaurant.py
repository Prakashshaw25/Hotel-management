from database import get_connection

# ─────────────────────────────────────────────
# MENU PROCEDURES
# ─────────────────────────────────────────────

def view_menu(category=None):
    conn = get_connection()
    if category:
        rows = conn.execute(
            "SELECT * FROM menu_items WHERE category=? AND available=1 ORDER BY item_name",
            (category,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM menu_items WHERE available=1 ORDER BY category, item_name"
        ).fetchall()
    conn.close()
    return rows

def add_menu_item(name, category, price):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO menu_items (item_name, category, price) VALUES (?,?,?)",
            (name, category, price)
        )
        conn.commit()
        return True, f"'{name}' added to menu."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def toggle_menu_item(item_id):
    conn = get_connection()
    row = conn.execute("SELECT available FROM menu_items WHERE item_id=?", (item_id,)).fetchone()
    if not row:
        conn.close()
        return False, "Item not found."
    new_val = 0 if row["available"] else 1
    conn.execute("UPDATE menu_items SET available=? WHERE item_id=?", (new_val, item_id))
    conn.commit()
    conn.close()
    status = "enabled" if new_val else "disabled"
    return True, f"Item {status}."

# ─────────────────────────────────────────────
# ORDER PROCEDURES
# ─────────────────────────────────────────────

def place_order(booking_id, room_number, items):
    """
    items: list of (item_id, quantity)
    """
    conn = get_connection()
    try:
        # Create order record
        cur = conn.execute(
            "INSERT INTO restaurant_orders (booking_id, room_number) VALUES (?,?)",
            (booking_id, room_number)
        )
        order_id = cur.lastrowid

        total = 0.0
        for item_id, qty in items:
            item = conn.execute(
                "SELECT price FROM menu_items WHERE item_id=? AND available=1", (item_id,)
            ).fetchone()
            if not item:
                conn.rollback()
                conn.close()
                return False, f"Item ID {item_id} not available."
            unit_price = item["price"]
            conn.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, unit_price) VALUES (?,?,?,?)",
                (order_id, item_id, qty, unit_price)
            )
            total += unit_price * qty

        conn.execute(
            "UPDATE restaurant_orders SET total_amount=? WHERE order_id=?", (total, order_id)
        )
        conn.commit()
        return True, order_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def view_orders(booking_id=None, status=None):
    conn = get_connection()
    q = """
        SELECT o.order_id, o.room_number, o.order_date, o.total_amount, o.status
        FROM restaurant_orders o WHERE 1=1
    """
    params = []
    if booking_id:
        q += " AND o.booking_id=?"
        params.append(booking_id)
    if status:
        q += " AND o.status=?"
        params.append(status)
    q += " ORDER BY o.order_id DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return rows

def view_order_details(order_id):
    conn = get_connection()
    order = conn.execute(
        "SELECT * FROM restaurant_orders WHERE order_id=?", (order_id,)
    ).fetchone()
    items = conn.execute("""
        SELECT m.item_name, m.category, oi.quantity, oi.unit_price,
               (oi.quantity * oi.unit_price) AS subtotal
        FROM order_items oi
        JOIN menu_items m ON oi.item_id = m.item_id
        WHERE oi.order_id=?
    """, (order_id,)).fetchall()
    conn.close()
    return order, items

def update_order_status(order_id, status):
    conn = get_connection()
    cur = conn.execute(
        "UPDATE restaurant_orders SET status=? WHERE order_id=?", (status, order_id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0

def get_total_restaurant_charges(booking_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT COALESCE(SUM(total_amount),0) AS total
        FROM restaurant_orders
        WHERE booking_id=? AND status != 'Pending'
    """, (booking_id,)).fetchone()
    conn.close()
    return row["total"] if row else 0
