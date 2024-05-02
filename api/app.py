from flask import Flask
from api.endpoints import setup_routes

app = Flask(__name__)

# Setup routes
setup_routes(app)

if __name__ == "__main__":
    app.run(debug=True)