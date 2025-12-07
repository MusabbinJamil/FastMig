# 🚀 ETL Operations Quick Start Guide

## What's New?
Your FastMig app now includes **ETL operations** and an improved **Step Recording** feature!

## 🎯 How to Use in 3 Easy Steps

### Step 1: Load Your Data
1. Click **"Load Data"** in the side menu
2. Upload your CSV or Excel file
3. Wait for data to load

### Step 2: Clean & Transform (NEW!)
1. Click **"Record Steps"** in the side menu
2. You'll see two panels:
   - **Top Panel**: Step Recording controls
   - **Bottom Panel**: ETL Operations

3. Choose an operation from the dropdown:
   - **Remove Null Rows** - Delete rows with missing data
   - **Remove Duplicates** - Remove duplicate records
   - **Trim Whitespace** - Clean extra spaces
   - **Find & Replace** - Replace specific values
   - **Fill Nulls** - Fill missing values
   - **Change Case** - Convert text to UPPER/lower/Title
   - **Filter Rows** - Keep only matching rows
   - **Sort Data** - Sort by column values

4. Fill in the parameters
5. Click **"Execute Operation"**

### Step 3: Save Your Pipeline (Optional)
1. Click **"Start Recording"** (top panel)
2. Perform multiple operations
3. Click **"Stop Recording"**
4. Click **"Save Steps"**
5. Give it a name like "My Cleanup Pipeline"
6. Replay on future datasets!

## 💡 Quick Examples

### Example 1: Basic Cleaning (2 minutes)
```
1. Remove Null Rows → Select all columns → Execute
2. Trim Whitespace → Select text columns → Execute
3. Remove Duplicates → Select ID column → Keep 'first' → Execute
✅ Done! Your data is clean.
```

### Example 2: Text Standardization (3 minutes)
```
1. Trim Whitespace → Select all text columns → Execute
2. Change Case → Select 'email' column → 'lower' → Execute
3. Change Case → Select 'name' column → 'title' → Execute
4. Find & Replace → Select 'status' → Find 'canceled' → Replace 'cancelled' → Execute
✅ Done! Consistent formatting.
```

### Example 3: Data Filtering (2 minutes)
```
1. Filter Rows → Select 'amount' → '>' → 1000 → Execute
2. Sort Data → Select 'date' → Descending → Execute
3. Fill Nulls → Select 'customer' → Forward fill → Execute
✅ Done! Filtered and sorted.
```

## 🎬 Recording a Pipeline

Want to save time? Record your steps!

```
1. Click "Start Recording" (🔴 button)
2. Do your cleaning operations (they're auto-recorded)
3. Click "Stop Recording"
4. Click "View Steps" to review
5. Click "Save Steps" and name it
6. Next time: Click "Replay Steps" on new data!
```

**Example Pipeline:**
```
Name: "Sales Data Cleanup"
Steps:
1. Remove Null Rows
2. Trim Whitespace (all columns)
3. Change Case (email → lower)
4. Sort Data (date → descending)
5. Remove Duplicates (order_id → keep first)
```

## 🎨 UI Quick Reference

### Where Everything Is

**Side Menu:**
- 📂 Load Data
- 🔄 Convert Fields
- 🎥 **Record Steps** ← NEW! Your ETL hub
- 📊 View Data
- 💾 Export Data
- 🏥 Data Fitness
- ✨ AI Cleaning
- ⚙️ Settings
- ❓ Help

**Record Steps Screen:**
```
┌─────────────────────────────────────┐
│   STEP RECORDING                    │
│   ⚪ Not Recording | ● Recording   │
│   [Start Recording] [Stop]          │
│   [View Steps] [Save Steps]         │
├─────────────────────────────────────┤
│   ETL OPERATIONS                    │
│   Select Operation: [Dropdown ▼]    │
│   ┌───────────────────────────────┐ │
│   │  Dynamic Parameter Form       │ │
│   │  (changes based on operation) │ │
│   └───────────────────────────────┘ │
│   [Execute Operation]               │
└─────────────────────────────────────┘
```

## 🎓 Tips for Success

### Do's ✅
- ✅ Load data first before ETL operations
- ✅ Use "View Data" to check results after each operation
- ✅ Test operations before recording a pipeline
- ✅ Give pipelines descriptive names
- ✅ Start with Remove Nulls, end with Sort
- ✅ Save your work frequently

### Don'ts ❌
- ❌ Don't apply operations without data loaded
- ❌ Don't skip viewing results
- ❌ Don't record while testing
- ❌ Don't use special characters in pipeline names
- ❌ Don't apply Mean/Median to text columns
- ❌ Don't forget to Stop Recording before saving

## 🔧 Troubleshooting

**Problem**: "No data loaded" error  
**Solution**: Go to "Load Data" and upload a file first

**Problem**: Operation button is grayed out  
**Solution**: Fill in all required parameters

**Problem**: Column not in dropdown  
**Solution**: Reload data or check "View Data" screen

**Problem**: Can't see changes  
**Solution**: Go to "View Data" screen to see updated data

**Problem**: Recording won't save  
**Solution**: Stop recording first, then click "Save Steps"

## 📊 Operation Cheat Sheet

| Operation | Best For | Example |
|-----------|----------|---------|
| Remove Nulls | Initial cleaning | Remove incomplete records |
| Remove Duplicates | Data quality | Remove duplicate orders |
| Trim Whitespace | Text cleanup | Fix "  John  " → "John" |
| Find & Replace | Fix typos | "canceled" → "cancelled" |
| Fill Nulls | Missing data | Fill empty prices with average |
| Change Case | Standardization | Email addresses to lowercase |
| Filter Rows | Subsetting | Only 2024 records |
| Sort Data | Organization | Sort by date |

## 🚀 Advanced: Replay Pipeline

Once you've saved a pipeline:

```
1. Load NEW data file
2. Go to "Record Steps"
3. Click "Replay Steps" (future feature)
4. Select saved pipeline name
5. Watch it apply all steps automatically!
```

*Note: Replay feature coming in next update!*

## 📚 Need More Help?

- **User Guide**: See `ETL_FEATURES_README.md`
- **Technical Docs**: See `FRONTEND_ETL_IMPLEMENTATION.md`
- **Backend Docs**: See `python-backend/docs/ETL_OPERATIONS_GUIDE.md`

## ⚡ Pro Tips

1. **Combine Operations**: Remove nulls → Trim → Dedupe → Sort
2. **Name Wisely**: Use project_purpose_v1 (e.g., "sales_cleanup_v1")
3. **Test First**: Try operations individually before recording
4. **View Often**: Check results in "View Data" after each step
5. **Export Checkpoints**: Save data after major transformations

---

**Ready to clean your data?**  
👉 Go to "Record Steps" and start transforming! 🎉

**Version**: 1.0  
**Last Updated**: 2024
