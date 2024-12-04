from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman

from backend.src.config.config import load_config
from backend.src.config.db import connect_db
from backend.src.routes import api_v1_bp
from backend.src.utils.error_handlers import register_error_handlers
from backend.src.utils.exceptions import UserError

try:
    app = Flask(__name__)
    config = load_config()
    app.config.update(config)
    app.url_map.strict_slashes = False  # no need for the end slash in endpoint

    CORS(app)
    jwt = JWTManager(app)


    @jwt.expired_token_loader
    def handle_expired_token(_jwt_header, _jwt_data):
        """Handle expired token"""
        raise UserError("Token has expired", 401)


    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        """Handle invalid token format"""
        raise UserError("Invalid token format", 401)


    @jwt.unauthorized_loader
    def handle_missing_token(error):
        """Handle missing token"""
        raise UserError("Authentication token is missing", 401)


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
except Exception as e:
    print(f"Initialization Error: {str(e)}")
    exit(1)

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=5000)


