# Flutter Frontend - AI Data Quality Features

This document describes the new AI-powered data quality features in the FastMig Flutter frontend.

## New Features

### 1. Data Fitness Evaluation

**Location:** AI Features → Data Fitness

**Purpose:** Assess the health and quality of your data records.

**Features:**
- Evaluate overall fitness score (0-100%) for your dataset
- View detailed breakdown by health category:
  - Excellent (95-100%)
  - Good (80-95%)
  - Fair (60-80%)
  - Poor (40-60%)
  - Critical (0-40%)
- Identify records that need cleaning
- Real-time visual indicators and progress bars

**How to Use:**
1. Load your data file
2. Navigate to "Data Fitness" from the side menu
3. Click "Evaluate Fitness" button
4. Review the fitness summary and health breakdown

### 2. Evolutionary Data Cleaning

**Location:** AI Features → AI Cleaning

**Purpose:** Use evolutionary algorithms to intelligently clean and impute missing values.

**Available Algorithms:**

#### Hybrid Method (Recommended)
- Automatically selects the best algorithm per column type
- Optimal for mixed datasets
- No parameter tuning required

#### Genetic Algorithm (GA)
- Evolves populations using selection, crossover, and mutation
- Best for: Mixed data types, general-purpose cleaning

#### Particle Swarm Optimization (PSO)
- Particles "swarm" toward optimal imputation values
- Best for: Numeric data, continuous values

#### Differential Evolution (DE)
- Robust global optimization
- Best for: Numeric data with complex distributions

#### Evolution Strategy (ES)
- Self-adaptive mutation for consistent improvements
- Best for: When you need reliable, incremental improvements

**Features:**
- Compare all 5 methods to find the best for your data
- Track AI modifications with "Modified_by_AI" column
- View before/after fitness improvements
- See modification statistics and rates
- Restore original data if needed

**How to Use:**
1. Load and evaluate fitness of your data first
2. Navigate to "AI Cleaning" from the side menu
3. Select a cleaning method (or use Hybrid)
4. Enable/disable AI modification tracking
5. Click "Clean Data" to process
6. Optional: Click "Compare Methods" to find the best algorithm
7. Review the cleaning report showing improvements

### 3. AI Data Quality Workflow (Combined View)

**Location:** Can be accessed programmatically

**Purpose:** Guided workflow for complete data quality improvement.

**Workflow Steps:**

1. **Evaluate Fitness**
   - Assess current data health
   - Identify issues and missing values

2. **Clean Data**
   - Select and apply cleaning algorithm
   - Track AI modifications

3. **Verify & Export**
   - Review cleaned data
   - Re-evaluate fitness to confirm improvements
   - Export cleaned data
   - Restore original if needed

## Technical Implementation

### New API Endpoints Used

```dart
// Evaluate data fitness
POST /fitness/evaluate

// Get specific record fitness
GET /fitness/record/<row_index>

// Clean data with evolutionary algorithms
POST /clean/evolutionary
{
  "method": "hybrid|ga|pso|de|es",
  "save_result": true,
  "track_modifications": true,
  "parameters": {}
}

// Compare all cleaning methods
POST /clean/compare

// Restore original data
POST /data/restore
```

### New Widgets

- `FitnessEvaluationSection`: Displays fitness evaluation results
- `EvolutionaryCleaningSection`: Provides cleaning algorithm interface
- `AiDataQualityScreen`: Guided workflow combining both features

### Updated Models

**MigrationData** - New methods:
- `evaluateDataFitness()`: Evaluate fitness of loaded data
- `getRecordFitness(int rowIndex)`: Get fitness of specific record
- `cleanDataEvolutionary()`: Clean data with selected algorithm
- `compareCleaningMethods()`: Compare all algorithms
- `restoreOriginalData()`: Restore data before cleaning

**ApiService** - New methods:
- `evaluateFitness()`: API call for fitness evaluation
- `getRecordFitness()`: API call for record fitness
- `cleanDataEvolutionary()`: API call for cleaning
- `compareCleaningMethods()`: API call for comparison
- `restoreOriginalData()`: API call for data restoration

## UI Features

### Visual Indicators

- **Fitness Colors:**
  - Green: Excellent fitness (95-100%)
  - Light Green: Good fitness (80-95%)
  - Orange: Fair fitness (60-80%)
  - Deep Orange: Poor fitness (40-60%)
  - Red: Critical fitness (0-40%)

### Interactive Elements

- Method selection cards with icons and descriptions
- Progress bars for health status breakdown
- Summary cards showing key metrics
- Comparison dialog with best method highlighting
- Responsive buttons with loading states

### User Experience

- Clear visual feedback during processing
- Success/error messages with SnackBars
- Confirmation dialogs for destructive actions
- Smooth transitions between screens
- Real-time data updates with Provider

## Best Practices

### Recommended Workflow

1. **Always evaluate fitness first**
   - Understand your data quality before cleaning
   - Identify which records need attention

2. **Use Hybrid method for first attempt**
   - It automatically selects the best algorithm
   - Requires no parameter tuning

3. **Compare methods for optimal results**
   - If time permits, compare all algorithms
   - Use the best performing method

4. **Enable modification tracking**
   - Keep "Track AI Modifications" enabled
   - Maintains transparency about AI changes
   - Useful for auditing and compliance

5. **Re-evaluate after cleaning**
   - Verify fitness improvements
   - Ensure data quality goals are met

6. **Export or restore**
   - Export if satisfied with results
   - Restore original if changes are unsatisfactory

## Data Privacy & Transparency

### Modified_by_AI Column

When "Track AI Modifications" is enabled:
- A new column `Modified_by_AI` is added to your dataset
- Records with AI-imputed values are marked `True`
- Original records remain marked `False`
- The column is preserved in exports
- Provides full transparency about AI modifications

### Benefits

- **Compliance:** Meet regulatory requirements for AI disclosure
- **Auditing:** Track which data was AI-generated
- **Quality Control:** Separate original from imputed data
- **Trust:** Stakeholders can see exactly what was modified

## Performance Considerations

### Computation Time

- **Fitness Evaluation:** Fast (< 1 second for most datasets)
- **Single Method Cleaning:** Moderate (5-30 seconds depending on size)
- **Method Comparison:** Longer (5x single method time)

### Optimization Tips

1. Start with small datasets to test
2. Use Hybrid method to avoid testing all algorithms
3. Compare methods on sample data first
4. Monitor progress with loading indicators

## Troubleshooting

### "No data loaded" Error
- Ensure you've loaded a file from "Load Data" section
- Check backend connection status

### Cleaning takes too long
- Try Hybrid method (auto-optimized)
- Use smaller datasets for testing
- Check backend server logs for issues

### Fitness not improving
- Verify data has actual missing values
- Try different algorithms with Compare Methods
- Some data may be inherently low quality

### Backend Connection Issues
- Ensure Python backend is running
- Check `http://localhost:5000/health` endpoint
- Verify firewall settings

## Future Enhancements

Potential additions:
- Custom fitness thresholds
- Batch processing for large files
- Advanced algorithm parameters
- Visualization of distribution preservation
- Export fitness reports
- Historical tracking of cleaning operations

## Dependencies

Required Flutter packages:
- `provider`: State management
- `http`: API communication
- `file_picker`: File selection

Backend requirements:
- Python backend with evolutionary cleaning module
- Required Python packages: numpy, pandas, scipy

## Support

For issues or questions:
1. Check backend server logs
2. Verify all dependencies are installed
3. Test with sample data first
4. Check the main project README

---

**Version:** 1.0  
**Last Updated:** November 1, 2025  
**Author:** FastMig Development Team
