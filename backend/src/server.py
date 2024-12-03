from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend.src.config.config import load_config
from backend.src.config.db import connect_db
from backend.src.routes import api_v1_bp
from backend.src.utils.error_handlers import register_error_handlers

try:
    app = Flask(__name__)
    config = load_config()
    app.config.update(config)
    app.url_map.strict_slashes = False  # no need for the end slash in endpoint

    CORS(app)
    jwt = JWTManager(app)

    connect_db(app)

    app.register_blueprint(api_v1_bp)
    register_error_handlers(app)
except Exception as e:
    print(f"Initialization Error: {str(e)}")
    exit(1)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

    # if __name__ == '__main__':
    #     app.run(debug=app.config["DEBUG"], port=5000)
