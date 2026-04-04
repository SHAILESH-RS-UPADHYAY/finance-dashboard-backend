from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(*allowed_roles):
    """
    Decorator to restrict access based on user roles.
    Expects JWT token in Authorization header.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Extract role from JWT claims (we'll set this during login)
            user_role = claims.get('role', 'viewer')
            is_active = claims.get('is_active', False)

            if not is_active:
                return jsonify({"error": "Account is inactive."}), 403

            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Access denied. Insufficient permissions.",
                    "required_roles": allowed_roles,
                    "your_role": user_role
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
