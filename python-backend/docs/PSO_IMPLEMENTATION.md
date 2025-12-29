# Particle Swarm Optimization (PSO) Implementation

## Overview

The PSO implementation provides a complete particle swarm optimization engine for numeric cell evolution. It supports multiple topologies, variants, and constraint handling methods.

## Files

- `pso_operators.py` - Enums, configuration, metrics, and operator functions
- `pso_engine.py` - Main PSO engine class

## Configuration

### PSOConfig Dataclass

```python
@dataclass
class PSOConfig:
    swarm_size: int = 30
    iterations: int = 100
    inertia_weight: float = 0.7
    inertia_min: float = 0.4
    inertia_max: float = 0.9
    cognitive_coeff: float = 1.5      # c1 - Personal best attraction
    social_coeff: float = 1.5         # c2 - Global best attraction
    velocity_clamp: float = 0.2       # Max velocity as fraction of range
    topology: PSOTopology = PSOTopology.GLOBAL_BEST
    variant: PSOVariant = PSOVariant.STANDARD
    constriction_factor: float = 0.729
    neighborhood_size: int = 3
    constraint_handling: ConstraintHandling = ConstraintHandling.CLAMP
    early_stopping: bool = True
    patience: int = 10
    min_improvement: float = 1e-6
    fitness_threshold: float = 0.95
```

## Topologies

### PSOTopology Enum

| Topology | Value | Description |
|----------|-------|-------------|
| `GLOBAL_BEST` | `"gbest"` | All particles connected (star topology) |
| `LOCAL_BEST` | `"lbest"` | Ring topology with neighborhood |
| `RING` | `"ring"` | Alias for local best |
| `RANDOM` | `"random"` | Random neighbors each iteration |
| `VON_NEUMANN` | `"von_neumann"` | 2D grid topology |

### Topology Characteristics

- **Global Best (gbest)**: Fast convergence, risk of premature convergence
- **Local Best (lbest)**: Slower but more thorough exploration
- **Ring**: Similar to lbest, particles connected in a ring
- **Random**: Good exploration, neighbors change each iteration
- **Von Neumann**: 2D grid, balanced exploration/exploitation

## Variants

### PSOVariant Enum

| Variant | Value | Description |
|---------|-------|-------------|
| `STANDARD` | `"standard"` | Classic PSO with inertia weight |
| `CONSTRICTION` | `"constriction"` | Clerc's constriction factor method |
| `INERTIA_DECAY` | `"inertia_decay"` | Linear inertia weight decay |

### Variant Details

#### Standard PSO
Classic velocity update equation:
```
v(t+1) = w * v(t) + c1 * r1 * (pbest - x) + c2 * r2 * (gbest - x)
```

#### Constriction Factor PSO
Uses Clerc's constriction factor (chi):
```
chi = 2 / |2 - phi - sqrt(phi^2 - 4*phi)|
where phi = c1 + c2 (typically phi > 4)
```

#### Inertia Decay PSO
Linearly decreases inertia weight over iterations:
```
w(t) = w_max - (w_max - w_min) * (t / max_iterations)
```

## Constraint Handling

### ConstraintHandling Enum

| Method | Value | Description |
|--------|-------|-------------|
| `CLAMP` | `"clamp"` | Clip to bounds |
| `REFLECT` | `"reflect"` | Bounce off boundaries |
| `ABSORB` | `"absorb"` | Set velocity to zero at boundary |
| `RANDOM` | `"random"` | Reinitialize randomly within bounds |

## Operators

### PSOOperators Static Class

```python
class PSOOperators:
    @staticmethod
    def initialize_swarm(swarm_size, bounds_min, bounds_max, seed_values=None)

    @staticmethod
    def update_velocity_standard(velocity, position, pbest, gbest,
                                  inertia, c1, c2, velocity_max)

    @staticmethod
    def update_velocity_constriction(velocity, position, pbest, gbest,
                                      c1, c2, chi, velocity_max)

    @staticmethod
    def update_position(position, velocity, bounds_min, bounds_max, handling)

    @staticmethod
    def get_neighborhood_best(particle_idx, positions, fitness,
                               topology, neighborhood_size, swarm_size)

    @staticmethod
    def calculate_diversity(positions)

    @staticmethod
    def decay_inertia(current_iteration, max_iterations, w_max, w_min)
```

## Metrics

### PSOMetrics Dataclass

```python
@dataclass
class PSOMetrics:
    iteration: int
    global_best_fitness: float
    average_fitness: float
    worst_fitness: float
    average_velocity: float
    velocity_std: float
    swarm_diversity: float
    convergence_rate: float
    stagnation_counter: int
    current_inertia: float
```

## Result

### PSOResult Dataclass

```python
@dataclass
class PSOResult:
    best_position: np.ndarray
    best_fitness: float
    worst_fitness: float
    average_fitness: float
    total_iterations: int
    converged: bool
    convergence_iteration: Optional[int]
    fitness_history: List[float]
    avg_fitness_history: List[float]
    velocity_history: List[float]
    diversity_history: List[float]
    inertia_history: List[float]
    iteration_metrics: List[PSOMetrics]
    final_swarm: np.ndarray
    final_velocities: np.ndarray
    final_pbest: np.ndarray
    final_pbest_fitness: np.ndarray
    execution_time: float
    errors: List[str]
    config: PSOConfig
```

## Usage Example

```python
from pso_operators import PSOConfig, PSOTopology, PSOVariant
from pso_engine import ParticleSwarmOptimizer

# Define fitness function
def fitness_func(value):
    # Higher is better
    return 1.0 - abs(value - target_value) / range_size

# Create configuration
config = PSOConfig(
    swarm_size=30,
    iterations=100,
    inertia_weight=0.7,
    cognitive_coeff=1.5,
    social_coeff=1.5,
    topology=PSOTopology.GLOBAL_BEST,
    variant=PSOVariant.STANDARD,
    early_stopping=True,
    patience=10
)

# Create optimizer
optimizer = ParticleSwarmOptimizer(
    config=config,
    fitness_function=fitness_func,
    bounds_min=0.0,
    bounds_max=100.0,
    seed_values=healthy_cell_values  # Optional seeding
)

# Run optimization
result = optimizer.run()

print(f"Best value: {result.best_position}")
print(f"Best fitness: {result.best_fitness}")
print(f"Converged: {result.converged}")
print(f"Iterations: {result.total_iterations}")
```

## Integration with Cell Cleaner

The PSO engine is integrated into `evolutionary_cell_cleaner.py`:

```python
def _pso_evolve_numeric(self, healthy_cells, fitness_func, min_val, max_val):
    # Maps string config to enums
    topology = topology_map.get(config.pso_topology, PSOTopology.GLOBAL_BEST)
    variant = variant_map.get(config.pso_variant, PSOVariant.STANDARD)

    # Creates PSO config from cell evolution config
    pso_config = PSOConfig(
        swarm_size=config.population_size,
        iterations=config.generations,
        # ... other parameters
    )

    # Runs optimization
    optimizer = ParticleSwarmOptimizer(...)
    result = optimizer.run()

    return best_value, history
```

## API Parameters

When calling the `/clean/evolve-cells` endpoint with `method: "pso"`, you can pass:

```json
{
  "method": "pso",
  "config": {
    "population_size": 30,
    "generations": 100,
    "inertia_weight": 0.7,
    "inertia_min": 0.4,
    "inertia_max": 0.9,
    "cognitive_coeff": 1.5,
    "social_coeff": 1.5,
    "velocity_clamp": 0.2,
    "pso_topology": "gbest",
    "pso_variant": "standard",
    "constriction_factor": 0.729,
    "neighborhood_size": 3,
    "early_stopping": true,
    "patience": 10,
    "fitness_threshold": 0.95
  }
}
```

## Best Practices

1. **Topology Selection**:
   - Use `gbest` for fast convergence on simple problems
   - Use `lbest` or `ring` for complex multimodal problems
   - Use `random` when unsure about problem landscape

2. **Parameter Tuning**:
   - c1 + c2 should be around 4.0 for stability
   - Higher inertia (0.7-0.9) for exploration
   - Lower inertia (0.4-0.6) for exploitation

3. **Variant Selection**:
   - `standard`: Good default, easy to understand
   - `constriction`: Better convergence guarantees
   - `inertia_decay`: Good for unknown problem difficulty
