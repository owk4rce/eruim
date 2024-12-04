from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman

from backend.src.config.config import load_config
from backend.src.config.db import connect_db
from backend.src.routes import api_v1_bp
from backend.src.utils.error_handlers import register_error_handlers
from backend.src.utils.exceptions import UserError

app = Flask(__name__)

try:
    config = load_config()
    app.config.update(config)
except Exception as e:
    print(f"Initialization Error: {str(e)}")
    exit(1)

app.url_map.strict_slashes = False  # no need for the end slash in endpoint

CORS(app)
jwt = JWTManager(app)


@jwt.unauthorized_loader
def custom_unauthorized_response(err_msg):
    return jsonify({
        "error": "Authentication required",
        "message": err_msg
    }), 401


@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    return jsonify({
        "error": "Token has expired",
        "message": "Please log in again."
    }), 401


@jwt.invalid_token_loader
def custom_invalid_token_response(err_msg):
    return jsonify({
        "error": "Invalid token",
        "message": f"Token error: {err_msg}"
    }), 422


if app.config["DEBUG"]:
    Talisman(
        app,
        force_https=False,  # позволяет HTTP в разработке
        content_security_policy=None  # отключаем CSP для разработки
    )
else:
    # В production включаем все защиты
    Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy={
            'default-src': "'self'",
            'img-src': '*',
            'script-src': "'self'"
        }
    )

connect_db(app)

app.register_blueprint(api_v1_bp)
register_error_handlers(app)

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=5000)
