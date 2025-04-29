from flask import Blueprint, render_template, jsonify
from firebase_connection import fetch_inventory_data

app_routes = Blueprint('app_routes', __name__)

# SPLASH PAGE
@app_routes.route('/')
def splash():
    return render_template('start.html')

# MAIN CART PAGE
@app_routes.route('/cart')
def index():
    return render_template('index.html')

@app_routes.route('/app/fetch_data', methods=['GET'])
def fetch_data():
    try:
        data = fetch_inventory_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app_routes.route('/total_amount')
def total_amount():
    try:
        data = fetch_inventory_data()
        total = 0
        all_products = []

        for item in data:
            try:
                quantity = int(item.get('quantity', 0))  # using 'quantity'
                price = float(item.get('price', 0))
                total += price * quantity
                all_products.append(item)
            except:
                continue

        # Use your own QR code stored in static
        return render_template('total_amount.html', total=total, items=all_products)

    except Exception as e:
        return render_template('total_amount.html', total=0, items=[], error=str(e))
