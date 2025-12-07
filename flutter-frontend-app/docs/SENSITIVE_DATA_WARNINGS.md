# Sensitive Data Imputation Warnings - Implementation Guide

## Overview

This implementation adds specific warnings for data that shouldn't be imputed using AI models, particularly for sensitive columns like Date of Birth, NIC (National ID), Passport numbers, and similar identifiers.

## Features Implemented

### 1. **Backend Detection** (`python-backend/data_fitness.py`)

Added `detect_sensitive_columns()` method to the `DataFitnessEvaluator` class that identifies sensitive columns based on:

- **Column name patterns**: Detects keywords like:
  - Date of Birth: `birth`, `dob`, `birthday`, `date_of_birth`, `born`, `birthdate`
  - ID/NIC: `nic`, `nid`, `national_id`, `passport`, `ssn`, `social_security`, `tax_id`, `license`, `driver`, `registration`, `vehicle`, `vin`, `chassis`, `serial`, `id_number`
  - Contact: `phone`, `mobile`, `contact`

- **Data patterns**: Analyzes actual data values for:
  - High uniqueness ratio (>95%) suggesting ID-like fields
  - Specific value patterns

### 2. **API Endpoint** (`python-backend/server.py`)

New endpoint: `GET /fitness/sensitive-columns`

**Response:**
```json
{
  "success": true,
  "sensitive_columns": {
    "date_of_birth": {
      "reason": "Date of Birth - Cannot be reliably imputed...",
      "severity": "high",
      "recommendation": "Consider manual imputation...",
      "has_missing": 5,
      "total_missing_pct": 2.5
    },
    "nic_number": {
      "reason": "Identification Number (NIC/Passport/ID)...",
      "severity": "high",
      "recommendation": "Consider manual imputation...",
      "has_missing": 3,
      "total_missing_pct": 1.5
    }
  },
  "count": 2,
  "message": "Detected 2 columns with potentially sensitive data..."
}
```

### 3. **Flutter API Service** (`flutter-frontend-app/lib/services/api_service.dart`)

Added `detectSensitiveColumns()` method that:
- Calls the backend endpoint
- Returns gracefully if error occurs (non-blocking)
- Logs warnings without throwing exceptions

### 4. **Flutter Model** (`flutter-frontend-app/lib/models/migration_data.dart`)

Added `detectSensitiveColumns()` method that:
- Wraps the API service call
- Returns structured result with sensitive column data
- Handles errors gracefully

### 5. **Warning Widget** (`flutter-frontend-app/lib/widgets/sensitive_data_warning.dart`)

Created `SensitiveDataWarning` widget featuring:

#### Visual Design:
- **Red background** with red border indicating high-severity warning
- **Warning icon** (🔴) for visibility
- **Severity badges**: HIGH and MEDIUM badges for each column

#### Content:
- Summary count of sensitive columns
- Detailed list of each sensitive column with:
  - Column name and severity level
  - Reason why the data is sensitive
  - Recommendation for handling
  - Number and percentage of missing values
- General warning about AI imputation risks
- Guidance on manual verification
- Option to dismiss warning

### 6. **Integration into Evolutionary Cleaning Section** 

Modified `flutter-frontend-app/lib/widgets/evolutionary_cleaning_section.dart`:

- Added state variables to track sensitive columns
- Added `initState()` to load sensitive columns when widget initializes
- Added `_loadSensitiveColumns()` method
- Integrated warning display in the UI:
  - Shows loading indicator while checking
  - Displays `SensitiveDataWarning` when sensitive columns detected
  - Allows users to dismiss the warning

## Warning Messages

### For Date of Birth Columns:
```
"Date of Birth - Cannot be reliably imputed. Missing dates should be 
obtained from original source."
```

### For ID/NIC Columns:
```
"Identification Number (NIC/Passport/ID) - These are unique identifiers 
that cannot be imputed. Missing values must be verified from original 
documents."
```

### General Imputation Warning:
```
"AI imputation may create false or invalid values for these columns. 
Consider: 
1) Manually verifying imputed values
2) Excluding these columns from cleaning
3) Obtaining original data from source documents."
```

## User Workflow

1. User uploads data file
2. User navigates to "AI Cleaning" section
3. System automatically detects sensitive columns
4. Warning is displayed with:
   - List of sensitive columns found
   - Severity levels
   - Specific reasons for each
   - Recommendations
5. User can:
   - Review the warning
   - Dismiss it and proceed with cleaning
   - Exclude sensitive columns manually
   - Take data to original source for verification

## Configuration

### Sensitivity Keywords

To add more sensitive keywords, edit `data_fitness.py`:

```python
date_keywords = ['birth', 'dob', 'birthday', ...]
id_keywords = ['nic', 'nid', 'passport', ...]
```

### Uniqueness Threshold

To adjust the ID detection threshold, modify in `data_fitness.py`:

```python
unique_ratio = len(non_null.unique()) / len(non_null)
if unique_ratio > 0.95:  # Adjust this threshold
```

## Technical Details

### Severity Levels:
- **HIGH**: Cannot be reliably imputed (Date of Birth, ID numbers)
- **MEDIUM**: Should be carefully verified (Phone numbers, contact info)

### Detection Priority:
1. Column name pattern matching (highest priority)
2. Data pattern analysis (high uniqueness ratio)
3. Combined heuristics

## Testing

### Test Cases:

1. **Dataset with Date of Birth column**
   - Column should be detected as HIGH severity
   - Missing values should be counted
   - Recommendation should be shown

2. **Dataset with NIC/Passport column**
   - Column should be detected as HIGH severity
   - Unique values should trigger detection

3. **Dataset with no sensitive columns**
   - Warning should not display
   - Cleaning can proceed normally

4. **Dataset with phone numbers**
   - Should be detected as MEDIUM severity
   - Context matters (personal vs. work)

### Sample Test Data:

```csv
id,name,date_of_birth,nic_number,phone,salary
1,John,1990-05-15,123-456-789,0300-1234567,50000
2,Jane,,123-456-790,,60000
3,Bob,1985-03-20,,0300-1234569,70000
```

Expected: 2 HIGH severity warnings (date_of_birth, nic_number)

## Benefits

1. **User Protection**: Warns users about unreliable imputation
2. **Data Integrity**: Prevents invalid synthetic data from being created
3. **Compliance**: Meets requirements for sensitive data handling
4. **Transparency**: Shows exactly which columns are flagged and why
5. **Guidance**: Provides clear recommendations for each sensitive column
6. **Non-Blocking**: Feature is non-critical, doesn't prevent workflow

## Future Enhancements

1. Add user-defined sensitive column list
2. Allow excluding specific columns from cleaning
3. Add hashing/encryption option for sensitive data
4. Machine learning model for better pattern detection
5. Integration with data governance policies
6. Audit logging for sensitive column handling
7. Custom severity rules per organization

## Error Handling

- **Backend unavailable**: Warning silently skips, cleaning proceeds
- **Malformed response**: Treated as no sensitive columns found
- **API timeout**: Warning shows loading state, defaults to safe behavior

## Files Modified

1. `python-backend/data_fitness.py` - Added sensitive column detection
2. `python-backend/server.py` - Added `/fitness/sensitive-columns` endpoint
3. `flutter-frontend-app/lib/services/api_service.dart` - Added API call
4. `flutter-frontend-app/lib/models/migration_data.dart` - Added model method
5. `flutter-frontend-app/lib/widgets/evolutionary_cleaning_section.dart` - Integration

## Files Created

1. `flutter-frontend-app/lib/widgets/sensitive_data_warning.dart` - Warning widget

## Deployment Notes

- No database migrations required
- Backward compatible with existing data
- No breaking changes to existing APIs
- Can be deployed independently
- Feature is gracefully degraded if backend not available

---

**Version**: 1.0  
**Last Updated**: December 7, 2025  
**Status**: Ready for Testing
