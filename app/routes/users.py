from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import jwt_required
from app.middleware import role_required

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_all_users():
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]}), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user.to_dict()), 200

@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user_role(user_id):
    data = request.get_json()
    new_role = data.get('role')

    if new_role not in ['viewer', 'analyst', 'admin']:
        return jsonify({"error": "Invalid role. Must be 'viewer', 'analyst', or 'admin'."}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    user.role = new_role
    db.session.commit()

    return jsonify({"message": f"User role updated to {new_role}.", "user": user.to_dict()}), 200

@users_bp.route('/<int:user_id>/status', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user_status(user_id):
    data = request.get_json()
    is_active = data.get('is_active')

    if is_active is None or not isinstance(is_active, bool):
        return jsonify({"error": "Invalid status. Must be a boolean value (true/false)."}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    user.is_active = is_active
    db.session.commit()

    return jsonify({"message": f"User active status updated.", "user": user.to_dict()}), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully."}), 200
