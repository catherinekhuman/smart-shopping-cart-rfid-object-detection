from flask import Flask
from flask_cors import CORS
from app_routes import app_routes

app = Flask(__name__)
app.secret_key = '1b2a3c4d5e6f7a8b9c0d1e2f3a4b5c6d'
CORS(app)

# Register Blueprints
app.register_blueprint(app_routes)

if __name__ == "__main__":
    app.run(debug=True)

