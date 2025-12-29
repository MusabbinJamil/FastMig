# PSO UI Implementation Guide

## Overview

This document describes the PSO (Particle Swarm Optimization) UI controls and visualization components in the Flutter frontend.

## Files

- `lib/models/evolutionary_config_models.dart` - `PSOConfigModel` class
- `lib/widgets/evolutionary_cleaning_section.dart` - PSO parameter UI
- `lib/widgets/pso_visualization.dart` - PSO charts and metrics display

## Configuration Model

### PSOConfigModel

```dart
class PSOConfigModel extends EvolutionaryConfigBase {
  final int swarmSize;
  final int iterations;
  final double inertiaWeight;
  final double inertiaMin;
  final double inertiaMax;
  final double cognitiveParameter;  // c1
  final double socialParameter;     // c2
  final double velocityClamp;
  final String topologyType;
  final String variant;
  final double constrictionFactor;
  final int neighborhoodSize;
  final bool earlyStoppingEnabled;
  final int earlyStoppingPatience;
}
```

### Static Constants

```dart
// Available topologies
static const List<String> topologyTypes = [
  'gbest',      // Global best
  'lbest',      // Local best
  'ring',       // Ring topology
  'random',     // Random neighbors
  'von_neumann' // Grid topology
];

// Topology display names
static const Map<String, String> topologyDisplayNames = {
  'gbest': 'Global Best (Star)',
  'lbest': 'Local Best (Ring)',
  'ring': 'Ring Topology',
  'random': 'Random Neighbors',
  'von_neumann': 'Von Neumann (Grid)',
};

// Available variants
static const List<String> variants = [
  'standard',      // Classic PSO
  'constriction',  // Clerc's constriction
  'inertia_decay', // Linear decay
];

// Variant display names
static const Map<String, String> variantDisplayNames = {
  'standard': 'Standard PSO',
  'constriction': 'Constriction Factor PSO',
  'inertia_decay': 'Inertia Decay PSO',
};
```

### Presets

```dart
static PSOConfigModel getPreset(String presetName) {
  switch (presetName) {
    case 'fast':
      return PSOConfigModel(
        swarmSize: 20,
        iterations: 30,
        inertiaWeight: 0.8,
        earlyStoppingPatience: 5,
      );
    case 'balanced':
      return PSOConfigModel(
        swarmSize: 30,
        iterations: 100,
        inertiaWeight: 0.7,
        earlyStoppingPatience: 10,
      );
    case 'quality':
      return PSOConfigModel(
        swarmSize: 50,
        iterations: 200,
        inertiaWeight: 0.6,
        topologyType: 'lbest',
        variant: 'constriction',
        earlyStoppingPatience: 15,
      );
    default:
      return PSOConfigModel();
  }
}
```

## UI Components

### Parameter Section

Located in `evolutionary_cleaning_section.dart`, the PSO parameter section includes:

#### Basic Parameters
- **Swarm Size** - Slider (10-100)
- **Iterations** - Slider (10-500)

#### Velocity Parameters
- **Inertia Weight (w)** - Slider (0.0-1.0)
- **Velocity Clamp** - Slider (0.0-1.0)

#### Attraction Coefficients
- **Cognitive (c1)** - Slider (0.0-4.0) with tooltip
- **Social (c2)** - Slider (0.0-4.0) with tooltip

#### Dropdowns
- **Topology** - Dropdown with 5 options
- **Variant** - Dropdown with 3 options

#### Conditional Parameters
- **Constriction Factor** - Shows when variant is 'constriction'
- **Inertia Min/Max** - Shows when variant is 'inertia_decay'
- **Neighborhood Size** - Shows when topology is 'lbest', 'ring', or 'random'

### Preset Buttons

Three preset buttons for quick configuration:
- **Fast** - Quick evolution, smaller swarm
- **Balanced** - Default settings
- **Quality** - Thorough evolution, larger swarm

## Visualization

### PSOVisualization Widget

Located in `lib/widgets/pso_visualization.dart`.

#### Constructor

```dart
const PSOVisualization({
  required List<PSOMetrics> metricsHistory,
  bool isRunning = false,
  double? progressPercent,
  VoidCallback? onStop,
  String? topologyType,
  String? variant,
});
```

#### PSOMetrics Model

```dart
class PSOMetrics {
  final int iteration;
  final double globalBestFitness;
  final double averageFitness;
  final double worstFitness;
  final double averageVelocity;
  final double swarmDiversity;
  final int swarmSize;
}
```

#### Chart Types

The visualization supports three chart views (togglable):

1. **Fitness Chart** (default)
   - Global best fitness (gold/amber line)
   - Average fitness (green line)
   - Legend in top-right corner

2. **Velocity Chart**
   - Average velocity magnitude (blue line)
   - Useful for monitoring convergence

3. **Diversity Chart**
   - Swarm diversity over time (purple line)
   - Helps detect premature convergence

#### Metrics Grid

Displays four key metrics:
- **Iteration** - Current iteration number
- **Global Best** - Best fitness found
- **Avg Fitness** - Population average
- **Improvement** - Improvement from start

#### Data Table

Shows recent iterations with columns:
- Iter | GBest | Avg | Velocity | Diversity

## State Management

In `_EvolutionaryCleaningSectionState`:

```dart
// PSO Configuration State
PSOConfigModel _psoConfig = PSOConfigModel();

// Update config
setState(() {
  _psoConfig = _psoConfig.copyWith(swarmSize: newSize);
});

// Get config for API
Map<String, dynamic> _getMethodConfig() {
  switch (_selectedMethod) {
    case 'pso':
      return _psoConfig.toJson();
    // ...
  }
}
```

## JSON Serialization

### toJson()

```dart
Map<String, dynamic> toJson() {
  return {
    'population_size': swarmSize,
    'generations': iterations,
    'inertia_weight': inertiaWeight,
    'inertia_min': inertiaMin,
    'inertia_max': inertiaMax,
    'cognitive_coeff': cognitiveParameter,
    'social_coeff': socialParameter,
    'velocity_clamp': velocityClamp,
    'pso_topology': topologyType,
    'pso_variant': variant,
    'constriction_factor': constrictionFactor,
    'neighborhood_size': neighborhoodSize,
    'early_stopping': earlyStoppingEnabled,
    'patience': earlyStoppingPatience,
    'fitness_threshold': fitnessThreshold / 100.0,
    'track_progress': trackProgress,
  };
}
```

### fromJson()

```dart
factory PSOConfigModel.fromJson(Map<String, dynamic> json) {
  return PSOConfigModel(
    swarmSize: json['population_size'] ?? json['swarm_size'] ?? 30,
    iterations: json['generations'] ?? json['iterations'] ?? 100,
    inertiaWeight: (json['inertia_weight'] ?? 0.7).toDouble(),
    // ... handles both old and new parameter names
  );
}
```

## Styling

### Color Scheme
- Primary color: `Colors.blue`
- Topology icon: `Icons.hub`
- Variant icon: `Icons.settings`

### Chart Colors
- Global Best: `Colors.amber`
- Average: `Colors.green`
- Velocity: `Colors.blue`
- Diversity: `Colors.purple`

## Usage Example

```dart
// In evolutionary_cleaning_section.dart
if (_selectedMethod == 'pso')
  _buildAdvancedSettingsSection(),

// Building PSO settings
Widget _buildPSOSettings() {
  return Column(
    children: [
      _buildPresetRow('PSO Presets', ['fast', 'balanced', 'quality'], (preset) {
        setState(() {
          _psoConfig = PSOConfigModel.getPreset(preset);
        });
      }),
      // ... sliders and dropdowns
    ],
  );
}
```

## Integration with API

The configuration is passed to the API via `evolveErrorCells`:

```dart
final result = await migrationData.evolveErrorCells(
  method: 'pso',
  saveResult: true,
  config: _psoConfig.toJson(),
);
```
