# FastMig Python Backend

AI-powered data migration and quality improvement system using evolutionary algorithms.

## 📁 Project Structure

```
python-backend/
├── 📄 Core Files
│   ├── server.py              # Flask REST API server
│   ├── data_fitness.py        # Evolutionary cleaning algorithms & fitness evaluation
│   ├── functions.py           # Utility functions
│   ├── example_client.py      # Example API client
│   └── requirements.txt       # Python dependencies
│
├── 📚 docs/                   # All documentation
│   ├── INDEX.md              # Documentation index
│   ├── README.md             # Main documentation
│   ├── QUICK_REFERENCE.md    # Quick reference guide
│   ├── EVOLUTIONARY_CLEANING_GUIDE.md
│   ├── TRACKING_FEATURE.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PROJECT_STRUCTURE.md
│   ├── CHECKLIST.md
│   └── BUGFIX_MODIFIED_BY_AI.md
│
├── 🧪 tests/                  # All test files
│   ├── README.md
│   ├── test_tracking_feature.py
│   ├── test_evolutionary_cleaning.py
│   ├── simple_tracking_test.py
│   └── test_fix_validation.py
│
└── 📦 uploads/                # Uploaded data files
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python server.py
```

The server will start at `http://localhost:5000`

### 3. Test the API
```bash
python example_client.py
```

## ✨ Key Features

- **🧬 Evolutionary Data Cleaning**: 5 algorithms (GA, PSO, DE, ES, Hybrid)
- **📊 Data Fitness Evaluation**: Assess data quality with multiple metrics
- **🔍 AI Modification Tracking**: Transparent tracking of AI-modified records
- **📈 Statistical Analysis**: Comprehensive data quality reports
- **🔄 REST API**: Easy integration with any frontend

## 📖 Documentation

All documentation is organized in the `docs/` folder:

- **Getting Started**: [docs/README.md](docs/README.md)
- **Full Index**: [docs/INDEX.md](docs/INDEX.md)
- **Quick Reference**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

## 🧪 Testing

All tests are in the `tests/` folder:

```bash
# Run comprehensive tracking test
python tests/test_tracking_feature.py

# Run quick validation test
python tests/simple_tracking_test.py
```

See [tests/README.md](tests/README.md) for more details.

## 🔧 API Endpoints

### Evaluate Data Fitness
```bash
POST /evaluate
```

### Clean Data with Evolutionary Algorithms
```bash
POST /clean/evolutionary
```

### Get Current Data
```bash
GET /data
```

See [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) for full API documentation.

## 🐛 Recent Updates

**November 8, 2025** - Fixed Modified_by_AI tracking bug  
See: [docs/BUGFIX_MODIFIED_BY_AI.md](docs/BUGFIX_MODIFIED_BY_AI.md)

## 📦 Dependencies

- Flask - REST API framework
- pandas - Data manipulation
- numpy - Numerical computing
- scipy - Scientific computing
- flask-cors - CORS support

## 🤝 Contributing

1. Create tests in `tests/` folder
2. Document features in `docs/` folder
3. Follow existing code structure
4. Run tests before committing

## 📝 License

See main project repository for license information.

---

**Version**: 0.3.2  
**Last Updated**: November 8, 2025
