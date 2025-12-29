#!/usr/bin/env python3
"""
Comprehensive PSO System Demonstration
=======================================
Run this to see all PSO features in action.

Usage:
    python pso_demo.py
"""

import numpy as np
import sys
from pso_operators import (
    PSOConfig, PSOTopology, PSOVariant, PSOOperators
)
from pso_engine import ParticleSwarmOptimizer, optimize_value_pso


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_operators():
    """Demonstrate PSO operators"""
    print_section("1. PSO OPERATORS DEMONSTRATION")

    # Initialize swarm
    print("\nSWARM INITIALIZATION:")
    positions, velocities = PSOOperators.initialize_swarm(
        n_particles=6,
        bounds_min=0.0,
        bounds_max=10.0
    )
    print(f"  Positions: {positions.round(2)}")
    print(f"  Velocities: {velocities.round(2)}")

    # With seeding
    seed_vals = np.array([3.0, 5.0, 7.0])
    seeded_pos, seeded_vel = PSOOperators.initialize_swarm(
        n_particles=6,
        bounds_min=0.0,
        bounds_max=10.0,
        seed_values=seed_vals,
        seed_ratio=0.5
    )
    print(f"  Seeded positions: {seeded_pos.round(2)}")

    # Velocity update
    print("\nVELOCITY UPDATE METHODS:")
    pbest = positions.copy()
    gbest = np.array([5.0])

    new_vel_std, stats_std = PSOOperators.update_velocity_standard(
        velocities=velocities,
        positions=positions,
        personal_best=pbest,
        neighborhood_best=gbest,
        w=0.7, c1=1.5, c2=1.5,
        v_min=-2.0, v_max=2.0
    )
    print(f"  Standard update: avg_vel={stats_std['avg_velocity']:.3f}")

    new_vel_con, stats_con = PSOOperators.update_velocity_constriction(
        velocities=velocities,
        positions=positions,
        personal_best=pbest,
        neighborhood_best=gbest,
        chi=0.729, c1=2.05, c2=2.05,
        v_min=-2.0, v_max=2.0
    )
    print(f"  Constriction update: avg_vel={stats_con['avg_velocity']:.3f}")

    # Position update
    print("\nPOSITION UPDATE:")
    new_pos, new_vel, pos_stats = PSOOperators.update_position(
        positions=positions,
        velocities=new_vel_std,
        bounds_min=0.0,
        bounds_max=10.0
    )
    print(f"  New positions: {new_pos.round(2)}")
    print(f"  Boundary hits: {pos_stats['boundary_hits']}")

    # Global best
    print("\nGLOBAL BEST FINDING:")
    fitness = -((new_pos - 5) ** 2)
    best_pos, best_fit, best_idx = PSOOperators.get_global_best(new_pos, fitness)
    print(f"  Best position: {best_pos:.4f}")
    print(f"  Best fitness: {best_fit:.4f}")

    # Diversity
    print("\nSWARM DIVERSITY:")
    diversity = PSOOperators.calculate_swarm_diversity(new_pos)
    print(f"  Diversity: {diversity:.4f}")


def demo_topologies():
    """Demonstrate different topologies"""
    print_section("2. TOPOLOGY DEMONSTRATION")

    def fitness_func(x):
        return -((x - 5) ** 2)

    print("\nOptimizing f(x) = -(x-5)^2 with different topologies:\n")

    for topology in PSOTopology:
        config = PSOConfig(
            swarm_size=20,
            iterations=40,
            topology=topology,
            early_stopping=True,
            patience=8
        )

        result = optimize_value_pso(
            fitness_function=fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        print(f"  {topology.value:15} | x={result.best_position[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | iters={result.total_iterations:3d}")


def demo_variants():
    """Demonstrate different PSO variants"""
    print_section("3. VARIANT DEMONSTRATION")

    def fitness_func(x):
        return -((x - 3) ** 2)

    print("\nOptimizing f(x) = -(x-3)^2 with different variants:\n")

    for variant in PSOVariant:
        config = PSOConfig(
            swarm_size=20,
            iterations=40,
            variant=variant,
            early_stopping=True,
            patience=8
        )

        result = optimize_value_pso(
            fitness_function=fitness_func,
            bounds_min=-5.0,
            bounds_max=10.0,
            config=config
        )

        print(f"  {variant.value:15} | x={result.best_position[0]:7.4f} | "
              f"fitness={result.best_fitness:8.4f} | iters={result.total_iterations:3d}")


def demo_optimization():
    """Demonstrate PSO optimization"""
    print_section("4. PSO OPTIMIZATION DEMONSTRATION")

    # Sphere function
    print("\nOptimizing SPHERE FUNCTION (minimize x^2)")

    def sphere_fitness(x):
        return -(x ** 2)

    config = PSOConfig(
        swarm_size=25,
        iterations=50,
        early_stopping=True,
        patience=10
    )

    result = optimize_value_pso(
        fitness_function=sphere_fitness,
        bounds_min=-10.0,
        bounds_max=10.0,
        config=config
    )

    print(f"\nResults:")
    print(f"  Best Position: {result.best_position[0]:.6f}")
    print(f"  Best Fitness:  {result.best_fitness:.6f}")
    print(f"  Iterations:    {result.total_iterations}")
    print(f"  Converged:     {result.converged}")
    print(f"  Time:          {result.execution_time:.3f}s")

    # Shifted function
    print("\n\nOptimizing SHIFTED FUNCTION (optimal at x=7)")

    def shifted_fitness(x):
        return -((x - 7) ** 2)

    config2 = PSOConfig(
        swarm_size=30,
        iterations=60,
        variant=PSOVariant.INERTIA_DECAY,
        early_stopping=True
    )

    result2 = optimize_value_pso(
        fitness_function=shifted_fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config2
    )

    print(f"\nResults:")
    print(f"  Best Position: {result2.best_position[0]:.6f}")
    print(f"  Best Fitness:  {result2.best_fitness:.6f}")
    print(f"  Iterations:    {result2.total_iterations}")


def demo_inertia_decay():
    """Demonstrate inertia decay"""
    print_section("5. INERTIA DECAY DEMONSTRATION")

    print("\nInertia weight progression over 100 iterations:")
    print("  (from w_max=0.9 to w_min=0.4)")
    print("-" * 50)

    for iteration in [0, 25, 50, 75, 99]:
        w = PSOOperators.calculate_inertia_decay(
            iteration=iteration,
            max_iterations=100,
            w_max=0.9,
            w_min=0.4
        )
        bar = "#" * int(w * 40)
        print(f"  Iter {iteration:3d}: w={w:.4f} |{bar}")


def demo_metrics():
    """Demonstrate metrics tracking"""
    print_section("6. METRICS AND CONVERGENCE TRACKING")

    def fitness(x):
        return -((x - 5) ** 2)

    config = PSOConfig(
        swarm_size=20,
        iterations=60,
        variant=PSOVariant.INERTIA_DECAY,
        early_stopping=False  # Run all iterations for demo
    )

    result = optimize_value_pso(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config
    )

    print("\nIteration progression:")
    print("-" * 70)
    print(f"{'Iter':>5} | {'Best':>10} | {'Avg':>10} | {'Velocity':>10} | {'Diversity':>10}")
    print("-" * 70)

    for i, m in enumerate(result.iteration_metrics):
        if i % 10 == 0:
            print(f"{m.iteration:5d} | {m.global_best_fitness:10.4f} | "
                  f"{m.average_fitness:10.4f} | {m.average_velocity:10.4f} | "
                  f"{m.swarm_diversity:10.4f}")

    print("-" * 70)
    print(f"\nFinal Statistics:")
    print(f"  Best Fitness:    {result.best_fitness:.6f}")
    print(f"  Best Position:   {result.best_position[0]:.6f}")
    print(f"  Avg Fitness:     {result.average_fitness:.6f}")
    print(f"  Total Iterations: {result.total_iterations}")
    print(f"  Execution Time:  {result.execution_time:.3f}s")


def demo_seed_values():
    """Demonstrate seeding with initial values"""
    print_section("7. SEEDING DEMONSTRATION")

    def fitness(x):
        return -((x - 5) ** 2)

    print("\nOptimizing f(x) = -(x-5)^2")
    print("Seeding with values around the optimum")

    # Without seeding
    config = PSOConfig(swarm_size=15, iterations=30, early_stopping=True)
    result_no_seed = optimize_value_pso(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config
    )

    # With seeding
    seed_values = np.array([4.0, 5.0, 6.0])  # Near optimal
    result_seeded = optimize_value_pso(
        fitness_function=fitness,
        bounds_min=0.0,
        bounds_max=10.0,
        config=config,
        seed_values=seed_values
    )

    print(f"\n  Without seeding:")
    print(f"    Best: x={result_no_seed.best_position[0]:.4f}, "
          f"fitness={result_no_seed.best_fitness:.4f}, "
          f"iters={result_no_seed.total_iterations}")

    print(f"\n  With seeding (values near optimal):")
    print(f"    Best: x={result_seeded.best_position[0]:.4f}, "
          f"fitness={result_seeded.best_fitness:.4f}, "
          f"iters={result_seeded.total_iterations}")


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("  PSO SYSTEM - COMPREHENSIVE DEMONSTRATION")
    print("  All Features & Capabilities")
    print("="*70)

    try:
        demo_operators()
        demo_topologies()
        demo_variants()
        demo_optimization()
        demo_inertia_decay()
        demo_metrics()
        demo_seed_values()

        print_section("DEMONSTRATION COMPLETE")
        print("\nAll PSO components working correctly!")
        print("\nNext Steps:")
        print("  1. Run: python test_pso_system.py  (unit tests)")
        print("  2. Run: python pso_cli.py          (interactive CLI)")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
