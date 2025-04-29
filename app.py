from flask import Flask
from flask_cors import CORS
from app_routes import app_routes

app = Flask(__name__)
app.secret_key = ' '
CORS(app)

# Register Blueprints
app.register_blueprint(app_routes)

if __name__ == "__main__":
    app.run(debug=True)

