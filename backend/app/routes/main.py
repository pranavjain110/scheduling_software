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
    if not data or "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400
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
    if not data or "name" not in data or "type" not in data:
        return jsonify({"error": "Missing required fields: name, type"}), 400
    machine = Machine(name=data["name"], type=data["type"])
    db.session.add(machine)
    db.session.commit()
    return jsonify(machine.to_dict()), 201

# Part CRUD operations
@main_bp.route("/parts", methods=["GET"])
def get_parts():
    parts = Part.query.all()
    return jsonify([part.to_dict() for part in parts])

@main_bp.route("/parts", methods=["POST"])
def create_part():
    data = request.get_json()
    if not data or "name" not in data or "company_id" not in data:
        return jsonify({"error": "Missing required fields: name, company_id"}), 400
    
    # Validate company exists
    company = Company.query.get(data["company_id"])
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    part = Part(
        name=data["name"],
        company_id=data["company_id"],
        total_operations=data.get("total_operations", 0)
    )
    db.session.add(part)
    db.session.commit()
    return jsonify(part.to_dict()), 201

@main_bp.route("/parts/<int:part_id>", methods=["GET"])
def get_part(part_id):
    part = Part.query.get_or_404(part_id)
    return jsonify(part.to_dict())

@main_bp.route("/parts/<int:part_id>", methods=["PUT"])
def update_part(part_id):
    part = Part.query.get_or_404(part_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate company if company_id is being updated
    if "company_id" in data:
        company = Company.query.get(data["company_id"])
        if not company:
            return jsonify({"error": "Company not found"}), 404
        part.company_id = data["company_id"]
    
    if "name" in data:
        part.name = data["name"]
    if "total_operations" in data:
        part.total_operations = data["total_operations"]
    
    db.session.commit()
    return jsonify(part.to_dict())

@main_bp.route("/parts/<int:part_id>", methods=["DELETE"])
def delete_part(part_id):
    part = Part.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": "Part deleted successfully"}), 200

@main_bp.route("/parts/<int:part_id>/operations", methods=["GET"])
def get_part_operations(part_id):
    part = Part.query.get_or_404(part_id)
    operations = part.operations
    return jsonify([operation.to_dict() for operation in operations])

# Operation CRUD operations
@main_bp.route("/operations", methods=["GET"])
def get_operations():
    operations = Operation.query.all()
    return jsonify([operation.to_dict() for operation in operations])

@main_bp.route("/operations", methods=["POST"])
def create_operation():
    data = request.get_json()
    if not data or not all(key in data for key in ["part_id", "sequence_number", "machining_time", "loading_time"]):
        return jsonify({"error": "Missing required fields: part_id, sequence_number, machining_time, loading_time"}), 400
    
    # Validate part exists
    part = Part.query.get(data["part_id"])
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    operation = Operation(
        part_id=data["part_id"],
        sequence_number=data["sequence_number"],
        machining_time=data["machining_time"],
        loading_time=data["loading_time"]
    )
    db.session.add(operation)
    db.session.commit()
    return jsonify(operation.to_dict()), 201

@main_bp.route("/operations/<int:operation_id>", methods=["GET"])
def get_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)
    return jsonify(operation.to_dict())

@main_bp.route("/operations/<int:operation_id>", methods=["PUT"])
def update_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate part if part_id is being updated
    if "part_id" in data:
        part = Part.query.get(data["part_id"])
        if not part:
            return jsonify({"error": "Part not found"}), 404
        operation.part_id = data["part_id"]
    
    if "sequence_number" in data:
        operation.sequence_number = data["sequence_number"]
    if "machining_time" in data:
        operation.machining_time = data["machining_time"]
    if "loading_time" in data:
        operation.loading_time = data["loading_time"]
    
    db.session.commit()
    return jsonify(operation.to_dict())

@main_bp.route("/operations/<int:operation_id>", methods=["DELETE"])
def delete_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)
    db.session.delete(operation)
    db.session.commit()
    return jsonify({"message": "Operation deleted successfully"}), 200

# Operation-Machine relationship
@main_bp.route("/operations/<int:operation_id>/eligible-machines", methods=["GET"])
def get_eligible_machines(operation_id):
    operation = Operation.query.get_or_404(operation_id)
    machines = operation.get_eligible_machines()
    return jsonify([machine.to_dict() for machine in machines])

@main_bp.route("/operations/<int:operation_id>/machines/<int:machine_id>", methods=["POST"])
def assign_machine_to_operation(operation_id, machine_id):
    operation = Operation.query.get_or_404(operation_id)
    machine = Machine.query.get_or_404(machine_id)
    
    # Check if already assigned
    if machine in operation.eligible_machines:
        return jsonify({"message": "Machine already assigned to operation"}), 200
    
    # Add machine to operation
    operation.eligible_machines.append(machine)
    db.session.commit()
    return jsonify({"message": "Machine assigned to operation successfully"}), 201

@main_bp.route("/operations/<int:operation_id>/machines/<int:machine_id>", methods=["DELETE"])
def remove_machine_from_operation(operation_id, machine_id):
    operation = Operation.query.get_or_404(operation_id)
    machine = Machine.query.get_or_404(machine_id)
    
    # Check if assigned
    if machine not in operation.eligible_machines:
        return jsonify({"error": "Machine not assigned to operation"}), 404
    
    # Remove machine from operation
    operation.eligible_machines.remove(machine)
    db.session.commit()
    return jsonify({"message": "Machine removed from operation successfully"}), 200

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
