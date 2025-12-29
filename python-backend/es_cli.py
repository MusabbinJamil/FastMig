#!/usr/bin/env python3
"""
ES (Evolution Strategy) Interactive CLI
========================================
Run this for interactive testing and exploration of ES features.

Usage:
    python es_cli.py
"""

import numpy as np
import sys
import logging

from es_operators import (
    ESConfig, ESSelectionType, ESRecombinationType, ConstraintHandling
)
from es_engine import EvolutionStrategyOptimizer, optimize_value_es

# Configure logging
logging.basicConfig(level=logging.WARNING)


def clear_screen():
    """Clear console screen"""
    print("\033[H\033[J", end="")


def print_header():
    """Print CLI header"""
    print("\n" + "="*60)
    print("  ES (Evolution Strategy) Interactive CLI")
    print("="*60)


def print_menu():
    """Print main menu"""
    print("\n--- Main Menu ---")
    print("1. Quick optimization demo")
    print("2. Test ES operators")
    print("3. Configure and run ES")
    print("4. Compare selection types")
    print("5. Compare recombination types")
    print("6. Test self-adaptive mutation")
    print("7. View documentation")
    print("8. Exit")
    print("-" * 30)


def get_user_choice(prompt: str, valid_options: list) -> str:
    """Get validated user input"""
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"Invalid choice. Please enter one of: {valid_options}")


def demo_quick_optimization():
    """Quick demonstration of ES optimization"""
    print("\n" + "="*50)
    print("  QUICK ES OPTIMIZATION DEMO")
    print("="*50)

    # Simple fitness function
    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nOptimizing function: f(x) = -(x-5)^2")
    print("Optimal solution: x = 5, f(x) = 0")
    print("Bounds: [0, 10]")

    config = ESConfig(
        mu=15,
        lambda_=100,
        generations=50,
        self_adaptive=True,
        early_stopping=True,
        patience=10
    )

    result = optimize_value_es(
        fitness_function=fitness_func,
        bounds_min=0.0,
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

    input("\nPress Enter to continue...")


def demo_operators():
    """Demonstrate ES operators"""
    print("\n" + "="*50)
    print("  ES OPERATORS DEMONSTRATION")
    print("="*50)

    from es_operators import ESOperators

    print("\n1. Population Initialization:")
    population, sigmas = ESOperators.initialize_population(
        mu=5,
        bounds_min=0.0,
        bounds_max=10.0,
        initial_sigma=0.3
    )
    print(f"   Population: {population.round(2)}")
    print(f"   Sigmas: {sigmas.round(3)}")

    # Recombination
    print("\n2. Recombination:")
    fitness = -((population - 5) ** 2)

    for recomb_type in ESRecombinationType:
        value, sigma, stats = ESOperators.apply_recombination(
            recomb_type=recomb_type,
            population=population,
            sigmas=sigmas,
            fitness=fitness,
            rho=2
        )
        print(f"   {recomb_type.value:15}: value={value:.3f}, sigma={sigma:.3f}")

    # Mutation
    print("\n3. Self-Adaptive Mutation:")
    config = ESConfig(
        self_adaptive=True,
        initial_sigma=0.3,
        sigma_min=1e-6,
        sigma_max=1.0
    )

    for _ in range(3):
        new_val, new_sigma, stats = ESOperators.apply_mutation(
            value=5.0,
            sigma=0.3,
            config=config,
            bounds_min=0.0,
            bounds_max=10.0
        )
        print(f"   value=5.0, sigma=0.3 -> value={new_val:.3f}, sigma={new_sigma:.3f}")

    # Selection
    print("\n4. Selection:")
    offspring = np.array([4.0, 4.5, 5.0, 5.5, 6.0, 4.2, 5.8, 3.5])
    offspring_sigmas = np.full(8, 0.25)
    offspring_fitness = -((offspring - 5) ** 2)

    for sel_type in ESSelectionType:
        try:
            sel_pop, sel_sig, sel_fit, stats = ESOperators.apply_selection(
                selection_type=sel_type,
                parents=population,
                parent_sigmas=sigmas,
                parent_fitness=fitness,
                offspring=offspring,
                offspring_sigmas=offspring_sigmas,
                offspring_fitness=offspring_fitness,
                mu=3
            )
            print(f"   {sel_type.value:10}: selected={sel_pop.round(2)}")
        except Exception as e:
            print(f"   {sel_type.value:10}: {e}")

    input("\nPress Enter to continue...")


def configure_and_run():
    """Configure and run custom ES"""
    print("\n" + "="*50)
    print("  CONFIGURE AND RUN ES")
    print("="*50)

    # Get configuration
    print("\nSelection Type:")
    print("  1. (mu+lambda) Plus - parents and offspring compete")
    print("  2. (mu,lambda) Comma - only offspring compete")
    sel_choice = get_user_choice("Select type (1-2): ", ['1', '2'])
    selection = ESSelectionType.PLUS if sel_choice == '1' else ESSelectionType.COMMA

    print("\nRecombination Type:")
    for i, r in enumerate(ESRecombinationType, 1):
        print(f"  {i}. {r.value}")
    recomb_choice = get_user_choice("Select type (1-3): ", ['1', '2', '3'])
    recomb_types = list(ESRecombinationType)
    recombination = recomb_types[int(recomb_choice) - 1]

    try:
        mu = int(input("Parent population mu (default 15): ") or "15")
        lambda_ = int(input("Offspring population lambda (default 100): ") or "100")
        generations = int(input("Max generations (default 100): ") or "100")
    except ValueError:
        mu, lambda_, generations = 15, 100, 100

    self_adaptive = input("Self-adaptive mutation? (y/n, default y): ").lower() != 'n'

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

    config = ESConfig(
        mu=mu,
        lambda_=lambda_,
        generations=generations,
        selection_type=selection,
        recombination_type=recombination,
        self_adaptive=self_adaptive,
        early_stopping=True
    )

    print(f"\nRunning ES with {config}...")

    result = optimize_value_es(
        fitness_function=fitness_func,
        bounds_min=bounds[0],
        bounds_max=bounds[1],
        config=config
    )

    print(f"\nResults:")
    print(f"  Best Value:     {result.best_individual[0]:.6f}")
    print(f"  Best Fitness:   {result.best_fitness:.6f}")
    print(f"  Best Sigma:     {result.best_sigma:.6f}")
    print(f"  Generations:    {result.total_generations}")
    print(f"  Converged:      {result.converged}")
    print(f"  Time:           {result.execution_time:.3f}s")

    input("\nPress Enter to continue...")


def compare_selection():
    """Compare selection types"""
    print("\n" + "="*50)
    print("  SELECTION TYPE COMPARISON")
    print("="*50)

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nOptimizing f(x) = -(x-5)^2 with different selection types:")
    print("-" * 60)

    for selection in ESSelectionType:
        config = ESConfig(
            mu=15,
            lambda_=100,
            generations=50,
            selection_type=selection,
            early_stopping=True,
            patience=10
        )

        result = optimize_value_es(
            fitness_function=fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        print(f"  ({selection.value:5}) | x={result.best_individual[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | gens={result.total_generations:3d} | "
              f"sigma={result.best_sigma:.4f}")

    input("\nPress Enter to continue...")


def compare_recombination():
    """Compare recombination types"""
    print("\n" + "="*50)
    print("  RECOMBINATION TYPE COMPARISON")
    print("="*50)

    def fitness_func(x):
        return -((x - 3) ** 2)

    print("\nOptimizing f(x) = -(x-3)^2 with different recombination types:")
    print("-" * 70)

    for recomb in ESRecombinationType:
        config = ESConfig(
            mu=15,
            lambda_=100,
            generations=50,
            recombination_type=recomb,
            early_stopping=True,
            patience=10
        )

        result = optimize_value_es(
            fitness_function=fitness_func,
            bounds_min=-5.0,
            bounds_max=10.0,
            config=config
        )

        print(f"  {recomb.value:15} | x={result.best_individual[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | gens={result.total_generations:3d}")

    input("\nPress Enter to continue...")


def test_self_adaptive():
    """Test self-adaptive mutation"""
    print("\n" + "="*50)
    print("  SELF-ADAPTIVE MUTATION DEMONSTRATION")
    print("="*50)

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nComparing fixed vs self-adaptive mutation:")
    print("-" * 60)

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

    print(f"\n  Fixed (sigma=0.5):")
    print(f"    Best: x={result_fixed.best_individual[0]:.6f}, "
          f"fitness={result_fixed.best_fitness:.6f}")
    print(f"    Final sigma: {result_fixed.best_sigma:.6f}")

    print(f"\n  Self-Adaptive:")
    print(f"    Best: x={result_adaptive.best_individual[0]:.6f}, "
          f"fitness={result_adaptive.best_fitness:.6f}")
    print(f"    Final sigma: {result_adaptive.best_sigma:.6f}")

    if result_adaptive.sigma_history:
        print(f"    Sigma progression: {result_adaptive.sigma_history[0]:.4f} -> "
              f"{result_adaptive.sigma_history[-1]:.4f}")

    input("\nPress Enter to continue...")


def view_documentation():
    """View ES documentation"""
    print("\n" + "="*50)
    print("  ES DOCUMENTATION")
    print("="*50)

    print("""
ES (Evolution Strategy)
=======================

Key Concepts:
- (mu, lambda) or (mu+lambda) selection strategies
- Self-adaptive step sizes (sigma)
- Recombination to create offspring
- Gaussian mutation with adapted step sizes

Selection Types:
- (mu+lambda) Plus: Parents and offspring compete for selection
- (mu,lambda) Comma: Only offspring compete (requires lambda >= mu)

Recombination Types:
- Discrete: Each component randomly from one parent
- Intermediate: Average of parent components
- Global: Components from any member of population

Self-Adaptive Mutation:
  sigma' = sigma * exp(tau' * N(0,1) + tau * N_i(0,1))
  x' = x + sigma' * N(0,1)

where:
  - tau = 1/sqrt(2n) - local learning rate
  - tau' = 1/sqrt(2*sqrt(n)) - global learning rate
  - N(0,1) - standard normal random

Key Parameters:
- mu: Parent population size
- lambda: Offspring population size (typically 7*mu)
- rho: Number of parents for recombination
- initial_sigma: Starting step size

Usage Example:
  from es_engine import optimize_value_es
  from es_operators import ESConfig, ESSelectionType

  config = ESConfig(
      mu=15,
      lambda_=100,
      selection_type=ESSelectionType.PLUS,
      self_adaptive=True
  )
  result = optimize_value_es(
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

        choice = get_user_choice("Enter choice (1-8): ",
                                ['1', '2', '3', '4', '5', '6', '7', '8'])

        if choice == '1':
            demo_quick_optimization()
        elif choice == '2':
            demo_operators()
        elif choice == '3':
            configure_and_run()
        elif choice == '4':
            compare_selection()
        elif choice == '5':
            compare_recombination()
        elif choice == '6':
            test_self_adaptive()
        elif choice == '7':
            view_documentation()
        elif choice == '8':
            print("\nExiting ES CLI. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
