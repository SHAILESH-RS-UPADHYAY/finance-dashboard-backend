from flask import Blueprint, jsonify
from app.models import FinancialRecord
from flask_jwt_extended import jwt_required
from app.middleware import role_required
from sqlalchemy import func
from app import db
import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
@role_required('analyst', 'admin')
def dashboard_summary():
    # Calculate total income
    total_income = db.session.query(func.sum(FinancialRecord.amount)).filter_by(
        record_type='income', is_deleted=False
    ).scalar() or 0.0

    # Calculate total expense
    total_expense = db.session.query(func.sum(FinancialRecord.amount)).filter_by(
        record_type='expense', is_deleted=False
    ).scalar() or 0.0

    net_balance = total_income - total_expense

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance
    }), 200

@dashboard_bp.route('/category-breakdown', methods=['GET'])
@jwt_required()
@role_required('analyst', 'admin')
def category_breakdown():
    # Group by category and type
    results = db.session.query(
        FinancialRecord.category,
        FinancialRecord.record_type,
        func.sum(FinancialRecord.amount).label('total_amount')
    ).filter_by(is_deleted=False).group_by(
        FinancialRecord.category, FinancialRecord.record_type
    ).all()

    breakdown = []
    for row in results:
        breakdown.append({
            "category": row.category,
            "type": row.record_type,
            "total_amount": float(row.total_amount)
        })

    return jsonify(breakdown), 200

@dashboard_bp.route('/recent', methods=['GET'])
@jwt_required()
@role_required('viewer', 'analyst', 'admin')
def recent_activity():
    # Last 5 records
    recent_records = FinancialRecord.query.filter_by(is_deleted=False).order_by(
        FinancialRecord.created_at.desc()
    ).limit(5).all()

    return jsonify([record.to_dict() for record in recent_records]), 200
