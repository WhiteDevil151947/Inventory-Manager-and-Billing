import csv
import os
import datetime
import subprocess

# File paths
INVENTORY_FILE = "inventory.csv"
SALES_FILE = "sales.csv"
CUSTOMERS_FILE = "customers.csv"
BILLS_FOLDER = "bills"

# Ensure necessary files and directories exist
os.makedirs(BILLS_FOLDER, exist_ok=True)

def ensure_file_exists(file_path, headers):
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

ensure_file_exists(INVENTORY_FILE, ["name", "stock", "price"])
ensure_file_exists(SALES_FILE, ["bill_no", "customer_name", "customer_phone", "date", "total", "status"])
ensure_file_exists(CUSTOMERS_FILE, ["name", "phone"])

# Load inventory
def load_inventory():
    inventory = []
    with open(INVENTORY_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            inventory.append({"name": row[0], "stock": int(row[1]), "price": float(row[2])})
    return inventory

# Save inventory
def save_inventory(inventory):
    with open(INVENTORY_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "stock", "price"])
        for item in inventory:
            writer.writerow([item["name"], item["stock"], item["price"]])

# Load customers
def load_customers():
    customers = []
    with open(CUSTOMERS_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            customers.append({"name": row[0], "phone": row[1]})
    return customers

# Save customers
def save_customers(customers):
    with open(CUSTOMERS_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "phone"])
        for customer in customers:
            writer.writerow([customer["name"], customer["phone"]])

# Add a new product
def add_product():
    name = input("Enter product name: ")
    stock = int(input("Enter stock quantity: "))
    price = float(input("Enter product price: "))

    inventory = load_inventory()
    for item in inventory:
        if item["name"].lower() == name.lower():
            item["stock"] += stock
            item["price"] = price
            break
    else:
        inventory.append({"name": name, "stock": stock, "price": price})

    save_inventory(inventory)
    print("✅ Product added/updated successfully!")

# Update product details
def update_product():
    name = input("Enter product name to update: ")
    inventory = load_inventory()

    for item in inventory:
        if item["name"].lower() == name.lower():
            print(f"Current Stock: {item['stock']}, Current Price: {item['price']}")
            new_stock = int(input("Enter new stock: "))
            new_price = float(input("Enter new price: "))
            item["stock"] = new_stock
            item["price"] = new_price
            save_inventory(inventory)
            print("✅ Product updated successfully!")
            return
    
    print("❌ Product not found!")

# View inventory
def view_inventory():
    inventory = load_inventory()
    print("\n========== Inventory ==========")
    print("{:<30} {:<10} {:<10}".format("Product", "Stock", "Price"))
    print("-" * 50)
    for item in inventory:
        print("{:<30} {:<10} {:<10}".format(item["name"], item["stock"], item["price"]))

# Generate a unique bill number
def generate_bill_number():
    return str(int(datetime.datetime.now().timestamp()))

# Save bill and open it
def generate_bill(customer_name, customer_phone, cart, status):
    total = 0
    bill_no = generate_bill_number()
    bill_path = os.path.join(BILLS_FOLDER, f"{bill_no}.txt")

    with open(bill_path, "w") as bill_file:
        bill_file.write(f"==================== MAMTA DAILY NEEDS ====================\n")
        bill_file.write("Address: 123 Main Street, City, Country\n")
        bill_file.write("GSTIN: 123456789\n")
        bill_file.write(f"Bill No: {bill_no}\n")
        bill_file.write(f"Customer Name: {customer_name}\n")
        bill_file.write(f"Customer Phone: {customer_phone}\n")
        bill_file.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        bill_file.write("------------------------------------------------------------\n")

        bill_file.write(f"{'Item':<30} {'Quantity':<10} {'Price':<10} {'Total':<10}\n")
        bill_file.write("-" * 70 + "\n")

        for item in cart:
            item_total = item["price"] * item["quantity"]
            bill_file.write(f"{item['name']:<30} {item['quantity']:<10} {item['price']:<10} {item_total:<10}\n")
            total += item_total

        bill_file.write("-" * 70 + "\n")
        bill_file.write(f"{'Grand Total:':<50} {total}\n")
        bill_file.write(f"{'Payment Status:':<50} {status}\n")
        bill_file.write("==================== THANK YOU! VISIT AGAIN ====================\n")

    with open(SALES_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([bill_no, customer_name, customer_phone, datetime.datetime.now().strftime("%Y-%m-%d"), total, status])

    subprocess.Popen(["notepad", bill_path], shell=True)

# Process sale
def process_sale():
    customer_name = input("Enter customer name: ")
    customer_phone = input("Enter phone number: ")

    inventory = load_inventory()
    cart = []

    while True:
        product_name = input("Enter product name (or 'done' to finish): ")
        if product_name.lower() == "done":
            break

        for item in inventory:
            if item["name"].lower() == product_name.lower():
                quantity = int(input("Enter quantity: "))
                if quantity > item["stock"]:
                    print("❌ Not enough stock available!")
                else:
                    item["stock"] -= quantity
                    cart.append({"name": item["name"], "quantity": quantity, "price": item["price"]})
                    print("✅ Item added to cart.")
                break
        else:
            print("❌ Product not found!")

    if cart:
        status = input("Payment Status (Paid/Unpaid): ").capitalize()
        generate_bill(customer_name, customer_phone, cart, status)
        save_inventory(inventory)

# Find bill
def find_bill():
    search = input("Enter Name, Serial No., Phone, or Date: ").strip()
    with open(SALES_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader, None)

        for row in reader:
            if search.lower() in row[1].lower() or search == row[0] or search == row[2] or search in row[3]:
                bill_file = os.path.join(BILLS_FOLDER, f"{row[0]}.txt")
                if os.path.exists(bill_file):
                    subprocess.Popen(["notepad", bill_file], shell=True)
                    return
                else:
                    print("❌ Bill file missing!")
                    return

    print("❌ No matching bill found!")

# Generate annual report
def generate_annual_report():
    with open(SALES_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader, None)
        total_revenue = sum(float(row[4]) for row in reader)

    inventory = load_inventory()
    total_expense = sum(item["price"] * item["stock"] for item in inventory)
    profit_loss = total_revenue - total_expense

    print("\n========== Annual Report ==========")
    print(f"Total Revenue: {total_revenue}")
    print(f"Total Expense: {total_expense}")
    print(f"Net Profit/Loss: {profit_loss}")

# Add a new customer
def add_customer():
    name = input("Enter customer name: ")
    phone = input("Enter customer phone: ")

    customers = load_customers()
    for customer in customers:
        if customer["phone"] == phone:
            print("❌ Customer already exists!")
            return

    customers.append({"name": name, "phone": phone})
    save_customers(customers)
    print("✅ Customer added successfully!")

# Find a customer
def find_customer():
    search = input("Enter customer name or phone: ").strip()
    customers = load_customers()

    for customer in customers:
        if search.lower() in customer["name"].lower() or search == customer["phone"]:
            print(f"Customer Found: Name: {customer['name']}, Phone: {customer['phone']}")
            return

    print("❌ No matching customer found!")

# Update payment status
def update_payment_status():
    bill_no = input("Enter the bill number to update payment status: ")
    new_status = input("Enter new payment status (Paid/Unpaid): ").capitalize()

    updated = False
    sales_data = []

    with open(SALES_FILE, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        sales_data.append(header)  # Keep the header
        for row in reader:
            if row[0] == bill_no:
                row[5] = new_status  # Update the status
                updated = True
            sales_data.append(row)

    if updated:
        with open(SALES_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(sales_data)
        print("✅ Payment status updated successfully!")
    else:
        print("❌ Bill number not found!")

# Main menu
def menu():
    while True:
        print("\n===== MAMTA DAILY NEEDS =====")
        print("1. Add Product")
        print("2. Update Product")
        print("3. View Inventory")
        print("4. Process Sale")
        print("5. Find Bill")
        print("6. Generate Annual Report")
        print("7. Add Customer")
        print("8. Find Customer")
        print("9. Update Payment Status")
        print("10. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            update_product()
        elif choice == "3":
            view_inventory()
        elif choice == "4":
            process_sale()
        elif choice == "5":
            find_bill()
        elif choice == "6":
            generate_annual_report()
        elif choice == "7":
            add_customer()
        elif choice == "8":
            find_customer()
        elif choice == "9":
            update_payment_status()
        elif choice == "10":
            break

# Run the program
menu()
