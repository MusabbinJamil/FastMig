"""
PSO (Particle Swarm Optimization) Engine Module

This module provides the main PSO engine class for optimization.
Supports multiple topologies (gbest, lbest, ring, random, von_neumann)
and variants (standard, constriction, inertia_decay).
"""

import numpy as np
import time
import logging
from typing import Callable, Optional, List, Tuple, Dict, Any

from pso_operators import (
    PSOConfig,
    PSOTopology,
    PSOVariant,
    ConstraintHandling,
    PSOMetrics,
    PSOResult,
    PSOOperators
)

logger = logging.getLogger(__name__)


class ParticleSwarmOptimizer:
    """
    Particle Swarm Optimization Engine.

    Supports:
    - Global best (gbest) topology
    - Local best (lbest/ring) topology
    - Random neighbors topology
    - Von Neumann (grid) topology
    - Standard PSO with inertia weight
    - Constriction factor PSO
    - Linear inertia decay PSO
    """

    def __init__(
        self,
        config: PSOConfig,
        fitness_function: Callable[[float], float],
        bounds_min: float,
        bounds_max: float,
        seed_values: Optional[np.ndarray] = None
    ):
        """
        Initialize PSO engine.

        Args:
            config: PSO configuration
            fitness_function: Function that takes a value and returns fitness (higher is better)
            bounds_min: Lower bound for positions
            bounds_max: Upper bound for positions
            seed_values: Optional array of values to seed particles from
        """
        # Validate config
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid PSO config: {errors}")

        self.config = config
        self.fitness_function = fitness_function
        self.bounds_min = bounds_min
        self.bounds_max = bounds_max
        self.seed_values = seed_values

        # Calculate velocity bounds based on position range
        range_size = bounds_max - bounds_min
        self.v_max = range_size * config.velocity_clamp
        self.v_min = -self.v_max

        # Initialize swarm
        self._initialize_swarm()

        # Tracking
        self.fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.velocity_history: List[float] = []
        self.diversity_history: List[float] = []
        self.iteration_metrics: List[PSOMetrics] = []
        self.errors: List[str] = []

        # Convergence tracking
        self.stagnation_counter = 0
        self.best_fitness_ever = -np.inf

        logger.info(f"PSO Engine initialized: {config}")

    def _initialize_swarm(self):
        """Initialize particle positions, velocities, and personal bests."""
        n = self.config.swarm_size

        # Initialize positions and velocities
        self.positions, self.velocities = PSOOperators.initialize_swarm(
            n_particles=n,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
            seed_values=self.seed_values,
            seed_ratio=0.5 if self.seed_values is not None else 0.0
        )

        # Evaluate initial fitness
        self.fitness_values = np.array([
            self.fitness_function(pos) for pos in self.positions
        ])

        # Initialize personal bests
        self.personal_best_positions = self.positions.copy()
        self.personal_best_fitness = self.fitness_values.copy()

        # Initialize global best
        self.global_best_position, self.global_best_fitness, self.global_best_idx = \
            PSOOperators.get_global_best(self.personal_best_positions, self.personal_best_fitness)

        logger.debug(f"Swarm initialized: n={n}, initial best fitness={self.global_best_fitness:.4f}")

    def _get_neighborhood_best(self, particle_idx: int) -> Tuple[np.ndarray, float]:
        """
        Get the best position in particle's neighborhood based on topology.

        Args:
            particle_idx: Index of the current particle

        Returns:
            Tuple of (best position, best fitness) in neighborhood
        """
        topology = self.config.topology
        n = self.config.swarm_size

        if topology == PSOTopology.GLOBAL_BEST:
            # Everyone connects to global best
            return self.global_best_position, self.global_best_fitness

        elif topology in (PSOTopology.LOCAL_BEST, PSOTopology.RING):
            # Ring topology
            return PSOOperators.get_neighborhood_best_ring(
                particle_idx=particle_idx,
                n_particles=n,
                personal_best_positions=self.personal_best_positions,
                personal_best_fitness=self.personal_best_fitness,
                neighborhood_size=self.config.neighborhood_size
            )

        elif topology == PSOTopology.RANDOM:
            # Random neighbors
            return PSOOperators.get_neighborhood_best_random(
                particle_idx=particle_idx,
                n_particles=n,
                personal_best_positions=self.personal_best_positions,
                personal_best_fitness=self.personal_best_fitness,
                neighborhood_size=self.config.neighborhood_size
            )

        elif topology == PSOTopology.VON_NEUMANN:
            # 2D grid topology
            return PSOOperators.get_neighborhood_best_von_neumann(
                particle_idx=particle_idx,
                n_particles=n,
                personal_best_positions=self.personal_best_positions,
                personal_best_fitness=self.personal_best_fitness
            )

        else:
            # Default to global best
            return self.global_best_position, self.global_best_fitness

    def _update_velocities(self, iteration: int) -> Dict[str, float]:
        """
        Update all particle velocities based on PSO variant.

        Args:
            iteration: Current iteration number

        Returns:
            Statistics dictionary
        """
        variant = self.config.variant
        c1 = self.config.cognitive_coeff
        c2 = self.config.social_coeff

        # Calculate inertia weight based on variant
        if variant == PSOVariant.INERTIA_DECAY:
            w = PSOOperators.calculate_inertia_decay(
                iteration=iteration,
                max_iterations=self.config.iterations,
                w_max=self.config.inertia_max,
                w_min=self.config.inertia_min
            )
        else:
            w = self.config.inertia_weight

        # For local topologies, need to get neighborhood best for each particle
        if self.config.topology != PSOTopology.GLOBAL_BEST:
            # Update each particle individually
            all_stats = []
            for i in range(self.config.swarm_size):
                nbest_pos, nbest_fit = self._get_neighborhood_best(i)

                if variant == PSOVariant.CONSTRICTION:
                    new_vel, stats = PSOOperators.update_velocity_constriction(
                        velocities=self.velocities[i:i+1],
                        positions=self.positions[i:i+1],
                        personal_best=self.personal_best_positions[i:i+1],
                        neighborhood_best=np.array([nbest_pos]),
                        chi=self.config.constriction_factor,
                        c1=c1,
                        c2=c2,
                        v_min=self.v_min,
                        v_max=self.v_max
                    )
                else:
                    new_vel, stats = PSOOperators.update_velocity_standard(
                        velocities=self.velocities[i:i+1],
                        positions=self.positions[i:i+1],
                        personal_best=self.personal_best_positions[i:i+1],
                        neighborhood_best=np.array([nbest_pos]),
                        w=w,
                        c1=c1,
                        c2=c2,
                        v_min=self.v_min,
                        v_max=self.v_max
                    )

                self.velocities[i] = new_vel[0]
                all_stats.append(stats)

            # Aggregate statistics
            combined_stats = {
                'avg_velocity': float(np.mean([s['avg_velocity'] for s in all_stats])),
                'velocity_std': float(np.std(self.velocities)),
                'max_velocity': float(np.max(np.abs(self.velocities))),
                'current_inertia': w
            }
            return combined_stats

        else:
            # Global best topology - can update all at once
            if variant == PSOVariant.CONSTRICTION:
                self.velocities, stats = PSOOperators.update_velocity_constriction(
                    velocities=self.velocities,
                    positions=self.positions,
                    personal_best=self.personal_best_positions,
                    neighborhood_best=self.global_best_position,
                    chi=self.config.constriction_factor,
                    c1=c1,
                    c2=c2,
                    v_min=self.v_min,
                    v_max=self.v_max
                )
            else:
                self.velocities, stats = PSOOperators.update_velocity_standard(
                    velocities=self.velocities,
                    positions=self.positions,
                    personal_best=self.personal_best_positions,
                    neighborhood_best=self.global_best_position,
                    w=w,
                    c1=c1,
                    c2=c2,
                    v_min=self.v_min,
                    v_max=self.v_max
                )

            stats['current_inertia'] = w
            return stats

    def _update_positions(self) -> Dict[str, Any]:
        """
        Update all particle positions.

        Returns:
            Statistics dictionary
        """
        self.positions, self.velocities, stats = PSOOperators.update_position(
            positions=self.positions,
            velocities=self.velocities,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
            constraint_handling=self.config.constraint_handling
        )
        return stats

    def _evaluate_fitness(self) -> Dict[str, float]:
        """
        Evaluate fitness for all particles.

        Returns:
            Statistics dictionary
        """
        self.fitness_values = np.array([
            self.fitness_function(pos) for pos in self.positions
        ])

        return {
            'best_fitness': float(np.max(self.fitness_values)),
            'worst_fitness': float(np.min(self.fitness_values)),
            'avg_fitness': float(np.mean(self.fitness_values)),
            'fitness_std': float(np.std(self.fitness_values))
        }

    def _update_personal_bests(self) -> int:
        """
        Update personal bests for particles with improved fitness.

        Returns:
            Number of particles that improved
        """
        improved_mask = self.fitness_values > self.personal_best_fitness
        n_improved = int(np.sum(improved_mask))

        if n_improved > 0:
            self.personal_best_positions[improved_mask] = self.positions[improved_mask]
            self.personal_best_fitness[improved_mask] = self.fitness_values[improved_mask]

        return n_improved

    def _update_global_best(self) -> bool:
        """
        Update global best if a better solution is found.

        Returns:
            True if global best was updated
        """
        current_best_idx = np.argmax(self.personal_best_fitness)
        current_best_fitness = self.personal_best_fitness[current_best_idx]

        if current_best_fitness > self.global_best_fitness:
            self.global_best_position = self.personal_best_positions[current_best_idx].copy()
            self.global_best_fitness = current_best_fitness
            self.global_best_idx = current_best_idx
            return True

        return False

    def _calculate_metrics(self, iteration: int, velocity_stats: Dict, position_stats: Dict) -> PSOMetrics:
        """
        Calculate metrics for current iteration.

        Args:
            iteration: Current iteration number
            velocity_stats: Statistics from velocity update
            position_stats: Statistics from position update

        Returns:
            PSOMetrics object
        """
        diversity = PSOOperators.calculate_swarm_diversity(self.positions)
        convergence_rate = PSOOperators.calculate_convergence_rate(self.fitness_history)

        metrics = PSOMetrics(
            iteration=iteration,
            global_best_fitness=self.global_best_fitness,
            average_fitness=float(np.mean(self.fitness_values)),
            worst_fitness=float(np.min(self.fitness_values)),
            best_position=self.global_best_position.copy() if isinstance(self.global_best_position, np.ndarray) else np.array([self.global_best_position]),
            average_velocity=velocity_stats.get('avg_velocity', 0.0),
            velocity_std=velocity_stats.get('velocity_std', 0.0),
            max_velocity=velocity_stats.get('max_velocity', 0.0),
            swarm_diversity=diversity,
            convergence_rate=convergence_rate,
            stagnation_counter=self.stagnation_counter,
            current_inertia=velocity_stats.get('current_inertia', self.config.inertia_weight)
        )

        return metrics

    def _check_convergence(self) -> bool:
        """
        Check if optimization has converged.

        Returns:
            True if converged (should stop)
        """
        if not self.config.early_stopping:
            return False

        # Check fitness threshold
        if self.global_best_fitness >= self.config.fitness_threshold:
            logger.info(f"PSO: Fitness threshold {self.config.fitness_threshold} reached")
            return True

        # Check stagnation
        if self.stagnation_counter >= self.config.patience:
            logger.info(f"PSO: Stagnation detected after {self.stagnation_counter} iterations")
            return True

        return False

    def run(self) -> PSOResult:
        """
        Run PSO optimization.

        Returns:
            PSOResult with best solution and history
        """
        start_time = time.time()
        convergence_iteration = None

        logger.info(f"Starting PSO: {self.config.swarm_size} particles, {self.config.iterations} iterations")
        logger.info(f"Topology: {self.config.topology.value}, Variant: {self.config.variant.value}")

        try:
            for iteration in range(self.config.iterations):
                # Store previous best for stagnation detection
                prev_best = self.global_best_fitness

                # Update velocities
                velocity_stats = self._update_velocities(iteration)

                # Update positions
                position_stats = self._update_positions()

                # Evaluate fitness
                fitness_stats = self._evaluate_fitness()

                # Update personal bests
                n_improved = self._update_personal_bests()

                # Update global best
                global_improved = self._update_global_best()

                # Track stagnation
                if global_improved:
                    improvement = self.global_best_fitness - prev_best
                    if improvement > self.config.min_improvement:
                        self.stagnation_counter = 0
                    else:
                        self.stagnation_counter += 1
                else:
                    self.stagnation_counter += 1

                # Calculate and store metrics
                metrics = self._calculate_metrics(iteration, velocity_stats, position_stats)
                self.iteration_metrics.append(metrics)
                self.fitness_history.append(self.global_best_fitness)
                self.avg_fitness_history.append(metrics.average_fitness)
                self.velocity_history.append(metrics.average_velocity)
                self.diversity_history.append(metrics.swarm_diversity)

                # Log progress periodically
                if iteration % 10 == 0 or iteration == self.config.iterations - 1:
                    logger.debug(
                        f"PSO Iter {iteration}: best={self.global_best_fitness:.4f}, "
                        f"avg={metrics.average_fitness:.4f}, div={metrics.swarm_diversity:.4f}"
                    )

                # Check convergence
                if self._check_convergence():
                    convergence_iteration = iteration
                    break

        except Exception as e:
            logger.error(f"PSO error at iteration {iteration}: {str(e)}")
            self.errors.append(str(e))

        execution_time = time.time() - start_time

        # Create result
        result = PSOResult(
            best_position=self.global_best_position if isinstance(self.global_best_position, np.ndarray) else np.array([self.global_best_position]),
            best_fitness=float(self.global_best_fitness),
            worst_fitness=float(np.min(self.personal_best_fitness)),
            average_fitness=float(np.mean(self.personal_best_fitness)),
            total_iterations=len(self.fitness_history),
            converged=convergence_iteration is not None,
            convergence_iteration=convergence_iteration,
            fitness_history=self.fitness_history,
            avg_fitness_history=self.avg_fitness_history,
            velocity_history=self.velocity_history,
            diversity_history=self.diversity_history,
            iteration_metrics=self.iteration_metrics,
            final_positions=self.positions.copy(),
            final_velocities=self.velocities.copy(),
            execution_time=execution_time,
            errors=self.errors,
            config=self.config
        )

        logger.info(
            f"PSO complete: best={result.best_fitness:.4f}, "
            f"iterations={result.total_iterations}, "
            f"converged={result.converged}, "
            f"time={execution_time:.2f}s"
        )

        return result


def optimize_value_pso(
    fitness_function: Callable[[float], float],
    bounds_min: float,
    bounds_max: float,
    config: Optional[PSOConfig] = None,
    seed_values: Optional[np.ndarray] = None
) -> PSOResult:
    """
    Convenience function to optimize a single value using PSO.

    Args:
        fitness_function: Function that takes a value and returns fitness
        bounds_min: Lower bound
        bounds_max: Upper bound
        config: Optional PSO configuration (uses defaults if not provided)
        seed_values: Optional values to seed particles from

    Returns:
        PSOResult with best solution
    """
    if config is None:
        config = PSOConfig()

    optimizer = ParticleSwarmOptimizer(
        config=config,
        fitness_function=fitness_function,
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        seed_values=seed_values
    )

    return optimizer.run()
