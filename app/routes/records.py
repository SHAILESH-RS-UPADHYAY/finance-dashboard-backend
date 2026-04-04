from flask import Blueprint, request, jsonify
from app import db
from app.models import FinancialRecord, User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.middleware import role_required
import datetime

records_bp = Blueprint('records', __name__)

@records_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_record():
    data = request.get_json()
    
    # Validation
    required_fields = ['amount', 'type', 'category', 'date']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
            
    if data['type'] not in ['income', 'expense']:
        return jsonify({"error": "Type must be either 'income' or 'expense'."}), 400

    try:
        record_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    current_user_id = get_jwt_identity()

    new_record = FinancialRecord(
        user_id=current_user_id,
        amount=float(data['amount']),
        record_type=data['type'],
        category=data['category'],
        description=data.get('description', ''),
        date=record_date
    )

    db.session.add(new_record)
    db.session.commit()

    return jsonify({"message": "Financial record created successfully.", "record": new_record.to_dict()}), 201

@records_bp.route('', methods=['GET'])
@jwt_required()
@role_required('viewer', 'analyst', 'admin')
def get_records():
    # Filtering params
    record_type = request.args.get('type')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = FinancialRecord.query.filter_by(is_deleted=False)

    if record_type:
        query = query.filter_by(record_type=record_type)
    if category:
        query = query.filter_by(category=category)
    
    if start_date:
        try:
            start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(FinancialRecord.date >= start_date_obj)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
            
    if end_date:
        try:
            end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(FinancialRecord.date <= end_date_obj)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400

    query = query.order_by(FinancialRecord.date.desc())
    
    paginated_records = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "records": [record.to_dict() for record in paginated_records.items],
        "total": paginated_records.total,
        "pages": paginated_records.pages,
        "current_page": paginated_records.page
    }), 200

@records_bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
@role_required('viewer', 'analyst', 'admin')
def get_record(record_id):
    record = FinancialRecord.query.filter_by(id=record_id, is_deleted=False).first()
    if not record:
        return jsonify({"error": "Record not found."}), 404

    return jsonify(record.to_dict()), 200

@records_bp.route('/<int:record_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_record(record_id):
    record = FinancialRecord.query.filter_by(id=record_id, is_deleted=False).first()
    if not record:
        return jsonify({"error": "Record not found."}), 404

    data = request.get_json()

    if data.get('type') and data['type'] not in ['income', 'expense']:
        return jsonify({"error": "Type must be either 'income' or 'expense'."}), 400

    if data.get('date'):
        try:
            record.date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    if 'amount' in data:
        record.amount = float(data['amount'])
    if 'type' in data:
        record.record_type = data['type']
    if 'category' in data:
        record.category = data['category']
    if 'description' in data:
        record.description = data['description']

    db.session.commit()

    return jsonify({"message": "Record updated successfully.", "record": record.to_dict()}), 200

@records_bp.route('/<int:record_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_record(record_id):
    record = FinancialRecord.query.filter_by(id=record_id, is_deleted=False).first()
    if not record:
        return jsonify({"error": "Record not found."}), 404

    # Soft delete
    record.is_deleted = True
    db.session.commit()

    return jsonify({"message": "Record deleted successfully."}), 200
