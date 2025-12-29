"""
DE (Differential Evolution) Engine Module

This module provides the main DE engine class for optimization.
Supports all 6 mutation strategies with optional adaptive F and CR.
"""

import numpy as np
import time
import logging
from typing import Callable, Optional, List, Tuple, Dict, Any

from de_operators import (
    DEConfig,
    DEMutationStrategy,
    DECrossoverType,
    ConstraintHandling,
    DEMetrics,
    DEResult,
    DEOperators
)

logger = logging.getLogger(__name__)


class DifferentialEvolutionOptimizer:
    """
    Differential Evolution Optimization Engine.

    Supports:
    - 6 mutation strategies: rand/1, rand/2, best/1, best/2, current-to-best/1, current-to-rand/1
    - Binomial and exponential crossover
    - Adaptive F and CR parameters
    - Multiple constraint handling methods
    """

    def __init__(
        self,
        config: DEConfig,
        fitness_function: Callable[[float], float],
        bounds_min: float,
        bounds_max: float,
        seed_values: Optional[np.ndarray] = None
    ):
        """
        Initialize DE engine.

        Args:
            config: DE configuration
            fitness_function: Function that takes a value and returns fitness (higher is better)
            bounds_min: Lower bound for values
            bounds_max: Upper bound for values
            seed_values: Optional array of values to seed population from
        """
        # Validate config
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid DE config: {errors}")

        self.config = config
        self.fitness_function = fitness_function
        self.bounds_min = bounds_min
        self.bounds_max = bounds_max
        self.seed_values = seed_values

        # Current adaptive parameters
        self.current_f = config.scale_factor
        self.current_cr = config.crossover_rate

        # Initialize population
        self._initialize_population()

        # Tracking
        self.fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.success_rate_history: List[float] = []
        self.diversity_history: List[float] = []
        self.f_history: List[float] = []
        self.cr_history: List[float] = []
        self.generation_metrics: List[DEMetrics] = []
        self.errors: List[str] = []

        # Convergence tracking
        self.stagnation_counter = 0
        self.best_fitness_ever = -np.inf

        logger.info(f"DE Engine initialized: {config}")

    def _initialize_population(self):
        """Initialize population and evaluate initial fitness."""
        self.population = DEOperators.initialize_population(
            pop_size=self.config.population_size,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
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
        self.best_fitness = self.fitness_values[best_idx]
        self.best_fitness_ever = self.best_fitness

        logger.debug(
            f"Population initialized: n={self.config.population_size}, "
            f"initial best fitness={self.best_fitness:.4f}"
        )

    def _evolve_generation(self, generation: int) -> Tuple[int, int]:
        """
        Evolve one generation.

        Args:
            generation: Current generation number

        Returns:
            Tuple of (number of improvements, number of trials evaluated)
        """
        improvements = 0
        trials_evaluated = 0
        new_population = self.population.copy()
        new_fitness = self.fitness_values.copy()

        for i in range(self.config.population_size):
            try:
                # Mutation
                mutant, mutation_stats = DEOperators.apply_mutation(
                    strategy=self.config.mutation_strategy,
                    population=self.population,
                    fitness=self.fitness_values,
                    target_idx=i,
                    F=self.current_f
                )

                # Apply constraints to mutant
                mutant = DEOperators.apply_constraints(
                    value=mutant,
                    bounds_min=self.bounds_min,
                    bounds_max=self.bounds_max,
                    handling=self.config.constraint_handling
                )

                # Crossover
                trial, from_mutant = DEOperators.apply_crossover(
                    crossover_type=self.config.crossover_type,
                    target=self.population[i],
                    mutant=mutant,
                    CR=self.current_cr
                )

                # Ensure at least one dimension comes from mutant
                # (for 1D, this means sometimes force the mutant value)
                if not from_mutant and np.random.random() < 0.5:
                    trial = mutant

                # Apply constraints to trial
                trial = DEOperators.apply_constraints(
                    value=trial,
                    bounds_min=self.bounds_min,
                    bounds_max=self.bounds_max,
                    handling=self.config.constraint_handling
                )

                # Evaluate trial
                trial_fitness = self.fitness_function(trial)
                trials_evaluated += 1

                # Selection
                selected, selected_fitness, trial_won = DEOperators.greedy_selection(
                    target_value=self.population[i],
                    target_fitness=self.fitness_values[i],
                    trial_value=trial,
                    trial_fitness=trial_fitness
                )

                new_population[i] = selected
                new_fitness[i] = selected_fitness

                if trial_won:
                    improvements += 1

            except Exception as e:
                logger.warning(f"Error evolving individual {i}: {e}")
                self.errors.append(f"Gen {generation}, ind {i}: {str(e)}")
                # Keep original
                new_population[i] = self.population[i]
                new_fitness[i] = self.fitness_values[i]

        # Update population
        self.population = new_population
        self.fitness_values = new_fitness

        # Update best
        best_idx = np.argmax(self.fitness_values)
        if self.fitness_values[best_idx] > self.best_fitness:
            self.best_individual = self.population[best_idx]
            self.best_fitness = self.fitness_values[best_idx]

        return improvements, trials_evaluated

    def _adapt_parameters(self, success_rate: float):
        """
        Adapt F and CR based on success rate.

        Args:
            success_rate: Fraction of successful mutations
        """
        if self.config.adaptive_f:
            self.current_f = DEOperators.adapt_f(
                current_f=self.current_f,
                success_rate=success_rate,
                f_min=self.config.f_min,
                f_max=self.config.f_max,
                learning_rate=self.config.adaptation_rate
            )

        if self.config.adaptive_cr:
            self.current_cr = DEOperators.adapt_cr(
                current_cr=self.current_cr,
                success_rate=success_rate,
                cr_min=self.config.cr_min,
                cr_max=self.config.cr_max,
                learning_rate=self.config.adaptation_rate
            )

    def _calculate_metrics(
        self,
        generation: int,
        improvements: int,
        trials_evaluated: int
    ) -> DEMetrics:
        """
        Calculate metrics for current generation.

        Args:
            generation: Current generation number
            improvements: Number of improvements this generation
            trials_evaluated: Number of trial vectors evaluated

        Returns:
            DEMetrics object
        """
        success_rate = improvements / max(trials_evaluated, 1)
        diversity = DEOperators.calculate_diversity(self.population)
        convergence_rate = DEOperators.calculate_convergence_rate(self.fitness_history)

        metrics = DEMetrics(
            generation=generation,
            best_fitness=float(self.best_fitness),
            average_fitness=float(np.mean(self.fitness_values)),
            worst_fitness=float(np.min(self.fitness_values)),
            population_diversity=diversity,
            convergence_rate=convergence_rate,
            success_rate=success_rate,
            trials_evaluated=trials_evaluated,
            improvements=improvements,
            current_f=self.current_f,
            current_cr=self.current_cr,
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
            logger.info(f"DE: Fitness threshold {self.config.fitness_threshold} reached")
            return True

        # Check stagnation
        if self.stagnation_counter >= self.config.patience:
            logger.info(f"DE: Stagnation detected after {self.stagnation_counter} generations")
            return True

        return False

    def run(self) -> DEResult:
        """
        Run DE optimization.

        Returns:
            DEResult with best solution and history
        """
        start_time = time.time()
        convergence_generation = None

        logger.info(
            f"Starting DE: {self.config.population_size} individuals, "
            f"{self.config.generations} generations, "
            f"strategy={self.config.mutation_strategy.value}"
        )

        try:
            for generation in range(self.config.generations):
                # Store previous best for stagnation detection
                prev_best = self.best_fitness

                # Evolve one generation
                improvements, trials_evaluated = self._evolve_generation(generation)

                # Calculate success rate
                success_rate = improvements / max(trials_evaluated, 1)

                # Adapt parameters if enabled
                self._adapt_parameters(success_rate)

                # Track stagnation
                if self.best_fitness > prev_best + self.config.min_improvement:
                    self.stagnation_counter = 0
                else:
                    self.stagnation_counter += 1

                # Calculate and store metrics
                metrics = self._calculate_metrics(generation, improvements, trials_evaluated)
                self.generation_metrics.append(metrics)
                self.fitness_history.append(self.best_fitness)
                self.avg_fitness_history.append(metrics.average_fitness)
                self.success_rate_history.append(success_rate)
                self.diversity_history.append(metrics.population_diversity)
                self.f_history.append(self.current_f)
                self.cr_history.append(self.current_cr)

                # Log progress periodically
                if generation % 10 == 0 or generation == self.config.generations - 1:
                    logger.debug(
                        f"DE Gen {generation}: best={self.best_fitness:.4f}, "
                        f"avg={metrics.average_fitness:.4f}, "
                        f"success={success_rate:.2%}, F={self.current_f:.3f}, CR={self.current_cr:.3f}"
                    )

                # Check convergence
                if self._check_convergence():
                    convergence_generation = generation
                    break

        except Exception as e:
            logger.error(f"DE error at generation {generation}: {str(e)}")
            self.errors.append(str(e))

        execution_time = time.time() - start_time

        # Create result
        result = DEResult(
            best_individual=np.array([self.best_individual]) if not isinstance(self.best_individual, np.ndarray) else self.best_individual,
            best_fitness=float(self.best_fitness),
            worst_fitness=float(np.min(self.fitness_values)),
            average_fitness=float(np.mean(self.fitness_values)),
            total_generations=len(self.fitness_history),
            converged=convergence_generation is not None,
            convergence_generation=convergence_generation,
            fitness_history=self.fitness_history,
            avg_fitness_history=self.avg_fitness_history,
            success_rate_history=self.success_rate_history,
            diversity_history=self.diversity_history,
            f_history=self.f_history,
            cr_history=self.cr_history,
            generation_metrics=self.generation_metrics,
            final_population=self.population.copy(),
            final_fitness=self.fitness_values.copy(),
            strategy_used=self.config.mutation_strategy.value,
            execution_time=execution_time,
            errors=self.errors,
            config=self.config
        )

        logger.info(
            f"DE complete: best={result.best_fitness:.4f}, "
            f"generations={result.total_generations}, "
            f"converged={result.converged}, "
            f"time={execution_time:.2f}s"
        )

        return result


def optimize_value_de(
    fitness_function: Callable[[float], float],
    bounds_min: float,
    bounds_max: float,
    config: Optional[DEConfig] = None,
    seed_values: Optional[np.ndarray] = None
) -> DEResult:
    """
    Convenience function to optimize a single value using DE.

    Args:
        fitness_function: Function that takes a value and returns fitness
        bounds_min: Lower bound
        bounds_max: Upper bound
        config: Optional DE configuration (uses defaults if not provided)
        seed_values: Optional values to seed population from

    Returns:
        DEResult with best solution
    """
    if config is None:
        config = DEConfig()

    optimizer = DifferentialEvolutionOptimizer(
        config=config,
        fitness_function=fitness_function,
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        seed_values=seed_values
    )

    return optimizer.run()
