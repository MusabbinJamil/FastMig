# Differential Evolution (DE) Implementation

## Overview

The DE implementation provides a complete differential evolution engine for numeric cell evolution. It supports all 6 standard mutation strategies, both crossover types, and adaptive parameter control.

## Files

- `de_operators.py` - Enums, configuration, metrics, and operator functions
- `de_engine.py` - Main DE engine class

## Configuration

### DEConfig Dataclass

```python
@dataclass
class DEConfig:
    population_size: int = 30
    generations: int = 100
    scale_factor: float = 0.8         # F parameter
    crossover_rate: float = 0.9       # CR parameter
    mutation_strategy: DEMutationStrategy = DEMutationStrategy.RAND_1
    crossover_type: DECrossoverType = DECrossoverType.BINOMIAL
    adaptive_f: bool = False
    adaptive_cr: bool = False
    f_min: float = 0.1
    f_max: float = 1.0
    cr_min: float = 0.1
    cr_max: float = 1.0
    adaptation_rate: float = 0.1
    constraint_handling: ConstraintHandling = ConstraintHandling.CLAMP
    early_stopping: bool = True
    patience: int = 10
    min_improvement: float = 1e-6
    fitness_threshold: float = 0.95
```

## Mutation Strategies

### DEMutationStrategy Enum

| Strategy | Value | Formula |
|----------|-------|---------|
| `RAND_1` | `"DE/rand/1"` | v = x_r1 + F*(x_r2 - x_r3) |
| `RAND_2` | `"DE/rand/2"` | v = x_r1 + F*(x_r2 - x_r3) + F*(x_r4 - x_r5) |
| `BEST_1` | `"DE/best/1"` | v = x_best + F*(x_r1 - x_r2) |
| `BEST_2` | `"DE/best/2"` | v = x_best + F*(x_r1 - x_r2) + F*(x_r3 - x_r4) |
| `CURRENT_TO_BEST_1` | `"DE/current-to-best/1"` | v = x_i + F*(x_best - x_i) + F*(x_r1 - x_r2) |
| `CURRENT_TO_RAND_1` | `"DE/current-to-rand/1"` | v = x_i + F*(x_r1 - x_i) + F*(x_r2 - x_r3) |

### Strategy Characteristics

| Strategy | Exploration | Exploitation | Use Case |
|----------|-------------|--------------|----------|
| `DE/rand/1` | High | Low | Unknown problem landscape |
| `DE/rand/2` | Very High | Very Low | Highly multimodal problems |
| `DE/best/1` | Low | High | Unimodal, fast convergence needed |
| `DE/best/2` | Low | Very High | Strong exploitation, fine-tuning |
| `DE/current-to-best/1` | Medium | Medium | Balanced exploration/exploitation |
| `DE/current-to-rand/1` | High | Medium | Exploration with some greediness |

## Crossover Types

### DECrossoverType Enum

| Type | Value | Description |
|------|-------|-------------|
| `BINOMIAL` | `"binomial"` | Standard binomial crossover |
| `EXPONENTIAL` | `"exponential"` | Exponential (contiguous) crossover |

### Crossover Details

#### Binomial Crossover
Each dimension is independently selected from mutant with probability CR:
```python
trial[j] = mutant[j] if rand() < CR or j == j_rand else target[j]
```

#### Exponential Crossover
Contiguous block of dimensions from mutant:
```python
# Start at random position, copy until CR fails
start = randint(0, D)
L = 0
while rand() < CR and L < D:
    trial[(start + L) % D] = mutant[(start + L) % D]
    L += 1
```

## Adaptive Parameters

### Adaptive F (Scale Factor)

When `adaptive_f=True`, F is adjusted based on success rate:
```python
if success_rate > target_success:
    F = F * (1 + adaptation_rate)  # Increase exploration
else:
    F = F * (1 - adaptation_rate)  # Decrease exploration
F = clamp(F, f_min, f_max)
```

### Adaptive CR (Crossover Rate)

When `adaptive_cr=True`, CR is adjusted similarly:
```python
if success_rate > target_success:
    CR = CR * (1 + adaptation_rate)  # More from mutant
else:
    CR = CR * (1 - adaptation_rate)  # More from target
CR = clamp(CR, cr_min, cr_max)
```

## Constraint Handling

### ConstraintHandling Enum

| Method | Value | Description |
|--------|-------|-------------|
| `CLAMP` | `"clamp"` | Clip to bounds |
| `REFLECT` | `"reflect"` | Bounce off boundaries |
| `ABSORB` | `"absorb"` | Set to boundary value |
| `RANDOM` | `"random"` | Reinitialize randomly |

## Operators

### DEOperators Static Class

```python
class DEOperators:
    @staticmethod
    def initialize_population(pop_size, bounds_min, bounds_max,
                               seed_values=None, seed_ratio=0.5)

    @staticmethod
    def apply_mutation(strategy, population, fitness, target_idx, F)

    @staticmethod
    def apply_crossover(crossover_type, target, mutant, CR)

    @staticmethod
    def apply_constraints(value, bounds_min, bounds_max, handling)

    @staticmethod
    def greedy_selection(target_value, target_fitness,
                          trial_value, trial_fitness)

    @staticmethod
    def adapt_f(current_f, success_rate, f_min, f_max, learning_rate)

    @staticmethod
    def adapt_cr(current_cr, success_rate, cr_min, cr_max, learning_rate)

    @staticmethod
    def calculate_diversity(population)

    @staticmethod
    def calculate_convergence_rate(fitness_history, window=10)
```

## Metrics

### DEMetrics Dataclass

```python
@dataclass
class DEMetrics:
    generation: int
    best_fitness: float
    average_fitness: float
    worst_fitness: float
    population_diversity: float
    convergence_rate: float
    success_rate: float
    trials_evaluated: int
    improvements: int
    current_f: float
    current_cr: float
    stagnation_counter: int
```

## Result

### DEResult Dataclass

```python
@dataclass
class DEResult:
    best_individual: np.ndarray
    best_fitness: float
    worst_fitness: float
    average_fitness: float
    total_generations: int
    converged: bool
    convergence_generation: Optional[int]
    fitness_history: List[float]
    avg_fitness_history: List[float]
    success_rate_history: List[float]
    diversity_history: List[float]
    f_history: List[float]
    cr_history: List[float]
    generation_metrics: List[DEMetrics]
    final_population: np.ndarray
    final_fitness: np.ndarray
    strategy_used: str
    execution_time: float
    errors: List[str]
    config: DEConfig
```

## Usage Example

```python
from de_operators import DEConfig, DEMutationStrategy, DECrossoverType
from de_engine import DifferentialEvolutionOptimizer

# Define fitness function
def fitness_func(value):
    # Higher is better
    return 1.0 - abs(value - target_value) / range_size

# Create configuration
config = DEConfig(
    population_size=30,
    generations=100,
    scale_factor=0.8,
    crossover_rate=0.9,
    mutation_strategy=DEMutationStrategy.RAND_1,
    crossover_type=DECrossoverType.BINOMIAL,
    adaptive_f=True,
    adaptive_cr=True,
    early_stopping=True,
    patience=10
)

# Create optimizer
optimizer = DifferentialEvolutionOptimizer(
    config=config,
    fitness_function=fitness_func,
    bounds_min=0.0,
    bounds_max=100.0,
    seed_values=healthy_cell_values  # Optional seeding
)

# Run optimization
result = optimizer.run()

print(f"Best value: {result.best_individual}")
print(f"Best fitness: {result.best_fitness}")
print(f"Strategy: {result.strategy_used}")
print(f"Final F: {result.f_history[-1]}")
print(f"Final CR: {result.cr_history[-1]}")
```

## Integration with Cell Cleaner

The DE engine is integrated into `evolutionary_cell_cleaner.py`:

```python
def _de_evolve_numeric(self, healthy_cells, fitness_func, min_val, max_val):
    # Maps string config to enums
    strategy = strategy_map.get(config.de_mutation_strategy, DEMutationStrategy.RAND_1)
    crossover_type = crossover_map.get(config.de_crossover_type, DECrossoverType.BINOMIAL)

    # Creates DE config from cell evolution config
    de_config = DEConfig(
        population_size=config.population_size,
        generations=config.generations,
        scale_factor=config.differential_weight,
        crossover_rate=config.crossover_prob,
        mutation_strategy=strategy,
        crossover_type=crossover_type,
        adaptive_f=config.adaptive_f,
        adaptive_cr=config.adaptive_cr,
        # ... other parameters
    )

    # Runs optimization
    optimizer = DifferentialEvolutionOptimizer(...)
    result = optimizer.run()

    return best_value, history
```

## API Parameters

When calling the `/clean/evolve-cells` endpoint with `method: "de"`, you can pass:

```json
{
  "method": "de",
  "config": {
    "population_size": 30,
    "generations": 100,
    "scale_factor": 0.8,
    "crossover_rate": 0.9,
    "de_mutation_strategy": "DE/rand/1",
    "de_crossover_type": "binomial",
    "adaptive_f": false,
    "adaptive_cr": false,
    "f_min": 0.1,
    "f_max": 1.0,
    "cr_min": 0.1,
    "cr_max": 1.0,
    "adaptation_rate": 0.1,
    "early_stopping": true,
    "patience": 10,
    "fitness_threshold": 0.95
  }
}
```

## Best Practices

1. **Strategy Selection**:
   - Start with `DE/rand/1` for unknown problems
   - Use `DE/best/1` when you need fast convergence
   - Use `DE/current-to-best/1` for balanced performance

2. **Parameter Tuning**:
   - F typically in range [0.4, 1.0], default 0.8
   - CR typically in range [0.7, 1.0], default 0.9
   - Higher CR for continuous problems
   - Lower CR for discrete/separable problems

3. **Adaptive Parameters**:
   - Enable for unknown problem difficulty
   - Set reasonable min/max bounds
   - Use adaptation_rate around 0.1

4. **Population Size**:
   - Minimum 4 (needed for mutation)
   - Typically 5-10x the problem dimension
   - Larger for multimodal problems

## Fallback Mechanism

If the DE engine fails (e.g., due to invalid parameters), the system falls back to a simple DE/rand/1 implementation:

```python
try:
    optimizer = DifferentialEvolutionOptimizer(...)
    result = optimizer.run()
except Exception as e:
    logger.error(f"DE engine error: {e}, falling back to simple DE")
    return self._simple_de_evolve(healthy_cells, fitness_func, min_val, max_val)
```
