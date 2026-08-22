ORDERS_FILE = "orders.txt"
CUST_SERVICE_ORDERS_FILE = "service_orders.txt"

def generate_service_id():
    #%Y = Year, full version
    #%m = Month as a number 01-12
    #%d = Day of month 01-31
    #%H = Hour 00-23
    #%M = Minute 00-59
    #%S = Second 00-59
    return "SR" + datetime.now().strftime("%Y%m%d%H%M%S")

def generate_order_id():
    #%Y = Year, full version
    #%m = Month as a number 01-12
    #%d = Day of month 01-31
    #%H = Hour 00-23
    #%M = Minute 00-59
    #%S = Second 00-59
    return "OR" + datetime.now().strftime("%Y%m%d%H%M%S")

def get_item(item):
    if item == 1:
        return "Desktop"
    elif item == 2:
        return "Laptop"
    elif item == 3:
        return "Mouse"
    elif item == 4:
        return "Keyboard"
    elif item == 5:
        return "Monitor"
    elif item == 6:
        return "Charger"
    else:
        return None
    
def get_item_price(item_name):
    if item_name == "Desktop":
        return 2500
    elif item_name == "Laptop":
        return 4000
    elif item_name == "Mouse":
        return 80
    elif item_name == "Keyboard":
        return 150
    elif item_name == "Monitor":
        return 500
    elif item_name == "Charger":
        return 100
    else:
        return 0

def save_purchase_order(order):
    with open("orders.txt", "a") as file:
        items_str = ';'.join([f"{item['name']},{item['quantity']},{item['price']:.2f}" for item in order['items']])
        file.write(f"{order['order_id']};{order['username']};{order['status']};{order['total_price']:.2f};{items_str}\n")

def place_purchase_order(username):
    order_id = generate_order_id()
    order_items = []
    total_price = 0
    stock = get_stock()
    print("****************************************************************************************")
    print("                                     Available Items")
    print("****************************************************************************************\n")
    for idx, (item, details) in enumerate(stock.items(), start=1):
        if details.get('for_staff_only') == False:
            print(f"{idx}. {item}")
            print(f"   Price: RM{details['price']:.2f}")
    while True:
        try:
            item = int(input("Please enter the number of item you want to purchase (Enter '0' to finish): "))
            
            if item == 0:
                break
            
            item_name = get_item(item)
            if item_name is None:
                print("Invalid choice, please try again")
                continue  
            
            quantity = int(input(f"Please enter the quantity for {item_name}: "))
            
            if quantity <= 0:
                print("Quantity must be greater than zero.")
                continue
            
            item_stock = stock[item_name]
            
            if item_stock['quantity'] >= quantity:
                order_items.append({
                    "name": item_name,
                    "quantity": quantity,
                    "price": item_stock['price'] * quantity
                })
                total_price += item_stock['price'] * quantity
                item_stock['quantity'] -= quantity
                print(f"Added {quantity} {item_name}(s) to your order.")
            else:
                print(f"Insufficient stock for {item_name}. Only {item_stock['quantity']} available.")
        
        except ValueError:
            print("Invalid input. Please enter a number.")

    if order_items:
        order = {
            "order_id": order_id,
            "username": username,
            "items": order_items,
            "total_price": total_price,
            "status": "Unpaid"
        }
        save_purchase_order(order)
        print(f"Order {order_id} placed successfully.")
        log_action(username, "Place Purchase Order")
        customer_interface(username)
    else:
        print("No items added to the order.") 
    return order_id, order_items, total_price

def get_service(service_option):
    if service_option == 1:
        return "Device Repair"
    elif service_option == 2:
        return "Software Installation"
    elif service_option == 3:
        return "Hardware Upgrade"
    elif service_option == 4:
        return "Computer Repair"
    else:
        return None

def get_service_price(service_name, services):
    return services[service_name]['service_price']

def save_service_order(order):
    with open("service_orders.txt", "a") as file:
        services_str = ';'.join([f"{service['name']},{service['price']:.2f}" for service in order['services']])
        file.write(f"{order['service_id']};{order['username']};{order['status']};{order['total_price']:.2f};{services_str}\n")

def create_service_order(username):
    service_id = generate_service_id()
    service_items = []
    total_price = 0
    services = load_data(SERVICE_ORDERS_FILE)
    print("****************************************************************************************")
    print("                             Availabe Service/Repair Option")
    print("****************************************************************************************\n")
    for idx,(service, details) in enumerate(services.items(),start=1):
        print(f"{idx}. {service} : {details['tentative_time']}")
        print(f"   Price: RM{details['service_price']:.2f}")
    
    while True:
        try:
            service_option = int(input("Please selecgt the service you want to request (Enter '0' to finish): "))

            if service_option == 0:
                break

            service_name = get_service(service_option)
            if service_name is None:
                print("Invalid choice, please try again")
                continue

            if any(service['name'] == service_name for service in service_items):
                print(f"{service_name} has already been added to your order.")
                continue


            service_details = services.get(service_name)
            if service_details:
                service_items.append({
                    "name": service_name,
                    "price": service_details["service_price"],
                    "tentative_time": service_details["tentative_time"]
                })
            total_price += service_details["service_price"]
            print(f"Added {service_name} to your order.")
        except ValueError:
            print("Invalid input. Please enter a number")
    
    if service_items:
        order = {
            "service_id": service_id,
            "username": username,
            "services": service_items,
            "total_price": total_price,
            "status": "Unpaid"
        }
        save_service_order(order)
        print(f"Service Order {service_id} placed successfully.")
        log_action(username, "Place Service/Repair Order")
        customer_interface(username)
    else:
        print("No service added to the order.")
    return service_id, service_items, total_price

def load_orders_details(filename):
    orders = {}
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(";")
                if len(parts) < 4:
                    print(f"Skipping malformed line: {line}")
                    continue
                
                order_id = parts[0]
                try:
                    orders[order_id] = {
                        'username': parts[1],
                        'status': parts[2],
                        'total_price': float(parts[3]),
                        'items': []
                    }
                    for item in parts[4:]:
                        item_parts = item.split(",")
                        if len(item_parts) == 2:  # For services
                            item_name = item_parts[0]
                            item_price = float(item_parts[1])
                            orders[order_id]['items'].append({
                                'name': item_name,
                                'price': item_price
                            })
                        elif len(item_parts) == 3:  # For items
                            item_name = item_parts[0]
                            quantity = int(item_parts[1])
                            item_price = float(item_parts[2])
                            orders[order_id]['items'].append({
                                'name': item_name,
                                'quantity': quantity,
                                'price': item_price
                            })
                        else:
                            print(f"Skipping malformed item: {item}")
                except ValueError as e:
                    print(f"Error parsing line {line}: {e}")
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error loading orders: {e}")
    return orders

def save_orders(filename, orders):
    try:
        with open(filename, "w") as file:
            for order_id, order in orders.items():
                if filename == 'orders.txt':
                    items_str = ";".join([
                        f"{item['name']},{item['quantity']},{item['price']:.2f}"
                        for item in order['items']
                    ])
                elif filename == 'service_orders.txt': 
                    items_str = ";".join([
                        f"{item['name']},{item['price']:.2f}"
                        for item in order['items']
                    ])
                else:
                    raise ValueError("Unsupported file type.")
                
                line = f"{order_id};{order['username']};{order['status']};{order['total_price']:.2f};{items_str}\n"
                print(f"Writing to file: {line}")
                file.write(line)
    except Exception as e:
        print(f"An error occurred while saving orders: {e}")

def check_order_details(username):
    purchase_orders = load_orders_details('orders.txt')
    service_orders = load_orders_details('service_orders.txt')

    user_purchase_orders = {order_id: order for order_id, order in purchase_orders.items() if order['username'] == username}
    user_service_orders = {order_id: order for order_id, order in service_orders.items() if order['username'] == username}

    return user_purchase_orders, user_service_orders

def modify_order(username):
    user_purchase_orders, user_service_orders = check_order_details(username)

    if not user_purchase_orders and not user_service_orders:
        print("You have no orders to modify.")
        return

    while True:
        print("****************************************************************************************")
        print("                          Modify Purchase/Service/Repair Order")
        print("****************************************************************************************\n")
        print("1. Modify Purchase Order")
        print("2. Modify Service/Repair Order")
        print("3. Exit")
        try:
            choice = int(input("Please enter what type of order that you want to modify: "))
            if choice == 1:
                order_file = 'orders.txt'
                orders = user_purchase_orders
                modify_type = "item"
            elif choice == 2:
                order_file = 'service_orders.txt'
                orders = user_service_orders
                modify_type = "service"
            elif choice == 3:
                print("Exiting modification menu.")
                return
            else:
                print("Invalid choice. Please try again.")
                continue
        except ValueError:
            print("Invalid choice. Please try again.")
            continue

        if not orders:
            print("You have no orders of this type.")
            continue

        print("****************************************************************************************")
        print("                                     Order Summary")
        print("****************************************************************************************\n")
        for order_id, order in orders.items():
            print(f"Order ID: {order_id}, Status: {order['status']}, Total Price: RM{order['total_price']:.2f}")
            for item in order['items']:
                print(f" - {item['name']} (RM{item['price']:.2f})")

        order_id = input("Enter the Order ID you want to modify: ")
        if order_id not in orders:
            print("Invalid Order ID.")
            continue

        if orders[order_id]['status'] == 'paid':
            print("Order cannot be modified as it has already been paid.")
            continue

        while True:
            print("1. Add " + modify_type)
            print("2. Remove " + modify_type)
            print("3. Finish modification")
            try:
                option = int(input("Please enter your choice: "))
                if option == 1:
                    if modify_type == "item":
                        stock = get_stock()
                        print("****************************************************************************************")
                        print("                                     Available Items")
                        print("****************************************************************************************\n")
                        for idx, (item, details) in enumerate(stock.items(), start=1):
                            if not details.get('for_staff_only', False):
                                print(f"{idx}. {item}")
                                print(f"   Price: RM{details['price']:.2f}")
                        while True:
                            try:
                                item_choice = int(input("Please enter the number of item you want to add (Enter '0' to finish): "))
                                if item_choice == 0:
                                    break
                                item_name = get_item(item_choice)
                                if item_name is None:
                                    print("Invalid choice, please try again")
                                    continue  
            
                                quantity = int(input(f"Please enter the quantity for {item_name}: "))
                                if quantity <= 0:
                                    print("Quantity must be greater than zero.")
                                    continue
            
                                item_stock = stock[item_name]
            
                                if item_stock['quantity'] >= quantity:
                                    orders[order_id]['items'].append({
                                        "name": item_name,
                                        "quantity": quantity,
                                        "price": item_stock['price'] * quantity
                                    })
                                    orders[order_id]['total_price'] += item_stock['price'] * quantity
                                    item_stock['quantity'] -= quantity
                                    save_orders(order_file, orders)
                                    print(f"Order {order_id} has been modified successfully.")
                                    log_action(username, "Modify Purchase Order - Add Item")
                                else:
                                    print(f"Insufficient stock for {item_name}. Only {item_stock['quantity']} available.")
                            except ValueError:
                                print("Invalid input. Please enter a number.")
                    elif modify_type == "service":
                        services = load_data(SERVICE_ORDERS_FILE)
                        print("****************************************************************************************")
                        print("                             Available Service/Repair Option")
                        print("****************************************************************************************\n")
                        for idx, (service, details) in enumerate(services.items(), start=1):
                            print(f"{idx}. {service} : {details['tentative_time']}")
                            print(f"   Price: RM{details['service_price']:.2f}")
    
                        while True:
                            try:
                                service_option = int(input("Please select the service you want to request (Enter '0' to finish): "))

                                if service_option == 0:
                                    break

                                service_name = get_service(service_option)
                                if service_name is None:
                                    print("Invalid choice, please try again")
                                    continue

                                if any(service['name'] == service_name for service in orders[order_id]['items']):
                                    print(f"{service_name} has already been added to your order.")
                                    continue

                                service_details = services.get(service_name)
                                if service_details:
                                    orders[order_id]['items'].append({
                                        "name": service_name,
                                        "price": service_details["service_price"],
                                        "tentative_time": service_details["tentative_time"]
                                    })
                                    orders[order_id]['total_price'] += service_details["service_price"]
                                    print(f"Added {service_name} to your order.")
                                    save_orders(order_file, orders)
                                    print(f"Order {order_id} has been modified successfully.")
                                    log_action(username, "Modify Service/Repair Order - Add Service")
                            except ValueError:
                                print("Invalid input. Please enter a number")

                elif option == 2:
                    if modify_type == "item":
                        item_name = input(f"Enter the name of the {modify_type} to remove: ")
                        item_to_remove = None
                        for item in orders[order_id]['items']:
                            if item['name'] == item_name:
                                item_to_remove = item
                                break
                        if item_to_remove:
                            orders[order_id]['items'].remove(item_to_remove)
                            orders[order_id]['total_price'] -= item_to_remove['price']
                            print(f"{item_name} removed from the order.")
                            log_action(username, "Modify Purchase Order - Remove Item")
                        else:
                            print(f"{item_name} not found in the order.")
                    elif modify_type == "service":
                        service_name = input(f"Enter the name of the {modify_type} to remove: ")
                        service_to_remove = None
                        for service in orders[order_id]['items']:
                            if service['name'] == service_name:
                                service_to_remove = service
                                break
                        if service_to_remove:
                            orders[order_id]['items'].remove(service_to_remove)
                            orders[order_id]['total_price'] -= service_to_remove['price']
                            print(f"{service_name} removed from the order.")
                            save_orders(order_file, orders)
                            print(f"Order {order_id} has been modified successfully.")
                            log_action(username, "Modify Service/Repair Order - Remove Service")
                        else:
                            print(f"{service_name} not found in the order.")
                elif option == '3':
                    customer_interface(username)
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

def generate_invoice(username):
    user_purchase_orders, user_service_orders = check_order_details(username)
    if not user_purchase_orders and not user_service_orders:
        print("No orders found for generating an invoice.")
        return
    print("**********************************************************************")
    print("                            INVOICE")
    print("**********************************************************************")
    total_amount = 0.0
    
    if user_purchase_orders:
        print("                            Purchase Orders")
        print("-----------------------------------------------------------------------")
        for order_id, order in user_purchase_orders.items():
            print(f"Order ID: {order_id}")
            for idx, item in enumerate(order['items'], start=1):
                item_details = f"{idx}. {item['name']}"
                if 'quantity' in item:
                    item_details += f" (Quantity: {item['quantity']})"
                item_details += f" - Price: RM{item['price']:.2f}"
                print(f"   {item_details}")
            total_amount += order['total_price']

    elif user_service_orders:
        print("                                 Service/Repair Orders")
        print("-----------------------------------------------------------------------\n")
        for order_id, order in user_service_orders.items():
            print(f"Order ID: {order_id}")
            for idx, service in enumerate(order['items'], start=1):
                print(f"{idx}. {service['name']}")
                if 'tentative_time' in service:
                    print(f"   Tentative Time: {service['tentative_time']}")
                print(f"   Price: RM{service['price']:.2f}")
            total_amount += order['total_price']

    print("-----------------------------------------------------------------------\n")
    print(f"               Total Amount Due: RM{total_amount:.2f}")
    print("-----------------------------------------------------------------------\n")
    print("                Thank you for your payment!")
    print("***********************************************************************")

def make_payment(username):
    user_purchase_orders, user_service_orders = check_order_details(username)

    orders_to_pay = {}

    for order_id, order in user_purchase_orders.items():
        if not order['status'] == 'paid':
            orders_to_pay[order_id] = order

    for order_id, order in user_service_orders.items():
        if not order['status'] == 'paid':
            orders_to_pay[order_id] = order

    if not orders_to_pay:
        print("You have no unpaid orders to pay for.")

    print("Your unpaid orders:")
    for order_id, order in orders_to_pay.items():
        print(f"Order ID: {order_id}, Total Price: RM{order['total_price']:.2f}")

    order_id = input("Enter the Order ID you want to pay for: ")
    if order_id in orders_to_pay:
        orders_to_pay[order_id]['status'] = 'paid'
        save_orders('orders.txt', user_purchase_orders)
        save_orders('service_orders.txt', user_service_orders)
        print(f"Order {order_id} has been paid successfully.")
        generate_invoice(username)
        log_action(username, "Make Payment")
    else:
        print("Invalid Order ID.")

def inquiry_of_order_status(username):
    log_action(username, "Inquiry of Order Status")
    user_purchase_orders, user_service_orders = check_order_details(username)
    print("****************************************************************************************")
    print("                           Order Status Inquiry")
    print("****************************************************************************************\n")

    if not user_purchase_orders and not user_service_orders:
        print("You have no orders to inquire about.")

    if user_purchase_orders:
        print("Purchase Orders:")
        for order_id, order in user_purchase_orders.items():
            print(f"\nOrder ID: {order_id}")
            print(f"Status: {order['status']}")
            print(f"Total Price: RM{order['total_price']:.2f}")
            print("Items:")
            for item in order['items']:
                print(f" - {item['name']} (RM{item['price']:.2f})")
    else:
        print("No purchase orders found.")

    if user_service_orders:
        print("\nService/Repair Orders:")
        for order_id, order in user_service_orders.items():
            print(f"\nOrder ID: {order_id}")
            print(f"Status: {order['status']}")
            print(f"Total Price: RM{order['total_price']:.2f}")
            print("Services:")
            for item in order['items']:
                print(f" - {item['name']} (RM{item['price']:.2f})")
    else:
        print("No service/repair orders found.")

def cancel_order(username):
    user_purchase_orders, user_service_orders = check_order_details(username)

    orders_to_cancel = {}

    for order_id, order in user_purchase_orders.items():
        if not order['status'] == 'paid':
            orders_to_cancel[order_id] = order

    for order_id, order in user_service_orders.items():
        if not order['status'] == 'paid':
            orders_to_cancel[order_id] = order

    if not orders_to_cancel:
        print("You have no unpaid orders to cancel.")
        return

    print("Your unpaid orders:")
    for order_id, order in orders_to_cancel.items():
        print(f"Order ID: {order_id}, Total Price: RM{order['total_price']:.2f}")

    order_id = input("Enter the Order ID you want to cancel: ")
    if order_id in orders_to_cancel:
        if order_id in user_purchase_orders:
            del user_purchase_orders[order_id]
            save_orders('orders.txt', user_purchase_orders)
        elif order_id in user_service_orders:
            del user_service_orders[order_id]
            save_orders('service_orders.txt', user_service_orders)
        log_action(username, "Cancel Order")
        print(f"Order {order_id} has been canceled successfully.")
    else:
        print("Invalid Order ID.")

def customer_reports(username):
    log_action(username, "Generate Customer Report")
    reports = load_data(REPORTS_FILE)
    user_reports = reports.get(username, [])
    if not user_reports:
        print(f"No reports found for user: {username}.")
    else:
        print(f"\nReports for {username}:")
        print("     Date    |  Time  |       Actions")
        for action in user_reports:
            print(f" - {action['time']}: {action['action']}")

    input("\nPress Enter to return to the main menu...")

def collect_feedback(username):
    print("Please provide your feedback.")
    
    rating = None
    while rating is None:
        try:
            rating = int(input("Rate our service (1-5): "))
            if rating < 1 or rating > 5:
                print("Please enter a number between 1 and 5.")
                rating = None
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")
    
    comments = input("Please leave your comments: ")

    feedback = {
        'username': username,
        'rating': rating,
        'comments': comments,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    feedback_data = load_data('feedback.json')
    feedback_data["feedback"].append(feedback)
    save_data(feedback_data, 'feedback.json')
    
    print("Thank you for your feedback!")
    log_action(username, "Give Feedback")

def customer_interface(username):
    while True:
        print("\n****************************************************************************************")
        print("                                      Customer Menu")
        print("****************************************************************************************\n")
        print("1. Purchase Order")
        print("2. Service/Repair Order")
        print("3. Modify Purchase/Service/Repair Order")
        print("4. Make payment")
        print("5. Inquiry of Order Status")
        print("6. Cancel Orders")
        print("7. Reports")
        print("8. Give feedback")
        print("9. Log Out")
        try:
            option = int(input("Please select an option to continue with: "))
            if option == 1:
                order, order_id = place_purchase_order(username)
            elif option == 2:
                create_service_order(username)
            elif option == 3:
                modify_order(username)
            elif option == 4:
                make_payment(username)
            elif option == 5:
                inquiry_of_order_status(username)
            elif option == 6:
                cancel_order(username)
            elif option == 7:
                customer_reports(username)
            elif option == 8:
                collect_feedback(username)
            elif option == 9:
                print("Logging out.")
                log_action(username, "Customer Log Out")
                homepage()
            else:
                print("Invalid option. Please try again.")
        except ValueError:
            print("Invalid input. Please try again.")

def reset_customer_password(username, filename):
    print("****************************************************************************************")
    print("                                     Reset Password")
    print("****************************************************************************************\n")
    while True:
        print("Password Requirements: At least 8 characters, including uppercase letter, number, and special character")
        new_password = input("Please enter new password: ")
        
        if len(new_password) < 8:
            print("Password must be at least 8 characters.")
            continue
    
        has_upper = any(char.isupper() for char in new_password)
        has_digit = any(char.isdigit() for char in new_password)
        special_characters = "!@#$%^&*_-+=()./?:;\"<>[]{|}"
        has_special = any(char in special_characters for char in new_password)

        if not has_upper:
            print("Password must contain at least 1 uppercase letter.")
            continue
        if not has_digit:
            print("Password must contain at least 1 number.")
            continue
        if not has_special:
            print("Password must contain at least 1 special character.")
            continue
        
        success = modify_customer_password(username, new_password, filename)
        if success:
            return True, "Password has been reset successfully."
        else:
            return False, "Failed to reset password. Please try again."

def modify_customer_password(username, new_password, filename):
    modified = False
    records = []
    try:
        with open(filename, "r") as file:
            records = file.readlines()
        
        with open(filename, "w") as file:
            for line in records:
                stored_username, stored_password = line.strip().split(",")
                if stored_username == username:
                    file.write(f"{username},{new_password}\n")
                    modified = True
                else:
                    file.write(line)
    except FileNotFoundError:
        print("No record found.")
    
    return modified

def verify_customer_credentials(username, password, filename):
    try:
        with open(filename, "r") as file:
            for line in file.readlines():
                stored_username, stored_password = line.strip().split(",")

                if username == stored_username and password == stored_password:
                    return True
    except FileNotFoundError:
        return False
    return False

def is_user_pending(username, filename):
    try:
        with open(filename, "r") as file:
            for line in file:
                pending_username = line.strip().split(",")[0]
                if pending_username == username:
                    return True
    except FileNotFoundError:
        return False
    return False

def CustomerSignIn():
    print("****************************************************************************************")
    print("                                  Customer Log In Page")
    print("****************************************************************************************\n")
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        username = input("Enter Username: ")
        if is_user_pending(username, "users.txt"):
            print("Your account is still pending approval. Please wait for confirmation.")
            CustomerMenu()
        password = input("Enter Password: ")
        if verify_customer_credentials(username, password, "customers.txt"):
            print(f"Login successful! Welcome, {username}")
            log_action(username, "Customer Sign In")
            customer_interface(username)
        else:
            attempts += 1
            print(f"Incorrect username or password. You have {max_attempts - attempts} attempt(s) left.")
    
    print("Too many failed attempts. Please reset your password.")
    valid, message = reset_customer_password(username, "customers.txt")
    print(message)
    
def check_username(username, filename):
    try:
        with open(filename, "r") as file:
            existing_username = [line.strip().split(",")[0] for line in file.readlines()]
            if username in existing_username:
                return True
    except FileNotFoundError:
        return False
    return False

def check_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    special_characters = "!@#$%^&*_-+=()./?:;\"<>[]{|}"
    has_special = any(char in special_characters for char in password)

    if not has_upper:
        return False, "Password must contain at least 1 uppercase letter."
    if not has_digit:
        return False, "Password must contain at least 1 number."
    if not has_special:
        return False, "Password must contain at least 1 special character."
    return True, "Password is valid"

def save_pendingCust(username, password, role, status, filename):
    with open(filename, "a") as file:
        file.write(f"{username},{password},{role},{status}\n")

def CustomerSignUp():
    print("****************************************************************************************")
    print("                                    Create an account")
    print("****************************************************************************************\n")
    while True:
        username = input("Create username (At least 4 characters and must contain only alphabetic character): ")
        if check_username(username, "customers.txt"):
            print("Username already exists. Please try another one.")
        elif len(username) < 4:
            print("Invalid username. Please try another one.")
        elif not username.isalpha():
            print("Invalid username. Username must contain only alphabetic character.")
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
            print("Password match")
            print("Your registration is pending to be approved.")
            
            role = "customer"
            status = "pending"

            save_pendingCust(username, password, role, status, "users.txt")
            break
        else:
            print("Password do not match. Please try again.")

def CustomerMenu():
    while True:
        print("****************************************************************************************")
        print("                                        SIGN IN/SIGN UP")
        print("****************************************************************************************\n")
        print("Dear customer, do you have an account?")
        print("1. Yes, I would like to SIGN IN.")
        print("2. No, I would like to REGISTER for an account.")
        print("3. Exit")
        try:
            choice = int(input("Please enter your choice: "))
            if choice == 1:
                CustomerSignIn()
            elif choice == 2:
                CustomerSignUp()
            elif choice == 3:
                homepage()
            else:
                print("Invalid input. Please try again.")
                CustomerMenu()
        except ValueError:
            print("Invalid input. Please try again.")

def homepage():
    while True:
        print("****************************************************************************************")
        print("                 Welcome to KL Central Computer Company (KLCCC) website")
        print("****************************************************************************************\n")
        print("Please select a role to access to the system")
        print("1. Customer")
        print("2. Admin")
        print("3. Super User")
        print("4. Inventory Staff")
        try:
            role = int(input("Please enter your role: "))
            if role == 1:
                role = "customer"
                CustomerMenu()
            elif role == 2:
                role = "admin"
                AdminMenu()
            elif role == 3:
                role = "super user"
                SuperUserMenu()
            elif role == 4:
                role = "inentory staff"
                InventoryStaffMenu()
            else:
                print("Invalid input. Please try again.")
        except ValueError:
            print("Invalid input. Please try again.")

#SuperUserLoginPage
def create_SuperUser_data():
    SuperUser_data=[
        'superuser,superpass'
        ]
    with open('SuperUser.txt','w') as file:
        for line in SuperUser_data:
            file.write(line + '\n')
    print("Super User data file created with initial data.")

def SuperUser_login():
    max_attempts=3
    attempts=0

    while attempts<max_attempts:
        print("\n****************************")
        print("      Super User Login      ")
        print("****************************")
        print("Enter Super User ID: ")
        superuser_id = input()
        print("Enter Password: ")
        password = input()

        valid_login=False

        try:
            with open('SuperUser.txt', 'r') as file:
                for line in file:
                    stored_superuser_id, stored_password = line.strip().split(',')
                    if stored_superuser_id == superuser_id and stored_password == password:
                        valid_login=True
                        break
        except FileNotFoundError:
            print("User data file not found.")
            return
        except ValueError:
            print("Error reading user data file.")
            return

        if valid_login:
            print("Login successful.")
            SuperUser_menu()
            return
        else:
            attempts +=1
            print(f"Invalid credentials. You have {max_attempts-attempts} attempts left.")

    print("Too many failed attempts. Access denied.")

#Verify_New_Users

def Verify_New_Users():
    try:
        with open('users.txt', 'r')as file:
            users=file.readlines()
    except FileNotFoundError:
        print("No users to verify.")
        return
        
    pending_users=[user for user in users if "pending" in user]

    if not pending_users:
        print("No pending users to verify.")
        return

    for i, user in enumerate(pending_users, start=1):
        username, password, ic, role, status=user.strip().split(',')
        print(f"{i}. Username: {username}, \nPassword:{password},\nIdentity Card:{ic}, \nRole: {role}, \nStatus: {status}")

    with open('users.txt', 'w') as file:
        file.writelines(users)


#Add_User

def Add_User():
    try:
        with open('users.txt', 'r') as file:
            users=file.readlines()
    except FileNotFoundError:
        print("No users found.")
        return

    pending_users=[user for user in users if "pending" in user]

    if not pending_users:
        print("No pending users to add.")
        return

    for i, user in enumerate(pending_users, start=1):
        username, password, ic, role, status=user.strip().split(',')
        print(f"{i}. Username: {username}, Role: {role}, Status: {status}")

        while True:
            decision=input("Approve (A) or Reject (R) this user? ").strip().upper()
            if decision in ['A', 'R']:
                break
            print("Invalid choice. Please enter 'A' to approve or 'R' to reject.")

        if decision=='A':
            users[users.index(user)]=f"{username},{password},{ic},{role},approved\n"
            print(f"User {username} approved.")
        else:
            users[users.index(user)]=f"{username},{password},{ic},{role},rejected\n"
            print(f"User {username} rejected.")

#Modify_User_Details

def Modify_User_Details():
    try:
        with open('user.txt', 'r') as file:
            users=file.readlines()
    except FileNotFoundError:
        print("No users found.")
        return
    
    print("****************************")
    print("     Modify User Details    ")
    print("****************************")
    for i, user in enumerate(users, start=1):
        user_id, pw, role, status=user.strip().split(',')
        print(f"(i). Username: {username}, Password:{password}Role: {role}, Status: {status}")

    user_choice=int(input("Select the user number to modify: "))

    if 1 <= user_choice <= len(users):
        selected_user=users[user_choice -1]
        username, password, role, status=selected_user.strip().spilt(',')

        new_user_id=input(f"Enter new User ID (leave blank to keep '{username}'): ") or username
        new_password=input(f"Enter new Password (leave blank to keep current password): ") or password
        new_role=input(f"Enter new Role (Admin/Inventory Staff, leave blank to keep '{role}'): ") or role

        users[user_choice -1]=f"{new_user_id},{new_pw}, {new_role},{status}\n"
        with open('users.txt', 'w') as file:
            file.writelines(users)

        print(f"User {username} details have been updated.")
    else:
        print("Invalid user selection.")

#Disable_User_Access

def Disable_User_Access():
    try:
        with open('users.txt', 'r') as file:
            users=file.read.readlines()
    except FileNotFoundError:
        print("No users found.")
        return

    print("****************************")
    print("    Disable User Access     ")
    print("****************************")
    for i, user in enumerate(users, start=1):
        user_id, pw, role, status=user.strip().spilt(',')
        print(f"{i}. Username: {username}, Role: {role}, Status: {status}")

    user_choice=int(input("Select the user number to disable: "))

    if 1 <= user_choice <= len(users):
        selected_user=user[user_choice -1]
        user_id, pw, role, status=selected_user.strip().split(',')

        if status=="disabled":
            print(f"Username {username} is already disabled.")
        else:
            print("Invalid user selection.")

        with open('users.txt', 'w') as file:
            file.writelines(users)

#SuperUserMenu

def SuperUser_menu():
    while True:
        print("****************************")
        print("      Super User Menu       ")
        print("****************************")
        print("1. Add User")
        print("2. Approve/Reject User Registrations")
        print("3. Modify User Personal Details")
        print("4. Disable User Access")
        print("5. Inquiry of User's System Usage")
        print("6. Check Customer Order Status")
        print("7. View Reports")
        print("8. Logout")
        choice=input("Choose an option: ")

        if choice=='1':
            print("Add User")
            Add_User()

        elif choice=='2':
            print("Approve/Reject User Registration")
            Verify_New_Users()

        elif choice=='3':
            print("Modify User Personal Details")
            Modify_User_Details()

        elif choice=='4':
            print("Disable User Access")
            Disable_User_Access()

        elif choice=='5':
            print("Inquiry of User's System Usage")

        elif choice=='6':
            print("Check Customer Order Status")

        elif choice=='7':
            print("View Reports")

        elif choice=='8':
            print("Logout")
            break   

#Inventory Part
import json
from datetime import datetime

# File paths
STOCK_FILE = 'stock.json'
PURCHASED_ITEMS_FILE = 'purchased_items.json'
NEWSTAFF_FILE='newuser.json'
REPORTS_FILE = 'reports.json'
SERVICE_ORDERS_FILE = 'service_orders.json'

def log_action(username, action):
    """Log actions performed by users."""
    reports = load_data(REPORTS_FILE)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if username not in reports:
        reports[username] = []
    
    reports[username].append({
        'time': current_time,
        'action': action
    })
    
    save_data(reports, REPORTS_FILE)

def StaffLogIn():
    max_attempts=3
    attempts=0
    print("\n*******************************")
    print("  Inventory Staff Log In Page  ")
    print("*******************************")
    while True:
        username = input("\nEnter Username: ")
        password = input("Enter Password: ")
        if verify_Staffcredentials(username, password, "staff.txt"):
            print(f"Login successful! Welcome, {username}")
            staff_menu(username)
        else:
            attempts+=1
            print(f"Invalid credentials. You have {max_attempts-attempts} attempts left.")
            if attempts==3:
                print("Too many failed attempts. Access denied")
                #rolemenu()
                

def verify_Staffcredentials(username, password, filename):
    try:
        with open(filename, "r") as file:
            for line in file.readlines():
                stored_username, stored_password = line.strip().split(",")

                if username == stored_username and password == stored_password:
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
        password = input("Create password (At least 8 characters): ")
        if len(password) < 8:
            print("Invalid password. Please try again.")
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
    
def check_username(username, filename):
    try:
        with open(filename, "r") as file:
            existing_username = [line.strip().split(",")[0] for line in file.readlines()]
            if username in existing_username:
                return True
    except FileNotFoundError:
        return False
    return False

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

    if not load_data(NEWSTAFF_FILE):
        save_data([], NEWSTAFF_FILE)

def save_new_user(username, password, ic, role):
    #Save a record of new users
    new_user = load_data(NEWSTAFF_FILE)
    new_user.append({'Username': username, 'Password': password,'IC': ic,'Role': role})
    save_data(new_user, NEWSTAFF_FILE)

def update_stock(item, quantity):
    """Update stock levels in the stock file."""
    stock = load_data(STOCK_FILE)
    
    if item in stock:
        stock[item]['quantity'] += quantity
        save_data(stock, STOCK_FILE)
        print(f"\nStock updated: {item} now has {stock[item]['quantity']} units.")
    else:
        print("Invalid item for stock update.")

def save_purchase_record(order_items, total_cost, status):
    # Save a record of the purchased items
    orders = load_data(PURCHASED_ITEMS_FILE)
    orders.append({'items': order_items, 'total_cost': total_cost, 'status': status})
    save_data(orders, PURCHASED_ITEMS_FILE)

def get_stock():
    #Retrieve current stock levels
    return load_data(STOCK_FILE)

def inventory_modify_order(order_id, item, new_quantity):
    """Modify the quantity of a specific item in an existing purchase order."""
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
        
        save_data(orders, PURCHASED_ITEMS_FILE)
        
        print(f"Order {order_id} modified.")
        print(f"Item: {item}")
        print(f"Old Quantity: {old_quantity}, New Quantity: {new_quantity}")
        print(f"New Total Cost for Item: RM{item_to_modify['total_cost']:.2f}")
        print(f"New Total Cost for Order: RM{order['total_cost']:.2f}")
    else:
        print("Invalid order ID.")
    log_action(username, "Stock Check - Modify Purchase Order")


def inventory_cancel_order(username, order_id):
    """Cancel an existing purchase order."""
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

##PURCHASE ORDER CAN BE USED BY CUSTOMER
def inventory_purchase_order(username):
    """Function for inventory staff to place a purchase order."""
    stock = get_stock()

    print("\n--------Available Items for Inventory Staff--------")
    # Display items with their index, quantity, and price
    for idx, (item, details) in enumerate(stock.items(), start=1):
        print(f"{idx}. {item}")
        print(f"    Quantity: {details['quantity']}")
        print(f"    Price: RM{details['price']:.2f}")

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
            
            # Check if requested quantity is available
            if quantity > stock[item]['quantity']:
                print(f"Insufficient stock for {item}. Available: {stock[item]['quantity']}.")
                continue

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
        save_purchase_record(order_items, total_cost, status)  # Save the purchase record

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
    

def inventory_check_purchase_order_status(username):
    """List all purchase orders with their IDs."""
    try:
        orders = load_data(PURCHASED_ITEMS_FILE)
        
        if not orders:
            print("No orders found.")
        else:
            print("Purchase orders:")
            for index, order in enumerate(orders, start=1):
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
    log_action(username, "Check Purchase Order Status")

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

def inventory_payment(username):#if status =paid nid go where???
    try:
        orders = load_data(PURCHASED_ITEMS_FILE)
        if not orders:
            print("No orders found. No payment needed.")
        else:
            print("Purchase orders:")
            for index, order in enumerate(orders, start=1):
                status = "Paid" if order.get('paid', False) else "Unpaid"
                total_cost = order.get('total_cost', '')  # Safely get the total cost
                print(f"Order ID: {index}, Item: {order['item']}, Quantity: {order['quantity']}, Price: {total_cost}, Status: {status}")

            payment = int(input("Select your Order ID: "))
            if 1 <= payment <= len(orders):
                selected_order = orders[payment - 1]
                answer = input("Do you want to make payment (Y for Yes, N for No): ").strip().upper()
                if answer == 'Y':
                    selected_order['paid'] = True
                    save_data(orders, PURCHASED_ITEMS_FILE)  # Save the updated orders
                    print("Payment successful. Order marked as Paid.")
                elif answer == 'N':
                    print("Payment not completed. Order remains Unpaid.")
                else:
                    print("Invalid input. Please try again.")
            else:
                print("Invalid Order ID.")
    except Exception as e:
        print(f"An error occurred while processing payment: {e}")
    log_action(username, "Make Payment")

def view_reports(username):
    """View the action logs (reports)."""
    reports = load_data(REPORTS_FILE)
    
    if not reports:
        print("No reports found.")
    else:
        for username, actions in reports.items():
            print(f"\nReports:")
            print(f"Username: {username}")
            print("     Date    |  Time  |       Actions")
            for action in actions:
                print(f" - {action['time']}: {action['action']}")

    input("\nPress Enter to return to the main menu...")

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
        print("9. Logout")
        choice = input("Choose an option: ")

        if choice == '1':
            inventory_purchase_order(username)
        elif choice == '2':
            inventory_check_purchase_order_status(username)  # Show orders to find the ID
            order_id = int(input("Enter order ID to modify: "))
            item=str(input("Enter Item Name to modify:"))
            new_quantity = int(input("Enter new quantity: "))
            inventory_modify_order(order_id, item, new_quantity)
        elif choice == '3':
            inventory_check_purchase_order_status(username)  # Show orders to find the ID
            order_id = int(input("Enter order ID to cancel: "))
            inventory_cancel_order(username, order_id)
        elif choice == '4':#without Price
            inventory_check_purchase_order_status(username)
        elif choice == '5':#Able to Add, Remove, Update details of item
            inventory_stock_check(username, for_staff=False)
        elif choice == '6':
            inventory_payment(username)
        elif choice == '7':
            service_order(username)
        elif choice == '8':
            view_reports(username)
        elif choice == '9':
            log_action(username,"Logout")
            homepage()
        else:
            print("Invalid choice.Please try again.")
            continue

homepage()
