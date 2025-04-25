import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from db_config import connect_mariadb
from firebase_config import firebase_ref

GPIO.setwarnings(False)
reader = SimpleMFRC522()

def scan_product():
    """Reads RFID tag and adds the product to the cart."""
    conn = connect_mariadb()
    cursor = conn.cursor()

    print("Place your tag to scan...")
    try:
        tag_id, _ = reader.read()
        tag_id = str(tag_id)

        cursor.execute("SELECT product_id, name, price, quantity FROM products WHERE rfid_tag=%s", (tag_id,))
        result = cursor.fetchone()

        if result:
            product_id, product_name, product_price, product_qty = result
            print(f"Product: {product_name} | Price: {product_price} | Available: {product_qty}")

            if product_qty > 0:
                cursor.execute("INSERT INTO cart (product_id, user_id, quantity) VALUES (%s, %s, %s)", 
                               (product_id, 1, 1))  # Assuming user_id = 1
                conn.commit()

                firebase_ref.child(str(product_id)).update({"quantity": product_qty - 1})
                print(f"{product_name} added to cart. Remaining quantity: {product_qty - 1}")
            else:
                print(f"{product_name} is out of stock!")

        else:
            print("Product not found.")

    finally:
        conn.close()
        GPIO.cleanup()

def register_product():
    """Writes an RFID tag with product data and stores it in MySQL & Firebase."""
    conn = connect_mariadb()
    cursor = conn.cursor()

    product_name = input("Enter Product Name: ").strip()
    product_price = float(input("Enter Price: ").strip())
    product_qty = int(input("Enter quantity: ").strip())

    print("Place your tag to write...")
    try:
        reader.write(product_name)
        print("RFID Written Successfully!")

        tag_id, _ = reader.read()
        tag_id = str(tag_id)

        cursor.execute("INSERT INTO products (rfid_tag, name, price, quantity) VALUES (%s, %s, %s, %s)", 
                       (tag_id, product_name, product_price, product_qty))
        product_id = cursor.lastrowid  # Get the auto-incremented product_id
        conn.commit()

        firebase_ref.child(str(product_id)).set({
            "name": product_name,
            "price": product_price,
            "quantity": product_qty
        })
        print(f"Product {product_name} added to MySQL & Firebase.")

    finally:
        conn.close()
        GPIO.cleanup()

if __name__ == "__main__":
    action = input("Enter 'scan' to scan a product or 'register' to register a new product: ").strip().lower()
    if action == "scan":
        scan_product()
    elif action == "register":
        register_product()
    else:
        print("Invalid option!")