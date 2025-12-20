DATA FITNESS EVOLUTION WITH GA - QUICK START GUIDE
==================================================

Overview
--------
This module allows users to:
1. Identify unhealthy records in their dataset (low fitness scores)
2. Select healthy records as evolutionary templates
3. Use genetic algorithms to evolve unhealthy records toward health
4. Track improvements and modifications

Components
----------
- ga_fitness_evolver.py: Main module with DataFitnessEvolverGA class
- ga_data_cleaning_pipeline.py: Interactive user interface
- run_fitness_evolution.py: Quick-start demo script

Quick Usage
-----------

Basic 3-Step Process:

Step 1: Initialize and Analyze
```python
from ga_fitness_evolver import DataFitnessEvolverGA

evolver = DataFitnessEvolverGA(your_dataframe)
analysis = evolver.analyze_population(fitness_threshold=85.0)
```

Step 2: Select Populations
```python
config = evolver.select_populations(
    fitness_threshold=85.0,
    healthy_sample_size=1000  # Use 1000 healthy records as templates
)
```

Step 3: Evolve Unhealthy Records
```python
from ga_operators import GAConfig

ga_config = GAConfig(
    population_size=30,
    generations=100,
    early_stopping=True
)

evolved_df, results = evolver.evolve_unhealthy_records(config, ga_config)
```

View Results
```python
metrics = results['fitness_metrics']
print(f"Avg improvement: {metrics['improvement']:.2f}")
print(f"Records at target: {metrics['records_at_target']}/{config.unhealthy_count}")
```

Interactive CLI
---------------

For a fully interactive experience with step-by-step guidance:

```bash
python ga_data_cleaning_pipeline.py
```

This provides:
- Menu-driven data loading (CSV or demo)
- Fitness analysis with distribution statistics
- Interactive population selection with options
- GA configuration with presets
- Results visualization and reporting
- CSV export of evolved data and detailed reports

Parameters Explained
--------------------

fitness_threshold (float, default 85.0):
  - Score below which records are considered "unhealthy"
  - 0-100 scale
  - Based on: missing values (40%), type consistency (30%), SQLite compatibility (30%)

healthy_sample_size (int, default=None):
  - How many healthy records to use as evolutionary templates
  - None = use all available healthy records
  - Larger values = more computational time but potentially better templates

population_size (int):
  - GA population size per record evolution
  - Larger = slower but potentially better solutions
  - Recommended: 20-50 for fast results, 50-100 for quality

generations (int):
  - How many GA iterations to run per record
  - Larger = slower but potentially better convergence
  - Recommended: 50-200 depending on time budget

early_stopping (bool):
  - Stop GA if no improvement detected
  - Saves computation time
  - Recommended: True

Example Workflow
----------------

1. Load your dataset:
   ```python
   df = pd.read_csv('your_data.csv')
   ```

2. Identify problematic records:
   ```python
   evolver = DataFitnessEvolverGA(df)
   analysis = evolver.analyze_population(fitness_threshold=75.0)
   print(f"Found {analysis['unhealthy_records']} unhealthy records")
   ```

3. Select templates (e.g., 10% of healthy records):
   ```python
   config = evolver.select_populations(
       fitness_threshold=75.0,
       healthy_sample_size=analysis['healthy_records'] // 10
   )
   ```

4. Run evolution:
   ```python
   evolved_df, results = evolver.evolve_unhealthy_records(config)
   ```

5. Save results:
   ```python
   evolved_df.to_csv('cleaned_data.csv', index=False)
   ```

Key Features
------------

✓ User-configurable population sizes
✓ All unhealthy records included in evolution
✓ Healthy records used as evolutionary templates
✓ Modification tracking (Modified_by_AI column)
✓ Detailed improvement metrics
✓ Early stopping for efficiency
✓ Error handling and logging
✓ Supports any numeric columns (excluding IDs)

Results Dictionary
------------------

The returned results dict contains:

{
  'evolved_records': int,  # How many records were evolved
  'fitness_metrics': {
    'avg_initial_fitness': float,  # Average fitness before evolution
    'avg_evolved_fitness': float,  # Average fitness after evolution
    'improvement': float,  # Average improvement (evolved - initial)
    'records_at_target': int,  # Records achieving 95+ fitness
    'target_achievement_rate': float,  # Percentage achieving target
    'min_improvement': float,  # Worst improvement
    'max_improvement': float,  # Best improvement
  },
  'detailed_results': [  # Per-record statistics
    {
      'record_index': int,
      'original_fitness': float,
      'evolved_fitness': float,
      'improvement': float,
      'generations': int,
      'converged': bool
    },
    ...
  ],
  'evolution_configs': {
    'unhealthy_count': int,
    'healthy_count': int,
    'target_columns': list,
    'ga_config': str
  }
}

Performance Considerations
--------------------------

Time per record evolution:
- Small dataset (10 features, 20 pop, 50 gens): ~0.5 seconds
- Medium dataset (20 features, 50 pop, 100 gens): ~2 seconds
- Large dataset (50 features, 100 pop, 200 gens): ~10+ seconds

Total time = unhealthy_records * time_per_record

Tips for Faster Evolution:
1. Use smaller population_size (20 instead of 50)
2. Use fewer generations (50 instead of 100)
3. Enable early_stopping (default True)
4. Sample healthy records (don't use all)
5. Target only the most important columns

Troubleshooting
---------------

Q: All records are marked as healthy
A: Your fitness threshold may be too low. Try fitness_threshold=75.0 or 80.0

Q: Evolution is very slow
A: Reduce population_size or generations, or sample fewer healthy records

Q: Improvements are minimal
A: Healthy and unhealthy records may be too similar, or evolution parameters need adjustment

Q: ModuleNotFoundError
A: Ensure ga_fitness_evolver.py, ga_engine.py, ga_operators.py, and ga_genotype_phenotype.py are in the same directory

References
----------

DataFitnessEvaluator:
  - File: data_fitness.py
  - Method: evaluate_record_fitness(row_idx) -> Dict[str, Any]
  - Returns: {overall_fitness, missing_score, type_consistency_score, sqlite_compatibility_score, issues}

GAConfig:
  - File: ga_operators.py
  - Parameters: population_size, generations, crossover_rate, mutation_rate, early_stopping, etc.

GeneticAlgorithmEngine:
  - File: ga_engine.py
  - Method: run(use_async=False) -> GAResult
  - Returns: {best_fitness, best_phenotype, generation, converged, ...}

RealValuedMapper:
  - File: ga_genotype_phenotype.py
  - Maps continuous values in [0, 1] to phenotype space

API Reference
-------------

class DataFitnessEvolverGA:
    def __init__(df, track_modifications=True)
    def analyze_population(fitness_threshold=85.0) -> Dict
    def select_populations(fitness_threshold=85.0, healthy_sample_size=None) -> PopulationConfig
    def evolve_unhealthy_records(config, ga_config=None) -> Tuple[DataFrame, Dict]

@dataclass PopulationConfig:
    unhealthy_indices: List[int]
    healthy_indices: List[int]
    unhealthy_count: int
    healthy_count: int
    target_columns: List[str]
    fitness_threshold: float
    column_bounds: Dict[str, Tuple[float, float]]

function evolve_records(df, fitness_threshold=85.0, healthy_sample_size=None, ga_config=None) -> Tuple[DataFrame, Dict]:
    """Convenience function for quick evolution"""
