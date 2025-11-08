"""
ETL Operations Module
Provides basic data cleaning and transformation operations
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ETLOperations:
    """
    Handles basic ETL operations for data cleaning and transformation
    """
    
    @staticmethod
    def remove_null_rows(df: pd.DataFrame, columns: Optional[List[str]] = None, how: str = 'any') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove rows containing null values
        
        Args:
            df: DataFrame to process
            columns: Specific columns to check for nulls (None = all columns)
            how: 'any' to remove rows with any null, 'all' to remove rows with all nulls
        
        Returns:
            Tuple of (cleaned DataFrame, operation report)
        """
        original_rows = len(df)
        
        if columns:
            df_cleaned = df.dropna(subset=columns, how=how)
        else:
            df_cleaned = df.dropna(how=how)
        
        rows_removed = original_rows - len(df_cleaned)
        
        report = {
            'operation': 'remove_null_rows',
            'original_rows': original_rows,
            'rows_removed': rows_removed,
            'remaining_rows': len(df_cleaned),
            'columns_checked': columns if columns else 'all',
            'how': how
        }
        
        logger.info(f"Removed {rows_removed} rows containing null values")
        return df_cleaned, report
    
    @staticmethod
    def remove_duplicate_rows(df: pd.DataFrame, columns: Optional[List[str]] = None, keep: str = 'first') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove duplicate rows
        
        Args:
            df: DataFrame to process
            columns: Columns to check for duplicates (None = all columns)
            keep: 'first', 'last', or False (remove all duplicates)
        
        Returns:
            Tuple of (cleaned DataFrame, operation report)
        """
        original_rows = len(df)
        
        df_cleaned = df.drop_duplicates(subset=columns, keep=keep)
        
        rows_removed = original_rows - len(df_cleaned)
        
        report = {
            'operation': 'remove_duplicate_rows',
            'original_rows': original_rows,
            'rows_removed': rows_removed,
            'remaining_rows': len(df_cleaned),
            'columns_checked': columns if columns else 'all',
            'keep': keep
        }
        
        logger.info(f"Removed {rows_removed} duplicate rows")
        return df_cleaned, report
    
    @staticmethod
    def find_replace(df: pd.DataFrame, column: str, find_value: Any, replace_value: Any, 
                     use_regex: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Find and replace values in a column
        
        Args:
            df: DataFrame to process
            column: Column name to perform find/replace
            find_value: Value to find
            replace_value: Value to replace with
            use_regex: Whether to use regex pattern matching
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")
        
        original_values = df[column].copy()
        
        if use_regex:
            df[column] = df[column].astype(str).replace(find_value, replace_value, regex=True)
        else:
            df[column] = df[column].replace(find_value, replace_value)
        
        replacements_made = (original_values != df[column]).sum()
        
        report = {
            'operation': 'find_replace',
            'column': column,
            'find_value': str(find_value),
            'replace_value': str(replace_value),
            'use_regex': use_regex,
            'replacements_made': int(replacements_made)
        }
        
        logger.info(f"Replaced {replacements_made} values in column '{column}'")
        return df, report
    
    @staticmethod
    def fill_null_values(df: pd.DataFrame, column: str, method: str = 'forward', 
                        value: Any = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fill null values in a column
        
        Args:
            df: DataFrame to process
            column: Column name to fill nulls
            method: 'forward', 'backward', 'mean', 'median', 'mode', 'constant'
            value: Value to use when method='constant'
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")
        
        nulls_before = df[column].isnull().sum()
        
        if method == 'forward':
            df[column] = df[column].fillna(method='ffill')
        elif method == 'backward':
            df[column] = df[column].fillna(method='bfill')
        elif method == 'mean':
            df[column] = df[column].fillna(df[column].mean())
        elif method == 'median':
            df[column] = df[column].fillna(df[column].median())
        elif method == 'mode':
            mode_value = df[column].mode()[0] if not df[column].mode().empty else None
            df[column] = df[column].fillna(mode_value)
        elif method == 'constant':
            df[column] = df[column].fillna(value)
        else:
            raise ValueError(f"Invalid fill method: {method}")
        
        nulls_after = df[column].isnull().sum()
        nulls_filled = nulls_before - nulls_after
        
        report = {
            'operation': 'fill_null_values',
            'column': column,
            'method': method,
            'value': str(value) if value is not None else None,
            'nulls_filled': int(nulls_filled),
            'nulls_remaining': int(nulls_after)
        }
        
        logger.info(f"Filled {nulls_filled} null values in column '{column}'")
        return df, report
    
    @staticmethod
    def rename_column(df: pd.DataFrame, old_name: str, new_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Rename a column
        
        Args:
            df: DataFrame to process
            old_name: Current column name
            new_name: New column name
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        if old_name not in df.columns:
            raise KeyError(f"Column '{old_name}' not found in DataFrame")
        
        df = df.rename(columns={old_name: new_name})
        
        report = {
            'operation': 'rename_column',
            'old_name': old_name,
            'new_name': new_name
        }
        
        logger.info(f"Renamed column '{old_name}' to '{new_name}'")
        return df, report
    
    @staticmethod
    def remove_column(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Remove a column from the DataFrame
        
        Args:
            df: DataFrame to process
            column: Column name to remove
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")
        
        df = df.drop(columns=[column])
        
        report = {
            'operation': 'remove_column',
            'column': column
        }
        
        logger.info(f"Removed column '{column}'")
        return df, report
    
    @staticmethod
    def filter_rows(df: pd.DataFrame, column: str, operator: str, value: Any) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Filter rows based on a condition
        
        Args:
            df: DataFrame to process
            column: Column to filter on
            operator: Comparison operator ('==', '!=', '>', '<', '>=', '<=', 'contains', 'startswith', 'endswith')
            value: Value to compare against
        
        Returns:
            Tuple of (filtered DataFrame, operation report)
        """
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")
        
        original_rows = len(df)
        
        if operator == '==':
            df_filtered = df[df[column] == value]
        elif operator == '!=':
            df_filtered = df[df[column] != value]
        elif operator == '>':
            df_filtered = df[df[column] > value]
        elif operator == '<':
            df_filtered = df[df[column] < value]
        elif operator == '>=':
            df_filtered = df[df[column] >= value]
        elif operator == '<=':
            df_filtered = df[df[column] <= value]
        elif operator == 'contains':
            df_filtered = df[df[column].astype(str).str.contains(str(value), na=False)]
        elif operator == 'startswith':
            df_filtered = df[df[column].astype(str).str.startswith(str(value), na=False)]
        elif operator == 'endswith':
            df_filtered = df[df[column].astype(str).str.endswith(str(value), na=False)]
        else:
            raise ValueError(f"Invalid operator: {operator}")
        
        rows_filtered = original_rows - len(df_filtered)
        
        report = {
            'operation': 'filter_rows',
            'column': column,
            'operator': operator,
            'value': str(value),
            'original_rows': original_rows,
            'rows_removed': rows_filtered,
            'remaining_rows': len(df_filtered)
        }
        
        logger.info(f"Filtered {rows_filtered} rows based on {column} {operator} {value}")
        return df_filtered, report
    
    @staticmethod
    def trim_whitespace(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Trim leading and trailing whitespace from string columns
        
        Args:
            df: DataFrame to process
            columns: Specific columns to trim (None = all string columns)
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        if columns is None:
            # Auto-detect string columns
            columns = df.select_dtypes(include=['object']).columns.tolist()
        
        modifications = 0
        for col in columns:
            if col in df.columns:
                original = df[col].copy()
                df[col] = df[col].astype(str).str.strip()
                modifications += (original != df[col]).sum()
        
        report = {
            'operation': 'trim_whitespace',
            'columns_processed': columns,
            'modifications_made': int(modifications)
        }
        
        logger.info(f"Trimmed whitespace from {len(columns)} columns, {modifications} modifications made")
        return df, report
    
    @staticmethod
    def change_case(df: pd.DataFrame, column: str, case_type: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Change the case of text in a column
        
        Args:
            df: DataFrame to process
            column: Column name to change case
            case_type: 'upper', 'lower', 'title', 'capitalize'
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")
        
        original_values = df[column].copy()
        
        if case_type == 'upper':
            df[column] = df[column].astype(str).str.upper()
        elif case_type == 'lower':
            df[column] = df[column].astype(str).str.lower()
        elif case_type == 'title':
            df[column] = df[column].astype(str).str.title()
        elif case_type == 'capitalize':
            df[column] = df[column].astype(str).str.capitalize()
        else:
            raise ValueError(f"Invalid case type: {case_type}")
        
        modifications = (original_values != df[column]).sum()
        
        report = {
            'operation': 'change_case',
            'column': column,
            'case_type': case_type,
            'modifications_made': int(modifications)
        }
        
        logger.info(f"Changed case to {case_type} in column '{column}', {modifications} modifications")
        return df, report
    
    @staticmethod
    def split_column(df: pd.DataFrame, column: str, delimiter: str, new_column_names: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Split a column into multiple columns
        
        Args:
            df: DataFrame to process
            column: Column to split
            delimiter: Delimiter to split on
            new_column_names: Names for the new columns
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame")
        
        # Split the column
        split_data = df[column].astype(str).str.split(delimiter, expand=True)
        
        # Assign new column names (use default if not enough names provided)
        for i, col_name in enumerate(new_column_names):
            if i < len(split_data.columns):
                df[col_name] = split_data[i]
        
        # Remove original column
        df = df.drop(columns=[column])
        
        report = {
            'operation': 'split_column',
            'original_column': column,
            'delimiter': delimiter,
            'new_columns': new_column_names,
            'columns_created': len(new_column_names)
        }
        
        logger.info(f"Split column '{column}' into {len(new_column_names)} new columns")
        return df, report
    
    @staticmethod
    def merge_columns(df: pd.DataFrame, columns: List[str], new_column_name: str, 
                     separator: str = ' ') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Merge multiple columns into a single column
        
        Args:
            df: DataFrame to process
            columns: List of columns to merge
            new_column_name: Name for the merged column
            separator: Separator to use when merging
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        # Validate all columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Columns not found: {missing_cols}")
        
        # Merge columns
        df[new_column_name] = df[columns].astype(str).agg(separator.join, axis=1)
        
        # Optionally remove original columns
        # df = df.drop(columns=columns)
        
        report = {
            'operation': 'merge_columns',
            'source_columns': columns,
            'new_column': new_column_name,
            'separator': separator
        }
        
        logger.info(f"Merged {len(columns)} columns into '{new_column_name}'")
        return df, report
    
    @staticmethod
    def sort_data(df: pd.DataFrame, columns: List[str], ascending: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Sort data by specified columns
        
        Args:
            df: DataFrame to process
            columns: Columns to sort by
            ascending: Sort order
        
        Returns:
            Tuple of (sorted DataFrame, operation report)
        """
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Columns not found: {missing_cols}")
        
        df = df.sort_values(by=columns, ascending=ascending)
        
        report = {
            'operation': 'sort_data',
            'columns': columns,
            'ascending': ascending
        }
        
        logger.info(f"Sorted data by {columns}")
        return df, report
    
    @staticmethod
    def add_calculated_column(df: pd.DataFrame, new_column_name: str, 
                            expression: str, columns_map: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Add a calculated column based on an expression
        
        Args:
            df: DataFrame to process
            new_column_name: Name for the new column
            expression: Python expression (e.g., "col1 + col2", "col1 * 2")
            columns_map: Mapping of placeholders to actual column names
        
        Returns:
            Tuple of (modified DataFrame, operation report)
        """
        # Replace placeholders with actual column references
        eval_expression = expression
        for placeholder, col_name in columns_map.items():
            if col_name not in df.columns:
                raise KeyError(f"Column '{col_name}' not found in DataFrame")
            eval_expression = eval_expression.replace(placeholder, f"df['{col_name}']")
        
        try:
            df[new_column_name] = eval(eval_expression)
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")
        
        report = {
            'operation': 'add_calculated_column',
            'new_column': new_column_name,
            'expression': expression,
            'columns_used': list(columns_map.values())
        }
        
        logger.info(f"Added calculated column '{new_column_name}'")
        return df, report


class StepRecorder:
    """
    Records and manages ETL transformation steps
    """
    
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        self.is_recording = False
        
    def start_recording(self):
        """Start recording steps"""
        self.is_recording = True
        self.steps = []
        logger.info("Started recording ETL steps")
        
    def stop_recording(self):
        """Stop recording steps"""
        self.is_recording = False
        logger.info(f"Stopped recording. Total steps: {len(self.steps)}")
        
    def record_step(self, operation: str, params: Dict[str, Any], report: Dict[str, Any]):
        """Record a single step"""
        if self.is_recording:
            step = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'parameters': params,
                'report': report
            }
            self.steps.append(step)
            logger.info(f"Recorded step {len(self.steps)}: {operation}")
    
    def get_steps(self) -> List[Dict[str, Any]]:
        """Get all recorded steps"""
        return self.steps
    
    def clear_steps(self):
        """Clear all recorded steps"""
        self.steps = []
        logger.info("Cleared all recorded steps")
    
    def save_steps(self, file_path: str):
        """Save steps to JSON file"""
        import json
        with open(file_path, 'w') as f:
            json.dump(self.steps, f, indent=2)
        logger.info(f"Saved {len(self.steps)} steps to {file_path}")
    
    def load_steps(self, file_path: str):
        """Load steps from JSON file"""
        import json
        with open(file_path, 'r') as f:
            self.steps = json.load(f)
        logger.info(f"Loaded {len(self.steps)} steps from {file_path}")
    
    def replay_steps(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Replay all recorded steps on a DataFrame
        
        Args:
            df: DataFrame to apply steps to
        
        Returns:
            Tuple of (transformed DataFrame, list of reports)
        """
        etl = ETLOperations()
        reports = []
        
        for i, step in enumerate(self.steps):
            try:
                operation = step['operation']
                params = step['parameters']
                
                logger.info(f"Replaying step {i+1}/{len(self.steps)}: {operation}")
                
                # Execute the operation
                if operation == 'remove_null_rows':
                    df, report = etl.remove_null_rows(df, **params)
                elif operation == 'remove_duplicate_rows':
                    df, report = etl.remove_duplicate_rows(df, **params)
                elif operation == 'find_replace':
                    df, report = etl.find_replace(df, **params)
                elif operation == 'fill_null_values':
                    df, report = etl.fill_null_values(df, **params)
                elif operation == 'rename_column':
                    df, report = etl.rename_column(df, **params)
                elif operation == 'remove_column':
                    df, report = etl.remove_column(df, **params)
                elif operation == 'filter_rows':
                    df, report = etl.filter_rows(df, **params)
                elif operation == 'trim_whitespace':
                    df, report = etl.trim_whitespace(df, **params)
                elif operation == 'change_case':
                    df, report = etl.change_case(df, **params)
                elif operation == 'split_column':
                    df, report = etl.split_column(df, **params)
                elif operation == 'merge_columns':
                    df, report = etl.merge_columns(df, **params)
                elif operation == 'sort_data':
                    df, report = etl.sort_data(df, **params)
                elif operation == 'add_calculated_column':
                    df, report = etl.add_calculated_column(df, **params)
                elif operation == 'convert_column':
                    # Use existing convert_column from functions
                    from functions import convert_column
                    df = convert_column(df, params['column_name'], 
                                      params['target_type'], 
                                      params.get('format_spec'))
                    report = {'operation': 'convert_column', 'success': True}
                else:
                    logger.warning(f"Unknown operation: {operation}")
                    continue
                
                reports.append(report)
                
            except Exception as e:
                logger.error(f"Error replaying step {i+1}: {e}")
                reports.append({
                    'operation': step['operation'],
                    'success': False,
                    'error': str(e)
                })
        
        logger.info(f"Replay complete. Processed {len(self.steps)} steps")
        return df, reports
