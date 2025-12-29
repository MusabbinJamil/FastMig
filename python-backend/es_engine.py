"""
ES (Evolution Strategy) Engine Module

This module provides the main ES engine class for optimization.
Supports (μ+λ) and (μ,λ) selection with self-adaptive mutation.
"""

import numpy as np
import time
import logging
from typing import Callable, Optional, List, Dict, Any

from es_operators import (
    ESConfig,
    ESSelectionType,
    ESRecombinationType,
    ESMetrics,
    ESResult,
    ESOperators
)

logger = logging.getLogger(__name__)


class EvolutionStrategyOptimizer:
    """
    Evolution Strategy Optimization Engine.

    Supports:
    - (μ+λ) plus selection: parents and offspring compete
    - (μ,λ) comma selection: only offspring compete
    - Discrete, intermediate, and global recombination
    - Self-adaptive step size mutation
    - Multiple constraint handling methods
    """

    def __init__(
        self,
        config: ESConfig,
        fitness_function: Callable[[float], float],
        bounds_min: float,
        bounds_max: float,
        seed_values: Optional[np.ndarray] = None
    ):
        """
        Initialize ES engine.

        Args:
            config: ES configuration
            fitness_function: Function that takes a value and returns fitness (higher is better)
            bounds_min: Lower bound for values
            bounds_max: Upper bound for values
            seed_values: Optional array of values to seed population from
        """
        # Validate config
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid ES config: {errors}")

        self.config = config
        self.fitness_function = fitness_function
        self.bounds_min = bounds_min
        self.bounds_max = bounds_max
        self.seed_values = seed_values

        # Initialize population
        self._initialize_population()

        # Tracking
        self.fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.sigma_history: List[float] = []
        self.diversity_history: List[float] = []
        self.generation_metrics: List[ESMetrics] = []
        self.errors: List[str] = []

        # Convergence tracking
        self.stagnation_counter = 0
        self.best_fitness_ever = -np.inf

        logger.info(f"ES Engine initialized: {config}")

    def _initialize_population(self):
        """Initialize population and evaluate initial fitness."""
        self.population, self.sigmas = ESOperators.initialize_population(
            mu=self.config.mu,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
            initial_sigma=self.config.initial_sigma,
            seed_values=self.seed_values,
            seed_ratio=0.5 if self.seed_values is not None else 0.0
        )

        # Evaluate initial fitness
        self.fitness_values = np.array([
            self.fitness_function(ind) for ind in self.population
        ])

        # Track best
        best_idx = np.argmax(self.fitness_values)
        self.best_individual = self.population[best_idx]
        self.best_sigma = self.sigmas[best_idx]
        self.best_fitness = self.fitness_values[best_idx]
        self.best_fitness_ever = self.best_fitness

        logger.debug(
            f"Population initialized: μ={self.config.mu}, "
            f"initial best fitness={self.best_fitness:.4f}"
        )

    def _generate_offspring(self) -> tuple:
        """
        Generate λ offspring through recombination and mutation.

        Returns:
            Tuple of (offspring values, offspring sigmas, offspring fitness)
        """
        offspring = []
        offspring_sigmas = []
        offspring_fitness = []

        for _ in range(self.config.lambda_):
            try:
                # Recombination
                value, sigma, _ = ESOperators.apply_recombination(
                    recomb_type=self.config.recombination_type,
                    population=self.population,
                    sigmas=self.sigmas,
                    fitness=self.fitness_values,
                    rho=self.config.rho
                )

                # Mutation
                new_value, new_sigma, _ = ESOperators.apply_mutation(
                    value=value,
                    sigma=sigma,
                    config=self.config,
                    bounds_min=self.bounds_min,
                    bounds_max=self.bounds_max
                )

                # Evaluate fitness
                fitness = self.fitness_function(new_value)

                offspring.append(new_value)
                offspring_sigmas.append(new_sigma)
                offspring_fitness.append(fitness)

            except Exception as e:
                logger.warning(f"Error generating offspring: {e}")
                self.errors.append(f"Offspring generation: {str(e)}")

        return (
            np.array(offspring),
            np.array(offspring_sigmas),
            np.array(offspring_fitness)
        )

    def _evolve_generation(self, generation: int) -> Dict[str, Any]:
        """
        Evolve one generation.

        Args:
            generation: Current generation number

        Returns:
            Statistics dictionary
        """
        # Generate offspring
        offspring, offspring_sigmas, offspring_fitness = self._generate_offspring()

        if len(offspring) == 0:
            return {
                'offspring_generated': 0,
                'parents_selected': self.config.mu,
                'successful_mutations': 0
            }

        # Selection
        self.population, self.sigmas, self.fitness_values, selection_stats = \
            ESOperators.apply_selection(
                selection_type=self.config.selection_type,
                parents=self.population,
                parent_sigmas=self.sigmas,
                parent_fitness=self.fitness_values,
                offspring=offspring,
                offspring_sigmas=offspring_sigmas,
                offspring_fitness=offspring_fitness,
                mu=self.config.mu
            )

        # Update best
        best_idx = np.argmax(self.fitness_values)
        if self.fitness_values[best_idx] > self.best_fitness:
            self.best_individual = self.population[best_idx]
            self.best_sigma = self.sigmas[best_idx]
            self.best_fitness = self.fitness_values[best_idx]

        # Count successful mutations (offspring better than worst parent before selection)
        parent_worst = np.min(self.fitness_values)
        successful_mutations = int(np.sum(offspring_fitness > parent_worst))

        return {
            'offspring_generated': len(offspring),
            'parents_selected': self.config.mu,
            'successful_mutations': successful_mutations,
            'selection_stats': selection_stats
        }

    def _calculate_metrics(
        self,
        generation: int,
        evolution_stats: Dict[str, Any]
    ) -> ESMetrics:
        """
        Calculate metrics for current generation.

        Args:
            generation: Current generation number
            evolution_stats: Statistics from evolution

        Returns:
            ESMetrics object
        """
        sigma_stats = ESOperators.calculate_sigma_stats(self.sigmas)
        diversity = ESOperators.calculate_diversity(self.population)
        convergence_rate = ESOperators.calculate_convergence_rate(self.fitness_history)

        offspring_gen = evolution_stats.get('offspring_generated', 0)
        successful = evolution_stats.get('successful_mutations', 0)
        success_rate = successful / max(offspring_gen, 1)

        metrics = ESMetrics(
            generation=generation,
            best_fitness=float(self.best_fitness),
            average_fitness=float(np.mean(self.fitness_values)),
            worst_fitness=float(np.min(self.fitness_values)),
            population_diversity=diversity,
            convergence_rate=convergence_rate,
            offspring_generated=offspring_gen,
            parents_selected=self.config.mu,
            average_sigma=sigma_stats['average'],
            sigma_std=sigma_stats['std'],
            min_sigma=sigma_stats['min'],
            max_sigma=sigma_stats['max'],
            successful_mutations=successful,
            success_rate=success_rate,
            stagnation_counter=self.stagnation_counter
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
        if self.best_fitness >= self.config.fitness_threshold:
            logger.info(f"ES: Fitness threshold {self.config.fitness_threshold} reached")
            return True

        # Check stagnation
        if self.stagnation_counter >= self.config.patience:
            logger.info(f"ES: Stagnation detected after {self.stagnation_counter} generations")
            return True

        return False

    def run(self) -> ESResult:
        """
        Run ES optimization.

        Returns:
            ESResult with best solution and history
        """
        start_time = time.time()
        convergence_generation = None

        logger.info(
            f"Starting ES: (μ={self.config.mu}, λ={self.config.lambda_}), "
            f"{self.config.generations} generations, "
            f"selection={self.config.selection_type.value}"
        )

        try:
            for generation in range(self.config.generations):
                # Store previous best for stagnation detection
                prev_best = self.best_fitness

                # Evolve one generation
                evolution_stats = self._evolve_generation(generation)

                # Track stagnation
                if self.best_fitness > prev_best + self.config.min_improvement:
                    self.stagnation_counter = 0
                else:
                    self.stagnation_counter += 1

                # Calculate and store metrics
                metrics = self._calculate_metrics(generation, evolution_stats)
                self.generation_metrics.append(metrics)
                self.fitness_history.append(self.best_fitness)
                self.avg_fitness_history.append(metrics.average_fitness)
                self.sigma_history.append(metrics.average_sigma)
                self.diversity_history.append(metrics.population_diversity)

                # Log progress periodically
                if generation % 10 == 0 or generation == self.config.generations - 1:
                    logger.debug(
                        f"ES Gen {generation}: best={self.best_fitness:.4f}, "
                        f"avg={metrics.average_fitness:.4f}, "
                        f"σ={metrics.average_sigma:.4f}"
                    )

                # Check convergence
                if self._check_convergence():
                    convergence_generation = generation
                    break

        except Exception as e:
            logger.error(f"ES error at generation {generation}: {str(e)}")
            self.errors.append(str(e))

        execution_time = time.time() - start_time

        # Create result
        result = ESResult(
            best_individual=np.array([self.best_individual]) if not isinstance(self.best_individual, np.ndarray) else self.best_individual,
            best_fitness=float(self.best_fitness),
            worst_fitness=float(np.min(self.fitness_values)),
            average_fitness=float(np.mean(self.fitness_values)),
            best_sigma=float(self.best_sigma),
            total_generations=len(self.fitness_history),
            converged=convergence_generation is not None,
            convergence_generation=convergence_generation,
            fitness_history=self.fitness_history,
            avg_fitness_history=self.avg_fitness_history,
            sigma_history=self.sigma_history,
            diversity_history=self.diversity_history,
            generation_metrics=self.generation_metrics,
            final_population=self.population.copy(),
            final_sigmas=self.sigmas.copy(),
            final_fitness=self.fitness_values.copy(),
            selection_type_used=self.config.selection_type.value,
            recombination_type_used=self.config.recombination_type.value,
            execution_time=execution_time,
            errors=self.errors,
            config=self.config
        )

        logger.info(
            f"ES complete: best={result.best_fitness:.4f}, "
            f"generations={result.total_generations}, "
            f"converged={result.converged}, "
            f"time={execution_time:.2f}s"
        )

        return result


def optimize_value_es(
    fitness_function: Callable[[float], float],
    bounds_min: float,
    bounds_max: float,
    config: Optional[ESConfig] = None,
    seed_values: Optional[np.ndarray] = None
) -> ESResult:
    """
    Convenience function to optimize a single value using ES.

    Args:
        fitness_function: Function that takes a value and returns fitness
        bounds_min: Lower bound
        bounds_max: Upper bound
        config: Optional ES configuration (uses defaults if not provided)
        seed_values: Optional values to seed population from

    Returns:
        ESResult with best solution
    """
    if config is None:
        config = ESConfig()

    optimizer = EvolutionStrategyOptimizer(
        config=config,
        fitness_function=fitness_function,
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        seed_values=seed_values
    )

    return optimizer.run()
