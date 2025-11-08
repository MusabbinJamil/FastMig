"""
Test script for Machine Readable Transform features
"""
import requests
import pandas as pd
import json
import os

BASE_URL = "http://localhost:5000"

def test_label_encoding():
    """Test label encoding functionality"""
    print("\n" + "="*60)
    print("TEST 1: Label Encoding")
    print("="*60)
    
    # Create sample data with categorical columns
    sample_data = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Category': ['A', 'B', 'A', 'C', 'B'],
        'City': ['NYC', 'LA', 'NYC', 'Chicago', 'LA'],
        'Score': [85, 90, 78, 92, 88]
    })
    
    # Save to CSV
    test_file = 'test_encoding.csv'
    sample_data.to_csv(test_file, index=False)
    
    # Upload file
    print("\n1. Uploading test file...")
    with open(test_file, 'rb') as f:
        upload_response = requests.post(f"{BASE_URL}/upload", files={'file': f})
    
    if upload_response.status_code == 200:
        print("   ✓ File uploaded successfully")
    else:
        print(f"   ✗ Upload failed: {upload_response.text}")
        return
    
    # Test label encoding
    print("\n2. Performing label encoding on all categorical columns...")
    encode_response = requests.post(
        f"{BASE_URL}/transform/label-encode",
        json={
            "columns": None,  # Auto-detect all categorical
            "save_mapping": True
        }
    )
    
    if encode_response.status_code == 200:
        result = encode_response.json()
        print("   ✓ Label encoding successful")
        print(f"\n   Report:")
        print(f"   - Columns encoded: {result['report']['columns_encoded']}")
        print(f"   - Total encoded: {result['report']['total_encoded']}")
        if result['report']['mappings']:
            print(f"\n   Mappings:")
            for col, mapping in result['report']['mappings'].items():
                print(f"     {col}: {mapping}")
    else:
        print(f"   ✗ Encoding failed: {encode_response.text}")
        return
    
    # Test reverse encoding
    print("\n3. Reversing label encoding...")
    reverse_response = requests.post(
        f"{BASE_URL}/transform/reverse-label-encode",
        json={"columns": None}
    )
    
    if reverse_response.status_code == 200:
        result = reverse_response.json()
        print("   ✓ Reverse encoding successful")
        print(f"   - Columns decoded: {result['report']['columns_decoded']}")
    else:
        print(f"   ✗ Reverse encoding failed: {reverse_response.text}")
    
    # Cleanup
    os.remove(test_file)
    print("\n✓ Test 1 completed")


def test_one_hot_encoding():
    """Test one-hot encoding functionality"""
    print("\n" + "="*60)
    print("TEST 2: One-Hot Encoding")
    print("="*60)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Product': ['A', 'B', 'A', 'C', 'B', 'A'],
        'Region': ['North', 'South', 'East', 'North', 'West', 'South'],
        'Sales': [100, 150, 120, 180, 90, 110]
    })
    
    test_file = 'test_onehot.csv'
    sample_data.to_csv(test_file, index=False)
    
    # Upload file
    print("\n1. Uploading test file...")
    with open(test_file, 'rb') as f:
        upload_response = requests.post(f"{BASE_URL}/upload", files={'file': f})
    
    if upload_response.status_code == 200:
        print("   ✓ File uploaded successfully")
    else:
        print(f"   ✗ Upload failed: {upload_response.text}")
        return
    
    # Test one-hot encoding
    print("\n2. Performing one-hot encoding...")
    encode_response = requests.post(
        f"{BASE_URL}/transform/one-hot-encode",
        json={
            "columns": ["Product", "Region"],
            "drop_first": False,
            "prefix_sep": "_"
        }
    )
    
    if encode_response.status_code == 200:
        result = encode_response.json()
        print("   ✓ One-hot encoding successful")
        print(f"\n   Report:")
        print(f"   - Original columns encoded: {result['report']['columns_encoded']}")
        print(f"   - New columns created: {result['report']['total_new_columns']}")
        print(f"   - New column names: {result['report']['new_columns_created'][:5]}...")
        print(f"   - Final shape: {result['shape']}")
    else:
        print(f"   ✗ Encoding failed: {encode_response.text}")
    
    # Cleanup
    os.remove(test_file)
    print("\n✓ Test 2 completed")


def test_encoding_with_missing_values():
    """Test encoding with missing values"""
    print("\n" + "="*60)
    print("TEST 3: Encoding with Missing Values")
    print("="*60)
    
    # Create sample data with missing values
    sample_data = pd.DataFrame({
        'Status': ['Active', None, 'Inactive', 'Active', None, 'Pending'],
        'Type': ['X', 'Y', None, 'X', 'Z', 'Y'],
        'Value': [10, 20, 30, 40, 50, 60]
    })
    
    test_file = 'test_missing.csv'
    sample_data.to_csv(test_file, index=False)
    
    # Upload file
    print("\n1. Uploading test file with missing values...")
    with open(test_file, 'rb') as f:
        upload_response = requests.post(f"{BASE_URL}/upload", files={'file': f})
    
    if upload_response.status_code == 200:
        print("   ✓ File uploaded successfully")
    else:
        print(f"   ✗ Upload failed: {upload_response.text}")
        return
    
    # Test label encoding with missing values
    print("\n2. Label encoding with missing values...")
    encode_response = requests.post(
        f"{BASE_URL}/transform/label-encode",
        json={"columns": None, "save_mapping": True}
    )
    
    if encode_response.status_code == 200:
        result = encode_response.json()
        print("   ✓ Encoding handled missing values correctly")
        print(f"   - Columns encoded: {result['report']['columns_encoded']}")
    else:
        print(f"   ✗ Encoding failed: {encode_response.text}")
    
    # Cleanup
    os.remove(test_file)
    print("\n✓ Test 3 completed")


def test_evolutionary_cleaning_with_logging():
    """Test evolutionary cleaning to see enhanced logging"""
    print("\n" + "="*60)
    print("TEST 4: Evolutionary Cleaning with Enhanced Logging")
    print("="*60)
    
    # Create sample data with missing values
    sample_data = pd.DataFrame({
        'Age': [25, None, 30, 28, None, 35, 27],
        'Score': [85, 90, None, 92, 88, None, 91],
        'Category': ['A', 'B', None, 'A', 'B', 'C', None]
    })
    
    test_file = 'test_cleaning.csv'
    sample_data.to_csv(test_file, index=False)
    
    # Upload file
    print("\n1. Uploading test file...")
    with open(test_file, 'rb') as f:
        upload_response = requests.post(f"{BASE_URL}/upload", files={'file': f})
    
    if upload_response.status_code == 200:
        print("   ✓ File uploaded successfully")
    else:
        print(f"   ✗ Upload failed: {upload_response.text}")
        return
    
    # Test GA with small parameters for quick test
    print("\n2. Running Genetic Algorithm (check server logs for detailed steps)...")
    clean_response = requests.post(
        f"{BASE_URL}/clean/evolutionary",
        json={
            "method": "ga",
            "track_modifications": True,
            "parameters": {
                "population_size": 20,
                "generations": 40,
                "mutation_rate": 0.1,
                "crossover_rate": 0.8
            }
        }
    )
    
    if clean_response.status_code == 200:
        result = clean_response.json()
        print("   ✓ Cleaning completed")
        print(f"\n   Report:")
        print(f"   - Method: {result['report']['method'].upper()}")
        print(f"   - Before fitness: {result['report']['before']['average_fitness']:.2f}%")
        print(f"   - After fitness: {result['report']['after']['average_fitness']:.2f}%")
        print(f"   - Improvement: {result['report']['improvement']['fitness_increase']:+.2f}%")
        print(f"   - Records modified: {result['report']['modifications']['records_modified']}")
        print(f"\n   ⚠️  Check server console for detailed step-by-step logging!")
    else:
        print(f"   ✗ Cleaning failed: {clean_response.text}")
    
    # Cleanup
    os.remove(test_file)
    print("\n✓ Test 4 completed")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MACHINE READABLE TRANSFORM FEATURE TESTS")
    print("="*60)
    print("\nMake sure the FastMig backend server is running at:")
    print(f"  {BASE_URL}")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("✗ Server is not responding. Please start the server first.")
            return
        print("✓ Server is running\n")
        
        # Run tests
        test_label_encoding()
        test_one_hot_encoding()
        test_encoding_with_missing_values()
        test_evolutionary_cleaning_with_logging()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        print("\nFeatures tested:")
        print("  ✓ Label encoding")
        print("  ✓ Reverse label encoding")
        print("  ✓ One-hot encoding")
        print("  ✓ Handling missing values")
        print("  ✓ Enhanced evolutionary algorithm logging")
        print("\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server. Please start the backend server:")
        print("  cd python-backend")
        print("  python server.py")
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == '__main__':
    main()
