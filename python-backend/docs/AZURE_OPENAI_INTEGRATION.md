# Azure OpenAI Integration - Backend

This document describes the Azure OpenAI chat integration in the FastMig Python backend.

## Overview

The Azure OpenAI integration allows users to interact with their data using natural language. Users can ask questions about their dataset, get AI-powered analysis, and execute data modification commands through conversational prompts.

## Configuration

### Environment Variables

Create a `.env` file in the `python-backend/` directory with the following variables:

```bash
# Required
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# Optional (defaults to 2024-02-15-preview)
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Getting Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Create an Azure OpenAI resource
3. Deploy a model (e.g., GPT-4, GPT-3.5-turbo)
4. Copy the API key and endpoint from the resource
5. Note the deployment name you created

## API Endpoints

### GET `/openai/status`

Check if Azure OpenAI is configured and available.

**Response:**
```json
{
  "available": true,
  "configured": true,
  "message": "Azure OpenAI is configured and ready"
}
```

### POST `/openai/chat`

Send a chat message to Azure OpenAI with optional data context.

**Request:**
```json
{
  "message": "What columns have missing values?",
  "include_data_context": true,
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "Based on the data, the 'age' column has 15 missing values...",
  "suggested_actions": [
    {
      "type": "fill_nulls",
      "column": "age",
      "method": "mean"
    }
  ]
}
```

### POST `/openai/modify-data`

Execute a natural language data modification command.

**Request:**
```json
{
  "command": "Fill missing values in the age column with the average",
  "preview": false
}
```

**Response:**
```json
{
  "success": true,
  "operation": "fill_nulls",
  "description": "Filled 15 missing values in 'age' column with mean (34.5)",
  "column": "age",
  "parameters": {
    "method": "mean",
    "value": 34.5
  },
  "data": [...],
  "columns": ["id", "name", "age", "email"],
  "shape": [100, 4],
  "message": "Successfully modified 15 cells"
}
```

### POST `/openai/analyze`

Get AI analysis of the current dataset.

**Request:**
```json
{
  "analysis_type": "quality_report"
}
```

**Analysis Types:**
- `summary` - General dataset summary
- `quality_report` - Data quality assessment
- `recommendations` - Improvement suggestions

**Response:**
```json
{
  "success": true,
  "analysis_type": "quality_report",
  "analysis": "# Data Quality Report\n\n## Overview\n..."
}
```

## Data Context

When `include_data_context` is true, the following information is sent to the AI:

```python
{
    "columns": ["id", "name", "age", "email"],
    "dtypes": {"id": "int64", "name": "object", ...},
    "shape": [100, 4],
    "sample_rows": [...],  # First 5 rows
    "statistics": {
        "age": {"mean": 34.5, "std": 12.3, ...},
        ...
    },
    "null_counts": {"age": 15, "email": 3},
    "error_cells_count": 5
}
```

## Supported Operations

The AI can understand and execute these data operations:

| Command Pattern | Operation | Example |
|-----------------|-----------|---------|
| "Fill missing values in X with Y" | `fill_nulls` | "Fill missing values in age with mean" |
| "Remove rows with null values" | `remove_nulls` | "Remove rows with null values in email" |
| "Remove duplicate rows" | `remove_duplicates` | "Remove duplicate rows" |
| "Remove column X" | `remove_column` | "Remove the temp_id column" |
| "Rename column X to Y" | `rename_column` | "Rename col1 to user_id" |
| "Convert X to uppercase" | `transform_column` | "Convert names to uppercase" |
| "Filter rows where X > Y" | `filter_rows` | "Filter rows where age > 18" |

## Error Handling

All endpoints return appropriate error responses:

```json
{
  "error": "Azure OpenAI is not configured",
  "details": "Missing AZURE_OPENAI_API_KEY environment variable"
}
```

Common error codes:
- `400` - Bad request (missing parameters)
- `500` - Server error (API failure)
- `503` - Service unavailable (not configured)

## Implementation Details

### Files

| File | Description |
|------|-------------|
| `server.py` | Contains all OpenAI endpoints and helper functions |
| `.env` | Environment variables (create from `.env.example`) |
| `.env.example` | Template for environment variables |

### Helper Functions

```python
# Get configured Azure OpenAI client
def get_azure_openai_client():
    """Returns configured AzureOpenAI client or None if not configured"""

# Build data context for AI
def build_data_context(df):
    """Creates a summary of the dataframe for AI context"""

# Parse AI modification commands
def parse_ai_modification_command(command):
    """Parses natural language command to operation parameters"""
```

## Security Considerations

1. **API Keys**: Never commit `.env` files to version control
2. **Data Privacy**: Be aware that data context is sent to Azure OpenAI
3. **Rate Limits**: Azure OpenAI has rate limits; handle appropriately
4. **Input Validation**: All user inputs are validated before processing

## Dependencies

Add to `requirements.txt`:
```
openai>=1.0.0
python-dotenv>=1.0.0
```

## Testing

Test the integration:

```bash
# Check status
curl http://localhost:5000/openai/status

# Send a chat message
curl -X POST http://localhost:5000/openai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Describe the dataset", "include_data_context": true}'
```

## Troubleshooting

### "Azure OpenAI is not configured"
- Ensure `.env` file exists in `python-backend/`
- Check that all required environment variables are set
- Restart the Flask server after adding `.env`

### "Failed to connect to Azure OpenAI"
- Verify the endpoint URL is correct
- Check that the API key is valid
- Ensure the deployment name matches your Azure deployment

### "Model not found"
- The deployment name must match exactly
- Check Azure Portal for the correct deployment name
