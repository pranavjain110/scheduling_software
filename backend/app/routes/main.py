from flask import Blueprint, request, jsonify
from app import db
from app.models.company import Company
from app.models.part import Part
from app.models.operation import Operation
from app.models.machine import Machine
from app.models.operation_machine import OperationMachine
from app.models.monthly_plan import MonthlyPlan
from app.models.forecast_plan import ForecastPlan
from app.models.production_schedule import ProductionSchedule

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return {"message": "CNC Workshop Production Planning Software API"}

# Company CRUD operations
@main_bp.route("/companies", methods=["GET"])
def get_companies():
    companies = Company.query.all()
    return jsonify([company.to_dict() for company in companies])

@main_bp.route("/companies", methods=["POST"])
def create_company():
    data = request.get_json()
    company = Company(name=data["name"])
    db.session.add(company)
    db.session.commit()
    return jsonify(company.to_dict()), 201

# Machine CRUD operations
@main_bp.route("/machines", methods=["GET"])
def get_machines():
    machines = Machine.query.all()
    return jsonify([machine.to_dict() for machine in machines])

@main_bp.route("/machines", methods=["POST"])
def create_machine():
    data = request.get_json()
    machine = Machine(name=data["name"], type=data["type"])
    db.session.add(machine)
    db.session.commit()
    return jsonify(machine.to_dict()), 201

# Operation-Machine relationship
@main_bp.route("/operations/<int:operation_id>/eligible-machines", methods=["GET"])
def get_eligible_machines(operation_id):
    operation = Operation.query.get_or_404(operation_id)
    machines = operation.get_eligible_machines()
    return jsonify([machine.to_dict() for machine in machines])

# Test route to verify database setup
@main_bp.route("/test-db", methods=["GET"])
def test_database():
    try:
        # Test basic database connectivity
        companies_count = Company.query.count()
        machines_count = Machine.query.count()
        parts_count = Part.query.count()
        operations_count = Operation.query.count()
        
        return jsonify({
            "database_status": "connected",
            "tables": {
                "companies": companies_count,
                "machines": machines_count,
                "parts": parts_count,
                "operations": operations_count
            }
        })
    except Exception as e:
        return jsonify({"database_status": "error", "error": str(e)}), 500
