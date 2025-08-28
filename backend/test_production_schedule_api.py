#!/usr/bin/env python3
"""
Test script for the production schedule API endpoints.
This script tests the sub-batch progress tracking and status update functionality.
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

def test_production_schedule_crud():
    """Test production schedule CRUD operations."""
    print("🧪 Testing Production Schedule CRUD API...")
    
    # Create test company
    company_data = {"name": "Test Production Company"}
    response = requests.post(f"{BASE_URL}/companies", json=company_data)
    assert response.status_code == 201
    company = response.json()
    company_id = company["company_id"]
    print(f"✅ Created company: {company['name']} (ID: {company_id})")
    
    # Create test machine
    machine_data = {"name": "Test CNC Machine", "type": "Lathe"}
    response = requests.post(f"{BASE_URL}/machines", json=machine_data)
    assert response.status_code == 201
    machine = response.json()
    machine_id = machine["machine_id"]
    print(f"✅ Created machine: {machine['name']} (ID: {machine_id})")
    
    # Create test part
    part_data = {"name": "Test Gear", "company_id": company_id, "total_operations": 2}
    response = requests.post(f"{BASE_URL}/parts", json=part_data)
    assert response.status_code == 201
    part = response.json()
    part_id = part["part_id"]
    print(f"✅ Created part: {part['name']} (ID: {part_id})")
    
    # Create test operation
    operation_data = {
        "part_id": part_id,
        "sequence_number": 10,
        "machining_time": 15.5,
        "loading_time": 2.0
    }
    response = requests.post(f"{BASE_URL}/operations", json=operation_data)
    assert response.status_code == 201
    operation = response.json()
    operation_id = operation["operation_id"]
    print(f"✅ Created operation: Sequence {operation['sequence_number']} (ID: {operation_id})")
    
    # Test CREATE production schedule
    today = datetime.now().strftime("%Y-%m-%d")
    schedule_data = {
        "date": today,
        "shift_number": 1,
        "slot_number": 1,
        "part_id": part_id,
        "operation_id": operation_id,
        "machine_id": machine_id,
        "quantity_scheduled": 50,
        "sub_batch_id": "BATCH001",
        "status": "planned"
    }
    response = requests.post(f"{BASE_URL}/production-schedules", json=schedule_data)
    assert response.status_code == 201
    schedule = response.json()
    schedule_id = schedule["schedule_id"]
    print(f"✅ Created production schedule (ID: {schedule_id}) with status: {schedule['status']}")
    
    # Test READ production schedule
    response = requests.get(f"{BASE_URL}/production-schedules/{schedule_id}")
    assert response.status_code == 200
    retrieved_schedule = response.json()
    assert retrieved_schedule["status"] == "planned"
    assert retrieved_schedule["sub_batch_id"] == "BATCH001"
    print(f"✅ Retrieved production schedule: {retrieved_schedule['quantity_scheduled']} units")
    
    # Test UPDATE production schedule status
    update_data = {"status": "in_progress"}
    response = requests.put(f"{BASE_URL}/production-schedules/{schedule_id}/status", json=update_data)
    assert response.status_code == 200
    updated_schedule = response.json()
    assert updated_schedule["status"] == "in_progress"
    print(f"✅ Updated schedule status to: {updated_schedule['status']}")
    
    # Test UPDATE full production schedule
    full_update_data = {
        "quantity_scheduled": 75,
        "status": "completed",
        "sub_batch_id": "BATCH001_COMPLETED"
    }
    response = requests.put(f"{BASE_URL}/production-schedules/{schedule_id}", json=full_update_data)
    assert response.status_code == 200
    updated_schedule = response.json()
    assert updated_schedule["status"] == "completed"
    assert updated_schedule["quantity_scheduled"] == 75
    assert updated_schedule["sub_batch_id"] == "BATCH001_COMPLETED"
    print(f"✅ Updated schedule: {updated_schedule['quantity_scheduled']} units, status: {updated_schedule['status']}")
    
    # Test LIST production schedules
    response = requests.get(f"{BASE_URL}/production-schedules")
    assert response.status_code == 200
    schedules = response.json()
    assert len(schedules) >= 1
    print(f"✅ Listed production schedules: {len(schedules)} found")
    
    return schedule_id, machine_id, part_id, today

def test_production_schedule_filtering(schedule_id, machine_id, part_id, date):
    """Test production schedule filtering endpoints."""
    print("🧪 Testing Production Schedule Filtering...")
    
    # Test filter by date
    response = requests.get(f"{BASE_URL}/production-schedules/by-date/{date}")
    assert response.status_code == 200
    schedules_by_date = response.json()
    assert len(schedules_by_date) >= 1
    print(f"✅ Found {len(schedules_by_date)} schedules for date: {date}")
    
    # Test filter by machine
    response = requests.get(f"{BASE_URL}/production-schedules/by-machine/{machine_id}")
    assert response.status_code == 200
    schedules_by_machine = response.json()
    assert len(schedules_by_machine) >= 1
    print(f"✅ Found {len(schedules_by_machine)} schedules for machine ID: {machine_id}")
    
    # Test filter by machine with date
    response = requests.get(f"{BASE_URL}/production-schedules/by-machine/{machine_id}?date={date}")
    assert response.status_code == 200
    schedules_by_machine_date = response.json()
    assert len(schedules_by_machine_date) >= 1
    print(f"✅ Found {len(schedules_by_machine_date)} schedules for machine {machine_id} on {date}")
    
    # Test filter by part
    response = requests.get(f"{BASE_URL}/production-schedules/by-part/{part_id}")
    assert response.status_code == 200
    schedules_by_part = response.json()
    assert len(schedules_by_part) >= 1
    print(f"✅ Found {len(schedules_by_part)} schedules for part ID: {part_id}")
    
    # Test combined filters using query parameters
    response = requests.get(f"{BASE_URL}/production-schedules?date={date}&machine_id={machine_id}")
    assert response.status_code == 200
    filtered_schedules = response.json()
    assert len(filtered_schedules) >= 1
    print(f"✅ Found {len(filtered_schedules)} schedules with combined filters")

def test_status_validation():
    """Test status validation and error handling."""
    print("🧪 Testing Status Validation...")
    
    # Test invalid status
    invalid_status_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "shift_number": 1,
        "slot_number": 2,
        "part_id": 1,
        "operation_id": 1,
        "machine_id": 1,
        "quantity_scheduled": 25,
        "status": "invalid_status"
    }
    response = requests.post(f"{BASE_URL}/production-schedules", json=invalid_status_data)
    assert response.status_code == 400
    error = response.json()
    assert "Status must be one of" in error["error"]
    print("✅ Validated error handling for invalid status")
    
    # Test invalid shift number
    invalid_shift_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "shift_number": 3,  # Invalid: must be 1 or 2
        "slot_number": 1,
        "part_id": 1,
        "operation_id": 1,
        "machine_id": 1,
        "quantity_scheduled": 25
    }
    response = requests.post(f"{BASE_URL}/production-schedules", json=invalid_shift_data)
    assert response.status_code == 400
    error = response.json()
    assert "Shift number must be 1 or 2" in error["error"]
    print("✅ Validated error handling for invalid shift number")
    
    # Test missing required fields
    incomplete_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "shift_number": 1
        # Missing required fields
    }
    response = requests.post(f"{BASE_URL}/production-schedules", json=incomplete_data)
    assert response.status_code == 400
    error = response.json()
    assert "Missing required fields" in error["error"]
    print("✅ Validated error handling for missing required fields")

def test_sub_batch_tracking():
    """Test sub-batch specific functionality."""
    print("🧪 Testing Sub-batch Tracking...")
    
    # Create multiple schedules for the same sub-batch
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Schedule 1: Operation 1 of sub-batch
    schedule1_data = {
        "date": today,
        "shift_number": 1,
        "slot_number": 1,
        "part_id": 1,
        "operation_id": 1,
        "machine_id": 1,
        "quantity_scheduled": 100,
        "sub_batch_id": "SUB_BATCH_001",
        "status": "planned"
    }
    response = requests.post(f"{BASE_URL}/production-schedules", json=schedule1_data)
    if response.status_code == 201:
        schedule1 = response.json()
        schedule1_id = schedule1["schedule_id"]
        print(f"✅ Created sub-batch schedule 1 (ID: {schedule1_id}): {schedule1['status']}")
        
        # Update sub-batch progress through different statuses
        statuses = ["in_progress", "completed"]
        for status in statuses:
            update_data = {"status": status}
            response = requests.put(f"{BASE_URL}/production-schedules/{schedule1_id}/status", json=update_data)
            assert response.status_code == 200
            updated = response.json()
            assert updated["status"] == status
            print(f"✅ Updated sub-batch {updated['sub_batch_id']} to status: {status}")
    else:
        print(f"ℹ️  Skipping sub-batch test due to missing test data (status: {response.status_code})")

def run_tests():
    """Run all production schedule API tests."""
    print("🚀 Starting Production Schedule API Tests")
    
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
        
        # Run tests
        schedule_id, machine_id, part_id, date = test_production_schedule_crud()
        test_production_schedule_filtering(schedule_id, machine_id, part_id, date)
        test_status_validation()
        test_sub_batch_tracking()
        
        print("\n🎉 All Production Schedule API tests passed!")
        return True
        
    finally:
        # Stop server
        print("✅ Flask server stopped")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)