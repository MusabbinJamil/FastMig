
# GA Frontend Integration Guide

## Overview
The FastMig Flutter frontend has been enhanced with comprehensive Genetic Algorithm (GA) and Grammatical Evolution (GE) capabilities. This guide covers the new UI components, API integration, and usage patterns.

## New Components Added

### 1. **GA Configuration Model** (`ga_config_model.dart`)
Models for GA configuration and execution:
- `GAConfigModel`: Complete GA configuration with parameters
  - Population size, generations, mutation/crossover rates
  - Selection, crossover, and mutation methods
  - Early stopping and convergence settings
  - Includes preset configurations (Fast, Balanced, Quality)
  
- `GAMetricsModel`: Generation-by-generation metrics
  - Best, worst, average fitness scores
  - Fitness variance and population statistics
  - Timestamp and best individual tracking
  
- `ExpressionTreeNode`: Expression tree visualization
  - Recursive tree structure with node types
  - Fitness contribution tracking per node
  - Support for operators, functions, and operands
  
- `GrammarConfigModel`: Grammar and rule configuration
  - Grammar type selection (standard, boolean, trigonometric, etc.)
  - Custom grammar rules (BNF format)
  - Max tree depth and type checking settings

### 2. **GA Configuration Panel** (`ga_configuration_panel.dart`)
Interactive UI for GA parameter tuning:
```dart
GAConfigurationPanel(
  initialConfig: GAConfigModel(),
  onConfigChanged: (config) { /* Handle config changes */ },
  onApplyPressed: () { /* Apply configuration */ },
)
```

**Features:**
- Quick preset buttons (Fast, Balanced, Quality)
- Population parameter controls
- Evolution operator selection
- Convergence settings
- Real-time configuration validation

### 3. **GA Progress Visualization** (`ga_progress_visualization.dart`)
Real-time progress visualization during evolution:
```dart
GAProgressVisualization(
  metricsHistory: gaMetrics,
  isRunning: isEvolving,
  progressPercent: 0.75,
  onStop: () { /* Stop evolution */ },
)
```

**Features:**
- Overall progress bar with percentage
- Metrics grid (generation, best fitness, avg fitness, population)
- Generation-by-generation fitness chart
- Detailed metrics table with scrolling
- Play/pause status indicator

### 4. **Grammar Rule Selection Panel** (`grammar_rule_selection_panel.dart`)
UI for managing grammar rules and derivation trees:
```dart
GrammarRuleSelectionPanel(
  initialConfig: GrammarConfigModel(),
  onConfigChanged: (config) { /* Handle grammar changes */ },
  onApplyPressed: () { /* Apply grammar */ },
)
```

**Features:**
- Grammar type presets (Standard, Boolean, Trigonometric, Data Cleaning, Statistical)
- Tree parameter controls (max depth, type checking)
- Rule management (add, remove, view rules)
- Visual rule enumeration
- Max nodes calculation display

### 5. **Expression Tree Visualization** (`expression_tree_visualization.dart`)
Interactive visualization of evolved expressions:
```dart
ExpressionTreeVisualization(
  rootNode: treeNode,
  rawExpression: 'sin(x) + cos(y)',
  fitnessScore: 92.5,
  isLoading: false,
)
```

**Features:**
- Interactive tree visualization with zoom/pan
- Node selection and detail display
- Fitness contribution tracking per node
- Custom painter for tree rendering
- Children enumeration and navigation
- Error handling and empty state displays

### 6. **GA Evolution Screen** (`ga_evolution_screen.dart`)
Complete integration screen with 4 tabs:

#### Tab 1: Configuration
- Nested tabs for GA parameters and grammar rules
- Configuration summary display
- Start Evolution button

#### Tab 2: Progress
- Real-time fitness progression
- Generation-by-generation metrics
- Stop button for early termination

#### Tab 3: Expression Tree
- Visual representation of best solution
- Interactive node exploration
- Fitness scoring display

#### Tab 4: Analysis
- Population fitness distribution
- Unhealthy/healthy record statistics
- Detailed statistics table

### 7. **API Service Extensions** (`api_service.dart`)
New API endpoints for GA operations:

```dart
// Run GA evolution with full configuration
Future<Map<String, dynamic>> runGeneticAlgorithmEvolution({
  required Map<String, dynamic> gaConfig,
  required Map<String, dynamic> grammarConfig,
  bool trackProgress = true,
})

// Get GA evolution progress (for streaming)
Future<Map<String, dynamic>> getGAProgress()

// Analyze population fitness distribution
Future<Map<String, dynamic>> analyzePopulationFitness({
  double fitnessThreshold = 85.0,
})

// Get available grammar presets
Future<Map<String, dynamic>> getGrammarPresets()

// Parse and validate expression tree
Future<Map<String, dynamic>> parseExpressionTree(Map<String, dynamic> treeData)
```

## Navigation Integration

### Main Screen Updates
The GA Evolution feature is integrated into the main ribbon:
- Added "GA Evolution" button in "AI Features" section
- Color: Deep Purple
- Icon: Biotech
- Navigation: Opens full-screen GA Evolution Screen

```dart
_RibbonButton(
  icon: Icons.biotech,
  label: 'GA Evolution',
  color: Colors.deepPurple,
  onPressed: () => _navigateToGAScreen(),
  featureKey: 'ga',
)
```

## Usage Workflow

### 1. **Basic GA Evolution**
```dart
// Initialize models
final gaConfig = GAConfigModel();
final grammarConfig = GrammarConfigModel.withPreset('standard');

// Run evolution
final result = await apiService.runGeneticAlgorithmEvolution(
  gaConfig: gaConfig.toJson(),
  grammarConfig: grammarConfig.toJson(),
);

// Process results
final metrics = result['fitness_history']
    .map((m) => GAMetricsModel.fromJson(m))
    .toList();
final tree = ExpressionTreeNode.fromJson(result['expression_tree']);
```

### 2. **Custom Configuration**
```dart
// Adjust parameters
var config = GAConfigModel()
    .copyWith(
      populationSize: 50,
      generations: 200,
      mutationRate: 0.08,
      crossoverRate: 0.85,
    );

// Add custom grammar rules
var grammar = GrammarConfigModel()
    .copyWith(
      grammarType: 'custom',
      rules: [
        '<expr> ::= <expr> + <term> | <term>',
        '<term> ::= <term> * <factor> | <factor>',
      ],
    );
```

### 3. **Monitor Evolution Progress**
```dart
// Periodically check progress
while (isEvolving) {
  final progress = await apiService.getGAProgress();
  setState(() {
    _metricsHistory = progress['metrics'];
    _evolutionProgress = progress['progress_percent'];
  });
  await Future.delayed(Duration(seconds: 1));
}
```

## Configuration Presets

### Fast (Quick Results)
- Population Size: 20
- Generations: 30
- Mutation Rate: 15%
- Crossover Rate: 75%
- Early Stopping: 5 generations

### Balanced (Recommended)
- Population Size: 30
- Generations: 100
- Mutation Rate: 10%
- Crossover Rate: 80%
- Early Stopping: 10 generations

### Quality (Thorough)
- Population Size: 50
- Generations: 200
- Mutation Rate: 8%
- Crossover Rate: 85%
- Early Stopping: 15 generations

## Grammar Presets

### Standard (Arithmetic)
Basic mathematical expressions with +, -, *, /

### Boolean
Logical expressions with AND, OR, NOT comparisons

### Trigonometric
Mathematical functions: sin, cos, tan, sqrt, etc.

### Data Cleaning
Operations: filter, transform, aggregate

### Statistical
Statistical functions: mean, std, median, variance, etc.

## API Response Structure

### GA Evolution Response
```json
{
  "success": true,
  "evolved_data": [[...], [...], ...],
  "metrics": {
    "generations_completed": 100,
    "convergence_achieved": true,
    "final_best_fitness": 92.5
  },
  "expression_tree": {
    "value": "root",
    "type": "operator",
    "children": [...]
  },
  "fitness_history": [
    {
      "generation": 1,
      "best_fitness": 45.2,
      "worst_fitness": 10.1,
      "average_fitness": 28.5,
      "fitness_variance": 145.3
    },
    ...
  ],
  "convergence_info": {
    "converged": true,
    "convergence_generation": 87
  }
}
```

### Fitness Analysis Response
```json
{
  "success": true,
  "unhealthy_records": 45,
  "healthy_records": 455,
  "fitness_distribution": {
    "0-20": 5,
    "20-40": 8,
    "40-60": 12,
    "60-80": 20,
    "80-100": 455
  },
  "statistics": {
    "mean_fitness": 87.3,
    "std_fitness": 12.4,
    "min_fitness": 5.2,
    "max_fitness": 100.0
  }
}
```

## State Management

### Widget State
- `_gaConfig`: Current GA configuration
- `_grammarConfig`: Current grammar configuration
- `_isEvolving`: Evolution running flag
- `_evolutionProgress`: Progress percentage (0.0-1.0)
- `_metricsHistory`: List of metrics from each generation
- `_bestExpressionTree`: Best evolved expression tree
- `_fitnessAnalysis`: Population fitness analysis
- `_errorMessage`: Error state and messages

### Lifecycle Hooks
```dart
@override
void initState() {
  // Load initial data
  _loadFitnessAnalysis();
}

@override
void dispose() {
  // Cleanup
  _tabController.dispose();
}
```

## Error Handling

All API calls include error handling:
```dart
try {
  final result = await _apiService.runGeneticAlgorithmEvolution(...);
  // Process success
} catch (e) {
  setState(() {
    _errorMessage = 'Evolution failed: $e';
    _isEvolving = false;
  });
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('Error: $e'),
      backgroundColor: Colors.red,
    ),
  );
}
```

## Visualization Features

### Progress Chart
- Custom painted line chart
- Shows best fitness (green line)
- Shows average fitness (orange dashed line)
- Automatic scaling based on data range
- Axes and gridlines

### Expression Tree
- Hierarchical layout
- Circle nodes with labels
- Connection lines between parent/child
- Interactive selection
- Zoom/pan support via InteractiveViewer
- Node detail panel on selection

### Metrics Grid
- 4-column grid (Generation, Best, Avg, Population)
- Color-coded metric cards
- Icon indicators for each metric type
- Real-time updates

## Performance Considerations

1. **Large Metrics History**
   - Only last 10 generations displayed in detail table
   - Chart renders all data but with responsive painting

2. **Tree Rendering**
   - Limited to viewport size
   - Uses CustomPaint for efficiency
   - InteractiveViewer for zoom/pan

3. **Data Updates**
   - Batch metrics updates
   - Use setState minimally
   - Consider FutureBuilder for async operations

## Testing

To test the GA integration:

1. **Manual Testing**
   ```dart
   // In main_screen.dart
   void _navigateToGAScreen() {
     Navigator.of(context).push(
       MaterialPageRoute(
         builder: (context) => const GAEvolutionScreen(),
       ),
     );
   }
   ```

2. **Configuration Testing**
   - Test each preset (Fast, Balanced, Quality)
   - Verify parameter bounds
   - Test preset switching

3. **Grammar Testing**
   - Try each grammar preset
   - Add custom rules
   - Verify rule visualization

4. **API Testing**
   - Mock API responses
   - Test error handling
   - Verify data parsing

## Backend Requirements

Ensure the backend provides these endpoints:

- `POST /ga/evolve` - Run evolution with config
- `GET /ga/progress` - Get progress updates
- `POST /ga/analyze-fitness` - Analyze population fitness
- `GET /ga/grammar-presets` - Get available presets
- `POST /ga/parse-tree` - Parse expression tree

## Future Enhancements

1. **Streaming Progress**
   - WebSocket support for real-time updates
   - Server-sent events for metric streaming

2. **Advanced Visualization**
   - 3D fitness landscape visualization
   - Pareto front visualization
   - Heatmaps for parameter sensitivity

3. **Batch Operations**
   - Run multiple evolution experiments
   - Parameter sweep UI
   - Results comparison tool

4. **Export/Import**
   - Save/load configurations
   - Export expression trees
   - Share results

## Troubleshooting

### Issue: "No metrics available yet"
**Solution:** Evolution hasn't started or completed. Click "Start Evolution" first.

### Issue: Expression tree not rendering
**Solution:** Check that API returned valid tree structure in response.

### Issue: Configuration not applying
**Solution:** Click "Apply Configuration" button after making changes.

### Issue: API connection errors
**Solution:** Verify backend is running and accessible at localhost:5000.

## References

- Backend GA System: [python-backend/GA_SYSTEM_README.md](../python-backend/GA_SYSTEM_README.md)
- Fitness Evaluation: [python-backend/data_fitness.py](../python-backend/data_fitness.py)
- Flutter Widgets: Official Flutter documentation
- Custom Painting: [CustomPaint and CustomPainter](https://flutter.dev/docs/development/ui/advanced/custom-paint)

---

**Last Updated:** December 19, 2025
**Version:** 1.0.0
**Status:** Production Ready
