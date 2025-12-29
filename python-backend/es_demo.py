#!/usr/bin/env python3
"""
Comprehensive ES System Demonstration
======================================
Run this to see all ES features in action.

Usage:
    python es_demo.py
"""

import numpy as np
import sys
from es_operators import (
    ESConfig, ESSelectionType, ESRecombinationType,
    ConstraintHandling, ESOperators
)
from es_engine import EvolutionStrategyOptimizer, optimize_value_es


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_operators():
    """Demonstrate ES operators"""
    print_section("1. ES OPERATORS DEMONSTRATION")

    # Initialize population
    print("\nPOPULATION INITIALIZATION:")
    population, sigmas = ESOperators.initialize_population(
        mu=6,
        bounds_min=0.0,
        bounds_max=10.0,
        initial_sigma=0.3
    )
    print(f"  Population: {population.round(2)}")
    print(f"  Sigmas: {sigmas.round(3)}")

    # With seeding
    seed_vals = np.array([4.0, 5.0, 6.0])
    seeded_pop, seeded_sig = ESOperators.initialize_population(
        mu=6,
        bounds_min=0.0,
        bounds_max=10.0,
        initial_sigma=0.3,
        seed_values=seed_vals,
        seed_ratio=0.5
    )
    print(f"  Seeded pop: {seeded_pop.round(2)}")

    # Recombination
    print("\nRECOMBINATION TYPES:")
    fitness = -((population - 5) ** 2)

    for recomb_type in ESRecombinationType:
        value, sigma, stats = ESOperators.apply_recombination(
            recomb_type=recomb_type,
            population=population,
            sigmas=sigmas,
            fitness=fitness,
            rho=2
        )
        print(f"  {recomb_type.value:15}: value={value:.4f}, sigma={sigma:.4f}")

    # Mutation
    print("\nMUTATION (Self-Adaptive):")
    config = ESConfig(self_adaptive=True, initial_sigma=0.3)

    print("  Starting: value=5.0, sigma=0.3")
    for i in range(4):
        new_val, new_sigma, stats = ESOperators.apply_mutation(
            value=5.0,
            sigma=0.3,
            config=config,
            bounds_min=0.0,
            bounds_max=10.0
        )
        print(f"  Trial {i+1}: value={new_val:.4f}, sigma={new_sigma:.4f}")

    # Selection
    print("\nSELECTION TYPES:")
    offspring = np.array([4.0, 4.5, 5.0, 5.5, 6.0, 4.2, 5.8, 3.5, 6.2, 4.8])
    offspring_sigmas = np.full(10, 0.25)
    offspring_fitness = -((offspring - 5) ** 2)

    for sel_type in ESSelectionType:
        sel_pop, sel_sig, sel_fit, stats = ESOperators.apply_selection(
            selection_type=sel_type,
            parents=population,
            parent_sigmas=sigmas,
            parent_fitness=fitness,
            offspring=offspring,
            offspring_sigmas=offspring_sigmas,
            offspring_fitness=offspring_fitness,
            mu=4
        )
        print(f"  {sel_type.value:5}: selected={sel_pop.round(2)}, "
              f"offspring_sel={stats['offspring_selected']}")


def demo_selection_types():
    """Demonstrate selection types"""
    print_section("2. SELECTION TYPE COMPARISON")

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nOptimizing f(x) = -(x-5)^2 with different selection types:\n")

    for selection in ESSelectionType:
        config = ESConfig(
            mu=15,
            lambda_=100,
            generations=40,
            selection_type=selection,
            early_stopping=True,
            patience=8
        )

        result = optimize_value_es(
            fitness_function=fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        sel_name = f"(mu{'+' if selection == ESSelectionType.PLUS else ','}lambda)"
        print(f"  {sel_name:12} | x={result.best_individual[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | gens={result.total_generations:3d} | "
              f"sigma={result.best_sigma:.4f}")


def demo_recombination_types():
    """Demonstrate recombination types"""
    print_section("3. RECOMBINATION TYPE COMPARISON")

    def fitness_func(x):
        return -((x - 3) ** 2)

    print("\nOptimizing f(x) = -(x-3)^2 with different recombination types:\n")

    for recomb in ESRecombinationType:
        config = ESConfig(
            mu=15,
            lambda_=100,
            generations=40,
            recombination_type=recomb,
            early_stopping=True,
            patience=8
        )

        result = optimize_value_es(
            fitness_function=fitness_func,
            bounds_min=-5.0,
            bounds_max=10.0,
            config=config
        )

        print(f"  {recomb.value:15} | x={result.best_individual[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | gens={result.total_generations:3d}")


def demo_optimization():
    """Demonstrate ES optimization"""
    print_section("4. ES OPTIMIZATION DEMONSTRATION")

    # Sphere function
    print("\nOptimizing SPHERE FUNCTION (minimize x^2)")

    def sphere_fitness(x):
        return -(x ** 2)

    config = ESConfig(
        mu=20,
        lambda_=140,
        generations=50,
        selection_type=ESSelectionType.PLUS,
        self_adaptive=True,
        early_stopping=True,
        patience=10
    )

    result = optimize_value_es(
        fitness_function=sphere_fitness,
        bounds_min=-10.0,
        bounds_max=10.0,
        config=config
    )

    print(f"\nResults:")
    print(f"  Best Value:     {result.best_individual[0]:.6f}")
    print(f"  Best Fitness:   {result.best_fitness:.6f}")
    print(f"  Best Sigma:     {result.best_sigma:.6f}")
    print(f"  Generations:    {result.total_generations}")
    print(f"  Converged:      {result.converged}")
    print(f"  Selection:      {result.selection_type_used}")
    print(f"  Recombination:  {result.recombination_type_used}")
    print(f"  Time:           {result.execution_time:.3f}s")

    # Shifted function
    print("\n\nOptimizing SHIFTED FUNCTION (optimal at x=7)")

    def shifted_fitness(x):
        return -((x - 7) ** 2)

    config2 = ESConfig(
        mu=15,
        lambda_=100,
        generations=60,
        selection_type=ESSelectionType.COMMA,
        self_adaptive=True,
        early_stopping=True
    )

    result2 = optimize_value_es(
        fitness_function=shifted_fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config2
    )

    print(f"\nResults:")
    print(f"  Best Value:     {result2.best_individual[0]:.6f}")
    print(f"  Best Fitness:   {result2.best_fitness:.6f}")
    print(f"  Best Sigma:     {result2.best_sigma:.6f}")
    print(f"  Generations:    {result2.total_generations}")


def demo_self_adaptive():
    """Demonstrate self-adaptive mutation"""
    print_section("5. SELF-ADAPTIVE MUTATION DEMONSTRATION")

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nComparing fixed vs self-adaptive step sizes:\n")

    # Fixed sigma
    config_fixed = ESConfig(
        mu=15,
        lambda_=100,
        generations=60,
        self_adaptive=False,
        initial_sigma=0.5,
        early_stopping=False
    )

    result_fixed = optimize_value_es(
        fitness_function=fitness_func,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config_fixed
    )

    # Self-adaptive sigma
    config_adaptive = ESConfig(
        mu=15,
        lambda_=100,
        generations=60,
        self_adaptive=True,
        initial_sigma=0.5,
        early_stopping=False
    )

    result_adaptive = optimize_value_es(
        fitness_function=fitness_func,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config_adaptive
    )

    print(f"  Fixed (sigma=0.5):")
    print(f"    Best: x={result_fixed.best_individual[0]:.6f}, "
          f"fitness={result_fixed.best_fitness:.6f}")
    print(f"    Final sigma: {result_fixed.best_sigma:.6f}")

    print(f"\n  Self-Adaptive:")
    print(f"    Best: x={result_adaptive.best_individual[0]:.6f}, "
          f"fitness={result_adaptive.best_fitness:.6f}")
    print(f"    Final sigma: {result_adaptive.best_sigma:.6f}")

    if result_adaptive.sigma_history:
        print(f"\n  Sigma progression (self-adaptive):")
        for i in [0, len(result_adaptive.sigma_history)//4,
                  len(result_adaptive.sigma_history)//2,
                  3*len(result_adaptive.sigma_history)//4,
                  len(result_adaptive.sigma_history)-1]:
            print(f"    Gen {i:3d}: sigma={result_adaptive.sigma_history[i]:.6f}")


def demo_metrics():
    """Demonstrate metrics tracking"""
    print_section("6. METRICS AND CONVERGENCE TRACKING")

    def fitness(x):
        return -((x - 5) ** 2)

    config = ESConfig(
        mu=15,
        lambda_=100,
        generations=50,
        self_adaptive=True,
        early_stopping=False
    )

    result = optimize_value_es(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config
    )

    print("\nGeneration progression:")
    print("-" * 80)
    print(f"{'Gen':>5} | {'Best':>10} | {'Avg':>10} | {'Sigma':>10} | {'Diversity':>10}")
    print("-" * 80)

    for i, m in enumerate(result.generation_metrics):
        if i % 10 == 0:
            print(f"{m.generation:5d} | {m.best_fitness:10.4f} | "
                  f"{m.average_fitness:10.4f} | {m.average_sigma:10.4f} | "
                  f"{m.population_diversity:10.4f}")

    print("-" * 80)
    print(f"\nFinal Statistics:")
    print(f"  Best Fitness:     {result.best_fitness:.6f}")
    print(f"  Best Value:       {result.best_individual[0]:.6f}")
    print(f"  Best Sigma:       {result.best_sigma:.6f}")
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

    config = ESConfig(
        mu=15,
        lambda_=100,
        generations=30,
        early_stopping=True
    )

    # Without seeding
    result_no_seed = optimize_value_es(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config
    )

    # With seeding
    seed_values = np.array([4.0, 5.0, 6.0])
    result_seeded = optimize_value_es(
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
    print("  ES SYSTEM - COMPREHENSIVE DEMONSTRATION")
    print("  All Features & Capabilities")
    print("="*70)

    try:
        demo_operators()
        demo_selection_types()
        demo_recombination_types()
        demo_optimization()
        demo_self_adaptive()
        demo_metrics()
        demo_seed_values()

        print_section("DEMONSTRATION COMPLETE")
        print("\nAll ES components working correctly!")
        print("\nNext Steps:")
        print("  1. Run: python test_es_system.py  (unit tests)")
        print("  2. Run: python es_cli.py          (interactive CLI)")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
