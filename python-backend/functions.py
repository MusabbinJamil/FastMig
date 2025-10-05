import pandas as pd
import json
import warnings
import logging
import chardet
import io
from pathlib import Path
from typing import Union, BinaryIO, Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress pandas warnings for datetime parsing
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')


class UniversalDataLoader:
    """
    A robust data loader that can handle ANY text-based data format.
    Supports: CSV, TSV, Excel (xls, xlsx), JSON, XML, TXT, and various delimiters.
    """
    
    def __init__(self):
        self.supported_extensions = {
            '.csv', '.tsv', '.txt', '.xlsx', '.xls', 
            '.json', '.xml', '.dat', '.log'
        }
        self.common_delimiters = [',', '\t', ';', '|', ':', ' ']
        self.common_encodings = [
            'utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 
            'ascii', 'utf-16', 'utf-32'
        ]
    
    def detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding using chardet."""
        try:
            result = chardet.detect(file_content)
            encoding = result['encoding']
            confidence = result['confidence']
            
            logger.info(f"Detected encoding: {encoding} (confidence: {confidence})")
            
            # Fallback if confidence is too low
            if confidence < 0.7:
                logger.warning("Low confidence in encoding detection, trying common encodings")
                for enc in self.common_encodings:
                    try:
                        file_content.decode(enc)
                        return enc
                    except (UnicodeDecodeError, AttributeError):
                        continue
            
            return encoding or 'utf-8'
        except Exception as e:
            logger.error(f"Encoding detection failed: {e}")
            return 'utf-8'
    
    def detect_delimiter(self, content: str, sample_lines: int = 5) -> str:
        """Detect the most likely delimiter in the file."""
        lines = content.split('\n')[:sample_lines]
        delimiter_counts = {delim: 0 for delim in self.common_delimiters}
        
        for line in lines:
            if not line.strip():
                continue
            for delim in self.common_delimiters:
                delimiter_counts[delim] += line.count(delim)
        
        # Find delimiter with highest count that appears consistently
        best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        logger.info(f"Detected delimiter: {repr(best_delimiter)}")
        return best_delimiter
    
    def load_excel(self, file_path: Union[str, Path, BinaryIO]) -> pd.DataFrame:
        """Load Excel files (.xlsx, .xls) with multiple fallback strategies."""
        try:
            # Try openpyxl first (xlsx)
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.info("Loaded Excel file with openpyxl")
            return df
        except Exception as e1:
            logger.warning(f"openpyxl failed: {e1}")
            try:
                # Try xlrd for older .xls files
                df = pd.read_excel(file_path, engine='xlrd')
                logger.info("Loaded Excel file with xlrd")
                return df
            except Exception as e2:
                logger.error(f"All Excel engines failed: {e1}, {e2}")
                raise ValueError("Unable to load Excel file with any available engine")
    
    def load_csv_smart(self, file_content: bytes, encoding: str) -> pd.DataFrame:
        """Load CSV with automatic delimiter detection and error handling."""
        try:
            content = file_content.decode(encoding)
        except Exception as e:
            logger.warning(f"Decoding with {encoding} failed: {e}, trying latin-1")
            content = file_content.decode('latin-1', errors='ignore')
        
        # Detect delimiter
        delimiter = self.detect_delimiter(content)
        
        # Try multiple strategies
        strategies = [
            # Strategy 1: Standard read with detected delimiter
            lambda: pd.read_csv(
                io.StringIO(content), 
                delimiter=delimiter,
                encoding=encoding,
                on_bad_lines='skip'
            ),
            # Strategy 2: Let pandas infer delimiter
            lambda: pd.read_csv(
                io.StringIO(content),
                sep=None,
                engine='python',
                encoding=encoding,
                on_bad_lines='skip'
            ),
            # Strategy 3: Force common delimiters
            lambda: self._try_multiple_delimiters(content, encoding),
            # Strategy 4: Read as fixed-width if all else fails
            lambda: pd.read_fwf(io.StringIO(content))
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                df = strategy()
                if not df.empty and len(df.columns) > 0:
                    logger.info(f"Successfully loaded CSV with strategy {i}")
                    return df
            except Exception as e:
                logger.warning(f"Strategy {i} failed: {e}")
                continue
        
        raise ValueError("Unable to parse file with any available strategy")
    
    def _try_multiple_delimiters(self, content: str, encoding: str) -> pd.DataFrame:
        """Try loading with each common delimiter."""
        for delim in self.common_delimiters:
            try:
                df = pd.read_csv(
                    io.StringIO(content),
                    delimiter=delim,
                    encoding=encoding,
                    on_bad_lines='skip'
                )
                if len(df.columns) > 1:  # Successfully found columns
                    return df
            except Exception:
                continue
        raise ValueError("No suitable delimiter found")
    
    def load_json(self, file_content: bytes, encoding: str) -> pd.DataFrame:
        """Load JSON files (both array and line-delimited)."""
        try:
            content = file_content.decode(encoding)
            # Try standard JSON
            df = pd.read_json(io.StringIO(content))
            return df
        except Exception as e1:
            logger.warning(f"Standard JSON parsing failed: {e1}")
            try:
                # Try line-delimited JSON
                df = pd.read_json(io.StringIO(content), lines=True)
                return df
            except Exception as e2:
                logger.error(f"All JSON parsing methods failed: {e1}, {e2}")
                raise ValueError("Unable to parse JSON file")
    
    def load_xml(self, file_path: Union[str, Path, BinaryIO]) -> pd.DataFrame:
        """Load XML files."""
        try:
            df = pd.read_xml(file_path)
            logger.info("Loaded XML file")
            return df
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            raise ValueError(f"Unable to parse XML file: {e}")
    
    def _detect_format_from_content(self, content: bytes) -> str:
        """Try to detect file format from content."""
        try:
            # Check for Excel magic numbers
            if content.startswith(b'PK'):  # ZIP-based (xlsx)
                return '.xlsx'
            if content.startswith(b'\xd0\xcf\x11\xe0'):  # OLE2 (xls)
                return '.xls'
            
            # Try to decode and check for JSON/XML
            text = content.decode('utf-8', errors='ignore')[:1000]
            if text.strip().startswith('{') or text.strip().startswith('['):
                return '.json'
            if text.strip().startswith('<?xml') or text.strip().startswith('<'):
                return '.xml'
            
            # Default to CSV/text
            return '.csv'
        except Exception:
            return '.csv'
    
    def load(
        self, 
        file_path: Optional[Union[str, Path]] = None,
        file_content: Optional[bytes] = None,
        file_extension: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Universal loader that handles any text-based data format.
        
        Args:
            file_path: Path to the file
            file_content: Raw bytes content of the file
            file_extension: File extension (with dot, e.g., '.csv')
        
        Returns:
            Dict with 'dataframe', 'encoding', 'delimiter', 'format', 'success'
        """
        if file_path is None and file_content is None:
            raise ValueError("Either file_path or file_content must be provided")
        
        # Read file content if path is provided
        if file_content is None:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        
        # Detect extension
        if file_extension is None:
            if file_path:
                file_extension = Path(file_path).suffix.lower()
            else:
                # Try to detect from content
                file_extension = self._detect_format_from_content(file_content)
        
        # Detect encoding
        encoding = self.detect_encoding(file_content)
        
        # Load based on file type
        try:
            if file_extension in ['.xlsx', '.xls']:
                df = self.load_excel(io.BytesIO(file_content))
                return {
                    'dataframe': df,
                    'encoding': encoding,
                    'delimiter': None,
                    'format': 'excel',
                    'success': True
                }
            
            elif file_extension == '.json':
                df = self.load_json(file_content, encoding)
                return {
                    'dataframe': df,
                    'encoding': encoding,
                    'delimiter': None,
                    'format': 'json',
                    'success': True
                }
            
            elif file_extension == '.xml':
                df = self.load_xml(io.BytesIO(file_content))
                return {
                    'dataframe': df,
                    'encoding': encoding,
                    'delimiter': None,
                    'format': 'xml',
                    'success': True
                }
            
            else:  # CSV, TSV, TXT, or any text-based format
                df = self.load_csv_smart(file_content, encoding)
                delimiter = self.detect_delimiter(file_content.decode(encoding, errors='ignore'))
                return {
                    'dataframe': df,
                    'encoding': encoding,
                    'delimiter': delimiter,
                    'format': 'delimited',
                    'success': True
                }
        
        except Exception as e:
            logger.error(f"Failed to load file: {e}")
            return {
                'dataframe': None,
                'encoding': encoding,
                'delimiter': None,
                'format': 'unknown',
                'success': False,
                'error': str(e)
            }


def read_file(file_path):
    """
    Enhanced version: Reads ANY text-based file format into a pandas DataFrame.
    Now supports CSV, TSV, Excel, JSON, XML with automatic encoding/delimiter detection.
    
    Returns:
        pandas.DataFrame: The loaded data
    
    Raises:
        ValueError: If the file format is unsupported or parsing fails.
        FileNotFoundError: If the file path does not exist.
    """
    try:
        logger.info(f"Reading file: {file_path}")
        
        # Use the universal loader
        loader = UniversalDataLoader()
        result = loader.load(file_path=file_path)
        
        if not result['success']:
            raise ValueError(f"Failed to load file: {result.get('error', 'Unknown error')}")
        
        df = result['dataframe']
        
        if df.empty:
            raise ValueError("File is empty or contains no data")
        
        logger.info(f"Successfully read file with {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"Detected format: {result['format']}, encoding: {result['encoding']}")
        
        return df
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the file: {str(e)}")


def read_file_advanced(file_path=None, file_content=None, file_extension=None):
    """
    Advanced file reader that returns detailed metadata along with the DataFrame.
    
    Args:
        file_path: Path to the file (optional if file_content provided)
        file_content: Raw bytes content (optional if file_path provided)
        file_extension: File extension override (optional)
    
    Returns:
        Dict containing:
            - dataframe: The loaded pandas DataFrame
            - encoding: Detected encoding
            - delimiter: Detected delimiter (if applicable)
            - format: File format (excel, json, xml, delimited)
            - success: Boolean indicating success
            - rows: Number of rows
            - columns: Number of columns
            - column_names: List of column names
    """
    try:
        loader = UniversalDataLoader()
        result = loader.load(file_path, file_content, file_extension)
        
        if result['success']:
            df = result['dataframe']
            result['rows'] = len(df)
            result['columns'] = len(df.columns)
            result['column_names'] = df.columns.tolist()
            result['dtypes'] = df.dtypes.astype(str).to_dict()
        
        return result
    
    except Exception as e:
        logger.error(f"Error in advanced file reading: {e}")
        return {
            'success': False,
            'error': str(e),
            'dataframe': None
        }


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
            df.to_excel(output_path, index=False, engine='openpyxl')
        elif output_path.endswith('.json'):
            df.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError("Unsupported output file format. Supported: .csv, .xlsx, .xls, .json")
    except Exception as e:
        raise RuntimeError(f"An error occurred while exporting data: {e}")
