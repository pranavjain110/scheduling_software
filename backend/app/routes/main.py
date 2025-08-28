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

# Monthly Plan CRUD operations
@main_bp.route("/monthly-plans", methods=["GET"])
def get_monthly_plans():
    plans = MonthlyPlan.query.all()
    return jsonify([plan.to_dict() for plan in plans])

@main_bp.route("/monthly-plans", methods=["POST"])
def create_monthly_plan():
    data = request.get_json()
    if not data or not all(key in data for key in ["part_id", "company_id", "month", "planned_quantity"]):
        return jsonify({"error": "Missing required fields: part_id, company_id, month, planned_quantity"}), 400
    
    # Validate company exists
    company = Company.query.get(data["company_id"])
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    # Validate part exists
    part = Part.query.get(data["part_id"])
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    # Parse month date
    try:
        from datetime import datetime
        month_date = datetime.fromisoformat(data["month"]).date()
    except ValueError:
        return jsonify({"error": "Invalid month format. Use YYYY-MM-DD"}), 400
    
    # Remove previous schedule for same company/part/month (supersede logic)
    existing_plan = MonthlyPlan.query.filter_by(
        part_id=data["part_id"],
        company_id=data["company_id"],
        month=month_date
    ).first()
    
    if existing_plan:
        db.session.delete(existing_plan)
    
    # Create new plan
    plan = MonthlyPlan(
        part_id=data["part_id"],
        company_id=data["company_id"],
        month=month_date,
        planned_quantity=data["planned_quantity"]
    )
    
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201

@main_bp.route("/monthly-plans/<int:plan_id>", methods=["GET"])
def get_monthly_plan(plan_id):
    plan = MonthlyPlan.query.get_or_404(plan_id)
    return jsonify(plan.to_dict())

@main_bp.route("/monthly-plans/<int:plan_id>", methods=["PUT"])
def update_monthly_plan(plan_id):
    plan = MonthlyPlan.query.get_or_404(plan_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate company if company_id is being updated
    if "company_id" in data:
        company = Company.query.get(data["company_id"])
        if not company:
            return jsonify({"error": "Company not found"}), 404
        plan.company_id = data["company_id"]
    
    # Validate part if part_id is being updated
    if "part_id" in data:
        part = Part.query.get(data["part_id"])
        if not part:
            return jsonify({"error": "Part not found"}), 404
        plan.part_id = data["part_id"]
    
    # Update month if provided
    if "month" in data:
        try:
            from datetime import datetime
            plan.month = datetime.fromisoformat(data["month"]).date()
        except ValueError:
            return jsonify({"error": "Invalid month format. Use YYYY-MM-DD"}), 400
    
    # Update quantity if provided
    if "planned_quantity" in data:
        plan.planned_quantity = data["planned_quantity"]
    
    db.session.commit()
    return jsonify(plan.to_dict())

@main_bp.route("/monthly-plans/<int:plan_id>", methods=["DELETE"])
def delete_monthly_plan(plan_id):
    plan = MonthlyPlan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return jsonify({"message": "Monthly plan deleted successfully"}), 200

# Forecast Plan CRUD operations
@main_bp.route("/forecast-plans", methods=["GET"])
def get_forecast_plans():
    plans = ForecastPlan.query.all()
    return jsonify([plan.to_dict() for plan in plans])

@main_bp.route("/forecast-plans", methods=["POST"])
def create_forecast_plan():
    data = request.get_json()
    if not data or not all(key in data for key in ["part_id", "company_id", "month", "week", "forecasted_quantity"]):
        return jsonify({"error": "Missing required fields: part_id, company_id, month, week, forecasted_quantity"}), 400
    
    # Validate company exists
    company = Company.query.get(data["company_id"])
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    # Validate part exists
    part = Part.query.get(data["part_id"])
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    # Validate week number
    if not (1 <= data["week"] <= 4):
        return jsonify({"error": "Week number must be between 1 and 4"}), 400
    
    # Parse month date
    try:
        from datetime import datetime
        month_date = datetime.fromisoformat(data["month"]).date()
    except ValueError:
        return jsonify({"error": "Invalid month format. Use YYYY-MM-DD"}), 400
    
    # Remove previous forecast for same company/part/month/week (supersede logic)
    existing_forecast = ForecastPlan.query.filter_by(
        part_id=data["part_id"],
        company_id=data["company_id"],
        month=month_date,
        week=data["week"]
    ).first()
    
    if existing_forecast:
        db.session.delete(existing_forecast)
    
    # Create new forecast
    forecast = ForecastPlan(
        part_id=data["part_id"],
        company_id=data["company_id"],
        month=month_date,
        week=data["week"],
        forecasted_quantity=data["forecasted_quantity"]
    )
    
    db.session.add(forecast)
    db.session.commit()
    return jsonify(forecast.to_dict()), 201

@main_bp.route("/forecast-plans/<int:forecast_id>", methods=["GET"])
def get_forecast_plan(forecast_id):
    forecast = ForecastPlan.query.get_or_404(forecast_id)
    return jsonify(forecast.to_dict())

@main_bp.route("/forecast-plans/<int:forecast_id>", methods=["PUT"])
def update_forecast_plan(forecast_id):
    forecast = ForecastPlan.query.get_or_404(forecast_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate company if company_id is being updated
    if "company_id" in data:
        company = Company.query.get(data["company_id"])
        if not company:
            return jsonify({"error": "Company not found"}), 404
        forecast.company_id = data["company_id"]
    
    # Validate part if part_id is being updated
    if "part_id" in data:
        part = Part.query.get(data["part_id"])
        if not part:
            return jsonify({"error": "Part not found"}), 404
        forecast.part_id = data["part_id"]
    
    # Update month if provided
    if "month" in data:
        try:
            from datetime import datetime
            forecast.month = datetime.fromisoformat(data["month"]).date()
        except ValueError:
            return jsonify({"error": "Invalid month format. Use YYYY-MM-DD"}), 400
    
    # Update week if provided
    if "week" in data:
        if not (1 <= data["week"] <= 4):
            return jsonify({"error": "Week number must be between 1 and 4"}), 400
        forecast.week = data["week"]
    
    # Update quantity if provided
    if "forecasted_quantity" in data:
        forecast.forecasted_quantity = data["forecasted_quantity"]
    
    db.session.commit()
    return jsonify(forecast.to_dict())

@main_bp.route("/forecast-plans/<int:forecast_id>", methods=["DELETE"])
def delete_forecast_plan(forecast_id):
    forecast = ForecastPlan.query.get_or_404(forecast_id)
    db.session.delete(forecast)
    db.session.commit()
    return jsonify({"message": "Forecast plan deleted successfully"}), 200

# Production Schedule CRUD operations
@main_bp.route("/production-schedules", methods=["GET"])
def get_production_schedules():
    # Support filtering by date, machine_id, part_id
    date_param = request.args.get('date')
    machine_id_param = request.args.get('machine_id')
    part_id_param = request.args.get('part_id')
    
    query = ProductionSchedule.query
    
    if date_param:
        try:
            from datetime import datetime
            date_filter = datetime.fromisoformat(date_param).date()
            query = query.filter_by(date=date_filter)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    if machine_id_param:
        try:
            machine_id = int(machine_id_param)
            query = query.filter_by(machine_id=machine_id)
        except ValueError:
            return jsonify({"error": "Invalid machine_id format"}), 400
    
    if part_id_param:
        try:
            part_id = int(part_id_param)
            query = query.filter_by(part_id=part_id)
        except ValueError:
            return jsonify({"error": "Invalid part_id format"}), 400
    
    schedules = query.all()
    return jsonify([schedule.to_dict() for schedule in schedules])

@main_bp.route("/production-schedules", methods=["POST"])
def create_production_schedule():
    data = request.get_json()
    if not data or not all(key in data for key in ["date", "shift_number", "slot_number", "part_id", "operation_id", "machine_id", "quantity_scheduled"]):
        return jsonify({"error": "Missing required fields: date, shift_number, slot_number, part_id, operation_id, machine_id, quantity_scheduled"}), 400
    
    # Validate part exists
    part = Part.query.get(data["part_id"])
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    # Validate operation exists
    operation = Operation.query.get(data["operation_id"])
    if not operation:
        return jsonify({"error": "Operation not found"}), 404
    
    # Validate machine exists
    machine = Machine.query.get(data["machine_id"])
    if not machine:
        return jsonify({"error": "Machine not found"}), 404
    
    # Validate shift and slot numbers
    if data["shift_number"] not in [1, 2]:
        return jsonify({"error": "Shift number must be 1 or 2"}), 400
    
    if data["slot_number"] not in [1, 2]:
        return jsonify({"error": "Slot number must be 1 or 2"}), 400
    
    # Parse date
    try:
        from datetime import datetime
        schedule_date = datetime.fromisoformat(data["date"]).date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Validate status if provided
    if "status" in data and data["status"] not in ["planned", "in_progress", "completed", "delayed"]:
        return jsonify({"error": "Status must be one of: planned, in_progress, completed, delayed"}), 400
    
    # Check for conflicts before creating the schedule
    existing_conflicts = ProductionSchedule.get_slot_conflicts(
        data["machine_id"], 
        schedule_date, 
        data["shift_number"], 
        data["slot_number"]
    )
    
    # Create production schedule (allow double-booking but warn about conflicts)
    schedule = ProductionSchedule(
        date=schedule_date,
        shift_number=data["shift_number"],
        slot_number=data["slot_number"],
        part_id=data["part_id"],
        operation_id=data["operation_id"],
        machine_id=data["machine_id"],
        quantity_scheduled=data["quantity_scheduled"],
        sub_batch_id=data.get("sub_batch_id"),
        status=data.get("status", "planned")
    )
    
    db.session.add(schedule)
    db.session.commit()
    
    # Prepare response with conflict warnings if any
    response_data = schedule.to_dict()
    
    if existing_conflicts:
        response_data["warnings"] = {
            "conflicts_detected": True,
            "message": "Schedule created successfully, but conflicts detected in this slot.",
            "conflicts": existing_conflicts
        }
        return jsonify(response_data), 201  # Created with warnings
    else:
        response_data["warnings"] = {
            "conflicts_detected": False,
            "message": "Schedule created successfully with no conflicts."
        }
        return jsonify(response_data), 201

@main_bp.route("/production-schedules/<int:schedule_id>", methods=["GET"])
def get_production_schedule(schedule_id):
    schedule = ProductionSchedule.query.get_or_404(schedule_id)
    return jsonify(schedule.to_dict())

@main_bp.route("/production-schedules/<int:schedule_id>", methods=["PUT"])
def update_production_schedule(schedule_id):
    schedule = ProductionSchedule.query.get_or_404(schedule_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate status if provided
    if "status" in data and data["status"] not in ["planned", "in_progress", "completed", "delayed"]:
        return jsonify({"error": "Status must be one of: planned, in_progress, completed, delayed"}), 400
    
    # Validate machine if being updated
    if "machine_id" in data:
        machine = Machine.query.get(data["machine_id"])
        if not machine:
            return jsonify({"error": "Machine not found"}), 404
        schedule.machine_id = data["machine_id"]
    
    # Validate part if being updated
    if "part_id" in data:
        part = Part.query.get(data["part_id"])
        if not part:
            return jsonify({"error": "Part not found"}), 404
        schedule.part_id = data["part_id"]
    
    # Validate operation if being updated
    if "operation_id" in data:
        operation = Operation.query.get(data["operation_id"])
        if not operation:
            return jsonify({"error": "Operation not found"}), 404
        schedule.operation_id = data["operation_id"]
    
    # Update date if provided
    if "date" in data:
        try:
            from datetime import datetime
            schedule.date = datetime.fromisoformat(data["date"]).date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Update shift and slot numbers if provided
    if "shift_number" in data:
        if data["shift_number"] not in [1, 2]:
            return jsonify({"error": "Shift number must be 1 or 2"}), 400
        schedule.shift_number = data["shift_number"]
    
    if "slot_number" in data:
        if data["slot_number"] not in [1, 2]:
            return jsonify({"error": "Slot number must be 1 or 2"}), 400
        schedule.slot_number = data["slot_number"]
    
    # Update other fields
    if "quantity_scheduled" in data:
        schedule.quantity_scheduled = data["quantity_scheduled"]
    if "sub_batch_id" in data:
        schedule.sub_batch_id = data["sub_batch_id"]
    if "status" in data:
        schedule.status = data["status"]
    
    # Check for conflicts after potential slot/machine changes (excluding current schedule)
    conflicts = ProductionSchedule.get_slot_conflicts(
        schedule.machine_id, 
        schedule.date, 
        schedule.shift_number, 
        schedule.slot_number,
        exclude_schedule_id=schedule_id
    )
    
    db.session.commit()
    
    # Prepare response with conflict warnings if any
    response_data = schedule.to_dict()
    
    if conflicts:
        response_data["warnings"] = {
            "conflicts_detected": True,
            "message": "Schedule updated successfully, but conflicts detected in this slot.",
            "conflicts": conflicts
        }
    else:
        response_data["warnings"] = {
            "conflicts_detected": False,
            "message": "Schedule updated successfully with no conflicts."
        }
    
    return jsonify(response_data)

@main_bp.route("/production-schedules/<int:schedule_id>", methods=["DELETE"])
def delete_production_schedule(schedule_id):
    schedule = ProductionSchedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({"message": "Production schedule deleted successfully"}), 200

@main_bp.route("/production-schedules/<int:schedule_id>/status", methods=["PUT"])
def update_production_schedule_status(schedule_id):
    """Update only the status of a production schedule for sub-batch tracking"""
    schedule = ProductionSchedule.query.get_or_404(schedule_id)
    data = request.get_json()
    
    if not data or "status" not in data:
        return jsonify({"error": "Missing required field: status"}), 400
    
    # Validate status
    if data["status"] not in ["planned", "in_progress", "completed", "delayed"]:
        return jsonify({"error": "Status must be one of: planned, in_progress, completed, delayed"}), 400
    
    schedule.status = data["status"]
    db.session.commit()
    return jsonify(schedule.to_dict())

# Specific filtering endpoints for day/machine/part queries
@main_bp.route("/production-schedules/by-date/<date>", methods=["GET"])
def get_schedules_by_date(date):
    try:
        from datetime import datetime
        date_filter = datetime.fromisoformat(date).date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    schedules = ProductionSchedule.query.filter_by(date=date_filter).all()
    return jsonify([schedule.to_dict() for schedule in schedules])

@main_bp.route("/production-schedules/by-machine/<int:machine_id>", methods=["GET"])
def get_schedules_by_machine(machine_id):
    # Validate machine exists
    machine = Machine.query.get_or_404(machine_id)
    
    # Optional date filtering
    date_param = request.args.get('date')
    if date_param:
        try:
            from datetime import datetime
            date_filter = datetime.fromisoformat(date_param).date()
            schedules = ProductionSchedule.get_machine_schedule(machine_id, date_filter)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    else:
        schedules = ProductionSchedule.query.filter_by(machine_id=machine_id).all()
    
    return jsonify([schedule.to_dict() for schedule in schedules])

@main_bp.route("/production-schedules/by-part/<int:part_id>", methods=["GET"])
def get_schedules_by_part(part_id):
    # Validate part exists
    part = Part.query.get_or_404(part_id)
    
    schedules = ProductionSchedule.query.filter_by(part_id=part_id).all()
    return jsonify([schedule.to_dict() for schedule in schedules])

# Conflict detection endpoints
@main_bp.route("/production-schedules/conflicts/by-date/<date>", methods=["GET"])
def get_conflicts_by_date(date):
    """Get all scheduling conflicts for a specific date"""
    try:
        from datetime import datetime
        date_filter = datetime.fromisoformat(date).date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    conflicts = ProductionSchedule.get_date_conflicts(date_filter)
    
    return jsonify({
        "date": date,
        "conflicts_count": len(conflicts),
        "conflicts": conflicts
    })

@main_bp.route("/production-schedules/conflicts/by-machine/<int:machine_id>", methods=["GET"])
def get_conflicts_by_machine(machine_id):
    """Get all scheduling conflicts for a specific machine"""
    # Validate machine exists
    machine = Machine.query.get_or_404(machine_id)
    
    # Optional date filtering
    date_param = request.args.get('date')
    date_filter = None
    
    if date_param:
        try:
            from datetime import datetime
            date_filter = datetime.fromisoformat(date_param).date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    conflicts = ProductionSchedule.get_machine_conflicts(machine_id, date_filter)
    
    response_data = {
        "machine_id": machine_id,
        "conflicts_count": len(conflicts),
        "conflicts": conflicts
    }
    
    if date_filter:
        response_data["date"] = date_param
    
    return jsonify(response_data)

@main_bp.route("/production-schedules/conflicts/check-slot", methods=["POST"])
def check_slot_conflicts():
    """Check for conflicts in a specific slot before scheduling"""
    data = request.get_json()
    
    if not data or not all(key in data for key in ["machine_id", "date", "shift_number", "slot_number"]):
        return jsonify({"error": "Missing required fields: machine_id, date, shift_number, slot_number"}), 400
    
    # Validate machine exists
    machine = Machine.query.get_or_404(data["machine_id"])
    
    # Validate shift and slot numbers
    if data["shift_number"] not in [1, 2]:
        return jsonify({"error": "Shift number must be 1 or 2"}), 400
    
    if data["slot_number"] not in [1, 2]:
        return jsonify({"error": "Slot number must be 1 or 2"}), 400
    
    # Parse date
    try:
        from datetime import datetime
        date_filter = datetime.fromisoformat(data["date"]).date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Check for conflicts
    exclude_schedule_id = data.get("exclude_schedule_id")  # For update operations
    conflicts = ProductionSchedule.get_slot_conflicts(
        data["machine_id"], 
        date_filter, 
        data["shift_number"], 
        data["slot_number"],
        exclude_schedule_id
    )
    
    if conflicts:
        return jsonify({
            "has_conflicts": True,
            "conflicts_count": len(conflicts),
            "conflicts": conflicts,
            "warning": "This slot is already occupied. Double-booking will create a conflict."
        })
    else:
        return jsonify({
            "has_conflicts": False,
            "conflicts_count": 0,
            "conflicts": [],
            "message": "Slot is available for scheduling."
        })

# Test route to verify database setup
@main_bp.route("/test-db", methods=["GET"])
def test_database():
    try:
        # Test basic database connectivity
        companies_count = Company.query.count()
        machines_count = Machine.query.count()
        parts_count = Part.query.count()
        operations_count = Operation.query.count()
        monthly_plans_count = MonthlyPlan.query.count()
        forecast_plans_count = ForecastPlan.query.count()
        production_schedules_count = ProductionSchedule.query.count()
        
        return jsonify({
            "database_status": "connected",
            "tables": {
                "companies": companies_count,
                "machines": machines_count,
                "parts": parts_count,
                "operations": operations_count,
                "monthly_plans": monthly_plans_count,
                "forecast_plans": forecast_plans_count,
                "production_schedules": production_schedules_count
            }
        })
    except Exception as e:
        return jsonify({"database_status": "error", "error": str(e)}), 500
