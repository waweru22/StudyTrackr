from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # === TEMPORARY MAIL CONFIG DEBUG (remove after diagnosis) ===
    print("=== MAIL CONFIG DEBUG ===")
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    pw = app.config.get('MAIL_PASSWORD', '')
    print(f"MAIL_PASSWORD set: {'YES (' + str(len(pw)) + ' chars)' if pw else 'NO - THIS IS THE PROBLEM'}")
    print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
    print(f"MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND')}")
    print(f"TESTING: {app.config.get('TESTING')}")
    print("=========================")
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:3000"
            ],
            "supports_credentials": True
        }
    })

    # Register blueprints 
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.session_routes import session_bp
    from app.routes.schedule_routes import schedule_bp
    from app.routes.note_routes import note_bp
    from app.routes.resource_routes import resource_bp
    from app.routes.audit_routes import audit_bp
    from app.routes.knowledge_routes import knowledge_bp
    from app.routes.course_routes import course_bp
    from app.routes.user_routes import user_bp
    from app.routes.material_routes import material_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(session_bp, url_prefix='/sessions')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge')
    app.register_blueprint(note_bp, url_prefix='/notes')
    app.register_blueprint(resource_bp, url_prefix='/resources')
    app.register_blueprint(audit_bp, url_prefix='/audit')
    app.register_blueprint(course_bp, url_prefix='/courses')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(material_bp, url_prefix='/materials')
    
    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.routes.notification_routes import notification_bp
    app.register_blueprint(notification_bp, url_prefix='/notifications')

    # Initialize Firebase Cloud Messaging (non-blocking)
    try:
        from app.services.fcm_service import FCMService
        FCMService.initialize_firebase()
    except Exception as e:
        print(f"[APP] Firebase init failed (push disabled): {e}")

    # ── Rate limit exceeded handler (HTTP 429) ──
    from flask_limiter.errors import RateLimitExceeded

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        return jsonify({
            "error": "Too many requests",
            "message": "You are being rate limited. Please wait before trying again.",
            "retry_after": e.description
        }), 429

    return app
