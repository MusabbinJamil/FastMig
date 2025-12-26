from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os
import logging
from typing import List
from collections import deque
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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _dataframe_to_list(df: pd.DataFrame, max_rows: int = 100) -> List[List]:
    """Convert DataFrame to list format for JSON response"""
    data_list = []
    # Add headers as first row
    data_list.append(df.columns.tolist())
    # Add data rows (limited to max_rows for performance)
    for _, row in df.head(max_rows).iterrows():
        row_data = []
        for val in row:
            if pd.isna(val):
                row_data.append(None)
            elif isinstance(val, pd.Timestamp):
                row_data.append(val.isoformat())
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
    Clean data using evolutionary algorithms
    
    Request body:
    {
        "method": "ga|pso|de|es|hybrid",
        "save_result": true/false,
        "track_modifications": true/false,
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
        
        # Validate method
        valid_methods = ['ga', 'pso', 'de', 'es', 'hybrid']
        if method not in valid_methods:
            return jsonify({
                'error': f"Invalid method: {method}",
                'valid_methods': valid_methods
            }), 400
        
        df = current_data['df'].copy()
        
        logger.info(f"Starting evolutionary cleaning with method: {method.upper()}")
        
        # Clean data
        cleaned_df, report = clean_data_evolutionary(
            df, 
            method=method, 
            track_modifications=track_modifications,
            **parameters
        )
        
        # Optionally save the cleaned data
        if save_result:
            current_data['df'] = cleaned_df
            current_data['df_original'] = df  # Keep backup
        
        # Convert cleaned data to list format (first 100 rows)
        data_list = []
        data_list.append(cleaned_df.columns.tolist())
        for _, row in cleaned_df.head(100).iterrows():
            row_data = []
            for val in row:
                if pd.isna(val):
                    row_data.append(None)
                elif isinstance(val, pd.Timestamp):
                    row_data.append(val.isoformat())
                else:
                    row_data.append(val)
            data_list.append(row_data)
        
        logger.info(f"Cleaning complete. Fitness improvement: {report['improvement']['fitness_increase']:.2f}%")
        
        return jsonify({
            'success': True,
            'method': method.upper(),
            'report': report,
            'data': data_list,
            'columns': cleaned_df.columns.tolist(),
            'shape': cleaned_df.shape,
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