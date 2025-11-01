# FastMig Python Backend

## 🚀 New Feature: Data Fitness & Evolutionary Cleaning

This backend now includes advanced data quality assessment and evolutionary data cleaning capabilities!

### ✨ What's New

- **Data Fitness Evaluation**: Automatically score the health of each record (0-100%)
- **SQLite Compatibility Checking**: Detect import errors before they happen
- **5 Evolutionary Algorithms**: GA, PSO, DE, ES, and Hybrid methods
- **Distribution Preservation**: Imputes missing data while maintaining statistical properties
- **Intelligent Imputation**: Uses existing data patterns for natural value suggestions

## 📁 Files

### Core Server
- `server.py` - Main Flask server with all API endpoints
- `functions.py` - Data processing utilities
- `app.py` - Application entry point

### New Modules (v0.3)
- **`data_fitness.py`** - Core fitness evaluation and evolutionary cleaning module
- **`test_evolutionary_cleaning.py`** - Comprehensive test suite
- **`example_client.py`** - Example Python client for testing

### Documentation
- **`EVOLUTIONARY_CLEANING_GUIDE.md`** - Complete feature documentation
- **`QUICK_REFERENCE.md`** - Quick start guide
- `requirements.txt` - Python dependencies
- `Next updates.txt` - Development roadmap

## 🔧 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Required packages (auto-installed):
# - Flask & Flask-CORS
# - pandas, numpy, scipy
# - openpyxl, xlrd (Excel support)
```

## 🏃 Quick Start

### 1. Start the Server
```bash
python server.py
```
Server runs at: `http://localhost:5000`

### 2. Test the New Features
```bash
# Run comprehensive tests
python test_evolutionary_cleaning.py

# Or try the example client
python example_client.py
```

### 3. Use in Your Application
```python
import requests

BASE_URL = "http://localhost:5000"

# Upload file
with open('data.csv', 'rb') as f:
    response = requests.post(f"{BASE_URL}/upload", files={'file': f})

# Evaluate fitness
response = requests.post(f"{BASE_URL}/fitness/evaluate")
print(f"Average fitness: {response.json()['summary']['average_fitness']}%")

# Clean with hybrid method (recommended)
response = requests.post(f"{BASE_URL}/clean/evolutionary", 
                        json={"method": "hybrid", "save_result": True})

# Export cleaned data
response = requests.post(f"{BASE_URL}/export", 
                        json={"output_path": "cleaned.csv"})
```

## 📡 API Endpoints

### Original Endpoints
- `POST /upload` - Upload and load a file
- `POST /process` - Process/convert column data
- `POST /export` - Export processed data
- `GET /columns` - Get column information
- `POST /recording/*` - Macro recording features

### New Endpoints (v0.3)

#### Data Fitness
- `POST /fitness/evaluate` - Evaluate all records' health scores
- `GET /fitness/record/<index>` - Get fitness for specific record

#### Evolutionary Cleaning
- `POST /clean/evolutionary` - Clean data using evolutionary algorithms
  - Methods: `ga`, `pso`, `de`, `es`, `hybrid`
- `POST /clean/compare` - Compare all cleaning methods
- `POST /data/restore` - Restore original data

## 🧬 Evolutionary Algorithms

### 1. Genetic Algorithm (GA)
- **Best for**: Mixed data types
- **How it works**: Evolution through selection, crossover, and mutation
- **Speed**: Medium

### 2. Particle Swarm Optimization (PSO)
- **Best for**: Numeric data
- **How it works**: Particles explore solution space collaboratively
- **Speed**: Fast

### 3. Differential Evolution (DE)
- **Best for**: Complex distributions
- **How it works**: Mutation with difference vectors
- **Speed**: Medium

### 4. Evolution Strategy (ES)
- **Best for**: Consistent improvements
- **How it works**: (μ, λ) selection with self-adaptive mutation
- **Speed**: Slower but reliable

### 5. Hybrid Method ⭐ (Recommended)
- **Best for**: Everything
- **How it works**: Auto-selects best algorithm per column type
- **Speed**: Fast

## 📊 Health Status Categories

- ✅ **Excellent** (95-100%): No issues, ready to use
- ✔️ **Good** (80-94%): Minor issues, mostly clean
- ⚠️ **Fair** (60-79%): Needs cleaning
- ❌ **Poor** (40-59%): Requires attention
- 🔴 **Critical** (0-39%): Major problems

## 🎯 Example Workflow

```python
from example_client import FastMigClient

client = FastMigClient()

# 1. Upload data
client.upload_file("messy_data.csv")

# 2. Check fitness
fitness = client.evaluate_fitness()
print(f"Records needing cleaning: {fitness['summary']['records_needing_cleaning']}")

# 3. Compare methods to find the best
comparison = client.compare_methods()
print(f"Best method: {comparison['best_method']}")

# 4. Clean with best method
result = client.clean_data(method=comparison['best_method'])
print(f"Improvement: +{result['report']['improvement']['fitness_increase']}%")

# 5. Export
client.export_data("cleaned_data.csv")
```

## 🔬 How It Works

### Fitness Evaluation
Each record is scored based on:
1. **Missing Values (40%)** - Completeness
2. **Type Consistency (30%)** - Data type correctness
3. **SQLite Compatibility (30%)** - Import safety

### Evolutionary Imputation
The algorithms:
1. Sample from existing data to create candidate solutions
2. Evaluate fitness based on distribution similarity
3. Evolve solutions through algorithm-specific operations
4. Select best solution that preserves data properties

### Key Advantages
- ✅ Preserves probability distributions (KS test validation)
- ✅ Maintains statistical properties (mean, std, quartiles)
- ✅ Uses similar values to existing data
- ✅ Validates SQLite compatibility
- ✅ Multiple algorithms for different data types

## 🧪 Testing

Run the test suite:
```bash
python test_evolutionary_cleaning.py
```

This will:
1. Create sample data with intentional issues
2. Evaluate fitness scores
3. Test all evolutionary algorithms
4. Compare performance
5. Save results to CSV files

## 📚 Documentation

- **Full Guide**: `EVOLUTIONARY_CLEANING_GUIDE.md` - Complete documentation
- **Quick Reference**: `QUICK_REFERENCE.md` - Cheat sheet
- **Example Code**: `example_client.py` - Python client examples
- **Test Suite**: `test_evolutionary_cleaning.py` - Testing examples

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Or use different port
python server.py  # Edit server.py to change port
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Slow Cleaning
- Use `"hybrid"` method (auto-optimized)
- Reduce population size and iterations
- Start with smaller datasets for testing

### No Improvement
- Check if data has missing values: `/fitness/evaluate`
- Try `/clean/compare` to find best method
- Some data may not benefit from these techniques

## 📈 Performance Tips

1. **Start small**: Test with limited parameters
   ```json
   {"population_size": 20, "generations": 30}
   ```

2. **Use hybrid**: Auto-selects best approach
   ```json
   {"method": "hybrid"}
   ```

3. **Check first**: Evaluate fitness before cleaning
   ```bash
   curl -X POST http://localhost:5000/fitness/evaluate
   ```

## 🔄 Version History

### v0.3 (Current) - November 2025
- ✨ Added data fitness evaluation
- ✨ Implemented 5 evolutionary algorithms
- ✨ SQLite compatibility checking
- ✨ Distribution preservation
- ✨ Comprehensive testing suite

### v0.2
- File upload and processing
- Column conversion
- Macro recording

### v0.1
- Initial release
- Basic data loading and export

## 📝 Next Updates (Planned)

From `Next updates.txt`:
- Fix bugs (error pop-ups, data conversion formats)
- Bulk edit files with same changes
- Break product codes into categories
- Split datetime to date and time
- Menu bar enhancements

**New Ideas:**
- Deep learning-based imputation
- Anomaly detection and correction
- Parallel processing for large datasets
- Custom fitness functions
- Real-time cleaning progress

## 🤝 Contributing

To add new evolutionary algorithms:
1. Add method to `EvolutionaryDataCleaner` class in `data_fitness.py`
2. Update `clean_data_evolutionary()` function
3. Add endpoint support in `server.py`
4. Update documentation

## 📄 License

Part of the FastMig project - Data Migration Tool

## 🆘 Support

For issues or questions:
1. Check server logs (console output)
2. Review documentation in `EVOLUTIONARY_CLEANING_GUIDE.md`
3. Run test suite: `python test_evolutionary_cleaning.py`
4. Check health endpoint: `http://localhost:5000/health`

---

**Made with ❤️ for better data quality**
