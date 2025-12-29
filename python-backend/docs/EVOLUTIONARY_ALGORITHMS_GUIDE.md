# Evolutionary Algorithms Quick Guide

## Available Algorithms

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| **GA** | Genetic Algorithm | General optimization, discrete problems |
| **PSO** | Particle Swarm Optimization | Continuous optimization, fast convergence |
| **DE** | Differential Evolution | Robust optimization, noisy fitness |
| **ES** | Evolution Strategy | Self-adaptive step sizes, precision |

---

## Quick Start

```bash
cd python-backend

# Run demos to see all features
python ga_demo.py
python pso_demo.py
python de_demo.py
python es_demo.py

# Interactive CLIs for testing
python ga_cli.py
python pso_cli.py
python de_cli.py
python es_cli.py

# Run unit tests
python test_ga_system.py
python test_pso_system.py
python test_de_system.py
python test_es_system.py
```

---

## How Each Algorithm Works

### GA (Genetic Algorithm)
```
Population → Selection → Crossover → Mutation → New Population
```
- **Selection**: Tournament, Roulette Wheel, Rank-Based
- **Crossover**: Single-Point, Two-Point, Uniform, Arithmetic
- **Mutation**: Gaussian, Uniform, Adaptive

```python
from ga_engine import GeneticAlgorithmEngine
from ga_operators import GAConfig
from ga_genotype_phenotype import RealValuedMapper

config = GAConfig(population_size=50, generations=100)
mapper = RealValuedMapper(min_val=-10, max_val=10)
engine = GeneticAlgorithmEngine(config, fitness_func, mapper)
result = engine.run()
```

### PSO (Particle Swarm Optimization)
```
Particles fly through search space, attracted to:
  - Their personal best position (pbest)
  - The swarm's global best position (gbest)
```
- **Velocity**: `v = w*v + c1*r1*(pbest-x) + c2*r2*(gbest-x)`
- **Position**: `x = x + v`
- **Topologies**: Global Best, Ring, Random, Von Neumann

```python
from pso_engine import optimize_value_pso
from pso_operators import PSOConfig, PSOTopology

config = PSOConfig(swarm_size=30, iterations=100, topology=PSOTopology.GLOBAL_BEST)
result = optimize_value_pso(fitness_func, bounds_min=-10, bounds_max=10, config=config)
```

### DE (Differential Evolution)
```
For each individual:
  1. Mutant = base + F * (diff1 - diff2)
  2. Trial = crossover(target, mutant)
  3. Keep better of target vs trial
```
- **Strategies**: rand/1, rand/2, best/1, best/2, current-to-best/1, current-to-rand/1
- **F** (scale factor): Controls step size (0.4-1.0)
- **CR** (crossover rate): How much from mutant (0.0-1.0)

```python
from de_engine import optimize_value_de
from de_operators import DEConfig, DEMutationStrategy

config = DEConfig(population_size=30, generations=100, mutation_strategy=DEMutationStrategy.BEST_1)
result = optimize_value_de(fitness_func, bounds_min=-10, bounds_max=10, config=config)
```

### ES (Evolution Strategy)
```
(μ+λ) or (μ,λ) selection with self-adaptive mutation:
  1. Recombine parents → offspring base
  2. Mutate sigma: σ' = σ * exp(τ*N(0,1))
  3. Mutate value: x' = x + σ'*N(0,1)
  4. Select best μ individuals
```
- **Selection**: Plus (μ+λ) or Comma (μ,λ)
- **Recombination**: Discrete, Intermediate, Global
- **Self-Adaptive**: Step size evolves with solution

```python
from es_engine import optimize_value_es
from es_operators import ESConfig, ESSelectionType

config = ESConfig(mu=15, lambda_=100, selection_type=ESSelectionType.PLUS, self_adaptive=True)
result = optimize_value_es(fitness_func, bounds_min=-10, bounds_max=10, config=config)
```

---

## Comparison

| Feature | GA | PSO | DE | ES |
|---------|----|----|----|----|
| Convergence Speed | Medium | Fast | Medium | Medium |
| Exploration | High | Medium | High | Medium |
| Parameter Sensitivity | Medium | High | Low | Low |
| Self-Adaptation | No | No | Optional | Yes |
| Memory Usage | Low | Low | Low | Low |

---

## Key Parameters

### Common to All
- **Population/Swarm Size**: 20-100 typical
- **Generations/Iterations**: 50-500 typical
- **Early Stopping**: Stop when fitness threshold reached

### Algorithm-Specific
| GA | PSO | DE | ES |
|----|-----|----|----|
| mutation_rate: 0.1 | w (inertia): 0.7 | F (scale): 0.8 | μ (parents): 15 |
| crossover_rate: 0.8 | c1, c2: 1.5-2.0 | CR (crossover): 0.9 | λ (offspring): 100 |
| elitism: 2 | velocity_clamp: 0.2 | adaptive_f: True | self_adaptive: True |
