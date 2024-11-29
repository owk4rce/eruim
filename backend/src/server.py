from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from backend.src.config.db import connect_db
from backend.src.routes import api_v1_bp
from backend.src.utils.error_handlers import register_error_handlers

load_dotenv()
app = Flask(__name__)
app.url_map.strict_slashes = False  # no need for the end slash in endpoint
CORS(app)

connect_db()

app.register_blueprint(api_v1_bp)
register_error_handlers(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
