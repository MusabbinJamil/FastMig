"""
Test script for ETL Operations and Step Recording
Run this after starting the server to verify functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test if server is running"""
    print("\n" + "="*60)
    print("Testing Server Health...")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_etl_operations():
    """Test ETL operations"""
    print("\n" + "="*60)
    print("Testing ETL Operations...")
    print("="*60)
    
    # Create sample data
    import pandas as pd
    import os
    
    sample_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 5],  # Duplicate ID
        'name': ['  John  ', 'JANE', 'bob', None, 'Alice', 'Alice'],  # Whitespace, case issues, null
        'age': [25, None, 35, 40, 30, 30],  # Null value
        'status': ['active', 'inactive', 'active', 'pending', 'active', 'active'],
        'email': ['john@test.com', 'jane@test.com', 'bob@test.com', 'test@test.com', 'alice@test.com', 'alice@test.com']
    })
    
    # Save to temp file
    temp_file = 'test_data_etl.csv'
    sample_data.to_csv(temp_file, index=False)
    print(f"\nCreated test file: {temp_file}")
    print(f"Original data shape: {sample_data.shape}")
    print(f"Original data:\n{sample_data}")
    
    # Upload file
    print("\n1. Uploading file...")
    with open(temp_file, 'rb') as f:
        files = {'file': (temp_file, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return False
    
    result = response.json()
    print(f"✓ Uploaded successfully. Shape: {result['shape']}")
    
    # Start recording steps
    print("\n2. Starting step recording...")
    response = requests.post(f"{BASE_URL}/steps/start")
    print(f"✓ Recording started: {response.json()}")
    
    # Test: Trim whitespace
    print("\n3. Trimming whitespace...")
    response = requests.post(f"{BASE_URL}/etl/trim-whitespace", json={
        "columns": ["name"]
    })
    result = response.json()
    print(f"✓ {result['message']}")
    print(f"   Modifications: {result['report']['modifications_made']}")
    
    # Test: Change case
    print("\n4. Changing case to title...")
    response = requests.post(f"{BASE_URL}/etl/change-case", json={
        "column": "name",
        "case_type": "title"
    })
    result = response.json()
    print(f"✓ {result['message']}")
    
    # Test: Fill nulls
    print("\n5. Filling null values in 'age' with median...")
    response = requests.post(f"{BASE_URL}/etl/fill-nulls", json={
        "column": "age",
        "method": "median"
    })
    result = response.json()
    print(f"✓ {result['message']}")
    print(f"   Filled: {result['report']['nulls_filled']}, Remaining: {result['report']['nulls_remaining']}")
    
    # Test: Remove duplicates
    print("\n6. Removing duplicate rows...")
    response = requests.post(f"{BASE_URL}/etl/remove-duplicates", json={
        "keep": "first"
    })
    result = response.json()
    print(f"✓ {result['message']}")
    print(f"   Rows removed: {result['report']['rows_removed']}")
    
    # Test: Remove nulls
    print("\n7. Removing rows with null values...")
    response = requests.post(f"{BASE_URL}/etl/remove-nulls", json={
        "how": "any"
    })
    result = response.json()
    print(f"✓ {result['message']}")
    print(f"   Rows removed: {result['report']['rows_removed']}")
    
    # Test: Find and replace
    print("\n8. Replacing 'pending' with 'review'...")
    response = requests.post(f"{BASE_URL}/etl/find-replace", json={
        "column": "status",
        "find_value": "pending",
        "replace_value": "review"
    })
    result = response.json()
    print(f"✓ {result['message']}")
    
    # Test: Filter rows
    print("\n9. Filtering active users only...")
    response = requests.post(f"{BASE_URL}/etl/filter-rows", json={
        "column": "status",
        "operator": "==",
        "value": "active"
    })
    result = response.json()
    print(f"✓ {result['message']}")
    print(f"   Final shape: {result['shape']}")
    
    # Test: Sort data
    print("\n10. Sorting by name...")
    response = requests.post(f"{BASE_URL}/etl/sort-data", json={
        "columns": ["name"],
        "ascending": True
    })
    result = response.json()
    print(f"✓ {result['message']}")
    
    # Stop recording
    print("\n11. Stopping step recording...")
    response = requests.post(f"{BASE_URL}/steps/stop")
    result = response.json()
    print(f"✓ Stopped. Total steps: {result['steps_count']}")
    
    # Get recorded steps
    print("\n12. Getting recorded steps...")
    response = requests.get(f"{BASE_URL}/steps/get")
    result = response.json()
    print(f"✓ Retrieved {result['steps_count']} steps")
    print("\nRecorded steps:")
    for i, step in enumerate(result['steps'], 1):
        print(f"   {i}. {step['operation']}")
    
    # Save steps
    print("\n13. Saving steps...")
    response = requests.post(f"{BASE_URL}/steps/save", json={
        "name": "test_etl_pipeline"
    })
    result = response.json()
    print(f"✓ {result['message']}")
    
    # Test replay on fresh data
    print("\n14. Testing step replay on new data...")
    
    # Create new sample data with similar structure
    new_data = pd.DataFrame({
        'id': [10, 11, 12, 13, 14, 14],
        'name': ['  DAVID  ', 'emma', 'FRANK', None, '  grace  ', '  grace  '],
        'age': [28, 32, None, 45, 27, 27],
        'status': ['inactive', 'active', 'pending', 'active', 'active', 'active'],
        'email': ['david@test.com', 'emma@test.com', 'frank@test.com', 'test2@test.com', 'grace@test.com', 'grace@test.com']
    })
    
    new_file = 'test_data_new.csv'
    new_data.to_csv(new_file, index=False)
    print(f"Created new test file: {new_file}")
    print(f"New data shape: {new_data.shape}")
    
    # Replay steps
    response = requests.post(f"{BASE_URL}/steps/replay", json={
        "file_path": new_file
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Replay successful!")
        print(f"   Steps applied: {result['steps_applied']}")
        print(f"   Final shape: {result['shape']}")
        print(f"\n   Transformation reports:")
        for report in result['reports']:
            if 'operation' in report:
                print(f"   - {report['operation']}: {report}")
    else:
        print(f"✗ Replay failed: {response.text}")
    
    # Cleanup
    print("\n15. Cleaning up test files...")
    import os
    try:
        os.remove(temp_file)
        os.remove(new_file)
        print("✓ Test files removed")
    except:
        pass
    
    print("\n" + "="*60)
    print("ETL Operations Test Complete!")
    print("="*60)
    
    return True

def test_status():
    """Test status endpoint"""
    print("\n" + "="*60)
    print("Testing Status Endpoint...")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/status")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Status retrieved:")
        print(f"   Is Recording: {result.get('is_recording')}")
        print(f"   Recorded Steps: {result.get('recorded_steps_count')}")
        print(f"   Has Data: {result.get('has_data')}")
        print(f"   Current File: {result.get('current_file')}")
        print(f"   Data Shape: {result.get('data_shape')}")
        return True
    else:
        print(f"✗ Status check failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*10 + "FastMig ETL Operations & Step Recording Test Suite")
    print("="*70)
    
    # Test 1: Health check
    if not test_health():
        print("\n✗ Server is not running. Please start the server first.")
        print("   Run: python server.py")
        return
    
    # Test 2: ETL operations
    try:
        test_etl_operations()
    except Exception as e:
        print(f"\n✗ ETL test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Status
    test_status()
    
    print("\n" + "="*70)
    print(" "*20 + "All Tests Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Check the saved steps in: recordings/test_etl_pipeline.json")
    print("2. Review the ETL Operations Guide: docs/ETL_OPERATIONS_GUIDE.md")
    print("3. Integrate with your Flutter frontend")
    print("\n")

if __name__ == "__main__":
    main()
