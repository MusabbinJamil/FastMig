# Quick Reference: Data Fitness & Evolutionary Cleaning

## Installation

```bash
pip install -r requirements.txt
```

## Start Server

```bash
python server.py
```

Server runs at: `http://localhost:5000`

## Quick Start

### 1. Upload & Evaluate
```bash
# Upload file
curl -X POST http://localhost:5000/upload -F "file=@data.csv"

# Check fitness
curl -X POST http://localhost:5000/fitness/evaluate
```

### 2. Clean Data (Recommended Method)
```bash
curl -X POST http://localhost:5000/clean/evolutionary \
  -H "Content-Type: application/json" \
  -d '{"method": "hybrid", "save_result": true}'
```

### 3. Export Cleaned Data
```bash
curl -X POST http://localhost:5000/export \
  -H "Content-Type: application/json" \
  -d '{"output_path": "cleaned.csv"}'
```

## All Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/fitness/evaluate` | POST | Evaluate all records |
| `/fitness/record/<id>` | GET | Check specific record |
| `/clean/evolutionary` | POST | Clean with evolution |
| `/clean/compare` | POST | Compare all methods |
| `/data/restore` | POST | Restore original data |

## Evolutionary Methods

| Method | Best For | Speed |
|--------|----------|-------|
| `ga` | Mixed data types | Medium |
| `pso` | Numeric data | Fast |
| `de` | Complex distributions | Medium |
| `es` | Consistency | Slow |
| `hybrid` | **Everything** (recommended) | Fast |

## Health Status

- ✅ **Excellent** (95-100%): No action needed
- ✔️ **Good** (80-94%): Minor issues
- ⚠️ **Fair** (60-79%): Needs cleaning
- ❌ **Poor** (40-59%): Requires attention
- 🔴 **Critical** (0-39%): Major problems

## Python Quick Code

```python
import requests

BASE_URL = "http://localhost:5000"

# Upload
with open('data.csv', 'rb') as f:
    r = requests.post(f"{BASE_URL}/upload", files={'file': f})

# Evaluate
r = requests.post(f"{BASE_URL}/fitness/evaluate")
print(f"Average fitness: {r.json()['summary']['average_fitness']}%")

# Clean
r = requests.post(f"{BASE_URL}/clean/evolutionary", 
                  json={"method": "hybrid", "save_result": True})
print(f"Improvement: +{r.json()['report']['improvement']['fitness_increase']}%")

# Export
r = requests.post(f"{BASE_URL}/export", 
                  json={"output_path": "cleaned.csv"})
```

## Test the Features

```bash
python test_evolutionary_cleaning.py
```

## Troubleshooting

**Problem:** "No data loaded"  
**Solution:** Upload a file first using `/upload`

**Problem:** Slow cleaning  
**Solution:** Use `"hybrid"` method or reduce parameters

**Problem:** No improvement  
**Solution:** Try `/clean/compare` to find best method

## Parameters (Optional)

### Genetic Algorithm
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

### PSO
```json
{
  "method": "pso",
  "parameters": {
    "n_particles": 30,
    "iterations": 100
  }
}
```

### Default (Fast)
```json
{
  "method": "hybrid"
}
```

## Files Created

- `data_fitness.py` - Core module
- `EVOLUTIONARY_CLEANING_GUIDE.md` - Full documentation
- `test_evolutionary_cleaning.py` - Test script
- `QUICK_REFERENCE.md` - This file

## Need Help?

Check the full guide: `EVOLUTIONARY_CLEANING_GUIDE.md`
