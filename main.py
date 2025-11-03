
from owner import register_owner, login_owner,view_owner_bookings
from equipment import add_equipment, view_equipment,update_quantity_after_rent, delete_equipment
from admin import admin_login,owner_module,renter_module,equipment_module,approved_module,view_all_bookings
from renter import register_renter, login_renter, book_equipment, cancel_booking,search_equipment



def owner_dashboard(owner_id):
    while True:
        print("\n[Owner Dashboard]")
        print("1. Add Equipment")
        print("2. View Equipment")
        print("3. View bookings")
        print("4. Delete Equipment")
        print("5. Logout")

        choice = input("Choose an option: ")
        if choice == '1':
            add_equipment(owner_id)
        elif choice == '2':
            view_equipment(owner_id)
        elif choice == '3':
            view_owner_bookings(owner_id)
        elif choice == '4':
            delete_equipment(owner_id)
        elif choice == '5':
            print("Logging out...\n")
            break
        else:
            print("Invalid choice.")

def owner_menu():
    while True:
        print("\nOwner Menu")
        print("1. Register")
        print("2. Login")
        print("3. Back")
        choice = input("Choose an option: ")
        if choice == '1':
            register_owner()
        elif choice == '2':
            owner_id = login_owner()
            if owner_id:
                owner_dashboard(owner_id)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")




def renter_dashboard(renter_id):
    while True:
        print("\n[Renter Dashboard]")
        print("1. Search Equipment")
        print("2. Book Equipment")
        print("3. Cancel Booking")
        print("4. View Booked Equipment")   # ✅ New option
        print("5. Logout")
        choice = input("Choose an option: ")

        if choice == '1':
            search_equipment()
        elif choice == '2':
            book_equipment(renter_id)
        elif choice == '3':
            cancel_booking(renter_id)
        elif choice == '4':
            from renter import view_booked_equipment
            view_booked_equipment(renter_id)
        elif choice == '5':
            print("Logging out...\n")
            break
        else:
            print("Invalid choice.")




def renter_menu():
    while True:
        print("\n[Renter Menu]")
        print("1. Register")
        print("2. Login")
        print("3. Back")
        choice = input("Choose an option: ")
        if choice == '1':
            register_renter()
        elif choice == '2':
            renter_id = login_renter()
            if renter_id:
                renter_dashboard(renter_id)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")



def admin_menu():
    if not admin_login():
        return

    while True:
        print("\n[Admin Dashboard]")
        print("1. Owner ")
        print("2. Renter ")
        print("3. Equipment ")
        print("4. Approved ")   # ✅ New submodule
        print("5. Bookings")
        print("6. logout")

        choice = input("Choose an option: ")

        if choice == '1':
            owner_module()
        elif choice == '2':
            renter_module()
        elif choice == '3':
            equipment_module()
        elif choice == '4':
            approved_module()   # ✅ Call new menu
        elif choice == '5':
            view_all_bookings()
        elif choice == '6':
            print("logging out.....")
            break
        else:
            print("Invalid choice.")



def main_menu():
    while True:
        print("\n" + "="*40)
        print("   MEDICAL EQUIPMENT RENTAL SYSTEM   ")
        print("="*40)
        print("Select User Type:")
        print("1. Owner")
        print("2. Renter")
        print("3. Admin")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            owner_menu()
        elif choice == '2':
            renter_menu()
        elif choice == '3':
            admin_menu()
        elif choice == '4':
            print("Exiting the system. Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1–4.")

# Run the app
main_menu()
