# Data Quality Analysis - Practical Examples

## Example 1: Your Exact Use Case

### Input Data
```
Prices    Product    Procurement
10        Apple      2024-01-09 00:00:00
25        Orange     
23        Mango      2024-01-11 00:00:00
abc       Banana     2024-01-12 00:00:00
32        Avacado    2024-01-13 00:00:00
42        12         2024-01-14 00:00:00
22        Plum       2024-01-15 00:00:00
14        Grapes     2024-01-16 00:00:00
15        Worm       2024-01-17 00:00:00
```

### Analysis Output

**Column Types Detected:**
- `Prices`: `numeric` (values: 10, 25, 23, 32, 42, 22, 14, 15)
- `Product`: `string` (text values)
- `Procurement`: `datetime` (date values)

**Error Cells Identified:**

```json
{
  "error_cells": [
    {
      "row": 2,
      "col": 2,
      "issues": ["missing_value"]
    },
    {
      "row": 4,
      "col": 0,
      "issues": ["non_numeric"]
    },
    {
      "row": 6,
      "col": 1,
      "issues": ["mixed_content"]
    }
  ]
}
```

### Frontend Display

| Prices | Product | Procurement |
|--------|---------|------------|
| 10 | Apple | 2024-01-09 00:00:00 |
| 25 | 🔴Orange | 🔴(empty) |
| 23 | Mango | 2024-01-11 00:00:00 |
| 🔴abc | Banana | 2024-01-12 00:00:00 |
| 32 | Avacado | 2024-01-13 00:00:00 |
| 42 | 🔴12 | 2024-01-14 00:00:00 |
| 22 | Plum | 2024-01-15 00:00:00 |
| 14 | Grapes | 2024-01-16 00:00:00 |
| 15 | Worm | 2024-01-17 00:00:00 |

---

## Example 2: E-Commerce Order Data

### Input Data
```
OrderID    Customer        Amount    OrderDate        Status
1001       John Doe        150.50    2024-01-15      completed
1002       Jane Smith      200.00    2024-01-16      shipped
1003       Bob Johnson     NOT_PAID  2024-01-17      pending
1004       Alice Brown     85.99     InvalidDate     completed
1005       null            120.00    2024-01-19      pending
```

### Analysis Results

**Column Types:**
- `OrderID`: `numeric` 
- `Customer`: `string`
- `Amount`: `numeric`
- `OrderDate`: `datetime`
- `Status`: `string`

**Errors:**
- Row 3, Col 2: "NOT_PAID" → `non_numeric`, `mixed_content`
- Row 4, Col 3: "InvalidDate" → `invalid_datetime`
- Row 5, Col 1: "null" → `null_string`

**User Action:**
- Fix amount in row 3 (non-numeric)
- Fix date in row 4 (invalid format)
- Fill customer name in row 5
- Data never fails to load ✓

---

## Example 3: Scientific Data with Outliers

### Input Data
```
Temperature    Humidity    PressureMB    LocationID
22.5           65.3        1013.25      SENSOR_A
21.8           68.1        1013.18      SENSOR_B
23.2           62.5        1013.45      SENSOR_C
999999         70.2        1013.32      SENSOR_D
20.5           75.8        1012.95      SENSOR_E
```

### Analysis Results

**Column Types:**
- All detected as `numeric`

**Errors:**
- Row 4, Col 0: 999999 → `suspicious_value`

**Why Suspicious:**
- Value is far outside normal range (normal: ~20°C)
- Threshold: < -999,999 or > 999,999
- Flagged for human review

**User Action:**
- Check if it's a real measurement or data entry error
- Could be typo (99 instead of 999999)
- Data loads but is marked for review ✓

---

## Example 4: Mixed Data Types in Single Column

### Input Data
```
Product         Quantity    Notes
Widget-A        10          "Good stock"
Widget-B        20          "Low stock"
Widget-C        N/A         "Out of stock"
Widget-D        BULK        "Restocking"
Widget-E        35          "Oversupply"
```

### Analysis Results

**Column Types:**
- `Product`: `string`
- `Quantity`: `numeric` (inferred from 10, 20, 35)
- `Notes`: `string`

**Errors Found:**
- Row 3, Col 1: "N/A" → `null_string`, `non_numeric`
- Row 4, Col 1: "BULK" → `non_numeric`, `mixed_content`

**Visual Result:**

| Product | Quantity | Notes |
|---------|----------|-------|
| Widget-A | 10 | "Good stock" |
| Widget-B | 20 | "Low stock" |
| Widget-C | 🔴N/A | "Out of stock" |
| Widget-D | 🔴BULK | "Restocking" |
| Widget-E | 35 | "Oversupply" |

---

## Example 5: All Empty Column

### Input Data
```
Name           Email              Phone         Website
John Doe       john@email.com     555-1234      
Jane Smith     jane@email.com     555-5678      
Bob Johnson    bob@email.com      555-9012      
Alice Brown    alice@email.com    555-3456      
```

### Analysis Results

**Column Types:**
- `Name`: `string`
- `Email`: `string`
- `Phone`: `string`
- `Website`: `unknown` (all values missing)

**Errors:**
- All 4 rows, Column 3 → `missing_value`

**What To Do:**
- Column is completely empty
- Either delete it or fill in website URLs
- All cells marked but loading succeeds ✓

---

## Example 6: Date Format Variations

### Input Data
```
EventID    EventName          EventDate
1          Annual Meeting     2024-01-15
2          Quarterly Review   01/15/2024
3          Team Standup       15-Jan-2024
4          Budget Planning    not a date
5          Planning Session   2024-01-19
```

### Analysis Results

**Column Type:**
- `EventDate`: `datetime` 
  - Reason: Rows 1, 3, 5 parse successfully (50%+ threshold)

**Errors:**
- Row 4, Col 2: "not a date" → `invalid_datetime`
- Rows 2, 3: Different formats but still parse → No error

**Frontend Display:**
- Rows 2-3 with different date formats: ✓ No error
- Row 4: 🔴 Marked as invalid datetime
- User can apply "Date Format Conversion" to fix if needed

---

## Example 7: Real-World Messy CSV

### Input Data (from Excel export with issues)
```
SKU            Description        ListPrice    CostPrice    InStock
SKU-001        Product A          99.99        45.50        TRUE
SKU-002        Product B          149.99       70.25        FALSE
SKU-003        Product C          null         55.00        N/A
SKU-004        Product D          -99.99       40.00        YES
SKU-005        Product E          ERROR        60.00        
SKU-006        Product F          199.99       UNKNOWN      10
SKU-007        Product G          299.99       150.50       MAYBE
```

### Analysis Results

**Column Types:**
- `SKU`: `string`
- `Description`: `string`
- `ListPrice`: `numeric`
- `CostPrice`: `numeric`
- `InStock`: `string`

**Total Errors Found: 8**

| Issue | Row | Col | Data |
|-------|-----|-----|------|
| missing_value | 3 | 2 | null |
| null_string | 3 | 4 | N/A |
| suspicious_value | 4 | 2 | -99.99 |
| non_numeric | 5 | 2 | ERROR |
| missing_value | 5 | 4 | (empty) |
| null_string | 6 | 3 | UNKNOWN |
| mixed_content | 7 | 4 | MAYBE |

**Frontend View:**
```
🔴 Red cells appear immediately after upload
Users can:
  - Hover for warning: "⚠️ Data quality issue detected"
  - Use ETL tools to fix specific columns
  - Run AI cleaning if enabled
```

---

## Example 8: Numeric Data with Commas (European Format)

### Input Data
```
Amount         Currency    Date
"1.234,56"     EUR         2024-01-15
"2.500,00"     EUR         2024-01-16
"abc,de"       EUR         2024-01-17
"3.100,25"     EUR         2024-01-18
```

### Analysis Results

**Column Type:** `numeric`
- Pandas auto-detection might interpret as `float64`
- But with string format containing non-ASCII commas

**Errors:**
- Row 3, Col 0: "abc,de" → `non_numeric`

**Note:**
- Rows 1-2, 4: Format with comma as decimal separator
- Analyzer marks row 3 as problematic
- Other rows pass because float() can usually parse numeric strings
- If all rows were in this format, may need locale-aware parsing

---

## Example 9: URL/Email Validation

### Input Data
```
Email                  Website                Phone
john@example.com       https://john.com       (555) 123-4567
jane@invalid           www.jane.org           555-123-4568
bob@example.com        not a url              +1 555-123-4569
alice@test.co.uk       https://alice.co      555 123 4570
```

### Analysis Results

**Column Types:**
- All detected as `string` (correct)

**Current Analyzer Result:**
- No errors flagged (all are valid strings)

**Note:**
- Current version doesn't validate email/URL format
- Future enhancement could add pattern validation
- For now, accepts any non-empty string as valid

**If Email Validation Added:**
- Row 2, Col 0: "jane@invalid" → `invalid_email` (future)
- Row 3, Col 1: "not a url" → `invalid_url` (future)

---

## Example 10: Time Series Data with Missing Points

### Input Data
```
Timestamp              Value     Sensor
2024-01-15 10:00:00   23.5      A
2024-01-15 10:15:00   24.1      A
2024-01-15 10:30:00            A
2024-01-15 10:45:00   25.2      B
2024-01-15 11:00:00   26.0      
```

### Analysis Results

**Column Types:**
- `Timestamp`: `datetime`
- `Value`: `numeric`
- `Sensor`: `string`

**Errors:**
- Row 3, Col 1: Empty → `missing_value`
- Row 5, Col 2: Empty → `missing_value`

**Time Series Analysis:**
- 2 missing values in dataset
- Data loads but marked for interpolation
- User can:
  - Delete rows with missing values
  - Interpolate (linear, forward fill, etc.)
  - Leave as-is if acceptable for analysis

**Frontend:**
```
2024-01-15 10:00:00   23.5      A
2024-01-15 10:15:00   24.1      A
2024-01-15 10:30:00   🔴        A
2024-01-15 10:45:00   25.2      B
2024-01-15 11:00:00   26.0      🔴
```

---

## Common Patterns & Solutions

### Pattern 1: Typo in Numeric Column
```
Input:  [10, 25, 2a, 40]
Error:  Row 3 → non_numeric
Fix:    Replace "2a" with "23"
Status: Data loads, user can see and fix
```

### Pattern 2: Copy-Paste Errors
```
Input:  ["2024-01-15", "", "2024-01-17", "null"]
Errors: Row 2 → missing_value
        Row 4 → null_string
Fix:    Fill empty, replace "null" string
Status: All marked, no crashes
```

### Pattern 3: Format Inconsistency
```
Input:  [1000, 2_000, 3,000, "4000"]
Errors: May vary by system locale
Fix:    Standardize format before upload
Status: Analyzer is locale-aware through pandas
```

### Pattern 4: Hidden Characters
```
Input:  ["Product", "Product ", "Product\n", "Produc\t"]
Analysis: All parsed as string (correct)
Status: No error if expected type is string
Note:   Whitespace-only cells are missing_value
```

### Pattern 5: Mixed Unit Columns
```
Input:  ["100 kg", "50 kg", "75", "80 lbs"]
Error:  Row 3, 4 → mixed_content or non_numeric
Fix:    Extract numbers or standardize units
Status: Marked for review/fixing
```

---

## Best Practices

### 1. Upload Clean Data When Possible
- Remove obvious errors before upload
- Data still loads even if dirty

### 2. Understand Column Types
- Check inferred `column_types` in response
- Confirm they match your expectations
- Manually override if needed

### 3. Act on Red Cells
- Don't ignore cells marked in red
- Either fix them or document why they're acceptable
- Use ETL tools or AI cleaning for bulk fixes

### 4. Leverage Error Information
```json
{
  "row": 4,           // Exact row number for lookup
  "col": 0,           // Exact column to fix
  "issues": ["..."]   // Specific problem type
}
```

### 5. Test with Sample Data First
- Upload 10-20 rows to check types
- Confirm column inference is correct
- Then upload full dataset

### 6. Document Data Quality
- Keep quality reports for audit trail
- Track how many cells were flagged
- Monitor improvement over time
