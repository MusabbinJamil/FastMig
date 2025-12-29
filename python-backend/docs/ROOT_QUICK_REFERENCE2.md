# GA System - Quick Reference Card

## 🚀 Quick Start (Copy & Paste)

### Test 1: GA Operators
```powershell
cd python-backend
python ga_operators.py
```
✓ Tests: Selection, Crossover, Mutation, Metrics

### Test 2: Mapping
```powershell
python ga_genotype_phenotype.py
```
✓ Tests: Real-valued, Binary, Grammar

### Test 3: Engine
```powershell
python ga_engine.py
```
✓ Tests: Full GA execution

### Test 4: All Tests (37 tests)
```powershell
python test_ga_system.py
```
✓ Result: 37/37 PASSING

### Test 5: Full Demo
```powershell
python ga_demo.py
```
✓ Demonstrates: All features

### Test 6: Interactive
```powershell
python ga_cli.py
```
✓ Menu-driven testing

---

## 🎯 Common Code Patterns

### Pattern 1: Simple Optimization
```python
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import RealValuedMapper
from ga_operators import GAConfig
import numpy as np

# Fitness function
fitness = lambda x: -np.sum(np.array(x)**2) if x else -np.inf

# Setup
config = GAConfig(population_size=20, generations=50)
mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
engine = GeneticAlgorithmEngine(config, fitness, mapper)

# Run
result = engine.run()
print(f"Best: {result.best_phenotype}")
print(f"Fitness: {result.best_fitness:.6f}")
```

### Pattern 2: Different Selection
```python
from ga_operators import SelectionMethod

config = GAConfig(
    population_size=20,
    generations=50,
    selection_method=SelectionMethod.TOURNAMENT  # or ROULETTE_WHEEL, RANK_BASED
)
```

### Pattern 3: Binary Representation
```python
from ga_genotype_phenotype import BinaryMapper

mapper = BinaryMapper(interpretation="decimal")
# Genotype [1,0,1,0] → Phenotype 10
```

### Pattern 4: Grammar-Based
```python
from ga_genotype_phenotype import GrammarMapper

grammar = {
    '<expr>': [['<num>'], ['<num>', '+', '<num>']],
    '<num>': [['1'], ['2'], ['3']]
}
mapper = GrammarMapper(grammar, max_depth=5)
```

### Pattern 5: Async Evaluation
```python
result = engine.run(use_async=True)  # Parallel fitness evaluation
```

### Pattern 6: Early Stopping
```python
config = GAConfig(
    population_size=20,
    generations=1000,  # Max generations
    early_stopping=True,
    early_stopping_generations=10,
    early_stopping_threshold=1e-6
)
```

### Pattern 7: Check Results
```python
print(result.best_phenotype)          # Best solution
print(result.best_fitness)            # Best fitness
print(result.convergence_achieved)    # Did it converge early?
print(result.total_generations)       # How many generations?
print(result.execution_time)          # Time elapsed
print(result.errors)                  # Any errors?
```

---

## 📊 Selection Methods

| Method | Command | Use Case |
|--------|---------|----------|
| **Tournament** | `SelectionMethod.TOURNAMENT` | General purpose, tunable |
| **Roulette Wheel** | `SelectionMethod.ROULETTE_WHEEL` | Fitness-proportionate |
| **Rank-Based** | `SelectionMethod.RANK_BASED` | Stable, less variance |

### Configure Selection
```python
config = GAConfig(
    selection_method=SelectionMethod.RANK_BASED,
    tournament_size=3,           # For tournament
    selection_pressure=1.5       # For rank-based
)
```

---

## 🔄 Crossover Methods

| Method | Command | Characteristics |
|--------|---------|-----------------|
| **Single-Point** | `CrossoverMethod.SINGLE_POINT` | Simple, creates 1 cut |
| **Two-Point** | `CrossoverMethod.TWO_POINT` | 2 cuts, more variation |
| **Uniform** | `CrossoverMethod.UNIFORM` | Gene-by-gene swapping |
| **Arithmetic** | `CrossoverMethod.ARITHMETIC` | Weighted averaging |

### Configure Crossover
```python
config = GAConfig(
    crossover_method=CrossoverMethod.TWO_POINT,
    crossover_rate=0.85  # 85% probability
)
```

---

## 🧬 Mutation Methods

| Method | Command | Best For |
|--------|---------|----------|
| **Gaussian** | `MutationMethod.GAUSSIAN` | Continuous, exploration |
| **Uniform** | `MutationMethod.UNIFORM` | Bounded ranges |
| **Adaptive** | `MutationMethod.ADAPTIVE` | Auto-tuning, convergence |

### Configure Mutation
```python
config = GAConfig(
    mutation_method=MutationMethod.ADAPTIVE,
    mutation_rate=0.15,           # 15% probability
    mutation_std=1.0,             # For Gaussian
    adaptive_mutation=True        # Rate decreases over time
)
```

---

## 🗺️ Genotype-Phenotype Mappers

### Real-Valued
```python
from ga_genotype_phenotype import RealValuedMapper
mapper = RealValuedMapper(min_val=-10.0, max_val=10.0)
# Genotype [0.0, 0.5, 1.0] → Phenotype [-10, 0, 10]
```

### Binary
```python
from ga_genotype_phenotype import BinaryMapper
mapper = BinaryMapper(interpretation="decimal")
# Genotype [1,0,1,0] → Phenotype 10
```

### Grammar
```python
from ga_genotype_phenotype import GrammarMapper
grammar = {'<expr>': [['1'], ['1', '+', '2']]}
mapper = GrammarMapper(grammar, max_depth=5)
# Genotype [0.1, 0.5] → Phenotype "1+2"
```

---

## 📈 Metrics Available

```python
result.generation_metrics  # List of per-generation metrics
# Each contains:
#   - generation: int
#   - best_fitness: float
#   - worst_fitness: float
#   - average_fitness: float
#   - population_diversity: float
#   - convergence_rate: float
#   - selections_performed: int
#   - crossovers_performed: int
#   - mutations_performed: int
```

---

## ⚙️ Parameter Defaults

```python
GAConfig(
    population_size=50,
    generations=100,
    selection_method='tournament',
    crossover_method='single_point',
    mutation_method='gaussian',
    crossover_rate=0.8,
    mutation_rate=0.1,
    elitism_rate=0.05,
    early_stopping=False,
    early_stopping_generations=20,
    early_stopping_threshold=1e-6
)
```

---

## 🧪 Testing

```powershell
# Run all tests
python test_ga_system.py

# Run specific test class
python -m unittest test_ga_system.TestGAConfig -v

# Run specific test
python -m unittest test_ga_system.TestGAConfig.test_valid_config -v

# Run tests matching pattern
python -m unittest test_ga_system -k "selection" -v
```

---

## 📝 Common Fitness Functions

### Minimize Sum of Squares (Sphere)
```python
fitness = lambda x: -np.sum(np.array(x)**2)
```

### Rosenbrock Function
```python
def rosenbrock(x):
    x = np.array(x)
    return -sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
```

### Rastrigin Function
```python
def rastrigin(x):
    x = np.array(x)
    return -(10 * len(x) + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))
```

### Custom Function
```python
def my_fitness(phenotype):
    try:
        if phenotype is None:
            return -np.inf
        # Calculate fitness
        score = compute_quality(phenotype)
        return score if not np.isnan(score) else -np.inf
    except:
        return -np.inf
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid phenotype" | Check mapper validation, fitness function |
| "NaN fitness" | Handle exceptions in fitness function |
| "Slow convergence" | Increase population size or generations |
| "No improvement" | Try different selection/mutation methods |
| "Out of memory" | Reduce population size or generations |

---

## 📚 File Guide

| File | Purpose | Run it |
|------|---------|--------|
| `ga_operators.py` | Core operators | `python ga_operators.py` |
| `ga_genotype_phenotype.py` | Mappers | `python ga_genotype_phenotype.py` |
| `ga_engine.py` | GA execution | `python ga_engine.py` |
| `test_ga_system.py` | Unit tests | `python test_ga_system.py` |
| `ga_cli.py` | Interactive menu | `python ga_cli.py` |
| `ga_demo.py` | Demonstrations | `python ga_demo.py` |
| `GA_EXAMPLES.py` | Code examples | View in editor |
| `GA_SYSTEM_README.md` | Full docs | Read in editor |
| `IMPLEMENTATION_SUMMARY.md` | Completion report | Read in editor |

---

## ⚡ Performance Tips

1. **Larger population** → Better coverage but slower
2. **More generations** → Better convergence but slower
3. **Higher mutation rate** → More exploration, less exploitation
4. **Higher crossover rate** → More mixing of solutions
5. **Async evaluation** → Faster on multi-core systems
6. **Early stopping** → Avoid unnecessary generations

---

## ✅ Verification Checklist

- [ ] Run `python ga_operators.py` - All operators work
- [ ] Run `python ga_genotype_phenotype.py` - All mappers work
- [ ] Run `python ga_engine.py` - Engine executes
- [ ] Run `python test_ga_system.py` - All 37 tests pass
- [ ] Run `python ga_demo.py` - All demos run
- [ ] Try `python ga_cli.py` - Interactive menu works

---

## 🎓 Learning Path

1. Start: `GA_EXAMPLES.py` - Copy paste examples
2. Test: `python ga_demo.py` - See all features
3. Explore: `python ga_cli.py` - Interactive testing
4. Deep Dive: Read `GA_SYSTEM_README.md`
5. Integrate: Use in your code

---

**Status**: ✅ Production Ready
**Tests**: 37/37 Passing
**Last Update**: 2024
