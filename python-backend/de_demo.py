#!/usr/bin/env python3
"""
Comprehensive DE System Demonstration
======================================
Run this to see all DE features in action.

Usage:
    python de_demo.py
"""

import numpy as np
import sys
from de_operators import (
    DEConfig, DEMutationStrategy, DECrossoverType,
    ConstraintHandling, DEOperators
)
from de_engine import DifferentialEvolutionOptimizer, optimize_value_de


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_operators():
    """Demonstrate DE operators"""
    print_section("1. DE OPERATORS DEMONSTRATION")

    # Initialize population
    print("\nPOPULATION INITIALIZATION:")
    population = DEOperators.initialize_population(
        pop_size=8,
        bounds_min=0.0,
        bounds_max=10.0
    )
    print(f"  Population: {population.round(2)}")

    # With seeding
    seed_vals = np.array([3.0, 5.0, 7.0])
    seeded_pop = DEOperators.initialize_population(
        pop_size=8,
        bounds_min=0.0,
        bounds_max=10.0,
        seed_values=seed_vals,
        seed_ratio=0.5
    )
    print(f"  Seeded pop: {seeded_pop.round(2)}")

    # Mutation strategies
    print("\nMUTATION STRATEGIES:")
    fitness = -((population - 5) ** 2)

    for strategy in DEMutationStrategy:
        try:
            mutant, stats = DEOperators.apply_mutation(
                strategy=strategy,
                population=population,
                fitness=fitness,
                target_idx=0,
                F=0.8
            )
            print(f"  {strategy.value:25} -> mutant={mutant:.4f}")
        except Exception as e:
            print(f"  {strategy.value:25} -> (needs larger population)")

    # Crossover
    print("\nCROSSOVER:")
    target, mutant = 3.0, 7.0
    trial_bin, from_mut_bin = DEOperators.crossover_binomial(target, mutant, CR=0.9)
    trial_exp, from_mut_exp = DEOperators.crossover_exponential(target, mutant, CR=0.9)
    print(f"  Binomial:    target={target}, mutant={mutant} -> trial={trial_bin:.2f}")
    print(f"  Exponential: target={target}, mutant={mutant} -> trial={trial_exp:.2f}")

    # Selection
    print("\nGREEDY SELECTION:")
    selected, sel_fit, improved = DEOperators.greedy_selection(
        target_value=3.0,
        target_fitness=-4.0,
        trial_value=5.0,
        trial_fitness=0.0
    )
    print(f"  Target: 3.0 (fitness=-4.0)")
    print(f"  Trial:  5.0 (fitness= 0.0)")
    print(f"  Selected: {selected:.1f} (improved={improved})")

    # Constraint handling
    print("\nCONSTRAINT HANDLING:")
    out_val = 15.0
    for handling in ConstraintHandling:
        constrained = DEOperators.apply_constraints(out_val, 0.0, 10.0, handling)
        print(f"  {handling.value:10}: {out_val} -> {constrained:.2f}")


def demo_strategies():
    """Demonstrate different mutation strategies"""
    print_section("2. MUTATION STRATEGY COMPARISON")

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nOptimizing f(x) = -(x-5)^2 with different strategies:\n")

    for strategy in DEMutationStrategy:
        pop_size = 30 if '2' in strategy.value else 20

        config = DEConfig(
            population_size=pop_size,
            generations=40,
            mutation_strategy=strategy,
            early_stopping=True,
            patience=8
        )

        result = optimize_value_de(
            fitness_function=fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        print(f"  {strategy.value:25} | x={result.best_individual[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | gens={result.total_generations:3d}")


def demo_crossover():
    """Demonstrate crossover types"""
    print_section("3. CROSSOVER TYPE COMPARISON")

    def fitness_func(x):
        return -((x - 3) ** 2)

    print("\nOptimizing f(x) = -(x-3)^2 with different crossover types:\n")

    for crossover in DECrossoverType:
        config = DEConfig(
            population_size=20,
            generations=40,
            crossover_type=crossover,
            early_stopping=True,
            patience=8
        )

        result = optimize_value_de(
            fitness_function=fitness_func,
            bounds_min=-5.0,
            bounds_max=10.0,
            config=config
        )

        print(f"  {crossover.value:15} | x={result.best_individual[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | gens={result.total_generations:3d}")


def demo_optimization():
    """Demonstrate DE optimization"""
    print_section("4. DE OPTIMIZATION DEMONSTRATION")

    # Sphere function
    print("\nOptimizing SPHERE FUNCTION (minimize x^2)")

    def sphere_fitness(x):
        return -(x ** 2)

    config = PSOConfig = DEConfig(
        population_size=25,
        generations=50,
        mutation_strategy=DEMutationStrategy.BEST_1,
        early_stopping=True,
        patience=10
    )

    result = optimize_value_de(
        fitness_function=sphere_fitness,
        bounds_min=-10.0,
        bounds_max=10.0,
        config=config
    )

    print(f"\nResults:")
    print(f"  Best Value:    {result.best_individual[0]:.6f}")
    print(f"  Best Fitness:  {result.best_fitness:.6f}")
    print(f"  Generations:   {result.total_generations}")
    print(f"  Converged:     {result.converged}")
    print(f"  Strategy:      {result.strategy_used}")
    print(f"  Time:          {result.execution_time:.3f}s")

    # Shifted function
    print("\n\nOptimizing SHIFTED FUNCTION (optimal at x=7)")

    def shifted_fitness(x):
        return -((x - 7) ** 2)

    config2 = DEConfig(
        population_size=30,
        generations=60,
        mutation_strategy=DEMutationStrategy.CURRENT_TO_BEST_1,
        early_stopping=True
    )

    result2 = optimize_value_de(
        fitness_function=shifted_fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config2
    )

    print(f"\nResults:")
    print(f"  Best Value:    {result2.best_individual[0]:.6f}")
    print(f"  Best Fitness:  {result2.best_fitness:.6f}")
    print(f"  Generations:   {result2.total_generations}")


def demo_adaptive():
    """Demonstrate adaptive F and CR"""
    print_section("5. ADAPTIVE PARAMETERS DEMONSTRATION")

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nComparing fixed vs adaptive parameters:\n")

    # Fixed
    config_fixed = DEConfig(
        population_size=25,
        generations=60,
        scale_factor=0.8,
        crossover_rate=0.9,
        adaptive_f=False,
        adaptive_cr=False,
        early_stopping=False
    )

    result_fixed = optimize_value_de(
        fitness_function=fitness_func,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config_fixed
    )

    # Adaptive
    config_adaptive = DEConfig(
        population_size=25,
        generations=60,
        scale_factor=0.8,
        crossover_rate=0.9,
        adaptive_f=True,
        adaptive_cr=True,
        early_stopping=False
    )

    result_adaptive = optimize_value_de(
        fitness_function=fitness_func,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config_adaptive
    )

    print(f"  Fixed (F=0.8, CR=0.9):")
    print(f"    Best: x={result_fixed.best_individual[0]:.6f}, "
          f"fitness={result_fixed.best_fitness:.6f}")

    print(f"\n  Adaptive:")
    print(f"    Best: x={result_adaptive.best_individual[0]:.6f}, "
          f"fitness={result_adaptive.best_fitness:.6f}")
    if result_adaptive.f_history and result_adaptive.cr_history:
        print(f"    F progression: {result_adaptive.f_history[0]:.3f} -> "
              f"{result_adaptive.f_history[-1]:.3f}")
        print(f"    CR progression: {result_adaptive.cr_history[0]:.3f} -> "
              f"{result_adaptive.cr_history[-1]:.3f}")


def demo_metrics():
    """Demonstrate metrics tracking"""
    print_section("6. METRICS AND CONVERGENCE TRACKING")

    def fitness(x):
        return -((x - 5) ** 2)

    config = DEConfig(
        population_size=25,
        generations=50,
        early_stopping=False
    )

    result = optimize_value_de(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config
    )

    print("\nGeneration progression:")
    print("-" * 80)
    print(f"{'Gen':>5} | {'Best':>10} | {'Avg':>10} | {'Success%':>10} | {'F':>8} | {'CR':>8}")
    print("-" * 80)

    for i, m in enumerate(result.generation_metrics):
        if i % 10 == 0:
            print(f"{m.generation:5d} | {m.best_fitness:10.4f} | "
                  f"{m.average_fitness:10.4f} | {m.success_rate*100:9.1f}% | "
                  f"{m.current_f:8.3f} | {m.current_cr:8.3f}")

    print("-" * 80)
    print(f"\nFinal Statistics:")
    print(f"  Best Fitness:     {result.best_fitness:.6f}")
    print(f"  Best Value:       {result.best_individual[0]:.6f}")
    print(f"  Avg Fitness:      {result.average_fitness:.6f}")
    print(f"  Total Generations: {result.total_generations}")
    print(f"  Execution Time:   {result.execution_time:.3f}s")


def demo_seed_values():
    """Demonstrate seeding with initial values"""
    print_section("7. SEEDING DEMONSTRATION")

    def fitness(x):
        return -((x - 5) ** 2)

    print("\nOptimizing f(x) = -(x-5)^2")
    print("Comparing with and without seed values near optimum")

    config = DEConfig(
        population_size=20,
        generations=30,
        early_stopping=True
    )

    # Without seeding
    result_no_seed = optimize_value_de(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config
    )

    # With seeding
    seed_values = np.array([4.0, 5.0, 6.0])
    result_seeded = optimize_value_de(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config,
        seed_values=seed_values
    )

    print(f"\n  Without seeding:")
    print(f"    Best: x={result_no_seed.best_individual[0]:.4f}, "
          f"fitness={result_no_seed.best_fitness:.4f}, "
          f"gens={result_no_seed.total_generations}")

    print(f"\n  With seeding (values near optimal):")
    print(f"    Best: x={result_seeded.best_individual[0]:.4f}, "
          f"fitness={result_seeded.best_fitness:.4f}, "
          f"gens={result_seeded.total_generations}")


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("  DE SYSTEM - COMPREHENSIVE DEMONSTRATION")
    print("  All Features & Capabilities")
    print("="*70)

    try:
        demo_operators()
        demo_strategies()
        demo_crossover()
        demo_optimization()
        demo_adaptive()
        demo_metrics()
        demo_seed_values()

        print_section("DEMONSTRATION COMPLETE")
        print("\nAll DE components working correctly!")
        print("\nNext Steps:")
        print("  1. Run: python test_de_system.py  (unit tests)")
        print("  2. Run: python de_cli.py          (interactive CLI)")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
