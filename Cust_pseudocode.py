START

FUNCTION homepage()
    WHILE True
        OUTPUT "Welcome to KL Central Computer Company (KLCCC)"
        OUTPUT "Please select a role to access to the system"
        OUTPUT "1. Customer"
        OUTPUT "2. Admin"
        OUTPUT "3. Super User"
        OUTPUT "4. Inventory Staff"
        OUTPUT "Please enter your role: "
        INPUT choice
        IF choice == 1 THEN
            SET role = "customer"
            CALL FUNCTION CustomerMenu()
        ELSEIF choice == 2 THEN
            SET role = "admin"
            CALL FUNCTION AdminMenu()
        ELSEIF choice == 3 THEN
            SET role = "super user"
            CALL FUNCTION SuperUserMenu()
        ELSEIF choice == 4 THEN
            SET role = "inventory staff"
            CALL FUNCTION InventoryStaffMenu()
        ELSE
            OUTPUT "Invalid input. Please try again."
        ENDIF
    ENDWHILE
ENDFUNCTION

CALL homepage()

FUNCTION CustomerMenu()
     WHILE True    
         OUTPUT "1. Sign In."
         OUTPUT "2. Register"
         OUTPUT "3. Exit"
         OUTPUT "Please enter your choice: "
         INPUT choice
         IF choice == 1 THEN
             CALL FUNCTION CustomerSignIn()
         ELSEIF choice == 2 THEN
             CALL FUNCTION CustomerSignUp()
         ELSEIF choice == 3 THEN
             CALL FUNCTION homepage()
         ELSE
             OUTPUT "Invalid input. Please try again."
             CALL FUNCTION CustomerMenu()
         ENDIF
     ENDWHILE
ENDFUNCTION

FUNCTION is_user_pending(username, filename)
    OPEN filename AS filehandler IN READ MODE
    IF filehandler FOUND THEN
        FOR each line IN filehandler
            SPLIT line BY comma INTO pending_username
            IF pending_username == username THEN
                RETURN True
            ENDIF
        ENDFOR
    ELSE
        OUTPUT " File not found"
        RETURN False
    ENDIF
    RETURN False
ENDFUNCTION


FUNCTION verify_customer_credentials(username, password, filename)
    OPEN filename AS filehandler IN READ MODE
    IF filehandler FOUND THEN
        FOR each line IN filehandler
            SPLIT line BY comma INTO stored_username AND stored_password
            IF username == stored_username AND password == stored_password THEN
                RETURN True
            ENDIF
        ENDFOR
    ELSE
        OUTPUT " File not found"
        RETURN False
    ENDIF
    RETURN False
ENDFUNCTION

FUNCTION CustomerSignIn()
    SET max_attempts TO 3
    SET attempts TO 0
    
    WHILE attempts IS LESS THAN max_attempts DO
        OUTPUT "Enter Username: "
        INPUT username
        IF is_user_pending(username, "users.txt") THEN
            OUTPUT "Your account is still pending approval. Please wait for confirmation."
            CALL CustomerSignIn()
        ENDIF
        OUTPUT "Enter Password: "
        INPUT password
        IF verify_customer_credentials(username, password, "customers.txt") THEN
            OUTPUT "Login successful!
            CALL log_action(username, "Customer Sign In")
            CALL customer_interface(username)
        ELSE
            INCREMENT attempts BY 1
            OUTPUT "Incorrect username or password. You have " + (max_attempts - attempts) + " attempt(s) left."
        ENDIF
    ENDWHILE
    OUTPUT "Too many failed attempts. Please reset your password."
    CALL reset_customer_password(username, "customers.txt") AS valid, message
    OUTPUT message
ENDFUNCTION

-----

FUNCTION check_username(username, filename)
OPEN filename AS filehandler IN READ MODE
    IF filehandler FOUND THEN
	SET existing_username = []
        FOR each line IN filehandler
            EXTRACT the first part of the line UNTIL the first comma AS stored_username
	    ADD stored_username TO existing_username
	END FOR
            IF username IS IN existing_username THEN
                RETURN True
            ENDIF
    ELSE
        OUTPUT " File not found"
        RETURN False
    ENDIF
    RETURN False
ENDFUNCTION

FUNCTION check_password(password)
    IF LENGTH of password IS LESS THAN 8 THEN
	RETURN False, "Password must be at least 8 characters."
    SET has_upper TO False
    SET has_digit TO False
    SET has_special TO False
    SET special_characters TO "!@#$%^&*_-+=()./?:;\"<>[]{|}"

    FOR each character IN password
        IF character IS  uppercase THEN
            SET has_upper TO True
        ENDIF
        IF character IS a digit THEN
            SET has_digit TO True
        ENDIF
        IF character IS IN special_characters THEN
            SET has_special TO True
        ENDIF
    ENDFOR
    IF has_upper IS False THEN
        RETURN False, "Password must contain at least 1 uppercase letter"
    ENDIF
    IF has_digit IS False THEN
        RETURN False, "Password must contain at least 1 number"
    ENDIF
    IF has_special IS False THEN
        RETURN False, "Password must contain at least 1 special character"
    ENDIF
    RETURN True, "Password is valid"
ENDFUNCTION
    
FUNCTION save_pendingCust(username, password, role, status, filename)
    OPEN filename AS filehandler IN APPEND MODE
    IF filehandler FOUND THEN
        WRITE username, password, role, and status TO filehandler SEPARATED BY commas
    ENDIF
ENDFUNCTION

FUNCTION CustomerSignUp
    WHILE True
        OUTPUT "Create username (At least 4 characters and must contain only alphabetic character)"
        INPUT username
        IF check_username(username, "customers.txt") THEN
            OUTPUT "Username already exists. Please try another one"
        ELSEIF LENGTH of username IS LESS THAN 4 THEN
            OUTPUT "Invalid username. Please try another one"
        ELSEIF username CONTAINS non-alphabetic characters THEN
            OUTPUT "Invalid username. Username must contain only alphabetic characters"
        ELSE
            BREAK
        ENDIF
    ENDWHILE
    
    WHILE True
        OUTPUT "Create password (At least 8 characters, including uppercase letter, number, and special character)"
        INPUT password
        CALL check_password(password) AS valid, message
        IF valid IS False THEN
            OUTPUT message
            CONTINUE
        ENDIF
        OUTPUT "Re-enter password"
        INPUT verify_pw
        IF verify_pw == password THEN
            OUTPUT "Password match"
            OUTPUT "Your registration is pending to be approved"
            SET role TO "customer"
            SET status TO "pending"
            CALL save_pendingCust(username, password, role, status, "users.txt")
            BREAK
        ELSE
            OUTPUT "Passwords do not match. Please try again"
        ENDIF
    ENDWHILE
ENDFUNCTION

FUNCTION reset_customer_password(username, filename)
    WHILE True
        OUTPUT "Password Requirements: At least 8 characters, including uppercase letter, number, and special character"
        OUTPUT "Please enter new password"
        INPUT new_password
        IF LENGTH of new_password IS LESS THAN 8 THEN
            OUTPUT "Password must be at least 8 characters"
            CONTINUE
        ENDIF
        SET has_upper TO False
        SET has_digit TO False
        SET has_special TO False
        SET special_characters TO "!@#$%^&*_-+=()./?:;\"<>[]{|}"
        FOR each character IN new_password
            IF character IS uppercase THEN
                SET has_upper TO True
            ELSEIF character IS a digit THEN
                SET has_digit TO True
            ELSEIF character IS IN special_characters THEN
                SET has_special TO True
            ENDIF
        ENDFOR

        IF has_upper IS False THEN
            OUTPUT "Password must contain at least 1 uppercase letter"
            CONTINUE
        ELSEIF has_digit IS False THEN
            OUTPUT "Password must contain at least 1 number"
            CONTINUE
        ELSEIF has_special IS False THEN
            OUTPUT "Password must contain at least 1 special character"
            CONTINUE
        ENDIF
        
        CALL modify_customer_password(username, new_password, filename) AS success
        IF success IS True THEN
            RETURN True, "Password has been reset successfully"
        ELSE
            RETURN False, "Failed to reset password. Please try again"
        ENDIF
    ENDWHILE
ENDFUNCTION

FUNCTION modify_customer_password(username, new_password, filename)
    SET modified TO False
    SET records = []    
    OPEN filename AS filehandler IN READ MODE
    IF filehandler FOUND THEN
        READ all lines FROM filehandler INTO records
        
        OPEN filename AS filehandler IN WRITE MODE
            FOR each line IN records
                EXTRACT stored_username and stored_password FROM line USING comma as the separator
                IF stored_username == username THEN
                    WRITE username and new_password TO filehandler SEPARATED BY a comma
                    SET modified TO True
                ELSE
                    WRITE the original line TO filehandler
                ENDIF
            ENDFOR
    ELSE
        OUTPUT "No record found"
    ENDIF
    
    RETURN modified
ENDFUNCTION

FUNCTION customer_interface(username)
    WHILE True
        OUTPUT "1. Purchase Order"
        OUTPUT "2. Service/Repair Order"
        OUTPUT "3. Modify Purchase/Service/Repair Order"
        OUTPUT "4. Make payment"
        OUTPUT "5. Inquiry of Order Status"
        OUTPUT "6. Cancel Orders"
        OUTPUT "7. Reports"
        OUTPUT "8. Give feedback"
        OUTPUT "9. Log Out"
        
        OUTPUT "Please select an option to continue with"
        INPUT option
        IF option IS an integer THEN
            IF option == 1 THEN
                CALL place_purchase_order(username) AS order, order_id
            ELSEIF option == 2 THEN
                CALL create_service_order(username)
            ELSEIF option == 3 THEN
                CALL modify_order(username)
            ELSEIF option == 4 THEN
                CALL make_payment(username)
            ELSEIF option == 5 THEN
                CALL inquiry_of_order_status(username)
            ELSEIF option == 6 THEN
                CALL cancel_order(username)
            ELSEIF option == 7 THEN
                CALL customer_reports(username)
            ELSEIF option == 8 THEN
                CALL collect_feedback(username)
            ELSEIF option == 9 THEN
                OUTPUT "Logging out."
                CALL log_action(username, "Customer Log Out")
                CALL homepage()
            ELSE
                OUTPUT "Invalid option. Please try again."
            ENDIF
        ELSE
            OUTPUT "Invalid input. Please try again."
        ENDIF
    ENDWHILE
ENDFUNCTION

FUNCTION generate_order_id
    RETURN "OR" + current date and time in format YearMonthDayHourMinuteSecond
ENDFUNCTION

FUNCTION get_item(item)
    IF item == 1 THEN
        RETURN "Desktop"
    ELSEIF item == 2 THEN
        RETURN "Laptop"
    ELSEIF item == 3 THEN
        RETURN "Mouse"
    ELSEIF item == 4 THEN
        RETURN "Keyboard"
    ELSEIF item == 5 THEN
        RETURN "Monitor"
    ELSEIF item == 6 THEN
        RETURN "Charger"
    ELSE
        RETURN None
    END IF
END FUNCTION

FUNCTION get_item_price(item_name)
    IF item_name == "Desktop" THEN
        RETURN 2500
    ELSEIF item_name == "Laptop" THEN
        RETURN 4000
    ELSEIF item_name == "Mouse" THEN
        RETURN 80
    ELSEIF item_name == "Keyboard" THEN
        RETURN 150
    ELSEIF item_name == "Monitor" THEN
        RETURN 500
    ELSEIF item_name == "Charger" THEN
        RETURN 100
    ELSE
        RETURN 0
    ENDIF
ENDFUNCTION

FUNCTION save_purchase_order(order)
    OPEN "orders.txt" AS filehandler IN APPEND MODE
    IF filehandler FOUND THEN
        SET order_details TO EMPTY STRING
        FOR each item IN order['items']
            CONCATENATE item['name'], item['quantity'], item['price'] AND ADD TO order_details
            CONCATENATE order['order_id'], order['username'], order['status'], order['total_price'], order_details
            WRITE THE CONCATENATED ORDER DETAILS TO filehandler
        ENDFOR
            CLOSE filehandler
    ELSE
        OUTPUT " File not found"
    ENDIF
ENDFUNCTION

FUNCTION place_purchase_order(username)
    order_id = CALL generate_order_id
    SET order_items = []
    SET total_price = 0
    stock = CALL get_stock
    FOR each item IN stock
        IF item is not for staff only THEN
            OUTPUT item index, item name, AND item price
        ENDIF
    ENDFOR
    
    WHILE True
        OUTPUT "Please enter the number of item you want to purchase (Enter '0' to finish)"
        INPUT item
        IF item == 0 THEN
            BREAK WHILE LOOP
        ENDIF
        item_name = CALL get_item(item)
        IF item_name is None THEN
            OUTPUT "Invalid choice, please try again"
            CONTINUE WHILE LOOP
        ENDIF
        OUTPUT "Please enter the quantity: "
        INPUT quantity
        IF quantity <= 0 THEN
            OUTPUT "Quantity must be greater than zero."
            CONTINUE WHILE LOOP
        ENDIF
        item_stock = stock[item_name]
        IF item_stock['quantity'] >= quantity THEN
            ADD item_name, quantity, AND item_stock ['price'] TO order_items
            total_price = item_stock ['price'] * quantity
            DECREASE item_stock['quantity'] by quantity
        ELSE
            OUTPUT "Insufficient stock."
        ENDIF
    ENDWHILE
    
    IF order_items is not empty THEN
        SET status = "Unpaid"
        SET order TO CREATE an order dictionary WITH order_id, username, order_items, total_price, AND status
        CALL save_purchase_order(order)
        OUTPUT "Order placed successfully."
        CALL log_action(username, "Place Purchase Order")
        CALL customer_interface(username)
    ELSE
        OUTPUT "No items added to the order."
    ENDIF
    RETURN order_id, order_items, total_price
END FUNCTION

FUNCTION generate_service_id
    RETURN "SR" + current date and time in format YearMonthDayHourMinuteSecond
ENDFUNCTION

FUNCTION get_service(service_option)
    IF service_option == 1 THEN
        RETURN "Device Repair"
    ELSEIF service_option == 2 THEN
        RETURN "Software Installation"
    ELSEIF service_option == 3 THEN
        RETURN "Hardware Upgrade"
    ELSEIF service_option == 4 THEN
        RETURN "Computer Repair"
    ELSE
        RETURN None
    ENDIF
ENDFUNCTION

FUNCTION get_service_price(service_name)
    IF item_name == "Device Repair" THEN
        RETURN 100
    ELSEIF item_name == "Software Installation" THEN
        RETURN 200
    ELSEIF item_name == "Hardware Upgrade" THEN
        RETURN 250
    ELSEIF item_name == "Computer Repair" THEN
        RETURN 250
    ELSE
        RETURN 0
    ENDIF
ENDFUNCTION

FUNCTION save_service_order(order)
    OPEN "service_orders.txt" AS filehandler IN APPEND MODE
    IF filehandler FOUND THEN
        SET services_str = EMPTY STRING
        FOR each service IN order['services']
            CONCATENATE service['name'], service['price'] AND ADD TO services_str
        ENDFOR
        CONCATENATE order['service_id'], order['username'], order['status'], order['total_price'], services_str
        WRITE THE CONCATENATED ORDER DETAILS TO filehandler
        CLOSE filehandler
    ELSE
        OUTPUT "File not found"
    ENDIF
ENDFUNCTION

FUNCTION create_service_order(username)
    service_id = CALL generate_service_id
    SET service_items = []
    SET total_price = 0
    services = CALL load_data(SERVICE_ORDERS_FILE)
    FOR each service AND details IN services
        DISPLAY service INDEX, service NAME, AND details['tentative_time']
        DISPLAY "Price: RM" AND details['service_price']
    ENDFOR
    
    WHILE True
        OUTPUT "Please select the service you want to request (Enter '0' to finish)"
        INPUT service_option
        IF service_option == 0 THEN
            BREAK WHILE LOOP
        ENDIF
        service_name = CALL get_service(service_option)
        IF service_name IS None THEN
            DISPLAY "Invalid choice, please try again"
            CONTINUE WHILE LOOP
        ENDIF
        IF ANY SERVICE IN service_items HAS service['name'] == service_name THEN
            OUTPUT "This service has been added to your order."
            CONTINUE WHILE LOOP
        ENDIF
        service_details = services.get(service_name)
        IF service_details EXISTS THEN
            ADD service_name, service_details['service_price'], service_details['tentative_time'] TO service_items
            total_price = service_details['service_price']
            DISPLAY "Added service to your order."
        ENDIF
    ENDWHILE
    IF service_items IS NOT EMPTY THEN
        status = "Unpaid"
        order = CREATE AN ORDER DICTIONARY WITH service_id, username, service_items, total_price, AND status
        CALL save_service_order(order)
        DISPLAY "Service Order placed successfully."
        CALL log_action(username, "Place Service/Repair Order")
        CALL customer_interface(username)
    ELSE
        DISPLAY "No service added to the order."
    ENDIF
    RETURN service_id, service_items, total_price
END FUNCTION

FUNCTION load_orders_details(filename)
    OPEN filename AS filehandler IN READ MODE
    IF filehandler FOUND THEN
        SET data TO EMPTY DICTIONARY
        WHILE NOT END OF FILE
            READ LINE FROM filehandler
            SET order_id TO PART BEFORE FIRST SEMICOLON
            REMOVE PART BEFORE FIRST SEMICOLON AND SEMICOLON FROM LINE
            SET username TO PART BEFORE FIRST SEMICOLON
            REMOVE PART BEFORE FIRST SEMICOLON AND SEMICOLON FROM LINE
            SET status TO PART BEFORE FIRST SEMICOLON
            REMOVE PART BEFORE FIRST SEMICOLON AND SEMICOLON FROM LINE
            SET total_price TO PART BEFORE FIRST SEMICOLON
            REMOVE PART BEFORE FIRST SEMICOLON AND SEMICOLON FROM LINE
            SET items_str TO LINE

            SET items TO EMPTY LIST
            WHILE items_str IS NOT EMPTY
                SET item_part TO PART BEFORE FIRST SEMICOLON
                REMOVE PART BEFORE FIRST SEMICOLON AND SEMICOLON FROM items_str
                SET item_details TO PART SPLIT BY COMMA
                SET item_name TO FIRST PART
                SET item_price TO SECOND PART
                SET item_quantity TO 1
                IF item_details HAS MORE THAN 2 PARTS THEN
                    SET item_quantity TO THIRD PART
                ENDIF
                ADD item_name, item_quantity, AND item_price TO items
            ENDWHILE

            SET data[order_id] TO DICTIONARY WITH username, status, total_price, AND items
        ENDWHILE
        CLOSE filehandler
        RETURN data
    ELSE
        OUTPUT "File not found."
        RETURN EMPTY DICTIONARY
    ENDIF
ENDFUNCTION

FUNCTION display_order_details(username)
    SET purchase_orders TO CALL load_order_details('orders.txt')
    SET service_orders TO CALL load_order_details('service_orders.txt')
    FOR each order_id AND order IN purchase_orders
        IF order['username'] == username THEN
            OUTPUT "Order ID: " + order_id + ", Status: " + order['status'] + ", Total Price: RM" + order['total_price'] + ", Items: " + order['items']
        ENDIF
    END FOR

    FOR each order_id AND order IN service_orders
        IF order['username'] EQUALS username THEN
            OUTPUT "Order ID: " + order_id + ", Status: " + order['status'] + ", Total Price: RM" + order['total_price'] + ", Services: " + order['items']
        ENDIF
    END FOR
END FUNCTION

FUNCTION modify_order(username)
    SET user_purchase_orders, user_service_orders TO CALL display_order_details(username)
    IF user_purchase_orders IS EMPTY AND user_service_orders IS EMPTY THEN
        OUTPUT "You have no orders to modify."
    ENDIF

    WHILE True
        OUTPUT "1. Modify Purchase Order"
        OUTPUT "2. Modify Service/Repair Order"
        OUTPUT "3. Exit"
        INPUT choice
        IF choice == 1 THEN
            SET order_file TO 'orders.txt'
            SET orders TO user_purchase_orders
            SET modify_type TO "item"
        ELSEIF choice == 2 THEN
            SET order_file TO 'service_orders.txt'
            SET orders TO user_service_orders
            SET modify_type TO "service"
        ELSEIF choice == 3 THEN
            OUTPUT "Exiting modification menu."
            CALL customer_interface(username)
        ELSE
            OUTPUT "Invalid choice. Please try again."
            CONTINUE WHILE LOOP
        ENDIF

        IF orders IS empty THEN
            OUTPUT "You have no orders of this type."
            CONTINUE WHILE LOOP
        ENDIF
        OUTPUT "Order Summary:"
        FOR each order_id AND order IN orders
            OUTPUT "Order ID: " + order_id + ", Status: " + order['status'] + ", Total Price: RM" + order['total_price']
            OUTPUT "Items: " + CONCATENATE ITEMS
        ENDFOR

        OUTPUT "Enter the Order ID you want to modify: "
        INPUT order_id
        IF order_id NOT IN orders THEN
            OUTPUT "Invalid Order ID."
            CONTINUE WHILE LOOP
        ENDIF

        IF orders[order_id]['status'] == 'paid' THEN
            OUTPUT "Order cannot be modified as it has been paid."
            CONTINUE WHILE LOOP
        ENDIF

        WHILE True
            OUTPUT "1. Add " + modify_type
            OUTPUT "2. Remove " + modify_type
            OUTPUT "3. Finish modification"
            INPUT option
            IF option == 1 THEN
                IF modify_type == "item" THEN
                    SET stock TO CALL get_stock()
                    OUTPUT "Available Items:"
                    FOR each item AND details IN stock
                        IF details['for_staff_only'] IS False THEN
                            OUTPUT item_name AND details['price']
                        ENDIF
                    ENDFOR
                    WHILE True
                        OUTPUT "Please enter the number of item you want to add (Enter '0' to finish): "
                        INPUT item_choice
                        IF item_choice EQUALS 0 THEN
                            BREAK WHILE LOOP
                        ENDIF
                        SET item_name TO CALL get_item(item_choice)
                        IF item_name IS None THEN
                            OUTPUT "Invalid choice, please try again"
                            CONTINUE WHILE LOOP
                        ENDIF
                        OUTPUT "Enter quantity"
                        INPUT quantity
                        IF quantity <= 0 THEN
                            OUTPUT "Quantity must be greater than zero."
                            CONTINUE WHILE LOOP
                        ENDIF
                        SET item_stock TO stock[item_name]
                        IF item_stock['quantity'] >= quantity THEN
                            ADD item_name, quantity, AND item_stock['price'] TO orders[order_id]['items']
                            INCREASE orders[order_id]['total_price'] BY item_stock['price'] * quantity
                            DECREASE item_stock['quantity'] BY quantity
                            CALL save_orders(order_file, orders)
                            OUTPUT "Order has been modified successfully."
                            CALL log_action(username, "Modify Purchase Order - Add Item")
                        ELSE
                            OUTPUT "Insufficient stock."
                        ENDIF
                    ENDWHILE
                ELSEIF modify_type == "service" THEN
                    SET services TO CALL load_data(SERVICE_ORDERS_FILE)
                    OUTPUT "Available Service/Repair Option:"
                    FOR each service AND details IN services
                        OUTPUT service_name AND details['service_price']
                    ENDFOR
                    WHILE True
                        INPUT service_option
                        IF service_option == 0 THEN
                            BREAK WHILE LOOP
                        ENDIF
                        SET service_name TO CALL get_service(service_option)
                        IF service_name IS None THEN
                            OUTPUT "Invalid choice, please try again"
                            CONTINUE WHILE LOOP
                        ENDIF
                        IF ANY service IN orders[order_id]['items'] HAS 'name' EQUAL TO service_name THEN
                            OUTPUT "This service has been added to your order."
                            CONTINUE WHILE LOOP
                        ENDIF
                        SET service_details TO services[service_name]
                        IF service_details EXISTS THEN
                            ADD service_name, service_details['service_price'], AND service_details['tentative_time'] TO orders[order_id]['items']
                            INCREASE orders[order_id]['total_price'] BY service_details['service_price']
                            OUTPUT "Added service to your order."
                            CALL save_orders(order_file, orders)
                            OUTPUT "Order has been modified successfully."
                            CALL log_action(username, "Modify Service/Repair Order - Add Service")
                        ENDIF
                    ENDWHILE
                ENDIF
            ELSEIF option == 2 THEN
                IF modify_type == "item" THEN
                    OUTPUT "Enter item name to remove: "
                    INPUT item_name
                    SET item_to_remove TO None
                    FOR each item IN orders[order_id]['items']
                        IF item['name'] == item_name THEN
                            SET item_to_remove TO item
                            BREAK
                        ENDIF
                    ENDFOR
                    IF item_to_remove EXISTS THEN
                        REMOVE item_to_remove FROM orders[order_id]['items']
                        DECREASE orders[order_id]['total_price'] BY item_to_remove['price']
                        CALL save_orders(order_file, orders)
                        OUTPUT "Item removed"
                        CALL log_action(username, "Modify Purchase Order - Remove Item")
                    ELSE
                        OUTPUT "Item not found in the order."
                    ENDIF
                ELSEIF modify_type == "service" THEN
                    OUTPUT "Enter the service name to remove: "
                    INPUT service_name
                    SET service_to_remove TO None
                    FOR each service IN orders[order_id]['items']
                        IF service['name'] == service_name THEN
                            SET service_to_remove TO service
                            BREAK
                        ENDIF
                    ENDFOR
                    IF service_to_remove EXISTS THEN
                        REMOVE service_to_remove FROM orders[order_id]['items']
                        DECREASE orders[order_id]['total_price'] BY service_to_remove['price']
                        CALL save_orders(order_file, orders)
                        OUTPUT "Service removed."
                        CALL log_action(username, "Modify Service/Repair Order - Remove Service")
                    ELSE
                        OUTPUT "Service not found in the order."
                    ENDIF
                ENDIF
            ELSEIF option == 3 THEN
                CALL customer_interface(username)
            ELSE
                OUTPUT "Invalid choice. Please try again."
            ENDIF
        ENDWHILE
ENDFUNCTION

FUNCTION save_orders(filename, order)
    OPEN filename AS filehandler IN WRITE MODE
    IF filehandler FOUND THEN
        FOR each order_id AND order IN orders
            IF filename IS 'orders.txt' THEN
                SET items_str TO EMPTY STRING
                FOR each item IN order['items']
                    CONCATENATE item['name'], ",", item['quantity'], ",", item['price'] AND ADD TO items_str
                    CONCATENATE ";" AND ADD TO items_str
                ENDFOR
                REMOVE LAST CHARACTER ";" FROM items_str
            ELSEIF filename IS 'service_orders.txt' THEN
                SET items_str TO EMPTY STRING
                FOR each service IN order['items']
                    CONCATENATE service['name'], ",", service['price'] AND ADD TO items_str
                    CONCATENATE ";" AND ADD TO items_str
                ENDFOR
                REMOVE LAST CHARACTER ";" FROM items_str
            ELSE
                OUTPUT "Unsupported file type."
                CLOSE filehandler
                RETURN
            ENDIF

            CONCATENATE order_id, ";", order['username'], ";", order['status'], ";", order['total_price'], ";", items_str AND STORE IN line
            WRITE line TO filehandler
        ENDFOR
        CLOSE filehandler
    ELSE
        OUTPUT "File not found."
    ENDIF
ENDFUNCTION

FUNCTION make_payment(username)
    CALL check_order_details(username) AS user_purchase_orders AND user_service_orders

    SET orders_to_pay = {}

    FOR each order_id AND order IN user_purchase_orders
        IF order['status'] IS NOT 'paid' THEN
            ADD order_id AND order TO orders_to_pay
        ENDIF
    ENDFOR

    FOR each order_id AND order IN user_service_orders
        IF order['status'] IS NOT 'paid' THEN
            ADD order_id AND order TO orders_to_pay
        ENDIF
    ENDFOR

    IF orders_to_pay IS EMPTY THEN
        OUTPUT "You have no unpaid orders to pay for."
    ENDIF

    OUTPUT "Your unpaid orders:"
    FOR each order_id AND order IN orders_to_pay
        OUTPUT "Order ID: " + order_id + ", Total Price: RM" + order['total_price']
    ENDFOR

    OUTPUT "Enter the Order ID you want to pay for:"
    INPUT order_id

    IF order_id IS IN orders_to_pay THEN
        SET orders_to_pay[order_id]['status'] TO 'paid'
        CALL save_orders('orders.txt', user_purchase_orders)
        CALL save_orders('service_orders.txt', user_service_orders)
        OUTPUT "Order has been paid successfully."
        CALL generate_invoice(username)
        CALL log_action(username, "Make Payment")
    ELSE
        OUTPUT "Invalid Order ID."
    ENDIF
ENDFUNCTION

FUNCTION inquiry_of_order_status(username)
    CALL log_action(username, "Inquiry of Order Status")
    CALL check_order_details(username) AS user_purchase_orders AND user_service_orders

    IF user_purchase_orders IS EMPTY AND user_service_orders IS EMPTY THEN
        OUTPUT "Order Status Inquiry:"
        OUTPUT "You have no orders to inquire about."
    ENDIF

    IF user_purchase_orders IS NOT EMPTY THEN
        OUTPUT "Purchase Orders:"
        FOR each order_id AND order IN user_purchase_orders
            OUTPUT "Order ID: " + order_id
            OUTPUT "Status: " + order['status']
            OUTPUT "Total Price: RM" + order['total_price']
            OUTPUT "Items:"
            FOR each item IN order['items']
                OUTPUT " - " + item['name'] + " (RM" + item['price'] + ")"
            ENDFOR
        ENDFOR
    ELSE
        OUTPUT "No purchase orders found."
    ENDIF

    IF user_service_orders IS NOT EMPTY THEN
        OUTPUT "Service/Repair Orders:"
        FOR each order_id AND order IN user_service_orders
            OUTPUT "Order ID: " + order_id
            OUTPUT "Status: " + order['status']
            OUTPUT "Total Price: RM" + order['total_price']
            OUTPUT "Services:"
            FOR each item IN order['items']
                OUTPUT " - " + item['name'] + " (RM" + item['price'] + ")"
            ENDFOR
        ENDFOR
    ELSE
        OUTPUT "No service/repair orders found."
    ENDIF
ENDFUNCTION

FUNCTION cancel_order(username)
    CALL check_order_details(username) AS user_purchase_orders AND user_service_orders
    SET orders_to_cancel = {}

    FOR each order_id AND order IN user_purchase_orders
        IF order['status'] IS NOT 'paid' THEN
            ADD order_id AND order TO orders_to_cancel
        ENDIF
    ENDFOR

    FOR each order_id AND order IN user_service_orders
        IF order['status'] IS NOT 'paid' THEN
            ADD order_id AND order TO orders_to_cancel
        ENDIF
    ENDFOR

    IF orders_to_cancel IS EMPTY THEN
        OUTPUT "You have no unpaid orders to cancel."
        RETURN
    ENDIF

    OUTPUT "Your unpaid orders:"
    FOR each order_id AND order IN orders_to_cancel
        OUTPUT "Order ID: " + order_id + ", Total Price: RM" + order['total_price']
    ENDFOR

    OUTPUT "Enter the Order ID you want to cancel: "
    INPUT order_id
    IF order_id EXISTS IN orders_to_cancel THEN
        IF order_id EXISTS IN user_purchase_orders THEN
            REMOVE order_id FROM user_purchase_orders
            CALL save_orders('orders.txt', user_purchase_orders)
        ELSE IF order_id EXISTS IN user_service_orders THEN
            REMOVE order_id FROM user_service_orders
            CALL save_orders('service_orders.txt', user_service_orders)
        ENDIF
        CALL log_action(username, "Cancel Order")
        OUTPUT "Order has been canceled successfully."
    ELSE
        OUTPUT "Invalid Order ID."
    ENDIF
ENDFUNCTION

FUNCTION customer_reports(username)
    CALL log_action(username, "Generate Customer Report")
    CALL load_data(REPORTS_FILE) AS reports
    SET user_reports AS reports.GET(username, EMPTY_LIST)

    IF user_reports IS EMPTY THEN
        OUTPUT "No reports found for user: " + username
    ELSE
        OUTPUT "Reports:"
        OUTPUT "     Date    |  Time  |       Actions"
        FOR EACH action IN user_reports
            OUTPUT " - " + action['time'] + ": " + action['action']
        ENDFOR
    ENDIF
ENDFUNCTION

FUNCTION collect_feedback(username)
    OUTPUT "Please provide your feedback."
    SET rating TO None
    While rating IS None
        OUTPUT "Rate our service (1-5): "
        INPUT rating
        IF rating IS INTEGER THEN
            IF rating < 1 OR rating > 5 THEN
                OUTPUT "Please enter a number between 1 and 5."
                SET rating TO None
            ENDIF
        ELSE
            OUTPUT "Invalid input. Please try again."
        ENDIF
    ENDWHILE

    OUTPUT "Please leave your comments: "
    INPUT comments

    SET feedback TO DICTIONARY WITH
        'username' AS username,
        'rating' AS rating
        'comments' AS comments,
        'date' AS CURRENT DATE AND TIME

    OPEN 'feedback.json' AS filehandler IN READ MODE
    IF file FOUND THEN
        SET feedback_data TO CONTENTS OF 'feedback.json'
        APPEND feedback TO feedback_data
        SAVE feedback_data TO 'feedback.json'
    ELSE
        OUTPUT "File not found"
    ENDIF

    OUTPUT "Thank you for your feedback!"
    CALL log_action(username, "Give Feedback")
