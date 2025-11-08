# ETL Operations Guide

## Overview
FastMig now includes a comprehensive suite of ETL (Extract, Transform, Load). These operations allow you to clean, transform, and prepare your data before migration.

## Table of Contents
1. [Data Cleaning Operations](#data-cleaning-operations)
2. [Data Transformation Operations](#data-transformation-operations)
3. [Step Recording & Replay](#step-recording--replay)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)

---

## Data Cleaning Operations

### Remove Null Rows
Remove rows containing null/missing values.

**Endpoint:** `POST /etl/remove-nulls`

**Parameters:**
```json
{
  "columns": ["col1", "col2"],  // Optional: specific columns (null = all)
  "how": "any"                  // "any" or "all"
}
```

**Use Cases:**
- Remove incomplete records
- Clean data before analysis
- Ensure data quality

---

### Remove Duplicate Rows
Remove duplicate rows from the dataset.

**Endpoint:** `POST /etl/remove-duplicates`

**Parameters:**
```json
{
  "columns": ["id", "name"],    // Optional: columns to check (null = all)
  "keep": "first"               // "first", "last", or false
}
```

**Use Cases:**
- Remove redundant data
- Prevent data duplication
- Clean merged datasets

---

### Fill Null Values
Fill missing values using various strategies.

**Endpoint:** `POST /etl/fill-nulls`

**Parameters:**
```json
{
  "column": "age",
  "method": "mean",             // "forward", "backward", "mean", "median", "mode", "constant"
  "value": 0                    // Required when method="constant"
}
```

**Fill Methods:**
- `forward`: Forward fill (use previous value)
- `backward`: Backward fill (use next value)
- `mean`: Fill with column mean
- `median`: Fill with column median
- `mode`: Fill with column mode
- `constant`: Fill with specified value

---

### Trim Whitespace
Remove leading and trailing whitespace from text columns.

**Endpoint:** `POST /etl/trim-whitespace`

**Parameters:**
```json
{
  "columns": ["name", "address"]  // Optional: specific columns (null = all string columns)
}
```

**Use Cases:**
- Clean user input
- Standardize text data
- Fix copy-paste errors

---

## Data Transformation Operations

### Find and Replace
Find and replace values in a column.

**Endpoint:** `POST /etl/find-replace`

**Parameters:**
```json
{
  "column": "status",
  "find_value": "old_value",
  "replace_value": "new_value",
  "use_regex": false            // Optional: use regex pattern matching
}
```

**Examples:**
- Replace "N/A" with null
- Standardize status codes
- Fix data entry errors
- Regex replacement: `"find_value": "\\d{3}-\\d{4}"` to match phone patterns

---

### Rename Column
Rename a column in the dataset.

**Endpoint:** `POST /etl/rename-column`

**Parameters:**
```json
{
  "old_name": "old_column_name",
  "new_name": "new_column_name"
}
```

---

### Remove Column
Remove a column from the dataset.

**Endpoint:** `POST /etl/remove-column`

**Parameters:**
```json
{
  "column": "unwanted_column"
}
```

---

### Filter Rows
Filter rows based on a condition.

**Endpoint:** `POST /etl/filter-rows`

**Parameters:**
```json
{
  "column": "age",
  "operator": ">",              // "==", "!=", ">", "<", ">=", "<=", "contains", "startswith", "endswith"
  "value": 18
}
```

**Operators:**
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Text matching: `contains`, `startswith`, `endswith`

**Examples:**
```json
// Keep only adults
{"column": "age", "operator": ">=", "value": 18}

// Filter by status
{"column": "status", "operator": "==", "value": "active"}

// Find emails
{"column": "email", "operator": "contains", "value": "@gmail.com"}
```

---

### Change Case
Change the case of text in a column.

**Endpoint:** `POST /etl/change-case`

**Parameters:**
```json
{
  "column": "name",
  "case_type": "title"          // "upper", "lower", "title", "capitalize"
}
```

**Case Types:**
- `upper`: UPPERCASE
- `lower`: lowercase
- `title`: Title Case
- `capitalize`: Capitalize first letter

---

### Sort Data
Sort data by one or more columns.

**Endpoint:** `POST /etl/sort-data`

**Parameters:**
```json
{
  "columns": ["last_name", "first_name"],
  "ascending": true             // true or false
}
```

---

## Step Recording & Replay

### Overview
The Step Recording feature allows you to record a sequence of transformations and replay them on different datasets.

### Start Recording
**Endpoint:** `POST /steps/start`

**Response:**
```json
{
  "success": true,
  "message": "Started recording steps",
  "is_recording": true
}
```

### Stop Recording
**Endpoint:** `POST /steps/stop`

**Response:**
```json
{
  "success": true,
  "message": "Stopped recording steps",
  "is_recording": false,
  "steps_count": 5
}
```

### Get Recorded Steps
**Endpoint:** `GET /steps/get`

**Response:**
```json
{
  "success": true,
  "steps": [
    {
      "timestamp": "2025-11-08T10:30:00",
      "operation": "remove_null_rows",
      "parameters": {"columns": null, "how": "any"},
      "report": {"rows_removed": 10}
    }
  ],
  "steps_count": 5,
  "is_recording": false
}
```

### Save Steps
**Endpoint:** `POST /steps/save`

**Parameters:**
```json
{
  "name": "my_transformation_steps"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Saved 5 steps to recordings/my_transformation_steps.json",
  "file_path": "recordings/my_transformation_steps.json",
  "steps_count": 5
}
```

### Load Steps
**Endpoint:** `POST /steps/load`

**Parameters:**
```json
{
  "file_path": "recordings/my_transformation_steps.json"
}
```

### Replay Steps
**Endpoint:** `POST /steps/replay`

**Parameters:**
```json
{
  "file_path": "path/to/new_data.csv"  // Optional: omit to use currently loaded data
}
```

**Response:**
```json
{
  "success": true,
  "data": [[...], [...], ...],
  "columns": ["id", "name", "age"],
  "shape": [1000, 3],
  "reports": [
    {"operation": "remove_null_rows", "rows_removed": 10},
    {"operation": "find_replace", "replacements_made": 5}
  ],
  "steps_applied": 5,
  "message": "Successfully applied 5 steps"
}
```

---

## API Reference

### Common Response Format

All ETL operations return a consistent response format:

```json
{
  "success": true,
  "data": [[...], [...], ...],          // First 100 rows
  "columns": ["col1", "col2", ...],
  "shape": [rows, columns],
  "report": {
    "operation": "operation_name",
    "rows_removed": 10,
    "modifications_made": 5,
    ...
  },
  "message": "Operation completed successfully"
}
```

### Error Response Format

```json
{
  "error": "Error message describing what went wrong"
}
```

---

## Usage Examples

### Example 1: Basic Data Cleaning Pipeline

```python
import requests

base_url = "http://localhost:5000"

# 1. Upload data
with open('data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{base_url}/upload", files=files)

# 2. Start recording steps
requests.post(f"{base_url}/steps/start")

# 3. Remove null rows
requests.post(f"{base_url}/etl/remove-nulls", json={
    "how": "any"
})

# 4. Remove duplicates
requests.post(f"{base_url}/etl/remove-duplicates", json={
    "keep": "first"
})

# 5. Trim whitespace
requests.post(f"{base_url}/etl/trim-whitespace")

# 6. Stop recording
requests.post(f"{base_url}/steps/stop")

# 7. Save steps for reuse
requests.post(f"{base_url}/steps/save", json={
    "name": "basic_cleaning"
})

# 8. Export cleaned data
requests.post(f"{base_url}/export", json={
    "output_path": "cleaned_data.csv"
})
```

### Example 2: Text Data Standardization

```python
# Start recording
requests.post(f"{base_url}/steps/start")

# Change names to title case
requests.post(f"{base_url}/etl/change-case", json={
    "column": "name",
    "case_type": "title"
})

# Trim whitespace
requests.post(f"{base_url}/etl/trim-whitespace", json={
    "columns": ["name", "address", "city"]
})

# Standardize country codes
requests.post(f"{base_url}/etl/find-replace", json={
    "column": "country",
    "find_value": "USA",
    "replace_value": "United States"
})

# Stop and save
requests.post(f"{base_url}/steps/stop")
requests.post(f"{base_url}/steps/save", json={"name": "text_standardization"})
```

### Example 3: Data Filtering

```python
# Filter active users over 18
requests.post(f"{base_url}/etl/filter-rows", json={
    "column": "age",
    "operator": ">=",
    "value": 18
})

requests.post(f"{base_url}/etl/filter-rows", json={
    "column": "status",
    "operator": "==",
    "value": "active"
})

# Sort by last name
requests.post(f"{base_url}/etl/sort-data", json={
    "columns": ["last_name", "first_name"],
    "ascending": true
})
```

### Example 4: Replay Steps on New Data

```python
# Load previously saved steps
requests.post(f"{base_url}/steps/load", json={
    "file_path": "recordings/basic_cleaning.json"
})

# Replay on new data
requests.post(f"{base_url}/steps/replay", json={
    "file_path": "new_data.csv"
})
```

---

## Best Practices

1. **Always Start with Recording**: Start recording steps before performing transformations if you plan to reuse them.

2. **Test Before Replay**: Test your recorded steps on a small dataset before applying to large production data.

3. **Name Steps Descriptively**: Use clear, descriptive names when saving steps (e.g., "customer_data_cleaning", "sales_standardization").

4. **Document Your Steps**: Keep a record of what each saved step file does.

5. **Check Reports**: Always review the operation reports to understand what changed.

6. **Use Appropriate Fill Methods**: Choose the right fill method for null values:
   - Use `mean` or `median` for numeric data
   - Use `mode` for categorical data
   - Use `forward`/`backward` for time-series data

7. **Validate After Each Operation**: Check the data shape and sample rows after each operation.

8. **Keep Backups**: The system doesn't modify the original uploaded file - transformed data is in memory until exported.

## Troubleshooting

### Common Issues

**Issue:** "No data loaded" error
- **Solution:** Upload a file first using `/upload` endpoint

**Issue:** "Column not found" error
- **Solution:** Check column names using `/columns` endpoint

**Issue:** Steps replay fails
- **Solution:** Ensure the new data has the same column structure as the original

**Issue:** Null values remain after filling
- **Solution:** Check the fill method and ensure the column has valid values to fill from

---

## Next Steps

- Explore the [Data Fitness & Evolutionary Cleaning Guide](EVOLUTIONARY_CLEANING_GUIDE.md)
- Learn about [Advanced Column Conversions](QUICK_REFERENCE.md)
- Check the [API Architecture](ARCHITECTURE.md)
