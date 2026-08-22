#Inventory
#Function used to record every actions users did
def log_action(username, action):
    #Log actions performed by users.
    reports = load_data(REPORTS_FILE)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if username not in reports:
        reports[username] = []
    
    reports[username].append({
        'time': current_time,
        'action': action
    })
    
    save_data(reports, REPORTS_FILE)

def modify_staff_password(username, new_password, ic, active, filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        with open(filename, 'w') as file:
            found = False
            for line in lines:
                user_data = line.strip().split(',')
                if user_data[0] == username and user_data[2] == ic and user_data[3] == active:
                    file.write(f"{username},{new_password},{ic},{active}\n")
                    found = True
                else:
                    file.write(line)
            
            if not found:
                return False, "Username, Identity Card, or account status does not match."

        return True, "Password updated successfully."

    except Exception as e:
        return False, f"An error occurred: {e}"


def StaffLogIn():
    max_attempts=3
    attempts=0
    print("\n*******************************")
    print("  Inventory Staff Log In Page  ")
    print("*******************************")
    while attempts<max_attempts:
        username = input("\nEnter Username: ")
        password = input("Enter Password: ")
        ic = input("Enter Identity Card:")
        active="active"
        if verify_Staffcredentials(username, password, ic, active,"staff.txt"):
            print(f"Login successful! Welcome, {username}")
            staff_menu(username)
        else:
            attempts+=1
            print(f"Wrong username or password. You have {max_attempts-attempts} attempts left.")
            if attempts==3:
                print("Too many failed attempts. Please reset your password.")
                valid, message = reset_staff_password(username, ic, active, "staff.txt")
                print(message)

def reset_staff_password(username, ic, active, filename):
    print("****************************************")
    print("             Reset Password             ")
    print("****************************************")
    
    attempt_count = 0
    max_attempts = 5
    
    while attempt_count < max_attempts:
        new_password = input("Please enter new password (At least 8 characters, including uppercase letter, number, and special character): ")
        
        if len(new_password) < 8:
            print("Password must be at least 8 characters.")
            attempt_count += 1
            continue
    
        has_upper = any(char.isupper() for char in new_password)
        has_digit = any(char.isdigit() for char in new_password)
        special_characters = "!@#$%^&*_-+=()./?:;\"<>[]{|}"
        has_special = any(char in special_characters for char in new_password)

        if not has_upper:
            print("Password must contain at least 1 uppercase letter.")
            attempt_count += 1
            continue
        if not has_digit:
            print("Password must contain at least 1 number.")
            attempt_count += 1
            continue
        if not has_special:
            print("Password must contain at least 1 special character.")
            attempt_count += 1
            continue
        
        # Password Confirmation
        confirm_password = input("Please confirm your new password: ")
        if new_password != confirm_password:
            print("Passwords do not match. Please try again.")
            attempt_count += 1
            continue

        # If all checks passed, modify the password
        valid, message = modify_staff_password(username, new_password, ic, active, filename)
        print(f"Modify password result: {valid}, Message: {message}")  # Debug print
        if valid:
            return True, "Password has been reset successfully."
        else:
            return False, "Failed to reset password. Please try again."
    
    return False, "Too many failed attempts. Please contact the system administrator."

def verify_Staffcredentials(username, password, ic, active, filename):
    try:
        with open(filename, "r") as file:
            for line in file.readlines():
                stored_username, stored_password, stored_ic, stored_active = line.strip().split(",")

                if username == stored_username and password == stored_password and ic == stored_ic and active == stored_active:
                    return True
    except FileNotFoundError:
        return False
    return False

def StaffSignUp():
    role="staff"
    status="pending"
    print("\n*************************************")
    print("  Inventory Staff Registration Page  ")
    print("*************************************")
    while True:
        username = input("\nCreate username: ")
        if check_username(username, "staff.txt"):
            print("Username already exists. Please try another one.")
        else:
            break

    while True:
        password = input("Create password (At least 8 characters, including uppercase letter, number, and special character): ")
        valid, message = check_password(password)
        if not valid:
            print(message)
            continue
        
        verify_pw = input("Re-enter password: ")
        if verify_pw == password:
            print("-Password match-")
            break

        else:
            print("Password do not match. Please try again.")
            continue

    while True:
        ic=int(input("Identity Card:"))
        if check_ic(ic,"staff_ic.txt"):
            print("Invalid Identity Card. Please try again.")
        else:
            print("Your registration is pending to be approved.")
            print("You will be returned to Homepage.")
            save_pendingStaff(username, password, ic, role, status, "users.txt")
            homepage()
            break

def save_pendingStaff(username, password, ic, role, status, filename):
    with open('users.txt', "a") as file:
        file.writelines(f"{username},{password},{ic},{role},{status}\n")

def check_ic(ic, filename):
    try:
        with open(filename, "r") as file:
            existing_username = [line.strip().split(",")[0] for line in file.readlines()]
            if ic in existing_ic:
                return True
    except FileNotFoundError:
        return False
    return False

def Staffhomepage():
    print("\n******************************")
    print("   Inventory Staff Homepage   ")
    print("******************************")
    print("1. Login")
    print("2. Signup")
    homepageoption=input("Please enter your option:")
    if homepageoption == "1":
        StaffLogIn()
    elif homepageoption == "2":
        StaffSignUp()
    else:
        print("Invalid options. Please try again")
        Staffhomepage()

def load_data(filename):
    #Load JSON data from a file
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, filename):
    #Save JSON data to a file
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def initialize_files():
    #Initialize stock and orders files with default values
    if not load_data(STOCK_FILE):
        initial_stock={
            'Desktop':{'quantity':17,'price':2500,"for_staff_only": False},
            'Laptop':{'quantity':20,'price':4000,"for_staff_only": False},
            'Mouse':{'quantity':10,'price':80,"for_staff_only": False},
            'Keyboard':{'quantity':20,'price':150,"for_staff_only": False},
            'Monitor':{'quantity':10,'price':500,"for_staff_only": False},
            'Charger':{'quantity':10,'price':100,"for_staff_only": False},
            'CPU':{'quantity':10,'price':500,"for_staff_only": True},
            }
        save_data(initial_stock, STOCK_FILE)

    if not load_data(SERVICE_ORDERS_FILE):
        initial_service={
            'Computer Repair':{'tentative_time':'3-5 days','service_price':250},
            'Device Repair':{'tentative_time':'2-4 days','service_price':100},
            'Software Installation':{'tentative_time':'1 days','service_price':200},
            'Hardware Upgrade':{'tentative_time':'2-3 days','service_price':250}
            }
        save_data(initial_service, SERVICE_ORDERS_FILE)

    if not load_data(PURCHASED_ITEMS_FILE):
        save_data([], PURCHASED_ITEMS_FILE)

    if not load_data(FEEDBACK_FILE):
        initial_feedback={
            'username': 'JohnDoe',
            'date': '2024-08-14 10:15:30',
            'rating': 5,
            'comments': 'Great service!'
            }
        save_data(initial_feedback, FEEDBACK_FILE)

def update_stock(item, quantity):
    #Update stock levels in the stock file.
    stock = load_data(STOCK_FILE)
    
    if item in stock:
        stock[item]['quantity'] += quantity
        save_data(stock, STOCK_FILE)
        print(f"\nStock updated: {item} now has {stock[item]['quantity']} units.")
    else:
        print("Invalid item for stock update.")

def save_purchase_record(username, order_items, total_cost, status):
    # Save a record of the purchased items
    orders = load_data(PURCHASED_ITEMS_FILE)
    orders.append({'username': username, 'items': order_items, 'total_cost': total_cost, 'status': status})
    save_data(orders, PURCHASED_ITEMS_FILE)

def get_stock():
    #Retrieve current stock levels
    return load_data(STOCK_FILE)

def inventory_modify_order(username, order_id, item, new_quantity):
    #Modify the quantity of a specific item in an existing purchase order.
    orders = load_data(PURCHASED_ITEMS_FILE)
    stock = load_data(STOCK_FILE)
    
    if 1 <= order_id <= len(orders):
        order = orders[order_id - 1]
        
        if order.get('status') == 'Paid':
            print("Cannot modify a paid order.")
            return

        items = order.get('items', [])
        
        # Find the item in the order
        item_to_modify = None
        for i in items:
            if i['item'] == item:
                item_to_modify = i
                break
        
        if not item_to_modify:
            print(f"Item '{item}' not found in the order.")
            return
        
        old_quantity = item_to_modify['quantity']
        quantity_difference = new_quantity - old_quantity

        # Update stock based on the difference in quantity
        update_stock(item, quantity_difference)

        # Update the item with the new quantity and recalculate the total cost
        item_to_modify['quantity'] = new_quantity
        item_to_modify['total_cost'] = stock[item]['price'] * new_quantity

        # Recalculate the total cost for the entire order
        order['total_cost'] = sum(
            i.get('total_cost', stock[i['item']]['price'] * i['quantity']) for i in items
        )
        
        print(f"Order {order_id} modified.")
        print(f"Item: {item}")
        print(f"Old Quantity: {old_quantity}, New Quantity: {new_quantity}")
        print(f"New Total Cost for Item: RM{item_to_modify['total_cost']:.2f}")
        print(f"New Total Cost for Order: RM{order['total_cost']:.2f}")
        save_data(orders, PURCHASED_ITEMS_FILE)
    else:
        print("Invalid order ID.")
    log_action(username, "Stock Check - Modify Purchase Order")


def inventory_cancel_order(username, order_id):
    #Cancel an existing purchase order.
    try:
        orders = load_data(PURCHASED_ITEMS_FILE)
        
        if 1 <= order_id <= len(orders):
            order = orders[order_id - 1]  # Adjust for 1-based index
            items = order.get('items', [])
            
            if order.get('status') == 'paid':
                print("Paid orders are non-refundable unless the product is unavailable.")
            else:
                # Update stock for each item in the order
                for item in items:
                    item_name = item['item']
                    quantity = item['quantity']
                    update_stock(item_name, quantity)  # Increase stock by the ordered quantity
                
                # Remove the order from the list
                orders.pop(order_id - 1)
                
                # Save the updated orders list
                save_data(orders, PURCHASED_ITEMS_FILE)
                
                print(f"Order ID: {order_id} canceled.")
                log_action(username, "Cancel Purchase Order")
        else:
            print("Invalid order ID.")
    except Exception as e:
        print(f"An error occurred while canceling the order: {e}")
    

def inventory_stock_check(username, for_staff=False):
    #Display and adjust current stock levels, optionally filtering by visibility.
    stock = get_stock()
    
    while True:
        print("\nCurrent stock:")
        for idx, (item, details) in enumerate(stock.items(), start=1):
            quantity = details.get('quantity', 0)
            price = details.get('price', 0.0)
            item_type = details.get('type', 'Unknown')
            for_staff_only = details.get('for_staff_only', False)
            visibility = 'Staff Only' if for_staff_only else 'Staff and Customer'
            
            # Filter items based on visibility
            if not for_staff or (for_staff and for_staff_only):
                print(f"{idx}. {item} ")
                print(f"   Quantity: {quantity}")
                print(f"   Price: RM{price:.2f}")
                print(f"   Available for: {visibility}")
        print("\nOptions:")
        print("1. Update Quantity")
        print("2. Update Price")
        print("3. Add New Item")
        print("4. Remove Item")
        print("5. Exit")
        
        option = input("Select an option (1-5): ")
        
        if option == '1':
            item_index = int(input("Enter the item number to update quantity: ")) - 1
            if 0 <= item_index < len(stock):
                item = list(stock.keys())[item_index]
                new_quantity = int(input("Enter the new quantity: "))
                stock[item]['quantity'] = new_quantity
                save_data(stock, STOCK_FILE)
                print(f"Updated quantity for {item} to {new_quantity}.")
            else:
                print("Invalid item number.")
            log_action(username, "Stock Check - Update Quantity")
        
        elif option == '2':
            item_index = int(input("Enter the item number to update price: ")) - 1
            if 0 <= item_index < len(stock):
                item = list(stock.keys())[item_index]
                new_price = float(input("Enter the new price: RM"))
                stock[item]['price'] = new_price
                save_data(stock, STOCK_FILE)
                print(f"Updated price for {item} to RM{new_price:.2f}.")
            else:
                print("Invalid item number.")
            log_action(username, "Stock Check - Update Price")
        
        elif option == '3':
            item = input("Enter the name of the new item: ")
            initial_quantity = int(input("Enter the initial quantity of the new item: "))
            initial_price = float(input("Enter the price of the new item: RM"))
            for_staff_only = input("Is this item available for staff only? (Y for Yes | N for No): ").strip().upper()

            if item in stock:
                print(f"{item} already exists in stock.")
            else:
                if for_staff_only == 'Y':
                    for_staff_only = True
                elif for_staff_only == 'N':
                    for_staff_only = False
                else:
                    print("Invalid input. Please try again.")
                    return  # Exit the function if input is invalid

            # Save the item to stock with the appropriate availability
            stock[item] = {
                'quantity': initial_quantity,
                'price': initial_price,
                'for_staff_only': for_staff_only  
            }
            save_data(stock, STOCK_FILE)

            # Display the registered item details
            print(f"New item registered: {item}")
            print(f"    Quantity: {initial_quantity}")
            print(f"    Price per unit: RM{initial_price:.2f}")
            print(f"    For staff only: {for_staff_only}")

            # Log the action
            log_action(username, "Stock Check - Add New Item")

        elif option == '4':
            item_index = int(input("Enter the item number to remove: ")) - 1
            if 0 <= item_index < len(stock):
                item = list(stock.keys())[item_index]
                del stock[item]
                save_data(stock, STOCK_FILE)
                print(f"Removed item: {item}.")
            else:
                print("Invalid item number.")
            log_action(username, "Stock Check - Remove Item")
        
        elif option == '5':
            print("Exiting stock check.")
            log_action(username, "Stock Check - Exit")
            break
        
        else:
            print("Invalid option. Please try again.")

#PURCHASE ORDER FOR STAFF
def inventory_purchase_order(username):
    stock = get_stock()
    purchased_items = load_data(PURCHASED_ITEMS_FILE)
    user_orders = [order for order in purchased_items if order.get('username') == username]
    
    print("\n--------Available Items for Inventory Staff--------")
    # Display items with index, item name, quantity, price
    for idx, (item, details) in enumerate(stock.items(), start=1):
        print(f"{idx}. {item}")
        print(f"    Quantity: {details['quantity']}")
        print(f"    Price: RM{details['price']:.2f}")

    #Create a list to store the items that staff bought
    order_items = []
    
    try:
        while True:
            item_idx = int(input("\nEnter the item number to order (or 0 to finish): "))
            if item_idx == 0:
                break
            
            if item_idx < 1 or item_idx > len(stock):
                print("Invalid item number.")
                continue
            
            item = list(stock.keys())[item_idx - 1]
            quantity = int(input(f"Enter quantity for {item}: "))
            

            # Calculate total price for the quantity ordered
            total = stock[item]['price'] * quantity
            order_items.append({
                'item': item,
                'quantity': quantity,
                'price': stock[item]['price'],
                'total_cost': total
            })
            
            # Update stock
            update_stock(item, +quantity)  # Increase stock by the ordered quantity

        # Check if any items were ordered
        if not order_items:
            print("No items were ordered.")
            return
        
        # Save the purchase record
        total_cost = sum(item['total_cost'] for item in order_items)
        status = "Unpaid"
        save_purchase_record(username, order_items, total_cost, status)  # Save the purchase record
        save_data(stock, "stock.json")
        
        # Print the order summary
        print("\nPurchase Order Placed Successfully!")
        for idx, item in enumerate(order_items, start=1):
            print(f"{idx}. {item['item']}")
            print(f"    Quantity: {item['quantity']}")
            print(f"    Price: RM{item['price']:.2f}")
        
        print(f"\nTotal Price: RM{total_cost:.2f}")
        print(f"Status: {status}")
        log_action(username, "Make Purchase Order")

    except ValueError:
        print("Invalid input. Please enter numbers only.")
        log_action(username, "Fail to Make Purchase Order")
    

def inventory_check_purchase_order_status(username):
    log_action(username, "Check Purchase Order Status")
    try:
        #List the purchase orders
        orders = load_data(PURCHASED_ITEMS_FILE)

        user_orders = [order for order in orders if order.get('username') == username]
        
        if not user_orders:
            print("No orders found.")
            staff_menu(username)
        else:
            print("Purchase orders:")
            #List the purchase order with index number
            for index, order in enumerate(user_orders, start=1):
                # Get the order status, default to 'Unpaid' if not set
                status = "Paid" if order.get('status', 'Unpaid') == 'Paid' else "Unpaid"
                # Safely get the total cost, default to 0.0 if not set
                total_cost = order.get('total_cost', 0.0)
                
                print(f"\n---------Order ID: {index}---------")
                
                # Check if 'items' key exists and is a list
                if 'items' in order and isinstance(order['items'], list):
                    for idx, item in enumerate(order['items'], start=1):
                        # Ensure item dictionary contains necessary keys
                        quantity = item.get('quantity', 'Unknown')
                        item_name = item.get('item', 'Unknown')
                        price = item.get('price', 0.0)
                        print(f"{idx}. {item_name}")
                        print(f"   Quantity: {quantity}")
                        print(f"   Price per unit: RM{price:.2f}")
                else:
                    print("  - No items found in this order.")
                
                print(f"\nTotal Price: RM{total_cost:.2f}")
                print(f"Status: {status}")
                       
    except Exception as e:
        print(f"An error occurred while listing orders: {e}")

def service_order(username):
    services=load_data(SERVICE_ORDERS_FILE)
    print("\nAvailabe Service/ Repairs:")
    for idx,(service, details) in enumerate(services.items(),start=1):
        print(f"{idx}. {service} : {details['tentative_time']}")
        print(f"   Price: RM{details['service_price']:.2f}")

    service_options=input("Enter Y to modify or N to exit.")
    
    if service_options == 'Y':
        service_name = input("Enter the service name you want to modify: ").strip()
        if service_name in services:
            new_name = input("Enter new service name (or press Enter to keep the current name): ").strip()
            new_time = input("Enter new tentative time (or press Enter to keep the current time): ").strip()
            new_price = input("Enter new service price (or press Enter to keep the current price):RM ").strip()

            if new_name:
                services[new_name] = services.pop(service_name)
                service_name = new_name
            
            if new_time:
                services[service_name]['tentative_time'] = new_time
            
            if new_price:
                try:
                    services[service_name]['service_price'] = float(new_price)
                except ValueError:
                    print("Invalid price input. Keeping the old price.")
            
            save_data(services, SERVICE_ORDERS_FILE)
            print("Service updated successfully.")
            log_action(username, "Modify Service Order")
        
        else:
            print("Service not found.")
        staff_menu(username)

def inventory_payment(username):
    log_action(username, "Make Payment")
    
    # Load purchase orders and filter for the specific user
    orders = load_data(PURCHASED_ITEMS_FILE)
    user_orders = [order for order in orders if order.get('username') == username]
    
    if not user_orders:
        print(f"No purchase orders found for {username}. No payment needed.")
        return

    print("\nYour Purchase Orders:")
    for index, order in enumerate(user_orders, start=1):
        # Get the order status, default to 'Unpaid' if not set
        status = "Paid" if order.get('status', 'Unpaid') == 'Paid' else "Unpaid"
        total_cost = order.get('total_cost', 0.0)
        
        print(f"\n---------Order ID: {index}---------")
        
        # Display Purchase Order
        if 'items' in order and isinstance(order['items'], list):
            for idx, item in enumerate(order['items'], start=1):
                item_name = item.get('item', 'Unknown')
                quantity = item.get('quantity', 'Unknown')
                price = item.get('price', 0.0)
                print(f"{idx}. {item_name}")
                print(f"   Quantity: {quantity}")
                print(f"   Price per unit: RM{price:.2f}")
            print(f"\nTotal Price: RM{total_cost:.2f}")
            print(f"Status: {status}")
        else:
            print("  - No items found in this order.")

    # Ask for Order ID to make payment
    try:
        payment_id = int(input("\nSelect your Order ID to make payment: "))
        
        if 1 <= payment_id <= len(user_orders):
            selected_order = user_orders[payment_id - 1]
            
            # Check current status
            if selected_order.get('status', 'Unpaid') == 'Paid':
                print("This order is already paid.")
                return

            answer = input("Do you want to make payment (Y for Yes, N for No): ").strip().upper()
            if answer == 'Y':
                selected_order['status'] = 'Paid'
                save_data(orders, PURCHASED_ITEMS_FILE)  # Save the updated orders
                print("Payment successful. You will receive your goods in 3-4 working days.")
            elif answer == 'N':
                print("Payment not completed. Don't forget to pay.")
            else:
                print("Invalid input. Please try again.")
        else:
            print("Invalid Order ID.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    
    log_action(username, "Attempted to Make Payment")
    
def staff_view_reports(username):
    #View the action logs (reports) for a specific user.
    reports = load_data(REPORTS_FILE)
    
    # Get reports for the specific username
    user_reports = reports.get(username, [])
    
    if not user_reports:
        print(f"No reports found for user: {username}.")
    else:
        print(f"\nReports for {username}:")
        print("     Date    |  Time  |       Actions")
        for action in user_reports:
            print(f" - {action['time']}: {action['action']}")

    input("\nPress Enter to return to the main menu...")

def staff_view_service_orders():
    # Load service orders from the file
    service_orders = load_orders_details('service_orders.txt')

    # Check if there are any service orders to display
    if not service_orders:
        print("No service orders found.")
        return

    # Print the order summary header
    print("****************************************************************************************")
    print("                                     Order Summary")
    print("****************************************************************************************\n")

    # Display each service order
    for order_id, order in service_orders.items():
        print(f"Order ID: {order_id}, Customer: {order['username']}, Status: {order['status']}, Total Price: RM{order['total_price']:.2f}")
        for item in order['items']:
            print(f" - {item['name']} (RM{item['price']:.2f})")
        print()  # Print a newline for better readability

    # Prompt for status update
    while True:
        order_id = input("Enter the Order ID you want to modify (or type '0' to quit): ")
        if order_id == '0':
            break
        
        if order_id not in service_orders:
            print("Invalid Order ID.")
            continue

        current_status = service_orders[order_id]['status']
        print(f"Current status for Order ID {order_id}: {current_status}")
        
        new_status = input("Enter new status (Done/Processing): ").capitalize()
        if new_status not in ['Done', 'Processing']:
            print("Invalid status. Please enter 'Done' or 'Processing'.")
            continue
        
        # Update the order status
        service_orders[order_id]['status'] = new_status
        print(f"Order ID {order_id} status updated to {new_status}.")

        # Save updated orders back to the file
        save_orders_details('service_orders.txt', service_orders)



def save_orders_details(filename, orders):
    with open(filename, 'w') as file:
        for order_id, order in orders.items():
            items_str = []
            for item in order['items']:
                if 'quantity' in item:
                    items_str.append(f"{item['name']},{item['quantity']},{item['price']}")
                else:
                    items_str.append(f"{item['name']},{item['price']}")
            items_line = ";".join(items_str)
            line = f"{order_id};{order['username']};{order['status']};{order['total_price']:.2f};{items_line}\n"
            file.write(line)

def staff_menu(username):
    #Main menu for interacting with the inventory system
    initialize_files()
    log_action(username,"Login")
    while True:
        print("\n************************")
        print("     Inventory Menu     ")
        print("************************")
        print("1. Place Purchase Order")
        print("2. Modify Purchase Order")
        print("3. Cancel Purchase Order")
        print("4. Check Purchase Order Status")
        print("5. Stock Check/Adjustments")
        print("6. Payment")
        print("7. Service/ Repairs")
        print("8. Report")
        print("9. View Service Order")
        print("10. Logout")
        choice = input("Choose an option: ")

        if choice == '1':#Place purchase order
            inventory_purchase_order(username)
        elif choice == '2':#Modify
            inventory_check_purchase_order_status(username)  # Show orders to find the ID
            order_id = int(input("Enter Order ID to modify: "))
            item=str(input("Enter Item Name to modify:"))
            new_quantity = int(input("Enter new quantity: "))
            inventory_modify_order(username, order_id, item, new_quantity)
        elif choice == '3':#Cancel purchase order
            inventory_check_purchase_order_status(username)  # Show orders to find the ID
            order_id = int(input("Enter order ID to cancel: "))
            inventory_cancel_order(username, order_id)
        elif choice == '4':#Check status
            inventory_check_purchase_order_status(username)
        elif choice == '5':#Able to make adjustments with stock
            inventory_stock_check(username, for_staff=False)
        elif choice == '6':#Make payment
            inventory_payment(username)
        elif choice == '7':#Show service/repairs
            service_order(username)
        elif choice == '8':#View reports
            log_action(username,"View Reports")
            staff_view_reports(username)
        elif choice == '9':
            log_action(username,"View Service Orders")
            staff_view_service_orders()
        elif choice == '10':
            log_action(username,"Logout")
            homepage()
        else:
            print("Invalid choice.Please try again.")
            continue
