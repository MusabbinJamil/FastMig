from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os
import logging
from functions import read_file, convert_column, export_data, apply_transformations, map_columns
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
recorded_actions = []
is_recording = False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'FastMig backend is running'})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file and return its data"""
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
        
        # Convert DataFrame to list of lists for JSON response
        data_list = []
        # Add headers as first row
        data_list.append(df.columns.tolist())
        # Add data rows (limit to first 100 rows for performance)
        for _, row in df.head(100).iterrows():
            # Handle NaN values and special types
            row_data = []
            for val in row:
                if pd.isna(val):
                    row_data.append(None)
                elif isinstance(val, pd.Timestamp):
                    row_data.append(val.isoformat())
                else:
                    row_data.append(val)
            data_list.append(row_data)
        
        app.logger.info(f"Successfully processed file: {filename} ({df.shape[0]} rows, {df.shape[1]} columns)")
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'filename': filename,
            'message': f"Successfully uploaded {filename}"
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
    """Load a file and return its data (legacy endpoint for file path)"""
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
        
        # Convert DataFrame to list of lists for JSON response
        data_list = []
        # Add headers as first row
        data_list.append(df.columns.tolist())
        # Add data rows (limit to first 100 rows for performance)
        for _, row in df.head(100).iterrows():
            data_list.append(row.tolist())
        
        return jsonify({
            'success': True,
            'data': data_list,
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
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
        'is_recording': is_recording,
        'recorded_actions_count': len(recorded_actions),
        'has_data': 'df' in current_data,
        'current_file': current_data.get('file_path', None),
        'data_shape': current_data['df'].shape if 'df' in current_data else None
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
    logger.info("Endpoints available:")
    logger.info("  GET  /health             - Health check")
    logger.info("  POST /upload             - Upload a file (recommended)")
    logger.info("  POST /load               - Load a file from server path (legacy)")
    logger.info("  POST /process            - Process data")
    logger.info("  POST /export             - Export processed data")
    logger.info("  GET  /columns            - Get column information")
    logger.info("  GET  /status             - Get application status")
    logger.info("  POST /recording/start    - Start recording actions")
    logger.info("  POST /recording/stop     - Stop recording actions")
    logger.info("  POST /recording/save     - Save recording")
    logger.info("  POST /recording/load     - Load and run recording")
    logger.info("="*60)
    logger.info("")
    
    app.run(host='0.0.0.0', port=5000, debug=True)