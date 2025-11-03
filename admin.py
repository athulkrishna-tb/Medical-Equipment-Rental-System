from Db_connection import get_connection
import os
import platform
import subprocess
from getpass import getpass
import sys
import msvcrt

def input_password(prompt="Enter password: "):
    """
    Windows-friendly password input with * masking.
    Works in Command Prompt.
    """
    print(prompt, end="", flush=True)
    pwd = ""
    while True:
        ch = msvcrt.getch()
        if ch in {b'\r', b'\n'}:  
            print("")  
            break
        elif ch == b'\x08':  
            if len(pwd) > 0:
                pwd = pwd[:-1]
                sys.stdout.write("\b \b")  
                sys.stdout.flush()
        elif ch == b'\x03':  
            raise KeyboardInterrupt
        else:
            try:
                char = ch.decode("utf-8", errors="ignore")
            except:
                char = ''
            pwd += char
            sys.stdout.write("*")
            sys.stdout.flush()
    return pwd




# ---------------- Helper function to open images ----------------
def open_image(file_path):
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)   
        elif platform.system() == "Darwin":  
            subprocess.run(["open", file_path])
        else:  # Linux
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        print(" Could not open image:", e)


# ---------------- Admin Login ----------------
def admin_login():
    username = input("Enter admin username: ")
    password = input_password("Enter admin password: ")  

    if username == "admin" and password == "admin123":
        print("Admin login successful.")
        return True
    else:
        print("Invalid admin credentials.")
        return False


# ---------------- Owners ----------------
def view_pending_owners():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT owner_id, name, email, gov_id_proof FROM owners WHERE status = 'pending'")
    pending = cursor.fetchall()

    if not pending:
        print("No pending owner approvals.")
    else:
        print("\nPending Owners:")
        for row in pending:
            print(f"\nID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Govt ID Proof Path: {row[3]}")
            choice = input("Do you want to open this ID proof image? (y/n): ")
            if choice.lower() == "y":
                open_image(row[3])
    conn.close()


def approve_owner():
    conn = get_connection()
    cursor = conn.cursor()
    owner_id = input("Enter the ID of the owner to approve: ")
    cursor.execute("UPDATE owners SET status = 'approved' WHERE owner_id = %s", (owner_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print(" Owner approved successfully.")
    else:
        print(" Invalid owner ID.")
    conn.close()


# ---------------- Renters ----------------
def view_pending_renters():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT renter_id, name, email, gov_id_proof FROM renters WHERE status = 'pending'")
    pending = cursor.fetchall()

    if not pending:
        print("No pending renter approvals.")
    else:
        print("\nPending Renters:")
        for row in pending:
            print(f"\nID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Govt ID Proof Path: {row[3]}")
            choice = input("Do you want to open this ID proof image? (y/n): ")
            if choice.lower() == "y":
                open_image(row[3])
    conn.close()


def approve_renter():
    conn = get_connection()
    cursor = conn.cursor()
    renter_id = input("Enter the ID of the renter to approve: ")
    cursor.execute("UPDATE renters SET status = 'approved' WHERE renter_id = %s", (renter_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print("Renter approved successfully.")
    else:
        print(" Invalid renter ID.")
    conn.close()


# ---------------- Equipment ----------------
def view_pending_equipment():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT equipment_id, name, description, price_per_day, image_path,
               purchase_proof, service_bill, purchase_date, model_number
        FROM equipment WHERE is_approved = FALSE
    """)
    pending = cursor.fetchall()

    if not pending:
        print("No pending equipment approvals.")
    else:
        print("\nPending Equipment:")
        for row in pending:
            eq_id, name, desc, price, image_path, purchase_proof, service_bill, purchase_date, model_number = row
            print(f"\nID: {eq_id}, Name: {name}")
            print(f"Description: {desc}")
            print(f"Price/Day: ₹{price}")
            print(f"Purchase Date: {purchase_date}")
            print(f"Model Number: {model_number}")
            print(f"Main Image: {image_path}")
            print(f"Purchase Proof: {purchase_proof}")
            print(f"Service Bill: {service_bill if service_bill else 'Not Provided'}")

            # Ask if admin wants to open images
            if purchase_proof:
                choice = input("Do you want to open Purchase Proof image? (y/n): ")
                if choice.lower() == "y":
                    open_image(purchase_proof)

            if service_bill:
                choice = input("Do you want to open Service Bill image? (y/n): ")
                if choice.lower() == "y":
                    open_image(service_bill)

    conn.close()


def approve_equipment():
    conn = get_connection()
    cursor = conn.cursor()
    eq_id = input("Enter the ID of the equipment to approve: ")
    cursor.execute("UPDATE equipment SET is_approved = TRUE WHERE equipment_id = %s", (eq_id,))
    if cursor.rowcount > 0:
        conn.commit()
        print(" Equipment approved successfully.")
    else:
        print(" Invalid equipment ID.")
    conn.close()

def owner_module():
    while True:
        print("\n[Owner ]")
        print("1. View Pending Owners")
        print("2. Approve Owner")
        print("3. Back")
        choice = input("Choose an option: ")

        if choice == '1':
            view_pending_owners()
        elif choice == '2':
            approve_owner()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")


def renter_module():
    while True:
        print("\n[Renter ]")
        print("1. View Pending Renters")
        print("2. Approve Renter")
        print("3. Back")
        choice = input("Choose an option: ")

        if choice == '1':
            view_pending_renters()
        elif choice == '2':
            approve_renter()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")


def equipment_module():
    while True:
        print("\n[Equipment ]")
        print("1. View Pending Equipment")
        print("2. Approve Equipment")
        print("3. Back")
        choice = input("Choose an option: ")

        if choice == '1':
            view_pending_equipment()
        elif choice == '2':
            approve_equipment()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")


# ---------------- Admin Dashboard ----------------
def admin_menu():
    if not admin_login():
        return

    while True:
        print("\n[Admin Dashboard]")
        print("1. Owner ")
        print("2. Renter ")
        print("3. Equipment ")
        print("4. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            owner_module()
        elif choice == '2':
            renter_module()
        elif choice == '3':
            equipment_module()
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice.")

# ---------------- Approved Records ----------------
def view_approved_owners():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT owner_id, name, email, city, pincode FROM owners WHERE status = 'approved'")
    rows = cursor.fetchall()

    if not rows:
        print("\nNo approved owners found.")
    else:
        print("\n Approved Owners:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, City: {row[3]}, Pincode: {row[4]}")
    conn.close()


def view_approved_renters():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT renter_id, name, email FROM renters WHERE status = 'approved'")
    rows = cursor.fetchall()

    if not rows:
        print("\nNo approved renters found.")
    else:
        print("\n Approved Renters:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
    conn.close()


def view_approved_equipment():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT equipment_id, name, description, price_per_day, quantity, model_number 
        FROM equipment WHERE is_approved = TRUE
    """)
    rows = cursor.fetchall()

    if not rows:
        print("\nNo approved equipment found.")
    else:
        print("\n Approved Equipment:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Description: {row[2]}, Price/Day: ₹{row[3]}, "
                  f"Quantity: {row[4]}, Model: {row[5]}")
    conn.close()

def approved_module():
    while True:
        print("\n[Approved Records]")
        print("1. View Approved Owners")
        print("2. View Approved Renters")
        print("3. View Approved Equipment")
        print("4. Back")
        choice = input("Choose an option: ")

        if choice == '1':
            view_approved_owners()
        elif choice == '2':
            view_approved_renters()
        elif choice == '3':
            view_approved_equipment()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def view_all_bookings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            b.booking_id,
            e.name AS equipment_name,
            e.model_number,
            e.city,
            e.pincode,
            o.name AS owner_name,
            o.mobile AS owner_mobile,
            r.name AS renter_name,
            r.mobile AS renter_mobile,
            b.start_date,
            b.end_date,
            b.quantity,
            b.status
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.equipment_id
        JOIN owners o ON e.owner_id = o.owner_id
        JOIN renters r ON b.renter_id = r.renter_id
        ORDER BY b.start_date DESC;
    """)

    rows = cursor.fetchall()

    if not rows:
        print("\nNo bookings have been made yet.")
    else:
        print("\n========= ALL EQUIPMENT BOOKINGS =========")
        for row in rows:
            (booking_id, eq_name, model_number, city, pincode,
             owner_name, owner_mobile, renter_name, renter_mobile,
             start_date, end_date, qty, status) = row

            print(f"\nBooking ID: {booking_id}")
            print(f"Equipment Name: {eq_name}")
            print(f"Model Number: {model_number}")
            print(f"Location: {city}, {pincode}")
            print(f"Quantity Booked: {qty}")
            print(f"Booking Schedule: {start_date} ➜ {end_date}")
            print(f"Status: {status}")
            print(f"Owner: {owner_name} | Mobile: {owner_mobile}")
            print(f"Renter: {renter_name} | Mobile: {renter_mobile}")
            print("--------------------------------------------")

    conn.close()
