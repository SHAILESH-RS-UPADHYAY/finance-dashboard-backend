from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"error": "Missing required fields (name, email, password)."}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered."}), 400

    new_user = User(
        name=data.get('name'),
        email=data.get('email'),
        role=data.get('role', 'viewer') # Default role is Viewer
    )
    # Ensure no one can register themselves as admin directly without approval
    if new_user.role not in ['viewer', 'analyst']:
        new_user.role = 'viewer'

    new_user.set_password(data.get('password'))

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully.", "user": new_user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields (email, password)."}), 400

    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid email or password."}), 401

    if not user.is_active:
        return jsonify({"error": "Account is strictly inactive. Please contact support."}), 403

    # Add custom claims to the JWT
    additional_claims = {"role": user.role, "is_active": user.is_active}
    
    # Create the token with 1 day expiration
    expires = datetime.timedelta(days=1)
    access_token = create_access_token(
        identity=str(user.id), 
        additional_claims=additional_claims,
        expires_delta=expires
    )

    return jsonify({
        "message": "Login successful.",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
        
    return jsonify(user.to_dict()), 200
