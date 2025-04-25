import firebase_admin
from firebase_admin import credentials, db

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(r"/home/cathe/Desktop/smartshoppingcart/firebase-key.json")

        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://smart-shopping-cart-652f2-default-rtdb.asia-southeast1.firebasedatabase.app'
        })

        print("Firebase initialized successfully!")

init_firebase()

firebase_ref = db.reference("inventory_log")

def add_product(product_id, name, quantity, price):
    firebase_ref.child(product_id).set({
        "name": name,
        "quantity": quantity,
        "price": price
    })
    print(f"Added {name} to Firebase.")

# Run only if this script is executed directly
if __name__ == "__main__":
    add_product("prod_001", "Milk", 10, 2.5)
    add_product("prod_002", "Maggi", 3, 5)