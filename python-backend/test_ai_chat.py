"""
Comprehensive Unit Tests for AI Chat System
============================================
Tests for AI Chat JSON-based communication, parsing, and operations.
Can be run individually from command prompt.

Usage:
    python3 test_ai_chat.py           # Basic output
    python3 test_ai_chat.py -v        # Verbose output with detailed data
    python3 test_ai_chat.py --verbose # Same as -v
"""

import json
import unittest
import logging
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

import pandas as pd
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_chat import (
    AIChat, AIChatConfig, AIResponse, AIOperation,
    DataContext, OperationType, FillMethod,
    create_sample_dataframe, AZURE_OPENAI_AVAILABLE
)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global verbose flag
VERBOSE = '-v' in sys.argv or '--verbose' in sys.argv


class VerboseTestResult(unittest.TextTestResult):
    """Custom test result class for verbose output"""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_details = []

    def startTest(self, test):
        super().startTest(test)
        if VERBOSE:
            self.stream.write("\n" + "-"*60 + "\n")
            self.stream.write(f"  TEST: {test._testMethodName}\n")
            self.stream.write("-"*60 + "\n")
            if test._testMethodDoc:
                self.stream.write(f"  Description: {test._testMethodDoc.strip()}\n")

    def addSuccess(self, test):
        super().addSuccess(test)
        if VERBOSE:
            self.stream.write(f"  Result: PASSED\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if VERBOSE:
            self.stream.write(f"  Result: FAILED\n")
            self.stream.write(f"  Error: {err[1]}\n")

    def addError(self, test, err):
        super().addError(test, err)
        if VERBOSE:
            self.stream.write(f"  Result: ERROR\n")
            self.stream.write(f"  Error: {err[1]}\n")


class VerboseTestRunner(unittest.TextTestRunner):
    """Custom test runner for verbose output"""

    def __init__(self, **kwargs):
        kwargs['resultclass'] = VerboseTestResult
        super().__init__(**kwargs)


# ==============================================================================
# CONFIG TESTS
# ==============================================================================

class TestAIChatConfig(unittest.TestCase):
    """Test AIChatConfig validation"""

    def test_config_with_all_values(self):
        """Test config with all required values"""
        config = AIChatConfig(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        is_valid, errors = config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_config_missing_api_key(self):
        """Test config validation fails without API key"""
        config = AIChatConfig(
            api_key=None,
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        # Clear env vars for test
        with patch.dict(os.environ, {}, clear=True):
            config.api_key = None
            is_valid, errors = config.validate()
            self.assertFalse(is_valid)
            self.assertTrue(any('API key' in e for e in errors))

    def test_config_missing_endpoint(self):
        """Test config validation fails without endpoint"""
        config = AIChatConfig(
            api_key="test_key",
            endpoint=None,
            deployment="gpt-4"
        )
        with patch.dict(os.environ, {}, clear=True):
            config.endpoint = None
            is_valid, errors = config.validate()
            self.assertFalse(is_valid)
            self.assertTrue(any('Endpoint' in e for e in errors))

    def test_config_missing_deployment(self):
        """Test config validation fails without deployment"""
        config = AIChatConfig(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            deployment=None
        )
        with patch.dict(os.environ, {}, clear=True):
            config.deployment = None
            is_valid, errors = config.validate()
            self.assertFalse(is_valid)
            self.assertTrue(any('Deployment' in e for e in errors))

    def test_config_default_values(self):
        """Test config has sensible defaults"""
        config = AIChatConfig(
            api_key="test",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        self.assertEqual(config.api_version, "2024-02-15-preview")
        self.assertEqual(config.max_tokens, 2000)
        self.assertIsNone(config.temperature)  # None by default (use model default)


# ==============================================================================
# DATA CONTEXT TESTS
# ==============================================================================

class TestDataContext(unittest.TestCase):
    """Test DataContext creation and serialization"""

    def setUp(self):
        """Set up test DataFrame"""
        self.df = create_sample_dataframe()

    def test_from_dataframe_basic(self):
        """Test DataContext creation from DataFrame"""
        context = DataContext.from_dataframe(self.df)

        self.assertEqual(context.row_count, len(self.df))
        self.assertEqual(context.column_count, len(self.df.columns))
        self.assertEqual(len(context.columns), len(self.df.columns))

    def test_from_dataframe_columns(self):
        """Test column information extraction"""
        context = DataContext.from_dataframe(self.df)

        column_names = [c['name'] for c in context.columns]
        self.assertEqual(set(column_names), set(self.df.columns))

        # Check column metadata
        for col_info in context.columns:
            col_name = col_info['name']
            self.assertIn('dtype', col_info)
            self.assertIn('null_count', col_info)
            self.assertIn('unique_count', col_info)
            self.assertEqual(col_info['null_count'], int(self.df[col_name].isnull().sum()))

    def test_from_dataframe_missing_values(self):
        """Test missing values detection"""
        context = DataContext.from_dataframe(self.df)

        # Sample data has missing values
        self.assertGreater(len(context.missing_values), 0)

        for col, info in context.missing_values.items():
            self.assertIn('count', info)
            self.assertIn('percentage', info)
            self.assertGreater(info['count'], 0)

    def test_from_dataframe_numeric_stats(self):
        """Test numeric column statistics"""
        context = DataContext.from_dataframe(self.df)

        # Should have stats for numeric columns
        self.assertGreater(len(context.numeric_stats), 0)

        for col, stats in context.numeric_stats.items():
            self.assertIn('mean', stats)
            self.assertIn('min', stats)
            self.assertIn('max', stats)
            self.assertIn('median', stats)

    def test_from_dataframe_sample_data(self):
        """Test sample data extraction"""
        context = DataContext.from_dataframe(self.df, max_samples=3)

        self.assertEqual(len(context.sample_data), 3)

        # Check sample data has correct columns
        for sample in context.sample_data:
            self.assertEqual(set(sample.keys()), set(self.df.columns))

    def test_to_json(self):
        """Test JSON serialization"""
        context = DataContext.from_dataframe(self.df)
        json_str = context.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        self.assertIn('row_count', parsed)
        self.assertIn('column_count', parsed)
        self.assertIn('columns', parsed)

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        context = DataContext.from_dataframe(empty_df)

        self.assertEqual(context.row_count, 0)
        self.assertEqual(context.column_count, 0)
        self.assertEqual(len(context.columns), 0)


# ==============================================================================
# JSON PARSING TESTS
# ==============================================================================

class TestJSONParsing(unittest.TestCase):
    """Test JSON response parsing"""

    def setUp(self):
        """Set up AIChat instance for testing"""
        # Create a mock chat instance that doesn't require real credentials
        self.chat = AIChat.__new__(AIChat)
        self.chat.config = AIChatConfig(
            api_key="test",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        self.chat.client = None

    def test_parse_clean_json(self):
        """Test parsing clean JSON response"""
        response = '''{
            "message": "Test message",
            "operations": [
                {
                    "operation": "fill_nulls",
                    "column": "age",
                    "parameters": {"method": "mean"},
                    "description": "Fill missing ages with mean",
                    "confidence": 0.95,
                    "reasoning": "Mean is appropriate for numeric data"
                }
            ],
            "analysis": null
        }'''

        parsed = self.chat._parse_json_response(response)

        self.assertEqual(parsed['message'], "Test message")
        self.assertEqual(len(parsed['operations']), 1)
        self.assertEqual(parsed['operations'][0]['operation'], 'fill_nulls')

    def test_parse_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks"""
        response = '''```json
{
    "message": "Test message",
    "operations": [],
    "analysis": null
}
```'''

        parsed = self.chat._parse_json_response(response)
        self.assertEqual(parsed['message'], "Test message")

    def test_parse_json_with_smart_quotes(self):
        """Test parsing JSON with smart quotes as delimiters"""
        # Smart quotes replacing JSON structure quotes (common from copy-paste)
        response = '''{
            "message": "Test message with data",
            "operations": [],
            "analysis": null
        }'''

        parsed = self.chat._parse_json_response(response)
        self.assertIn('Test message', parsed['message'])

    def test_parse_json_with_trailing_comma(self):
        """Test parsing JSON with trailing commas"""
        response = '''{
            "message": "Test",
            "operations": [],
        }'''

        parsed = self.chat._parse_json_response(response)
        self.assertEqual(parsed['message'], "Test")

    def test_parse_invalid_json(self):
        """Test handling of invalid JSON"""
        response = "This is not JSON at all"

        with self.assertRaises(ValueError):
            self.chat._parse_json_response(response)

    def test_extract_operations(self):
        """Test operation extraction from parsed JSON"""
        parsed = {
            "message": "Test",
            "operations": [
                {
                    "operation": "fill_nulls",
                    "column": "age",
                    "parameters": {"method": "mean"},
                    "confidence": 0.9
                },
                {
                    "operation": "remove_duplicates",
                    "column": None,
                    "parameters": {}
                }
            ]
        }

        operations = self.chat._extract_operations(parsed)

        self.assertEqual(len(operations), 2)
        self.assertEqual(operations[0].operation, OperationType.FILL_NULLS)
        self.assertEqual(operations[0].column, "age")
        self.assertEqual(operations[1].operation, OperationType.REMOVE_DUPLICATES)

    def test_extract_operations_invalid_type(self):
        """Test operation extraction with invalid operation type"""
        parsed = {
            "operations": [
                {
                    "operation": "invalid_operation",
                    "column": "test"
                }
            ]
        }

        operations = self.chat._extract_operations(parsed)
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0].operation, OperationType.NONE)


# ==============================================================================
# AI OPERATION TESTS
# ==============================================================================

class TestAIOperation(unittest.TestCase):
    """Test AIOperation dataclass"""

    def test_create_operation(self):
        """Test creating an AI operation"""
        op = AIOperation(
            operation=OperationType.FILL_NULLS,
            column="age",
            parameters={"method": "mean"},
            description="Fill with mean",
            confidence=0.95,
            reasoning="Mean is good for numeric"
        )

        self.assertEqual(op.operation, OperationType.FILL_NULLS)
        self.assertEqual(op.column, "age")
        self.assertEqual(op.parameters["method"], "mean")

    def test_operation_to_dict(self):
        """Test converting operation to dictionary"""
        op = AIOperation(
            operation=OperationType.REMOVE_NULLS,
            column="name"
        )

        d = op.to_dict()

        self.assertEqual(d['operation'], 'remove_nulls')
        self.assertEqual(d['column'], 'name')

    def test_operation_default_values(self):
        """Test operation default values"""
        op = AIOperation(operation=OperationType.ANALYZE)

        self.assertIsNone(op.column)
        self.assertEqual(op.parameters, {})
        self.assertEqual(op.confidence, 1.0)


# ==============================================================================
# AI RESPONSE TESTS
# ==============================================================================

class TestAIResponse(unittest.TestCase):
    """Test AIResponse dataclass"""

    def test_create_response(self):
        """Test creating AI response"""
        response = AIResponse(
            success=True,
            message="Analysis complete",
            operations=[
                AIOperation(operation=OperationType.FILL_NULLS, column="age")
            ]
        )

        self.assertTrue(response.success)
        self.assertEqual(response.message, "Analysis complete")
        self.assertEqual(len(response.operations), 1)

    def test_response_to_dict(self):
        """Test converting response to dictionary"""
        response = AIResponse(
            success=True,
            message="Test",
            usage={"total_tokens": 100}
        )

        d = response.to_dict()

        self.assertTrue(d['success'])
        self.assertEqual(d['message'], "Test")
        self.assertEqual(d['usage']['total_tokens'], 100)

    def test_response_to_json(self):
        """Test converting response to JSON string"""
        response = AIResponse(
            success=True,
            message="Test message"
        )

        json_str = response.to_json()
        parsed = json.loads(json_str)

        self.assertTrue(parsed['success'])
        self.assertEqual(parsed['message'], "Test message")

    def test_error_response(self):
        """Test error response"""
        response = AIResponse(
            success=False,
            message="",
            error="Connection failed"
        )

        self.assertFalse(response.success)
        self.assertEqual(response.error, "Connection failed")


# ==============================================================================
# OPERATION EXECUTION TESTS
# ==============================================================================

class TestOperationExecution(unittest.TestCase):
    """Test operation execution on DataFrames"""

    def setUp(self):
        """Set up test data"""
        self.df = create_sample_dataframe()
        self.chat = AIChat.__new__(AIChat)
        self.chat.config = AIChatConfig(
            api_key="test",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )

    def test_fill_nulls_mean(self):
        """Test fill nulls with mean"""
        op = AIOperation(
            operation=OperationType.FILL_NULLS,
            column="age",
            parameters={"method": "mean"}
        )

        original_nulls = self.df['age'].isnull().sum()
        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertEqual(result_df['age'].isnull().sum(), 0)
        self.assertGreater(original_nulls, 0)  # Confirm there were nulls

    def test_fill_nulls_median(self):
        """Test fill nulls with median"""
        op = AIOperation(
            operation=OperationType.FILL_NULLS,
            column="salary",
            parameters={"method": "median"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertEqual(result_df['salary'].isnull().sum(), 0)

    def test_fill_nulls_mode(self):
        """Test fill nulls with mode"""
        op = AIOperation(
            operation=OperationType.FILL_NULLS,
            column="department",
            parameters={"method": "mode"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertEqual(result_df['department'].isnull().sum(), 0)

    def test_fill_nulls_constant(self):
        """Test fill nulls with constant value"""
        op = AIOperation(
            operation=OperationType.FILL_NULLS,
            column="name",
            parameters={"method": "constant", "value": "Unknown"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertEqual(result_df['name'].isnull().sum(), 0)
        self.assertIn("Unknown", result_df['name'].values)

    def test_remove_nulls(self):
        """Test remove rows with nulls"""
        op = AIOperation(
            operation=OperationType.REMOVE_NULLS,
            column="age"
        )

        original_len = len(self.df)
        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertLess(len(result_df), original_len)
        self.assertEqual(result_df['age'].isnull().sum(), 0)

    def test_remove_duplicates(self):
        """Test remove duplicate rows"""
        # Add duplicates
        df_with_dups = pd.concat([self.df, self.df.head(2)], ignore_index=True)

        op = AIOperation(operation=OperationType.REMOVE_DUPLICATES)

        result_df, details = self.chat.execute_operation(df_with_dups, op)

        self.assertTrue(details['success'])
        self.assertLessEqual(len(result_df), len(df_with_dups))

    def test_remove_column(self):
        """Test remove column"""
        op = AIOperation(
            operation=OperationType.REMOVE_COLUMN,
            column="department"
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertNotIn("department", result_df.columns)

    def test_rename_column(self):
        """Test rename column"""
        op = AIOperation(
            operation=OperationType.RENAME_COLUMN,
            column="age",
            parameters={"new_name": "years_old"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertNotIn("age", result_df.columns)
        self.assertIn("years_old", result_df.columns)

    def test_change_case_upper(self):
        """Test change case to upper"""
        op = AIOperation(
            operation=OperationType.CHANGE_CASE,
            column="name",
            parameters={"case_type": "upper"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        # Check non-null values are uppercase
        non_null = result_df['name'][self.df['name'].notna()]
        for val in non_null:
            self.assertEqual(val, val.upper())

    def test_change_case_lower(self):
        """Test change case to lower"""
        op = AIOperation(
            operation=OperationType.CHANGE_CASE,
            column="department",
            parameters={"case_type": "lower"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])

    def test_trim_whitespace(self):
        """Test trim whitespace"""
        # Add whitespace to test
        df_with_spaces = self.df.copy()
        df_with_spaces['name'] = df_with_spaces['name'].apply(
            lambda x: f"  {x}  " if pd.notna(x) else x
        )

        op = AIOperation(
            operation=OperationType.TRIM_WHITESPACE,
            column="name"
        )

        result_df, details = self.chat.execute_operation(df_with_spaces, op)

        self.assertTrue(details['success'])

    def test_find_replace(self):
        """Test find and replace"""
        op = AIOperation(
            operation=OperationType.FIND_REPLACE,
            column="department",
            parameters={"find_value": "IT", "replace_value": "Engineering"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        self.assertNotIn("IT", result_df['department'].values)

    def test_invalid_column(self):
        """Test operation on non-existent column"""
        op = AIOperation(
            operation=OperationType.FILL_NULLS,
            column="nonexistent_column",
            parameters={"method": "mean"}
        )

        result_df, details = self.chat.execute_operation(self.df, op)

        # Should not crash, but success depends on implementation
        # The original DataFrame should remain unchanged
        pd.testing.assert_frame_equal(result_df, self.df)

    def test_analyze_operation_no_change(self):
        """Test analyze operation doesn't modify data"""
        op = AIOperation(operation=OperationType.ANALYZE)

        result_df, details = self.chat.execute_operation(self.df, op)

        self.assertTrue(details['success'])
        pd.testing.assert_frame_equal(result_df, self.df)


# ==============================================================================
# INTEGRATION TESTS (Mocked API)
# ==============================================================================

class TestAIChatIntegration(unittest.TestCase):
    """Integration tests with mocked API calls"""

    def setUp(self):
        """Set up mocked AI Chat"""
        self.df = create_sample_dataframe()

    @patch('ai_chat.AzureOpenAI')
    def test_chat_basic_flow(self, mock_azure):
        """Test basic chat flow with mocked API"""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "message": "I recommend filling missing values",
            "operations": [
                {
                    "operation": "fill_nulls",
                    "column": "age",
                    "parameters": {"method": "mean"},
                    "description": "Fill age with mean",
                    "confidence": 0.95,
                    "reasoning": "Mean is appropriate"
                }
            ],
            "analysis": None
        })
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client

        # Create chat with valid config
        config = AIChatConfig(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        chat = AIChat(config)

        # Send a message
        response = chat.chat("How should I handle missing values?", df=self.df)

        self.assertTrue(response.success)
        self.assertIn("missing values", response.message.lower())
        self.assertEqual(len(response.operations), 1)
        self.assertEqual(response.operations[0].operation, OperationType.FILL_NULLS)

    @patch('ai_chat.AzureOpenAI')
    def test_chat_with_analysis(self, mock_azure):
        """Test chat that returns analysis"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "message": "Here is my analysis",
            "operations": [
                {"operation": "analyze", "column": None, "parameters": {}}
            ],
            "analysis": {
                "summary": "Dataset has quality issues",
                "issues_found": ["Missing values in age", "Duplicates detected"],
                "recommendations": ["Fill nulls first", "Remove duplicates"]
            }
        })
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 80
        mock_response.usage.total_tokens = 180

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client

        config = AIChatConfig(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        chat = AIChat(config)

        response = chat.analyze_data_quality(self.df)

        self.assertTrue(response.success)
        self.assertIsNotNone(response.analysis)
        self.assertIn('issues_found', response.analysis)
        self.assertEqual(len(response.analysis['issues_found']), 2)

    @patch('ai_chat.AzureOpenAI')
    def test_chat_conversation_history(self, mock_azure):
        """Test chat maintains conversation history"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "message": "Based on our previous discussion...",
            "operations": [],
            "analysis": None
        })
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 200
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 250

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client

        config = AIChatConfig(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        chat = AIChat(config)

        history = [
            {"role": "user", "content": "I have a dataset"},
            {"role": "assistant", "content": "I see. Tell me more."}
        ]

        response = chat.chat(
            "Continue helping me",
            df=self.df,
            conversation_history=history
        )

        self.assertTrue(response.success)

        # Verify API was called with history
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        # Should have system + history + current message
        self.assertGreater(len(messages), 2)


# ==============================================================================
# EDGE CASE TESTS
# ==============================================================================

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        """Set up test data"""
        self.chat = AIChat.__new__(AIChat)
        self.chat.config = AIChatConfig(
            api_key="test",
            endpoint="https://test.openai.azure.com",
            deployment="gpt-4"
        )
        self.chat.client = None

    def test_empty_operations_list(self):
        """Test handling empty operations list"""
        parsed = {"message": "No actions needed", "operations": []}
        operations = self.chat._extract_operations(parsed)
        self.assertEqual(len(operations), 0)

    def test_null_operations_field(self):
        """Test handling null operations field"""
        parsed = {"message": "No actions", "operations": None}
        operations = self.chat._extract_operations(parsed)
        self.assertEqual(len(operations), 0)

    def test_missing_operations_field(self):
        """Test handling missing operations field"""
        parsed = {"message": "Response without operations"}
        operations = self.chat._extract_operations(parsed)
        self.assertEqual(len(operations), 0)

    def test_malformed_operation(self):
        """Test handling malformed operation object"""
        parsed = {"operations": ["not_a_dict", None, 123]}
        operations = self.chat._extract_operations(parsed)
        # Should skip invalid entries
        self.assertEqual(len(operations), 0)

    def test_operation_with_missing_fields(self):
        """Test operation with minimal fields"""
        parsed = {
            "operations": [
                {"operation": "fill_nulls"}  # Missing column and parameters
            ]
        }
        operations = self.chat._extract_operations(parsed)

        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0].operation, OperationType.FILL_NULLS)
        self.assertIsNone(operations[0].column)

    def test_very_large_dataframe_context(self):
        """Test handling large DataFrame context"""
        # Create a larger DataFrame
        large_df = pd.DataFrame({
            f'col_{i}': np.random.randn(1000) for i in range(50)
        })

        context = DataContext.from_dataframe(large_df, max_samples=5)

        self.assertEqual(context.row_count, 1000)
        self.assertEqual(context.column_count, 50)
        self.assertEqual(len(context.sample_data), 5)

    def test_dataframe_with_special_characters(self):
        """Test DataFrame with special characters in values"""
        df = pd.DataFrame({
            'text': ['Hello "World"', "It's a test", 'Line1\nLine2', 'Tab\there'],
            'unicode': ['café', '日本語', 'émoji 😀', 'Ñoño']
        })

        context = DataContext.from_dataframe(df)
        json_str = context.to_json()

        # Should produce valid JSON
        parsed = json.loads(json_str)
        self.assertIsNotNone(parsed)


# ==============================================================================
# SAMPLE DATA TESTS
# ==============================================================================

class TestSampleData(unittest.TestCase):
    """Test sample data creation"""

    def test_create_sample_dataframe(self):
        """Test sample DataFrame creation"""
        df = create_sample_dataframe()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 10)
        self.assertEqual(len(df.columns), 5)

    def test_sample_has_missing_values(self):
        """Test sample data has missing values for testing"""
        df = create_sample_dataframe()

        total_nulls = df.isnull().sum().sum()
        self.assertGreater(total_nulls, 0)

    def test_sample_has_various_types(self):
        """Test sample data has various data types"""
        df = create_sample_dataframe()

        # Should have string, numeric, and datetime columns
        dtypes = df.dtypes.astype(str).tolist()
        dtype_categories = set()

        for dtype in dtypes:
            if 'int' in dtype or 'float' in dtype:
                dtype_categories.add('numeric')
            elif 'datetime' in dtype:
                dtype_categories.add('datetime')
            elif 'object' in dtype:
                dtype_categories.add('object')

        self.assertIn('numeric', dtype_categories)
        self.assertIn('object', dtype_categories)


# ==============================================================================
# OPERATION TYPE TESTS
# ==============================================================================

class TestOperationTypes(unittest.TestCase):
    """Test OperationType enum"""

    def test_all_operation_types_defined(self):
        """Test all expected operation types are defined"""
        expected_ops = [
            'fill_nulls', 'remove_nulls', 'remove_duplicates',
            'remove_column', 'rename_column', 'change_case',
            'find_replace', 'filter_rows', 'trim_whitespace',
            'convert_type', 'analyze', 'none'
        ]

        for op in expected_ops:
            self.assertTrue(
                hasattr(OperationType, op.upper()),
                f"Missing operation type: {op}"
            )

    def test_operation_type_values(self):
        """Test operation type string values"""
        self.assertEqual(OperationType.FILL_NULLS.value, "fill_nulls")
        self.assertEqual(OperationType.REMOVE_DUPLICATES.value, "remove_duplicates")
        self.assertEqual(OperationType.NONE.value, "none")


# ==============================================================================
# TEST RUNNER
# ==============================================================================

def run_all_tests():
    """Run all test classes and print summary"""

    print("\n" + "="*70)
    print("  AI CHAT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)

    if VERBOSE:
        print("\nRunning in VERBOSE mode")
        print("-"*70)

    # Print test configuration in verbose mode
    if VERBOSE:
        print("\nTest Classes:")
        print("  - TestAIChatConfig: Configuration validation tests")
        print("  - TestDataContext: Data context creation and serialization")
        print("  - TestJSONParsing: JSON response parsing tests")
        print("  - TestAIOperation: AIOperation dataclass tests")
        print("  - TestAIResponse: AIResponse dataclass tests")
        print("  - TestOperationExecution: Operation execution on DataFrames")
        print("  - TestAIChatIntegration: Integration tests with mocked API")
        print("  - TestEdgeCases: Edge cases and error handling")
        print("  - TestSampleData: Sample data creation tests")
        print("  - TestOperationTypes: OperationType enum tests")
        print("\n" + "="*70 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAIChatConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestDataContext))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestAIOperation))
    suite.addTests(loader.loadTestsFromTestCase(TestAIResponse))
    suite.addTests(loader.loadTestsFromTestCase(TestOperationExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestAIChatIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestSampleData))
    suite.addTests(loader.loadTestsFromTestCase(TestOperationTypes))

    # Use verbose runner if verbose mode is enabled
    if VERBOSE:
        runner = VerboseTestRunner(verbosity=2)
    else:
        runner = unittest.TextTestRunner(verbosity=2)

    result = runner.run(suite)

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if VERBOSE and result.failures:
        print("\n" + "-"*70)
        print("FAILURE DETAILS:")
        print("-"*70)
        for test, traceback in result.failures:
            print(f"\n  Test: {test}")
            print(f"  Traceback:\n{traceback}")

    if VERBOSE and result.errors:
        print("\n" + "-"*70)
        print("ERROR DETAILS:")
        print("-"*70)
        for test, traceback in result.errors:
            print(f"\n  Test: {test}")
            print(f"  Traceback:\n{traceback}")

    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
