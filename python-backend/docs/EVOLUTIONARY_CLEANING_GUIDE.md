# Data Fitness & Evolutionary Cleaning Guide

## Overview

The FastMig backend now includes advanced data quality assessment and evolutionary data cleaning capabilities. This system evaluates the "health" or "fitness" of your data records and uses evolutionary algorithms to intelligently impute missing values while preserving the statistical properties of your data.

## Key Features

### 1. **Data Fitness Evaluation**
- Assigns health scores (0-100%) to each record
- Identifies missing values, type inconsistencies, and SQLite compatibility issues
- Categorizes records: Excellent (95%+), Good (80-95%), Fair (60-80%), Poor (40-60%), Critical (<40%)

### 2. **Evolutionary Algorithms**
Five different evolutionary approaches for data imputation:

#### **Genetic Algorithm (GA)**
- Evolves populations of candidate imputations
- Uses selection, crossover, and mutation operators
- Best for: Mixed data types, general-purpose cleaning

#### **Particle Swarm Optimization (PSO)**
- Particles "swarm" toward optimal imputation values
- Balances exploration and exploitation
- Best for: Numeric data, continuous values

#### **Differential Evolution (DE)**
- Uses mutation and crossover with difference vectors
- Robust global optimization
- Best for: Numeric data with complex distributions

#### **Evolution Strategy (ES)**
- (μ, λ) selection strategy
- Self-adaptive mutation
- Best for: When you need consistent improvements

#### **Hybrid Method**
- Automatically selects best algorithm per column type
- PSO for numeric columns, GA for categorical
- Best for: Mixed datasets (recommended)

## API Endpoints

### 1. Evaluate Data Fitness

**Endpoint:** `POST /fitness/evaluate`

**Description:** Evaluates the fitness/health of all records in the loaded dataset.

**Request:** No body required (uses currently loaded data)

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_records": 1000,
    "average_fitness": 87.5,
    "min_fitness": 45.0,
    "max_fitness": 100.0,
    "health_breakdown": {
      "excellent": 650,
      "good": 200,
      "fair": 100,
      "poor": 40,
      "critical": 10
    },
    "records_needing_cleaning": 350
  },
  "detailed_results": [
    {
      "row_index": 0,
      "fitness": 100.0,
      "health_status": "Excellent",
      "issues_count": 0,
      "missing_score": 100.0,
      "type_score": 100.0,
      "sqlite_score": 100.0
    },
    // ... more records
  ],
  "message": "Evaluated 1000 records. Average fitness: 87.50%"
}
```

### 2. Evaluate Specific Record

**Endpoint:** `GET /fitness/record/<row_index>`

**Example:** `GET /fitness/record/5`

**Response:**
```json
{
  "success": true,
  "row_index": 5,
  "fitness": {
    "overall_fitness": 75.5,
    "missing_score": 80.0,
    "type_consistency_score": 90.0,
    "sqlite_compatibility_score": 60.0,
    "issues": [
      "1 missing values",
      "Type mismatch in 'age'"
    ],
    "health_status": "Fair"
  }
}
```

### 3. Clean Data with Evolutionary Algorithms

**Endpoint:** `POST /clean/evolutionary`

**Request Body:**
```json
{
  "method": "hybrid",
  "save_result": true,
  "parameters": {
    // Method-specific parameters (optional)
  }
}
```

**Methods:** `"ga"`, `"pso"`, `"de"`, `"es"`, `"hybrid"`

**Parameters by Method:**

**Genetic Algorithm (GA):**
```json
{
  "method": "ga",
  "parameters": {
    "population_size": 50,
    "generations": 100,
    "mutation_rate": 0.1,
    "crossover_rate": 0.8
  }
}
```

**PSO:**
```json
{
  "method": "pso",
  "parameters": {
    "n_particles": 30,
    "iterations": 100,
    "inertia": 0.7,
    "cognitive": 1.5,
    "social": 1.5
  }
}
```

**Differential Evolution (DE):**
```json
{
  "method": "de",
  "parameters": {
    "pop_size": 30,
    "max_iter": 100
  }
}
```

**Evolution Strategy (ES):**
```json
{
  "method": "es",
  "parameters": {
    "mu": 15,
    "lambda_": 45,
    "generations": 100
  }
}
```

**Hybrid:** (No parameters needed - auto-configures)

**Response:**
```json
{
  "success": true,
  "method": "HYBRID",
  "report": {
    "method": "hybrid",
    "before": {
      "average_fitness": 75.5,
      "records_with_issues": 250
    },
    "after": {
      "average_fitness": 96.8,
      "records_with_issues": 15
    },
    "improvement": {
      "fitness_increase": 21.3,
      "records_fixed": 235
    }
  },
  "data": [...],  // First 100 rows of cleaned data
  "columns": [...],
  "shape": [1000, 15],
  "message": "Data cleaned using HYBRID. Fitness improved by 21.30%. 235 records fixed."
}
```

### 4. Compare All Methods

**Endpoint:** `POST /clean/compare`

**Description:** Tests all five evolutionary methods and reports which performs best on your data.

**Request:** No body required

**Response:**
```json
{
  "success": true,
  "results": {
    "ga": {
      "before_fitness": 75.5,
      "after_fitness": 92.3,
      "improvement": 16.8,
      "records_fixed": 200
    },
    "pso": {
      "before_fitness": 75.5,
      "after_fitness": 94.1,
      "improvement": 18.6,
      "records_fixed": 220
    },
    "de": {
      "before_fitness": 75.5,
      "after_fitness": 93.7,
      "improvement": 18.2,
      "records_fixed": 215
    },
    "es": {
      "before_fitness": 75.5,
      "after_fitness": 91.8,
      "improvement": 16.3,
      "records_fixed": 195
    },
    "hybrid": {
      "before_fitness": 75.5,
      "after_fitness": 96.8,
      "improvement": 21.3,
      "records_fixed": 235
    }
  },
  "best_method": "hybrid",
  "best_improvement": 21.3,
  "message": "Comparison complete. Best method: HYBRID"
}
```

### 5. Restore Original Data

**Endpoint:** `POST /data/restore`

**Description:** Restores the original data before cleaning was applied.

**Response:**
```json
{
  "success": true,
  "message": "Original data restored successfully"
}
```

## Usage Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:5000"

# 1. Upload a file
with open('data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(response.json())

# 2. Evaluate fitness
response = requests.post(f"{BASE_URL}/fitness/evaluate")
fitness_data = response.json()
print(f"Average fitness: {fitness_data['summary']['average_fitness']}%")
print(f"Records needing cleaning: {fitness_data['summary']['records_needing_cleaning']}")

# 3. Clean with hybrid method (recommended)
response = requests.post(f"{BASE_URL}/clean/evolutionary", json={
    "method": "hybrid",
    "save_result": True
})
result = response.json()
print(f"Fitness improvement: {result['report']['improvement']['fitness_increase']}%")

# 4. Export cleaned data
response = requests.post(f"{BASE_URL}/export", json={
    "output_path": "cleaned_data.csv"
})
print(response.json())
```

### cURL Examples

```bash
# Evaluate fitness
curl -X POST http://localhost:5000/fitness/evaluate

# Clean with Genetic Algorithm
curl -X POST http://localhost:5000/clean/evolutionary \
  -H "Content-Type: application/json" \
  -d '{
    "method": "ga",
    "save_result": true,
    "parameters": {
      "population_size": 50,
      "generations": 100
    }
  }'

# Compare all methods
curl -X POST http://localhost:5000/clean/compare

# Check specific record fitness
curl -X GET http://localhost:5000/fitness/record/42
```

## How It Works

### Fitness Evaluation

Each record is scored on three criteria:

1. **Missing Values (40% weight)**
   - 100% = No missing values
   - Penalty: (missing_count / total_columns) × 100

2. **Type Consistency (30% weight)**
   - Checks if values match expected data types
   - Validates numeric, datetime, boolean, string types

3. **SQLite Compatibility (30% weight)**
   - Checks for NULL characters, integer overflow, invalid floats
   - Ensures data can be imported to SQLite without errors

### Evolutionary Imputation

The algorithms work by:

1. **Initialization:** Create population of candidate imputation values sampled from existing data
2. **Evaluation:** Calculate fitness based on:
   - Distribution similarity (Kolmogorov-Smirnov test)
   - Statistical properties preservation (mean, std deviation)
   - Value similarity to existing data
3. **Evolution:** Apply algorithm-specific operators (selection, crossover, mutation, etc.)
4. **Iteration:** Repeat until convergence or max iterations
5. **Selection:** Choose best solution that maximizes fitness

### Distribution Preservation

All algorithms preserve the probability distribution of your data:
- **Numeric columns:** Uses KS test to ensure similar distributions
- **Categorical columns:** Maintains frequency distributions
- **Statistical properties:** Preserves mean, standard deviation, quartiles

## Best Practices

### When to Use Each Method

- **Just want it to work?** → Use `"hybrid"` (recommended)
- **Mostly numeric data?** → Use `"pso"` or `"de"`
- **Categorical/mixed data?** → Use `"ga"`
- **Need consistency?** → Use `"es"`
- **Not sure which is best?** → Use `/clean/compare` endpoint first

### Performance Tips

1. **Start with small parameters** for testing:
   ```json
   {
     "population_size": 20,
     "generations": 30
   }
   ```

2. **Use hybrid method** for automatic optimization

3. **Check fitness first** with `/fitness/evaluate` to see if cleaning is needed

4. **Compare methods** on a sample to find the best approach

### Workflow Recommendation

```
1. Upload data → POST /upload
2. Check fitness → POST /fitness/evaluate
3. If fitness < 90%:
   a. Compare methods → POST /clean/compare
   b. Use best method → POST /clean/evolutionary
   c. Verify improvement → POST /fitness/evaluate
4. Export cleaned data → POST /export
```

## Technical Details

### Fitness Score Calculation

```
Overall Fitness = (Missing Score × 0.4) + 
                  (Type Consistency × 0.3) + 
                  (SQLite Compatibility × 0.3)
```

### Health Status Thresholds

- **Excellent:** 95-100%
- **Good:** 80-94.9%
- **Fair:** 60-79.9%
- **Poor:** 40-59.9%
- **Critical:** 0-39.9%

### Algorithm Complexity

- **GA:** O(P × G × N) where P=population, G=generations, N=data_size
- **PSO:** O(P × I × N) where P=particles, I=iterations
- **DE:** Similar to PSO
- **ES:** O((μ + λ) × G × N)
- **Hybrid:** Varies by column type

## Troubleshooting

### "No data loaded" Error
- Make sure to upload a file first using `/upload` endpoint

### Cleaning Takes Too Long
- Reduce population size and generations
- Use hybrid method (auto-optimized)
- Start with `/clean/compare` to find fastest method

### Fitness Not Improving
- Check if data has actual missing values: `/fitness/evaluate`
- Try different methods with `/clean/compare`
- Increase generations/iterations
- Some data may be inherently low quality

### Memory Issues
- Reduce population size
- Process data in chunks
- Use simpler algorithms (ES, GA)

## Future Enhancements

Potential future additions:
- Multi-objective optimization (speed vs. quality)
- Custom fitness functions
- Parallel processing for large datasets
- Deep learning-based imputation
- Anomaly detection and correction
- Constraint-based imputation

## Dependencies

The evolutionary cleaning module requires:
- `numpy` - Numerical operations
- `pandas` - Data manipulation
- `scipy` - Statistical functions and differential evolution
- `sqlite3` - Compatibility testing (built-in)

All dependencies are listed in `requirements.txt`.

## References

This implementation is based on principles from:
- Genetic Algorithms (Holland, 1975)
- Particle Swarm Optimization (Kennedy & Eberhart, 1995)
- Differential Evolution (Storn & Price, 1997)
- Evolution Strategies (Rechenberg, 1973)

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Verify all dependencies are installed
3. Test with small dataset first
4. Use `/health` endpoint to check server status

---

**Version:** 1.0  
**Last Updated:** November 2025  
**Author:** FastMig Development Team
