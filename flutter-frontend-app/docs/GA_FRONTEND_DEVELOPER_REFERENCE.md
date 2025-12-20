# FastMig GA Frontend - Developer Reference

## Quick Start for Developers

### New Files Added
```
lib/models/ga_config_model.dart                    (320 lines)
lib/widgets/ga_configuration_panel.dart            (320 lines)
lib/widgets/ga_progress_visualization.dart         (400 lines)
lib/widgets/grammar_rule_selection_panel.dart      (350 lines)
lib/widgets/expression_tree_visualization.dart     (450 lines)
lib/screens/ga_evolution_screen.dart               (500 lines)
docs/GA_FRONTEND_INTEGRATION_GUIDE.md              (comprehensive)
```

### Files Modified
```
lib/screens/main_screen.dart                       (added GA button + import + navigation)
lib/services/api_service.dart                      (added 5 new GA methods)
```

## Architecture Overview

### State Management Pattern
```
GAEvolutionScreen (Stateful)
├── _gaConfig: GAConfigModel
├── _grammarConfig: GrammarConfigModel
├── _isEvolving: bool
├── _evolutionProgress: double
├── _metricsHistory: List<GAMetricsModel>
├── _bestExpressionTree: ExpressionTreeNode?
├── _fitnessAnalysis: Map?
└── _errorMessage: String?
```

### Data Flow
```
User Input
    ↓
[Configuration Panel] → Update _gaConfig
    ↓
[Start Evolution Button]
    ↓
[API Service] → runGeneticAlgorithmEvolution()
    ↓
[Response Parsing]
    ↓
[Update State]
    ↓
[Render Visualizations]
    ↓
[User Views Results]
```

## Model Relationships

```
GAConfigModel
├── population_size: int
├── generations: int
├── mutation_rate: double
├── crossover_rate: double
├── elitism: bool
├── selectionMethod: String
├── crossoverMethod: String
├── mutationMethod: String
├── earlyStoppingEnabled: bool
└── fitnessThreshold: double

GAMetricsModel
├── generation: int
├── bestFitness: double
├── averageFitness: double
├── fitnessVariance: double
├── populationSize: int
└── timestamp: DateTime

ExpressionTreeNode
├── value: String
├── type: String ('operator', 'function', 'operand')
├── children: List<ExpressionTreeNode>
└── fitnessContribution: double?

GrammarConfigModel
├── grammarType: String
├── rules: List<String>
├── maxTreeDepth: int
├── customGrammarPath: String?
└── enableTypeChecking: bool
```

## Widget Hierarchy

```
GAEvolutionScreen (TabBarView)
├── Tab 0: Configuration
│   └── DefaultTabController
│       ├── Tab 0.0: GAConfigurationPanel
│       └── Tab 0.1: GrammarRuleSelectionPanel
│
├── Tab 1: Progress
│   └── GAProgressVisualization
│       ├── Progress bar
│       ├── Metrics grid
│       ├── Fitness chart (CustomPaint)
│       └── Metrics table
│
├── Tab 2: Expression Tree
│   └── ExpressionTreeVisualization
│       ├── Header with fitness
│       ├── InteractiveViewer
│       │   └── CustomPaint (TreePainter)
│       └── Node detail panel
│
└── Tab 3: Analysis
    └── Fitness analysis display
        ├── Error display
        ├── Analysis cards
        ├── Statistics table
        └── Load analysis button
```

## API Contract

### Request Structure
```dart
// GA Evolution
{
  'ga_config': GAConfigModel.toJson(),
  'grammar_config': GrammarConfigModel.toJson(),
  'track_progress': true
}
```

### Response Structure
```dart
// GA Evolution Response
{
  'success': bool,
  'evolved_data': List<List<dynamic>>,
  'metrics': Map<String, dynamic>,
  'expression_tree': Map<String, dynamic>,
  'fitness_history': List<Map<String, dynamic>>,
  'convergence_info': Map<String, dynamic>,
  'message': String
}
```

## Key Implementation Details

### 1. Configuration Panel
**Type:** StatefulWidget with TextEditingControllers
**Key Methods:**
- `_updateConfig()`: Syncs controllers with model
- `_applyPreset()`: Loads preset configuration
- `_buildIntegerField()`: Builds number input fields
- `_buildDoubleField()`: Builds decimal input fields
- `_buildDropdown()`: Builds selection dropdowns

**Validation:**
- Population Size: 20-200
- Generations: 10-1000
- Mutation Rate: 0.0-1.0
- Crossover Rate: 0.0-1.0

### 2. Progress Visualization
**Type:** StatefulWidget with AnimationController
**Rendering:**
- LinearProgressIndicator for overall progress
- CustomPaint with FitnessChartPainter for graph
- GridView for metrics cards
- DataTable for detailed metrics

**Performance:**
- Paints only on data change (shouldRepaint)
- Metrics limited to 10 recent generations in table
- Full data plotted in chart

### 3. Grammar Panel
**Type:** StatefulWidget with TextEditingControllers
**Features:**
- Chip-based preset selection
- ListView for rule management
- Text field for custom rules
- Rule enumeration with numbering

**Presets:**
```dart
'standard': [<expr> ::= ..., <term> ::= ..., ...]
'boolean': [<expr> ::= ..., <term> ::= ..., ...]
'trigonometric': [<expr> ::= ..., <base> ::= ..., ...]
'data_cleaning': [<operation> ::= ..., ...]
'statistical': [<expr> ::= ..., <stat> ::= ..., ...]
```

### 4. Expression Tree Visualization
**Type:** StatefulWidget with TransformationController
**Rendering:**
- InteractiveViewer for zoom/pan (0.5x - 3.0x)
- CustomPaint with TreePainter for rendering
- Recursive tree layout with spacing

**Interaction:**
- Tap nodes to select
- Shows node details in panel
- Displays children enumeration
- Shows fitness contribution

**Custom Painter:**
- Draws circles for nodes (20px radius)
- Colors: blue[100] normal, amber[200] selected
- Draws connection lines
- Adds text labels (truncated to 3 chars)
- Automatic hierarchy layout

### 5. GA Evolution Screen
**Type:** StatefulWidget with SingleTickerProviderStateMixin
**Tabs:** 4 tabs with TabController
**Key Methods:**
- `_startEvolution()`: Calls API and updates UI
- `_stopEvolution()`: Stops ongoing evolution
- `_loadFitnessAnalysis()`: Gets population analysis
- `_buildConfigurationTab()`: Config interface
- `_buildProgressTab()`: Progress visualization
- `_buildExpressionTreeTab()`: Tree explorer
- `_buildAnalysisTab()`: Population analysis

**Error Handling:**
```dart
try {
  // API call
} catch (e) {
  setState(() { _errorMessage = 'Error: $e'; });
  ScaffoldMessenger.showSnackBar(
    SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red)
  );
}
```

## Common Patterns

### Model Serialization
```dart
// To JSON
final json = config.toJson();

// From JSON
final config = GAConfigModel.fromJson(jsonData);

// Copy with updates
final updated = config.copyWith(generations: 200);
```

### API Integration
```dart
try {
  final result = await _apiService.runGeneticAlgorithmEvolution(
    gaConfig: _gaConfig.toJson(),
    grammarConfig: _grammarConfig.toJson(),
  );
  setState(() { /* update UI */ });
} catch (e) {
  // Handle error
}
```

### State Updates
```dart
setState(() {
  _metricsHistory = newMetrics;
  _evolutionProgress = 0.75;
  _isEvolving = false;
});
```

### Custom Painting
```dart
CustomPaint(
  painter: MyPainter(data),
  size: Size.infinite,
)

class MyPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawCircle(Offset(x, y), radius, paint);
  }
  
  @override
  bool shouldRepaint(MyPainter old) => true;
}
```

## Testing Guide

### Unit Tests (Model)
```dart
test('GAConfigModel serialization', () {
  final config = GAConfigModel();
  final json = config.toJson();
  final restored = GAConfigModel.fromJson(json);
  expect(restored.populationSize, equals(config.populationSize));
});
```

### Widget Tests
```dart
testWidgets('Configuration Panel renders', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: GAConfigurationPanel(
          initialConfig: GAConfigModel(),
          onConfigChanged: (_) {},
        ),
      ),
    ),
  );
  expect(find.byType(TextField), findsWidgets);
});
```

### Integration Tests
```dart
testWidgets('Full GA Evolution flow', (tester) async {
  await tester.pumpWidget(const MyApp());
  
  // Navigate to GA screen
  await tester.tap(find.byIcon(Icons.biotech));
  await tester.pumpAndSettle();
  
  // Configure
  // Run evolution
  // Verify results
});
```

## Debugging Tips

### Enable Custom Paint Debug
```dart
// In TreePainter
@override
void paint(Canvas canvas, Size size) {
  // Draw debug grid
  final paint = Paint()..color = Colors.grey[300]!;
  for (int i = 0; i < size.width; i += 50) {
    canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
  }
}
```

### Log State Changes
```dart
@override
void setState(fn) {
  print('State change: ${DateTime.now()}');
  super.setState(fn);
}
```

### Monitor API Calls
```dart
// In api_service.dart
_consoleLogService.info('API call: $method $endpoint');
_consoleLogService.success('API success: $statusCode');
_consoleLogService.error('API error: $error');
```

## Performance Optimization

### Reduce Repaints
```dart
// Instead of
setState(() => _data = newData);

// Use
if (!_identical(_data, newData)) {
  setState(() => _data = newData);
}
```

### Lazy Load Tab Content
```dart
// Only build visible tab content
if (_tabController.index == selectedTab) {
  // Build widget
}
```

### Cache CustomPaint
```dart
// Limit repaint frequency
bool shouldRepaint(oldDelegate) =>
    oldDelegate.metrics.length != metrics.length;
```

## Dependency Management

### Required Packages
```yaml
dependencies:
  flutter:
    sdk: flutter
  provider: ^6.0.0
  http: ^1.0.0
```

### Optional Enhancements
```yaml
dependencies:
  intl: ^0.18.0  # For date formatting
  fl_chart: ^0.61.0  # Advanced charting
  syncfusion_flutter_charts: ^20.0.0  # Better visualizations
```

## Future Enhancement Roadmap

### Phase 2: Advanced Features
- [ ] WebSocket streaming for metrics
- [ ] Batch evolution experiments
- [ ] Parameter sensitivity analysis
- [ ] Results export (CSV, JSON, PDF)

### Phase 3: Visualization Upgrades
- [ ] 3D fitness landscape
- [ ] Pareto front visualization
- [ ] Heatmaps for parameter analysis
- [ ] Animation of tree evolution

### Phase 4: Advanced UX
- [ ] Undo/redo for configurations
- [ ] Configuration history
- [ ] Favorites/bookmarks
- [ ] Collaboration features

## Troubleshooting Common Issues

### "Null safety error: type X is not nullable"
**Solution:** Add ? to optional fields or use ?? operator

### "NoSuchMethodError on widget render"
**Solution:** Check model initialization in initState()

### "Tree doesn't render"
**Solution:** Verify ExpressionTreeNode.fromJson() parsing

### "Performance issues with large metrics"
**Solution:** Limit displayed data or use pagination

### "API response parsing fails"
**Solution:** Check response structure in _parseResponse()

## Resources

- **Flutter Documentation:** https://flutter.dev/docs
- **Dart Language:** https://dart.dev/guides
- **Custom Painting:** https://flutter.dev/docs/development/ui/advanced/custom-paint
- **State Management:** https://flutter.dev/docs/development/data-and-backend/state-mgmt

## Contact & Support

For issues or questions:
1. Check GA_FRONTEND_INTEGRATION_GUIDE.md
2. Review example code in GA_EXAMPLES.py (backend equivalent)
3. Check console logs via ConsoleLogService
4. Verify backend endpoints are running

---

**Last Updated:** December 19, 2025
**Version:** 1.0.0
**Audience:** Backend Developers, Frontend Developers, QA Engineers
