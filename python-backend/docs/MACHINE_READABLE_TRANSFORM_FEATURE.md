# Machine Readable Transform Feature

## Overview
Added comprehensive machine-readable transform features to FastMig backend that enable encoding of categorical data for machine learning models.

## New Features Added

### 1. Machine Readable Transform Endpoints (server.py)

#### **POST /transform/label-encode**
Label encode categorical columns to convert them to numeric format.

**Request Body:**
```json
{
  "columns": ["column1", "column2"],  // or null for all categorical columns
  "save_mapping": true                // whether to save encoding mapping
}
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "columns": [...],
  "shape": [rows, cols],
  "report": {
    "columns_encoded": ["column1", "column2"],
    "mappings": {
      "column1": {"Category A": 0, "Category B": 1},
      "column2": {...}
    },
    "total_encoded": 2
  },
  "message": "Successfully label encoded 2 columns"
}
```

**Features:**
- Automatically detects categorical columns if none specified
- Handles NaN values gracefully
- Stores encoding mappings for reverse transformation
- Skips already numeric columns
- Integrates with step recording

---

#### **POST /transform/one-hot-encode**
One-hot encode categorical columns (creates binary columns for each category).

**Request Body:**
```json
{
  "columns": ["column1", "column2"],  // or null for all categorical columns
  "drop_first": false,                // drop first category to avoid multicollinearity
  "prefix_sep": "_"                   // separator between column name and category
}
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "columns": [...],
  "shape": [rows, cols],
  "report": {
    "columns_encoded": ["column1"],
    "new_columns_created": ["column1_A", "column1_B", "column1_C"],
    "total_encoded": 1,
    "total_new_columns": 3
  },
  "message": "Successfully one-hot encoded 1 columns, created 3 new columns"
}
```

**Features:**
- Creates binary columns for each unique category value
- Option to drop first category to prevent multicollinearity
- Customizable separator for new column names
- Removes original categorical column after encoding
- Works seamlessly with step recording

---

#### **POST /transform/reverse-label-encode**
Reverse label encoding to get back original categorical values.

**Request Body:**
```json
{
  "columns": ["column1", "column2"]  // or null for all previously encoded columns
}
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "columns": [...],
  "shape": [rows, cols],
  "report": {
    "columns_decoded": ["column1", "column2"],
    "total_decoded": 2
  },
  "message": "Successfully reversed label encoding for 2 columns"
}
```

**Features:**
- Uses saved encoding mappings from label-encode
- Restores original categorical values
- Handles NaN values appropriately

---

### 2. Enhanced Evolutionary Algorithm Logging (data_fitness.py)

All evolutionary algorithms now provide detailed step-by-step logging:

#### **Genetic Algorithm (GA)**
```
🧬 Generation 1/100
   📊 Evaluating fitness for 50 individuals...
   ✨ New best fitness found: 0.8523
   🎯 Performing tournament selection...
   🔀 Performing crossover (rate=0.8)...
   🔀 Crossovers performed: 18
   🧪 Performing mutation (rate=0.1)...
   🧪 Mutations performed: 12
Gen 20: Best=0.8956, Avg=0.7834, Crossovers=19, Mutations=11
```

**Logs Include:**
- Generation number and progress
- Fitness evaluation counts
- Best fitness discoveries
- Selection operations
- Crossover operations with count
- Mutation operations with count
- Progress summaries every 20 generations

---

#### **Particle Swarm Optimization (PSO)**
```
🐝 Iteration 1/100
   🌀 Updating velocity for particle 1/30
   📍 Updating position for particle 1
   📊 Evaluating fitness for particle 1
   ⭐ Particle 5 found new personal best: 0.7654
   🏆 New global best found: 0.8234
Iter 20: Global=0.8956, Avg=0.7523, PersonalUpdates=12, GlobalUpdates=3
```

**Logs Include:**
- Iteration number and progress
- Velocity updates for each particle
- Position updates
- Fitness evaluations
- Personal best updates with count
- Global best discoveries with count
- Summary every 20 iterations

---

#### **Differential Evolution (DE)**
```
🧪 Running scipy.differential_evolution...
   Config: maxiter=100, popsize=15
   🎯 Bounds set: [0.00, 100.00]
   📊 Evaluation 50: fitness=0.7234
   📊 Evaluation 100: fitness=0.8123
✅ DE converged after 234 evaluations
✓ 'column_name' completed: fitness=0.8956, evaluations=234
```

**Logs Include:**
- Configuration parameters
- Bounds information
- Periodic fitness evaluations (every 50)
- Total evaluations count
- Final convergence metrics

---

#### **Evolution Strategy (ES)**
```
🎯 Generation 1/100
   👶 Generating 45 offspring from 15 parents
   ✓ 45 offspring generated with σ=0.0950
   📊 Evaluating 45 offspring...
   ✨ New best fitness found: 0.8234
   🏆 Selecting 15 best offspring as new parents
Gen 20: Best=0.8956, Avg=0.7612, σ=0.0800
```

**Logs Include:**
- Generation progress
- Offspring generation with mutation rate (σ)
- Fitness evaluation counts
- Best solution discoveries
- Parent selection process
- Self-adaptive mutation rate tracking

---

## Benefits

### Machine Readable Transforms
1. **Flexibility**: Support for both label encoding and one-hot encoding
2. **Automation**: Auto-detects categorical columns
3. **Reversibility**: Can reverse label encoding to original values
4. **Integration**: Works with step recording/replay feature
5. **Robustness**: Handles missing values and edge cases

### Enhanced Logging
1. **Transparency**: See exactly what each algorithm is doing
2. **Debugging**: Easier to troubleshoot and optimize
3. **Progress Tracking**: Real-time feedback on algorithm progress
4. **Performance Metrics**: Track crossovers, mutations, evaluations
5. **Educational**: Learn how evolutionary algorithms work

---

## Usage Examples

### Example 1: Label Encode All Categorical Columns
```python
import requests

# Upload data first
files = {'file': open('data.csv', 'rb')}
upload_response = requests.post('http://localhost:5000/upload', files=files)

# Label encode all categorical columns
encode_response = requests.post('http://localhost:5000/transform/label-encode', 
    json={
        "columns": None,  # Auto-detect all categorical
        "save_mapping": True
    })

print(encode_response.json()['report'])
```

### Example 2: One-Hot Encode Specific Columns
```python
# One-hot encode specific columns with custom separator
encode_response = requests.post('http://localhost:5000/transform/one-hot-encode',
    json={
        "columns": ["Country", "Gender"],
        "drop_first": True,  # Avoid multicollinearity
        "prefix_sep": "__"
    })

print(f"Created {len(encode_response.json()['report']['new_columns_created'])} new columns")
```

### Example 3: Reverse Label Encoding
```python
# Reverse the encoding to get original values
reverse_response = requests.post('http://localhost:5000/transform/reverse-label-encode',
    json={
        "columns": None  # Reverse all encoded columns
    })

print(reverse_response.json()['message'])
```

### Example 4: Run Evolutionary Cleaning with Detailed Logs
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run genetic algorithm cleaning
clean_response = requests.post('http://localhost:5000/clean/evolutionary',
    json={
        "method": "ga",
        "track_modifications": True,
        "parameters": {
            "population_size": 50,
            "generations": 100,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8
        }
    })

# Check server logs to see detailed step-by-step progress
```

---

## Server Startup Messages

The server now displays the new endpoints on startup:

```
=== Machine Readable Transform (Encoding) ===
  POST /transform/label-encode         - Label encode categorical columns
  POST /transform/one-hot-encode       - One-hot encode categorical columns
  POST /transform/reverse-label-encode - Reverse label encoding
```

---

## Technical Implementation

### Dependencies Added
- `sklearn.preprocessing.LabelEncoder` - For label encoding
- `sklearn.preprocessing.OneHotEncoder` - For one-hot encoding
- `numpy` - For array operations

### Data Structures
- `current_data['label_encoders']` - Stores encoder objects for reverse transformation
- Enhanced logging with emoji indicators for better readability
- Detailed progress tracking in all evolutionary algorithms

---

## Testing

To test the new features:

1. **Start the backend server:**
   ```bash
   python python-backend/server.py
   ```

2. **Upload a CSV file with categorical columns**

3. **Test label encoding:**
   ```bash
   curl -X POST http://localhost:5000/transform/label-encode \
     -H "Content-Type: application/json" \
     -d '{"columns": null, "save_mapping": true}'
   ```

4. **Test one-hot encoding:**
   ```bash
   curl -X POST http://localhost:5000/transform/one-hot-encode \
     -H "Content-Type: application/json" \
     -d '{"columns": ["Category"], "drop_first": false}'
   ```

5. **Run evolutionary cleaning and monitor logs:**
   - Check console output for detailed step-by-step progress
   - Look for emojis: 🧬 (GA), 🐝 (PSO), 🧪 (DE), 🎯 (ES)

---

## Files Modified

1. **python-backend/server.py**
   - Added imports for sklearn encoders
   - Added 3 new encoding endpoints
   - Updated server startup messages

2. **python-backend/data_fitness.py**
   - Enhanced GA with detailed crossover/mutation logging
   - Enhanced PSO with particle tracking
   - Enhanced DE with evaluation counting
   - Enhanced ES with offspring generation tracking
   - Added progress summaries every 20 iterations/generations

---

## Future Enhancements

Potential improvements:
- Add target encoding
- Add frequency encoding
- Add binary encoding
- Support for ordinal encoding with custom ordering
- Parallel processing for faster encoding
- Custom encoding strategies
- Integration with scikit-learn pipelines
