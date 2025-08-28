#!/usr/bin/env python3
"""
Test script for conflict detection functionality.
This script tests the new conflict detection features for double-booked machines.
"""

import requests
import json
import time
import subprocess
import signal
import os
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://127.0.0.1:5000"

def wait_for_server(max_attempts=10):
    """Wait for the Flask server to be ready."""
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

def setup_test_data():
    """Create test data for conflict detection tests."""
    print("🔧 Setting up test data...")
    
    # Create test company
    company_data = {"name": "Conflict Test Company"}
    response = requests.post(f"{BASE_URL}/companies", json=company_data)
    assert response.status_code == 201
    company = response.json()
    company_id = company["company_id"]
    print(f"✅ Created company: {company['name']} (ID: {company_id})")
    
    # Create test machine
    machine_data = {"name": "Test Conflict Machine", "type": "CNC Lathe"}
    response = requests.post(f"{BASE_URL}/machines", json=machine_data)
    assert response.status_code == 201
    machine = response.json()
    machine_id = machine["machine_id"]
    print(f"✅ Created machine: {machine['name']} (ID: {machine_id})")
    
    # Create test parts
    part1_data = {"name": "Test Gear A", "company_id": company_id, "total_operations": 2}
    response = requests.post(f"{BASE_URL}/parts", json=part1_data)
    assert response.status_code == 201
    part1 = response.json()
    part1_id = part1["part_id"]
    
    part2_data = {"name": "Test Gear B", "company_id": company_id, "total_operations": 2}
    response = requests.post(f"{BASE_URL}/parts", json=part2_data)
    assert response.status_code == 201
    part2 = response.json()
    part2_id = part2["part_id"]
    print(f"✅ Created parts: {part1['name']} (ID: {part1_id}), {part2['name']} (ID: {part2_id})")
    
    # Create test operations
    operation1_data = {
        "part_id": part1_id,
        "sequence_number": 10,
        "machining_time": 15.5,
        "loading_time": 2.0
    }
    response = requests.post(f"{BASE_URL}/operations", json=operation1_data)
    assert response.status_code == 201
    operation1 = response.json()
    operation1_id = operation1["operation_id"]
    
    operation2_data = {
        "part_id": part2_id,
        "sequence_number": 10,
        "machining_time": 20.0,
        "loading_time": 3.0
    }
    response = requests.post(f"{BASE_URL}/operations", json=operation2_data)
    assert response.status_code == 201
    operation2 = response.json()
    operation2_id = operation2["operation_id"]
    print(f"✅ Created operations: OP{operation1['sequence_number']} (ID: {operation1_id}), OP{operation2['sequence_number']} (ID: {operation2_id})")
    
    return {
        'company_id': company_id,
        'machine_id': machine_id,
        'part1_id': part1_id,
        'part2_id': part2_id,
        'operation1_id': operation1_id,
        'operation2_id': operation2_id
    }

def test_no_conflict_scenario(test_data):
    """Test scenario where no conflicts exist."""
    print("🧪 Testing No Conflict Scenario...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create first schedule - should have no conflicts
    schedule1_data = {
        "date": today,
        "shift_number": 1,
        "slot_number": 1,
        "part_id": test_data['part1_id'],
        "operation_id": test_data['operation1_id'],
        "machine_id": test_data['machine_id'],
        "quantity_scheduled": 50,
        "sub_batch_id": "BATCH_NO_CONFLICT_1",
        "status": "planned"
    }
    
    response = requests.post(f"{BASE_URL}/production-schedules", json=schedule1_data)
    assert response.status_code == 201
    schedule1 = response.json()
    
    # Check warnings
    assert "warnings" in schedule1
    assert schedule1["warnings"]["conflicts_detected"] == False
    print(f"✅ Created schedule with no conflicts: {schedule1['warnings']['message']}")
    
    # Test conflict check endpoint for empty slot
    check_data = {
        "machine_id": test_data['machine_id'],
        "date": today,
        "shift_number": 1,
        "slot_number": 2  # Different slot
    }
    response = requests.post(f"{BASE_URL}/production-schedules/conflicts/check-slot", json=check_data)
    assert response.status_code == 200
    check_result = response.json()
    assert check_result["has_conflicts"] == False
    print(f"✅ Slot availability check passed: {check_result['message']}")
    
    return schedule1["schedule_id"]

def test_conflict_creation(test_data):
    """Test creating conflicting schedules."""
    print("🧪 Testing Conflict Creation...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create first schedule in a slot
    schedule1_data = {
        "date": today,
        "shift_number": 2,
        "slot_number": 1,
        "part_id": test_data['part1_id'],
        "operation_id": test_data['operation1_id'],
        "machine_id": test_data['machine_id'],
        "quantity_scheduled": 30,
        "sub_batch_id": "BATCH_CONFLICT_A",
        "status": "planned"
    }
    
    response = requests.post(f"{BASE_URL}/production-schedules", json=schedule1_data)
    assert response.status_code == 201
    schedule1 = response.json()
    schedule1_id = schedule1["schedule_id"]
    print(f"✅ Created first schedule (ID: {schedule1_id}) - no conflicts yet")
    
    # Create second schedule in the SAME slot - should create conflict
    schedule2_data = {
        "date": today,
        "shift_number": 2,
        "slot_number": 1,  # Same slot as schedule1
        "part_id": test_data['part2_id'],
        "operation_id": test_data['operation2_id'],
        "machine_id": test_data['machine_id'],
        "quantity_scheduled": 40,
        "sub_batch_id": "BATCH_CONFLICT_B",
        "status": "planned"
    }
    
    response = requests.post(f"{BASE_URL}/production-schedules", json=schedule2_data)
    assert response.status_code == 201
    schedule2 = response.json()
    schedule2_id = schedule2["schedule_id"]
    
    # Check that warning about conflict was returned
    assert "warnings" in schedule2
    assert schedule2["warnings"]["conflicts_detected"] == True
    assert "conflicts" in schedule2["warnings"]
    assert len(schedule2["warnings"]["conflicts"]) == 1
    assert schedule2["warnings"]["conflicts"][0]["schedule_id"] == schedule1_id
    print(f"✅ Created conflicting schedule (ID: {schedule2_id}) with proper warning")
    print(f"    Conflict detected with schedule {schedule1_id}")
    
    return schedule1_id, schedule2_id

def test_conflict_detection_endpoints(test_data, schedule1_id, schedule2_id):
    """Test the conflict detection API endpoints."""
    print("🧪 Testing Conflict Detection Endpoints...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Test get conflicts by date
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-date/{today}")
    assert response.status_code == 200
    date_conflicts = response.json()
    
    assert date_conflicts["date"] == today
    assert date_conflicts["conflicts_count"] >= 1
    print(f"✅ Found {date_conflicts['conflicts_count']} conflicts for date {today}")
    
    # Verify conflict details
    found_conflict = False
    for conflict in date_conflicts["conflicts"]:
        if (conflict["slot_info"]["machine_id"] == test_data['machine_id'] and 
            conflict["slot_info"]["shift_number"] == 2 and 
            conflict["slot_info"]["slot_number"] == 1):
            assert len(conflict["conflicting_schedules"]) == 2
            found_conflict = True
            print(f"✅ Verified conflict details: {len(conflict['conflicting_schedules'])} schedules in same slot")
            break
    
    assert found_conflict, "Expected conflict not found in date conflicts"
    
    # Test get conflicts by machine
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-machine/{test_data['machine_id']}")
    assert response.status_code == 200
    machine_conflicts = response.json()
    
    assert machine_conflicts["machine_id"] == test_data['machine_id']
    assert machine_conflicts["conflicts_count"] >= 1
    print(f"✅ Found {machine_conflicts['conflicts_count']} conflicts for machine {test_data['machine_id']}")
    
    # Test get conflicts by machine with date filter
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-machine/{test_data['machine_id']}?date={today}")
    assert response.status_code == 200
    machine_date_conflicts = response.json()
    
    assert machine_date_conflicts["machine_id"] == test_data['machine_id']
    assert machine_date_conflicts["date"] == today
    assert machine_date_conflicts["conflicts_count"] >= 1
    print(f"✅ Found {machine_date_conflicts['conflicts_count']} conflicts for machine {test_data['machine_id']} on {today}")
    
    # Test check slot conflicts endpoint
    check_data = {
        "machine_id": test_data['machine_id'],
        "date": today,
        "shift_number": 2,
        "slot_number": 1
    }
    response = requests.post(f"{BASE_URL}/production-schedules/conflicts/check-slot", json=check_data)
    assert response.status_code == 200
    slot_check = response.json()
    
    assert slot_check["has_conflicts"] == True
    assert slot_check["conflicts_count"] == 2
    assert "warning" in slot_check
    print(f"✅ Slot conflict check detected {slot_check['conflicts_count']} conflicts")
    print(f"    Warning: {slot_check['warning']}")

def test_conflict_update_scenario(test_data, schedule1_id):
    """Test updating a schedule and checking for new conflicts."""
    print("🧪 Testing Conflict Update Scenario...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Update schedule to move to a different slot (no conflict)
    update_data = {
        "shift_number": 1,
        "slot_number": 2,
        "quantity_scheduled": 60
    }
    
    response = requests.put(f"{BASE_URL}/production-schedules/{schedule1_id}", json=update_data)
    assert response.status_code == 200
    updated_schedule = response.json()
    
    # Should have no conflicts after moving to different slot
    assert "warnings" in updated_schedule
    assert updated_schedule["warnings"]["conflicts_detected"] == False
    print(f"✅ Updated schedule to new slot - no conflicts: {updated_schedule['warnings']['message']}")
    
    # Now update schedule back to conflicting slot
    conflict_update_data = {
        "shift_number": 2,
        "slot_number": 1  # Back to conflicting slot
    }
    
    response = requests.put(f"{BASE_URL}/production-schedules/{schedule1_id}", json=conflict_update_data)
    assert response.status_code == 200
    updated_schedule = response.json()
    
    # Should detect conflicts again
    assert "warnings" in updated_schedule
    assert updated_schedule["warnings"]["conflicts_detected"] == True
    print(f"✅ Updated schedule back to conflicting slot - conflicts detected: {updated_schedule['warnings']['message']}")

def test_edge_cases(test_data):
    """Test edge cases and error handling."""
    print("🧪 Testing Edge Cases...")
    
    # Test invalid date format
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-date/invalid-date")
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["error"]
    print("✅ Invalid date format handled correctly")
    
    # Test non-existent machine
    response = requests.get(f"{BASE_URL}/production-schedules/conflicts/by-machine/99999")
    assert response.status_code == 404
    print("✅ Non-existent machine handled correctly")
    
    # Test check slot with missing fields
    incomplete_data = {
        "machine_id": test_data['machine_id'],
        "date": datetime.now().strftime("%Y-%m-%d")
        # Missing shift_number and slot_number
    }
    response = requests.post(f"{BASE_URL}/production-schedules/conflicts/check-slot", json=incomplete_data)
    assert response.status_code == 400
    assert "Missing required fields" in response.json()["error"]
    print("✅ Missing required fields handled correctly")
    
    # Test check slot with invalid shift number
    invalid_shift_data = {
        "machine_id": test_data['machine_id'],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "shift_number": 3,  # Invalid
        "slot_number": 1
    }
    response = requests.post(f"{BASE_URL}/production-schedules/conflicts/check-slot", json=invalid_shift_data)
    assert response.status_code == 400
    assert "Shift number must be 1 or 2" in response.json()["error"]
    print("✅ Invalid shift number handled correctly")

def run_conflict_tests():
    """Run all conflict detection tests."""
    print("🚀 Starting Conflict Detection Tests")
    
    # Start Flask server
    print("\nStarting Flask server...")
    server_process = subprocess.Popen(
        ["python", "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("❌ Flask server failed to start")
            return False
        
        print("✅ Flask server is ready")
        
        # Setup test data
        test_data = setup_test_data()
        
        # Run conflict detection tests
        no_conflict_schedule_id = test_no_conflict_scenario(test_data)
        schedule1_id, schedule2_id = test_conflict_creation(test_data)
        test_conflict_detection_endpoints(test_data, schedule1_id, schedule2_id)
        test_conflict_update_scenario(test_data, no_conflict_schedule_id)
        test_edge_cases(test_data)
        
        print("\n🎉 All Conflict Detection tests passed!")
        return True
        
    finally:
        # Stop server
        print("✅ Flask server stopped")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    success = run_conflict_tests()
    if not success:
        exit(1)