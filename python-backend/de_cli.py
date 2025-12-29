#!/usr/bin/env python3
"""
DE (Differential Evolution) Interactive CLI
============================================
Run this for interactive testing and exploration of DE features.

Usage:
    python de_cli.py
"""

import numpy as np
import sys
import logging

from de_operators import (
    DEConfig, DEMutationStrategy, DECrossoverType, ConstraintHandling
)
from de_engine import DifferentialEvolutionOptimizer, optimize_value_de

# Configure logging
logging.basicConfig(level=logging.WARNING)


def clear_screen():
    """Clear console screen"""
    print("\033[H\033[J", end="")


def print_header():
    """Print CLI header"""
    print("\n" + "="*60)
    print("  DE (Differential Evolution) Interactive CLI")
    print("="*60)


def print_menu():
    """Print main menu"""
    print("\n--- Main Menu ---")
    print("1. Quick optimization demo")
    print("2. Test DE operators")
    print("3. Configure and run DE")
    print("4. Compare mutation strategies")
    print("5. Test adaptive parameters")
    print("6. View documentation")
    print("7. Exit")
    print("-" * 30)


def get_user_choice(prompt: str, valid_options: list) -> str:
    """Get validated user input"""
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"Invalid choice. Please enter one of: {valid_options}")


def demo_quick_optimization():
    """Quick demonstration of DE optimization"""
    print("\n" + "="*50)
    print("  QUICK DE OPTIMIZATION DEMO")
    print("="*50)

    # Simple fitness function
    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nOptimizing function: f(x) = -(x-5)^2")
    print("Optimal solution: x = 5, f(x) = 0")
    print("Bounds: [0, 10]")

    config = DEConfig(
        population_size=20,
        generations=50,
        early_stopping=True,
        patience=10
    )

    result = optimize_value_de(
        fitness_function=fitness_func,
        bounds_min=0.0,
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

    input("\nPress Enter to continue...")


def demo_operators():
    """Demonstrate DE operators"""
    print("\n" + "="*50)
    print("  DE OPERATORS DEMONSTRATION")
    print("="*50)

    from de_operators import DEOperators

    print("\n1. Population Initialization:")
    population = DEOperators.initialize_population(
        pop_size=6,
        bounds_min=0.0,
        bounds_max=10.0
    )
    print(f"   Population: {population.round(2)}")

    # With seeding
    seed_vals = np.array([3.0, 5.0, 7.0])
    seeded_pop = DEOperators.initialize_population(
        pop_size=6,
        bounds_min=0.0,
        bounds_max=10.0,
        seed_values=seed_vals,
        seed_ratio=0.5
    )
    print(f"   Seeded: {seeded_pop.round(2)}")

    print("\n2. Mutation Strategies:")
    fitness = np.array([-((p - 5)**2) for p in population])

    for strategy in DEMutationStrategy:
        try:
            mutant, stats = DEOperators.apply_mutation(
                strategy=strategy,
                population=population,
                fitness=fitness,
                target_idx=0,
                F=0.8
            )
            print(f"   {strategy.value:25}: mutant={mutant:.2f}")
        except Exception as e:
            print(f"   {strategy.value:25}: (requires more population)")

    print("\n3. Crossover:")
    target = 3.0
    mutant = 7.0
    trial_bin, from_mut = DEOperators.crossover_binomial(target, mutant, CR=0.9)
    print(f"   Binomial: target={target}, mutant={mutant} -> trial={trial_bin:.2f}")

    print("\n4. Greedy Selection:")
    selected, sel_fit, improved = DEOperators.greedy_selection(
        target_value=3.0,
        target_fitness=-4.0,
        trial_value=5.0,
        trial_fitness=0.0
    )
    print(f"   Selected: {selected:.2f} (fitness={sel_fit:.2f}, improved={improved})")

    print("\n5. Constraint Handling:")
    out_of_bounds = 15.0
    clamped = DEOperators.apply_constraints(out_of_bounds, 0.0, 10.0, ConstraintHandling.CLAMP)
    print(f"   Clamp: {out_of_bounds} -> {clamped}")

    input("\nPress Enter to continue...")


def configure_and_run():
    """Configure and run custom DE"""
    print("\n" + "="*50)
    print("  CONFIGURE AND RUN DE")
    print("="*50)

    # Get configuration
    print("\nMutation Strategy options:")
    strategies = list(DEMutationStrategy)
    for i, s in enumerate(strategies, 1):
        print(f"  {i}. {s.value}")
    strat_choice = get_user_choice(f"Select strategy (1-{len(strategies)}): ",
                                   [str(i) for i in range(1, len(strategies)+1)])
    strategy = strategies[int(strat_choice) - 1]

    print("\nCrossover options:")
    print("  1. Binomial")
    print("  2. Exponential")
    cross_choice = get_user_choice("Select crossover (1-2): ", ['1', '2'])
    crossover = DECrossoverType.BINOMIAL if cross_choice == '1' else DECrossoverType.EXPONENTIAL

    try:
        pop_size = int(input("Population size (default 30): ") or "30")
        generations = int(input("Max generations (default 100): ") or "100")
        F = float(input("Scale factor F (default 0.8): ") or "0.8")
        CR = float(input("Crossover rate CR (default 0.9): ") or "0.9")
    except ValueError:
        pop_size, generations, F, CR = 30, 100, 0.8, 0.9

    # Test functions
    print("\nTest functions:")
    print("  1. Sphere: f(x) = -x^2")
    print("  2. Shifted: f(x) = -(x-5)^2")
    print("  3. Rastrigin-like: f(x) = -(x^2 - cos(2*pi*x))")
    func_choice = get_user_choice("Select function (1-3): ", ['1', '2', '3'])

    if func_choice == '1':
        fitness_func = lambda x: -(x ** 2)
        bounds = (-10.0, 10.0)
    elif func_choice == '2':
        fitness_func = lambda x: -((x - 5) ** 2)
        bounds = (0.0, 10.0)
    else:
        fitness_func = lambda x: -(x**2 - np.cos(2 * np.pi * x))
        bounds = (-5.0, 5.0)

    config = DEConfig(
        population_size=pop_size,
        generations=generations,
        scale_factor=F,
        crossover_rate=CR,
        mutation_strategy=strategy,
        crossover_type=crossover,
        early_stopping=True
    )

    print(f"\nRunning DE with {config}...")

    result = optimize_value_de(
        fitness_function=fitness_func,
        bounds_min=bounds[0],
        bounds_max=bounds[1],
        config=config
    )

    print(f"\nResults:")
    print(f"  Best Value:     {result.best_individual[0]:.6f}")
    print(f"  Best Fitness:   {result.best_fitness:.6f}")
    print(f"  Generations:    {result.total_generations}")
    print(f"  Converged:      {result.converged}")
    print(f"  Final F:        {result.f_history[-1]:.3f}" if result.f_history else "")
    print(f"  Final CR:       {result.cr_history[-1]:.3f}" if result.cr_history else "")
    print(f"  Time:           {result.execution_time:.3f}s")

    input("\nPress Enter to continue...")


def compare_strategies():
    """Compare different mutation strategies"""
    print("\n" + "="*50)
    print("  MUTATION STRATEGY COMPARISON")
    print("="*50)

    def fitness_func(x):
        return -((x - 3) ** 2)

    print("\nOptimizing f(x) = -(x-3)^2 with different strategies:")
    print("-" * 70)

    for strategy in DEMutationStrategy:
        # Some strategies require larger population
        pop_size = 30 if 'rand/2' in strategy.value or 'best/2' in strategy.value else 20

        config = DEConfig(
            population_size=pop_size,
            generations=50,
            mutation_strategy=strategy,
            early_stopping=True,
            patience=10
        )

        result = optimize_value_de(
            fitness_function=fitness_func,
            bounds_min=-10.0,
            bounds_max=10.0,
            config=config
        )

        print(f"{strategy.value:25} | x={result.best_individual[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | gens={result.total_generations:3d}")

    input("\nPress Enter to continue...")


def test_adaptive():
    """Test adaptive F and CR"""
    print("\n" + "="*50)
    print("  ADAPTIVE PARAMETERS DEMONSTRATION")
    print("="*50)

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nComparing fixed vs adaptive F and CR:")
    print("-" * 60)

    # Fixed parameters
    config_fixed = DEConfig(
        population_size=25,
        generations=60,
        scale_factor=0.8,
        crossover_rate=0.9,
        adaptive_f=False,
        adaptive_cr=False,
        early_stopping=True
    )

    result_fixed = optimize_value_de(
        fitness_function=fitness_func,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config_fixed
    )

    # Adaptive parameters
    config_adaptive = DEConfig(
        population_size=25,
        generations=60,
        scale_factor=0.8,
        crossover_rate=0.9,
        adaptive_f=True,
        adaptive_cr=True,
        early_stopping=True
    )

    result_adaptive = optimize_value_de(
        fitness_function=fitness_func,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config_adaptive
    )

    print(f"\nFixed (F=0.8, CR=0.9):")
    print(f"  Best: x={result_fixed.best_individual[0]:.4f}, "
          f"fitness={result_fixed.best_fitness:.4f}, gens={result_fixed.total_generations}")

    print(f"\nAdaptive:")
    print(f"  Best: x={result_adaptive.best_individual[0]:.4f}, "
          f"fitness={result_adaptive.best_fitness:.4f}, gens={result_adaptive.total_generations}")
    if result_adaptive.f_history and result_adaptive.cr_history:
        print(f"  Final F: {result_adaptive.f_history[-1]:.3f}")
        print(f"  Final CR: {result_adaptive.cr_history[-1]:.3f}")

    input("\nPress Enter to continue...")


def view_documentation():
    """View DE documentation"""
    print("\n" + "="*50)
    print("  DE DOCUMENTATION")
    print("="*50)

    print("""
DE (Differential Evolution)
===========================

Key Concepts:
- Population-based optimization
- Uses difference vectors for mutation
- Greedy selection between parent and trial

Mutation Strategies:
- DE/rand/1:  v = x_r1 + F*(x_r2 - x_r3)
- DE/rand/2:  v = x_r1 + F*(x_r2 - x_r3) + F*(x_r4 - x_r5)
- DE/best/1:  v = x_best + F*(x_r1 - x_r2)
- DE/best/2:  v = x_best + F*(x_r1 - x_r2) + F*(x_r3 - x_r4)
- DE/current-to-best/1: v = x_i + F*(x_best - x_i) + F*(x_r1 - x_r2)
- DE/current-to-rand/1: v = x_i + F*(x_r1 - x_i) + F*(x_r2 - x_r3)

Crossover Types:
- Binomial: Each dimension has independent CR probability
- Exponential: Contiguous dimensions from mutant

Key Parameters:
- F (scale factor): Controls step size (typically 0.4-1.0)
- CR (crossover rate): How much from mutant (0.0-1.0)
- population_size: Number of individuals (typically 10*D)

Adaptive DE:
- F adapts based on success rate
- CR adapts based on success rate
- Helps balance exploration/exploitation

Usage Example:
  from de_engine import optimize_value_de
  from de_operators import DEConfig, DEMutationStrategy

  config = DEConfig(
      population_size=30,
      generations=100,
      mutation_strategy=DEMutationStrategy.BEST_1
  )
  result = optimize_value_de(
      fitness_function=lambda x: -(x**2),
      bounds_min=-10.0,
      bounds_max=10.0,
      config=config
  )
  print(f"Best: {result.best_individual}")
""")

    input("\nPress Enter to continue...")


def main():
    """Main CLI loop"""
    while True:
        clear_screen()
        print_header()
        print_menu()

        choice = get_user_choice("Enter choice (1-7): ",
                                ['1', '2', '3', '4', '5', '6', '7'])

        if choice == '1':
            demo_quick_optimization()
        elif choice == '2':
            demo_operators()
        elif choice == '3':
            configure_and_run()
        elif choice == '4':
            compare_strategies()
        elif choice == '5':
            test_adaptive()
        elif choice == '6':
            view_documentation()
        elif choice == '7':
            print("\nExiting DE CLI. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
