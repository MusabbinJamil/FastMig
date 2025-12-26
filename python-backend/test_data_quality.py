"""
Test suite for DataQualityAnalyzer
Tests various data quality scenarios
"""

import pandas as pd
import numpy as np
from data_quality_analyzer import DataQualityAnalyzer, get_quality_report


def test_missing_values():
    """Test detection of missing values"""
    df = pd.DataFrame({
        'Prices': [10, 25, None, 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'Procurement': ['2024-01-09', '2024-01-10', '2024-01-11', None]
    })
    
    report = get_quality_report(df)
    
    assert len(report['error_cells']) == 2
    assert any(e['row'] == 3 and e['col'] == 0 and 'missing_value' in e['issues'] 
               for e in report['error_cells'])
    assert any(e['row'] == 4 and e['col'] == 2 and 'missing_value' in e['issues'] 
               for e in report['error_cells'])
    
    print("✓ Missing values test passed")


def test_non_numeric_in_numeric_column():
    """Test detection of non-numeric values in numeric columns"""
    df = pd.DataFrame({
        'Prices': [10, 25, 'abc', 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'Quantity': [5, 10, 15, 20]
    })
    
    report = get_quality_report(df)
    
    # Should detect 'abc' in Prices column
    assert any(e['row'] == 3 and e['col'] == 0 and 'non_numeric' in e['issues']
               for e in report['error_cells'])
    
    print("✓ Non-numeric in numeric column test passed")


def test_type_inference():
    """Test automatic type inference"""
    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'Dates': ['2024-01-09', '2024-01-10', '2024-01-11', '2024-01-12']
    })
    
    report = get_quality_report(df)
    
    assert report['column_types']['Prices'] == 'numeric'
    assert report['column_types']['Product'] == 'string'
    assert report['column_types']['Dates'] == 'datetime'
    
    print("✓ Type inference test passed")


def test_mixed_content():
    """Test detection of mixed content"""
    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'MixedCol': [100, 200, '300px', 400]  # Mixed number and text
    })
    
    report = get_quality_report(df)
    
    # Should detect mixed content in MixedCol
    assert any('mixed_content' in e['issues'] or 'non_numeric' in e['issues']
               for e in report['error_cells'])
    
    print("✓ Mixed content test passed")


def test_null_strings():
    """Test detection of null-like strings"""
    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'Product': ['Apple', 'n/a', 'Mango', 'N/A'],
        'Notes': ['Good', 'null', 'Great', 'none']
    })
    
    report = get_quality_report(df)
    
    # Should detect null-like strings
    error_issues = [issue for e in report['error_cells'] for issue in e['issues']]
    assert 'null_string' in error_issues
    
    print("✓ Null-like strings test passed")

def test_numeric_in_string_column():
    """Test detection of purely numeric values in string columns"""
    df = pd.DataFrame({
        'Product': ['Apple', 'Banana', '12', 'Orange', '456', 'Grape'],
        'Description': ['Fresh fruit', 'Yellow', 'iPhone 12', 'Citrus', 'Good', 'Purple'],
        'Quantity': [10, 20, 30, 40, 50, 60]
    })
    
    report = get_quality_report(df)
    
    # Should detect '12' and '456' as purely numeric in Product column
    assert any(e['row'] == 3 and e['col'] == 0 and 'suspicious_numeric_in_string' in e['issues']
               for e in report['error_cells']), \
        "Expected '12' in Product column (row 3) to be flagged"
    
    assert any(e['row'] == 5 and e['col'] == 0 and 'suspicious_numeric_in_string' in e['issues']
               for e in report['error_cells']), \
        "Expected '456' in Product column (row 5) to be flagged"
    
    # Should NOT detect 'iPhone 12' in Description column as it's a legitimate product name
    assert not any(e['row'] == 3 and e['col'] == 1 and 'suspicious_numeric_in_string' in e['issues']
                   for e in report['error_cells']), \
        "'iPhone 12' in Description should NOT be flagged as it contains text"
    
    print("✓ Numeric in string column test passed")



def test_empty_dataframe_handling():
    """Test handling of empty dataframes"""
    df = pd.DataFrame()
    
    report = get_quality_report(df)
    
    # Should not crash
    assert report['success'] == True
    assert report['shape'] == (0, 0)
    
    print("✓ Empty dataframe test passed")


def test_single_column():
    """Test handling of single column dataframe"""
    df = pd.DataFrame({
        'Prices': [10, 25, 'abc', 40]
    })
    
    report = get_quality_report(df)
    
    assert report['shape'] == (4, 1)
    assert report['column_types']['Prices'] == 'numeric'
    assert len(report['error_cells']) > 0  # Should detect 'abc'
    
    print("✓ Single column test passed")


def test_all_null_column():
    """Test handling of all-null columns"""
    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'EmptyCol': [None, None, None, None],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana']
    })
    
    report = get_quality_report(df)
    
    # Empty column should have type 'unknown'
    assert report['column_types']['EmptyCol'] == 'unknown'
    
    # All cells in empty column should be marked as missing
    error_count = sum(1 for e in report['error_cells'] if e['col'] == 1)
    assert error_count == 4
    
    print("✓ All-null column test passed")


def test_realistic_data():
    """Test with realistic messy data"""
    df = pd.DataFrame({
        'Prices': [10, 25, 23, 'abc', 32, 42, 22, 14, 15],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana', 'Avacado', '12', 'Plum', 'Grapes', 'Worm'],
        'Procurement': ['2024-01-09 00:00:00', '', '2024-01-11 00:00:00', 
                        '2024-01-12 00:00:00', '2024-01-13 00:00:00',
                        '2024-01-14 00:00:00', '2024-01-15 00:00:00',
                        '2024-01-16 00:00:00', '2024-01-17 00:00:00']
    })
    
    report = get_quality_report(df)
    
    # Verify types
    assert report['column_types']['Prices'] == 'numeric'
    assert report['column_types']['Product'] == 'string'
    assert report['column_types']['Procurement'] == 'datetime'
    
    # Verify problematic cells are found
    assert len(report['error_cells']) > 0
    
    # Check specific errors
    # Row 2 (index 1), Col 2 - Empty Procurement: should be missing_value
    assert any(e['row'] == 2 and e['col'] == 2 and 'missing_value' in e['issues']
               for e in report['error_cells'])
    
    # Row 4 (index 3), Col 0 - 'abc' in Prices: should be non_numeric
    assert any(e['row'] == 4 and e['col'] == 0 and 'non_numeric' in e['issues']
               for e in report['error_cells'])
    
    # Row 6 (index 5), Col 1 - '12' in Product: should be marked as suspicious_numeric_in_string
    assert any(e['row'] == 6 and e['col'] == 1 and 'suspicious_numeric_in_string' in e['issues']
               for e in report['error_cells']), \
        "Expected '12' in Product column to be flagged as suspicious_numeric_in_string"

    print("✓ Realistic data test passed")


def test_data_to_list_conversion():
    """Test DataFrame to list conversion"""
    df = pd.DataFrame({
        'Prices': [10, 25, None],
        'Product': ['Apple', 'Orange', 'Mango'],
        'Date': pd.to_datetime(['2024-01-09', '2024-01-10', '2024-01-11'])
    })
    
    report = get_quality_report(df)
    data = report['data']
    
    # Check structure
    assert len(data) == 4  # 1 header + 3 rows
    assert data[0] == ['Prices', 'Product', 'Date']
    assert data[1] == ['10', 'Apple', '2024-01-09T00:00:00']
    assert data[2] == ['25', 'Orange', '2024-01-10T00:00:00']
    assert data[3] == [None, 'Mango', '2024-01-11T00:00:00']
    
    print("✓ Data to list conversion test passed")


def test_large_dataset():
    """Test with larger dataset"""
    size = 10000
    df = pd.DataFrame({
        'ID': range(size),
        'Value': np.random.randint(0, 100, size),
        'Name': ['Name' + str(i % 100) for i in range(size)],
        'Corrupted': [i if i < size - 100 else 'ERROR' for i in range(size)]  # Last 100 corrupted
    })
    
    report = get_quality_report(df)
    
    # Should detect errors in corrupted column
    assert len(report['error_cells']) > 0
    
    # Should identify Corrupted column as mixed type
    assert any('non_numeric' in e['issues'] for e in report['error_cells'])
    
    print(f"✓ Large dataset test passed ({size} rows, {len(report['error_cells'])} errors found)")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running DataQualityAnalyzer Test Suite")
    print("="*60 + "\n")
    
    tests = [
        test_missing_values,
        test_non_numeric_in_numeric_column,
        test_type_inference,
        test_mixed_content,
        test_null_strings,
        test_numeric_in_string_column,
        test_empty_dataframe_handling,
        test_single_column,
        test_all_null_column,
        test_realistic_data,
        test_data_to_list_conversion,
        test_large_dataset
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
