"""
Data Quality Analyzer Module
Analyzes data quality and identifies problematic cells for visual feedback
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class DataQualityAnalyzer:
    """
    Analyzes data quality and identifies cells that are out of place or problematic.
    Never fails - always loads data but marks problematic cells visually.
    """

    # Columns to exclude from error detection (e.g., tracking columns added by the system)
    EXCLUDED_COLUMNS = ['Modified_by_AI', 'modified_by_ai', '_modified_by_ai']

    def __init__(self):
        self.issues = {}  # Will store {(row, col): [issues]}
        self.column_types = {}  # Inferred types for each column
        self.warnings = []

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive data quality analysis that never fails
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with:
            - error_cells: List of [row, col, error_type, message]
            - column_types: Inferred types for each column
            - data: Original data as list of lists
            - warnings: List of dataset-level warnings
        """
        self.issues = {}
        self.column_types = {}
        self.warnings = []

        try:
            # Infer expected column types
            self._infer_column_types(df)

            # Analyze each cell
            for row_idx, row in df.iterrows():
                for col_idx, (col_name, value) in enumerate(zip(df.columns, row)):
                    self._validate_cell(row_idx, col_idx, col_name, value)

            # Convert DataFrame to list format
            data_list = self._dataframe_to_list(df)

            # Generate error cells list for frontend
            error_cells = []
            for (row_idx, col_idx), issue_list in self.issues.items():
                error_cells.append({
                    'row': row_idx + 1,  # +1 because first row is headers
                    'col': col_idx,
                    'issues': issue_list
                })

            logger.info(f"Data quality analysis complete: {len(error_cells)} problematic cells found")

            return {
                'success': True,
                'data': data_list,
                'error_cells': error_cells,
                'column_types': self.column_types,
                'warnings': self.warnings,
                'total_cells': len(error_cells),
                'shape': df.shape
            }

        except Exception as e:
            logger.error(f"Error in data quality analysis: {str(e)}")
            # Even on error, try to return what we can
            return {
                'success': True,  # Still return success - we don't fail on data
                'data': self._dataframe_to_list(df),
                'error_cells': [],
                'column_types': self.column_types,
                'warnings': [f"Analysis error: {str(e)}"],
                'total_cells': 0,
                'shape': df.shape
            }

    def _infer_column_types(self, df: pd.DataFrame) -> None:
        """Infer the expected type for each column"""
        for col in df.columns:
            # Skip excluded columns (e.g., tracking columns added by the system)
            if col in self.EXCLUDED_COLUMNS:
                self.column_types[col] = 'excluded'
                logger.info(f"Column '{col}' excluded from analysis (system tracking column)")
                continue

            col_data = df[col].dropna()  # Ignore NaN values

            if len(col_data) == 0:
                self.column_types[col] = 'unknown'
                continue

            # Try to infer type from non-null values
            inferred_type = self._infer_type(col_data)
            self.column_types[col] = inferred_type
            logger.info(f"Column '{col}' inferred as type: {inferred_type}")

    def _infer_type(self, series: pd.Series) -> str:
        """Infer the type of a pandas Series"""
        try:
            # Check if it's numeric
            if pd.api.types.is_numeric_dtype(series):
                return 'numeric'
            
            # Check if it's datetime
            if pd.api.types.is_datetime64_any_dtype(series):
                return 'datetime'
            
            # Try to convert to datetime
            if self._is_datetime_convertible(series):
                return 'datetime'
            
            # Try to convert to numeric
            if self._is_numeric_convertible(series):
                return 'numeric'
            
            # Default to string
            return 'string'
        except:
            return 'string'

    def _is_datetime_convertible(self, series: pd.Series) -> bool:
        """Check if series can be converted to datetime"""
        if len(series) < 2:
            return False
        
        convertible_count = 0
        for val in series.head(10):  # Check first 10 values
            try:
                if pd.notna(val) and val != '':
                    pd.to_datetime(str(val))
                    convertible_count += 1
            except:
                pass
        
        return convertible_count >= 5  # At least 50% convertible

    def _is_numeric_convertible(self, series: pd.Series) -> bool:
        """Check if series can be converted to numeric"""
        if len(series) < 2:
            return False
        
        convertible_count = 0
        for val in series.head(10):  # Check first 10 values
            try:
                if pd.notna(val) and val != '':
                    float(str(val))
                    convertible_count += 1
            except:
                pass
        
        return convertible_count >= 5  # At least 50% convertible

    def _validate_cell(self, row_idx: int, col_idx: int, col_name: str, value: Any) -> None:
        """Validate individual cell and add issues if found"""
        # Skip excluded columns (e.g., tracking columns added by the system)
        if col_name in self.EXCLUDED_COLUMNS:
            return

        issues = []
        expected_type = self.column_types.get(col_name, 'string')

        # Skip cells in excluded column types
        if expected_type == 'excluded':
            return

        # Check 1: Missing values
        if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
            issues.append('missing_value')

        # Check 2: Type mismatch
        if expected_type == 'numeric' and pd.notna(value):
            if not self._is_numeric_value(str(value)):
                issues.append('non_numeric')

        elif expected_type == 'datetime' and pd.notna(value):
            if not self._is_datetime_value(str(value)):
                issues.append('invalid_datetime')

        # Check 3: Outliers/suspicious values
        if expected_type == 'numeric' and pd.notna(value):
            try:
                numeric_val = float(str(value).replace(',', ''))
                # Very large negative values might be codes
                if numeric_val < -999999 or numeric_val > 999999:
                    issues.append('suspicious_value')
            except:
                pass

        # Check 4: Special characters that might indicate data entry errors
        if isinstance(value, str) and len(value) > 0:
            # Check for mixed types (e.g., text in numeric column)
            if expected_type == 'numeric' and any(c.isalpha() for c in str(value) if c not in [',']):
                issues.append('mixed_content')

        # Check 5: Numeric values in string columns (applies to both string values and numeric types)
        # This catches actual numbers (int/float) that ended up in string columns
        if expected_type == 'string' and pd.notna(value):
            # Convert to string to check the pattern
            value_as_str = str(value)
            if self._contains_numeric_patterns(value_as_str):
                logger.info(f"Found suspicious numeric pattern '{value}' in string column '{col_name}' at row {row_idx}, col {col_idx}")
                issues.append('suspicious_numeric_in_string')


        # Check 5: Null-like strings
        if isinstance(value, str):
            null_strings = ['null', 'none', 'n/a', 'na', 'unknown', '#n/a', '#na']
            if str(value).lower().strip() in null_strings:
                issues.append('null_string')

        # Record issues if any found
        if issues:
            self.issues[(row_idx, col_idx)] = issues

    def _is_numeric_value(self, value_str: str) -> bool:
        """Check if a string represents a numeric value"""
        if not value_str or not isinstance(value_str, str):
            return False
        
        value_str = str(value_str).strip()
        
        try:
            float(value_str.replace(',', ''))
            return True
        except:
            return False

    def _contains_numeric_patterns(self, value_str: str) -> bool:
        """
        Check if a string is purely numeric (e.g., '12', '42', '3.14')
        This detects values that are ONLY numbers in string columns like Product names.
        Does NOT flag legitimate values like 'iPhone 12' or 'Windows 10'.
        """
        if not isinstance(value_str, str) or not value_str:
            return False

        value_str = value_str.strip()

        # Check if the string is purely numeric (with optional commas, decimal points, +/- signs)
        # This will match: "12", "42", "3.14", "1,000", "+123", "-456.78"
        # This will NOT match: "iPhone 12", "Windows 10", "Apple", "12Pro"
        import re
        # Pattern: optional sign, digits with optional commas and decimal point
        purely_numeric_pattern = r'^[+-]?[\d,]+\.?\d*$'

        if re.match(purely_numeric_pattern, value_str):
            # Additional check: must have at least one digit
            return any(c.isdigit() for c in value_str)

        return False


    def _is_datetime_value(self, value_str: str) -> bool:
        """Check if a string represents a datetime value (not a numeric timestamp)"""
        if not value_str or not isinstance(value_str, str):
            return False

        value_str = str(value_str).strip()

        # Reject numeric timestamps (like 1.7047584e+18) - these need cleaning
        # They should be converted to proper datetime strings
        try:
            numeric_val = float(value_str)
            # If it parses as a very large number, it's likely a numeric timestamp
            # that needs to be converted to a proper datetime format
            if abs(numeric_val) > 1e9:  # Looks like a Unix timestamp
                return False
        except ValueError:
            pass  # Not a numeric value, continue checking

        try:
            pd.to_datetime(value_str)
            return True
        except:
            return False

    def _dataframe_to_list(self, df: pd.DataFrame) -> List[List]:
        """Convert DataFrame to list of lists for JSON response"""
        # Identify datetime columns
        datetime_cols = set()
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                datetime_cols.add(col)

        data_list = []

        # Add headers as first row
        data_list.append(df.columns.tolist())

        # Add data rows
        for _, row in df.iterrows():
            row_data = []
            for col_name, val in zip(df.columns, row):
                if pd.isna(val):
                    row_data.append(None)
                elif isinstance(val, pd.Timestamp):
                    row_data.append(val.isoformat())
                elif col_name in datetime_cols and isinstance(val, (int, float)):
                    # Convert numeric timestamps in datetime columns to ISO format
                    # Only if the number is large enough to be a reasonable timestamp
                    try:
                        numeric_val = float(val)
                        if abs(numeric_val) > 1e15:  # Nanoseconds
                            dt_val = datetime.fromtimestamp(numeric_val / 1e9)
                            row_data.append(dt_val.strftime('%Y-%m-%dT%H:%M:%S'))
                        elif abs(numeric_val) > 1e12:  # Milliseconds
                            dt_val = datetime.fromtimestamp(numeric_val / 1e3)
                            row_data.append(dt_val.strftime('%Y-%m-%dT%H:%M:%S'))
                        elif abs(numeric_val) > 1e9:  # Seconds (year ~2001+)
                            dt_val = datetime.fromtimestamp(numeric_val)
                            row_data.append(dt_val.strftime('%Y-%m-%dT%H:%M:%S'))
                        else:
                            # Small number - keep as-is (likely regular data, not a timestamp)
                            row_data.append(str(val))
                    except (ValueError, OSError, OverflowError):
                        row_data.append(str(val))
                else:
                    row_data.append(str(val))
            data_list.append(row_data)

        return data_list


def get_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to get quality analysis for a DataFrame
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Quality analysis report
    """
    analyzer = DataQualityAnalyzer()
    return analyzer.analyze(df)
