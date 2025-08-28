#!/usr/bin/env python3
"""
Test script for the new schedule API endpoints.
This script tests the monthly plan and forecast plan APIs.
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

def test_monthly_plans():
    """Test monthly plan CRUD operations."""
    print("🧪 Testing Monthly Plans API...")
    
    # Create test company
    company_data = {"name": "Test Company for Schedules"}
    response = requests.post(f"{BASE_URL}/companies", json=company_data)
    assert response.status_code == 201
    company = response.json()
    company_id = company["company_id"]
    print(f"✅ Created company: {company['name']} (ID: {company_id})")
    
    # Create test part
    part_data = {"name": "Test Part for Schedules", "company_id": company_id, "total_operations": 3}
    response = requests.post(f"{BASE_URL}/parts", json=part_data)
    assert response.status_code == 201
    part = response.json()
    part_id = part["part_id"]
    print(f"✅ Created part: {part['name']} (ID: {part_id})")
    
    # Test CREATE monthly plan
    month = (datetime.now().replace(day=1)).strftime("%Y-%m-%d")
    plan_data = {
        "part_id": part_id,
        "company_id": company_id,
        "month": month,
        "planned_quantity": 100
    }
    response = requests.post(f"{BASE_URL}/monthly-plans", json=plan_data)
    assert response.status_code == 201
    plan = response.json()
    plan_id = plan["plan_id"]
    print(f"✅ Created monthly plan (ID: {plan_id}) with quantity: {plan['planned_quantity']}")
    
    # Test GET monthly plan
    response = requests.get(f"{BASE_URL}/monthly-plans/{plan_id}")
    assert response.status_code == 200
    retrieved_plan = response.json()
    assert retrieved_plan["planned_quantity"] == 100
    print(f"✅ Retrieved monthly plan: {retrieved_plan['planned_quantity']} units")
    
    # Test UPDATE monthly plan
    update_data = {"planned_quantity": 150}
    response = requests.put(f"{BASE_URL}/monthly-plans/{plan_id}", json=update_data)
    assert response.status_code == 200
    updated_plan = response.json()
    assert updated_plan["planned_quantity"] == 150
    print(f"✅ Updated monthly plan quantity to: {updated_plan['planned_quantity']}")
    
    # Test SUPERSEDE functionality - create another plan for same company/part/month
    supersede_data = {
        "part_id": part_id,
        "company_id": company_id,
        "month": month,
        "planned_quantity": 200
    }
    response = requests.post(f"{BASE_URL}/monthly-plans", json=supersede_data)
    assert response.status_code == 201
    new_plan = response.json()
    new_plan_id = new_plan["plan_id"]
    assert new_plan["planned_quantity"] == 200
    print(f"✅ Created superseding plan (ID: {new_plan_id}) with quantity: {new_plan['planned_quantity']}")
    
    # Verify old plan was superseded
    response = requests.get(f"{BASE_URL}/monthly-plans")
    assert response.status_code == 200
    all_plans = response.json()
    matching_plans = [p for p in all_plans if p["part_id"] == part_id and p["company_id"] == company_id and p["month"] == month]
    assert len(matching_plans) == 1  # Only one plan should exist for this company/part/month
    assert matching_plans[0]["plan_id"] == new_plan_id  # Should be the new plan
    print(f"✅ Verified supersede logic: only 1 plan exists for company/part/month")
    
    # Test error cases
    # Invalid part ID
    invalid_data = {"part_id": 9999, "company_id": company_id, "month": month, "planned_quantity": 50}
    response = requests.post(f"{BASE_URL}/monthly-plans", json=invalid_data)
    assert response.status_code == 404
    assert "Part not found" in response.json()["error"]
    print(f"✅ Validated error handling for non-existent part")
    
    # Invalid date format
    invalid_date_data = {"part_id": part_id, "company_id": company_id, "month": "invalid-date", "planned_quantity": 50}
    response = requests.post(f"{BASE_URL}/monthly-plans", json=invalid_date_data)
    assert response.status_code == 400
    assert "Invalid month format" in response.json()["error"]
    print(f"✅ Validated error handling for invalid date format")
    
    print("✅ Monthly Plans API tests completed successfully!\n")
    return company_id, part_id

def test_forecast_plans(company_id, part_id):
    """Test forecast plan CRUD operations."""
    print("🧪 Testing Forecast Plans API...")
    
    # Test CREATE forecast plan
    next_month = (datetime.now().replace(day=1) + timedelta(days=32)).strftime("%Y-%m-%d")
    forecast_data = {
        "part_id": part_id,
        "company_id": company_id,
        "month": next_month,
        "week": 1,
        "forecasted_quantity": 25
    }
    response = requests.post(f"{BASE_URL}/forecast-plans", json=forecast_data)
    assert response.status_code == 201
    forecast = response.json()
    forecast_id = forecast["forecast_id"]
    print(f"✅ Created forecast plan (ID: {forecast_id}) for week {forecast['week']} with quantity: {forecast['forecasted_quantity']}")
    
    # Test GET forecast plan
    response = requests.get(f"{BASE_URL}/forecast-plans/{forecast_id}")
    assert response.status_code == 200
    retrieved_forecast = response.json()
    assert retrieved_forecast["forecasted_quantity"] == 25
    print(f"✅ Retrieved forecast plan: {retrieved_forecast['forecasted_quantity']} units")
    
    # Test UPDATE forecast plan
    update_data = {"forecasted_quantity": 35}
    response = requests.put(f"{BASE_URL}/forecast-plans/{forecast_id}", json=update_data)
    assert response.status_code == 200
    updated_forecast = response.json()
    assert updated_forecast["forecasted_quantity"] == 35
    print(f"✅ Updated forecast plan quantity to: {updated_forecast['forecasted_quantity']}")
    
    # Create another forecast plan for different week
    forecast_data2 = {
        "part_id": part_id,
        "company_id": company_id,
        "month": next_month,
        "week": 2,
        "forecasted_quantity": 30
    }
    response = requests.post(f"{BASE_URL}/forecast-plans", json=forecast_data2)
    assert response.status_code == 201
    forecast2 = response.json()
    print(f"✅ Created forecast plan for week {forecast2['week']} with quantity: {forecast2['forecasted_quantity']}")
    
    # Test SUPERSEDE functionality - create another plan for same company/part/month/week
    supersede_data = {
        "part_id": part_id,
        "company_id": company_id,
        "month": next_month,
        "week": 1,
        "forecasted_quantity": 40
    }
    response = requests.post(f"{BASE_URL}/forecast-plans", json=supersede_data)
    assert response.status_code == 201
    new_forecast = response.json()
    new_forecast_id = new_forecast["forecast_id"]
    assert new_forecast["forecasted_quantity"] == 40
    print(f"✅ Created superseding forecast (ID: {new_forecast_id}) with quantity: {new_forecast['forecasted_quantity']}")
    
    # Verify old forecast was superseded
    response = requests.get(f"{BASE_URL}/forecast-plans")
    assert response.status_code == 200
    all_forecasts = response.json()
    matching_forecasts = [f for f in all_forecasts if f["part_id"] == part_id and f["company_id"] == company_id and f["month"] == next_month and f["week"] == 1]
    assert len(matching_forecasts) == 1  # Only one forecast should exist for this company/part/month/week
    assert matching_forecasts[0]["forecast_id"] == new_forecast_id  # Should be the new forecast
    print(f"✅ Verified supersede logic: only 1 forecast exists for company/part/month/week")
    
    # Test error cases
    # Invalid week number
    invalid_week_data = {"part_id": part_id, "company_id": company_id, "month": next_month, "week": 5, "forecasted_quantity": 25}
    response = requests.post(f"{BASE_URL}/forecast-plans", json=invalid_week_data)
    assert response.status_code == 400
    assert "Week number must be between 1 and 4" in response.json()["error"]
    print(f"✅ Validated error handling for invalid week number")
    
    # Invalid company ID
    invalid_company_data = {"part_id": part_id, "company_id": 9999, "month": next_month, "week": 1, "forecasted_quantity": 25}
    response = requests.post(f"{BASE_URL}/forecast-plans", json=invalid_company_data)
    assert response.status_code == 404
    assert "Company not found" in response.json()["error"]
    print(f"✅ Validated error handling for non-existent company")
    
    print("✅ Forecast Plans API tests completed successfully!\n")

def test_forecast_data_separation():
    """Test that forecast data is stored separately from monthly plans."""
    print("🧪 Testing Data Separation...")
    
    # Get counts of each type
    response = requests.get(f"{BASE_URL}/test-db")
    assert response.status_code == 200
    counts = response.json()["tables"]
    
    print(f"✅ Monthly plans count: {counts['monthly_plans']}")
    print(f"✅ Forecast plans count: {counts['forecast_plans']}")
    
    # Verify they are stored in separate tables
    assert counts["monthly_plans"] > 0
    assert counts["forecast_plans"] > 0
    print("✅ Verified forecast data is stored separately from monthly plans\n")

def main():
    """Main test function."""
    print("🚀 Starting Schedule API Tests\n")
    
    # Start Flask server
    print("Starting Flask server...")
    server_process = subprocess.Popen(
        ["python", "run.py"],
        cwd="/home/runner/work/scheduling_software/scheduling_software/backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("❌ Failed to start Flask server")
            return False
        
        print("✅ Flask server is ready\n")
        
        # Run tests
        company_id, part_id = test_monthly_plans()
        test_forecast_plans(company_id, part_id)
        test_forecast_data_separation()
        
        print("🎉 All Schedule API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Stop Flask server
        server_process.send_signal(signal.SIGINT)
        server_process.wait()
        print("✅ Flask server stopped")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)