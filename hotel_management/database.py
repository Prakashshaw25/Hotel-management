import sqlite3
import os

DB_NAME = "hotel.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    # Rooms table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT    NOT NULL UNIQUE,
            room_type   TEXT    NOT NULL CHECK(room_type IN ('Single','Double','Suite','Deluxe')),
            price_per_night REAL NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Available'
                            CHECK(status IN ('Available','Occupied','Maintenance'))
        )
    """)

    # Guests table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            guest_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL,
            email       TEXT,
            id_proof    TEXT    NOT NULL
        )
    """)

    # Bookings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id        INTEGER NOT NULL REFERENCES guests(guest_id),
            room_id         INTEGER NOT NULL REFERENCES rooms(room_id),
            check_in_date   TEXT    NOT NULL,
            check_out_date  TEXT    NOT NULL,
            booking_date    TEXT    NOT NULL DEFAULT (date('now')),
            status          TEXT    NOT NULL DEFAULT 'Reserved'
                                    CHECK(status IN ('Reserved','Checked-In','Checked-Out','Cancelled')),
            total_amount    REAL    DEFAULT 0
        )
    """)

    # Restaurant orders table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name   TEXT    NOT NULL,
            category    TEXT    NOT NULL CHECK(category IN ('Breakfast','Lunch','Dinner','Beverages','Snacks')),
            price       REAL    NOT NULL,
            available   INTEGER NOT NULL DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_orders (
            order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id  INTEGER REFERENCES bookings(booking_id),
            room_number TEXT,
            order_date  TEXT    NOT NULL DEFAULT (datetime('now')),
            total_amount REAL   NOT NULL DEFAULT 0,
            status      TEXT    NOT NULL DEFAULT 'Pending'
                                CHECK(status IN ('Pending','Served','Billed'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    INTEGER NOT NULL REFERENCES restaurant_orders(order_id),
            item_id     INTEGER NOT NULL REFERENCES menu_items(item_id),
            quantity    INTEGER NOT NULL DEFAULT 1,
            unit_price  REAL    NOT NULL
        )
    """)

    # Billing table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id      INTEGER NOT NULL REFERENCES bookings(booking_id),
            room_charges    REAL    NOT NULL DEFAULT 0,
            restaurant_charges REAL NOT NULL DEFAULT 0,
            tax_amount      REAL    NOT NULL DEFAULT 0,
            total_amount    REAL    NOT NULL DEFAULT 0,
            payment_status  TEXT    NOT NULL DEFAULT 'Pending'
                                    CHECK(payment_status IN ('Pending','Paid')),
            payment_method  TEXT,
            bill_date       TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()

    # Seed rooms if empty
    cur.execute("SELECT COUNT(*) FROM rooms")
    if cur.fetchone()[0] == 0:
        _seed_rooms(cur)
        conn.commit()

    # Seed menu items if empty
    cur.execute("SELECT COUNT(*) FROM menu_items")
    if cur.fetchone()[0] == 0:
        _seed_menu(cur)
        conn.commit()

    conn.close()
    print("Database initialized successfully.")

def _seed_rooms(cur):
    rooms = [
        ("101","Single",1500),("102","Single",1500),("103","Single",1500),
        ("201","Double",2500),("202","Double",2500),("203","Double",2500),
        ("301","Deluxe",4000),("302","Deluxe",4000),
        ("401","Suite",7000),("402","Suite",7000),
    ]
    cur.executemany(
        "INSERT INTO rooms (room_number,room_type,price_per_night) VALUES (?,?,?)", rooms
    )

def _seed_menu(cur):
    items = [
        ("Masala Dosa","Breakfast",120),("Idli Sambhar","Breakfast",80),
        ("Poha","Breakfast",70),("Aloo Paratha","Breakfast",100),
        ("Veg Thali","Lunch",200),("Chicken Biryani","Lunch",280),
        ("Dal Rice","Lunch",150),("Paneer Butter Masala","Dinner",220),
        ("Butter Naan","Dinner",40),("Grilled Fish","Dinner",320),
        ("Mutton Curry","Dinner",350),("Tea","Beverages",30),
        ("Coffee","Beverages",50),("Fresh Juice","Beverages",80),
        ("Lassi","Beverages",60),("Samosa","Snacks",30),
        ("Spring Rolls","Snacks",120),("French Fries","Snacks",100),
    ]
    cur.executemany(
        "INSERT INTO menu_items (item_name,category,price) VALUES (?,?,?)", items
    )
