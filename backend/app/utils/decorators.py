from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user:
                return jsonify({"error": "User not found in system"}), 403
            
            if user.role != 'admin':
                return jsonify({"error": "Insufficient role: admin required"}), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper
