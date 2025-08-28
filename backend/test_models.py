#!/usr/bin/env python3
"""
Test script to validate database models and CRUD operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.company import Company
from app.models.part import Part
from app.models.operation import Operation
from app.models.machine import Machine
from app.models.operation_machine import OperationMachine
from app.models.monthly_plan import MonthlyPlan
from app.models.forecast_plan import ForecastPlan
from app.models.production_schedule import ProductionSchedule
from datetime import datetime, date

def test_models():
    app = create_app()
    
    with app.app_context():
        # Clear existing data for clean test
        db.drop_all()
        db.create_all()
        
        print("Testing database models...")
        
        # Test Company model
        print("\n1. Testing Company model:")
        company1 = Company(name="ABC Manufacturing")
        company2 = Company(name="XYZ Industries")
        db.session.add_all([company1, company2])
        db.session.commit()
        print(f"Created companies: {company1}, {company2}")
        
        # Test Machine model  
        print("\n2. Testing Machine model:")
        machine1 = Machine(name="CNC Lathe 1", type="CNC Lathe")
        machine2 = Machine(name="VMC 1", type="VMC")
        machine3 = Machine(name="Robot 1", type="Robot")
        db.session.add_all([machine1, machine2, machine3])
        db.session.commit()
        print(f"Created machines: {machine1}, {machine2}, {machine3}")
        
        # Test Part model
        print("\n3. Testing Part model:")
        part1 = Part(company_id=company1.company_id, name="Gear Shaft", total_operations=3)
        part2 = Part(company_id=company2.company_id, name="Housing Cover", total_operations=2)
        db.session.add_all([part1, part2])
        db.session.commit()
        print(f"Created parts: {part1}, {part2}")
        
        # Test Operation model
        print("\n4. Testing Operation model:")
        op1 = Operation(part_id=part1.part_id, sequence_number=10, machining_time=15.5, loading_time=2.0)
        op2 = Operation(part_id=part1.part_id, sequence_number=20, machining_time=12.0, loading_time=1.5)
        op3 = Operation(part_id=part2.part_id, sequence_number=10, machining_time=8.5, loading_time=1.0)
        db.session.add_all([op1, op2, op3])
        db.session.commit()
        print(f"Created operations: {op1}, {op2}, {op3}")
        
        # Test OperationMachine relationship
        print("\n5. Testing OperationMachine relationship:")
        # Operation 1 can run on CNC Lathe and VMC
        om1 = OperationMachine(operation_id=op1.operation_id, machine_id=machine1.machine_id)
        om2 = OperationMachine(operation_id=op1.operation_id, machine_id=machine2.machine_id)
        # Operation 2 can only run on VMC
        om3 = OperationMachine(operation_id=op2.operation_id, machine_id=machine2.machine_id)
        db.session.add_all([om1, om2, om3])
        db.session.commit()
        print(f"Created operation-machine relationships: {om1}, {om2}, {om3}")
        
        # Test querying eligible machines
        print("\n6. Testing eligible machines query:")
        eligible_machines = op1.get_eligible_machines()
        print(f"Operation {op1.operation_id} can run on machines: {[m.name for m in eligible_machines]}")
        
        # Test MonthlyPlan model
        print("\n7. Testing MonthlyPlan model:")
        monthly_plan = MonthlyPlan(
            part_id=part1.part_id,
            company_id=company1.company_id,
            month=date(2024, 1, 1),
            planned_quantity=100
        )
        db.session.add(monthly_plan)
        db.session.commit()
        print(f"Created monthly plan: {monthly_plan}")
        
        # Test ForecastPlan model
        print("\n8. Testing ForecastPlan model:")
        forecast_plan = ForecastPlan(
            part_id=part1.part_id,
            company_id=company1.company_id,
            month=date(2024, 2, 1),
            week=1,
            forecasted_quantity=25
        )
        db.session.add(forecast_plan)
        db.session.commit()
        print(f"Created forecast plan: {forecast_plan}")
        
        # Test ProductionSchedule model
        print("\n9. Testing ProductionSchedule model:")
        production_schedule = ProductionSchedule(
            date=date(2024, 1, 15),
            shift_number=1,
            slot_number=1,
            part_id=part1.part_id,
            operation_id=op1.operation_id,
            machine_id=machine1.machine_id,
            quantity_scheduled=10,
            sub_batch_id="BATCH001",
            status="planned"
        )
        db.session.add(production_schedule)
        db.session.commit()
        print(f"Created production schedule: {production_schedule}")
        
        # Test relationships
        print("\n10. Testing relationships:")
        print(f"Company {company1.name} has parts: {[p.name for p in company1.parts]}")
        print(f"Part {part1.name} has operations: {[f'OP{op.sequence_number}' for op in part1.operations]}")
        print(f"Machine {machine1.name} is eligible for operations: {[op.operation_id for op in machine1.eligible_operations]}")
        
        # Test CRUD operations
        print("\n11. Testing CRUD operations:")
        
        # Read
        all_companies = Company.query.all()
        print(f"Total companies: {len(all_companies)}")
        
        # Update
        company1.name = "ABC Manufacturing Ltd."
        db.session.commit()
        print(f"Updated company name: {company1.name}")
        
        # Query with join
        parts_with_company = db.session.query(Part, Company).join(Company).all()
        print(f"Parts with companies: {[(p.name, c.name) for p, c in parts_with_company]}")
        
        print("\n✅ All tests passed! Database models are working correctly.")
        
        return True

if __name__ == "__main__":
    try:
        test_models()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)