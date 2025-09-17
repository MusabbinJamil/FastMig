import pandas as pd
import json

def read_file(file_path):
    """
    Reads a CSV or Excel file into a pandas DataFrame.
    
    Raises:
        ValueError: If the file format is unsupported.
        FileNotFoundError: If the file path does not exist.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the file: {e}")

def convert_column(df, column_name, target_type, format=None):
    """
    Converts a specified column to a given target type.
    
    Raises:
        ValueError: If the target type is unsupported.
        KeyError: If the specified column is not found.
    """
    try:
        if column_name not in df.columns:
            raise KeyError(f"Column '{column_name}' not found in DataFrame")
        
        if target_type == 'datetime':
            df[column_name] = pd.to_datetime(df[column_name], format=format, errors='coerce')
        elif target_type == 'decimal':
            df[column_name] = df[column_name].astype(float)
        elif target_type == 'int':
            df[column_name] = df[column_name].astype(int)
        elif target_type == 'bool':
            df[column_name] = df[column_name].astype(bool)
        elif target_type == 'category':
            df[column_name] = df[column_name].astype('category')
        elif target_type == 'string':
            df[column_name] = df[column_name].astype(str)
        elif target_type == 'object':
            df[column_name] = df[column_name].astype('object')
        elif target_type == 'binary':
            df[column_name] = df[column_name].apply(lambda x: x.encode())
        else:
            raise ValueError(f"Unsupported target type: {target_type}")
        
        # Warn if conversion leads to NaN/NaT
        if df[column_name].isnull().any():
            raise ValueError(f"Some values in column '{column_name}' could not be converted to {target_type} and were set to NaT/NaN.")
        
        return df
    except Exception as e:
        raise RuntimeError(f"Error converting column '{column_name}' to {target_type}: {e}")

def apply_transformations(df, transformations):
    """
    Applies a series of transformations to the DataFrame.
    
    Raises:
        RuntimeError: If any transformation fails.
    """
    try:
        for transformation in transformations:
            df = convert_column(df, transformation['column'], transformation['type'], transformation.get('format'))
        return df
    except Exception as e:
        raise RuntimeError(f"Error applying transformations: {e}")

def map_columns(df, column_mapping):
    """
    Maps the columns in the DataFrame according to the provided mapping.
    
    Raises:
        ValueError: If the column mapping is incorrect.
    """
    try:
        return df.rename(columns=column_mapping)
    except Exception as e:
        raise ValueError(f"Error mapping columns: {e}")

def export_data(df, output_path):
    """
    Exports the DataFrame to a CSV or Excel file.
    
    Raises:
        ValueError: If the file format is unsupported.
    """
    try:
        if output_path.endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif output_path.endswith(('.xls', '.xlsx')):
            df.to_excel(output_path, index=False)
        else:
            raise ValueError("Unsupported output file format")
    except Exception as e:
        raise RuntimeError(f"An error occurred while exporting data: {e}")
