import firebase_admin
from firebase_admin import credentials, db
from db_config import connect_mariadb  # Import the MariaDB connection function
from firebase_config import init_firebase  # Import Firebase initialization

# Initialize Firebase before using db.reference()
init_firebase()

# Now, we can safely use db.reference()
firebase_ref = db.reference("inventory_log")

from firebase_admin import db

firebase_ref = db.reference("inventory_log")  # Adjust if your Firebase path is different
data = firebase_ref.get()
print("Firebase Data:", data)


# Function to sync Firebase data to MariaDB
def sync_firebase_to_mariadb():
    conn = connect_mariadb()  # Connect to MariaDB
    cursor = conn.cursor()

    inventory_data = firebase_ref.get()

    if inventory_data:
        for product_id, data in inventory_data.items():
            change_type = data.get("change_type", "Added")  # Default "Added"
            quantity_changed = data.get("quantity_changed", 1)  # Default 1

            # Check if product exists in products table
            cursor.execute("SELECT COUNT(*) FROM products WHERE product_id = %s", (product_id,))
            (product_exists,) = cursor.fetchone()

            if product_exists == 0:
                print(f"Skipping {product_id}: Product does not exist in MariaDB.")
                continue  # Skip this product

            # Insert into inventory_log
            sql = """
                INSERT INTO inventory_log (product_id, change_type, quantity_changed)
                VALUES (%s, %s, %s)
            """
            values = (product_id, change_type, quantity_changed)
            cursor.execute(sql, values)
            conn.commit()
            print(f"Synced {product_id} to MariaDB")

    cursor.close()
    conn.close()



# Run script
if __name__ == "__main__":
    sync_firebase_to_mariadb()