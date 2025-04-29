from flask import Blueprint, jsonify
from firebase_connection import fetch_inventory_data

api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/api/fetch_data', methods=['GET'])
def fetch_data():
    data = fetch_inventory_data()
    if not data:
        return jsonify({"error": "No data found in Firebase"}), 404
    return jsonify(data), 200

