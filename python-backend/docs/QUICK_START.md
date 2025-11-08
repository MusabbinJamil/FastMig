# Quick Start Guide - ETL Operations

## 🚀 5-Minute Setup

### Step 1: Start the Server (30 seconds)
```bash
cd python-backend
python server.py
```

**Expected Output:**
```
Starting FastMig Flask Backend Server...
Server will be available at http://localhost:5000

=== ETL Operations ===
  POST /etl/remove-nulls
  POST /etl/remove-duplicates
  ...
```

---

### Step 2: Test the Server (30 seconds)
Open a new terminal and run:
```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{"status": "healthy", "message": "FastMig backend is running"}
```

---

### Step 3: Run Automated Tests (2 minutes)
```bash
cd python-backend
python tests/test_etl_operations.py
```

**What it does:**
- Creates sample data
- Tests all 10 ETL operations
- Tests step recording & replay
- Verifies everything works

---

### Step 4: Try Your First Operation (2 minutes)

#### Create a test file:
```python
# save as test_quick.py
import requests
import pandas as pd

# Create sample data with issues
df = pd.DataFrame({
    'name': ['  John  ', 'JANE', None],
    'age': [25, None, 35],
})
df.to_csv('test.csv', index=False)

# Upload
with open('test.csv', 'rb') as f:
    r = requests.post('http://localhost:5000/upload', files={'file': f})
    print(f"Upload: {r.json()['message']}")

# Remove nulls
r = requests.post('http://localhost:5000/etl/remove-nulls', json={'how': 'any'})
print(f"Remove nulls: {r.json()['message']}")

# Trim whitespace
r = requests.post('http://localhost:5000/etl/trim-whitespace')
print(f"Trim: {r.json()['message']}")

# Export
r = requests.post('http://localhost:5000/export', json={'output_path': 'cleaned.csv'})
print(f"Export: {r.json()['message']}")

print("\n✓ Done! Check cleaned.csv")
```

#### Run it:
```bash
python test_quick.py
```

---

## 📚 What's Available

### 10 ETL Operations:
1. **Remove Nulls** - `/etl/remove-nulls`
2. **Remove Duplicates** - `/etl/remove-duplicates`
3. **Find & Replace** - `/etl/find-replace`
4. **Fill Nulls** - `/etl/fill-nulls`
5. **Rename Column** - `/etl/rename-column`
6. **Remove Column** - `/etl/remove-column`
7. **Filter Rows** - `/etl/filter-rows`
8. **Trim Whitespace** - `/etl/trim-whitespace`
9. **Change Case** - `/etl/change-case`
10. **Sort Data** - `/etl/sort-data`

### 7 Step Recording Operations:
1. **Start** - `/steps/start`
2. **Stop** - `/steps/stop`
3. **Get** - `/steps/get`
4. **Save** - `/steps/save`
5. **Load** - `/steps/load`
6. **Replay** - `/steps/replay`
7. **Clear** - `/steps/clear`

---

## 💡 Quick Examples

### Example 1: Clean Customer Data
```python
import requests

base = "http://localhost:5000"

# Upload
with open('customers.csv', 'rb') as f:
    requests.post(f"{base}/upload", files={'file': f})

# Clean
requests.post(f"{base}/etl/remove-nulls")
requests.post(f"{base}/etl/trim-whitespace")
requests.post(f"{base}/etl/remove-duplicates")

# Export
requests.post(f"{base}/export", json={"output_path": "clean_customers.csv"})
```

### Example 2: Record & Replay Pipeline
```python
# Start recording
requests.post(f"{base}/steps/start")

# Apply transformations
requests.post(f"{base}/etl/trim-whitespace")
requests.post(f"{base}/etl/change-case", 
              json={"column": "name", "case_type": "title"})

# Save pipeline
requests.post(f"{base}/steps/stop")
requests.post(f"{base}/steps/save", json={"name": "my_pipeline"})

# Later, use on new data
requests.post(f"{base}/steps/replay", json={"file_path": "new_data.csv"})
```

### Example 3: Find & Replace
```python
# Simple replacement
requests.post(f"{base}/etl/find-replace", json={
    "column": "status",
    "find_value": "old",
    "replace_value": "new"
})
```

---

## 🎯 Common Tasks

### Task 1: Remove Incomplete Records
```python
requests.post(f"{base}/etl/remove-nulls", json={"how": "any"})
```

### Task 2: Fill Missing Ages with Average
```python
requests.post(f"{base}/etl/fill-nulls", json={
    "column": "age",
    "method": "mean"
})
```

### Task 3: Filter Active Users Only
```python
requests.post(f"{base}/etl/filter-rows", json={
    "column": "status",
    "operator": "==",
    "value": "active"
})
```

### Task 4: Standardize Names
```python
requests.post(f"{base}/etl/trim-whitespace", json={"columns": ["name"]})
requests.post(f"{base}/etl/change-case", json={
    "column": "name",
    "case_type": "title"
})
```

---

## 📖 Read More

- **Quick Reference:** `docs/ETL_QUICK_REFERENCE.md` (1-page cheat sheet)
- **Complete Guide:** `docs/ETL_OPERATIONS_GUIDE.md` (full documentation)
- **Implementation:** `IMPLEMENTATION_SUMMARY.md` (technical details)
- **Update Info:** `ETL_UPDATE_README.md` (what's new)

---

## 🆘 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Or use a different port
python server.py  # Edit server.py to change port
```

### "No data loaded" error
```python
# Make sure to upload first
with open('data.csv', 'rb') as f:
    requests.post('http://localhost:5000/upload', files={'file': f})
```

### Tests fail
```bash
# Make sure server is running
python server.py

# In another terminal
python tests/test_etl_operations.py
```

---

## ✅ Checklist

- [ ] Server running at http://localhost:5000
- [ ] Health check returns success
- [ ] Automated tests pass
- [ ] Can upload a file
- [ ] Can apply an operation
- [ ] Can export results
- [ ] Step recording works
- [ ] Documentation reviewed

---

## 🎉 You're Ready!

You now have a **powerful ETL platform** ready to use. Start cleaning your data!

**Need help?** Check the documentation files listed above.

---

**Created:** November 8, 2025  
**Version:** 2.0.0
