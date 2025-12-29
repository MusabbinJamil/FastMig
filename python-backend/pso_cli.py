#!/usr/bin/env python3
"""
PSO (Particle Swarm Optimization) Interactive CLI
==================================================
Run this for interactive testing and exploration of PSO features.

Usage:
    python pso_cli.py
"""

import numpy as np
import sys
import logging
from typing import Optional

from pso_operators import (
    PSOConfig, PSOTopology, PSOVariant, ConstraintHandling
)
from pso_engine import ParticleSwarmOptimizer, optimize_value_pso

# Configure logging
logging.basicConfig(level=logging.WARNING)


def clear_screen():
    """Clear console screen"""
    print("\033[H\033[J", end="")


def print_header():
    """Print CLI header"""
    print("\n" + "="*60)
    print("  PSO (Particle Swarm Optimization) Interactive CLI")
    print("="*60)


def print_menu():
    """Print main menu"""
    print("\n--- Main Menu ---")
    print("1. Quick optimization demo")
    print("2. Test PSO operators")
    print("3. Configure and run PSO")
    print("4. Compare topologies")
    print("5. Compare variants")
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
    """Quick demonstration of PSO optimization"""
    print("\n" + "="*50)
    print("  QUICK PSO OPTIMIZATION DEMO")
    print("="*50)

    # Simple fitness function: maximize -(x-5)^2 (optimal at x=5)
    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nOptimizing function: f(x) = -(x-5)^2")
    print("Optimal solution: x = 5, f(x) = 0")
    print("Bounds: [0, 10]")

    config = PSOConfig(
        swarm_size=20,
        iterations=50,
        early_stopping=True,
        patience=10
    )

    result = optimize_value_pso(
        fitness_function=fitness_func,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config
    )

    print(f"\nResults:")
    print(f"  Best Position: {result.best_position[0]:.6f}")
    print(f"  Best Fitness:  {result.best_fitness:.6f}")
    print(f"  Iterations:    {result.total_iterations}")
    print(f"  Converged:     {result.converged}")
    print(f"  Time:          {result.execution_time:.3f}s")

    input("\nPress Enter to continue...")


def demo_operators():
    """Demonstrate PSO operators"""
    print("\n" + "="*50)
    print("  PSO OPERATORS DEMONSTRATION")
    print("="*50)

    from pso_operators import PSOOperators

    print("\n1. Swarm Initialization:")
    positions, velocities = PSOOperators.initialize_swarm(
        n_particles=5,
        bounds_min=0.0,
        bounds_max=10.0
    )
    print(f"   Positions: {positions.round(2)}")
    print(f"   Velocities: {velocities.round(2)}")

    print("\n2. Velocity Update (Standard):")
    new_vel, stats = PSOOperators.update_velocity_standard(
        velocities=velocities,
        positions=positions,
        personal_best=positions,
        neighborhood_best=np.array([5.0]),
        w=0.7,
        c1=1.5,
        c2=1.5,
        v_min=-2.0,
        v_max=2.0
    )
    print(f"   New velocities: {new_vel.round(2)}")
    print(f"   Avg velocity: {stats['avg_velocity']:.2f}")

    print("\n3. Position Update:")
    new_pos, new_vel, stats = PSOOperators.update_position(
        positions=positions,
        velocities=new_vel,
        bounds_min=0.0,
        bounds_max=10.0
    )
    print(f"   New positions: {new_pos.round(2)}")

    print("\n4. Global Best Finding:")
    fitness = np.array([-((p - 5)**2) for p in new_pos])
    best_pos, best_fit, best_idx = PSOOperators.get_global_best(new_pos, fitness)
    print(f"   Best position: {best_pos:.2f}")
    print(f"   Best fitness: {best_fit:.2f}")

    print("\n5. Swarm Diversity:")
    diversity = PSOOperators.calculate_swarm_diversity(new_pos)
    print(f"   Diversity: {diversity:.4f}")

    input("\nPress Enter to continue...")


def configure_and_run():
    """Configure and run custom PSO"""
    print("\n" + "="*50)
    print("  CONFIGURE AND RUN PSO")
    print("="*50)

    # Get configuration
    print("\nTopology options:")
    print("  1. Global Best (gbest)")
    print("  2. Local Best (lbest/ring)")
    print("  3. Random Neighbors")
    print("  4. Von Neumann Grid")
    topology_choice = get_user_choice("Select topology (1-4): ", ['1', '2', '3', '4'])
    topologies = {
        '1': PSOTopology.GLOBAL_BEST,
        '2': PSOTopology.RING,
        '3': PSOTopology.RANDOM,
        '4': PSOTopology.VON_NEUMANN
    }
    topology = topologies[topology_choice]

    print("\nVariant options:")
    print("  1. Standard (constant inertia)")
    print("  2. Constriction Factor")
    print("  3. Linear Inertia Decay")
    variant_choice = get_user_choice("Select variant (1-3): ", ['1', '2', '3'])
    variants = {
        '1': PSOVariant.STANDARD,
        '2': PSOVariant.CONSTRICTION,
        '3': PSOVariant.INERTIA_DECAY
    }
    variant = variants[variant_choice]

    try:
        swarm_size = int(input("Swarm size (default 30): ") or "30")
        iterations = int(input("Max iterations (default 100): ") or "100")
    except ValueError:
        swarm_size = 30
        iterations = 100

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

    config = PSOConfig(
        swarm_size=swarm_size,
        iterations=iterations,
        topology=topology,
        variant=variant,
        early_stopping=True
    )

    print(f"\nRunning PSO with {config}...")

    result = optimize_value_pso(
        fitness_function=fitness_func,
        bounds_min=bounds[0],
        bounds_max=bounds[1],
        config=config
    )

    print(f"\nResults:")
    print(f"  Best Position:  {result.best_position[0]:.6f}")
    print(f"  Best Fitness:   {result.best_fitness:.6f}")
    print(f"  Iterations:     {result.total_iterations}")
    print(f"  Converged:      {result.converged}")
    print(f"  Time:           {result.execution_time:.3f}s")

    if result.iteration_metrics:
        print("\nFitness Progression (every 10 iterations):")
        for i, m in enumerate(result.iteration_metrics):
            if i % 10 == 0:
                print(f"  Iter {m.iteration:3d}: best={m.global_best_fitness:8.4f}, "
                      f"avg={m.average_fitness:8.4f}, div={m.swarm_diversity:.4f}")

    input("\nPress Enter to continue...")


def compare_topologies():
    """Compare different PSO topologies"""
    print("\n" + "="*50)
    print("  TOPOLOGY COMPARISON")
    print("="*50)

    def fitness_func(x):
        return -((x - 3) ** 2)

    print("\nOptimizing f(x) = -(x-3)^2 with different topologies:")
    print("-" * 60)

    for topology in PSOTopology:
        config = PSOConfig(
            swarm_size=25,
            iterations=50,
            topology=topology,
            early_stopping=True,
            patience=10
        )

        result = optimize_value_pso(
            fitness_function=fitness_func,
            bounds_min=-10.0,
            bounds_max=10.0,
            config=config
        )

        print(f"{topology.value:15} | x={result.best_position[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | iters={result.total_iterations:3d}")

    input("\nPress Enter to continue...")


def compare_variants():
    """Compare different PSO variants"""
    print("\n" + "="*50)
    print("  VARIANT COMPARISON")
    print("="*50)

    def fitness_func(x):
        return -((x - 7) ** 2)

    print("\nOptimizing f(x) = -(x-7)^2 with different variants:")
    print("-" * 60)

    for variant in PSOVariant:
        config = PSOConfig(
            swarm_size=25,
            iterations=50,
            variant=variant,
            early_stopping=True,
            patience=10
        )

        result = optimize_value_pso(
            fitness_function=fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        print(f"{variant.value:15} | x={result.best_position[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | iters={result.total_iterations:3d}")

    input("\nPress Enter to continue...")


def view_documentation():
    """View PSO documentation"""
    print("\n" + "="*50)
    print("  PSO DOCUMENTATION")
    print("="*50)

    print("""
PSO (Particle Swarm Optimization)
=================================

Key Concepts:
- Particles: Solutions in the search space
- Velocity: Rate of change of position
- Personal Best (pbest): Best position found by each particle
- Global/Neighborhood Best (gbest/lbest): Best position in neighborhood

Topologies:
- Global Best (gbest): All particles connected, fast convergence
- Local Best (lbest/ring): Ring topology, better exploration
- Random: Random neighbors each iteration
- Von Neumann: 2D grid topology

Variants:
- Standard: Constant inertia weight (w)
- Constriction: Uses constriction factor (chi)
- Inertia Decay: Linear w decay from w_max to w_min

Key Parameters:
- w (inertia weight): Controls exploration/exploitation balance
- c1 (cognitive coeff): Pull toward personal best
- c2 (social coeff): Pull toward neighborhood best
- swarm_size: Number of particles

Velocity Update:
  v = w*v + c1*r1*(pbest-x) + c2*r2*(gbest-x)

Position Update:
  x = x + v

Usage Example:
  from pso_engine import optimize_value_pso
  from pso_operators import PSOConfig

  config = PSOConfig(swarm_size=30, iterations=100)
  result = optimize_value_pso(
      fitness_function=lambda x: -(x**2),
      bounds_min=-10.0,
      bounds_max=10.0,
      config=config
  )
  print(f"Best: {result.best_position}")
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
            compare_topologies()
        elif choice == '5':
            compare_variants()
        elif choice == '6':
            view_documentation()
        elif choice == '7':
            print("\nExiting PSO CLI. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
