import streamlit as st  # type: ignore
import sqlite3
from datetime import datetime

# Database functions
def connect_db():
    conn = sqlite3.connect('hotel.db')
    return conn

def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    # Guests table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    # Rooms table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            room_type TEXT,
            price REAL
        )
    ''')
    # Bookings table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER,
            room_id INTEGER,
            check_in DATE,
            check_out DATE,
            FOREIGN KEY (guest_id) REFERENCES guests(id),
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_guest(name, phone, email):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO guests (name, phone, email) VALUES (?, ?, ?)', (name, phone, email))
    conn.commit()
    conn.close()

def get_guests():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM guests')
    guests = cur.fetchall()
    conn.close()
    return guests

def add_room(room_number, room_type, price):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO rooms (room_number, room_type, price) VALUES (?, ?, ?)', (room_number, room_type, price))
    conn.commit()
    conn.close()

def get_rooms():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM rooms')
    rooms = cur.fetchall()
    conn.close()
    return rooms

def add_booking(guest_id, room_id, check_in, check_out):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO bookings (guest_id, room_id, check_in, check_out) VALUES (?, ?, ?, ?)', (guest_id, room_id, check_in, check_out))
    conn.commit()
    conn.close()

def get_bookings():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT bookings.id, guests.name, rooms.room_number, rooms.room_type, bookings.check_in, bookings.check_out
        FROM bookings
        JOIN guests ON bookings.guest_id = guests.id
        JOIN rooms ON bookings.room_id = rooms.id
    ''')
    bookings = cur.fetchall()
    conn.close()
    return bookings

# Initialize database and tables
create_tables()

# Streamlit UI
st.title("Hotel Management System")

menu = ["Add Guest", "View Guests", "Add Room", "View Rooms", "Add Booking", "View Bookings"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Guest":
    st.header("Add Guest")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    if st.button("Add Guest"):
        if name.strip() == "":
            st.error("Name is required")
        else:
            add_guest(name, phone, email)
            st.success(f"Guest {name} added successfully")

elif choice == "View Guests":
    st.header("Guests List")
    guests = get_guests()
    if guests:
        for guest in guests:
            st.write(f"ID: {guest[0]}, Name: {guest[1]}, Phone: {guest[2]}, Email: {guest[3]}")
    else:
        st.info("No guests found")

elif choice == "Add Room":
    st.header("Add Room")
    room_number = st.text_input("Room Number")
    room_type = st.selectbox("Room Type", ["Single", "Double", "Suite"])
    price = st.number_input("Price per night", min_value=0.0, format="%.2f")
    if st.button("Add Room"):
        if room_number.strip() == "":
            st.error("Room number is required")
        else:
            add_room(room_number, room_type, price)
            st.success(f"Room {room_number} added successfully")

elif choice == "View Rooms":
    st.header("Rooms List")
    rooms = get_rooms()
    if rooms:
        for room in rooms:
            st.write(f"ID: {room[0]}, Room Number: {room[1]}, Type: {room[2]}, Price: ${room[3]:.2f}")
    else:
        st.info("No rooms found")

elif choice == "Add Booking":
    st.header("Add Booking")
    guests = get_guests()
    rooms = get_rooms()
    if not guests:
        st.warning("No guests available. Please add guests first.")
    elif not rooms:
        st.warning("No rooms available. Please add rooms first.")
    else:
        guest_options = {f"{guest[1]} (ID: {guest[0]})": guest[0] for guest in guests}
        room_options = {f"{room[1]} - {room[2]} (ID: {room[0]})": room[0] for room in rooms}
        guest_selected = st.selectbox("Select Guest", list(guest_options.keys()))
        room_selected = st.selectbox("Select Room", list(room_options.keys()))
        check_in = st.date_input("Check-in Date")
        check_out = st.date_input("Check-out Date")
        if st.button("Add Booking"):
            if check_out <= check_in:
                st.error("Check-out date must be after check-in date")
            else:
                add_booking(guest_options[guest_selected], room_options[room_selected], check_in.strftime("%Y-%m-%d"), check_out.strftime("%Y-%m-%d"))
                st.success("Booking added successfully")

elif choice == "View Bookings":
    st.header("Bookings List")
    bookings = get_bookings()
    if bookings:
        for booking in bookings:
            st.write(f"Booking ID: {booking[0]}, Guest: {booking[1]}, Room: {booking[2]} ({booking[3]}), Check-in: {booking[4]}, Check-out: {booking[5]}")
    else:
        st.info("No bookings found")
