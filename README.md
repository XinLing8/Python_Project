# Python_Project
# KL Central Computer Company (KLCCC) Management System

**Programming with Python (AAPP015-4-1-PWP)**  
**Intake Code:** UCDF2308ICT(SE)

## 📘 Project Overview

This project is an automated sales and inventory management system developed as part of our Diploma coursework for the **Programming with Python** module. The primary focus of the project is designing and implementing a robust Python-based solution for the KL Central Computer Company (KLCCC) to manage their rapidly expanding computer sales and repair operations.

The system replaces manual processes with an efficient, role-based application that handles multiple user levels, data validation, and automated transactions. It demonstrates our practical application of core Python programming concepts, including:
*   Control structures and error handling
*   Data structures (lists, dictionaries)
*   File handling (reading/writing to external files for persistent data storage)
*   Modular programming (custom functions for specific tasks)
*   String manipulation and complex input validation (e.g., password security enforcement)

## 👥 Group Members

This group assignment was completed collaboratively by the following team members:
*   **Yap Xin Ling** (TP077057)
*   **Yeo Pei Wen** (TP077224)
*   **Sim Tian** (TP077056)

*Lecturer: Amardeep Singh A/L Uttam Singh*

## ✨ System Features

The system is designed with distinct functionalities tailored to different user roles:
*   **Super User / Admin:** Manage system access, approve or reject user registrations, view comprehensive reports, and review customer feedback.
*   **Inventory Staff:** Place, modify, and cancel purchase orders, perform stock checks and inventory adjustments, process payments, and manage service/repair orders.
*   **Customers:** Securely sign up and log in, place orders, check purchase and service order statuses, and leave service feedback.
*   **Security & Authentication:** Includes secure login, user registration pending states, and a robust password reset function enforcing strict complexity rules (minimum 8 characters, uppercase, number, and special character).

## 🗂️ Assignment Documentation Outline

The full project report includes the detailed logic and execution of the system, structured as follows:

1. **Introduction:** Overview of KLCCC's business needs and the Python solution.
2. **Assumptions:** System boundaries, user role definitions, and operational rules.
3. **Source Code with Explanation:** Detailed breakdowns of core system functions, including:
   * Authentication & Authorization (`check_password`, `verify_credentials`, `CustomerSignUp`)
   * Order & Inventory Management (`update_stock`, `modify_order`, `cancel_order`, `save_purchase_order`)
   * Service & Payments (`create_service_order`, `make_payment`, `generate_invoice`)
   * Reporting and Menus (`customer_reports`, `staff_view_reports`)
4. **Additional Features:** 
   * Advanced Password Reset handling (`reset_staff_password`, `reset_customer_password`)
   * Customer Feedback system (`collect_feedback`, `view_all_feedback`)
5. **Example of Input and Output:** UI walkthroughs of the system interfaces (Main Menu, Super User Menu, Inventory Staff Menu, Customer Menu).
6. **Conclusion:** Summary of project outcomes, the importance of system design, and lessons learned.
7. **References**

## 📚 Project Description

The KLCCC Management System addresses the challenges of tracking high volumes of sales and repairs manually. By utilizing Python, we built a modular and scalable text-based application that efficiently manages interactions between customers and company staff. 

Extensive planning went into the system's design phase, including the creation of detailed pseudocode and flowcharts to outline the logical steps before coding began. The implementation phase focused on writing accurate, clean, and well-documented Python code capable of handling potential user errors gracefully (such as invalid inputs or forgotten passwords) to ensure a smooth, effortless experience for all users.

## 📄 Note

This is an academic group project submitted to the Asia Pacific University of Technology & Innovation (APU). Please refer to the full assignment document for detailed flowcharts, pseudocode, and complete source code explanations.
