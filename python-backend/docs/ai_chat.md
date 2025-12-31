# AI Chat Module Documentation

JSON-based LLM communication for FastMig data cleaning and migration.

## Overview

The AI Chat module provides structured JSON-based input/output for AI chat functionality, ensuring reliable parsing and consistent response formats. It communicates with Azure OpenAI using a strict JSON schema for both data context and operation responses.

## Installation

Ensure you have the required dependencies:

```bash
pip install openai pandas numpy
```

## Configuration

Set the following environment variables:

```bash
export AZURE_OPENAI_API_KEY=your_api_key
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
export AZURE_OPENAI_DEPLOYMENT=your_deployment_name
export AZURE_OPENAI_API_VERSION=2024-02-15-preview  # Optional
```

## Quick Start

### Basic Usage

```python
from ai_chat import AIChat, AIChatConfig, create_sample_dataframe

# Create configuration
config = AIChatConfig()

# Initialize AI Chat
chat = AIChat(config)

# Create or load your DataFrame
df = create_sample_dataframe()

# Send a message
response = chat.chat("What columns have missing values?", df=df)

# Access structured response
print(response.message)
for op in response.operations:
    print(f"Operation: {op.operation.value}, Column: {op.column}")
```

### Data Quality Analysis

```python
response = chat.analyze_data_quality(df)

if response.analysis:
    print("Issues found:", response.analysis.get('issues_found'))
    print("Recommendations:", response.analysis.get('recommendations'))
```

### Execute AI-Suggested Operations

```python
# Get suggestions
response = chat.chat("Fix the missing values in age column", df=df)

# Execute the first suggested operation
if response.operations:
    df_cleaned, details = chat.execute_operation(df, response.operations[0])
    print(f"Rows affected: {details['rows_affected']}")
```

## CLI Usage

The CLI tool provides an interactive way to test AI Chat functionality.

```bash
# Interactive mode with sample data
python ai_chat_cli.py

# Load a CSV file
python ai_chat_cli.py -f data.csv

# Quick data quality analysis
python ai_chat_cli.py --analyze

# Verbose mode with JSON output
python ai_chat_cli.py -v --json

# Run demo
python ai_chat_cli.py --demo

# Single message and exit
python ai_chat_cli.py -m "What's wrong with my data?"

# Show data context as JSON
python ai_chat_cli.py --show-context

# Auto-execute suggested operations
python ai_chat_cli.py -f data.csv --auto-execute
```

### Interactive Commands

When in interactive mode:

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/data` | Show data preview |
| `/context` | Show data context as JSON |
| `/analyze` | Run data quality analysis |
| `/execute` | Execute last suggested operations |
| `/clear` | Clear conversation history |
| `/quit` | Exit |

## API Reference

### Classes

#### `AIChatConfig`

Configuration for AI Chat.

```python
@dataclass
class AIChatConfig:
    api_key: Optional[str] = None        # Azure OpenAI API key
    endpoint: Optional[str] = None       # Azure OpenAI endpoint
    deployment: Optional[str] = None     # Model deployment name
    api_version: str = "2024-02-15-preview"
    max_tokens: int = 2000
    temperature: float = 0.1             # Low for consistent JSON
```

#### `AIChat`

Main chat handler with JSON-based communication.

**Methods:**

| Method | Description |
|--------|-------------|
| `chat(message, df, conversation_history, include_data_context)` | Send a chat message |
| `analyze_data_quality(df)` | Analyze data quality |
| `suggest_fix_for_column(df, column, issue_type)` | Get fix suggestion for a column |
| `execute_operation(df, operation)` | Execute an AI operation |
| `is_available()` | Check if AI is available |

#### `AIResponse`

Structured response from AI Chat.

```python
@dataclass
class AIResponse:
    success: bool                    # Whether the request succeeded
    message: str                     # Human-readable response
    operations: List[AIOperation]    # Suggested operations
    analysis: Optional[Dict]         # Analysis results
    raw_response: str               # Raw AI response
    usage: Dict[str, int]           # Token usage
    error: Optional[str]            # Error message if failed
```

#### `AIOperation`

Structured operation suggestion.

```python
@dataclass
class AIOperation:
    operation: OperationType         # Operation type
    column: Optional[str]            # Target column
    parameters: Dict[str, Any]       # Operation parameters
    description: str                 # What this operation does
    confidence: float                # Confidence score (0-1)
    reasoning: str                   # Why this is recommended
```

#### `DataContext`

Structured data context for AI.

```python
@dataclass
class DataContext:
    row_count: int
    column_count: int
    columns: List[Dict[str, Any]]
    sample_data: List[Dict[str, Any]]
    numeric_stats: Dict[str, Dict[str, float]]
    missing_values: Dict[str, Dict[str, Any]]
    data_types: Dict[str, str]
```

### Operation Types

Available operations in `OperationType` enum:

| Operation | Description | Parameters |
|-----------|-------------|------------|
| `fill_nulls` | Fill missing values | `method`: mean, median, mode, constant, ffill, bfill; `value`: for constant |
| `remove_nulls` | Remove rows with nulls | - |
| `remove_duplicates` | Remove duplicate rows | - |
| `remove_column` | Remove a column | - |
| `rename_column` | Rename a column | `new_name`: new column name |
| `change_case` | Change text case | `case_type`: upper, lower, title |
| `find_replace` | Find and replace | `find_value`, `replace_value` |
| `filter_rows` | Filter rows | `operator`, `filter_value` |
| `trim_whitespace` | Trim whitespace | - |
| `convert_type` | Convert data type | `target_type`: int, float, str, datetime |
| `analyze` | Analyze without changes | - |
| `none` | No operation | - |

## JSON Communication Format

### Data Context (Sent to AI)

```json
{
  "row_count": 100,
  "column_count": 5,
  "columns": [
    {
      "name": "age",
      "dtype": "float64",
      "null_count": 5,
      "null_percentage": 5.0,
      "unique_count": 45
    }
  ],
  "sample_data": [
    {"name": "Alice", "age": 25, "salary": 50000}
  ],
  "numeric_stats": {
    "age": {"mean": 32.5, "std": 10.2, "min": 18, "max": 65, "median": 30}
  },
  "missing_values": {
    "age": {"count": 5, "percentage": 5.0}
  },
  "data_types": {
    "name": "object",
    "age": "float64"
  }
}
```

### AI Response Format

```json
{
  "message": "I recommend filling missing values in the age column with the mean value.",
  "operations": [
    {
      "operation": "fill_nulls",
      "column": "age",
      "parameters": {"method": "mean"},
      "description": "Fill missing ages with mean value (32.5)",
      "confidence": 0.95,
      "reasoning": "Mean is appropriate for normally distributed numeric data"
    }
  ],
  "analysis": {
    "summary": "Dataset has minor quality issues",
    "issues_found": [
      "5% missing values in age column",
      "No duplicates detected"
    ],
    "recommendations": [
      "Fill missing ages with mean or median",
      "Consider removing outliers above 3 standard deviations"
    ]
  }
}
```

## Testing

Run the comprehensive test suite:

```bash
# Basic output
python test_ai_chat.py

# Verbose output with detailed information
python test_ai_chat.py -v
python test_ai_chat.py --verbose
```

### Test Classes

| Class | Description |
|-------|-------------|
| `TestAIChatConfig` | Configuration validation |
| `TestDataContext` | DataFrame to JSON conversion |
| `TestJSONParsing` | JSON response parsing |
| `TestAIOperation` | Operation dataclass |
| `TestAIResponse` | Response dataclass |
| `TestOperationExecution` | Operation execution |
| `TestAIChatIntegration` | Mocked API integration |
| `TestEdgeCases` | Edge cases and errors |
| `TestSampleData` | Sample data creation |
| `TestOperationTypes` | Operation type enum |

## Server Integration

The `/openai/chat` endpoint uses this module for JSON-based communication:

### Request

```json
{
  "message": "What columns have missing values?",
  "include_data_context": true,
  "conversation_history": [
    {"role": "user", "content": "previous message"},
    {"role": "assistant", "content": "previous response"}
  ]
}
```

### Response

```json
{
  "success": true,
  "response": "AI message text",
  "suggested_actions": [...],
  "operations": [
    {
      "operation": "fill_nulls",
      "column": "age",
      "parameters": {"method": "mean"},
      "description": "Fill missing ages",
      "confidence": 0.95,
      "reasoning": "Mean is appropriate"
    }
  ],
  "analysis": {...},
  "has_data_context": true,
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

## Error Handling

The module handles various edge cases:

- **Missing API credentials**: Returns validation errors
- **Invalid JSON responses**: Attempts cleanup (markdown blocks, smart quotes, trailing commas)
- **Unknown operation types**: Defaults to `OperationType.NONE`
- **Invalid columns**: Operations fail gracefully without crashing
- **Empty DataFrames**: Handled correctly with zero counts

## Best Practices

1. **Always validate config** before creating AIChat instance
2. **Check `response.success`** before accessing operations
3. **Preview operations** before executing on real data
4. **Use conversation history** for context-aware responses
5. **Set low temperature** (0.1) for consistent JSON output

## Files

| File | Description |
|------|-------------|
| `ai_chat.py` | Main module with all classes |
| `ai_chat_cli.py` | CLI testing tool |
| `test_ai_chat.py` | Comprehensive test suite |
| `docs/ai_chat.md` | This documentation |
