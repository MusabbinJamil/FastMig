from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os
import logging
from typing import List, Dict, Any, Optional
from collections import deque
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI imports
try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False
    AzureOpenAI = None
from functions import read_file, convert_column, export_data, apply_transformations, map_columns
from werkzeug.utils import secure_filename
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import numpy as np
from data_fitness import (
    DataFitnessEvaluator, 
    EvolutionaryDataCleaner,
    evaluate_data_fitness,
    clean_data_evolutionary
)
from etl_operations import ETLOperations, StepRecorder
from ga_fitness_evolver import DataFitnessEvolverGA, PopulationConfig, evolve_records
from ga_engine import GeneticAlgorithmEngine, GAResult
from ga_operators import GAConfig, SelectionMethod, CrossoverMethod, MutationMethod
from ga_genotype_phenotype import RealValuedMapper
from ga_data_cleaning_pipeline import DataCleaningPipeline
from data_quality_analyzer import DataQualityAnalyzer
from evolutionary_cell_cleaner import evolve_error_cells, EvolutionMethod, CellEvolutionConfig
from ai_chat import (
    AIChat, AIChatConfig, AIResponse, AIOperation,
    DataContext, OperationType, AZURE_OPENAI_AVAILABLE as AI_CHAT_AVAILABLE
)

# Configure logging with custom handler to store logs
class LogCapture(logging.Handler):
    """Custom handler to capture logs in memory"""
    def __init__(self, max_logs=500):
        super().__init__()
        self.logs = deque(maxlen=max_logs)
    
    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)

log_capture = LogCapture()
log_capture.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(log_capture)
# Also add root logger handler
logging.getLogger().addHandler(log_capture)

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter web clients

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables to store data (in production, use a database)
current_data = {}
recorded_actions = []  # Legacy support
is_recording = False  # Legacy support

# New step recorder
step_recorder = StepRecorder()
etl_ops = ETLOperations()

# AI Modification Tracking - stores cell-level changes made by AI
ai_modifications = {
    'history': [],  # List of modification batches
    'current_session': [],  # Current session modifications
    'modified_cells': {}  # Quick lookup: {(row, col): modification_info}
}

def track_ai_modification(row_index: int, column: str, old_value: Any, new_value: Any, operation: str):
    """Track a single cell modification made by AI"""
    modification = {
        'row': row_index,
        'column': column,
        'old_value': str(old_value) if old_value is not None else None,
        'new_value': str(new_value) if new_value is not None else None,
        'operation': operation,
        'timestamp': pd.Timestamp.now().isoformat(),
        'modified_by': 'AI'
    }
    ai_modifications['current_session'].append(modification)
    ai_modifications['modified_cells'][(row_index, column)] = modification
    return modification

def clear_ai_modifications():
    """Clear current session modifications"""
    if ai_modifications['current_session']:
        ai_modifications['history'].append({
            'batch': ai_modifications['current_session'].copy(),
            'timestamp': pd.Timestamp.now().isoformat()
        })
    ai_modifications['current_session'] = []
    ai_modifications['modified_cells'] = {}

def get_ai_modifications() -> Dict[str, Any]:
    """Get all AI modifications for display"""
    return {
        'current_session': ai_modifications['current_session'],
        'modified_cells': {f"{k[0]},{k[1]}": v for k, v in ai_modifications['modified_cells'].items()},
        'total_modifications': len(ai_modifications['current_session']),
        'history_batches': len(ai_modifications['history'])
    }

# ============================================================================
# AZURE OPENAI CONFIGURATION
# ============================================================================

def get_azure_openai_client() -> Optional[AzureOpenAI]:
    """Get Azure OpenAI client if configured"""
    if not AZURE_OPENAI_AVAILABLE:
        return None

    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

    if not api_key or not endpoint:
        return None

    return AzureOpenAI(
        api_key=api_key,
        api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
        azure_endpoint=endpoint
    )

def build_data_context(df: pd.DataFrame) -> str:
    """Build a comprehensive data context string for the AI"""
    context_parts = []

    # Basic info
    context_parts.append(f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Column information
    context_parts.append("\nColumns:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        context_parts.append(f"  - {col} (type: {dtype}, nulls: {null_count}, unique: {unique_count})")

    # Sample data (first 5 rows)
    context_parts.append("\nSample Data (first 5 rows):")
    sample_df = df.head(5)
    for idx, row in sample_df.iterrows():
        row_str = ", ".join([f"{col}={row[col]}" for col in df.columns[:5]])  # Limit to 5 cols for brevity
        if len(df.columns) > 5:
            row_str += f" ... (+{len(df.columns) - 5} more columns)"
        context_parts.append(f"  Row {idx}: {row_str}")

    # Statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        context_parts.append("\nNumeric Column Statistics:")
        for col in numeric_cols[:5]:  # Limit to 5 columns
            stats = df[col].describe()
            context_parts.append(f"  - {col}: mean={stats['mean']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")

    # Missing values summary
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if len(cols_with_nulls) > 0:
        context_parts.append("\nColumns with Missing Values:")
        for col, count in cols_with_nulls.items():
            pct = (count / len(df)) * 100
            context_parts.append(f"  - {col}: {count} missing ({pct:.1f}%)")

    return "\n".join(context_parts)

def parse_ai_modification_command(response_text: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Parse AI response for actionable data modifications.
    Returns a dict with operation type and parameters.
    """
    response_lower = response_text.lower()

    # Detect fill null/missing values commands
    if any(phrase in response_lower for phrase in ['fill', 'replace missing', 'fill null', 'impute']):
        for col in df.columns:
            if col.lower() in response_lower:
                # Detect fill method
                if 'mean' in response_lower or 'average' in response_lower:
                    return {'type': 'fill_nulls', 'column': col, 'method': 'mean'}
                elif 'median' in response_lower:
                    return {'type': 'fill_nulls', 'column': col, 'method': 'median'}
                elif 'mode' in response_lower or 'most common' in response_lower:
                    return {'type': 'fill_nulls', 'column': col, 'method': 'mode'}
                elif 'zero' in response_lower or '0' in response_lower:
                    return {'type': 'fill_nulls', 'column': col, 'method': 'constant', 'value': 0}
                else:
                    return {'type': 'fill_nulls', 'column': col, 'method': 'mean'}

    # Detect remove/drop commands
    if any(phrase in response_lower for phrase in ['remove', 'drop', 'delete']):
        if 'duplicate' in response_lower:
            return {'type': 'remove_duplicates'}
        if 'null' in response_lower or 'missing' in response_lower:
            return {'type': 'remove_nulls'}
        for col in df.columns:
            if col.lower() in response_lower and 'column' in response_lower:
                return {'type': 'remove_column', 'column': col}

    # Detect rename commands
    if 'rename' in response_lower:
        for col in df.columns:
            if col.lower() in response_lower:
                return {'type': 'rename_column', 'column': col, 'needs_new_name': True}

    # Detect case change commands
    if any(phrase in response_lower for phrase in ['uppercase', 'upper case', 'to upper']):
        for col in df.columns:
            if col.lower() in response_lower:
                return {'type': 'change_case', 'column': col, 'case_type': 'upper'}
    if any(phrase in response_lower for phrase in ['lowercase', 'lower case', 'to lower']):
        for col in df.columns:
            if col.lower() in response_lower:
                return {'type': 'change_case', 'column': col, 'case_type': 'lower'}

    return {'type': 'none', 'message': 'No actionable command detected'}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _dataframe_to_list(df: pd.DataFrame, max_rows: int = 100) -> List[List]:
    """Convert DataFrame to list format for JSON response"""
    from datetime import datetime as dt

    # Identify datetime columns
    datetime_cols = set()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.add(col)

    data_list = []
    # Add headers as first row
    data_list.append(df.columns.tolist())
    # Add data rows (limited to max_rows for performance)
    for _, row in df.head(max_rows).iterrows():
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
                        dt_val = dt.fromtimestamp(numeric_val / 1e9)
                        row_data.append(dt_val.strftime('%Y-%m-%dT%H:%M:%S'))
                    elif abs(numeric_val) > 1e12:  # Milliseconds
                        dt_val = dt.fromtimestamp(numeric_val / 1e3)
                        row_data.append(dt_val.strftime('%Y-%m-%dT%H:%M:%S'))
                    elif abs(numeric_val) > 1e9:  # Seconds (year ~2001+)
                        dt_val = dt.fromtimestamp(numeric_val)
                        row_data.append(dt_val.strftime('%Y-%m-%dT%H:%M:%S'))
                    else:
                        # Small number - keep as-is (likely regular data, not a timestamp)
                        row_data.append(val)
                except (ValueError, OSError, OverflowError):
                    row_data.append(val)
            else:
                row_data.append(val)
        data_list.append(row_data)
    return data_list

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'FastMig backend is running'})

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get captured backend logs"""
    try:
        logs = list(log_capture.logs)
        return jsonify({'logs': logs, 'count': len(logs)}), 200
    except Exception as e:
        logger.error(f'Error retrieving logs: {e}')
        return jsonify({'error': 'Failed to retrieve logs', 'logs': []}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file and return its data with quality analysis"""
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided in request'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        allowed_extensions = {'.csv', '.xls', '.xlsx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f"Unsupported file type: {file_ext}",
                'allowed_types': list(allowed_extensions)
            }), 400
        
        # Secure the filename and save it
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(file_path)
        app.logger.info(f"File saved: {file_path}")
        
        # Read the file using your existing function
        df = read_file(file_path)
        
        # Store the dataframe globally (in production, use sessions or database)
        current_data['df'] = df
        current_data['file_path'] = file_path
        current_data['filename'] = filename
        
        # Perform data quality analysis
        analyzer = DataQualityAnalyzer()
        quality_report = analyzer.analyze(df)

        # Store error_cells in current_data for AI fixing
        current_data['error_cells'] = quality_report['error_cells']
        current_data['column_types'] = quality_report['column_types']

        app.logger.info(f"Successfully processed file: {filename} ({df.shape[0]} rows, {df.shape[1]} columns)")
        app.logger.info(f"Found {len(quality_report['error_cells'])} problematic cells")
        app.logger.info(f"DEBUG: error_cells = {quality_report['error_cells']}")
        
        return jsonify({
            'success': True,
            'data': quality_report['data'][:101],  # Include header + 100 rows max
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'column_types': quality_report['column_types'],
            'error_cells': quality_report['error_cells'],
            'warnings': quality_report['warnings'],
            'filename': filename,
            'message': f"Successfully uploaded {filename} - {len(quality_report['error_cells'])} cells flagged for review"
        })
    
    except FileNotFoundError as e:
        return jsonify({'error': f"File error: {str(e)}"}), 400
    
    except ValueError as e:
        return jsonify({'error': f"Value error: {str(e)}"}), 400
    
    except Exception as e:
        app.logger.error(f"Error in /upload endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"An error occurred while uploading: {str(e)}",
            'type': type(e).__name__
        }), 500

@app.route('/load', methods=['POST'])
def load_file():
    """Load a file and return its data with quality analysis (legacy endpoint for file path)"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({'error': 'file_path is required'}), 400
        
        file_path = data['file_path']
        
        # Read the file using your existing function
        df = read_file(file_path)
        
        # Store the dataframe globally (in production, use sessions or database)
        current_data['df'] = df
        current_data['file_path'] = file_path
        
        # Perform data quality analysis
        analyzer = DataQualityAnalyzer()
        quality_report = analyzer.analyze(df)
        
        return jsonify({
            'success': True,
            'data': quality_report['data'][:101],  # Include header + 100 rows max
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'column_types': quality_report['column_types'],
            'error_cells': quality_report['error_cells'],
            'warnings': quality_report['warnings']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_data():
    """Process data with column conversion"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'Request body is empty'}), 400
        
        if 'column' not in data:
            return jsonify({'error': 'Missing required field: column'}), 400
        
        if 'format' not in data:
            return jsonify({'error': 'Missing required field: format'}), 400
        
        column = data['column']
        target_format = data['format']
        file_path = data.get('file_path')
        
        # Validate column name
        if not column or not isinstance(column, str):
            return jsonify({'error': 'Column name must be a non-empty string'}), 400
        
        # Validate format
        if not target_format or not isinstance(target_format, str):
            return jsonify({'error': 'Format must be a non-empty string'}), 400
        
        # Load file if file_path is provided, otherwise use current data
        if file_path and os.path.exists(file_path):
            df = read_file(file_path)
            current_data['df'] = df
            current_data['file_path'] = file_path
        elif 'df' in current_data:
            df = current_data['df'].copy()
        else:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        # Validate that column exists
        if column not in df.columns:
            available_columns = ', '.join(df.columns.tolist())
            return jsonify({
                'error': f"Column '{column}' not found in data",
                'available_columns': df.columns.tolist(),
                'hint': f"Available columns are: {available_columns}"
            }), 400
        
        # Record action if recording is enabled
        if is_recording:
            record_action('convert_column', 
                         column_name=column,
                         target_type=target_format,
                         format_spec=None)
        
        # Convert the column
        processed_df = convert_column(df, column, target_format, None)
        current_data['df'] = processed_df
        
        # Convert processed DataFrame to list of lists
        data_list = []
        data_list.append(processed_df.columns.tolist())
        for _, row in processed_df.head(100).iterrows():
            # Handle NaN and NaT values
            row_data = []
            for val in row:
                if pd.isna(val):
                    row_data.append(None)
                elif isinstance(val, pd.Timestamp):
                    row_data.append(val.isoformat())
                else:
                    row_data.append(val)
            data_list.append(row_data)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': processed_df.columns.tolist(),
            'shape': processed_df.shape,
            'dtypes': {col: str(dtype) for col, dtype in processed_df.dtypes.items()},
            'message': f"Successfully converted column '{column}' to {target_format}"
        })
    
    except KeyError as e:
        return jsonify({
            'error': f"Column error: {str(e)}",
            'type': 'KeyError'
        }), 400
    
    except ValueError as e:
        return jsonify({
            'error': f"Value error: {str(e)}",
            'type': 'ValueError'
        }), 400
    
    except Exception as e:
        app.logger.error(f"Error in /process endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"An unexpected error occurred: {str(e)}",
            'type': type(e).__name__
        }), 500

@app.route('/export', methods=['POST'])
def export_file():
    """Export processed data to file"""
    try:
        data = request.get_json()
        
        if 'df' not in current_data:
            return jsonify({'error': 'No data to export. Please load and process data first.'}), 400
        
        output_path = data.get('output_path', 'exported_data.csv')
        
        # Export using your existing function
        export_data(current_data['df'], output_path)
        
        return jsonify({
            'success': True,
            'message': f'Data exported to {output_path}',
            'file_path': output_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/columns', methods=['GET'])
def get_columns():
    """Get column information for loaded data"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        df = current_data['df']
        columns_info = []
        
        for col in df.columns:
            columns_info.append({
                'name': col,
                'dtype': str(df[col].dtype),
                'sample_values': df[col].head(5).tolist()
            })
        
        return jsonify({
            'success': True,
            'columns': columns_info,
            'total_columns': len(df.columns),
            'total_rows': len(df)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ETL OPERATIONS ENDPOINTS (transformations)
# ============================================================================

@app.route('/etl/remove-nulls', methods=['POST'])
def etl_remove_nulls():
    """Remove rows containing null values"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        data = request.get_json()
        columns = data.get('columns')  # None = all columns
        how = data.get('how', 'any')  # 'any' or 'all'
        
        df = current_data['df'].copy()
        df_cleaned, report = etl_ops.remove_null_rows(df, columns=columns, how=how)
        
        current_data['df'] = df_cleaned
        
        # Record step if recording
        if step_recorder.is_recording:
            step_recorder.record_step('remove_null_rows', 
                                     {'columns': columns, 'how': how}, 
                                     report)
        
        # Convert to response format
        data_list = _dataframe_to_list(df_cleaned)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_cleaned.columns.tolist(),
            'shape': df_cleaned.shape,
            'report': report,
            'message': f"Removed {report['rows_removed']} rows containing null values"
        })
    
    except Exception as e:
        logger.error(f"Error in /etl/remove-nulls: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/remove-duplicates', methods=['POST'])
def etl_remove_duplicates():
    """Remove duplicate rows"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        columns = data.get('columns')  # None = all columns
        keep = data.get('keep', 'first')  # 'first', 'last', or False
        
        df = current_data['df'].copy()
        df_cleaned, report = etl_ops.remove_duplicate_rows(df, columns=columns, keep=keep)
        
        current_data['df'] = df_cleaned
        
        if step_recorder.is_recording:
            step_recorder.record_step('remove_duplicate_rows',
                                     {'columns': columns, 'keep': keep},
                                     report)
        
        data_list = _dataframe_to_list(df_cleaned)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_cleaned.columns.tolist(),
            'shape': df_cleaned.shape,
            'report': report,
            'message': f"Removed {report['rows_removed']} duplicate rows"
        })
    
    except Exception as e:
        logger.error(f"Error in /etl/remove-duplicates: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/find-replace', methods=['POST'])
def etl_find_replace():
    """Find and replace values in a column"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        
        if not data or 'column' not in data or 'find_value' not in data or 'replace_value' not in data:
            return jsonify({'error': 'column, find_value, and replace_value are required'}), 400
        
        column = data['column']
        find_value = data['find_value']
        replace_value = data['replace_value']
        use_regex = data.get('use_regex', False)
        
        df = current_data['df'].copy()
        df_modified, report = etl_ops.find_replace(df, column, find_value, replace_value, use_regex)
        
        current_data['df'] = df_modified
        
        if step_recorder.is_recording:
            step_recorder.record_step('find_replace',
                                     {'column': column, 'find_value': find_value, 
                                      'replace_value': replace_value, 'use_regex': use_regex},
                                     report)
        
        data_list = _dataframe_to_list(df_modified)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_modified.columns.tolist(),
            'shape': df_modified.shape,
            'report': report,
            'message': f"Made {report['replacements_made']} replacements in column '{column}'"
        })
    
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /etl/find-replace: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/fill-nulls', methods=['POST'])
def etl_fill_nulls():
    """Fill null values in a column"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        
        if not data or 'column' not in data or 'method' not in data:
            return jsonify({'error': 'column and method are required'}), 400
        
        column = data['column']
        method = data['method']  # 'forward', 'backward', 'mean', 'median', 'mode', 'constant'
        value = data.get('value')
        
        df = current_data['df'].copy()
        df_modified, report = etl_ops.fill_null_values(df, column, method, value)
        
        current_data['df'] = df_modified
        
        if step_recorder.is_recording:
            step_recorder.record_step('fill_null_values',
                                     {'column': column, 'method': method, 'value': value},
                                     report)
        
        data_list = _dataframe_to_list(df_modified)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_modified.columns.tolist(),
            'shape': df_modified.shape,
            'report': report,
            'message': f"Filled {report['nulls_filled']} null values in column '{column}'"
        })
    
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /etl/fill-nulls: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/rename-column', methods=['POST'])
def etl_rename_column():
    """Rename a column"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        
        if not data or 'old_name' not in data or 'new_name' not in data:
            return jsonify({'error': 'old_name and new_name are required'}), 400
        
        old_name = data['old_name']
        new_name = data['new_name']
        
        df = current_data['df'].copy()
        df_modified, report = etl_ops.rename_column(df, old_name, new_name)
        
        current_data['df'] = df_modified
        
        if step_recorder.is_recording:
            step_recorder.record_step('rename_column',
                                     {'old_name': old_name, 'new_name': new_name},
                                     report)
        
        data_list = _dataframe_to_list(df_modified)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_modified.columns.tolist(),
            'shape': df_modified.shape,
            'report': report,
            'message': f"Renamed column '{old_name}' to '{new_name}'"
        })
    
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /etl/rename-column: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/remove-column', methods=['POST'])
def etl_remove_column():
    """Remove a column"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        
        if not data or 'column' not in data:
            return jsonify({'error': 'column is required'}), 400
        
        column = data['column']
        
        df = current_data['df'].copy()
        df_modified, report = etl_ops.remove_column(df, column)
        
        current_data['df'] = df_modified
        
        if step_recorder.is_recording:
            step_recorder.record_step('remove_column',
                                     {'column': column},
                                     report)
        
        data_list = _dataframe_to_list(df_modified)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_modified.columns.tolist(),
            'shape': df_modified.shape,
            'report': report,
            'message': f"Removed column '{column}'"
        })
    
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /etl/remove-column: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/filter-rows', methods=['POST'])
def etl_filter_rows():
    """Filter rows based on a condition"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        
        if not data or 'column' not in data or 'operator' not in data or 'value' not in data:
            return jsonify({'error': 'column, operator, and value are required'}), 400
        
        column = data['column']
        operator = data['operator']
        value = data['value']
        
        df = current_data['df'].copy()
        df_filtered, report = etl_ops.filter_rows(df, column, operator, value)
        
        current_data['df'] = df_filtered
        
        if step_recorder.is_recording:
            step_recorder.record_step('filter_rows',
                                     {'column': column, 'operator': operator, 'value': value},
                                     report)
        
        data_list = _dataframe_to_list(df_filtered)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_filtered.columns.tolist(),
            'shape': df_filtered.shape,
            'report': report,
            'message': f"Filtered {report['rows_removed']} rows"
        })
    
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /etl/filter-rows: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/trim-whitespace', methods=['POST'])
def etl_trim_whitespace():
    """Trim whitespace from columns"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json() or {}
        columns = data.get('columns')  # None = all string columns
        
        df = current_data['df'].copy()
        df_modified, report = etl_ops.trim_whitespace(df, columns)
        
        current_data['df'] = df_modified
        
        if step_recorder.is_recording:
            step_recorder.record_step('trim_whitespace',
                                     {'columns': columns},
                                     report)
        
        data_list = _dataframe_to_list(df_modified)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_modified.columns.tolist(),
            'shape': df_modified.shape,
            'report': report,
            'message': f"Trimmed whitespace from {len(report['columns_processed'])} columns"
        })
    
    except Exception as e:
        logger.error(f"Error in /etl/trim-whitespace: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/change-case', methods=['POST'])
def etl_change_case():
    """Change text case in a column"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        
        if not data or 'column' not in data or 'case_type' not in data:
            return jsonify({'error': 'column and case_type are required'}), 400
        
        column = data['column']
        case_type = data['case_type']  # 'upper', 'lower', 'title', 'capitalize'
        
        df = current_data['df'].copy()
        df_modified, report = etl_ops.change_case(df, column, case_type)
        
        current_data['df'] = df_modified
        
        if step_recorder.is_recording:
            step_recorder.record_step('change_case',
                                     {'column': column, 'case_type': case_type},
                                     report)
        
        data_list = _dataframe_to_list(df_modified)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_modified.columns.tolist(),
            'shape': df_modified.shape,
            'report': report,
            'message': f"Changed case to {case_type} in column '{column}'"
        })
    
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /etl/change-case: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/etl/sort-data', methods=['POST'])
def etl_sort_data():
    """Sort data by columns"""
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json()
        
        if not data or 'columns' not in data:
            return jsonify({'error': 'columns array is required'}), 400
        
        columns = data['columns']
        ascending = data.get('ascending', True)
        
        df = current_data['df'].copy()
        df_sorted, report = etl_ops.sort_data(df, columns, ascending)
        
        current_data['df'] = df_sorted
        
        if step_recorder.is_recording:
            step_recorder.record_step('sort_data',
                                     {'columns': columns, 'ascending': ascending},
                                     report)
        
        data_list = _dataframe_to_list(df_sorted)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_sorted.columns.tolist(),
            'shape': df_sorted.shape,
            'report': report,
            'message': f"Sorted data by {columns}"
        })
    
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /etl/sort-data: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# STEP RECORDING ENDPOINTS (Renamed from Macro Recording)
# ============================================================================

@app.route('/steps/start', methods=['POST'])
def start_recording_steps():
    """Start recording transformation steps"""
    try:
        step_recorder.start_recording()
        
        # Also set legacy flags for backward compatibility
        global is_recording, recorded_actions
        is_recording = True
        recorded_actions = []
        
        return jsonify({
            'success': True,
            'message': 'Started recording steps',
            'is_recording': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/steps/stop', methods=['POST'])
def stop_recording_steps():
    """Stop recording transformation steps"""
    try:
        step_recorder.stop_recording()
        
        global is_recording
        is_recording = False
        
        return jsonify({
            'success': True,
            'message': 'Stopped recording steps',
            'is_recording': False,
            'steps_count': len(step_recorder.steps)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/steps/get', methods=['GET'])
def get_recorded_steps():
    """Get all recorded steps"""
    try:
        return jsonify({
            'success': True,
            'steps': step_recorder.get_steps(),
            'steps_count': len(step_recorder.steps),
            'is_recording': step_recorder.is_recording
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/steps/clear', methods=['POST'])
def clear_recorded_steps():
    """Clear all recorded steps"""
    try:
        step_recorder.clear_steps()
        
        global recorded_actions
        recorded_actions = []
        
        return jsonify({
            'success': True,
            'message': 'Cleared all recorded steps'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/steps/save', methods=['POST'])
def save_recorded_steps():
    """Save recorded steps to file"""
    try:
        data = request.get_json()
        step_name = data.get('name', 'steps')
        file_path = f"recordings/{step_name}.json"
        
        os.makedirs('recordings', exist_ok=True)
        
        step_recorder.save_steps(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(step_recorder.steps)} steps to {file_path}',
            'file_path': file_path,
            'steps_count': len(step_recorder.steps)
        })
    
    except Exception as e:
        logger.error(f"Error saving steps: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/steps/load', methods=['POST'])
def load_recorded_steps():
    """Load steps from file"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'file_path is required'}), 400
        
        step_recorder.load_steps(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Loaded {len(step_recorder.steps)} steps from {file_path}',
            'steps': step_recorder.get_steps(),
            'steps_count': len(step_recorder.steps)
        })
    
    except Exception as e:
        logger.error(f"Error loading steps: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/steps/replay', methods=['POST'])
def replay_recorded_steps():
    """Replay all recorded steps on current or specified data"""
    try:
        data = request.get_json() or {}
        file_path = data.get('file_path')
        
        # Load data if file_path provided, otherwise use current data
        if file_path:
            df = read_file(file_path)
        elif 'df' in current_data:
            df = current_data['df'].copy()
        else:
            return jsonify({'error': 'No data loaded. Provide file_path or load data first.'}), 400
        
        # Replay steps
        df_transformed, reports = step_recorder.replay_steps(df)
        
        # Store transformed data
        current_data['df'] = df_transformed
        if file_path:
            current_data['file_path'] = file_path
        
        data_list = _dataframe_to_list(df_transformed)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df_transformed.columns.tolist(),
            'shape': df_transformed.shape,
            'reports': reports,
            'steps_applied': len(reports),
            'message': f'Successfully applied {len(reports)} steps'
        })
    
    except Exception as e:
        logger.error(f"Error replaying steps: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# ============================================================================
# LEGACY RECORDING ENDPOINTS (for backward compatibility)
# ============================================================================

@app.route('/recording/start', methods=['POST'])
def start_recording():
    """Start recording actions"""
    global is_recording, recorded_actions
    is_recording = True
    recorded_actions = []
    
    return jsonify({
        'success': True,
        'message': 'Recording started',
        'is_recording': is_recording
    })

@app.route('/recording/stop', methods=['POST'])
def stop_recording():
    """Stop recording actions"""
    global is_recording
    is_recording = False
    
    return jsonify({
        'success': True,
        'message': 'Recording stopped',
        'is_recording': is_recording,
        'actions_count': len(recorded_actions)
    })

@app.route('/recording/save', methods=['POST'])
def save_recording():
    """Save recorded actions to file"""
    try:
        data = request.get_json()
        recording_name = data.get('name', 'recording')
        file_path = f"recordings/{recording_name}.json"
        
        # Create recordings directory if it doesn't exist
        os.makedirs('recordings', exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(recorded_actions, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Recording saved to {file_path}',
            'actions_count': len(recorded_actions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recording/load', methods=['POST'])
def load_and_run_recording():
    """Load and run a recording"""
    try:
        data = request.get_json()
        recording_path = data.get('recording_path')
        target_file = data.get('file_path')
        
        if not recording_path or not target_file:
            return jsonify({'error': 'Both recording_path and file_path are required'}), 400
        
        # Load recording
        with open(recording_path, 'r') as f:
            actions = json.load(f)
        
        # Load target file
        df = read_file(target_file)
        
        # Apply recorded actions
        for action in actions:
            if action['action_type'] == 'convert_column':
                params = action['params']
                df = convert_column(
                    df,
                    params['column_name'],
                    params['target_type'],
                    params.get('format_spec')
                )
        
        # Store processed data
        current_data['df'] = df
        current_data['file_path'] = target_file
        
        # Convert to response format
        data_list = []
        data_list.append(df.columns.tolist())
        for _, row in df.head(100).iterrows():
            data_list.append(row.tolist())
        
        return jsonify({
            'success': True,
            'data': data_list,
            'message': f'Recording applied successfully. {len(actions)} actions processed.',
            'actions_applied': len(actions)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current application status"""
    return jsonify({
        'is_recording': step_recorder.is_recording,
        'recorded_steps_count': len(step_recorder.steps),
        'has_data': 'df' in current_data,
        'current_file': current_data.get('file_path', None),
        'data_shape': current_data['df'].shape if 'df' in current_data else None,
        # Legacy support
        'recorded_actions_count': len(recorded_actions)
    })

@app.route('/config/apply', methods=['POST'])
def apply_configurations():
    """
    Apply general configuration settings to the application
    
    Request body:
    {
        "setting_name": "value",
        "another_setting": value
    }
    
    Returns: Confirmation of applied settings
    """
    try:
        data = request.get_json() or {}
        
        # Store configuration for future use
        if 'config' not in current_data:
            current_data['config'] = {}
        
        current_data['config'].update(data)
        
        logger.info(f"Applied configurations: {list(data.keys())}")
        
        return jsonify({
            'success': True,
            'message': 'Configurations applied successfully',
            'applied_settings': list(data.keys())
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /config/apply: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MACHINE READABLE TRANSFORM ENDPOINTS
# ============================================================================

@app.route('/transform/label-encode', methods=['POST'])
def label_encode():
    """
    Label encode categorical columns to make data machine-readable
    
    Request body:
    {
        "columns": ["column1", "column2"] or null for all categorical columns,
        "save_mapping": true/false  # whether to save the encoding mapping
    }
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        data = request.get_json() or {}
        columns = data.get('columns')
        save_mapping = data.get('save_mapping', True)
        
        df = current_data['df'].copy()
        encoders = {}
        mappings = {}
        columns_encoded = []
        
        # If no columns specified, find all categorical columns
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            # Exclude tracking column
            if 'Modified_by_AI' in columns:
                columns.remove('Modified_by_AI')
        
        logger.info(f"🔢 Label encoding {len(columns)} columns: {columns}")
        
        for col in columns:
            if col not in df.columns:
                logger.warning(f"Column '{col}' not found, skipping")
                continue
            
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                logger.info(f"  ⏭️  '{col}' is already numeric, skipping")
                continue
            
            # Create and fit label encoder
            le = LabelEncoder()
            
            # Handle NaN values
            non_null_mask = df[col].notna()
            if non_null_mask.sum() == 0:
                logger.warning(f"  ⚠️  '{col}' has all null values, skipping")
                continue
            
            # Fit and transform non-null values
            df.loc[non_null_mask, col] = le.fit_transform(df.loc[non_null_mask, col].astype(str))
            
            # Store encoder and mapping
            encoders[col] = le
            mappings[col] = dict(zip(le.classes_, le.transform(le.classes_)))
            columns_encoded.append(col)
            
            logger.info(f"  ✓ '{col}': {len(le.classes_)} unique values encoded")
        
        current_data['df'] = df
        
        # Store encoders for potential inverse transform
        if save_mapping:
            if 'label_encoders' not in current_data:
                current_data['label_encoders'] = {}
            current_data['label_encoders'].update(encoders)
        
        # Record step if recording
        if step_recorder.is_recording:
            step_recorder.add_step('label_encode', columns=columns, save_mapping=save_mapping)
        
        data_list = _dataframe_to_list(df)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'report': {
                'columns_encoded': columns_encoded,
                'mappings': mappings if save_mapping else None,
                'total_encoded': len(columns_encoded)
            },
            'message': f"Successfully label encoded {len(columns_encoded)} columns"
        })
    
    except Exception as e:
        logger.error(f"Error in /transform/label-encode: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to label encode columns'
        }), 500

@app.route('/transform/one-hot-encode', methods=['POST'])
def one_hot_encode():
    """
    One-hot encode categorical columns to make data machine-readable
    
    Request body:
    {
        "columns": ["column1", "column2"] or null for all categorical columns,
        "drop_first": false,  # whether to drop first category to avoid multicollinearity
        "prefix_sep": "_"     # separator between column name and category
    }
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        data = request.get_json() or {}
        columns = data.get('columns')
        drop_first = data.get('drop_first', False)
        prefix_sep = data.get('prefix_sep', '_')
        
        df = current_data['df'].copy()
        columns_encoded = []
        new_columns_created = []
        
        # If no columns specified, find all categorical columns
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            # Exclude tracking column
            if 'Modified_by_AI' in columns:
                columns.remove('Modified_by_AI')
        
        logger.info(f"🎯 One-hot encoding {len(columns)} columns: {columns}")
        
        for col in columns:
            if col not in df.columns:
                logger.warning(f"Column '{col}' not found, skipping")
                continue
            
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                logger.info(f"  ⏭️  '{col}' is already numeric, skipping")
                continue
            
            # Get unique values count
            unique_count = df[col].nunique()
            
            # Perform one-hot encoding
            one_hot = pd.get_dummies(df[col], prefix=col, prefix_sep=prefix_sep, drop_first=drop_first)
            
            # Track new columns
            new_cols = one_hot.columns.tolist()
            new_columns_created.extend(new_cols)
            
            # Drop original column and add one-hot columns
            df = df.drop(columns=[col])
            df = pd.concat([df, one_hot], axis=1)
            
            columns_encoded.append(col)
            logger.info(f"  ✓ '{col}': {unique_count} unique values → {len(new_cols)} new columns")
        
        current_data['df'] = df
        
        # Record step if recording
        if step_recorder.is_recording:
            step_recorder.add_step('one_hot_encode', columns=columns, drop_first=drop_first, prefix_sep=prefix_sep)
        
        data_list = _dataframe_to_list(df)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'report': {
                'columns_encoded': columns_encoded,
                'new_columns_created': new_columns_created,
                'total_encoded': len(columns_encoded),
                'total_new_columns': len(new_columns_created)
            },
            'message': f"Successfully one-hot encoded {len(columns_encoded)} columns, created {len(new_columns_created)} new columns"
        })
    
    except Exception as e:
        logger.error(f"Error in /transform/one-hot-encode: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to one-hot encode columns'
        }), 500

@app.route('/transform/reverse-label-encode', methods=['POST'])
def reverse_label_encode():
    """
    Reverse label encoding to get original categorical values
    
    Request body:
    {
        "columns": ["column1", "column2"] or null for all previously encoded columns
    }
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        if 'label_encoders' not in current_data or not current_data['label_encoders']:
            return jsonify({'error': 'No label encodings found. Please perform label encoding first.'}), 400
        
        data = request.get_json() or {}
        columns = data.get('columns')
        
        df = current_data['df'].copy()
        encoders = current_data['label_encoders']
        columns_decoded = []
        
        # If no columns specified, decode all encoded columns
        if columns is None:
            columns = list(encoders.keys())
        
        logger.info(f"🔄 Reversing label encoding for {len(columns)} columns: {columns}")
        
        for col in columns:
            if col not in df.columns:
                logger.warning(f"Column '{col}' not found, skipping")
                continue
            
            if col not in encoders:
                logger.warning(f"No encoder found for '{col}', skipping")
                continue
            
            le = encoders[col]
            
            # Handle NaN values
            non_null_mask = df[col].notna()
            if non_null_mask.sum() == 0:
                logger.warning(f"  ⚠️  '{col}' has all null values, skipping")
                continue
            
            # Inverse transform
            df.loc[non_null_mask, col] = le.inverse_transform(df.loc[non_null_mask, col].astype(int))
            columns_decoded.append(col)
            
            logger.info(f"  ✓ '{col}': decoded to original values")
        
        current_data['df'] = df
        
        data_list = _dataframe_to_list(df)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'report': {
                'columns_decoded': columns_decoded,
                'total_decoded': len(columns_decoded)
            },
            'message': f"Successfully reversed label encoding for {len(columns_decoded)} columns"
        })
    
    except Exception as e:
        logger.error(f"Error in /transform/reverse-label-encode: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to reverse label encoding'
        }), 500

# ============================================================================
# DATA FITNESS & EVOLUTIONARY CLEANING ENDPOINTS
# ============================================================================

@app.route('/fitness/evaluate', methods=['POST'])
def evaluate_fitness():
    """
    Evaluate fitness/health of all records in the loaded dataset
    Returns detailed fitness scores and health status for each record
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        df = current_data['df']
        
        # Evaluate fitness
        logger.info("Evaluating data fitness...")
        fitness_summary = evaluate_data_fitness(df)
        
        logger.info(f"Fitness evaluation complete. Average fitness: {fitness_summary['average_fitness']:.2f}%")
        
        return jsonify({
            'success': True,
            'summary': {
                'total_records': fitness_summary['total_records'],
                'average_fitness': fitness_summary['average_fitness'],
                'min_fitness': fitness_summary['min_fitness'],
                'max_fitness': fitness_summary['max_fitness'],
                'health_breakdown': {
                    'excellent': fitness_summary['excellent_records'],
                    'good': fitness_summary['good_records'],
                    'fair': fitness_summary['fair_records'],
                    'poor': fitness_summary['poor_records'],
                    'critical': fitness_summary['critical_records']
                },
                'records_needing_cleaning': fitness_summary['records_needing_cleaning']
            },
            'detailed_results': fitness_summary['detailed_results'][:100],  # Limit to first 100 for performance
            'message': f"Evaluated {fitness_summary['total_records']} records. "
                      f"Average fitness: {fitness_summary['average_fitness']:.2f}%"
        })
    
    except Exception as e:
        logger.error(f"Error in /fitness/evaluate endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to evaluate fitness: {str(e)}",
            'type': type(e).__name__
        }), 500

@app.route('/fitness/record/<int:row_index>', methods=['GET'])
def evaluate_record_fitness(row_index):
    """
    Evaluate fitness of a specific record
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        df = current_data['df']
        
        if row_index < 0 or row_index >= len(df):
            return jsonify({'error': f'Row index {row_index} out of range (0-{len(df)-1})'}), 400
        
        evaluator = DataFitnessEvaluator(df)
        fitness = evaluator.evaluate_record_fitness(row_index)
        
        return jsonify({
            'success': True,
            'row_index': row_index,
            'fitness': fitness
        })
    
    except Exception as e:
        logger.error(f"Error evaluating record fitness: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/fitness/sensitive-columns', methods=['GET'])
def detect_sensitive_columns():
    """
    Detect columns with sensitive data that shouldn't be AI-imputed.
    Includes: Date of Birth, NIC, Passport, ID numbers, etc.
    
    Returns:
    {
        'success': true,
        'sensitive_columns': {
            'column_name': {
                'reason': 'string explaining why',
                'severity': 'high|medium',
                'recommendation': 'string',
                'has_missing': number,
                'total_missing_pct': number
            }
        },
        'message': 'string'
    }
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        df = current_data['df']
        evaluator = DataFitnessEvaluator(df)
        sensitive_cols = evaluator.detect_sensitive_columns()
        
        logger.info(f"Detected {len(sensitive_cols)} sensitive columns")
        
        return jsonify({
            'success': True,
            'sensitive_columns': sensitive_cols,
            'count': len(sensitive_cols),
            'message': f"Detected {len(sensitive_cols)} columns with potentially sensitive data that may need special handling during imputation."
        })
    
    except Exception as e:
        logger.error(f"Error detecting sensitive columns: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'sensitive_columns': {}}), 500

@app.route('/clean/evolutionary', methods=['POST'])
def clean_evolutionary():
    """
    Clean data using evolutionary algorithms.

    When specific columns are provided, uses cell-level evolution (evolve_error_cells)
    which handles all error types (missing, non_numeric, mixed_content, etc.).

    When no columns are specified, uses record-level cleaning (clean_data_evolutionary)
    which focuses on missing value imputation.

    Request body:
    {
        "method": "ga|pso|de|es|hybrid",
        "save_result": true/false,
        "track_modifications": true/false,
        "columns": ["col1", "col2", ...],  // Optional: specific columns to clean
        "parameters": {
            // Algorithm-specific parameters
        }
    }
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        method = data.get('method', 'hybrid').lower()
        save_result = data.get('save_result', True)
        track_modifications = data.get('track_modifications', True)
        parameters = data.get('parameters', {})
        selected_columns = data.get('columns', None)  # Optional: specific columns to clean

        # Validate method
        valid_methods = ['ga', 'pso', 'de', 'es', 'hybrid']
        if method not in valid_methods:
            return jsonify({
                'error': f"Invalid method: {method}",
                'valid_methods': valid_methods
            }), 400

        df = current_data['df'].copy()
        original_df = df.copy()  # Keep a copy for comparison

        logger.info(f"🚀 Starting evolutionary cleaning with method: {method.upper()}")

        # ============================================================================
        # COLUMN-BASED CLEANING: Use evolve_error_cells for specific columns
        # This handles ALL error types (missing, non_numeric, mixed_content, etc.)
        # ============================================================================
        if selected_columns and len(selected_columns) > 0:
            logger.info(f"📌 Column-based cleaning mode for columns: {selected_columns}")

            # Validate columns exist
            invalid_cols = [c for c in selected_columns if c not in df.columns]
            if invalid_cols:
                return jsonify({
                    'error': f"Invalid columns: {invalid_cols}",
                    'valid_columns': df.columns.tolist()
                }), 400

            # Get column indices for selected columns
            selected_col_indices = [df.columns.get_loc(col) for col in selected_columns]
            logger.info(f"📊 Selected column indices: {selected_col_indices}")

            # Auto-detect error cells using DataQualityAnalyzer
            logger.info("🔍 Detecting error cells using DataQualityAnalyzer...")
            analyzer = DataQualityAnalyzer()
            quality_report = analyzer.analyze(df)
            all_error_cells = quality_report.get('error_cells', [])
            logger.info(f"📋 Total error cells detected: {len(all_error_cells)}")
            logger.info(f"📋 All error cells: {all_error_cells}")

            # Filter error cells to only include those from selected columns
            filtered_error_cells = [
                cell for cell in all_error_cells
                if cell['col'] in selected_col_indices
            ]
            logger.info(f"🎯 Error cells in selected columns: {len(filtered_error_cells)}")
            logger.info(f"🎯 Filtered error cells: {filtered_error_cells}")

            if not filtered_error_cells:
                logger.info("✅ No error cells found in selected columns - data is already clean!")

                # Re-analyze for updated quality report
                data_list = _dataframe_to_list(df, max_rows=100)

                return jsonify({
                    'success': True,
                    'method': method.upper(),
                    'cells_evolved': 0,
                    'cells_fixed': 0,
                    'average_fitness_before': 1.0,
                    'average_fitness_after': 1.0,
                    'fitness_improvement': 0.0,
                    'ai_modified_cells': [],
                    'evolved_cells': [],
                    'data': data_list,
                    'columns': df.columns.tolist(),
                    'shape': df.shape,
                    'error_cells': all_error_cells,
                    'column_types': quality_report.get('column_types', {}),
                    'warnings': quality_report.get('warnings', []),
                    'message': f"No error cells found in selected columns {selected_columns} - data is already clean!"
                })

            # Build config from parameters
            config = {
                'population_size': parameters.get('population_size', 30),
                'generations': parameters.get('generations', 50),
                'mutation_rate': parameters.get('mutation_rate', 0.1),
                'crossover_rate': parameters.get('crossover_rate', 0.8),
                'early_stopping': parameters.get('early_stopping', True),
                'patience': parameters.get('patience', 10),
                'fitness_threshold': parameters.get('fitness_threshold', 0.95),
                # PSO specific
                'inertia_weight': parameters.get('inertia_weight', 0.7),
                'cognitive_coeff': parameters.get('cognitive_coeff', 1.5),
                'social_coeff': parameters.get('social_coeff', 1.5),
                'pso_topology': parameters.get('pso_topology', 'gbest'),
                'pso_variant': parameters.get('pso_variant', 'standard'),
                # DE specific
                'differential_weight': parameters.get('differential_weight', 0.8),
                'crossover_prob': parameters.get('crossover_prob', 0.9),
                'de_mutation_strategy': parameters.get('de_mutation_strategy', 'DE/rand/1'),
            }

            logger.info(f"🧬 Running evolve_error_cells with {method.upper()} on {len(filtered_error_cells)} error cells...")

            # Run cell-level evolution using evolve_error_cells from evolutionary_cell_cleaner.py
            evolved_df, result = evolve_error_cells(
                df=df,
                error_cells=filtered_error_cells,
                method=method,
                config=config
            )

            logger.info(f"✅ Evolution complete: {result['cells_fixed']}/{result['cells_evolved']} cells fixed")
            logger.info(f"📈 Fitness: {result['average_fitness_before']:.2%} → {result['average_fitness_after']:.2%}")

            # Save result if requested
            if save_result:
                current_data['df'] = evolved_df
                current_data['df_original'] = original_df

            # Convert evolved data to list format
            data_list = _dataframe_to_list(evolved_df, max_rows=100)

            # Re-analyze data quality after evolution
            updated_quality_report = analyzer.analyze(evolved_df)
            updated_error_cells = updated_quality_report.get('error_cells', [])
            logger.info(f"📊 After evolution: {len(updated_error_cells)} error cells remaining")

            # Extract AI-modified cells for green highlighting on frontend
            # These are cells that were successfully evolved/fixed
            ai_modified_cells = []
            for cell in result.get('evolved_cells', []):
                # Check if fitness improved (cell was fixed)
                if cell.get('fitness_after', 0) > cell.get('fitness_before', 0):
                    ai_modified_cells.append({
                        'row': cell['row'],  # 1-indexed for frontend display
                        'col': cell['col'],
                        'col_name': cell.get('col_name', ''),
                        'original_value': cell.get('original_value'),
                        'evolved_value': cell.get('evolved_value'),
                        'fitness_before': cell.get('fitness_before', 0),
                        'fitness_after': cell.get('fitness_after', 0)
                    })

            logger.info(f"🟢 {len(ai_modified_cells)} cells marked as AI-modified for green highlighting")

            return jsonify({
                'success': True,
                'method': method.upper(),
                'cells_evolved': result['cells_evolved'],
                'cells_fixed': result['cells_fixed'],
                'cells_failed': result.get('cells_failed', 0),
                'average_fitness_before': result['average_fitness_before'],
                'average_fitness_after': result['average_fitness_after'],
                'fitness_improvement': result['fitness_improvement'],
                'evolved_cells': result['evolved_cells'],
                'ai_modified_cells': ai_modified_cells,
                'fitness_history': result.get('fitness_history', []),
                'data': data_list,
                'columns': evolved_df.columns.tolist(),
                'shape': evolved_df.shape,
                'error_cells': updated_error_cells,
                'column_types': updated_quality_report.get('column_types', {}),
                'warnings': updated_quality_report.get('warnings', []),
                'message': f"Evolved {result['cells_evolved']} cells in columns {selected_columns} using {method.upper()}. "
                          f"{result['cells_fixed']} cells fixed. "
                          f"Fitness improved by {result['fitness_improvement']:.2%}."
            })

        # ============================================================================
        # FULL DATASET CLEANING: Use clean_data_evolutionary for all columns
        # This focuses on missing value imputation across all columns
        # ============================================================================
        else:
            logger.info("📊 Full dataset cleaning mode (all columns)")

            # Clean data using record-level evolutionary cleaning
            cleaned_df, report = clean_data_evolutionary(
                df,
                method=method,
                track_modifications=track_modifications,
                **parameters
            )

            # Track modified cells by comparing original and cleaned DataFrames
            ai_modified_cells = []
            columns_to_check = [c for c in df.columns if c != 'Modified_by_AI']

            for col in columns_to_check:
                if col not in cleaned_df.columns or col not in original_df.columns:
                    continue
                col_idx = df.columns.get_loc(col)
                for row_idx in range(len(original_df)):
                    original_val = original_df.iloc[row_idx][col]
                    cleaned_val = cleaned_df.iloc[row_idx][col]

                    # Check if value changed (was null/missing and is now filled)
                    if pd.isna(original_val) and not pd.isna(cleaned_val):
                        ai_modified_cells.append({
                            'row': row_idx + 1,  # 1-indexed for frontend display
                            'col': col_idx,
                            'col_name': col,
                            'original_value': None,
                            'evolved_value': str(cleaned_val) if not isinstance(cleaned_val, (int, float)) else cleaned_val,
                            'fitness_before': 0.0,
                            'fitness_after': 1.0
                        })

            logger.info(f"🟢 Tracked {len(ai_modified_cells)} AI-modified cells")

            # Optionally save the cleaned data
            if save_result:
                current_data['df'] = cleaned_df
                current_data['df_original'] = original_df  # Keep backup

            # Convert cleaned data to list format (first 100 rows)
            data_list = _dataframe_to_list(cleaned_df, max_rows=100)

            # Re-analyze for updated error cells
            analyzer = DataQualityAnalyzer()
            updated_quality_report = analyzer.analyze(cleaned_df)
            updated_error_cells = updated_quality_report.get('error_cells', [])

            logger.info(f"✅ Cleaning complete. Fitness improvement: {report['improvement']['fitness_increase']:.2f}%")

            return jsonify({
                'success': True,
                'method': method.upper(),
                'report': report,
                'cells_evolved': report['modifications'].get('records_modified', 0),
                'cells_fixed': report['improvement'].get('records_fixed', 0),
                'average_fitness_before': report['before']['average_fitness'] / 100,
                'average_fitness_after': report['after']['average_fitness'] / 100,
                'fitness_improvement': report['improvement']['fitness_increase'] / 100,
                'ai_modified_cells': ai_modified_cells,
                'evolved_cells': [],
                'data': data_list,
                'columns': cleaned_df.columns.tolist(),
                'shape': cleaned_df.shape,
                'error_cells': updated_error_cells,
                'column_types': updated_quality_report.get('column_types', {}),
                'warnings': updated_quality_report.get('warnings', []),
                'message': f"Data cleaned using {method.upper()}. "
                          f"Fitness improved by {report['improvement']['fitness_increase']:.2f}%. "
                          f"{report['improvement']['records_fixed']} records fixed. "
                          f"{report['modifications']['records_modified'] or 0} records modified by AI."
            })

    except Exception as e:
        logger.error(f"Error in /clean/evolutionary endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to clean data: {str(e)}",
            'type': type(e).__name__
        }), 500

@app.route('/clean/compare', methods=['POST'])
def compare_cleaning_methods():
    """
    Compare different evolutionary cleaning methods
    Returns fitness improvements for each method
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        df = current_data['df'].copy()
        
        methods = ['ga', 'pso', 'de', 'es', 'hybrid']
        results = {}
        
        logger.info("Comparing evolutionary cleaning methods...")
        
        for method in methods:
            try:
                logger.info(f"Testing {method.upper()}...")
                
                # Use smaller parameters for comparison speed
                params = {
                    'ga': {'population_size': 20, 'generations': 30},
                    'pso': {'n_particles': 15, 'iterations': 30},
                    'de': {'pop_size': 15, 'max_iter': 30},
                    'es': {'mu': 10, 'lambda_': 30, 'generations': 30},
                    'hybrid': {}
                }
                
                cleaned_df, report = clean_data_evolutionary(
                    df, method=method, **params.get(method, {})
                )
                
                results[method] = {
                    'before_fitness': report['before']['average_fitness'],
                    'after_fitness': report['after']['average_fitness'],
                    'improvement': report['improvement']['fitness_increase'],
                    'records_fixed': report['improvement']['records_fixed']
                }
            except Exception as e:
                logger.warning(f"Method {method} failed: {e}")
                results[method] = {'error': str(e)}
        
        # Find best method
        best_method = max(
            [m for m in methods if 'error' not in results[m]],
            key=lambda m: results[m]['improvement']
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'best_method': best_method,
            'best_improvement': results[best_method]['improvement'],
            'message': f"Comparison complete. Best method: {best_method.upper()}"
        })
    
    except Exception as e:
        logger.error(f"Error comparing methods: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ============================================================================
# EVOLUTIONARY CELL CLEANER ENDPOINTS (Cell-Level Evolution)
# ============================================================================

@app.route('/clean/evolve-cells', methods=['POST'])
def evolve_error_cells_endpoint():
    """
    Evolve error cells using evolutionary algorithms.

    This endpoint takes error cells detected by the data quality analyzer
    and evolves them to become healthy using the specified evolutionary method.
    Each algorithm uses its unique mechanism:
    - GA: Crossover and mutation from healthy cell populations
    - PSO: Velocity-based particle movement towards healthy cell values
    - DE: Differential evolution with vector differences from healthy cells
    - ES: Evolution strategy with self-adaptive mutation
    - Hybrid: PSO for numeric columns, GA for categorical columns

    Request body:
    {
        "method": "ga|pso|de|es|hybrid",
        "save_result": true/false,
        "error_cells": [{"row": 0, "col": 1, "issues": ["missing_value"]}],  // Optional, auto-detect if not provided
        "config": {
            "population_size": 30,
            "generations": 50,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8,
            // PSO specific (NEW: topology and variant support)
            "inertia_weight": 0.7,
            "inertia_min": 0.4,            // For decay variant
            "inertia_max": 0.9,            // For decay variant
            "cognitive_coeff": 1.5,        // c1 - personal best
            "social_coeff": 1.5,           // c2 - global/local best
            "velocity_clamp": 0.2,
            "pso_topology": "gbest",       // gbest|lbest|ring|random|von_neumann
            "pso_variant": "standard",     // standard|constriction|inertia_decay
            "constriction_factor": 0.729,
            "neighborhood_size": 3,
            // DE specific (NEW: 6 mutation strategies + adaptive)
            "differential_weight": 0.8,    // F - scale factor
            "crossover_prob": 0.9,         // CR
            "de_mutation_strategy": "DE/rand/1",  // DE/rand/1|DE/rand/2|DE/best/1|DE/best/2|DE/current-to-best/1|DE/current-to-rand/1
            "de_crossover_type": "binomial",      // binomial|exponential
            "adaptive_f": false,           // Enable adaptive F
            "adaptive_cr": false,          // Enable adaptive CR
            "f_min": 0.1, "f_max": 1.0,
            "cr_min": 0.1, "cr_max": 1.0,
            // ES specific
            "mu": 10,
            "lambda_": 30,
            "initial_sigma": 0.3,
            // Common
            "early_stopping": true,
            "patience": 10,
            "fitness_threshold": 0.95
        }
    }

    Returns: Evolved DataFrame with fixed cells and evolution metrics (includes PSO/DE specific metrics)
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400

        data = request.get_json() or {}
        method = data.get('method', 'hybrid').lower()
        save_result = data.get('save_result', True)
        config = data.get('config', {})

        # Validate method
        valid_methods = ['ga', 'pso', 'de', 'es', 'hybrid']
        if method not in valid_methods:
            return jsonify({
                'error': f"Invalid method: {method}",
                'valid_methods': valid_methods
            }), 400

        df = current_data['df'].copy()

        # Get selected columns for filtering (NEW: column-based cleaning support)
        selected_columns = data.get('columns', [])

        # Get error cells - either from request or auto-detect
        error_cells = data.get('error_cells')
        if error_cells is None:
            # Auto-detect error cells using DataQualityAnalyzer
            logger.info("Auto-detecting error cells...")
            analyzer = DataQualityAnalyzer()
            quality_report = analyzer.analyze(df)
            error_cells = quality_report.get('error_cells', [])
            logger.info(f"Detected {len(error_cells)} error cells")

        # Filter error cells by selected columns if specified
        if selected_columns:
            logger.info(f"🎯 Column-based cleaning mode: filtering for columns {selected_columns}")
            # Get column indices for selected columns
            selected_col_indices = []
            for col_name in selected_columns:
                if col_name in df.columns:
                    selected_col_indices.append(df.columns.get_loc(col_name))
                else:
                    logger.warning(f"⚠️ Column '{col_name}' not found in dataframe")

            logger.info(f"📊 Selected column indices: {selected_col_indices}")

            # Filter error cells to only include those in selected columns
            original_count = len(error_cells)
            error_cells = [
                cell for cell in error_cells
                if cell.get('col') in selected_col_indices
            ]
            logger.info(f"🔍 Filtered error cells: {original_count} -> {len(error_cells)} (only in selected columns)")
        else:
            logger.info(f"📊 Full dataset cleaning mode (all columns)")

        if not error_cells:
            return jsonify({
                'success': True,
                'message': 'No error cells found - data is already clean!',
                'cells_evolved': 0,
                'cells_fixed': 0
            })

        logger.info(f"Starting cell evolution with {method.upper()} on {len(error_cells)} error cells")

        # Run evolutionary cell cleaning
        evolved_df, result = evolve_error_cells(
            df=df,
            error_cells=error_cells,
            method=method,
            config=config
        )

        # Optionally save the result
        if save_result:
            current_data['df'] = evolved_df
            current_data['df_original'] = df  # Keep backup

        # Convert evolved data to list format (first 100 rows)
        data_list = _dataframe_to_list(evolved_df, max_rows=100)

        logger.info(f"Cell evolution complete: {result['cells_fixed']}/{result['cells_evolved']} cells fixed")
        logger.info(f"Fitness improved from {result['average_fitness_before']:.2%} to {result['average_fitness_after']:.2%}")

        # Re-analyze data quality after evolution to get updated error_cells
        analyzer = DataQualityAnalyzer()
        updated_quality_report = analyzer.analyze(evolved_df)
        updated_error_cells = updated_quality_report.get('error_cells', [])
        logger.info(f"After evolution: {len(updated_error_cells)} error cells remaining")

        # Extract AI-modified cells (cells that were successfully fixed)
        # These will be highlighted in green on the frontend
        ai_modified_cells = []
        for cell in result.get('evolved_cells', []):
            # Check if the cell was actually improved (fitness increased)
            if cell.get('fitness_after', 0) > cell.get('fitness_before', 0):
                ai_modified_cells.append({
                    'row': cell['row'],  # Already 1-indexed from evolve_error_cells
                    'col': cell['col'],
                    'col_name': cell.get('col_name', ''),
                    'original_value': cell.get('original_value'),
                    'evolved_value': cell.get('evolved_value'),
                    'fitness_before': cell.get('fitness_before', 0),
                    'fitness_after': cell.get('fitness_after', 0)
                })

        logger.info(f"✅ {len(ai_modified_cells)} cells marked as AI-modified for green highlighting")

        return jsonify({
            'success': True,
            'method': method.upper(),
            'cells_evolved': result['cells_evolved'],
            'cells_fixed': result['cells_fixed'],
            'cells_failed': result['cells_failed'],
            'average_fitness_before': result['average_fitness_before'],
            'average_fitness_after': result['average_fitness_after'],
            'fitness_improvement': result['fitness_improvement'],
            'evolved_cells': result['evolved_cells'],
            'ai_modified_cells': ai_modified_cells,  # New field for green highlighting
            'fitness_history': result['fitness_history'],
            'data': data_list,
            'columns': evolved_df.columns.tolist(),
            'shape': evolved_df.shape,
            'error_cells': updated_error_cells,
            'column_types': updated_quality_report.get('column_types', {}),
            'warnings': updated_quality_report.get('warnings', []),
            'message': f"Evolved {result['cells_evolved']} cells using {method.upper()}. "
                      f"{result['cells_fixed']} cells fixed. "
                      f"Fitness improved by {result['fitness_improvement']:.2%}."
        })

    except Exception as e:
        logger.error(f"Error in /clean/evolve-cells: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to evolve cells: {str(e)}",
            'type': type(e).__name__
        }), 500


@app.route('/clean/evolve-cells/compare', methods=['POST'])
def compare_cell_evolution_methods():
    """
    Compare all evolutionary methods for cell cleaning.

    Request body:
    {
        "quick_mode": true/false  // Use smaller parameters for speed
    }

    Returns: Comparison of all methods with fitness improvements
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400

        data = request.get_json() or {}
        quick_mode = data.get('quick_mode', True)

        df = current_data['df'].copy()

        # Auto-detect error cells
        analyzer = DataQualityAnalyzer()
        quality_report = analyzer.analyze(df)
        error_cells = quality_report.get('error_cells', [])

        if not error_cells:
            return jsonify({
                'success': True,
                'message': 'No error cells found - data is already clean!',
                'results': {}
            })

        methods = ['ga', 'pso', 'de', 'es', 'hybrid']
        results = {}

        # Configuration for quick vs thorough comparison
        if quick_mode:
            config = {
                'population_size': 15,
                'generations': 20,
                'early_stopping': True,
                'patience': 5
            }
        else:
            config = {
                'population_size': 30,
                'generations': 50,
                'early_stopping': True,
                'patience': 10
            }

        logger.info(f"Comparing cell evolution methods on {len(error_cells)} error cells...")

        for method in methods:
            try:
                logger.info(f"Testing {method.upper()}...")

                evolved_df, result = evolve_error_cells(
                    df=df,
                    error_cells=error_cells,
                    method=method,
                    config=config
                )

                results[method] = {
                    'cells_evolved': result['cells_evolved'],
                    'cells_fixed': result['cells_fixed'],
                    'fitness_before': result['average_fitness_before'],
                    'fitness_after': result['average_fitness_after'],
                    'improvement': result['fitness_improvement'],
                    'fix_rate': result['cells_fixed'] / max(result['cells_evolved'], 1)
                }

                logger.info(f"  {method.upper()}: Fixed {result['cells_fixed']}/{result['cells_evolved']} cells")

            except Exception as e:
                logger.warning(f"Method {method} failed: {e}")
                results[method] = {'error': str(e)}

        # Find best method by fix rate
        valid_results = {m: r for m, r in results.items() if 'error' not in r}
        if valid_results:
            best_method = max(valid_results.keys(), key=lambda m: valid_results[m]['fix_rate'])
            best_result = valid_results[best_method]
        else:
            best_method = None
            best_result = None

        return jsonify({
            'success': True,
            'total_error_cells': len(error_cells),
            'results': results,
            'best_method': best_method,
            'best_fix_rate': best_result['fix_rate'] if best_result else 0,
            'recommendation': f"Use {best_method.upper()} for best results on this dataset" if best_method else "All methods failed",
            'message': f"Comparison complete. Best method: {best_method.upper() if best_method else 'None'}"
        })

    except Exception as e:
        logger.error(f"Error comparing cell evolution methods: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/clean/evolve-cells/preview', methods=['POST'])
def preview_cell_evolution():
    """
    Preview cell evolution without applying changes.
    Shows what cells would be fixed and their evolved values.

    Request body:
    {
        "method": "ga|pso|de|es|hybrid",
        "max_cells": 10  // Limit preview to first N cells
    }

    Returns: Preview of evolved cells without modifying data
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400

        data = request.get_json() or {}
        method = data.get('method', 'hybrid').lower()
        max_cells = data.get('max_cells', 10)

        df = current_data['df'].copy()

        # Auto-detect error cells
        analyzer = DataQualityAnalyzer()
        quality_report = analyzer.analyze(df)
        error_cells = quality_report.get('error_cells', [])[:max_cells]  # Limit for preview

        if not error_cells:
            return jsonify({
                'success': True,
                'message': 'No error cells found - data is already clean!',
                'preview': []
            })

        # Run evolution with quick settings for preview
        config = {
            'population_size': 15,
            'generations': 20,
            'early_stopping': True,
            'patience': 5
        }

        evolved_df, result = evolve_error_cells(
            df=df,
            error_cells=error_cells,
            method=method,
            config=config
        )

        # Format preview
        preview = []
        for cell in result['evolved_cells']:
            # Convert numpy types to Python native types for JSON serialization
            fitness_before = float(cell['fitness_before'])
            fitness_after = float(cell['fitness_after'])
            would_be_fixed = bool(fitness_after > fitness_before + 0.01)

            preview.append({
                'row': int(cell['row']),
                'column': str(cell['col_name']),
                'original_value': cell['original_value'],
                'evolved_value': cell['evolved_value'],
                'issues': cell['issues'],
                'fitness_before': f"{fitness_before:.2%}",
                'fitness_after': f"{fitness_after:.2%}",
                'would_be_fixed': would_be_fixed
            })

        # Store the preview results for later application
        current_data['preview_results'] = {
            'evolved_df': evolved_df,
            'evolved_cells': result['evolved_cells'],
            'method': method,
            'config': config,
            'fitness_before': result['average_fitness_before'],
            'fitness_after': result['average_fitness_after']
        }
        logger.info(f"Stored preview results with {len(result['evolved_cells'])} evolved cells for later application")

        return jsonify({
            'success': True,
            'method': method.upper(),
            'total_error_cells': len(quality_report.get('error_cells', [])),
            'previewed_cells': len(preview),
            'preview': preview,
            'would_fix': sum(1 for p in preview if p['would_be_fixed']),
            'has_cached_preview': True,  # Flag to indicate preview is cached for apply
            'message': f"Preview of {method.upper()} evolution on {len(preview)} cells"
        })

    except Exception as e:
        logger.error(f"Error in cell evolution preview: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/clean/apply-preview', methods=['POST'])
def apply_previewed_changes():
    """
    Apply the previewed cell evolution changes.

    This endpoint applies the exact same changes that were shown in the preview,
    ensuring consistency between preview and apply operations.

    Request body:
    {
        "save_result": true/false
    }

    Returns: Applied changes with the same values as the preview
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400

        if 'preview_results' not in current_data:
            return jsonify({'error': 'No preview available. Please run preview first.'}), 400

        data = request.get_json() or {}
        save_result = data.get('save_result', True)

        preview_data = current_data['preview_results']
        evolved_df = preview_data['evolved_df']
        evolved_cells = preview_data['evolved_cells']
        method = preview_data['method']

        logger.info(f"Applying {len(evolved_cells)} previewed cell changes using {method.upper()}")

        # Save the result if requested
        if save_result:
            current_data['df_original'] = current_data['df'].copy()
            current_data['df'] = evolved_df

        # Convert evolved data to list format
        data_list = _dataframe_to_list(evolved_df, max_rows=100)

        # Re-analyze data quality after applying changes
        analyzer = DataQualityAnalyzer()
        updated_quality_report = analyzer.analyze(evolved_df)
        updated_error_cells = updated_quality_report.get('error_cells', [])

        # Calculate metrics
        cells_fixed = sum(1 for cell in evolved_cells
                        if cell.get('fitness_after', 0) > cell.get('fitness_before', 0) + 0.01)
        cells_failed = len(evolved_cells) - cells_fixed
        fitness_improvement = preview_data['fitness_after'] - preview_data['fitness_before']

        # Extract AI-modified cells for green highlighting
        ai_modified_cells = []
        for cell in evolved_cells:
            if cell.get('fitness_after', 0) > cell.get('fitness_before', 0):
                ai_modified_cells.append({
                    'row': cell['row'],
                    'col': cell['col'],
                    'col_name': cell.get('col_name', ''),
                    'original_value': cell.get('original_value'),
                    'evolved_value': cell.get('evolved_value'),
                    'fitness_before': cell.get('fitness_before', 0),
                    'fitness_after': cell.get('fitness_after', 0)
                })

        # Clear the preview cache
        del current_data['preview_results']

        logger.info(f"Applied preview: {cells_fixed}/{len(evolved_cells)} cells fixed")
        logger.info(f"Fitness improved from {preview_data['fitness_before']:.2%} to {preview_data['fitness_after']:.2%}")

        return jsonify({
            'success': True,
            'method': method.upper(),
            'cells_evolved': len(evolved_cells),
            'cells_fixed': cells_fixed,
            'cells_failed': cells_failed,
            'average_fitness_before': preview_data['fitness_before'],
            'average_fitness_after': preview_data['fitness_after'],
            'fitness_improvement': fitness_improvement,
            'evolved_cells': evolved_cells,
            'ai_modified_cells': ai_modified_cells,
            'fitness_history': [],  # Not tracked for apply-preview
            'data': data_list,
            'columns': evolved_df.columns.tolist(),
            'shape': evolved_df.shape,
            'error_cells': updated_error_cells,
            'column_types': updated_quality_report.get('column_types', {}),
            'warnings': updated_quality_report.get('warnings', []),
            'message': f"Applied {len(evolved_cells)} previewed changes using {method.upper()}. "
                      f"{cells_fixed} cells fixed. "
                      f"Fitness improved by {fitness_improvement:.2%}."
        })

    except Exception as e:
        logger.error(f"Error in /clean/apply-preview: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to apply preview: {str(e)}",
            'type': type(e).__name__
        }), 500


@app.route('/data/restore', methods=['POST'])
def restore_original_data():
    """Restore original data before cleaning"""
    try:
        if 'df_original' not in current_data:
            return jsonify({'error': 'No original data to restore'}), 400
        
        current_data['df'] = current_data['df_original'].copy()
        del current_data['df_original']
        
        return jsonify({
            'success': True,
            'message': 'Original data restored successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# GENETIC ALGORITHM ENDPOINTS (GA Evolution)
# ============================================================================

@app.route('/ga/analyze-population', methods=['POST'])
def analyze_population_fitness():
    """
    Analyze fitness distribution of the population.
    
    Request body:
    {
        "fitness_threshold": 85.0
    }
    
    Returns: Detailed fitness analysis
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        data = request.get_json() or {}
        fitness_threshold = data.get('fitness_threshold', 85.0)
        
        df = current_data['df']
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        analysis = evolver.analyze_population(fitness_threshold=fitness_threshold)
        
        logger.info(f"Population analysis: {analysis['unhealthy_records']} unhealthy, {analysis['healthy_records']} healthy")
        
        return jsonify({
            'success': True,
            'total_records': analysis['total_records'],
            'healthy_records': analysis['healthy_records'],
            'unhealthy_records': analysis['unhealthy_records'],
            'healthy_percentage': analysis['healthy_percentage'],
            'unhealthy_percentage': analysis['unhealthy_percentage'],
            'average_fitness': analysis['avg_fitness'],
            'min_fitness': analysis['min_fitness'],
            'max_fitness': analysis['max_fitness'],
            'fitness_distribution': analysis['fitness_distribution'],
            'fitness_threshold': fitness_threshold,
            'statistics': {
                'std_fitness': analysis['std_fitness']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /ga/analyze-population: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/ga/select-populations', methods=['POST'])
def select_populations():
    """
    Select healthy and unhealthy populations for evolution.
    
    Request body:
    {
        "fitness_threshold": 85.0,
        "healthy_sample_size": null  (null = use all, or specify a number)
    }
    
    Returns: Population configuration
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json() or {}
        fitness_threshold = data.get('fitness_threshold', 85.0)
        healthy_sample_size = data.get('healthy_sample_size')
        
        df = current_data['df']
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        config = evolver.select_populations(fitness_threshold, healthy_sample_size)
        
        logger.info(f"Selected {config.unhealthy_count} unhealthy, {config.healthy_count} healthy")
        
        # Store config in session for next step
        current_data['ga_config'] = config
        
        return jsonify({
            'success': True,
            'unhealthy_count': config.unhealthy_count,
            'healthy_count': config.healthy_count,
            'target_columns': config.target_columns,
            'fitness_threshold': config.fitness_threshold,
            'column_bounds': {k: list(v) for k, v in config.column_bounds.items()}
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /ga/select-populations: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/ga/run-evolution', methods=['POST'])
def run_genetic_algorithm_evolution():
    """
    Run genetic algorithm evolution on unhealthy records.
    
    Request body:
    {
        "population_size": 30,
        "generations": 100,
        "mutation_rate": 0.1,
        "crossover_rate": 0.8,
        "selection_method": "tournament",
        "crossover_method": "single_point",
        "mutation_method": "gaussian",
        "fitness_threshold": 85.0,
        "healthy_sample_size": null,
        "elitism": true,
        "elite_count": 2,
        "early_stopping_enabled": true,
        "early_stopping_patience": 10,
        "track_progress": false
    }
    
    Returns: Evolution results with fitness history and best expression
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json() or {}
        
        # Extract GA config parameters
        ga_config = GAConfig(
            population_size=data.get('population_size', 30),
            generations=data.get('generations', 100),
            mutation_rate=data.get('mutation_rate', 0.1),
            crossover_rate=data.get('crossover_rate', 0.8),
            elitism_rate=data.get('elitism_rate', 0.05),  # Keep top 5%
            selection_method=SelectionMethod(data.get('selection_method', 'tournament')),
            crossover_method=CrossoverMethod(data.get('crossover_method', 'single_point')),
            mutation_method=MutationMethod(data.get('mutation_method', 'gaussian')),
            early_stopping=data.get('early_stopping_enabled', True),
            early_stopping_generations=data.get('early_stopping_patience', 10),
        )
        
        # Validate config
        is_valid, errors = ga_config.validate()
        if not is_valid:
            return jsonify({'error': 'Invalid GA config', 'validation_errors': errors}), 400
        
        df = current_data['df']
        fitness_threshold = data.get('fitness_threshold', 85.0)
        healthy_sample_size = data.get('healthy_sample_size')
        
        # Create evolver and run evolution
        logger.info("Starting GA evolution...")
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        config = evolver.select_populations(fitness_threshold, healthy_sample_size)
        evolved_df, results = evolver.evolve_unhealthy_records(config, ga_config)
        
        # Store evolved data
        current_data['evolved_df'] = evolved_df
        current_data['df_original'] = df
        
        # Format fitness history
        fitness_history = []
        if 'generation_metrics' in results:
            for metric in results['generation_metrics']:
                fitness_history.append({
                    'generation': metric.get('generation', 0),
                    'best_fitness': metric.get('best_fitness', 0),
                    'worst_fitness': metric.get('worst_fitness', 0),
                    'average_fitness': metric.get('average_fitness', 0),
                    'fitness_variance': metric.get('fitness_variance', 0),
                    'population_size': metric.get('population_size', 0)
                })
        
        logger.info(f"GA evolution complete. Fitness improved by {results.get('fitness_metrics', {}).get('improvement', 0):.2f}%")
        
        return jsonify({
            'success': True,
            'fitness_history': fitness_history,
            'fitness_metrics': results.get('fitness_metrics', {}),
            'modification_tracking': results.get('modification_tracking', {}),
            'convergence_achieved': results.get('convergence_achieved', False),
            'total_generations': results.get('total_generations', 0),
            'message': f"GA Evolution completed. Improved {results.get('fitness_metrics', {}).get('records_at_target', 0)} records to target fitness."
        }), 200
    
    except ValueError as e:
        logger.error(f"Invalid parameter in /ga/run-evolution: {str(e)}")
        return jsonify({'error': f'Invalid parameter: {str(e)}', 'type': 'ValueError'}), 400
    except Exception as e:
        logger.error(f"Error in /ga/run-evolution: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/ga/quick-evolve', methods=['POST'])
def quick_evolve_records():
    """
    Quick evolution endpoint - loads data, analyzes, and evolves in one call.
    
    Request body:
    {
        "fitness_threshold": 85.0,
        "population_size": 30,
        "generations": 50,
        "save_result": true
    }
    
    Returns: Evolved DataFrame and results
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json() or {}
        df = current_data['df']
        
        evolved_df, results = evolve_records(
            df,
            fitness_threshold=data.get('fitness_threshold', 85.0),
            healthy_sample_size=data.get('healthy_sample_size'),
            ga_config=GAConfig(
                population_size=data.get('population_size', 30),
                generations=data.get('generations', 50)
            ) if data.get('generations') else None
        )
        
        if data.get('save_result', True):
            current_data['evolved_df'] = evolved_df
            current_data['df_original'] = df
        
        # Convert to list for JSON response
        data_list = _dataframe_to_list(evolved_df, max_rows=100)
        
        return jsonify({
            'success': True,
            'data': data_list,
            'shape': evolved_df.shape,
            'columns': evolved_df.columns.tolist(),
            'results': results,
            'message': 'Quick evolution completed successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /ga/quick-evolve: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


@app.route('/ga/export-evolved', methods=['POST'])
def export_evolved_data():
    """
    Export the evolved/cleaned dataset.
    
    Request body:
    {
        "filename": "evolved_data.csv",
        "format": "csv"  (csv or json)
    }
    
    Returns: Download URL or file path
    """
    try:
        if 'evolved_df' not in current_data:
            return jsonify({'error': 'No evolved data. Run evolution first.'}), 400
        
        data = request.get_json() or {}
        filename = data.get('filename', 'evolved_data')
        format_type = data.get('format', 'csv').lower()
        
        evolved_df = current_data['evolved_df']
        
        # Create filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{filename}_{timestamp}.{format_type}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if format_type == 'csv':
            evolved_df.to_csv(filepath, index=False)
        elif format_type == 'json':
            evolved_df.to_json(filepath, orient='records')
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
        logger.info(f"Evolved data exported to {filepath}")
        
        return jsonify({
            'success': True,
            'filename': safe_filename,
            'filepath': filepath,
            'download_url': f'/uploads/{safe_filename}'
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /ga/export-evolved: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SECRET DEMO/TEST ENDPOINTS (For Development/Testing)
# ============================================================================

@app.route('/demo/run', methods=['POST'])
def run_demo():
    """
    Run a demo script for evolutionary algorithms.

    Request body:
    {
        "algorithm": "ga|pso|de|es",
        "demo_type": "demo|test|quick",
        "secret_key": "fastmig2024"  // Required for access
    }

    Returns: Demo output and results
    """
    import subprocess
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr

    try:
        data = request.get_json() or {}
        secret_key = data.get('secret_key', '')

        # Validate secret key
        if secret_key != 'fastmig2024':
            return jsonify({'error': 'Unauthorized access'}), 403

        algorithm = data.get('algorithm', 'ga').lower()
        demo_type = data.get('demo_type', 'quick').lower()

        valid_algorithms = ['ga', 'pso', 'de', 'es']
        if algorithm not in valid_algorithms:
            return jsonify({
                'error': f"Invalid algorithm: {algorithm}",
                'valid_algorithms': valid_algorithms
            }), 400

        # Determine which script to run
        if demo_type == 'demo':
            script_name = f"{algorithm}_demo.py"
        elif demo_type == 'test':
            script_name = f"test_{algorithm}_system.py"
        else:
            # Quick mode - run inline demo
            script_name = None

        output_lines = []
        results = {}

        if script_name:
            # Run the script as subprocess
            script_path = os.path.join(os.path.dirname(__file__), script_name)

            if not os.path.exists(script_path):
                return jsonify({'error': f"Script not found: {script_name}"}), 404

            logger.info(f"🚀 Running {demo_type} for {algorithm.upper()}: {script_path}")

            try:
                result = subprocess.run(
                    ['python', script_path],
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minute timeout
                    cwd=os.path.dirname(__file__)
                )

                output_lines = result.stdout.split('\n') if result.stdout else []
                error_lines = result.stderr.split('\n') if result.stderr else []

                results = {
                    'return_code': result.returncode,
                    'success': result.returncode == 0,
                    'output': output_lines,
                    'errors': error_lines
                }

            except subprocess.TimeoutExpired:
                return jsonify({
                    'error': 'Demo timed out after 120 seconds',
                    'algorithm': algorithm.upper(),
                    'demo_type': demo_type
                }), 408

        else:
            # Quick inline demo
            results = _run_quick_demo(algorithm)
            output_lines = results.get('output', [])

        logger.info(f"✅ {algorithm.upper()} {demo_type} completed")

        return jsonify({
            'success': True,
            'algorithm': algorithm.upper(),
            'demo_type': demo_type,
            'script': script_name or 'inline',
            'output': output_lines,
            'results': results,
            'message': f"{algorithm.upper()} {demo_type} completed successfully"
        })

    except Exception as e:
        logger.error(f"Error in /demo/run: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500


def _run_quick_demo(algorithm: str) -> dict:
    """Run a quick inline demo for the specified algorithm"""
    import time

    output = []
    results = {}

    output.append(f"{'='*60}")
    output.append(f"  QUICK {algorithm.upper()} DEMONSTRATION")
    output.append(f"{'='*60}")

    start_time = time.time()

    try:
        if algorithm == 'ga':
            from ga_operators import GAConfig, SelectionMethod, CrossoverMethod, MutationMethod
            from ga_genotype_phenotype import RealValuedMapper
            from ga_engine import GeneticAlgorithmEngine

            # Simple sphere optimization
            def fitness(x):
                import numpy as np
                return -float(np.sum(np.array(x)**2))

            config = GAConfig(
                population_size=20,
                generations=30,
                selection_method=SelectionMethod.TOURNAMENT,
                crossover_method=CrossoverMethod.SINGLE_POINT,
                mutation_method=MutationMethod.GAUSSIAN,
                early_stopping=True,
                early_stopping_generations=5
            )

            mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
            engine = GeneticAlgorithmEngine(config, fitness, mapper)
            result = engine.run()

            output.append(f"\n✓ GA Sphere Optimization:")
            output.append(f"  Best Fitness: {result.best_fitness:.6f}")
            output.append(f"  Generations: {result.total_generations}")
            output.append(f"  Converged: {result.convergence_achieved}")

            results = {
                'best_fitness': result.best_fitness,
                'generations': result.total_generations,
                'converged': result.convergence_achieved
            }

        elif algorithm == 'pso':
            from pso_operators import PSOConfig, PSOTopology, PSOVariant
            from pso_engine import optimize_value_pso

            def fitness(x):
                return -((x - 5) ** 2)

            config = PSOConfig(
                swarm_size=20,
                iterations=40,
                topology=PSOTopology.GBEST,
                variant=PSOVariant.STANDARD,
                early_stopping=True,
                patience=8
            )

            result = optimize_value_pso(
                fitness_function=fitness,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )

            output.append(f"\n✓ PSO Optimization (target x=5):")
            output.append(f"  Best Position: {result.best_position[0]:.6f}")
            output.append(f"  Best Fitness: {result.best_fitness:.6f}")
            output.append(f"  Iterations: {result.total_iterations}")
            output.append(f"  Converged: {result.converged}")

            results = {
                'best_position': float(result.best_position[0]),
                'best_fitness': float(result.best_fitness),
                'iterations': result.total_iterations,
                'converged': result.converged
            }

        elif algorithm == 'de':
            from de_operators import DEConfig, DEMutationStrategy, DECrossoverType
            from de_engine import optimize_value_de

            def fitness(x):
                return -((x - 3) ** 2)

            config = DEConfig(
                pop_size=20,
                max_iter=40,
                mutation_strategy=DEMutationStrategy.RAND_1,
                crossover_type=DECrossoverType.BINOMIAL,
                early_stopping=True,
                patience=8
            )

            result = optimize_value_de(
                fitness_function=fitness,
                bounds_min=-5.0,
                bounds_max=10.0,
                config=config
            )

            output.append(f"\n✓ DE Optimization (target x=3):")
            output.append(f"  Best Position: {result.best_position[0]:.6f}")
            output.append(f"  Best Fitness: {result.best_fitness:.6f}")
            output.append(f"  Generations: {result.total_generations}")
            output.append(f"  Converged: {result.converged}")

            results = {
                'best_position': float(result.best_position[0]),
                'best_fitness': float(result.best_fitness),
                'generations': result.total_generations,
                'converged': result.converged
            }

        elif algorithm == 'es':
            from es_operators import ESConfig, ESSelectionType, ESRecombinationType
            from es_engine import optimize_value_es

            def fitness(x):
                return -((x - 7) ** 2)

            config = ESConfig(
                mu=10,
                lambda_=30,
                max_generations=40,
                selection_type=ESSelectionType.COMMA,
                recombination_type=ESRecombinationType.INTERMEDIATE,
                early_stopping=True,
                patience=8
            )

            result = optimize_value_es(
                fitness_function=fitness,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )

            output.append(f"\n✓ ES Optimization (target x=7):")
            output.append(f"  Best Position: {result.best_position[0]:.6f}")
            output.append(f"  Best Fitness: {result.best_fitness:.6f}")
            output.append(f"  Generations: {result.total_generations}")
            output.append(f"  Converged: {result.converged}")

            results = {
                'best_position': float(result.best_position[0]),
                'best_fitness': float(result.best_fitness),
                'generations': result.total_generations,
                'converged': result.converged
            }

    except Exception as e:
        output.append(f"\n✗ Error: {str(e)}")
        results['error'] = str(e)
        results['success'] = False
        return {'output': output, **results}

    elapsed = time.time() - start_time
    output.append(f"\n  Time: {elapsed:.3f}s")
    output.append(f"{'='*60}")

    results['success'] = True
    results['execution_time'] = elapsed
    results['output'] = output

    return results


@app.route('/demo/compare', methods=['POST'])
def compare_algorithms():
    """
    Compare all evolutionary algorithms on the same problem.

    Request body:
    {
        "secret_key": "fastmig2024",
        "problem": "sphere|shifted|rastrigin"
    }

    Returns: Comparison results for all algorithms
    """
    import time
    import numpy as np

    try:
        data = request.get_json() or {}
        secret_key = data.get('secret_key', '')

        if secret_key != 'fastmig2024':
            return jsonify({'error': 'Unauthorized access'}), 403

        problem = data.get('problem', 'sphere').lower()

        # Define fitness functions
        if problem == 'sphere':
            target = 0.0
            def fitness(x):
                return -(x ** 2)
            bounds = (-10.0, 10.0)
        elif problem == 'shifted':
            target = 5.0
            def fitness(x):
                return -((x - 5) ** 2)
            bounds = (0.0, 10.0)
        elif problem == 'rastrigin':
            target = 0.0
            def fitness(x):
                return -(10 + x**2 - 10 * np.cos(2 * np.pi * x))
            bounds = (-5.12, 5.12)
        else:
            return jsonify({'error': f"Unknown problem: {problem}"}), 400

        results = {}
        output = []

        output.append(f"{'='*70}")
        output.append(f"  EVOLUTIONARY ALGORITHMS COMPARISON - {problem.upper()}")
        output.append(f"  Target: x = {target}")
        output.append(f"{'='*70}")

        # Test each algorithm
        algorithms = ['ga', 'pso', 'de', 'es']

        for algo in algorithms:
            try:
                start = time.time()
                result = _run_quick_demo(algo)
                elapsed = time.time() - start

                if result.get('success'):
                    best_pos = result.get('best_position', 0)
                    best_fit = result.get('best_fitness', 0)
                    gens = result.get('generations', result.get('iterations', 0))

                    error = abs(best_pos - target) if best_pos else float('inf')

                    results[algo] = {
                        'best_position': best_pos,
                        'best_fitness': best_fit,
                        'generations': gens,
                        'error': error,
                        'time': elapsed,
                        'success': True
                    }

                    output.append(f"\n  {algo.upper():4} | pos: {best_pos:8.4f} | fit: {best_fit:10.4f} | "
                                f"gens: {gens:3d} | err: {error:.4f} | {elapsed:.3f}s")
                else:
                    results[algo] = {'success': False, 'error': result.get('error', 'Unknown error')}
                    output.append(f"\n  {algo.upper():4} | FAILED: {result.get('error', 'Unknown')}")

            except Exception as e:
                results[algo] = {'success': False, 'error': str(e)}
                output.append(f"\n  {algo.upper():4} | ERROR: {str(e)}")

        # Find best algorithm
        valid_results = {k: v for k, v in results.items() if v.get('success')}
        if valid_results:
            best_algo = min(valid_results.keys(), key=lambda k: valid_results[k]['error'])
            output.append(f"\n\n  🏆 Best Algorithm: {best_algo.upper()}")
            output.append(f"     Error from target: {valid_results[best_algo]['error']:.6f}")

        output.append(f"\n{'='*70}")

        return jsonify({
            'success': True,
            'problem': problem,
            'target': target,
            'bounds': bounds,
            'results': results,
            'best_algorithm': best_algo if valid_results else None,
            'output': output,
            'message': f"Comparison complete. Best: {best_algo.upper() if valid_results else 'None'}"
        })

    except Exception as e:
        logger.error(f"Error in /demo/compare: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/demo/stress-test', methods=['POST'])
def stress_test_algorithms():
    """
    Run stress test on evolutionary algorithms.

    Request body:
    {
        "secret_key": "fastmig2024",
        "algorithm": "ga|pso|de|es|all",
        "iterations": 5
    }

    Returns: Stress test results with timing statistics
    """
    import time
    import numpy as np

    try:
        data = request.get_json() or {}
        secret_key = data.get('secret_key', '')

        if secret_key != 'fastmig2024':
            return jsonify({'error': 'Unauthorized access'}), 403

        algorithm = data.get('algorithm', 'all').lower()
        num_iterations = min(data.get('iterations', 5), 20)  # Cap at 20

        algorithms = [algorithm] if algorithm != 'all' else ['ga', 'pso', 'de', 'es']

        results = {}
        output = []

        output.append(f"{'='*70}")
        output.append(f"  STRESS TEST - {num_iterations} iterations each")
        output.append(f"{'='*70}")

        for algo in algorithms:
            times = []
            successes = 0

            output.append(f"\n  Testing {algo.upper()}...")

            for i in range(num_iterations):
                try:
                    start = time.time()
                    result = _run_quick_demo(algo)
                    elapsed = time.time() - start

                    if result.get('success'):
                        times.append(elapsed)
                        successes += 1

                except Exception as e:
                    output.append(f"    Iteration {i+1} failed: {str(e)}")

            if times:
                results[algo] = {
                    'iterations': num_iterations,
                    'successes': successes,
                    'failures': num_iterations - successes,
                    'avg_time': np.mean(times),
                    'min_time': np.min(times),
                    'max_time': np.max(times),
                    'std_time': np.std(times),
                    'success_rate': successes / num_iterations * 100
                }

                output.append(f"    ✓ {algo.upper()}: {successes}/{num_iterations} success "
                            f"(avg: {np.mean(times):.3f}s, min: {np.min(times):.3f}s, max: {np.max(times):.3f}s)")
            else:
                results[algo] = {'success': False, 'error': 'All iterations failed'}
                output.append(f"    ✗ {algo.upper()}: All iterations failed")

        output.append(f"\n{'='*70}")

        return jsonify({
            'success': True,
            'algorithms_tested': algorithms,
            'iterations_per_algorithm': num_iterations,
            'results': results,
            'output': output,
            'message': f"Stress test completed for {len(algorithms)} algorithm(s)"
        })

    except Exception as e:
        logger.error(f"Error in /demo/stress-test: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/demo/algorithms', methods=['GET'])
def list_demo_algorithms():
    """List available demo algorithms and scripts"""
    import os

    base_path = os.path.dirname(__file__)

    algorithms = {
        'ga': {
            'name': 'Genetic Algorithm',
            'demo_script': 'ga_demo.py',
            'test_script': 'test_ga_system.py',
            'cli_script': 'ga_cli.py',
            'demo_exists': os.path.exists(os.path.join(base_path, 'ga_demo.py')),
            'test_exists': os.path.exists(os.path.join(base_path, 'test_ga_system.py')),
            'cli_exists': os.path.exists(os.path.join(base_path, 'ga_cli.py')),
            'description': 'Evolutionary algorithm using selection, crossover, and mutation'
        },
        'pso': {
            'name': 'Particle Swarm Optimization',
            'demo_script': 'pso_demo.py',
            'test_script': 'test_pso_system.py',
            'cli_script': 'pso_cli.py',
            'demo_exists': os.path.exists(os.path.join(base_path, 'pso_demo.py')),
            'test_exists': os.path.exists(os.path.join(base_path, 'test_pso_system.py')),
            'cli_exists': os.path.exists(os.path.join(base_path, 'pso_cli.py')),
            'description': 'Swarm intelligence using particle velocity and best positions'
        },
        'de': {
            'name': 'Differential Evolution',
            'demo_script': 'de_demo.py',
            'test_script': 'test_de_system.py',
            'cli_script': 'de_cli.py',
            'demo_exists': os.path.exists(os.path.join(base_path, 'de_demo.py')),
            'test_exists': os.path.exists(os.path.join(base_path, 'test_de_system.py')),
            'cli_exists': os.path.exists(os.path.join(base_path, 'de_cli.py')),
            'description': 'Differential mutation and crossover for optimization'
        },
        'es': {
            'name': 'Evolution Strategy',
            'demo_script': 'es_demo.py',
            'test_script': 'test_es_system.py',
            'cli_script': 'es_cli.py',
            'demo_exists': os.path.exists(os.path.join(base_path, 'es_demo.py')),
            'test_exists': os.path.exists(os.path.join(base_path, 'test_es_system.py')),
            'cli_exists': os.path.exists(os.path.join(base_path, 'es_cli.py')),
            'description': 'Self-adaptive mutation with (μ,λ) or (μ+λ) selection'
        }
    }

    return jsonify({
        'success': True,
        'algorithms': algorithms,
        'demo_types': ['quick', 'demo', 'test'],
        'secret_required': True,
        'endpoints': {
            '/demo/run': 'Run a specific demo/test',
            '/demo/compare': 'Compare all algorithms on same problem',
            '/demo/stress-test': 'Run stress tests'
        }
    })


# ============================================================================
# AZURE OPENAI CHAT ENDPOINTS
# ============================================================================

@app.route('/openai/status', methods=['GET'])
def openai_status():
    """
    Check Azure OpenAI configuration status.

    Returns: Configuration status and availability
    """
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')

    is_configured = bool(api_key and endpoint and deployment)

    return jsonify({
        'success': True,
        'available': AZURE_OPENAI_AVAILABLE,
        'configured': is_configured,
        'has_api_key': bool(api_key),
        'has_endpoint': bool(endpoint),
        'has_deployment': bool(deployment),
        'message': 'Azure OpenAI is ready' if (AZURE_OPENAI_AVAILABLE and is_configured)
                   else 'Azure OpenAI requires configuration' if AZURE_OPENAI_AVAILABLE
                   else 'OpenAI package not installed'
    })


@app.route('/openai/chat', methods=['POST'])
def openai_chat():
    """
    Send a chat message to Azure OpenAI with JSON-based communication.

    Request body:
    {
        "message": "What columns have missing values?",
        "include_data_context": true,
        "conversation_history": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ]
    }

    Returns: AI response with structured operations in JSON format
    {
        "success": true,
        "response": "AI message text",
        "operations": [
            {
                "operation": "fill_nulls",
                "column": "age",
                "parameters": {"method": "mean"},
                "description": "Fill missing ages with mean value",
                "confidence": 0.95,
                "reasoning": "Mean is appropriate for numeric data"
            }
        ],
        "analysis": {...},
        "has_data_context": true,
        "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    }
    """
    try:
        logger.info("=== /openai/chat endpoint called (JSON mode) ===")
        logger.info(f"AI_CHAT_AVAILABLE: {AI_CHAT_AVAILABLE}")
        logger.info(f"API Key present: {bool(os.getenv('AZURE_OPENAI_API_KEY'))}")
        logger.info(f"Endpoint present: {bool(os.getenv('AZURE_OPENAI_ENDPOINT'))}")
        logger.info(f"Deployment present: {bool(os.getenv('AZURE_OPENAI_DEPLOYMENT'))}")

        if not AI_CHAT_AVAILABLE:
            logger.error("OpenAI package not available")
            return jsonify({
                'error': 'OpenAI package not installed. Run: pip install openai',
                'configured': False
            }), 400

        # Initialize AI Chat with JSON-based communication
        config = AIChatConfig()
        is_valid, errors = config.validate()

        if not is_valid:
            return jsonify({
                'error': f'Azure OpenAI not configured: {", ".join(errors)}',
                'configured': False
            }), 400

        ai_chat = AIChat(config)
        if not ai_chat.is_available():
            return jsonify({
                'error': 'Failed to initialize AI Chat client',
                'configured': False
            }), 400

        data = request.get_json() or {}
        user_message = data.get('message', '')
        include_context = data.get('include_data_context', True)
        conversation_history = data.get('conversation_history', [])

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Get DataFrame if available
        df = current_data.get('df') if include_context else None

        logger.info(f"Sending chat message (JSON mode): {user_message[:100]}...")

        # Call AI Chat with JSON-based communication
        response: AIResponse = ai_chat.chat(
            user_message=user_message,
            df=df,
            conversation_history=conversation_history,
            include_data_context=include_context
        )

        if not response.success:
            logger.error(f"AI Chat error: {response.error}")
            return jsonify({
                'error': f"AI response failed: {response.error}",
                'type': 'AIError'
            }), 500

        logger.info(f"AI Chat response received ({len(response.message)} chars, {len(response.operations)} operations)")

        # Convert operations to legacy format for backward compatibility
        suggested_actions = []
        for op in response.operations:
            if op.operation != OperationType.NONE and op.operation != OperationType.ANALYZE:
                action = {
                    'type': op.operation.value,
                    'column': op.column,
                    'parameters': op.parameters,
                    'description': op.description,
                    'confidence': op.confidence,
                    'reasoning': op.reasoning
                }
                # Add method parameter for fill_nulls compatibility
                if op.operation == OperationType.FILL_NULLS and 'method' in op.parameters:
                    action['method'] = op.parameters['method']
                suggested_actions.append(action)

        return jsonify({
            'success': True,
            'response': response.message,
            'suggested_actions': suggested_actions,
            'operations': [op.to_dict() for op in response.operations],
            'analysis': response.analysis,
            'has_data_context': include_context and df is not None,
            'usage': response.usage,
            'raw_response': response.raw_response if logger.isEnabledFor(logging.DEBUG) else None
        })

    except Exception as e:
        logger.error(f"Error in /openai/chat: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to get AI response: {str(e)}",
            'type': type(e).__name__
        }), 500


@app.route('/openai/modify-data', methods=['POST'])
def openai_modify_data():
    """
    Execute a natural language data modification command.

    Request body:
    {
        "command": "Fill missing values in age column with the average",
        "preview": false
    }

    Returns: Modified data with operation details
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400

        if not AZURE_OPENAI_AVAILABLE:
            return jsonify({'error': 'OpenAI package not installed'}), 400

        client = get_azure_openai_client()
        if not client:
            return jsonify({'error': 'Azure OpenAI not configured'}), 400

        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        if not deployment:
            return jsonify({'error': 'AZURE_OPENAI_DEPLOYMENT not set'}), 400

        data = request.get_json() or {}
        command = data.get('command', '')
        preview = data.get('preview', False)

        if not command:
            return jsonify({'error': 'Command is required'}), 400

        df = current_data['df']
        data_context = build_data_context(df)

        # Ask AI to parse the command into a structured operation
        system_prompt = f"""You are a data operation parser. Given a natural language command,
extract the specific operation to perform on the data.

Current Dataset Context:
{data_context}

Respond with ONLY a JSON object (no markdown, no explanation) in this format:
{{
    "operation": "fill_nulls|remove_nulls|remove_duplicates|remove_column|rename_column|change_case|find_replace|filter_rows|trim_whitespace",
    "column": "column_name or null",
    "parameters": {{
        "method": "mean|median|mode|constant (for fill_nulls)",
        "value": "value for constant fill or find_replace",
        "new_name": "for rename_column",
        "case_type": "upper|lower|title (for change_case)",
        "find_value": "for find_replace",
        "replace_value": "for find_replace",
        "operator": "==|!=|>|<|>=|<= (for filter_rows)",
        "filter_value": "for filter_rows"
    }},
    "description": "Brief description of what will happen"
}}

If the command cannot be parsed into an operation, respond with:
{{"operation": "unknown", "description": "explanation of why"}}
"""

        logger.info(f"Parsing command: {command}")

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ],
            max_completion_tokens=500
        )

        ai_response = response.choices[0].message.content.strip()

        # Parse AI response as JSON
        try:
            # Remove markdown code blocks if present
            if ai_response.startswith('```'):
                ai_response = ai_response.split('```')[1]
                if ai_response.startswith('json'):
                    ai_response = ai_response[4:]
            operation = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {ai_response}")
            return jsonify({
                'error': 'Failed to parse command',
                'ai_response': ai_response,
                'parse_error': str(e)
            }), 400

        op_type = operation.get('operation', 'unknown')

        if op_type == 'unknown':
            return jsonify({
                'success': False,
                'operation': op_type,
                'description': operation.get('description', 'Could not understand the command'),
                'message': 'Command not recognized. Try being more specific.'
            })

        # Execute the operation
        df_modified = df.copy()
        report = {}

        try:
            column = operation.get('column')
            params = operation.get('parameters', {})

            if op_type == 'fill_nulls':
                method = params.get('method', 'mean')
                value = params.get('value')
                df_modified, report = etl_ops.fill_null_values(df_modified, column, method, value)

            elif op_type == 'remove_nulls':
                df_modified, report = etl_ops.remove_null_rows(df_modified, columns=[column] if column else None)

            elif op_type == 'remove_duplicates':
                df_modified, report = etl_ops.remove_duplicate_rows(df_modified, columns=[column] if column else None)

            elif op_type == 'remove_column':
                df_modified, report = etl_ops.remove_column(df_modified, column)

            elif op_type == 'rename_column':
                new_name = params.get('new_name')
                if new_name:
                    df_modified, report = etl_ops.rename_column(df_modified, column, new_name)
                else:
                    return jsonify({'error': 'New column name not specified'}), 400

            elif op_type == 'change_case':
                case_type = params.get('case_type', 'lower')
                df_modified, report = etl_ops.change_case(df_modified, column, case_type)

            elif op_type == 'find_replace':
                find_value = params.get('find_value', '')
                replace_value = params.get('replace_value', '')
                df_modified, report = etl_ops.find_replace(df_modified, column, find_value, replace_value)

            elif op_type == 'filter_rows':
                operator = params.get('operator', '==')
                filter_value = params.get('filter_value')
                df_modified, report = etl_ops.filter_rows(df_modified, column, operator, filter_value)

            elif op_type == 'trim_whitespace':
                df_modified, report = etl_ops.trim_whitespace(df_modified, columns=[column] if column else None)

            else:
                return jsonify({
                    'error': f"Unknown operation: {op_type}",
                    'supported_operations': ['fill_nulls', 'remove_nulls', 'remove_duplicates',
                                            'remove_column', 'rename_column', 'change_case',
                                            'find_replace', 'filter_rows', 'trim_whitespace']
                }), 400

        except Exception as e:
            logger.error(f"Error executing operation {op_type}: {str(e)}")
            return jsonify({
                'error': f"Failed to execute operation: {str(e)}",
                'operation': op_type
            }), 500

        # Save the modified data unless preview mode
        if not preview:
            current_data['df_original'] = df
            current_data['df'] = df_modified

        # Convert to list format for response
        data_list = _dataframe_to_list(df_modified, max_rows=100)

        logger.info(f"Operation {op_type} completed successfully")

        return jsonify({
            'success': True,
            'operation': op_type,
            'description': operation.get('description', ''),
            'column': column,
            'parameters': params,
            'report': report,
            'preview': preview,
            'data': data_list,
            'columns': df_modified.columns.tolist(),
            'shape': df_modified.shape,
            'message': f"Successfully executed: {operation.get('description', op_type)}"
        })

    except Exception as e:
        logger.error(f"Error in /openai/modify-data: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to modify data: {str(e)}",
            'type': type(e).__name__
        }), 500


@app.route('/openai/analyze', methods=['POST'])
def openai_analyze():
    """
    Get AI analysis of the current dataset.

    Request body:
    {
        "analysis_type": "quality_report|summary|recommendations"
    }

    Returns: AI-generated analysis
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400

        if not AZURE_OPENAI_AVAILABLE:
            return jsonify({'error': 'OpenAI package not installed'}), 400

        client = get_azure_openai_client()
        if not client:
            return jsonify({'error': 'Azure OpenAI not configured'}), 400

        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        if not deployment:
            return jsonify({'error': 'AZURE_OPENAI_DEPLOYMENT not set'}), 400

        data = request.get_json() or {}
        analysis_type = data.get('analysis_type', 'summary')

        df = current_data['df']
        data_context = build_data_context(df)

        # Build prompt based on analysis type
        if analysis_type == 'quality_report':
            prompt = f"""Analyze this dataset for data quality issues.

{data_context}

Provide a structured quality report including:
1. Overall data quality score (0-100)
2. List of issues found (missing values, duplicates, inconsistencies)
3. Priority recommendations for cleaning
4. Columns that need attention

Be concise and actionable."""

        elif analysis_type == 'recommendations':
            prompt = f"""Based on this dataset, provide cleaning and transformation recommendations.

{data_context}

Provide:
1. Top 5 recommended actions in priority order
2. For each action, explain why it's needed
3. Suggest the best method/approach for each

Be specific about column names and methods."""

        else:  # summary
            prompt = f"""Provide a brief summary of this dataset.

{data_context}

Include:
1. What this data appears to represent
2. Key characteristics (size, completeness, data types)
3. Notable patterns or issues
4. Suggested use cases

Keep it concise (3-4 paragraphs max)."""

        logger.info(f"Generating {analysis_type} analysis...")

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a data analyst expert. Provide clear, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1500
        )

        analysis = response.choices[0].message.content

        logger.info(f"Analysis generated ({len(analysis)} chars)")

        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'analysis': analysis,
            'dataset_info': {
                'rows': df.shape[0],
                'columns': df.shape[1],
                'null_count': int(df.isnull().sum().sum()),
                'columns_list': df.columns.tolist()
            },
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        })

    except Exception as e:
        logger.error(f"Error in /openai/analyze: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to analyze data: {str(e)}",
            'type': type(e).__name__
        }), 500


# Store pending modifications for preview/apply workflow
pending_modifications = {
    'modifications': [],
    'preview_data': None,
    'original_data': None
}

@app.route('/openai/chat-modify', methods=['POST'])
def openai_chat_modify():
    """
    AI Chat endpoint focused on fixing detected error_cells.
    Returns a PREVIEW of changes - user must confirm to apply.

    Request body:
    {
        "message": "fix my data" or "please fix the errors",
        "auto_execute": false  // Preview mode by default
    }

    Returns: Preview of proposed fixes based on error_cells
    """
    global pending_modifications
    try:
        logger.info("=== /openai/chat-modify endpoint called ===")

        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400

        df = current_data['df'].copy()
        error_cells = current_data.get('error_cells', [])

        data = request.get_json() or {}
        user_message = data.get('message', '').lower()
        auto_execute = data.get('auto_execute', False)  # Preview by default

        # Check if this is a "fix" request
        is_fix_request = any(word in user_message for word in ['fix', 'repair', 'clean', 'correct', 'fill', 'replace'])

        if not is_fix_request or not error_cells:
            # If no fix request or no errors, return info about current errors
            if not error_cells:
                return jsonify({
                    'success': True,
                    'message': 'No error cells detected in your data. Your data looks clean!',
                    'modifications': [],
                    'preview_data': None,
                    'error_cells_count': 0,
                    'needs_confirmation': False
                })
            else:
                # Summarize errors
                error_summary = {}
                for err in error_cells:
                    col_idx = err.get('col', 0)
                    col_name = df.columns[col_idx] if col_idx < len(df.columns) else f'Column {col_idx}'
                    if col_name not in error_summary:
                        error_summary[col_name] = {'count': 0, 'types': set(), 'rows': []}
                    error_summary[col_name]['count'] += 1
                    error_summary[col_name]['types'].add(err.get('type', 'unknown'))
                    if len(error_summary[col_name]['rows']) < 5:
                        error_summary[col_name]['rows'].append(err.get('row', 0))

                summary_text = f"Found {len(error_cells)} error cells:\n"
                for col, info in error_summary.items():
                    summary_text += f"\n• **{col}**: {info['count']} issues (types: {', '.join(info['types'])})"
                    summary_text += f"\n  Rows: {info['rows'][:5]}{'...' if info['count'] > 5 else ''}"

                summary_text += "\n\nType 'fix my data' to preview and apply corrections."

                return jsonify({
                    'success': True,
                    'message': summary_text,
                    'modifications': [],
                    'preview_data': None,
                    'error_cells_count': len(error_cells),
                    'needs_confirmation': False
                })

        # Generate fixes for each error cell
        logger.info(f"Generating fixes for {len(error_cells)} error cells")
        logger.info(f"Error cells to fix: {error_cells}")
        modifications = []
        preview_df = df.copy()

        for err in error_cells:
            row_idx = err.get('row', 0) - 1  # Convert to 0-indexed (error_cells are 1-indexed)
            col_idx = err.get('col', 0)
            # Handle both 'issues' array and 'type' string formats
            issues = err.get('issues', [])
            error_type = issues[0] if issues else err.get('type', 'unknown')

            if col_idx >= len(df.columns) or row_idx < 0 or row_idx >= len(df):
                logger.warning(f"Skipping invalid cell: row={row_idx}, col={col_idx}")
                continue

            col_name = df.columns[col_idx]
            col_data = df[col_name]
            current_value = df.iloc[row_idx, col_idx]

            logger.info(f"Processing error: row={row_idx+1}, col={col_name}, type={error_type}, value={current_value}")

            # Calculate fix value based on column type and valid values
            new_value = None
            reason = ""

            # Get valid (non-error) values for this column
            valid_mask = pd.notna(col_data) & (col_data != '') & (col_data != 'null')

            # Try to determine if column should be numeric
            is_numeric_col = False
            try:
                valid_values = col_data[valid_mask]
                if len(valid_values) > 0:
                    # Check if most valid values are numeric
                    numeric_count = sum(1 for v in valid_values if str(v).replace('.','').replace('-','').isdigit())
                    is_numeric_col = numeric_count / len(valid_values) > 0.5
            except:
                pass

            # Handle missing_value, null, empty, missing error types
            if error_type in ['null', 'empty', 'missing', 'missing_value'] or pd.isna(current_value) or current_value in ['', None, 'null', 'NaN']:
                logger.info(f"  -> Fixing missing value in {col_name}")
                # Fill missing values
                if is_numeric_col:
                    try:
                        # Convert valid values to numeric and calculate mean
                        numeric_vals = pd.to_numeric(col_data[valid_mask], errors='coerce').dropna()
                        if len(numeric_vals) > 0:
                            new_value = round(float(numeric_vals.mean()), 2)
                            reason = f"Filled with column mean ({new_value})"
                    except Exception as e:
                        logger.warning(f"Could not calculate mean for {col_name}: {e}")

                if new_value is None:
                    # Use mode (most common value) for non-numeric
                    try:
                        valid_vals = col_data[valid_mask]
                        if len(valid_vals) > 0:
                            mode_val = valid_vals.mode()
                            if len(mode_val) > 0:
                                new_value = str(mode_val.iloc[0])
                                reason = f"Filled with most common value"
                    except:
                        new_value = "N/A"
                        reason = "Filled with placeholder"

            # Handle non_numeric, mixed_content, type_mismatch, invalid types
            elif error_type in ['type_mismatch', 'invalid', 'non_numeric', 'mixed_content']:
                logger.info(f"  -> Fixing type mismatch/invalid value in {col_name}: {current_value}")
                # Try to convert or replace invalid values
                if is_numeric_col:
                    # Try to extract number from value
                    try:
                        import re
                        numbers = re.findall(r'[\d.]+', str(current_value))
                        if numbers:
                            new_value = float(numbers[0])
                            reason = f"Extracted numeric value from '{current_value}'"
                        else:
                            # Use column mean
                            numeric_vals = pd.to_numeric(col_data[valid_mask], errors='coerce').dropna()
                            if len(numeric_vals) > 0:
                                new_value = round(float(numeric_vals.mean()), 2)
                                reason = f"Replaced invalid value with column mean"
                    except:
                        new_value = 0
                        reason = "Reset invalid numeric value"
                else:
                    # For string columns with type issues, try to clean the value
                    try:
                        import re
                        # Remove non-alpha characters for string columns
                        cleaned = re.sub(r'[^a-zA-Z\s]', '', str(current_value)).strip()
                        if cleaned:
                            new_value = cleaned
                            reason = f"Cleaned string value (removed non-alpha chars)"
                        else:
                            valid_vals = col_data[valid_mask]
                            if len(valid_vals) > 0:
                                mode_val = valid_vals.mode()
                                if len(mode_val) > 0:
                                    new_value = str(mode_val.iloc[0])
                                    reason = f"Replaced with most common value"
                    except:
                        new_value = str(current_value).strip() if current_value else "N/A"
                        reason = "Cleaned string value"

            # Handle suspicious_numeric_in_string
            elif error_type in ['suspicious_numeric_in_string']:
                logger.info(f"  -> Fixing suspicious numeric in string column {col_name}: {current_value}")
                # This is a string column with a numeric value - might be a data entry error
                try:
                    # Get valid string values (excluding numeric-looking ones)
                    valid_string_vals = []
                    for i, v in enumerate(col_data):
                        if pd.notna(v) and v != '' and v != 'null':
                            v_str = str(v).strip()
                            # Only include values that are NOT purely numeric
                            if not v_str.replace('.', '').replace('-', '').replace(',', '').isdigit():
                                valid_string_vals.append(v_str)

                    logger.info(f"  -> Valid string values for mode: {valid_string_vals[:5]}...")

                    if valid_string_vals:
                        # Use pandas Series mode to find most common string value
                        mode_series = pd.Series(valid_string_vals).mode()
                        if len(mode_series) > 0:
                            new_value = str(mode_series.iloc[0])
                            reason = f"Replaced numeric '{current_value}' with most common string value '{new_value}'"
                        else:
                            new_value = valid_string_vals[0]  # Use first valid string
                            reason = f"Replaced numeric '{current_value}' with valid string value"
                    else:
                        # No valid string values found, mark as needing manual review
                        new_value = f"[{current_value}]"
                        reason = "Marked for manual review (no valid string values found)"
                except Exception as e:
                    logger.warning(f"Error fixing suspicious_numeric_in_string: {e}")
                    new_value = str(current_value)  # Keep as-is if can't fix
                    reason = "Kept original value (fix failed)"

            # Default handling for unknown types
            else:
                logger.info(f"  -> Unknown error type '{error_type}', attempting generic fix")
                if pd.isna(current_value) or current_value in ['', None]:
                    try:
                        valid_vals = col_data[valid_mask]
                        if len(valid_vals) > 0:
                            mode_val = valid_vals.mode()
                            if len(mode_val) > 0:
                                new_value = mode_val.iloc[0]
                                reason = f"Filled with most common value"
                    except:
                        new_value = "N/A"
                        reason = "Filled with placeholder"

            if new_value is not None:
                logger.info(f"  -> Fix applied: '{current_value}' -> '{new_value}' ({reason})")
                # Apply to preview
                try:
                    preview_df.iloc[row_idx, col_idx] = new_value
                except Exception as e:
                    logger.error(f"Error setting preview value: {e}")
                    continue

                modifications.append({
                    'row': row_idx + 1,  # 1-indexed for frontend display (matches data row numbers)
                    'col': col_idx,
                    'column': col_name,
                    'col_name': col_name,  # Add col_name for frontend compatibility
                    'old_value': str(current_value) if current_value is not None else 'null',
                    'original_value': str(current_value) if current_value is not None else 'null',  # Alternative key
                    'new_value': new_value,
                    'evolved_value': new_value,  # Alternative key for frontend
                    'reason': reason,
                    'error_type': error_type
                })

        # Store pending modifications for apply step
        pending_modifications = {
            'modifications': modifications,
            'preview_data': preview_df,
            'original_data': df
        }

        # Generate preview data (first 100 rows with changes highlighted)
        preview_list = _dataframe_to_list(preview_df, max_rows=100)

        # Build response message
        if modifications:
            msg = f"**Preview: {len(modifications)} cells will be modified**\n\n"
            # Group by column
            col_mods = {}
            for mod in modifications:
                col = mod['column']
                if col not in col_mods:
                    col_mods[col] = []
                col_mods[col].append(mod)

            for col, mods in col_mods.items():
                msg += f"**{col}** ({len(mods)} changes):\n"
                for m in mods[:3]:  # Show first 3
                    msg += f"  • Row {m['row']}: `{m['old_value']}` → `{m['new_value']}` ({m['reason']})\n"
                if len(mods) > 3:
                    msg += f"  ... and {len(mods) - 3} more\n"

            msg += "\n**Click 'Apply Changes' to confirm, or 'Cancel' to discard.**"
        else:
            msg = "No fixes could be generated for the detected errors."

        # Auto-execute if requested
        if auto_execute and modifications:
            # Add "Modified_by_AI" column to track which rows were modified
            # Note: mod['row'] is 1-indexed, so we need to convert back to 0-indexed for df.index
            modified_rows_0indexed = set(mod['row'] - 1 for mod in modifications)
            preview_df['Modified_by_AI'] = preview_df.index.map(
                lambda idx: 'Yes' if idx in modified_rows_0indexed else 'No'
            )
            logger.info(f"Added Modified_by_AI column. Modified rows (0-indexed): {sorted(modified_rows_0indexed)}")

            current_data['df'] = preview_df

            # Track modifications (row is already 1-indexed in modifications)
            for mod in modifications:
                track_ai_modification(
                    row_index=mod['row'] - 1,  # Convert back to 0-indexed for internal tracking
                    column=mod['column'],
                    old_value=mod['old_value'],
                    new_value=mod['new_value'],
                    operation='ai_fix'
                )

            # Re-analyze for remaining errors using DataQualityAnalyzer
            analyzer = DataQualityAnalyzer()
            updated_quality_report = analyzer.analyze(preview_df)
            current_data['error_cells'] = updated_quality_report.get('error_cells', [])
            logger.info(f"After AI fix: {len(current_data['error_cells'])} error cells remaining")
            msg = f"**Applied {len(modifications)} fixes to your data.**"

        logger.info(f"Returning response: {len(modifications)} modifications, auto_execute={auto_execute}")

        return jsonify({
            'success': True,
            'message': msg,
            'modifications': modifications,
            'applied_modifications': modifications if auto_execute else [],  # For frontend compatibility
            'preview_data': preview_list if not auto_execute else None,
            'data': _dataframe_to_list(current_data['df'], max_rows=100) if auto_execute else None,
            'columns': current_data['df'].columns.tolist(),
            'shape': list(current_data['df'].shape),
            'error_cells': current_data.get('error_cells', []),  # Updated error cells after fix
            'error_cells_count': len(current_data.get('error_cells', [])),
            'fixes_count': len(modifications),
            'needs_confirmation': not auto_execute and len(modifications) > 0,
            'modifications_applied': auto_execute and len(modifications) > 0,
            'total_cells_modified': len(modifications) if auto_execute else 0,
            'ai_modifications': get_ai_modifications(),
            'ai_modified_cells': modifications if auto_execute else []  # For data grid highlighting
        })

    except Exception as e:
        logger.error(f"Error in /openai/chat-modify: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Failed to process request: {str(e)}",
            'type': type(e).__name__
        }), 500


@app.route('/openai/apply-modifications', methods=['POST'])
def apply_pending_modifications():
    """Apply the pending modifications from preview"""
    global pending_modifications
    try:
        if not pending_modifications.get('modifications'):
            return jsonify({'error': 'No pending modifications to apply'}), 400

        modifications = pending_modifications['modifications']
        preview_df = pending_modifications['preview_data']

        if preview_df is None:
            return jsonify({'error': 'Preview data not found'}), 400

        # Apply the preview data
        current_data['df'] = preview_df.copy()

        # Track all modifications
        for mod in modifications:
            track_ai_modification(
                row_index=mod['row'],
                column=mod['column'],
                old_value=mod['old_value'],
                new_value=mod['new_value'],
                operation='ai_fix'
            )

        # Re-analyze for remaining errors
        current_data['error_cells'] = _analyze_error_cells(preview_df)

        # Clear pending
        pending_modifications = {'modifications': [], 'preview_data': None, 'original_data': None}

        return jsonify({
            'success': True,
            'message': f'Applied {len(modifications)} modifications',
            'total_cells_modified': len(modifications),
            'data': _dataframe_to_list(current_data['df'], max_rows=100),
            'columns': current_data['df'].columns.tolist(),
            'error_cells': current_data.get('error_cells', []),
            'ai_modifications': get_ai_modifications()
        })

    except Exception as e:
        logger.error(f"Error applying modifications: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/openai/cancel-modifications', methods=['POST'])
def cancel_pending_modifications():
    """Cancel pending modifications"""
    global pending_modifications
    pending_modifications = {'modifications': [], 'preview_data': None, 'original_data': None}
    return jsonify({'success': True, 'message': 'Pending modifications cancelled'})


@app.route('/openai/modifications', methods=['GET'])
def get_modifications():
    """Get all AI modifications tracked in the current session"""
    return jsonify({
        'success': True,
        'modifications': get_ai_modifications()
    })


@app.route('/openai/modifications/clear', methods=['POST'])
def clear_modifications():
    """Clear current AI modification tracking"""
    clear_ai_modifications()
    return jsonify({
        'success': True,
        'message': 'AI modifications cleared'
    })


def record_action(action_type, **params):
    """Helper function to record an action"""
    if is_recording:
        recorded_actions.append({
            'action_type': action_type,
            'params': params
        })

@app.errorhandler(413)
def too_large(e):
    logger.warning("File upload rejected: File too large")
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error. Please check the server logs.'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'An unexpected error occurred',
        'message': str(e),
        'type': type(e).__name__
    }), 500

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Starting FastMig Flask Backend Server...")
    logger.info("="*60)
    logger.info("Server will be available at http://localhost:5000")
    logger.info("")
    logger.info("=== Core Endpoints ===")
    logger.info("  GET  /health             - Health check")
    logger.info("  POST /upload             - Upload a file")
    logger.info("  POST /load               - Load a file from server path (legacy)")
    logger.info("  POST /process            - Process data (convert column)")
    logger.info("  POST /export             - Export processed data")
    logger.info("  GET  /columns            - Get column information")
    logger.info("  GET  /status             - Get application status")
    logger.info("  POST /config/apply       - Apply configurations")
    logger.info("")
    logger.info("=== ETL Operations ===")
    logger.info("  POST /etl/remove-nulls       - Remove rows with null values")
    logger.info("  POST /etl/remove-duplicates  - Remove duplicate rows")
    logger.info("  POST /etl/find-replace       - Find and replace values")
    logger.info("  POST /etl/fill-nulls         - Fill null values (forward/backward/mean/median/mode/constant)")
    logger.info("  POST /etl/rename-column      - Rename a column")
    logger.info("  POST /etl/remove-column      - Remove a column")
    logger.info("  POST /etl/filter-rows        - Filter rows by condition")
    logger.info("  POST /etl/trim-whitespace    - Trim whitespace from columns")
    logger.info("  POST /etl/change-case        - Change text case (upper/lower/title/capitalize)")
    logger.info("  POST /etl/sort-data          - Sort data by columns")
    logger.info("")
    logger.info("=== Machine Readable Transform (Encoding) ===")
    logger.info("  POST /transform/label-encode         - Label encode categorical columns")
    logger.info("  POST /transform/one-hot-encode       - One-hot encode categorical columns")
    logger.info("  POST /transform/reverse-label-encode - Reverse label encoding")
    logger.info("")
    logger.info("=== Step Recording (Record & Replay Transformations) ===")
    logger.info("  POST /steps/start        - Start recording transformation steps")
    logger.info("  POST /steps/stop         - Stop recording steps")
    logger.info("  GET  /steps/get          - Get all recorded steps")
    logger.info("  POST /steps/clear        - Clear recorded steps")
    logger.info("  POST /steps/save         - Save steps to file")
    logger.info("  POST /steps/load         - Load steps from file")
    logger.info("  POST /steps/replay       - Replay steps on data")
    logger.info("")
    logger.info("=== Legacy Recording Endpoints (Backward Compatibility) ===")
    logger.info("  POST /recording/start    - Start recording (legacy)")
    logger.info("  POST /recording/stop     - Stop recording (legacy)")
    logger.info("  POST /recording/save     - Save recording (legacy)")
    logger.info("  POST /recording/load     - Load and run recording (legacy)")
    logger.info("")
    logger.info("=== Data Fitness & Evolutionary Cleaning ===")
    logger.info("  POST /fitness/evaluate   - Evaluate data fitness/health")
    logger.info("  GET  /fitness/record/<index> - Get fitness for specific record")
    logger.info("  POST /clean/evolutionary - Clean data using evolutionary algorithms")
    logger.info("  POST /clean/compare      - Compare all cleaning methods")
    logger.info("  POST /data/restore       - Restore original data")
    logger.info("")
    logger.info("=== Cell-Level Evolutionary Cleaning (NEW) ===")
    logger.info("  POST /clean/evolve-cells         - Evolve error cells using GA/PSO/DE/ES/Hybrid")
    logger.info("  POST /clean/evolve-cells/compare - Compare all evolution methods on error cells")
    logger.info("  POST /clean/evolve-cells/preview - Preview cell evolution without applying")
    logger.info("  Algorithms:")
    logger.info("    GA  - Crossover & mutation from healthy cell populations")
    logger.info("    PSO - Velocity-based particle movement towards healthy values")
    logger.info("    DE  - Differential evolution with vector differences")
    logger.info("    ES  - Evolution strategy with self-adaptive mutation")
    logger.info("    Hybrid - PSO for numeric, GA for categorical columns")
    logger.info("")
    logger.info("=== Genetic Algorithm (GA) Evolution ===")
    logger.info("  POST /ga/analyze-population  - Analyze population fitness distribution")
    logger.info("  POST /ga/select-populations  - Select healthy/unhealthy populations")
    logger.info("  POST /ga/run-evolution       - Run GA evolution with custom parameters")
    logger.info("  POST /ga/quick-evolve        - Quick evolution (one-call evolution)")
    logger.info("  POST /ga/export-evolved      - Export evolved/cleaned data")
    logger.info("")
    logger.info("  Methods: Tournament/Roulette/Rank-based Selection")
    logger.info("  Crossover: Single-point/Two-point/Uniform/Arithmetic")
    logger.info("  Mutation: Gaussian/Uniform/Adaptive")
    logger.info("="*60)
    logger.info("")
    
    app.run(host='0.0.0.0', port=5000, debug=True)