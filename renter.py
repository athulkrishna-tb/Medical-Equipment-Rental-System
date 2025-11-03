from Db_connection import get_connection
import re
from datetime import datetime, date
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
        if ch in {b'\r', b'\n'}:  # Enter key
            print("")  # move to next line
            break
        elif ch == b'\x08':  # Backspace
            if len(pwd) > 0:
                pwd = pwd[:-1]
                sys.stdout.write("\b \b")  # remove last *
                sys.stdout.flush()
        elif ch == b'\x03':  # Ctrl+C
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


# ---------------- Validation ----------------
def is_valid_name(name):
    return re.match(r'^[A-Za-z ]+$', name) is not None

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def is_valid_mobile(mobile):
    # Indian mobile validation: 10 digits, starts with 6-9
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, mobile) is not None


# ---------------- Registration ----------------
def register_renter():
    conn = get_connection()
    cursor = conn.cursor()
    print("\n--- RENTER REGISTRATION ---")

    renter_data = {}

    # Step 1: Input fields
    while True:
        name = input("Enter your name: ").strip()
        if not is_valid_name(name):
            print("Invalid name. Only letters and spaces allowed.")
        else:
            renter_data['name'] = name
            break

    while True:
        email = input("Enter your email: ").strip()
        if not is_valid_email(email):
            print("Invalid email format.")
            continue
        cursor.execute("SELECT email FROM renters WHERE email = %s", (email,))
        if cursor.fetchone():
            print("Email already registered. Please use a different one.")
            continue
        renter_data['email'] = email
        break

    while True:
        password1 = input_password("Create a password: ")
        password2 = input_password("Re-enter the password: ")
        if password1 != password2:
            print("Passwords do not match. Try again.")
        elif len(password1) < 4:
            print("Password too short. Use at least 4 characters.")
        else:
            renter_data['password'] = password1
            break

    while True:
        gov_id_proof = input("Enter path to your Government ID proof image: ").strip()
        if not gov_id_proof:
            print("Government ID proof is mandatory. Please enter a valid path.")
        else:
            renter_data['gov_id_proof'] = gov_id_proof
            break

    while True:
        mobile = input("Enter your mobile number: ").strip()
        if not is_valid_mobile(mobile):
            print("Invalid mobile number. Must be 10 digits starting with 6–9.")
        else:
            renter_data['mobile'] = mobile
            break

    # Step 2: Review before submitting
    while True:
        print("\n-----------------------------")
        print("Please review your entered details:")
        print(f"1. Name: {renter_data['name']}")
        print(f"2. Email: {renter_data['email']}")
        print(f"3. Password: {'*' * len(renter_data['password'])}")
        print(f"4. Gov ID Proof Path: {renter_data['gov_id_proof']}")
        print(f"5. Mobile: {renter_data['mobile']}")
        print("-----------------------------")

        edit_choice = input("Do you want to edit any field? (yes/no): ").strip().lower()

        if edit_choice == 'no':
            break
        elif edit_choice == 'yes':
            field_map = {
                '1': 'name',
                '2': 'email',
                '3': 'password',
                '4': 'gov_id_proof',
                '5': 'mobile'
            }

            field_choice = input("Enter the number of the field you want to edit: ").strip()
            if field_choice not in field_map:
                print("Invalid choice.")
                continue

            field = field_map[field_choice]

            if field == 'password':
                while True:
                    password1 = input_password("Enter new password: ")
                    password2 = input_password("Re-enter new password: ")
                    if password1 == password2 and len(password1) >= 4:
                        renter_data['password'] = password1
                        print("Password updated successfully.")
                        break
                    else:
                        print("Password mismatch or too short.")
                        continue
            elif field == 'mobile':
                while True:
                    new_mobile = input("Enter new mobile number: ").strip()
                    if not is_valid_mobile(new_mobile):
                        print("Invalid mobile number. Must be 10 digits starting with 6–9.")
                    else:
                        renter_data['mobile'] = new_mobile
                        print("Mobile number updated successfully.")
                        break
            elif field == 'email':
                while True:
                    new_email = input("Enter new email: ").strip()
                    if not is_valid_email(new_email):
                        print("Invalid email format.")
                        continue
                    cursor.execute("SELECT email FROM renters WHERE email = %s", (new_email,))
                    if cursor.fetchone():
                        print("Email already registered. Try a different one.")
                        continue
                    renter_data['email'] = new_email
                    print("Email updated successfully.")
                    break
            else:
                new_value = input(f"Enter new {field.replace('_', ' ').title()}: ").strip()
                renter_data[field] = new_value
                print(f"{field.replace('_', ' ').title()} updated successfully.")
        else:
            print("Please type 'yes' or 'no'.")

    # Step 3: Save final details
    try:
        cursor.execute("""
            INSERT INTO renters (name, email, password, gov_id_proof, mobile, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            renter_data['name'],
            renter_data['email'],
            renter_data['password'],
            renter_data['gov_id_proof'],
            renter_data['mobile'],
            'pending'
        ))

        conn.commit()
        print("\n✅ Registration successful. Waiting for admin approval.")
    except Exception as e:
        print("Error during registration:", e)
    finally:
        conn.close()



# ---------------- Login ----------------
def login_renter():
    conn = get_connection()
    cursor = conn.cursor()
    name = input("Enter your name: ")
    password = input_password("Enter your password: ")

    cursor.execute("SELECT renter_id, status FROM renters WHERE name=%s AND password=%s", (name, password))
    result = cursor.fetchone()

    if result:
        renter_id, status = result
        if status == 'approved':
            print("Login successful.")
            return renter_id
        else:
            print("Your account is pending admin approval.")
            return None
    else:
        print(" Invalid credentials")
        return None


# ---------------- Booking ----------------
from datetime import datetime, date

def book_equipment(renter_id):
    conn = get_connection()
    cursor = conn.cursor()

    print("\nAvailable Approved Equipment:")
    cursor.execute("""
        SELECT equipment_id, name, description, price_per_day, city, pincode, quantity
        FROM equipment
        WHERE is_approved = TRUE AND availability = 'available'
    """)
    items = cursor.fetchall()

    if not items:
        print("No equipment currently available.")
        conn.close()
        return

    for eq in items:
        eq_id, name, desc, price, city, pincode, qty = eq
        print(f"\nEquipment ID: {eq_id}")
        print(f"Name: {name}")
        print(f"Description: {desc}")
        print(f"Price per day: ₹{price}")
        print(f"Available Quantity: {qty}")
        print(f"Location: {city}, {pincode}")

    eq_id = input("\nEnter the Equipment ID you want to book: ")

    # Check equipment existence and availability
    cursor.execute("SELECT quantity FROM equipment WHERE equipment_id = %s AND is_approved = TRUE", (eq_id,))
    result = cursor.fetchone()
    if not result:
        print("Invalid Equipment ID or not approved yet.")
        conn.close()
        return

    available_qty = result[0]
    qty = int(input("Enter quantity to book: "))
    if qty > available_qty:
        print(f"Only {available_qty} units are available.")
        conn.close()
        return

    # Booking dates
    try:
        start_date_input = input("Enter start date (YYYY-MM-DD): ")
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d").date()
        end_date_input = input("Enter end date (YYYY-MM-DD): ")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d").date()

        if start_date < date.today():
            print("Booking cannot start from a past date.")
            conn.close()
            return
        if end_date < start_date:
            print("End date must be after start date.")
            conn.close()
            return
    except ValueError:
        print("Invalid date format! Please use YYYY-MM-DD.")
        conn.close()
        return

    # ----------------- Cancellation Policy Info -----------------
    print("\n CANCELLATION POLICY ")
    print("---------------------------------------------------")
    print("1. Bookings can be cancelled up to 1 day before the start date.")
    print("2. Cancellations made less than 1 day before start date will incur a fine.")
    print("3. For fine amount details, please contact the equipment owner directly.")
    print("---------------------------------------------------")

    confirm = input("\nDo you agree to the above policy and wish to proceed with the booking? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Booking cancelled by user.")
        conn.close()
        return

    # Insert booking
    cursor.execute("""
        INSERT INTO bookings (renter_id, equipment_id, start_date, end_date, quantity, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (renter_id, eq_id, start_date, end_date, qty, 'booked'))
    conn.commit()

    print("\n✅ Booking successful! Please contact the owner for fine-related queries or early cancellation details.")
    conn.close()



# ---------------- Cancel Booking ----------------
def cancel_booking(renter_id):
    conn = get_connection()
    cursor = conn.cursor()

    booking_id = input("Enter booking ID to cancel: ")

    cursor.execute("SELECT equipment_id, quantity, status, start_date FROM bookings WHERE booking_id=%s AND renter_id=%s",
                   (booking_id, renter_id))
    result = cursor.fetchone()

    if not result:
        print(" Booking not found.")
        conn.close()
        return

    eq_id, qty, status, start_date = result
    if status == "cancelled":
        print(" Booking already cancelled.")
        conn.close()
        return

    today = date.today()
    if start_date <= today:
        print(" ❌ Cannot cancel after booking has started.")
        conn.close()
        return

    # Check cancellation policy
    if (start_date - today).days < 1:
        fine = 0.2  # 20% fine (you can change this)
        cursor.execute("SELECT price_per_day FROM equipment WHERE equipment_id=%s", (eq_id,))
        price = cursor.fetchone()[0]
        fine_amount = price * qty * fine
        print(f"⚠️ Cancellation late! You must pay ₹{fine_amount:.2f} as fine.")

    # Update booking & restore equipment
    cursor.execute("UPDATE bookings SET status='cancelled' WHERE booking_id=%s", (booking_id,))
    cursor.execute("UPDATE equipment SET quantity = quantity + %s WHERE equipment_id=%s", (qty, eq_id))

    conn.commit()
    print("✅ Booking cancelled and equipment restored.")
    conn.close()


# ---------------- Search Equipment ----------------
def search_equipment():
    conn = get_connection()
    cursor = conn.cursor()

    search_term = input("\nEnter equipment name or keyword to search: ").strip()

    # Normalize user input (remove extra spaces and lowercase)
    normalized_input = search_term.replace(" ", "").lower()

    # Fetch matching equipment (case-insensitive & space-insensitive)
    cursor.execute("""
        SELECT equipment_id, name, description, price_per_day, city, pincode, quantity
        FROM equipment
        WHERE is_approved = TRUE AND availability = 'available'
        AND LOWER(REPLACE(name, ' ', '')) LIKE %s
    """, (f"%{normalized_input}%",))

    results = cursor.fetchall()

    if not results:
        print("\nNo equipment found matching your search.")
    else:
        print("\nSearch Results:")
        for row in results:
            eq_id, name, desc, price, city, pincode, qty = row
            print("\n----------------------------------")
            print(f"Equipment ID: {eq_id}")
            print(f"Name: {name}")
            print(f"Description: {desc}")
            print(f"Price per day: ₹{price}")
            print(f"Available Quantity: {qty}")
            print(f"Location: {city}, {pincode}")
            print("----------------------------------")

    conn.close()



# ---------------- View Booked Equipment ----------------
# ---------------- View Booked Equipment ----------------
def view_booked_equipment(renter_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            b.booking_id, 
            e.name AS equipment_name, 
            e.description, 
            b.start_date, 
            b.end_date, 
            b.quantity, 
            b.status,
            o.name AS owner_name,
            o.mobile AS owner_mobile
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.equipment_id
        JOIN owners o ON e.owner_id = o.owner_id
        WHERE b.renter_id = %s
        ORDER BY b.booking_id DESC
    """, (renter_id,))

    results = cursor.fetchall()

    if not results:
        print("\nYou have no bookings yet.")
    else:
        print("\nYour Booked Equipment:")
        for row in results:
            booking_id, eq_name, desc, start_date, end_date, qty, status, owner_name, owner_mobile = row
            print(f"\nBooking ID: {booking_id}")
            print(f"Equipment: {eq_name}")
            print(f"Description: {desc}")
            print(f"Start Date: {start_date}")
            print(f"End Date: {end_date}")
            print(f"Quantity: {qty}")
            print(f"Status: {status}")
            print(f"Owner Name: {owner_name}")
            print(f"Owner Mobile: {owner_mobile}")

    conn.close()

