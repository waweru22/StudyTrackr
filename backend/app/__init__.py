from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    # Allow specific origins for frontend (Vite defaults to 5173, but can shift to 5174, 5175)
    allowed_origins = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175"
    ]
    CORS(app, resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }, supports_credentials=True)

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
    app.register_blueprint(session_bp, url_prefix='/session')
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

    return app
