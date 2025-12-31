"""
Test suite for DataQualityAnalyzer
Tests various data quality scenarios

Usage:
    python3 test_data_quality.py           # Basic output
    python3 test_data_quality.py -v        # Verbose output with detailed data
    python3 test_data_quality.py --verbose # Same as -v
"""

import pandas as pd
import numpy as np
import sys
from data_quality_analyzer import DataQualityAnalyzer, get_quality_report

# Global verbose flag
VERBOSE = '-v' in sys.argv or '--verbose' in sys.argv


def print_section(title):
    """Print a section header"""
    if VERBOSE:
        print(f"\n{'─'*60}")
        print(f"  {title}")
        print(f"{'─'*60}")


def print_dataframe(df, title="Input Data"):
    """Print DataFrame in a readable format"""
    if VERBOSE:
        print(f"\n  📊 {title}:")
        print(df.to_string(index=True).replace('\n', '\n  '))


def print_report_summary(report):
    """Print a summary of the quality report"""
    if VERBOSE:
        print(f"\n  📋 Analysis Results:")
        print(f"     Shape: {report['shape'][0]} rows × {report['shape'][1]} columns")
        print(f"     Column Types: {report['column_types']}")
        print(f"     Errors Found: {len(report['error_cells'])}")
        if report['error_cells']:
            print(f"\n  🔍 Error Details:")
            for err in report['error_cells']:
                print(f"     Row {err['row']}, Col {err['col']}: {err['issues']}")


def print_test_criteria(criteria_list):
    """Print what the test is checking for"""
    if VERBOSE:
        print(f"\n  🎯 Test Criteria:")
        for criterion in criteria_list:
            print(f"     • {criterion}")


def print_test_result(passed, test_name):
    """Print detailed test result"""
    if passed:
        print(f"✓ {test_name} passed")
    else:
        print(f"✗ {test_name} failed")


def test_missing_values():
    """Test detection of missing values"""
    print_section("TEST: Missing Values Detection")

    df = pd.DataFrame({
        'Prices': [10, 25, None, 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'Procurement': ['2024-01-09', '2024-01-10', '2024-01-11', None]
    })

    print_dataframe(df)
    print_test_criteria([
        "Should detect None in Prices column (row 3, col 0)",
        "Should detect None in Procurement column (row 4, col 2)",
        "Should find exactly 2 error cells"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    assert len(report['error_cells']) == 2
    assert any(e['row'] == 3 and e['col'] == 0 and 'missing_value' in e['issues']
               for e in report['error_cells'])
    assert any(e['row'] == 4 and e['col'] == 2 and 'missing_value' in e['issues']
               for e in report['error_cells'])

    print("✓ Missing values test passed")


def test_non_numeric_in_numeric_column():
    """Test detection of non-numeric values in numeric columns"""
    print_section("TEST: Non-Numeric in Numeric Column")

    df = pd.DataFrame({
        'Prices': [10, 25, 'abc', 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'Quantity': [5, 10, 15, 20]
    })

    print_dataframe(df)
    print_test_criteria([
        "Prices column should be inferred as 'numeric'",
        "Should detect 'abc' as non-numeric in Prices (row 3, col 0)"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    # Should detect 'abc' in Prices column
    assert any(e['row'] == 3 and e['col'] == 0 and 'non_numeric' in e['issues']
               for e in report['error_cells'])

    print("✓ Non-numeric in numeric column test passed")


def test_type_inference():
    """Test automatic type inference"""
    print_section("TEST: Automatic Type Inference")

    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'Dates': ['2024-01-09', '2024-01-10', '2024-01-11', '2024-01-12']
    })

    print_dataframe(df)
    print_test_criteria([
        "Prices should be inferred as 'numeric' (all integers)",
        "Product should be inferred as 'string' (all text)",
        "Dates should be inferred as 'datetime' (date format strings)"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    assert report['column_types']['Prices'] == 'numeric'
    assert report['column_types']['Product'] == 'string'
    assert report['column_types']['Dates'] == 'datetime'

    print("✓ Type inference test passed")


def test_mixed_content():
    """Test detection of mixed content"""
    print_section("TEST: Mixed Content Detection")

    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana'],
        'MixedCol': [100, 200, '300px', 400]  # Mixed number and text
    })

    print_dataframe(df)
    print_test_criteria([
        "MixedCol has '300px' mixed with numbers",
        "Should detect mixed_content or non_numeric issue"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    # Should detect mixed content in MixedCol
    assert any('mixed_content' in e['issues'] or 'non_numeric' in e['issues']
               for e in report['error_cells'])

    print("✓ Mixed content test passed")


def test_null_strings():
    """Test detection of null-like strings"""
    print_section("TEST: Null-Like Strings Detection")

    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'Product': ['Apple', 'n/a', 'Mango', 'N/A'],
        'Notes': ['Good', 'null', 'Great', 'none']
    })

    print_dataframe(df)
    print_test_criteria([
        "Should detect 'n/a' and 'N/A' in Product column",
        "Should detect 'null' and 'none' in Notes column",
        "All should be flagged as 'null_string'"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    # Should detect null-like strings
    error_issues = [issue for e in report['error_cells'] for issue in e['issues']]
    assert 'null_string' in error_issues

    print("✓ Null-like strings test passed")

def test_numeric_in_string_column():
    """Test detection of purely numeric values in string columns"""
    print_section("TEST: Numeric Values in String Columns")

    df = pd.DataFrame({
        'Product': ['Apple', 'Banana', '12', 'Orange', '456', 'Grape'],
        'Description': ['Fresh fruit', 'Yellow', 'iPhone 12', 'Citrus', 'Good', 'Purple'],
        'Quantity': [10, 20, 30, 40, 50, 60]
    })

    print_dataframe(df)
    print_test_criteria([
        "Should detect '12' in Product (row 3) as suspicious_numeric_in_string",
        "Should detect '456' in Product (row 5) as suspicious_numeric_in_string",
        "Should NOT flag 'iPhone 12' - it contains text, not purely numeric"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

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
    print_section("TEST: Empty DataFrame Handling")

    df = pd.DataFrame()

    print_dataframe(df, "Empty DataFrame")
    print_test_criteria([
        "Should not crash on empty input",
        "Should return success=True",
        "Should return shape=(0, 0)"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    # Should not crash
    assert report['success'] == True
    assert report['shape'] == (0, 0)

    print("✓ Empty dataframe test passed")


def test_single_column():
    """Test handling of single column dataframe"""
    print_section("TEST: Single Column DataFrame")

    df = pd.DataFrame({
        'Prices': [10, 25, 'abc', 40]
    })

    print_dataframe(df)
    print_test_criteria([
        "Should handle single-column DataFrame",
        "Prices should be inferred as 'numeric'",
        "Should detect 'abc' as an error"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    assert report['shape'] == (4, 1)
    assert report['column_types']['Prices'] == 'numeric'
    assert len(report['error_cells']) > 0  # Should detect 'abc'

    print("✓ Single column test passed")


def test_all_null_column():
    """Test handling of all-null columns"""
    print_section("TEST: All-Null Column Handling")

    df = pd.DataFrame({
        'Prices': [10, 25, 23, 40],
        'EmptyCol': [None, None, None, None],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana']
    })

    print_dataframe(df)
    print_test_criteria([
        "EmptyCol should be inferred as 'unknown' type",
        "All 4 cells in EmptyCol should be marked as missing_value"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

    # Empty column should have type 'unknown'
    assert report['column_types']['EmptyCol'] == 'unknown'

    # All cells in empty column should be marked as missing
    error_count = sum(1 for e in report['error_cells'] if e['col'] == 1)
    assert error_count == 4

    print("✓ All-null column test passed")


def test_realistic_data():
    """Test with realistic messy data"""
    print_section("TEST: Realistic Messy Data")

    df = pd.DataFrame({
        'Prices': [10, 25, 23, 'abc', 32, 42, 22, 14, 15],
        'Product': ['Apple', 'Orange', 'Mango', 'Banana', 'Avacado', '12', 'Plum', 'Grapes', 'Worm'],
        'Procurement': ['2024-01-09 00:00:00', '', '2024-01-11 00:00:00',
                        '2024-01-12 00:00:00', '2024-01-13 00:00:00',
                        '2024-01-14 00:00:00', '2024-01-15 00:00:00',
                        '2024-01-16 00:00:00', '2024-01-17 00:00:00']
    })

    print_dataframe(df)
    print_test_criteria([
        "Prices='numeric', Product='string', Procurement='datetime'",
        "Row 2, Col 2: Empty Procurement → missing_value",
        "Row 4, Col 0: 'abc' in Prices → non_numeric",
        "Row 6, Col 1: '12' in Product → suspicious_numeric_in_string"
    ])

    report = get_quality_report(df)
    print_report_summary(report)

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
    print_section("TEST: DataFrame to List Conversion")

    df = pd.DataFrame({
        'Prices': [10, 25, None],
        'Product': ['Apple', 'Orange', 'Mango'],
        'Date': pd.to_datetime(['2024-01-09', '2024-01-10', '2024-01-11'])
    })

    print_dataframe(df)
    print_test_criteria([
        "Output should have 4 rows (1 header + 3 data)",
        "Header row: ['Prices', 'Product', 'Date']",
        "Integers formatted without decimals: 10 not 10.0",
        "Dates in ISO format: 2024-01-09T00:00:00",
        "None values preserved as None"
    ])

    report = get_quality_report(df)
    data = report['data']

    if VERBOSE:
        print(f"\n  📤 Converted Data:")
        for i, row in enumerate(data):
            print(f"     Row {i}: {row}")

    # Check structure
    assert len(data) == 4  # 1 header + 3 rows
    assert data[0] == ['Prices', 'Product', 'Date']
    assert data[1] == ['10', 'Apple', '2024-01-09T00:00:00']
    assert data[2] == ['25', 'Orange', '2024-01-10T00:00:00']
    assert data[3] == [None, 'Mango', '2024-01-11T00:00:00']

    print("✓ Data to list conversion test passed")


def test_large_dataset():
    """Test with larger dataset"""
    print_section("TEST: Large Dataset (10,000 rows)")

    size = 10000
    df = pd.DataFrame({
        'ID': range(size),
        'Value': np.random.randint(0, 100, size),
        'Name': ['Name' + str(i % 100) for i in range(size)],
        'Corrupted': [i if i < size - 100 else 'ERROR' for i in range(size)]  # Last 100 corrupted
    })

    if VERBOSE:
        print(f"\n  📊 Large Dataset Preview (first 5 rows):")
        print(df.head().to_string(index=True).replace('\n', '\n  '))
        print(f"\n  ... and {size - 5} more rows")
        print(f"\n  📊 Last 5 rows (with errors):")
        print(df.tail().to_string(index=True).replace('\n', '\n  '))

    print_test_criteria([
        f"Should handle {size} rows efficiently",
        "Last 100 rows have 'ERROR' in Corrupted column",
        "Should detect ~100 non_numeric errors"
    ])

    report = get_quality_report(df)

    if VERBOSE:
        print(f"\n  📋 Analysis Results:")
        print(f"     Shape: {report['shape'][0]} rows × {report['shape'][1]} columns")
        print(f"     Column Types: {report['column_types']}")
        print(f"     Total Errors Found: {len(report['error_cells'])}")
        if report['error_cells']:
            print(f"\n  🔍 Sample Errors (first 5):")
            for err in report['error_cells'][:5]:
                print(f"     Row {err['row']}, Col {err['col']}: {err['issues']}")

    # Should detect errors in corrupted column
    assert len(report['error_cells']) > 0

    # Should identify Corrupted column as mixed type
    assert any('non_numeric' in e['issues'] for e in report['error_cells'])

    print(f"✓ Large dataset test passed ({size} rows, {len(report['error_cells'])} errors found)")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running DataQualityAnalyzer Test Suite")
    print("="*60)
    if VERBOSE:
        print("Mode: VERBOSE (showing detailed test data and results)")
    else:
        print("Mode: Standard (use -v or --verbose for detailed output)")
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
