from Db_connection import get_connection
from datetime import datetime, date

def add_equipment(owner_id):
    conn = get_connection()
    cursor = conn.cursor()

    name = input("Enter equipment name: ")
    desc = input("Enter description: ")
    price = float(input("Enter rental price per day: "))

    # Location details
    city = input("Enter city where equipment is available: ")
    pincode = input("Enter pincode where equipment is available: ")

    # Main image (mandatory)
    image_path = input("Enter path to main equipment image (mandatory): ")
    if not image_path.strip():
        print("Equipment image is mandatory. Cannot add equipment.")
        conn.close()
        return

    # Purchase proof (mandatory)
    purchase_proof = input("Enter path to purchase proof image (mandatory, must show date & model): ")
    if not purchase_proof.strip():
        print("Purchase proof image is mandatory. Cannot add equipment.")
        conn.close()
        return

    # Purchase date (mandatory)
    try:
        purchase_date_input = input("Enter purchase date (YYYY-MM-DD): ")
        purchase_date = datetime.strptime(purchase_date_input, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        conn.close()
        return

    # Model number (mandatory)
    model_number = input("Enter equipment model number or HSN code: ")
    if not model_number.strip():
        print("Model number is mandatory.")
        conn.close()
        return

    # Check if service bill is mandatory (older than 2 years)
    today = date.today()
    age_in_years = (today - purchase_date).days / 365
    service_bill = None
    if age_in_years > 2:
        service_bill = input("Enter path to service bill image (mandatory for equipment older than 2 years): ")
        if not service_bill.strip():
            print("Service bill is mandatory for equipment older than 2 years.")
            conn.close()
            return
    else:
        service_bill = input("Enter path to service bill image (optional): ")

    quantity = int(input("Enter number of this equipment available: "))

    # Insert equipment record
    cursor.execute("""
        INSERT INTO equipment 
        (owner_id, name, description, price_per_day, availability, is_approved, quantity,
         image_path, purchase_proof, service_bill, purchase_date, model_number, city, pincode)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (owner_id, name, desc, price, 'available', False, quantity,
          image_path, purchase_proof, service_bill, purchase_date, model_number, city, pincode))

    conn.commit()
    print("Equipment added successfully. Waiting for admin approval.")
    conn.close()


def view_equipment(owner_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT equipment_id, name, description, price_per_day, availability, 
               is_approved, quantity, image_path, purchase_proof, service_bill, 
               purchase_date, model_number, city, pincode
        FROM equipment WHERE owner_id = %s
    """, (owner_id,))

    rows = cursor.fetchall()

    if not rows:
        print("No equipment found.")
    else:
        for row in rows:
            (eq_id, name, desc, price, status, approved, qty, image_path,
             purchase_proof, service_bill, purchase_date, model_number, city, pincode) = row

            print(f"\nEquipment ID: {eq_id}")
            print(f"Name: {name}")
            print(f"Description: {desc}")
            print(f"Price per day: ₹{price}")
            print(f"Quantity Available: {qty}")
            print(f"Purchase Date: {purchase_date}")
            print(f"Model Number: {model_number}")
            print(f"Location: {city}, {pincode}")
            print(f"Main Equipment Image: {image_path}")
            print(f"Purchase Proof Image: {purchase_proof}")
            print(f"Service Bill Image: {service_bill if service_bill else 'Not Provided'}")
            print(f"Availability: {status}")
            print("Status:", "Approved by Admin" if approved else "Not Approved by Admin")

    conn.close()


def update_quantity_after_rent(owner_id):
    conn = get_connection()
    cursor = conn.cursor()

    eq_id = input("Enter equipment ID to update as rented: ")
    rented_qty = int(input("Enter quantity rented: "))

    cursor.execute("SELECT quantity FROM equipment WHERE equipment_id = %s AND owner_id = %s", (eq_id, owner_id))
    result = cursor.fetchone()

    if result is None:
        print("Equipment not found.")
        conn.close()
        return

    current_qty = result[0]

    if rented_qty > current_qty:
        print(f"Not enough quantity available. Current quantity: {current_qty}")
        conn.close()
        return

    new_qty = current_qty - rented_qty

    if new_qty == 0:
        cursor.execute("""
            UPDATE equipment 
            SET quantity = %s, availability = %s 
            WHERE equipment_id = %s AND owner_id = %s
        """, (new_qty, 'rented', eq_id, owner_id))
    else:
        cursor.execute("""
            UPDATE equipment 
            SET quantity = %s 
            WHERE equipment_id = %s AND owner_id = %s
        """, (new_qty, eq_id, owner_id))

    conn.commit()
    print(f"Updated! Remaining quantity: {new_qty}")
    conn.close()


def delete_equipment(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    eq_id = input("Enter equipment ID to delete: ")
    cursor.execute("DELETE FROM equipment WHERE equipment_id = %s AND owner_id = %s", (eq_id, owner_id))
    conn.commit()
    print("Equipment deleted successfully.")
    conn.close()
