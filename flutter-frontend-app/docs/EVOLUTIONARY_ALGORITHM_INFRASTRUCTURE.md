# Evolutionary Algorithm Modular Infrastructure

## Overview

This comprehensive infrastructure provides power users with deep control over evolutionary computation methods for data cleaning and optimization. The system is fully modular, allowing seamless integration of new algorithms while maintaining a unified interface.

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│  User Interface Layer (Flutter)                         │
│  - EvolutionaryAlgorithmScreen                         │
│  - Method selector & configuration panels              │
│  - Real-time progress visualization                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  API Service Layer                                      │
│  - Unified endpoints for all methods                   │
│  - API routing & data serialization                    │
│  - Error handling & logging                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Backend Algorithm Layer (Python/Flask)                │
│  - GA, PSO, DE, ES, Hybrid implementations            │
│  - Data fitness evaluation                             │
│  - Results aggregation                                 │
└─────────────────────────────────────────────────────────┘
```

## Frontend Components

### 1. Configuration Models (`evolutionary_config_models.dart`)

Base class for all evolutionary algorithms:

```dart
abstract class EvolutionaryConfigBase {
  final double fitnessThreshold;
  final int? healthySampleSize;
  final bool trackProgress;
  final int maxIterations;
}
```

#### Algorithm-Specific Models

**GA (Genetic Algorithm)**
- Parameters: population_size, generations, mutation_rate, crossover_rate
- Operators: Selection (tournament, roulette, rank-based)
- Methods: Single/two-point, uniform, arithmetic crossover
- Mutations: Gaussian, uniform, adaptive

**PSO (Particle Swarm Optimization)**
- Parameters: swarm_size, iterations, inertia_weight
- Cognitive/Social: c1 (particle's best), c2 (swarm's best)
- Topology: Global, local, ring, random
- Velocity: Bounded v_min and v_max

**DE (Differential Evolution)**
- Parameters: scale_factor (F), crossover_rate (CR)
- Strategies: DE/best/1, DE/rand/1, DE/best/2, DE/rand/2
- Adaptive: Self-adaptive F and CR
- Bounds: Configurable search space limits

**ES (Evolution Strategy)**
- Selection: (μ+λ) or (μ,λ)
- Self-adaptive mutation with learning rate
- Recombination: Discrete, intermediate, global
- Parent count: Configurable

**Hybrid**
- Auto-selects algorithm per column type
- Ensemble mode for multiple algorithms
- Enabled algorithms configuration

### 2. Configuration Panels (`evolutionary_config_panels.dart`)

Modular UI components for each algorithm:

```dart
class GAConfigurationPanel extends StatefulWidget {
  final GAConfigModel config;
  final Function(GAConfigModel) onConfigChanged;
}

class PSOConfigurationPanel extends StatefulWidget {
  // Similar structure for PSO
}

class DEConfigurationPanel extends StatefulWidget {
  // Similar structure for DE
}

class ESConfigurationPanel extends StatefulWidget {
  // Similar structure for ES
}

class HybridConfigurationPanel extends StatefulWidget {
  // Hybrid configuration options
}
```

**Features:**
- Real-time parameter sliders with instant feedback
- Preset configurations (fast, balanced, quality)
- Section-based organization
- Tooltips for complex parameters
- Dependency-based UI (e.g., show elitism count only if enabled)

### 3. Main Screen (`evolutionary_algorithm_screen.dart`)

The comprehensive evolution screen with three main tabs:

**Configuration Tab:**
- Method selector with visual cards
- Algorithm-specific parameter panel
- Configuration summary
- Start/Reset buttons

**Progress Tab:**
- Real-time fitness progress chart
- Generation-by-generation metrics
- Stop button for long-running processes
- Statistics display

**Analysis Tab:**
- Population fitness analysis
- Detailed statistics
- Distribution visualization
- Comparison results

## Backend API Endpoints

### Unified Endpoints

```
POST /evo/run
├── method: ga|pso|de|es|hybrid
├── config: {algorithm-specific parameters}
└── Returns: fitness_history, best_fitness, improvement, etc.

POST /evo/compare
├── methods: [ga, pso, de, es]
├── config: {base configuration}
└── Returns: comparison_results, best_method, improvements
```

### Legacy Endpoints (Still Available)

```
POST /ga/analyze-population
POST /ga/select-populations
POST /ga/run-evolution
POST /ga/quick-evolve
POST /ga/export-evolved
POST /clean/evolutionary
POST /clean/compare
```

## Configuration Reference

### GA Configuration

```json
{
  "population_size": 30,
  "generations": 100,
  "mutation_rate": 0.1,
  "crossover_rate": 0.8,
  "elitism": true,
  "elite_count": 2,
  "selection_method": "tournament",
  "crossover_method": "single_point",
  "mutation_method": "gaussian",
  "early_stopping_enabled": true,
  "early_stopping_patience": 10,
  "fitness_threshold": 85.0,
  "track_progress": true
}
```

**Selection Methods:**
- `tournament`: Tournament selection (size = pop_size/4)
- `roulette`: Fitness-proportional selection
- `rank-based`: Rank-based selection

**Crossover Methods:**
- `single_point`: Crossover at single position
- `two_point`: Crossover at two positions
- `uniform`: Each gene selected from random parent
- `arithmetic`: Weighted average of parents

**Mutation Methods:**
- `gaussian`: Gaussian noise (mean=0, σ=mutation_rate)
- `uniform`: Uniform random in [-mutation_rate, mutation_rate]
- `adaptive`: Adapts mutation rate based on convergence

### PSO Configuration

```json
{
  "swarm_size": 30,
  "iterations": 100,
  "inertia_weight": 0.7,
  "cognitive_parameter": 1.5,
  "social_parameter": 1.5,
  "velocity_max": 1.0,
  "velocity_min": -1.0,
  "use_constriction_factor": false,
  "constriction_coefficient": 0.729,
  "topology_type": "global",
  "neighborhood_size": 5,
  "fitness_threshold": 85.0
}
```

**Topology Types:**
- `global`: All particles attract to global best
- `local`: Particles attract to neighborhood best
- `ring`: Ring topology with neighborhood radius
- `random`: Random neighborhood selection

### DE Configuration

```json
{
  "population_size": 30,
  "generations": 100,
  "scale_factor": 0.8,
  "crossover_rate": 0.9,
  "mutation_strategy": "DE/best/1",
  "selection_strategy": "best",
  "adaptive_f": false,
  "adaptive_cr": false,
  "lower_bound": 0.0,
  "upper_bound": 1.0,
  "fitness_threshold": 85.0
}
```

**Mutation Strategies:**
- `DE/best/1`: Best + 1 random difference
- `DE/best/2`: Best + 2 random differences
- `DE/rand/1`: Random + 1 difference
- `DE/rand/2`: Random + 2 differences

### ES Configuration

```json
{
  "population_size": 20,
  "offspring_size": 60,
  "generations": 100,
  "selection_type": "plus",
  "initial_mutation_rate": 0.1,
  "self_adaptive_mutation": true,
  "learning_rate": 0.1,
  "recombination_type": "intermediate",
  "parent_count": 2,
  "fitness_threshold": 85.0
}
```

**Selection Types:**
- `plus`: (μ+λ) - Best from parents + offspring
- `comma`: (μ,λ) - Only offspring (requires λ ≥ μ)

**Recombination Types:**
- `discrete`: Each gene from random parent
- `intermediate`: Average of selected parents
- `global`: Average of all parents

### Hybrid Configuration

```json
{
  "auto_select_algorithm": true,
  "column_algorithm_mapping": {
    "numeric_col": "pso",
    "categorical_col": "ga",
    "mixed_col": "hybrid"
  },
  "ensemble_mode": false,
  "enabled_algorithms": ["ga", "pso", "de", "es"],
  "fitness_threshold": 85.0,
  "max_iterations": 100
}
```

## Usage Examples

### Example 1: Run GA with Custom Parameters

```dart
final config = GAConfigModel(
  populationSize: 50,
  generations: 150,
  mutationRate: 0.05,
  crossoverRate: 0.85,
  selectionMethod: 'tournament',
  earlyStoppingPatience: 15,
);

final result = await apiService.runEvolutionaryMethod(
  method: 'ga',
  config: config.toJson(),
);
```

### Example 2: Compare All Methods

```dart
final result = await apiService.compareEvolutionaryMethods(
  methods: ['ga', 'pso', 'de', 'es', 'hybrid'],
  config: {
    'fitness_threshold': 90.0,
    'max_iterations': 50,
    'population_size': 25,
  },
);

print('Best method: ${result['best_method']}');
print('Improvements: ${result['comparison_results']}');
```

### Example 3: Run PSO for Numeric Data

```dart
final psoConfig = PSOConfigModel(
  swarmSize: 25,
  iterations: 80,
  inertiaWeight: 0.8,
  cognitiveParameter: 1.4,
  socialParameter: 1.6,
  topologyType: 'local',
  neighborhoodSize: 4,
);

final result = await apiService.runEvolutionaryMethod(
  method: 'pso',
  config: psoConfig.toJson(),
);
```

## Parameter Tuning Guide

### For Speed (Small Datasets)

```json
{
  "method": "ga",
  "population_size": 15,
  "generations": 20,
  "mutation_rate": 0.15,
  "early_stopping_enabled": true,
  "early_stopping_patience": 3
}
```

### For Quality (Large Datasets)

```json
{
  "method": "hybrid",
  "population_size": 50,
  "generations": 200,
  "mutation_rate": 0.08,
  "early_stopping_patience": 20,
  "track_progress": true
}
```

### For Mixed Data Types

```json
{
  "method": "hybrid",
  "auto_select_algorithm": true,
  "ensemble_mode": true,
  "enabled_algorithms": ["ga", "pso", "de"]
}
```

## Extending the System

### Adding a New Algorithm

1. **Create Config Model** (`evolutionary_config_models.dart`):
```dart
class NewAlgoConfigModel extends EvolutionaryConfigBase {
  final int paramA;
  final double paramB;
  
  @override
  Map<String, dynamic> toJson() { /* ... */ }
}
```

2. **Create Configuration Panel** (`evolutionary_config_panels.dart`):
```dart
class NewAlgoConfigurationPanel extends StatefulWidget { /* ... */ }
```

3. **Add Backend Implementation** (`evolutionary_endpoints.py`):
```python
def _run_newalgo_evolution(df: pd.DataFrame, config: dict) -> dict:
    # Implementation
    return result
```

4. **Route in Unified Endpoint** (`evolutionary_endpoints.py`):
```python
elif method == 'newalgo':
    result = _run_newalgo_evolution(df, config)
```

5. **Add API Service Method** (`api_service.dart`):
```dart
Future<Map<String, dynamic>> runNewAlgoEvolution({
  required Map<String, dynamic> config,
}) async { /* ... */ }
```

## Monitoring & Debugging

### Progress Tracking

Each algorithm outputs:
- Generation/Iteration number
- Best fitness in current generation
- Average fitness
- Worst fitness
- Population diversity metrics

### Result Visualization

The progress tab displays:
- Bar chart of fitness improvement
- Real-time statistics
- Convergence tracking
- Early stopping indicator

## Performance Characteristics

| Algorithm | Speed | Quality | Use Case |
|-----------|-------|---------|----------|
| GA | Medium | High | Mixed data types |
| PSO | Fast | Medium | Numeric data |
| DE | Medium | Very High | Continuous optimization |
| ES | Slow | High | Complex landscapes |
| Hybrid | Fast | Very High | Auto-detection |

## Known Limitations & Future Work

1. **Current:** PSO/DE/ES implemented as GA wrappers for compatibility
   - **Future:** Full native implementations

2. **Current:** Single-population evolution
   - **Future:** Multi-population, migration models

3. **Current:** No constraint handling
   - **Future:** Penalty methods, constraint operators

4. **Current:** No parallel fitness evaluation
   - **Future:** GPU-accelerated evaluation

## API Response Format

All endpoints return:
```json
{
  "success": true,
  "method": "GA",
  "fitness_history": [
    {
      "generation": 0,
      "best_fitness": 45.2,
      "average_fitness": 42.1,
      "worst_fitness": 30.5
    }
  ],
  "best_fitness": 92.3,
  "improvement": 18.5,
  "records_fixed": 245,
  "convergence_achieved": true,
  "message": "GA evolution completed successfully"
}
```

## Best Practices

1. **Use presets** for standard scenarios (fast, balanced, quality)
2. **Enable early stopping** for large datasets
3. **Track progress** for monitoring long-running evolutions
4. **Run comparisons** before committing to an algorithm
5. **Save configurations** for reproducible results
6. **Monitor fitness plateau** to detect convergence
7. **Use hybrid mode** for mixed data types
