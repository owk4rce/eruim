from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from backend.src.config.db import connect_db
from backend.src.routes import api_v1_bp

load_dotenv()
app = Flask(__name__)
CORS(app)
#connect_db(app)
connect_db()

app.register_blueprint(api_v1_bp)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
