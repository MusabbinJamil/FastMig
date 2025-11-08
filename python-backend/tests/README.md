# FastMig Backend Tests

This directory contains all test files for the FastMig Python backend.

## 🧪 Test Files

### Core Feature Tests

#### **test_tracking_feature.py**
- **Purpose**: Comprehensive test suite for the Modified_by_AI tracking feature
- **Tests**:
  - Tracking enabled/disabled modes
  - All evolutionary algorithms (GA, PSO, DE, ES, Hybrid)
  - CSV export persistence
  - Modification statistics accuracy
- **Run**: `python tests/test_tracking_feature.py`

#### **test_evolutionary_cleaning.py**
- **Purpose**: Tests for evolutionary data cleaning algorithms
- **Tests**:
  - Genetic Algorithm (GA)
  - Particle Swarm Optimization (PSO)
  - Differential Evolution (DE)
  - Evolution Strategy (ES)
  - Hybrid method
- **Run**: `python tests/test_evolutionary_cleaning.py`

### Validation & Quick Tests

#### **simple_tracking_test.py**
- **Purpose**: Quick validation test for Modified_by_AI tracking
- **Use Case**: Fast smoke test to verify tracking works correctly
- **Features**: Simple numeric data test with clear pass/fail output
- **Run**: `python tests/simple_tracking_test.py`

#### **test_fix_validation.py**
- **Purpose**: Validation test for the Modified_by_AI bug fix
- **Use Case**: Verify the tracking bug fix is working
- **Run**: `python tests/test_fix_validation.py`

## 🚀 Running Tests

### Run All Tests
```bash
cd python-backend
python -m pytest tests/
```

### Run Individual Test
```bash
cd python-backend
python tests/test_tracking_feature.py
```

### Run Quick Validation
```bash
cd python-backend
python tests/simple_tracking_test.py
```

## 📊 Test Data

- **test_tracked_modifications.csv** - Sample output from tracking tests showing Modified_by_AI column

## ✅ Test Coverage

Current test coverage includes:
- ✅ Modified_by_AI tracking feature
- ✅ All 5 evolutionary algorithms
- ✅ Data fitness evaluation
- ✅ CSV export with tracking
- ✅ Tracking enable/disable modes
- ✅ Modification statistics reporting

## 🐛 Known Issues

Some algorithms have issues with certain data types:
- **PSO**: Issues with categorical/string data
- **ES**: Issues with categorical/string data  
- **GA**: Edge case in crossover with single-value columns

These are separate from the tracking feature and documented in the main codebase.

## 📝 Adding New Tests

1. Create a new test file: `test_<feature_name>.py`
2. Follow the naming convention: `test_*`
3. Include docstrings explaining what is being tested
4. Add entry to this README
5. Ensure tests can run independently

## 🔗 Related Documentation

- [Tracking Feature Guide](../docs/TRACKING_FEATURE.md)
- [Evolutionary Cleaning Guide](../docs/EVOLUTIONARY_CLEANING_GUIDE.md)
- [Bug Fix Report](../docs/BUGFIX_MODIFIED_BY_AI.md)

---

**Last Updated**: November 8, 2025
