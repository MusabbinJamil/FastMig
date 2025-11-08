# ETL Operations Quick Reference Card

## 🚀 Quick Start

```bash
# Start the server
python server.py

# Test the new features
python tests/test_etl_operations.py
```

---

## 📋 Data Cleaning Operations

| Operation | Endpoint | Key Parameters |
|-----------|----------|----------------|
| **Remove Nulls** | `POST /etl/remove-nulls` | `columns`, `how` (any/all) |
| **Remove Duplicates** | `POST /etl/remove-duplicates` | `columns`, `keep` (first/last/false) |
| **Fill Nulls** | `POST /etl/fill-nulls` | `column`, `method`, `value` |
| **Trim Whitespace** | `POST /etl/trim-whitespace` | `columns` (optional) |

---

## 🔄 Data Transformation Operations

| Operation | Endpoint | Key Parameters |
|-----------|----------|----------------|
| **Find & Replace** | `POST /etl/find-replace` | `column`, `find_value`, `replace_value`, `use_regex` |
| **Rename Column** | `POST /etl/rename-column` | `old_name`, `new_name` |
| **Remove Column** | `POST /etl/remove-column` | `column` |
| **Filter Rows** | `POST /etl/filter-rows` | `column`, `operator`, `value` |
| **Change Case** | `POST /etl/change-case` | `column`, `case_type` |
| **Sort Data** | `POST /etl/sort-data` | `columns`, `ascending` |

---

## 📹 Step Recording

| Action | Endpoint | Purpose |
|--------|----------|---------|
| **Start** | `POST /steps/start` | Begin recording transformations |
| **Stop** | `POST /steps/stop` | Stop recording |
| **Get** | `GET /steps/get` | View recorded steps |
| **Save** | `POST /steps/save` | Save steps to file |
| **Load** | `POST /steps/load` | Load steps from file |
| **Replay** | `POST /steps/replay` | Apply steps to data |
| **Clear** | `POST /steps/clear` | Clear recorded steps |

---

## 💡 Common Use Cases

### Use Case 1: Clean Customer Data
```python
# 1. Remove rows with missing emails
POST /etl/remove-nulls
{"columns": ["email"], "how": "any"}

# 2. Trim whitespace from names
POST /etl/trim-whitespace
{"columns": ["first_name", "last_name"]}

# 3. Standardize to title case
POST /etl/change-case
{"column": "first_name", "case_type": "title"}

# 4. Remove duplicates
POST /etl/remove-duplicates
{"keep": "first"}
```

### Use Case 2: Standardize Product Codes
```python
# 1. Change to uppercase
POST /etl/change-case
{"column": "product_code", "case_type": "upper"}

# 2. Replace old codes
POST /etl/find-replace
{"column": "product_code", "find_value": "OLD-", "replace_value": "NEW-"}

# 3. Remove invalid products
POST /etl/filter-rows
{"column": "status", "operator": "!=", "value": "invalid"}
```

### Use Case 3: Prepare Sales Data
```python
# 1. Fill missing amounts with 0
POST /etl/fill-nulls
{"column": "amount", "method": "constant", "value": 0}

# 2. Filter this year's sales
POST /etl/filter-rows
{"column": "year", "operator": "==", "value": 2025}

# 3. Sort by date
POST /etl/sort-data
{"columns": ["sale_date"], "ascending": false}
```

---

## 🎯 Fill Methods Quick Reference

| Method | Best For | Example |
|--------|----------|---------|
| `forward` | Time series (use previous) | Stock prices, sensor data |
| `backward` | Time series (use next) | Forecasted values |
| `mean` | Numeric outliers | Age, salary, scores |
| `median` | Numeric with outliers | Income, price |
| `mode` | Categorical | Status, category, type |
| `constant` | Default values | 0, "Unknown", "N/A" |

---

## 🔍 Filter Operators Quick Reference

| Operator | Description | Example Value |
|----------|-------------|---------------|
| `==` | Equals | `"active"`, `25` |
| `!=` | Not equals | `"deleted"` |
| `>` | Greater than | `18` |
| `<` | Less than | `100` |
| `>=` | Greater or equal | `21` |
| `<=` | Less or equal | `65` |
| `contains` | Text contains | `"@gmail.com"` |
| `startswith` | Text starts with | `"USD"` |
| `endswith` | Text ends with | `".com"` |

---

## 📝 Step Recording Workflow

```
1. Upload Data          →  POST /upload
2. Start Recording      →  POST /steps/start
3. Apply Transformations →  POST /etl/[operation]
4. Stop Recording       →  POST /steps/stop
5. Save Steps           →  POST /steps/save {"name": "my_pipeline"}
6. Replay Later         →  POST /steps/replay {"file_path": "new.csv"}
```

---

## ⚡ Quick Tips

1. **Always start recording before transformations** if you plan to reuse them
2. **Test on small datasets first** before applying to production data
3. **Use descriptive names** when saving steps
4. **Check the report** after each operation to verify changes
5. **Keep backups** - original files are never modified
6. **Chain operations** - output of one becomes input to next

---

## 🔗 Related Endpoints

| Category | Endpoint | Purpose |
|----------|----------|---------|
| **Core** | `POST /upload` | Upload data file |
| **Core** | `GET /columns` | Get column info |
| **Core** | `POST /export` | Export processed data |
| **Core** | `GET /status` | Check system status |
| **AI** | `POST /fitness/evaluate` | Check data quality |
| **AI** | `POST /clean/evolutionary` | AI-powered cleaning |

---

## 📊 Example: Complete Pipeline

```python
import requests

base_url = "http://localhost:5000"

# 1. Upload
with open('data.csv', 'rb') as f:
    requests.post(f"{base_url}/upload", files={'file': f})

# 2. Start recording
requests.post(f"{base_url}/steps/start")

# 3. Clean data
requests.post(f"{base_url}/etl/remove-nulls", json={"how": "any"})
requests.post(f"{base_url}/etl/trim-whitespace")
requests.post(f"{base_url}/etl/remove-duplicates", json={"keep": "first"})

# 4. Transform
requests.post(f"{base_url}/etl/change-case", 
              json={"column": "name", "case_type": "title"})
requests.post(f"{base_url}/etl/sort-data", 
              json={"columns": ["name"], "ascending": True})

# 5. Stop & Save
requests.post(f"{base_url}/steps/stop")
requests.post(f"{base_url}/steps/save", json={"name": "cleaning_pipeline"})

# 6. Export
requests.post(f"{base_url}/export", json={"output_path": "cleaned.csv"})

# 7. Reuse on new data
requests.post(f"{base_url}/steps/replay", json={"file_path": "new_data.csv"})
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No data loaded" | Upload file first with `/upload` |
| "Column not found" | Check available columns with `/columns` |
| Steps won't replay | Ensure new data has same column structure |
| Nulls remain after fill | Check fill method is appropriate for data type |
| Recording not working | Call `/steps/start` before operations |

---

## 📚 Full Documentation

- **Complete Guide:** `docs/ETL_OPERATIONS_GUIDE.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **API Reference:** See server startup logs
- **Test Suite:** `tests/test_etl_operations.py`

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-08
