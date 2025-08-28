#!/usr/bin/env python3
"""
Conflict Detection Demonstration Script
This script demonstrates the new conflict detection features for double-booked machines.
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000"

def create_sample_data():
    """Create sample data for demonstration."""
    print("🏗️  Creating sample data...")
    
    # Create company
    company_data = {"name": "Demo Manufacturing Co."}
    response = requests.post(f"{BASE_URL}/companies", json=company_data)
    company = response.json()
    
    # Create machine
    machine_data = {"name": "CNC Lathe #001", "type": "Lathe"}
    response = requests.post(f"{BASE_URL}/machines", json=machine_data)
    machine = response.json()
    
    # Create parts
    part1_data = {"name": "Precision Gear", "company_id": company["company_id"], "total_operations": 3}
    part2_data = {"name": "Shaft Component", "company_id": company["company_id"], "total_operations": 2}
    
    response1 = requests.post(f"{BASE_URL}/parts", json=part1_data)
    response2 = requests.post(f"{BASE_URL}/parts", json=part2_data)
    part1, part2 = response1.json(), response2.json()
    
    # Create operations
    op1_data = {"part_id": part1["part_id"], "sequence_number": 10, "machining_time": 25.0, "loading_time": 3.0}
    op2_data = {"part_id": part2["part_id"], "sequence_number": 10, "machining_time": 30.0, "loading_time": 4.0}
    
    response1 = requests.post(f"{BASE_URL}/operations", json=op1_data)
    response2 = requests.post(f"{BASE_URL}/operations", json=op2_data)
    op1, op2 = response1.json(), response2.json()
    
    print(f"✅ Created sample data:")
    print(f"   Company: {company['name']} (ID: {company['company_id']})")
    print(f"   Machine: {machine['name']} (ID: {machine['machine_id']})")
    print(f"   Parts: {part1['name']} (ID: {part1['part_id']}), {part2['name']} (ID: {part2['part_id']})")
    print(f"   Operations: OP{op1['sequence_number']} (ID: {op1['operation_id']}), OP{op2['sequence_number']} (ID: {op2['operation_id']})")
    
    return {
        'company_id': company['company_id'],
        'machine_id': machine['machine_id'],
        'part1_id': part1['part_id'],
        'part2_id': part2['part_id'],
        'operation1_id': op1['operation_id'],
        'operation2_id': op2['operation_id']
    }

def demonstrate_conflict_detection(data):
    """Demonstrate conflict detection functionality."""
    print("\n🔍 Demonstrating Conflict Detection...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Step 1: Create first schedule
    print("\n📅 Step 1: Creating first production schedule...")
    schedule1_data = {
        "date": today,
        "shift_number": 1,
        "slot_number": 1,
        "part_id": data['part1_id'],
        "operation_id": data['operation1_id'],
        "machine_id": data['machine_id'],
        "quantity_scheduled": 100,
        "sub_batch_id": "BATCH_001",
        "status": "planned"
    }
    
    response = requests.post(f"{BASE_URL}/production-schedules", json=schedule1_data)
    schedule1 = response.json()
    
    print(f"✅ Schedule created successfully!")
    print(f"   Schedule ID: {schedule1['schedule_id']}")
    print(f"   Conflicts detected: {schedule1['warnings']['conflicts_detected']}")
    print(f"   Message: {schedule1['warnings']['message']}")
    
    # Step 2: Check slot availability before creating conflict
    print("\n🔎 Step 2: Checking slot availability before creating potential conflict...")
    check_data = {
        "machine_id": data['machine_id'],
        "date": today,
        "shift_number": 1,
        "slot_number": 1
    }
    
    response = requests.post(f"{BASE_URL}/production-schedules/conflicts/check-slot", json=check_data)
    check_result = response.json()
    
    print(f"✅ Slot availability check completed!")
    print(f"   Has conflicts: {check_result['has_conflicts']}")
    print(f"   Conflicts count: {check_result['conflicts_count']}")
    if check_result['has_conflicts']:
        print(f"   Warning: {check_result['warning']}")
    
    # Step 3: Create conflicting schedule (double-booking)
    print("\n⚠️  Step 3: Creating conflicting schedule (double-booking)...")
    schedule2_data = {
        "date": today,
        "shift_number": 1,
        "slot_number": 1,  # Same slot as first schedule
        "part_id": data['part2_id'],
        "operation_id": data['operation2_id'],
        "machine_id": data['machine_id'],
        "quantity_scheduled": 75,
        "sub_batch_id": "BATCH_002",
        "status": "planned"
    }
    
    response = requests.post(f"{BASE_URL}/production-schedules", json=schedule2_data)
    schedule2 = response.json()
    
    print(f"✅ Conflicting schedule created with warnings!")
    print(f"   Schedule ID: {schedule2['schedule_id']}")
    print(f"   Conflicts detected: {schedule2['warnings']['conflicts_detected']}")
    print(f"   Message: {schedule2['warnings']['message']}")
    print(f"   Number of conflicts: {len(schedule2['warnings']['conflicts'])}")
    
    if schedule2['warnings']['conflicts']:
        conflict = schedule2['warnings']['conflicts'][0]
        print(f"   Conflicting with schedule ID: {conflict['schedule_id']}")
        print(f"   Conflicting part ID: {conflict['part_id']}")
        print(f"   Conflicting operation ID: {conflict['operation_id']}")
    
    # Step 4: Query conflicts by date
    print(f"\n📊 Step 4: Querying all conflicts for date {today}...")
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-date/{today}")
    date_conflicts = response.json()
    
    print(f"✅ Date conflicts retrieved!")
    print(f"   Date: {date_conflicts['date']}")
    print(f"   Total conflicts: {date_conflicts['conflicts_count']}")
    
    for i, conflict in enumerate(date_conflicts['conflicts'], 1):
        slot_info = conflict['slot_info']
        print(f"   Conflict {i}:")
        print(f"     Machine: {slot_info['machine_id']}, Date: {slot_info['date']}")
        print(f"     Shift: {slot_info['shift_number']}, Slot: {slot_info['slot_number']}")
        print(f"     Schedules in conflict: {len(conflict['conflicting_schedules'])}")
    
    # Step 5: Query conflicts by machine
    print(f"\n🏭 Step 5: Querying all conflicts for machine {data['machine_id']}...")
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-machine/{data['machine_id']}")
    machine_conflicts = response.json()
    
    print(f"✅ Machine conflicts retrieved!")
    print(f"   Machine ID: {machine_conflicts['machine_id']}")
    print(f"   Total conflicts: {machine_conflicts['conflicts_count']}")
    
    # Step 6: Demonstrate conflict resolution by updating schedule
    print(f"\n🔧 Step 6: Resolving conflict by moving schedule to different slot...")
    update_data = {
        "shift_number": 1,
        "slot_number": 2  # Move to different slot
    }
    
    response = requests.put(f"{BASE_URL}/production-schedules/{schedule2['schedule_id']}", json=update_data)
    updated_schedule = response.json()
    
    print(f"✅ Schedule updated to resolve conflict!")
    print(f"   Updated schedule ID: {updated_schedule['schedule_id']}")
    print(f"   Conflicts detected: {updated_schedule['warnings']['conflicts_detected']}")
    print(f"   Message: {updated_schedule['warnings']['message']}")
    
    # Step 7: Verify conflicts are resolved
    print(f"\n✅ Step 7: Verifying conflicts are resolved...")
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-date/{today}")
    final_conflicts = response.json()
    
    print(f"✅ Final conflict check completed!")
    print(f"   Remaining conflicts: {final_conflicts['conflicts_count']}")
    if final_conflicts['conflicts_count'] == 0:
        print("   🎉 All conflicts resolved successfully!")
    else:
        print("   ⚠️  Some conflicts still exist.")

def main():
    """Main demonstration function."""
    print("🚀 CNC Workshop Conflict Detection Demonstration")
    print("=" * 55)
    
    try:
        # Test server connection
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Flask server is not running. Please start the server first.")
            print("   Run: python run.py")
            return
        
        # Create sample data
        data = create_sample_data()
        
        # Demonstrate conflict detection
        demonstrate_conflict_detection(data)
        
        print("\n" + "=" * 55)
        print("🎉 Demonstration completed successfully!")
        print("\nKey Features Demonstrated:")
        print("• ✅ Temporary double-booking with conflict warnings")
        print("• ✅ Detailed conflict detection and reporting")
        print("• ✅ Conflict queries by date and machine")
        print("• ✅ Slot availability checking")
        print("• ✅ Conflict resolution through schedule updates")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Please start the server first.")
        print("   Run: python run.py")
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")

if __name__ == "__main__":
    main()