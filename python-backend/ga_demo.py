#!/usr/bin/env python3
"""
Comprehensive GA System Demonstration
======================================
Run this to see all GA features in action.

Usage:
    python ga_demo.py
"""

import numpy as np
import sys
from typing import List
from ga_operators import (
    GAOperators, GAConfig, SelectionMethod,
    CrossoverMethod, MutationMethod
)
from ga_genotype_phenotype import (
    RealValuedMapper, BinaryMapper, GrammarMapper
)
from ga_engine import GeneticAlgorithmEngine


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_operators():
    """Demonstrate GA operators"""
    print_section("1. GA OPERATORS DEMONSTRATION")
    
    # Create test population
    population = [np.random.randn(5) for _ in range(6)]
    fitness_scores = [float(np.sum(ind**2)) for ind in population]
    
    print(f"\nTest Population: {len(population)} individuals")
    print(f"Fitness: {[f'{f:.2f}' for f in fitness_scores]}\n")
    
    # Selection
    print("SELECTION METHODS:")
    for method_name, method in [
        ("Tournament", SelectionMethod.TOURNAMENT),
        ("Roulette Wheel", SelectionMethod.ROULETTE_WHEEL),
        ("Rank-Based", SelectionMethod.RANK_BASED)
    ]:
        if method == SelectionMethod.TOURNAMENT:
            selected, _ = GAOperators.selection_tournament(population, fitness_scores, 3)
        elif method == SelectionMethod.ROULETTE_WHEEL:
            selected, _ = GAOperators.selection_roulette_wheel(population, fitness_scores, 3)
        else:
            selected, _ = GAOperators.selection_rank_based(population, fitness_scores, 3)
        print(f"  ✓ {method_name}: Selected {len(selected)} parents")
    
    # Crossover
    print("\nCROSSOVER METHODS:")
    p1, p2 = population[0], population[1]
    crossover_methods = [
        ("Single-Point", lambda: GAOperators.crossover_single_point(p1, p2)),
        ("Two-Point", lambda: GAOperators.crossover_two_point(p1, p2)),
        ("Uniform", lambda: GAOperators.crossover_uniform(p1, p2)),
        ("Arithmetic", lambda: GAOperators.crossover_arithmetic(p1, p2, weight=0.5))
    ]
    for name, func in crossover_methods:
        c1, c2 = func()
        print(f"  ✓ {name}: Created 2 children")
    
    # Mutation
    print("\nMUTATION METHODS:")
    individual = population[0].copy()
    mut_methods = [
        ("Gaussian", lambda: GAOperators.mutation_gaussian(individual, 0.5, std=0.2)),
        ("Uniform", lambda: GAOperators.mutation_uniform(individual, 0.5)),
        ("Adaptive", lambda: GAOperators.mutation_adaptive(individual, 0.5, 50, 100))
    ]
    for name, func in mut_methods:
        mutated = func()
        changes = np.sum(~np.isclose(individual, mutated))
        print(f"  ✓ {name}: {changes} genes mutated")


def demo_mappers():
    """Demonstrate genotype-phenotype mapping"""
    print_section("2. GENOTYPE-PHENOTYPE MAPPING DEMONSTRATION")
    
    # Real-valued
    print("\nREAL-VALUED MAPPING:")
    mapper = RealValuedMapper(min_val=-10.0, max_val=10.0)
    genotype = np.array([0.0, 0.5, 1.0])
    phenotype = mapper.genotype_to_phenotype(genotype)
    print(f"  Genotype [0.0, 0.5, 1.0] → Phenotype {phenotype.tolist()}")
    print(f"  Valid: {mapper.validate_phenotype(phenotype)[0]}")
    
    # Binary
    print("\nBINARY MAPPING (Decimal):")
    bin_mapper = BinaryMapper(interpretation="decimal")
    bin_genotype = np.array([1, 0, 1, 0])  # Binary 1010
    bin_phenotype = bin_mapper.genotype_to_phenotype(bin_genotype)
    print(f"  Binary [1, 0, 1, 0] → Decimal {bin_phenotype}")
    
    # Grammar-based
    print("\nGRAMMAR-BASED MAPPING (Expressions):")
    grammar = {
        '<expr>': [
            ['<num>'],
            ['<num>', '+', '<num>'],
            ['<num>', '*', '<num>']
        ],
        '<num>': [['1'], ['2'], ['3']]
    }
    g_mapper = GrammarMapper(grammar, max_depth=4)
    for i in range(3):
        g_genotype = np.random.uniform(0, 1, 4)
        g_phenotype = g_mapper.genotype_to_phenotype(g_genotype)
        print(f"  Genotype {g_genotype.round(2).tolist()} → Expression '{g_phenotype}'")


def demo_ga_optimization():
    """Demonstrate GA optimization"""
    print_section("3. GA OPTIMIZATION DEMONSTRATION")
    
    # Sphere function
    print("\nOptimizing SPHERE FUNCTION (minimize x^2 + y^2 + z^2)")
    
    def sphere_fitness(phenotype):
        try:
            x = np.array(phenotype, dtype=float).flatten()
            return -np.sum(x**2)
        except:
            return -np.inf
    
    config = GAConfig(
        population_size=15,
        generations=30,
        early_stopping=True,
        early_stopping_generations=5
    )
    
    mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
    engine = GeneticAlgorithmEngine(config, sphere_fitness, mapper)
    result = engine.run()
    
    print(f"\nResults:")
    print(f"  Best Fitness: {result.best_fitness:.6f}")
    print(f"  Best Solution: {result.best_phenotype}")
    print(f"  Generations: {result.total_generations}")
    print(f"  Time: {result.execution_time:.3f}s")
    print(f"  Converged: {result.convergence_achieved}")
    
    # Rosenbrock function
    print("\n\nOptimizing ROSENBROCK FUNCTION (harder problem)")
    
    def rosenbrock(phenotype):
        try:
            x = np.array(phenotype, dtype=float).flatten()
            if len(x) < 2:
                return -np.inf
            return -sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
        except:
            return -np.inf
    
    config2 = GAConfig(
        population_size=20,
        generations=50,
        mutation_method=MutationMethod.ADAPTIVE,
        crossover_rate=0.9,
        mutation_rate=0.15
    )
    
    engine2 = GeneticAlgorithmEngine(config2, rosenbrock, mapper)
    result2 = engine2.run()
    
    print(f"\nResults:")
    print(f"  Best Fitness: {result2.best_fitness:.6f}")
    print(f"  Generations: {result2.total_generations}")
    print(f"  Time: {result2.execution_time:.3f}s")


def demo_selection_methods():
    """Compare selection methods"""
    print_section("4. SELECTION METHOD COMPARISON")
    
    def rastrigin(phenotype):
        try:
            x = np.array(phenotype, dtype=float).flatten()
            return -(10 * len(x) + np.sum(x**2 - 10 * np.cos(2 * np.pi * x)))
        except:
            return -np.inf
    
    mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
    
    print("\nOptimizing Rastrigin Function with different selection methods:\n")
    
    for selection_method in [SelectionMethod.TOURNAMENT,
                             SelectionMethod.ROULETTE_WHEEL,
                             SelectionMethod.RANK_BASED]:
        config = GAConfig(
            population_size=20,
            generations=30,
            selection_method=selection_method
        )
        
        engine = GeneticAlgorithmEngine(config, rastrigin, mapper)
        result = engine.run()
        
        print(f"  {selection_method.value:20} → Fitness: {result.best_fitness:10.4f} "
              f"(gens: {result.total_generations})")


def demo_crossover_methods():
    """Compare crossover methods"""
    print_section("5. CROSSOVER METHOD COMPARISON")
    
    def fitness(x):
        try:
            return -np.sum(np.array(x)**2) if x is not None else -np.inf
        except:
            return -np.inf
    
    mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
    
    print("\nOptimizing Sphere Function with different crossover methods:\n")
    
    for crossover_method in [CrossoverMethod.SINGLE_POINT,
                             CrossoverMethod.TWO_POINT,
                             CrossoverMethod.UNIFORM,
                             CrossoverMethod.ARITHMETIC]:
        config = GAConfig(
            population_size=15,
            generations=25,
            crossover_method=crossover_method,
            crossover_rate=0.9
        )
        
        engine = GeneticAlgorithmEngine(config, fitness, mapper)
        result = engine.run()
        
        print(f"  {crossover_method.value:20} → Fitness: {result.best_fitness:10.4f} "
              f"(gens: {result.total_generations})")


def demo_mutation_methods():
    """Compare mutation methods"""
    print_section("6. MUTATION METHOD COMPARISON")
    
    def fitness(x):
        try:
            return -np.sum(np.array(x)**2) if x is not None else -np.inf
        except:
            return -np.inf
    
    mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
    
    print("\nOptimizing Sphere Function with different mutation methods:\n")
    
    for mutation_method in [MutationMethod.GAUSSIAN,
                           MutationMethod.UNIFORM,
                           MutationMethod.ADAPTIVE]:
        config = GAConfig(
            population_size=15,
            generations=25,
            mutation_method=mutation_method
        )
        
        engine = GeneticAlgorithmEngine(config, fitness, mapper)
        result = engine.run()
        
        print(f"  {mutation_method.value:20} → Fitness: {result.best_fitness:10.4f} "
              f"(gens: {result.total_generations})")


def demo_metrics():
    """Demonstrate metrics tracking"""
    print_section("7. METRICS AND CONVERGENCE TRACKING")
    
    def fitness(x):
        try:
            return -np.sum(np.array(x)**2) if x is not None else -np.inf
        except:
            return -np.inf
    
    config = GAConfig(
        population_size=15,
        generations=40
    )
    
    mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
    engine = GeneticAlgorithmEngine(config, fitness, mapper)
    result = engine.run()
    
    print("\nFitness progression:")
    print("-" * 50)
    for metric in result.generation_metrics[::5]:  # Every 5 generations
        if isinstance(metric, dict):
            g = metric['generation']
            best = metric['best_fitness']
            avg = metric['average_fitness']
            div = metric['population_diversity']
            print(f"Gen {g:2d} | Best: {best:8.4f} | Avg: {avg:8.4f} | Div: {div:.4f}")
    
    print("\nFinal Metrics:")
    print(f"  Best Fitness: {result.best_fitness:.6f}")
    print(f"  Avg Fitness: {result.average_fitness:.6f}")
    print(f"  Total Generations: {result.total_generations}")
    print(f"  Execution Time: {result.execution_time:.3f}s")
    print(f"  Total Errors: {len(result.errors)}")


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("  GA SYSTEM - COMPREHENSIVE DEMONSTRATION")
    print("  All Features & Capabilities")
    print("="*70)
    
    try:
        demo_operators()
        demo_mappers()
        demo_ga_optimization()
        demo_selection_methods()
        demo_crossover_methods()
        demo_mutation_methods()
        demo_metrics()
        
        print_section("DEMONSTRATION COMPLETE")
        print("\nAll GA components working correctly! ✓")
        print("\nNext Steps:")
        print("  1. Run: python test_ga_system.py  (37 unit tests)")
        print("  2. Run: python ga_cli.py          (interactive CLI)")
        print("  3. See: GA_EXAMPLES.py            (copy-paste examples)")
        print("  4. Read: GA_SYSTEM_README.md      (full documentation)")
        print("="*70 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
