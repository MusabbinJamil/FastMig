"""
AI Chat Module for FastMig
==========================
JSON-based communication with LLM models for data cleaning and migration tasks.

This module provides structured JSON-based input/output for AI chat functionality,
ensuring reliable parsing and consistent response formats.

Usage:
    from ai_chat import AIChat, AIChatConfig, DataCleaningRequest

    chat = AIChat(config)
    response = chat.analyze_data(df, user_query)
"""

import os
import json
import re
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Azure OpenAI
AZURE_OPENAI_AVAILABLE = False
AzureOpenAI = None
try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI package not available. Install with: pip install openai")


class OperationType(str, Enum):
    """Available data operations"""
    FILL_NULLS = "fill_nulls"
    REMOVE_NULLS = "remove_nulls"
    REMOVE_DUPLICATES = "remove_duplicates"
    REMOVE_COLUMN = "remove_column"
    RENAME_COLUMN = "rename_column"
    CHANGE_CASE = "change_case"
    FIND_REPLACE = "find_replace"
    FILTER_ROWS = "filter_rows"
    TRIM_WHITESPACE = "trim_whitespace"
    CONVERT_TYPE = "convert_type"
    ANALYZE = "analyze"
    NONE = "none"


class FillMethod(str, Enum):
    """Methods for filling null values"""
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    CONSTANT = "constant"
    FORWARD_FILL = "ffill"
    BACKWARD_FILL = "bfill"


@dataclass
class AIChatConfig:
    """Configuration for AI Chat"""
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    deployment: Optional[str] = None
    api_version: str = "2024-02-15-preview"
    max_tokens: int = 2000
    temperature: float = 0.1  # Low temperature for consistent JSON output

    def __post_init__(self):
        # Load from environment if not provided
        self.api_key = self.api_key or os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = self.endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        self.deployment = self.deployment or os.getenv('AZURE_OPENAI_DEPLOYMENT')
        self.api_version = self.api_version or os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration"""
        errors = []
        if not self.api_key:
            errors.append("API key is required (set AZURE_OPENAI_API_KEY)")
        if not self.endpoint:
            errors.append("Endpoint is required (set AZURE_OPENAI_ENDPOINT)")
        if not self.deployment:
            errors.append("Deployment is required (set AZURE_OPENAI_DEPLOYMENT)")
        return len(errors) == 0, errors


@dataclass
class DataContext:
    """Structured data context for AI"""
    row_count: int
    column_count: int
    columns: List[Dict[str, Any]]
    sample_data: List[Dict[str, Any]]
    numeric_stats: Dict[str, Dict[str, float]]
    missing_values: Dict[str, Dict[str, Any]]
    data_types: Dict[str, str]

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self), indent=2, default=str)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, max_samples: int = 5) -> 'DataContext':
        """Create DataContext from DataFrame"""
        columns = []
        missing_values = {}
        data_types = {}

        for col in df.columns:
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())
            dtype = str(df[col].dtype)

            columns.append({
                "name": col,
                "dtype": dtype,
                "null_count": null_count,
                "null_percentage": round((null_count / len(df)) * 100, 2) if len(df) > 0 else 0,
                "unique_count": unique_count
            })

            data_types[col] = dtype

            if null_count > 0:
                missing_values[col] = {
                    "count": null_count,
                    "percentage": round((null_count / len(df)) * 100, 2) if len(df) > 0 else 0
                }

        # Sample data
        sample_data = []
        for idx, row in df.head(max_samples).iterrows():
            sample_row = {}
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    sample_row[col] = None
                elif isinstance(val, pd.Timestamp):
                    sample_row[col] = val.isoformat()
                else:
                    sample_row[col] = val
            sample_data.append(sample_row)

        # Numeric statistics
        numeric_stats = {}
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            stats = df[col].describe()
            numeric_stats[col] = {
                "mean": round(float(stats['mean']), 4) if not pd.isna(stats['mean']) else None,
                "std": round(float(stats['std']), 4) if not pd.isna(stats['std']) else None,
                "min": round(float(stats['min']), 4) if not pd.isna(stats['min']) else None,
                "max": round(float(stats['max']), 4) if not pd.isna(stats['max']) else None,
                "median": round(float(stats['50%']), 4) if not pd.isna(stats['50%']) else None
            }

        return cls(
            row_count=len(df),
            column_count=len(df.columns),
            columns=columns,
            sample_data=sample_data,
            numeric_stats=numeric_stats,
            missing_values=missing_values,
            data_types=data_types
        )


@dataclass
class AIOperation:
    """Structured AI operation response"""
    operation: OperationType
    column: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    confidence: float = 1.0
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation.value if isinstance(self.operation, OperationType) else self.operation,
            "column": self.column,
            "parameters": self.parameters,
            "description": self.description,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


@dataclass
class AIResponse:
    """Structured AI chat response"""
    success: bool
    message: str
    operations: List[AIOperation] = field(default_factory=list)
    analysis: Optional[Dict[str, Any]] = None
    raw_response: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "operations": [op.to_dict() for op in self.operations],
            "analysis": self.analysis,
            "usage": self.usage,
            "error": self.error
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class AIChat:
    """
    AI Chat handler with JSON-based communication.

    This class provides structured JSON input/output for LLM interactions,
    ensuring reliable parsing and consistent response formats.
    """

    # JSON response schema for the LLM
    RESPONSE_SCHEMA = """
{
    "message": "Human-readable response to the user's query",
    "operations": [
        {
            "operation": "fill_nulls|remove_nulls|remove_duplicates|remove_column|rename_column|change_case|find_replace|filter_rows|trim_whitespace|convert_type|analyze|none",
            "column": "column_name or null",
            "parameters": {
                "method": "mean|median|mode|constant|ffill|bfill (for fill_nulls)",
                "value": "value for constant fill or replacements",
                "new_name": "for rename_column",
                "case_type": "upper|lower|title (for change_case)",
                "find_value": "for find_replace",
                "replace_value": "for find_replace",
                "operator": "==|!=|>|<|>=|<= (for filter_rows)",
                "filter_value": "for filter_rows",
                "target_type": "int|float|str|datetime (for convert_type)"
            },
            "description": "Brief description of what this operation will do",
            "confidence": 0.95,
            "reasoning": "Why this operation is recommended"
        }
    ],
    "analysis": {
        "summary": "Optional analysis summary",
        "issues_found": ["list of data quality issues"],
        "recommendations": ["list of recommendations"]
    }
}
"""

    SYSTEM_PROMPT = """You are a data cleaning and migration assistant for the FastMig tool.
You help users understand, clean, and transform their data using structured JSON responses.

IMPORTANT: You MUST respond with ONLY valid JSON. No markdown, no explanations outside JSON.

Available operations:
- fill_nulls: Fill missing values (methods: mean, median, mode, constant, ffill, bfill)
- remove_nulls: Remove rows with null values in specified column
- remove_duplicates: Remove duplicate rows
- remove_column: Remove a column from the dataset
- rename_column: Rename a column
- change_case: Change text case (upper, lower, title)
- find_replace: Find and replace values in a column
- filter_rows: Filter rows by condition
- trim_whitespace: Remove leading/trailing whitespace
- convert_type: Convert column data type
- analyze: Analyze data without modifications
- none: No operation needed (just answering a question)

Response format (MUST be valid JSON):
{schema}

Guidelines:
1. Always respond with valid JSON only - no text before or after
2. Suggest operations based on the data context provided
3. Include confidence scores (0-1) for each operation
4. Provide clear reasoning for each recommendation
5. For analysis queries, use operation="analyze" with analysis field
6. If you can't determine an operation, use operation="none"
7. Use actual column names from the data context
8. Be specific with parameters
"""

    def __init__(self, config: Optional[AIChatConfig] = None):
        """Initialize AI Chat with configuration"""
        self.config = config or AIChatConfig()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        if not AZURE_OPENAI_AVAILABLE:
            logger.warning("Azure OpenAI not available")
            return

        is_valid, errors = self.config.validate()
        if not is_valid:
            logger.warning(f"Config validation failed: {errors}")
            return

        try:
            self.client = AzureOpenAI(
                api_key=self.config.api_key,
                api_version=self.config.api_version,
                azure_endpoint=self.config.endpoint
            )
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if AI chat is available"""
        return self.client is not None

    def _build_system_prompt(self) -> str:
        """Build the system prompt with schema"""
        return self.SYSTEM_PROMPT.format(schema=self.RESPONSE_SCHEMA)

    def _build_data_context_prompt(self, df: pd.DataFrame) -> str:
        """Build data context in JSON format"""
        context = DataContext.from_dataframe(df)
        return f"\n\nCurrent Dataset Context (JSON):\n```json\n{context.to_json()}\n```"

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM with robust error handling.

        Handles common issues like:
        - Markdown code blocks
        - Smart quotes
        - Control characters
        - Trailing commas
        """
        cleaned = response_text.strip()

        # Remove markdown code blocks
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1].strip()

        # Replace smart quotes with regular quotes
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        cleaned = cleaned.replace(''', "'").replace(''', "'")

        # Remove control characters except newlines and tabs
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned)

        # Try to parse JSON
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}")

            # Try additional cleanup
            try:
                # Remove trailing commas before closing braces/brackets
                cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

                # Try to fix unescaped quotes in strings (aggressive)
                # This is risky but can help with malformed JSON
                return json.loads(cleaned)
            except json.JSONDecodeError as e2:
                logger.error(f"JSON parse failed after cleanup: {e2}")
                raise ValueError(f"Could not parse AI response as JSON: {e2}")

    def _extract_operations(self, parsed: Dict[str, Any]) -> List[AIOperation]:
        """Extract operations from parsed JSON response"""
        operations = []

        raw_ops = parsed.get('operations', [])
        if not isinstance(raw_ops, list):
            raw_ops = [raw_ops] if raw_ops else []

        for op in raw_ops:
            if not isinstance(op, dict):
                continue

            operation_type = op.get('operation', 'none')
            try:
                op_enum = OperationType(operation_type)
            except ValueError:
                op_enum = OperationType.NONE

            operations.append(AIOperation(
                operation=op_enum,
                column=op.get('column'),
                parameters=op.get('parameters', {}),
                description=op.get('description', ''),
                confidence=float(op.get('confidence', 1.0)),
                reasoning=op.get('reasoning', '')
            ))

        return operations

    def chat(
        self,
        user_message: str,
        df: Optional[pd.DataFrame] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        include_data_context: bool = True
    ) -> AIResponse:
        """
        Send a chat message to the AI with JSON-based communication.

        Args:
            user_message: The user's query
            df: Optional DataFrame for data context
            conversation_history: Previous conversation messages
            include_data_context: Whether to include data context in prompt

        Returns:
            AIResponse with structured operation suggestions
        """
        if not self.is_available():
            return AIResponse(
                success=False,
                message="AI Chat is not available",
                error="Azure OpenAI client not initialized"
            )

        try:
            # Build messages
            messages = [{"role": "system", "content": self._build_system_prompt()}]

            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Limit to last 10
                    messages.append({
                        "role": msg.get('role', 'user'),
                        "content": msg.get('content', '')
                    })

            # Build user message with data context
            full_message = user_message
            if include_data_context and df is not None:
                full_message += self._build_data_context_prompt(df)

            # Add instruction to respond in JSON
            full_message += "\n\nRespond with ONLY valid JSON following the schema provided."

            messages.append({"role": "user", "content": full_message})

            logger.info(f"Sending chat request: {user_message[:100]}...")

            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.config.deployment,
                messages=messages,
                max_completion_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            raw_response = response.choices[0].message.content.strip()
            logger.info(f"Received response ({len(raw_response)} chars)")

            # Parse JSON response
            try:
                parsed = self._parse_json_response(raw_response)
            except ValueError as e:
                # If JSON parsing fails, create a fallback response
                return AIResponse(
                    success=True,
                    message=raw_response,
                    operations=[],
                    raw_response=raw_response,
                    usage={
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    error=f"JSON parsing failed: {e}"
                )

            # Extract structured data
            operations = self._extract_operations(parsed)

            return AIResponse(
                success=True,
                message=parsed.get('message', ''),
                operations=operations,
                analysis=parsed.get('analysis'),
                raw_response=raw_response,
                usage={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            )

        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return AIResponse(
                success=False,
                message="",
                error=str(e)
            )

    def analyze_data_quality(self, df: pd.DataFrame) -> AIResponse:
        """
        Analyze data quality and suggest cleaning operations.

        Args:
            df: DataFrame to analyze

        Returns:
            AIResponse with analysis and recommended operations
        """
        prompt = """Analyze the data quality of this dataset and provide:
1. A summary of data quality issues found
2. Recommended cleaning operations in order of priority
3. Specific parameters for each recommended operation

Focus on:
- Missing values
- Potential duplicates
- Data type issues
- Outliers (if numeric columns exist)
- Formatting inconsistencies
"""
        return self.chat(prompt, df=df)

    def suggest_fix_for_column(
        self,
        df: pd.DataFrame,
        column: str,
        issue_type: str = "missing_values"
    ) -> AIResponse:
        """
        Get AI suggestion for fixing a specific column issue.

        Args:
            df: DataFrame containing the column
            column: Column name to fix
            issue_type: Type of issue (missing_values, outliers, format)

        Returns:
            AIResponse with suggested fix operation
        """
        if column not in df.columns:
            return AIResponse(
                success=False,
                message=f"Column '{column}' not found in dataset",
                error="Column not found"
            )

        prompt = f"""Suggest the best way to fix {issue_type} in the column '{column}'.

Consider:
- The data type of the column
- The distribution of existing values
- Best practices for this type of data

Provide a specific operation with parameters."""

        return self.chat(prompt, df=df)

    def execute_operation(
        self,
        df: pd.DataFrame,
        operation: AIOperation
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Execute an AI-suggested operation on the DataFrame.

        Args:
            df: DataFrame to modify
            operation: AIOperation to execute

        Returns:
            Tuple of (modified DataFrame, execution details)
        """
        result_df = df.copy()
        details = {
            "operation": operation.operation.value,
            "column": operation.column,
            "rows_affected": 0,
            "success": False
        }

        try:
            if operation.operation == OperationType.FILL_NULLS:
                col = operation.column
                if col and col in result_df.columns:
                    method = operation.parameters.get('method', 'mean')
                    original_nulls = result_df[col].isnull().sum()

                    if method == 'mean':
                        result_df[col] = result_df[col].fillna(result_df[col].mean())
                    elif method == 'median':
                        result_df[col] = result_df[col].fillna(result_df[col].median())
                    elif method == 'mode':
                        mode_val = result_df[col].mode()
                        if len(mode_val) > 0:
                            result_df[col] = result_df[col].fillna(mode_val[0])
                    elif method == 'constant':
                        value = operation.parameters.get('value', 0)
                        result_df[col] = result_df[col].fillna(value)
                    elif method == 'ffill':
                        result_df[col] = result_df[col].ffill()
                    elif method == 'bfill':
                        result_df[col] = result_df[col].bfill()

                    details["rows_affected"] = original_nulls - result_df[col].isnull().sum()
                    details["success"] = True

            elif operation.operation == OperationType.REMOVE_NULLS:
                original_len = len(result_df)
                col = operation.column
                if col and col in result_df.columns:
                    result_df = result_df.dropna(subset=[col])
                else:
                    result_df = result_df.dropna()
                details["rows_affected"] = original_len - len(result_df)
                details["success"] = True

            elif operation.operation == OperationType.REMOVE_DUPLICATES:
                original_len = len(result_df)
                result_df = result_df.drop_duplicates()
                details["rows_affected"] = original_len - len(result_df)
                details["success"] = True

            elif operation.operation == OperationType.REMOVE_COLUMN:
                col = operation.column
                if col and col in result_df.columns:
                    result_df = result_df.drop(columns=[col])
                    details["rows_affected"] = len(result_df)
                    details["success"] = True

            elif operation.operation == OperationType.RENAME_COLUMN:
                col = operation.column
                new_name = operation.parameters.get('new_name')
                if col and col in result_df.columns and new_name:
                    result_df = result_df.rename(columns={col: new_name})
                    details["new_column_name"] = new_name
                    details["success"] = True

            elif operation.operation == OperationType.CHANGE_CASE:
                col = operation.column
                case_type = operation.parameters.get('case_type', 'lower')
                if col and col in result_df.columns:
                    if case_type == 'upper':
                        result_df[col] = result_df[col].astype(str).str.upper()
                    elif case_type == 'lower':
                        result_df[col] = result_df[col].astype(str).str.lower()
                    elif case_type == 'title':
                        result_df[col] = result_df[col].astype(str).str.title()
                    details["rows_affected"] = len(result_df)
                    details["success"] = True

            elif operation.operation == OperationType.TRIM_WHITESPACE:
                col = operation.column
                if col and col in result_df.columns:
                    result_df[col] = result_df[col].astype(str).str.strip()
                    details["rows_affected"] = len(result_df)
                    details["success"] = True

            elif operation.operation == OperationType.FIND_REPLACE:
                col = operation.column
                find_val = operation.parameters.get('find_value')
                replace_val = operation.parameters.get('replace_value', '')
                if col and col in result_df.columns and find_val is not None:
                    mask = result_df[col] == find_val
                    result_df.loc[mask, col] = replace_val
                    details["rows_affected"] = mask.sum()
                    details["success"] = True

            elif operation.operation == OperationType.CONVERT_TYPE:
                col = operation.column
                target_type = operation.parameters.get('target_type')
                if col and col in result_df.columns and target_type:
                    if target_type == 'int':
                        result_df[col] = pd.to_numeric(result_df[col], errors='coerce').astype('Int64')
                    elif target_type == 'float':
                        result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
                    elif target_type == 'str':
                        result_df[col] = result_df[col].astype(str)
                    elif target_type == 'datetime':
                        result_df[col] = pd.to_datetime(result_df[col], errors='coerce')
                    details["rows_affected"] = len(result_df)
                    details["success"] = True

            elif operation.operation in (OperationType.ANALYZE, OperationType.NONE):
                details["success"] = True
                details["message"] = "No data modification performed"

        except Exception as e:
            details["error"] = str(e)
            details["success"] = False
            logger.error(f"Error executing operation: {e}")

        return result_df, details


def create_sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for testing"""
    import numpy as np
    np.random.seed(42)

    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', None, 'Eve', 'Frank', 'Grace', None, 'Ivan', 'Julia'],
        'age': [25, None, 35, 28, None, 45, 32, 29, None, 38],
        'salary': [50000, 60000, None, 55000, 65000, None, 58000, 62000, 70000, None],
        'department': ['IT', 'HR', 'IT', 'Finance', 'HR', 'IT', None, 'Finance', 'HR', 'IT'],
        'hire_date': pd.to_datetime(['2020-01-15', '2019-03-20', None, '2021-06-10',
                                      '2018-09-05', '2020-11-30', '2019-07-22', None,
                                      '2021-02-14', '2020-08-08'])
    })


# Export main classes
__all__ = [
    'AIChat',
    'AIChatConfig',
    'AIResponse',
    'AIOperation',
    'DataContext',
    'OperationType',
    'FillMethod',
    'create_sample_dataframe',
    'AZURE_OPENAI_AVAILABLE'
]
