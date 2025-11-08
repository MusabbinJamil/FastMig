# ETL Operations & Step Recording - Frontend Guide

## Overview
The FastMig Flutter frontend now includes powerful ETL (Extract, Transform, Load) operations, with the ability to record and replay transformation pipelines.

## 📍 Navigation
Access ETL features from the main menu:
- **Record Steps** - Combines step recording and ETL operations in one screen

## 🎯 Features

### 1. ETL Operations (8 Available)

#### **Remove Null Rows**
- **Purpose**: Remove rows containing null/missing values
- **Parameters**: Select specific columns to check (or check all columns)
- **Use Case**: Clean datasets before analysis

#### **Remove Duplicate Rows**
- **Purpose**: Remove duplicate records from dataset
- **Parameters**: 
  - Select columns to identify duplicates
  - Keep first or last occurrence
- **Use Case**: Ensure data uniqueness

#### **Trim Whitespace**
- **Purpose**: Remove leading/trailing spaces from text columns
- **Parameters**: Select columns to trim
- **Use Case**: Clean text data, standardize formatting

#### **Find & Replace**
- **Purpose**: Replace specific values in columns
- **Parameters**:
  - Select column
  - Find value (text to search for)
  - Replace value (text to replace with)
  - Case sensitive option
- **Use Case**: Fix typos, standardize values, rename categories

#### **Fill Null Values**
- **Purpose**: Fill missing values using various strategies
- **Parameters**:
  - Select columns to fill
  - Fill method:
    - **Forward Fill**: Use previous valid value
    - **Backward Fill**: Use next valid value
    - **Mean**: Fill with column average (numeric only)
    - **Median**: Fill with column median (numeric only)
    - **Mode**: Fill with most frequent value
    - **Constant**: Fill with specific value you provide
- **Use Case**: Handle missing data for analysis

#### **Change Case**
- **Purpose**: Convert text to different cases
- **Parameters**:
  - Select columns
  - Case type:
    - **Lower**: convert to lowercase
    - **Upper**: CONVERT TO UPPERCASE
    - **Title**: Convert To Title Case
- **Use Case**: Standardize text formatting

#### **Filter Rows**
- **Purpose**: Keep only rows matching specific criteria
- **Parameters**:
  - Select column to filter on
  - Operator: ==, !=, >, <, >=, <=, contains, startswith, endswith
  - Value to compare against
- **Use Case**: Extract subsets of data, data exploration

#### **Sort Data**
- **Purpose**: Sort dataset by column values
- **Parameters**:
  - Select column to sort by
  - Order: Ascending or Descending
- **Use Case**: Organize data for analysis

### 2. Step Recording

#### How It Works
1. **Start Recording**: Click "Start Recording" button
2. **Perform Operations**: Apply any ETL operations or conversions
3. **Stop Recording**: Click "Stop Recording" when done
4. **View Steps**: Review the recorded transformation pipeline
5. **Save Steps**: Give your pipeline a name and save for later use
6. **Replay Steps**: Apply saved pipeline to new datasets

#### Recording Features
- **Visual Indicator**: Red "Recording..." status when active
- **Step Counter**: Shows number of recorded steps
- **Step Preview**: View all recorded steps with parameters
- **Pipeline Persistence**: Saved steps persist on backend

#### Use Cases
- **Repetitive Tasks**: Record once, replay many times
- **Data Pipelines**: Create reusable transformation workflows
- **Consistency**: Apply same transformations across multiple files
- **Documentation**: Steps serve as data transformation documentation

## 🎨 User Interface

### Layout
The "Record Steps" screen is divided into two sections:
1. **Top Section (1/3)**: Step Recording controls
2. **Bottom Section (2/3)**: ETL Operations panel

### ETL Operations Panel
- **Operation Selector**: Dropdown to choose operation type
- **Dynamic Parameters**: Form fields change based on selected operation
- **Column Chips**: Visual display of selected columns
- **Execute Button**: Apply the selected operation
- **Status Messages**: Success/error feedback

## 🚀 Quick Start Guide

### Example 1: Basic Data Cleaning
```
1. Load your data (Load Data screen)
2. Navigate to "Record Steps"
3. Start Recording
4. Apply operations:
   - Remove Null Rows (check all columns)
   - Trim Whitespace (select text columns)
   - Remove Duplicates (select ID columns)
5. Stop Recording
6. Save Steps as "Basic Cleaning Pipeline"
```

### Example 2: Text Standardization
```
1. Load data with text columns
2. Navigate to "Record Steps"
3. Apply operations:
   - Trim Whitespace (all text columns)
   - Change Case (Lower case for email, Title case for names)
   - Find & Replace (fix common typos)
4. Record this pipeline for reuse
```

### Example 3: Data Filtering & Sorting
```
1. Load sales data
2. Navigate to "Record Steps"
3. Apply operations:
   - Filter Rows (Amount > 1000)
   - Sort Data (Date column, Descending)
   - Fill Null Values (Customer field, Forward Fill)
4. Export filtered results
```

## 🔄 Workflow Integration

### Recommended Workflow
1. **Load Data** → Upload your CSV/Excel file
2. **Convert Fields** → Set correct data types
3. **Record Steps + ETL** → Clean and transform data
4. **View Data** → Preview results
5. **AI Cleaning** → Optional: Apply evolutionary algorithms
6. **Export Data** → Save processed data

### Recording Best Practices
- ✅ Start recording BEFORE performing operations
- ✅ Test operations individually before recording pipeline
- ✅ Give pipelines descriptive names
- ✅ Review recorded steps before saving
- ✅ Keep pipelines focused (5-10 steps max)

### ETL Best Practices
- ✅ Remove nulls before other operations
- ✅ Trim whitespace before text comparisons
- ✅ Remove duplicates after cleaning
- ✅ Sort data as final step
- ✅ Use View Data to verify results

## 🎓 Advanced Features

### Column Selection
Most operations allow selecting specific columns:
- **Single Column**: Operations like Find & Replace, Sort
- **Multiple Columns**: Operations like Remove Nulls, Trim Whitespace
- **Smart Selection**: UI shows chips for selected columns

### Error Handling
- Operations validate parameters before execution
- Clear error messages shown in red snackbar
- Success messages shown in green snackbar
- Data automatically updates on success

### State Management
- Uses Flutter Provider pattern
- Data updates trigger UI refresh
- Column list updates after operations
- Shape (rows × columns) updates in real-time

## 🔧 Technical Details

### API Integration
All ETL operations communicate with Python backend:
- **Endpoint Base**: `http://localhost:5000/etl/`
- **Response Format**: JSON with data, columns, shape, message
- **Error Handling**: Comprehensive try-catch with user feedback

### Data Flow
```
User Action → ETL Widget → MigrationData Model → ApiService → Backend
                                    ↓
                               Update UI ← Parse Response ← Backend
```

### Dependencies
- `provider` - State management
- `http` - API communication
- Flutter Material Design components

## 📊 Supported Data Types

### Operations by Data Type
- **Text**: Trim, Find/Replace, Change Case, Fill (mode/constant)
- **Numeric**: Fill (mean/median/mode/constant), Filter, Sort
- **All Types**: Remove Nulls, Remove Duplicates, Sort

### Fill Methods Compatibility
| Method | Text | Numeric | Mixed |
|--------|------|---------|-------|
| Forward | ✅ | ✅ | ✅ |
| Backward | ✅ | ✅ | ✅ |
| Mean | ❌ | ✅ | ❌ |
| Median | ❌ | ✅ | ❌ |
| Mode | ✅ | ✅ | ✅ |
| Constant | ✅ | ✅ | ✅ |

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No data loaded" error
- **Solution**: Load data first from "Load Data" screen

**Issue**: Column not appearing in dropdown
- **Solution**: Refresh by switching screens or reloading data

**Issue**: Operation doesn't seem to work
- **Solution**: Check "View Data" screen to see actual changes

**Issue**: Can't save recording
- **Solution**: Stop recording first, then click "Save Steps"

**Issue**: Fill Null with mean/median fails
- **Solution**: Ensure column is numeric type (use Convert Fields)

## 📝 Tips & Tricks

1. **Preview Before Recording**: Test operations before starting recording
2. **Compound Operations**: Combine multiple operations in one pipeline
3. **Naming Convention**: Use descriptive names like "Sales_Data_Cleanup_v1"
4. **Version Control**: Save multiple versions of pipelines
5. **Column Selection**: Select fewer columns for faster processing
6. **View Often**: Check "View Data" frequently to verify changes
7. **Export Checkpoints**: Export data at key stages

## 🔮 Future Enhancements (Planned)

- Custom function support
- Conditional transformations
- Merge/Join operations
- Aggregate operations (GROUP BY)
- Regular expression support in Find & Replace
- Undo/Redo functionality
- Pipeline sharing/export
- Batch processing multiple files

## 📚 Related Documentation

- Backend ETL Guide: `python-backend/docs/ETL_OPERATIONS_GUIDE.md`
- Quick Reference: `python-backend/docs/ETL_QUICK_REFERENCE.md`
- API Documentation: `python-backend/README.md`
- Flutter Setup: `flutter-frontend-app/QUICK_SETUP.md`

---

**Version**: 1.0  
**Last Updated**: 2024  
**Framework**: Flutter 3.x  
**Backend**: Python/Flask
