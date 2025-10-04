import pandas as pd
import json
import warnings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress pandas warnings for datetime parsing
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

def read_file(file_path):
    """
    Reads a CSV or Excel file into a pandas DataFrame.
    
    Raises:
        ValueError: If the file format is unsupported.
        FileNotFoundError: If the file path does not exist.
    """
    try:
        logger.info(f"Reading file: {file_path}")
        
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported file format. File must be .csv, .xls, or .xlsx. Got: {file_path}")
        
        if df.empty:
            raise ValueError("File is empty or contains no data")
        
        logger.info(f"Successfully read file with {len(df)} rows and {len(df.columns)} columns")
        return df
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"File is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the file: {str(e)}")

def convert_column(df, column_name, target_type, format=None):
    """
    Converts a specified column to a given target type.
    
    Raises:
        ValueError: If the target type is unsupported.
        KeyError: If the specified column is not found.
    """
    try:
        # Validate inputs
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        if column_name not in df.columns:
            raise KeyError(f"Column '{column_name}' not found in DataFrame. Available columns: {', '.join(df.columns)}")
        
        # Create a copy of the column for conversion
        original_nulls = df[column_name].isnull().sum()
        
        logger.info(f"Converting column '{column_name}' to type '{target_type}'")
        
        if target_type == 'datetime':
            # Suppress warnings and try conversion with infer_datetime_format
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                if format:
                    df[column_name] = pd.to_datetime(df[column_name], format=format, errors='coerce')
                else:
                    # Try to infer format automatically
                    df[column_name] = pd.to_datetime(df[column_name], infer_datetime_format=True, errors='coerce')
        
        elif target_type == 'decimal' or target_type == 'float':
            # Convert to numeric, coercing errors to NaN
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
        
        elif target_type == 'int' or target_type == 'integer':
            # Convert to numeric first, then to int
            temp = pd.to_numeric(df[column_name], errors='coerce')
            if temp.isnull().sum() > original_nulls:
                raise ValueError(f"Column '{column_name}' contains non-numeric values that cannot be converted to integer")
            df[column_name] = temp.fillna(0).astype(int)
        
        elif target_type == 'bool' or target_type == 'boolean':
            df[column_name] = df[column_name].astype(bool)
        
        elif target_type == 'category':
            df[column_name] = df[column_name].astype('category')
        
        elif target_type == 'string' or target_type == 'str' or target_type == 'text':
            df[column_name] = df[column_name].astype(str)
        
        elif target_type == 'object':
            df[column_name] = df[column_name].astype('object')
        
        elif target_type == 'binary':
            df[column_name] = df[column_name].apply(lambda x: x.encode() if isinstance(x, str) else x)
        
        else:
            raise ValueError(f"Unsupported target type: '{target_type}'. Supported types: datetime, decimal, int, bool, category, string, object, binary")
        
        # Check if conversion created new nulls
        new_nulls = df[column_name].isnull().sum()
        if new_nulls > original_nulls:
            nulls_created = new_nulls - original_nulls
            logger.warning(f"Conversion created {nulls_created} null values in column '{column_name}'")
            # Don't raise error, just log it
        
        logger.info(f"Successfully converted column '{column_name}' to {target_type}")
        return df
    
    except KeyError as e:
        raise KeyError(str(e))
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise RuntimeError(f"Unexpected error converting column '{column_name}' to {target_type}: {str(e)}")

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
