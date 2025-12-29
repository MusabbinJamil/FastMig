# DE UI Implementation Guide

## Overview

This document describes the DE (Differential Evolution) UI controls and visualization components in the Flutter frontend.

## Files

- `lib/models/evolutionary_config_models.dart` - `DEConfigModel` class
- `lib/widgets/evolutionary_cleaning_section.dart` - DE parameter UI
- `lib/widgets/de_visualization.dart` - DE charts and metrics display

## Configuration Model

### DEConfigModel

```dart
class DEConfigModel extends EvolutionaryConfigBase {
  final int populationSize;
  final int generations;
  final double scaleFactor;       // F parameter
  final double crossoverRate;     // CR parameter
  final String mutationStrategy;  // All 6 strategies
  final String crossoverType;     // binomial or exponential
  final bool adaptiveF;
  final bool adaptiveCR;
  final double fMin;
  final double fMax;
  final double crMin;
  final double crMax;
  final double adaptationRate;
  final bool earlyStoppingEnabled;
  final int earlyStoppingPatience;
}
```

### Static Constants

```dart
// All 6 mutation strategies
static const List<String> mutationStrategies = [
  'DE/rand/1',           // Exploration
  'DE/rand/2',           // Strong exploration
  'DE/best/1',           // Exploitation
  'DE/best/2',           // Strong exploitation
  'DE/current-to-best/1', // Balanced
  'DE/current-to-rand/1', // Explorative balance
];

// Strategy display names
static const Map<String, String> mutationStrategyDisplayNames = {
  'DE/rand/1': 'DE/rand/1 (Exploration)',
  'DE/rand/2': 'DE/rand/2 (Strong Exploration)',
  'DE/best/1': 'DE/best/1 (Exploitation)',
  'DE/best/2': 'DE/best/2 (Strong Exploitation)',
  'DE/current-to-best/1': 'DE/current-to-best/1 (Balanced)',
  'DE/current-to-rand/1': 'DE/current-to-rand/1 (Explorative Balance)',
};

// Crossover types
static const List<String> crossoverTypes = [
  'binomial',
  'exponential',
];

// Crossover display names
static const Map<String, String> crossoverTypeDisplayNames = {
  'binomial': 'Binomial (Standard)',
  'exponential': 'Exponential',
};
```

### Presets

```dart
static DEConfigModel getPreset(String presetName) {
  switch (presetName) {
    case 'fast':
      return DEConfigModel(
        populationSize: 20,
        generations: 30,
        scaleFactor: 0.8,
        crossoverRate: 0.9,
        mutationStrategy: 'DE/best/1',
        adaptiveF: false,
        adaptiveCR: false,
        earlyStoppingPatience: 5,
      );
    case 'balanced':
      return DEConfigModel(
        populationSize: 30,
        generations: 100,
        scaleFactor: 0.8,
        crossoverRate: 0.9,
        mutationStrategy: 'DE/rand/1',
        earlyStoppingPatience: 10,
      );
    case 'quality':
      return DEConfigModel(
        populationSize: 50,
        generations: 200,
        scaleFactor: 0.7,
        crossoverRate: 0.85,
        mutationStrategy: 'DE/current-to-best/1',
        adaptiveF: true,
        adaptiveCR: true,
        earlyStoppingPatience: 15,
      );
    default:
      return DEConfigModel();
  }
}
```

## UI Components

### Parameter Section

Located in `evolutionary_cleaning_section.dart`, the DE parameter section includes:

#### Basic Parameters
- **Population Size** - Slider (10-100)
- **Generations** - Slider (10-500)

#### Core DE Parameters
- **Scale Factor (F)** - Slider (0.0-2.0) with tooltip
- **Crossover Rate (CR)** - Slider (0.0-1.0) with tooltip

#### Dropdowns
- **Mutation Strategy** - Dropdown with 6 options
- **Crossover Type** - Dropdown with 2 options

#### Adaptive Parameters Section
Container with orange styling:
- **Adaptive F** - Checkbox toggle
- **Adaptive CR** - Checkbox toggle

#### Conditional Parameters
- **F Min/Max** - Shows when Adaptive F is enabled
- **CR Min/Max** - Shows when Adaptive CR is enabled

### Preset Buttons

Three preset buttons for quick configuration:
- **Fast** - Quick evolution with DE/best/1
- **Balanced** - Default settings with DE/rand/1
- **Quality** - Thorough evolution with adaptive parameters

## Visualization

### DEVisualization Widget

Located in `lib/widgets/de_visualization.dart`.

#### Constructor

```dart
const DEVisualization({
  required List<DEMetrics> metricsHistory,
  bool isRunning = false,
  double? progressPercent,
  VoidCallback? onStop,
  String? mutationStrategy,
  bool adaptiveF = false,
  bool adaptiveCR = false,
});
```

#### DEMetrics Model

```dart
class DEMetrics {
  final int generation;
  final double bestFitness;
  final double averageFitness;
  final double worstFitness;
  final double populationDiversity;
  final double successRate;
  final double currentF;
  final double currentCR;
  final int populationSize;
}
```

#### Chart Types

The visualization supports four chart views (togglable):

1. **Fitness Chart** (default)
   - Best fitness (orange line)
   - Average fitness (green line)
   - Worst fitness (red dashed line)
   - Legend in top-right corner

2. **Success Rate Chart**
   - Mutation success rate over time (blue line)
   - 50% reference line
   - Useful for monitoring adaptive behavior

3. **Parameters Chart** (only when adaptive is enabled)
   - F value over time (orange line)
   - CR value over time (purple line)
   - Shows adaptive parameter evolution

4. **Diversity Chart**
   - Population diversity over time (purple line)
   - Helps detect convergence

#### Metrics Grid

Displays four key metrics:
- **Generation** - Current generation number
- **Best Fitness** - Best fitness found
- **Success Rate** - Mutation success percentage
- **Improvement** - Improvement from start

#### Data Table

Shows recent generations with columns:
- Gen | Best | Avg | Success | F | CR

## State Management

In `_EvolutionaryCleaningSectionState`:

```dart
// DE Configuration State
DEConfigModel _deConfig = DEConfigModel();

// Update config
setState(() {
  _deConfig = _deConfig.copyWith(scaleFactor: newF);
});

// Get config for API
Map<String, dynamic> _getMethodConfig() {
  switch (_selectedMethod) {
    case 'de':
      return _deConfig.toJson();
    // ...
  }
}
```

## JSON Serialization

### toJson()

```dart
Map<String, dynamic> toJson() {
  return {
    'population_size': populationSize,
    'generations': generations,
    'scale_factor': scaleFactor,
    'crossover_rate': crossoverRate,
    'de_mutation_strategy': mutationStrategy,
    'de_crossover_type': crossoverType,
    'adaptive_f': adaptiveF,
    'adaptive_cr': adaptiveCR,
    'f_min': fMin,
    'f_max': fMax,
    'cr_min': crMin,
    'cr_max': crMax,
    'adaptation_rate': adaptationRate,
    'early_stopping': earlyStoppingEnabled,
    'patience': earlyStoppingPatience,
    'fitness_threshold': fitnessThreshold / 100.0,
    'track_progress': trackProgress,
  };
}
```

### fromJson()

```dart
factory DEConfigModel.fromJson(Map<String, dynamic> json) {
  return DEConfigModel(
    populationSize: json['population_size'] ?? 30,
    generations: json['generations'] ?? 100,
    scaleFactor: (json['scale_factor'] ?? 0.8).toDouble(),
    crossoverRate: (json['crossover_rate'] ?? 0.9).toDouble(),
    mutationStrategy: json['de_mutation_strategy'] ??
                      json['mutation_strategy'] ?? 'DE/rand/1',
    crossoverType: json['de_crossover_type'] ??
                   json['crossover_type'] ?? 'binomial',
    // ... handles both old and new parameter names
  );
}
```

## Styling

### Color Scheme
- Primary color: `Colors.orange`
- Strategy icon: `Icons.shuffle`
- Crossover icon: `Icons.merge_type`
- Adaptive section: Orange shade background

### Chart Colors
- Best Fitness: `Colors.orange`
- Average: `Colors.green`
- Worst: `Colors.red.withOpacity(0.5)`
- Success Rate: `Colors.blue`
- F Parameter: `Colors.orange`
- CR Parameter: `Colors.purple`
- Diversity: `Colors.purple`

### Adaptive Section Styling

```dart
Container(
  padding: const EdgeInsets.all(12),
  decoration: BoxDecoration(
    color: Colors.orange.shade50,
    borderRadius: BorderRadius.circular(8),
    border: Border.all(color: Colors.orange.shade200),
  ),
  child: Column(...),
)
```

## Usage Example

```dart
// In evolutionary_cleaning_section.dart
if (_selectedMethod == 'de')
  _buildAdvancedSettingsSection(),

// Building DE settings
Widget _buildDESettings() {
  return Column(
    children: [
      _buildPresetRow('DE Presets', ['fast', 'balanced', 'quality'], (preset) {
        setState(() {
          _deConfig = DEConfigModel.getPreset(preset);
        });
      }),
      // ... sliders and dropdowns

      // Adaptive parameters section
      Container(
        decoration: BoxDecoration(
          color: Colors.orange.shade50,
          // ...
        ),
        child: Column(
          children: [
            CheckboxListTile(
              title: Text('Adaptive F'),
              value: _deConfig.adaptiveF,
              onChanged: (value) => setState(() {
                _deConfig = _deConfig.copyWith(adaptiveF: value);
              }),
            ),
            // ...
          ],
        ),
      ),

      // Conditional F range sliders
      if (_deConfig.adaptiveF) ...[
        // F Min/Max sliders
      ],
    ],
  );
}
```

## Integration with API

The configuration is passed to the API via `evolveErrorCells`:

```dart
final result = await migrationData.evolveErrorCells(
  method: 'de',
  saveResult: true,
  config: _deConfig.toJson(),
);
```

## Strategy Selection Guide

| Strategy | When to Use |
|----------|-------------|
| DE/rand/1 | Default choice, unknown problem |
| DE/rand/2 | Highly multimodal problems |
| DE/best/1 | Fast convergence needed |
| DE/best/2 | Fine-tuning, exploitation |
| DE/current-to-best/1 | Balanced exploration/exploitation |
| DE/current-to-rand/1 | More exploration than c-t-b |

## Adaptive Parameters Guide

- Enable **Adaptive F** when:
  - Problem difficulty is unknown
  - You want automatic exploration/exploitation balance

- Enable **Adaptive CR** when:
  - Optimal crossover rate is unknown
  - Problem has mixed separable/non-separable characteristics

- **Typical Ranges**:
  - F: 0.1 - 1.0 (can go up to 2.0)
  - CR: 0.1 - 1.0
  - Higher values = more aggressive mutation/crossover
