import firebase_admin
from firebase_admin import credentials, db
from db_config import connect_mariadb
from firebase_config import init_firebase

init_firebase()

firebase_ref = db.reference("inventory_log")

from firebase_admin import db

firebase_ref = db.reference("inventory_log")  
data = firebase_ref.get()
print("Firebase Data:", data)


def sync_firebase_to_mariadb():
    conn = connect_mariadb() 
    cursor = conn.cursor()

    inventory_data = firebase_ref.get()

    if inventory_data:
        for product_id, data in inventory_data.items():
            change_type = data.get("change_type", "Added")  # Default "Added"
            quantity_changed = data.get("quantity_changed", 1)  # Default 1

            # Check if product exists in the products table
            cursor.execute("SELECT COUNT(*) FROM products WHERE product_id = %s", (product_id,))
            (product_exists,) = cursor.fetchone()

            if product_exists == 0:
                print(f"Skipping {product_id}: Product does not exist in MariaDB.")
                continue

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


if __name__ == "__main__":
    sync_firebase_to_mariadb()
