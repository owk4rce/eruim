from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman

from backend.src.config.config import load_config
from backend.src.config.db import connect_db
from backend.src.config.limiter import public_routes_limiter, protected_routes_limiter
from backend.src.config.logger import setup_logger
from backend.src.config.swagger import get_swagger_config, get_swagger_template
from backend.src.routes import api_v1_bp
from backend.src.utils.error_handlers import register_error_handlers
from backend.src.config.scheduler import init_scheduler

app = Flask(__name__)

# Initialize logger with default settings
logger = setup_logger(is_initial=True)

@app.before_request
def log_request_info():
    logger.info("=== New Request ===")
    logger.info(f"Path: {request.path}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Content-Length: {request.content_length}")
    logger.info(f"Headers: {dict(request.headers)}")

# ADD NEW SETTINGS HERE, BEFORE try-except BLOCK:
# Max request size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# File upload settings
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.config['UPLOAD_PATH'] = 'uploads'

# CORS settings
CORS(app,
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     expose_headers=["Content-Type", "Authorization"],
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

try:
    config = load_config()
    app.config.update(config)

    swagger = Swagger(
        app,
        config=get_swagger_config(),
        template=get_swagger_template()
    )

    # Reconfigure logger with settings from config
    logger = setup_logger(app)
    logger.info("Configuration loaded successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    exit(1)

app.url_map.strict_slashes = False  # no need for the end slash in endpoint

#CORS(app)
jwt = JWTManager(app)

if not app.config.get('TESTING', False):
    public_routes_limiter.init_app(app)
    protected_routes_limiter.init_app(app)
    init_scheduler(app)  # Initialize scheduler


@jwt.unauthorized_loader
def custom_unauthorized_response(err_msg):
    logger.warning(f"Entering unauthorized handler")
    logger.warning(f"Unauthorized access attempt: {err_msg}")
    response = jsonify({
        "error": "Authentication required.",
        "message": err_msg
    })
    logger.warning("Response prepared")
    return response, 401


@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    logger.warning(f"Expired token used. Payload: {jwt_payload}")
    return jsonify({
        "error": "Token has expired",
        "message": "Please log in again."
    }), 401


@jwt.invalid_token_loader
def custom_invalid_token_response(err_msg):
    logger.warning(f"Invalid token used: {err_msg}")
    return jsonify({
        "error": "Invalid token.",
        "message": f"Token error: {err_msg}"
    }), 422


if app.config["DEBUG"]:
    Talisman(
        app,
        force_https=False,  # http allowed in development
        content_security_policy=None  # for development
    )
else:
    # all is True for Production
    Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy={
            'default-src': ["'self'"],
            'img-src': ["'self'", '*'],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'font-src': ["'self'", "data:", "https://fonts.gstatic.com"],
            'connect-src': ["'self'"],
            # external для Swagger
            'worker-src': ["'self'", "blob:"],
            'child-src': ["'self'", "blob:"],
            'frame-src': ["'self'"],
            'object-src': ["'none'"]
        }
        # content_security_policy={
        #     'default-src': "'self'",
        #     'img-src': '*',
        #     'script-src': "'self'"
        # }
    )

connect_db(app)

app.register_blueprint(api_v1_bp)
register_error_handlers(app)

if __name__ == '__main__':
    logger.info("Starting server...")
    app.run(debug=app.config["DEBUG"], port=5000)
