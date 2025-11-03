from Db_connection import get_connection
import re
import requests
from getpass import getpass
import sys
import msvcrt

# ---------------- Validations ----------------
def is_valid_name(name):
    pattern = r'^[A-Za-z ]+$'
    return re.match(pattern, name) is not None

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_city(city):
    pattern = r'^[A-Za-z ]+$'
    return re.match(pattern, city) is not None

def is_valid_pincode(pincode):
    pattern = r'^[1-9][0-9]{5}$'
    return re.match(pattern, pincode) is not None

def is_valid_mobile(mobile):
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, mobile) is not None

def verify_pincode_api(pincode):
    try:
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        if data and data[0]['Status'] == "Success":
            post_office = data[0]['PostOffice'][0]
            return True, post_office['District'], post_office['State']
        else:
            return False, None, None
    except Exception as e:
        print("Error checking pincode:", e)
        return False, None, None

def input_password(prompt="Password: "):
    """
    Windows-friendly masked input using msvcrt (keeps compatibility with original).
    """
    print(prompt, end="", flush=True)
    pwd = ""
    while True:
        ch = msvcrt.getch()
        if ch in {b'\r', b'\n'}:  # Enter key
            print("")
            break
        elif ch == b'\x08':  # Backspace
            if len(pwd) > 0:
                pwd = pwd[:-1]
                sys.stdout.write("\b \b")
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

# ---------------- Registration ----------------
def register_owner():
    conn = get_connection()
    cursor = conn.cursor()

    print("\n--- OWNER REGISTRATION ---")

    # Step 1: Collect all data first
    owner_data = {}

    # Name
    while True:
        name = input("Enter your name: ").strip()
        if not is_valid_name(name):
            print("Invalid name. Only letters and spaces allowed.")
        else:
            owner_data['name'] = name
            break

    # Email
    while True:
        email = input("Enter your email: ").strip()
        if not is_valid_email(email):
            print("Invalid email format.")
            continue
        cursor.execute("SELECT email FROM owners WHERE email = %s", (email,))
        if cursor.fetchone():
            print("Email already registered. Please use a different email.")
            continue
        owner_data['email'] = email
        break

    # Password (create & confirm)
    while True:
        password1 = input_password("Create a password: ")
        password2 = input_password("Re-enter the password: ")
        if password1 != password2:
            print("Passwords do not match. Try again.")
        elif len(password1) < 4:
            print("Password too short. Use at least 4 characters.")
        else:
            owner_data['password'] = password1
            break

    # Mobile
    while True:
        mobile = input("Enter your mobile number: ").strip()
        if not is_valid_mobile(mobile):
            print("Invalid mobile number. Must be 10 digits starting with 6–9.")
        else:
            owner_data['mobile'] = mobile
            break

    # City
    while True:
        city = input("Enter your city: ").strip()
        if not is_valid_city(city):
            print("Invalid city. Only letters and spaces allowed.")
        else:
            owner_data['city'] = city
            break

    # Pincode (with API verification)
    while True:
        pincode = input("Enter your 6-digit pincode: ").strip()
        if not is_valid_pincode(pincode):
            print("Invalid pincode format. Must be 6 digits.")
            continue
        valid_pin, district, state = verify_pincode_api(pincode)
        if not valid_pin:
            print("Pincode not found in India Post records. Re-enter.")
            continue
        else:
            print(f"Pincode verified ✅ District: {district}, State: {state}")
            owner_data['pincode'] = pincode
            break

    # Govt ID proof path
    while True:
        gov_id_proof = input("Enter path to your Government ID proof image: ").strip()
        if not gov_id_proof:
            print("Government ID proof is mandatory. Please enter a valid path.")
        else:
            owner_data['gov_id_proof'] = gov_id_proof
            break

    # Step 2: Review before submitting
    while True:
        print("\n-----------------------------")
        print("Please review your entered details:")
        print(f"1. Name: {owner_data['name']}")
        print(f"2. Email: {owner_data['email']}")
        print(f"3. Password: {'*' * len(owner_data['password'])}")
        print(f"4. Mobile: {owner_data['mobile']}")
        print(f"5. City: {owner_data['city']}")
        print(f"6. Pincode: {owner_data['pincode']}")
        print(f"7. Gov ID Proof Path: {owner_data['gov_id_proof']}")
        print("-----------------------------")

        edit_choice = input("Do you want to edit any field? (yes/no): ").strip().lower()

        if edit_choice == 'no':
            break
        elif edit_choice == 'yes':
            field_map = {
                '1': 'name',
                '2': 'email',
                '3': 'password',
                '4': 'mobile',
                '5': 'city',
                '6': 'pincode',
                '7': 'gov_id_proof'
            }

            field_choice = input("Enter the number of the field you want to edit: ").strip()
            if field_choice not in field_map:
                print("Invalid choice.")
                continue

            field = field_map[field_choice]

            if field == 'password':
                password1 = input_password("Enter new password: ")
                password2 = input_password("Re-enter new password: ")
                if password1 == password2 and len(password1) >= 4:
                    owner_data['password'] = password1
                    print("Password updated.")
                else:
                    print("Password mismatch or too short.")
                    continue
            elif field == 'pincode':
                while True:
                    new_pin = input("Enter new 6-digit pincode: ").strip()
                    if not is_valid_pincode(new_pin):
                        print("Invalid pincode format.")
                        continue
                    valid_pin, district, state = verify_pincode_api(new_pin)
                    if not valid_pin:
                        print("Pincode not found in India Post records.")
                        continue
                    else:
                        owner_data['pincode'] = new_pin
                        print(f"Updated Pincode ✅ District: {district}, State: {state}")
                        break
            else:
                new_value = input(f"Enter new {field.replace('_', ' ').title()}: ").strip()
                owner_data[field] = new_value
                print(f"{field.replace('_', ' ').title()} updated successfully.")
        else:
            print("Please type 'yes' or 'no'.")

    # Step 3: Save final details
    try:
        cursor.execute("""
            INSERT INTO owners (name, email, password, mobile, city, pincode, gov_id_proof, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            owner_data['name'],
            owner_data['email'],
            owner_data['password'],
            owner_data['mobile'],
            owner_data['city'],
            owner_data['pincode'],
            owner_data['gov_id_proof'],
            'pending'
        ))

        conn.commit()
        print("\n✅ Registration successful. Waiting for admin approval.")
    except Exception as e:
        print("Error during registration:", e)
    finally:
        conn.close()



# ---------------- Login ----------------
def login_owner():
    conn = get_connection()
    cursor = conn.cursor()
    name = input("Enter your name: ")
    password = input_password("Enter your password: ")

    cursor.execute("SELECT owner_id, status FROM owners WHERE name= %s  AND password=%s", (name, password))
    result = cursor.fetchone()

    if result:
        owner_id, status = result
        if status == 'approved':
            print("Login successful.")
            return owner_id
        else:
            print("Your account is pending admin approval.")
            return None
    else:
        print("Invalid credentials")
        return None
# ---------------- View Bookings (For Owner) ----------------
def view_owner_bookings(owner_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            b.booking_id,
            e.name AS equipment_name,
            b.quantity,
            b.start_date,
            b.end_date,
            r.name AS renter_name,
            r.mobile AS renter_mobile,
            b.status
        FROM bookings b
        JOIN equipment e ON b.equipment_id = e.equipment_id
        JOIN renters r ON b.renter_id = r.renter_id
        WHERE e.owner_id = %s
        ORDER BY b.start_date DESC;
    """, (owner_id,))

    results = cursor.fetchall()

    if not results:
        print("\nNo bookings found for your equipment yet.")
    else:
        print("\nYour Equipment Bookings:")
        for row in results:
            booking_id, eq_name, qty, start_date, end_date, renter_name, renter_mobile, status = row
            print(f"\nBooking ID: {booking_id}")
            print(f"Equipment: {eq_name}")
            print(f"Quantity Rented: {qty}")
            print(f"Start Date: {start_date}")
            print(f"End Date: {end_date}")
            print(f"Renter Name: {renter_name}")
            print(f"Renter Mobile: {renter_mobile}")
            print(f"Status: {status}")
    conn.close()

