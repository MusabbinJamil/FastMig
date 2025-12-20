"""
GA System Quick Start Guide & Examples
=======================================
This file contains copy-paste examples for testing GA components.
"""

# ============================================================================
# EXAMPLE 1: Test GA Operators from Command Prompt
# ============================================================================
"""
from ga_operators import *
import numpy as np

# Create test population
population = [np.random.randn(5) for _ in range(4)]
fitness_scores = [float(np.sum(ind**2)) for ind in population]

# Test Tournament Selection
selected, stats = GAOperators.selection_tournament(
    population, fitness_scores, 2, tournament_size=2
)
print(f"Selected {len(selected)} parents via tournament selection")

# Test Crossover
parent1, parent2 = population[0], population[1]
child1, child2 = GAOperators.crossover_single_point(parent1, parent2)
print(f"Crossover created 2 children")

# Test Mutation
mutated = GAOperators.mutation_gaussian(child1, mutation_rate=0.5, std=0.1)
print(f"Mutated child1")

# Calculate metrics
diversity = GAOperators.calculate_population_diversity(population)
print(f"Population diversity: {diversity:.4f}")
"""

# ============================================================================
# EXAMPLE 2: Test Genotype-Phenotype Mapping
# ============================================================================
"""
from ga_genotype_phenotype import *
import numpy as np

# Real-valued mapping
mapper = RealValuedMapper(min_val=-10.0, max_val=10.0)
genotype = np.array([0.0, 0.5, 1.0])
phenotype = mapper.genotype_to_phenotype(genotype)
print(f"Genotype {genotype} -> Phenotype {phenotype}")

is_valid, error = mapper.validate_phenotype(phenotype)
print(f"Valid: {is_valid}")

# Binary mapping
binary_mapper = BinaryMapper(interpretation="decimal")
bin_genotype = np.array([1, 0, 1, 0])
bin_phenotype = binary_mapper.genotype_to_phenotype(bin_genotype)
print(f"Binary {bin_genotype} -> Decimal {bin_phenotype}")

# Grammar mapping
grammar = {
    '<expr>': [
        ['<num>'],
        ['<num>', '+', '<num>'],
        ['<num>', '-', '<num>']
    ],
    '<num>': [['1'], ['2'], ['3']]
}
grammar_mapper = GrammarMapper(grammar)
grammar_genotype = np.array([0.1, 0.5, 0.9])
grammar_phenotype = grammar_mapper.genotype_to_phenotype(grammar_genotype)
print(f"Grammar expression: {grammar_phenotype}")
"""

# ============================================================================
# EXAMPLE 3: Run Complete GA Engine
# ============================================================================
"""
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import RealValuedMapper
from ga_operators import GAConfig
import numpy as np

# Define fitness function (minimize x^2 + y^2)
def sphere_fitness(phenotype):
    try:
        x = np.array(phenotype, dtype=float).flatten()
        return -np.sum(x**2)  # Negate because we maximize
    except:
        return -np.inf

# Setup GA
config = GAConfig(
    population_size=20,
    generations=50,
    crossover_rate=0.8,
    mutation_rate=0.1,
    early_stopping=True,
    early_stopping_generations=5
)

mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)

# Create and run GA
engine = GeneticAlgorithmEngine(config, sphere_fitness, mapper)
result = engine.run()

print(f"Best fitness: {result.best_fitness:.6f}")
print(f"Best phenotype: {result.best_phenotype}")
print(f"Generations: {result.total_generations}")
print(f"Time: {result.execution_time:.2f}s")
"""

# ============================================================================
# EXAMPLE 4: Test Unit Tests
# ============================================================================
"""
# Run from command prompt:
python test_ga_system.py

# Or run specific test:
python -m unittest test_ga_system.TestGAConfig.test_valid_config -v

# Run all tests in TestGAEngine:
python -m unittest test_ga_system.TestGAEngine -v
"""

# ============================================================================
# EXAMPLE 5: Interactive CLI
# ============================================================================
"""
# From command prompt:
python ga_cli.py

# Then use interactive menu to:
# 1. Test individual operators
# 2. Configure GA parameters
# 3. Create population
# 4. Select fitness function
# 5. Run GA
# 6. View/save results
"""

# ============================================================================
# EXAMPLE 6: Custom Fitness Function Tests
# ============================================================================
"""
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import RealValuedMapper
from ga_operators import GAConfig, MutationMethod
import numpy as np

# Rosenbrock function (harder optimization problem)
def rosenbrock(phenotype):
    try:
        x = np.array(phenotype, dtype=float).flatten()
        if len(x) < 2:
            return -np.inf
        # Negate because we maximize
        return -sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
    except:
        return -np.inf

# Test with adaptive mutation
config = GAConfig(
    population_size=30,
    generations=100,
    mutation_method=MutationMethod.ADAPTIVE,
    crossover_rate=0.9,
    mutation_rate=0.2,
    early_stopping=False
)

mapper = RealValuedMapper(min_val=-2.0, max_val=2.0)
engine = GeneticAlgorithmEngine(config, rosenbrock, mapper)
result = engine.run()

print(f"Rosenbrock optimization result: {result.best_fitness:.6f}")
print(f"Solution: {result.best_phenotype}")
"""

# ============================================================================
# EXAMPLE 7: Different Selection Methods
# ============================================================================
"""
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import RealValuedMapper
from ga_operators import GAConfig, SelectionMethod
import numpy as np

# Simple fitness
def fitness(x):
    return -np.sum(np.array(x)**2) if x is not None else -np.inf

mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)

for selection_method in [SelectionMethod.TOURNAMENT, 
                          SelectionMethod.ROULETTE_WHEEL,
                          SelectionMethod.RANK_BASED]:
    config = GAConfig(
        population_size=15,
        generations=20,
        selection_method=selection_method
    )
    
    engine = GeneticAlgorithmEngine(config, fitness, mapper)
    result = engine.run()
    
    print(f"{selection_method.value}: Best={result.best_fitness:.4f}")
"""

# ============================================================================
# EXAMPLE 8: Compare Crossover Methods
# ============================================================================
"""
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import RealValuedMapper
from ga_operators import GAConfig, CrossoverMethod
import numpy as np

def fitness(x):
    return -np.sum(np.array(x)**2) if x is not None else -np.inf

mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)

for crossover_method in [CrossoverMethod.SINGLE_POINT,
                          CrossoverMethod.TWO_POINT,
                          CrossoverMethod.UNIFORM,
                          CrossoverMethod.ARITHMETIC]:
    config = GAConfig(
        population_size=15,
        generations=20,
        crossover_method=crossover_method,
        crossover_rate=0.9
    )
    
    engine = GeneticAlgorithmEngine(config, fitness, mapper)
    result = engine.run()
    
    print(f"{crossover_method.value}: Best={result.best_fitness:.4f}")
"""

# ============================================================================
# EXAMPLE 9: Grammar-Based Optimization
# ============================================================================
"""
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import GrammarMapper
from ga_operators import GAConfig
import numpy as np
import re

# Grammar for mathematical expressions
grammar = {
    '<expr>': [
        ['<var>'],
        ['<expr>', '+', '<expr>'],
        ['<expr>', '-', '<expr>'],
        ['<expr>', '*', '<expr>'],
    ],
    '<var>': [['x'], ['y'], ['1'], ['2']]
}

# Fitness evaluates expression quality
def expr_fitness(phenotype):
    try:
        if phenotype is None or phenotype.startswith('<error'):
            return -np.inf
        
        # Simple heuristic: prefer shorter, valid expressions
        return -len(phenotype)
    except:
        return -np.inf

config = GAConfig(
    population_size=20,
    generations=30
)

mapper = GrammarMapper(grammar, max_depth=5)
engine = GeneticAlgorithmEngine(config, expr_fitness, mapper)
result = engine.run()

print(f"Best expression: {result.best_phenotype}")
print(f"Expression fitness: {result.best_fitness:.4f}")
"""

# ============================================================================
# EXAMPLE 10: Monitor Convergence
# ============================================================================
"""
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import RealValuedMapper
from ga_operators import GAConfig
import numpy as np

def fitness(x):
    return -np.sum(np.array(x)**2) if x is not None else -np.inf

config = GAConfig(
    population_size=20,
    generations=100,
    early_stopping=True,
    early_stopping_generations=10,
    early_stopping_threshold=1e-4
)

mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
engine = GeneticAlgorithmEngine(config, fitness, mapper)
result = engine.run()

# Analyze convergence
print(f"Total generations: {result.total_generations}")
print(f"Converged early: {result.convergence_achieved}")

# Print fitness progress
print("\\nFitness progression:")
for i, metric in enumerate(result.generation_metrics):
    if i % 5 == 0:
        if isinstance(metric, dict):
            print(f"Gen {metric['generation']}: {metric['best_fitness']:.6f}")
"""

if __name__ == "__main__":
    print(__doc__)
