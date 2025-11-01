# Quick Setup Guide - AI Features

## Prerequisites

1. **Backend Running**
   - Ensure Python backend is running on `http://localhost:5000`
   - Required Python packages installed (see python-backend/requirements.txt)
   - Evolutionary cleaning module available

2. **Flutter Dependencies**
   - Run `flutter pub get` if not already done
   - All packages should be installed

## New Files Added

### Widgets
- `lib/widgets/fitness_evaluation_section.dart` - Fitness evaluation UI
- `lib/widgets/evolutionary_cleaning_section.dart` - Cleaning algorithm UI

### Screens
- `lib/screens/ai_data_quality_screen.dart` - Combined workflow screen

### Services (Updated)
- `lib/services/api_service.dart` - Added new API methods:
  - `evaluateFitness()`
  - `getRecordFitness()`
  - `cleanDataEvolutionary()`
  - `compareCleaningMethods()`
  - `restoreOriginalData()`

### Models (Updated)
- `lib/models/migration_data.dart` - Added new state management methods

### Updated Files
- `lib/widgets/side_menu.dart` - Added AI Features section
- `lib/screens/data_migration_screen.dart` - Added new routes for AI features

## Testing the Features

### 1. Start Backend
```bash
cd python-backend
python server.py
```

### 2. Start Flutter App
```bash
cd flutter-frontend-app
flutter run -d windows
```

### 3. Test Workflow

**Step 1: Load Data**
1. Click "Load Data" from side menu
2. Select a CSV or Excel file with missing values
3. Wait for upload to complete

**Step 2: Evaluate Fitness**
1. Click "Data Fitness" from AI Features section
2. Click "Evaluate Fitness" button
3. Review fitness scores and health breakdown
4. Note records needing cleaning

**Step 3: Clean Data**
1. Click "AI Cleaning" from AI Features section
2. Select cleaning method (start with Hybrid)
3. Ensure "Track AI Modifications" is checked
4. Click "Clean Data"
5. Wait for processing
6. Review cleaning report

**Step 4: Optional - Compare Methods**
1. Click "Compare Methods" button
2. Wait for comparison (takes longer)
3. Review which method performed best
4. Select and use the best method if desired

**Step 5: Export**
1. Navigate to "Export Data"
2. Choose output format and location
3. Export cleaned data
4. The "Modified_by_AI" column will be included

## UI Navigation

### Side Menu Structure
```
FastMig
├── Load Data
├── Convert Fields
├── Record Macro
├── View Data
├── Export Data
├── ───────────────
├── AI Features
│   ├── Data Fitness
│   └── AI Cleaning
├── ───────────────
├── Settings
└── Help
```

## API Endpoint Mapping

| Feature | Endpoint | Method |
|---------|----------|--------|
| Evaluate Fitness | `/fitness/evaluate` | POST |
| Record Fitness | `/fitness/record/<int>` | GET |
| Clean Data | `/clean/evolutionary` | POST |
| Compare Methods | `/clean/compare` | POST |
| Restore Data | `/data/restore` | POST |

## Common Issues & Solutions

### Issue: "No data loaded" error
**Solution:** Load a file from "Load Data" section first

### Issue: Backend connection failed
**Solution:** 
1. Check if backend is running: `http://localhost:5000/health`
2. Restart backend server
3. Check firewall settings

### Issue: Cleaning takes forever
**Solution:**
1. Use smaller datasets for testing
2. Use Hybrid method (auto-optimized)
3. Don't use Compare Methods on large datasets initially

### Issue: Fitness doesn't improve
**Solution:**
1. Check if data actually has missing values
2. Try different algorithms
3. Use Compare Methods to find best algorithm

## Sample Test Data

Create a test CSV with missing values:

```csv
id,name,age,salary,department
1,John,25,50000,IT
2,Jane,,60000,HR
3,,30,,IT
4,Bob,35,70000,
5,Alice,,55000,HR
6,,,45000,IT
```

Expected results:
- Initial fitness: ~60-70%
- After cleaning: 95%+
- Modified records: 3-4 records
- Missing values filled intelligently

## Performance Benchmarks

| Dataset Size | Evaluation Time | Hybrid Cleaning | Compare All Methods |
|--------------|-----------------|-----------------|---------------------|
| 100 rows     | < 1 sec         | ~5 sec          | ~25 sec             |
| 1,000 rows   | ~1 sec          | ~10 sec         | ~50 sec             |
| 10,000 rows  | ~3 sec          | ~30 sec         | ~2.5 min            |

*Times are approximate and depend on system performance and data complexity*

## Next Steps

1. **Customize UI Colors:** Edit widget files to match your brand
2. **Add More Parameters:** Extend algorithm parameter controls
3. **Add Visualizations:** Show before/after distributions
4. **Export Reports:** Generate PDF reports of cleaning operations
5. **Batch Processing:** Add support for multiple files

## Resources

- **Backend Documentation:** `python-backend/EVOLUTIONARY_CLEANING_GUIDE.md`
- **Tracking Feature:** `python-backend/TRACKING_FEATURE.md`
- **Frontend Features:** `AI_FEATURES_README.md`
- **Main README:** `README.md`

## Support

For help:
1. Check backend server logs
2. Check Flutter console output
3. Review documentation files
4. Test with sample data first

---

**Ready to test!** Load some data and try the AI features! 🚀
