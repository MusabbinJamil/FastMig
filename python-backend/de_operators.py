"""
DE (Differential Evolution) Operators Module

This module provides:
- DEMutationStrategy enum for all 6 mutation strategies
- DECrossoverType enum for crossover types
- DEConfig dataclass for configuration
- DEMetrics dataclass for generation metrics
- DEResult dataclass for final results
- Static operator functions for mutation, crossover, and selection
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class DEMutationStrategy(Enum):
    """
    DE mutation strategies.

    Naming convention: DE/base/num_differences
    - base: which vector is the base (rand, best, current)
    - num_differences: how many difference vectors are added
    """
    RAND_1 = "DE/rand/1"              # v = x_r1 + F*(x_r2 - x_r3)
    RAND_2 = "DE/rand/2"              # v = x_r1 + F*(x_r2 - x_r3) + F*(x_r4 - x_r5)
    BEST_1 = "DE/best/1"              # v = x_best + F*(x_r1 - x_r2)
    BEST_2 = "DE/best/2"              # v = x_best + F*(x_r1 - x_r2) + F*(x_r3 - x_r4)
    CURRENT_TO_BEST_1 = "DE/current-to-best/1"  # v = x_i + F*(x_best - x_i) + F*(x_r1 - x_r2)
    CURRENT_TO_RAND_1 = "DE/current-to-rand/1"  # v = x_i + F*(x_r1 - x_i) + F*(x_r2 - x_r3)


class DECrossoverType(Enum):
    """DE crossover types."""
    BINOMIAL = "binomial"       # Each dimension independent probability
    EXPONENTIAL = "exponential" # Contiguous dimensions crossover


class ConstraintHandling(Enum):
    """Methods for handling boundary constraints."""
    CLAMP = "clamp"       # Clamp to bounds
    REFLECT = "reflect"   # Reflect off bounds
    RANDOM = "random"     # Random position within bounds


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class DEConfig:
    """Configuration for Differential Evolution algorithm."""

    # Population parameters
    population_size: int = 30
    generations: int = 100

    # DE parameters
    scale_factor: float = 0.8         # F (mutation scale factor, typically [0.4, 1.0])
    crossover_rate: float = 0.9       # CR (crossover probability, typically [0.0, 1.0])

    # Strategy selection
    mutation_strategy: DEMutationStrategy = DEMutationStrategy.RAND_1
    crossover_type: DECrossoverType = DECrossoverType.BINOMIAL

    # Adaptive parameters (self-adapting F and CR)
    adaptive_f: bool = False
    adaptive_cr: bool = False
    f_min: float = 0.1
    f_max: float = 1.0
    cr_min: float = 0.1
    cr_max: float = 1.0

    # Learning rate for adaptation
    adaptation_rate: float = 0.1  # How quickly F/CR adapt

    # Constraint handling
    constraint_handling: ConstraintHandling = ConstraintHandling.CLAMP

    # Early stopping
    early_stopping: bool = True
    patience: int = 10               # Generations without improvement
    min_improvement: float = 1e-6    # Minimum improvement threshold
    fitness_threshold: float = 0.95  # Stop if best fitness exceeds this

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration parameters."""
        errors = []

        if self.population_size < 4:
            errors.append("population_size must be at least 4 for DE")
        if self.generations < 1:
            errors.append("generations must be at least 1")
        if not 0.0 <= self.scale_factor <= 2.0:
            errors.append("scale_factor (F) should be between 0.0 and 2.0")
        if not 0.0 <= self.crossover_rate <= 1.0:
            errors.append("crossover_rate (CR) must be between 0.0 and 1.0")
        if self.f_min > self.f_max:
            errors.append("f_min must be <= f_max")
        if self.cr_min > self.cr_max:
            errors.append("cr_min must be <= cr_max")

        # Strategy-specific validation
        strategy = self.mutation_strategy
        if strategy == DEMutationStrategy.RAND_2 and self.population_size < 6:
            errors.append("population_size must be at least 6 for DE/rand/2")
        if strategy == DEMutationStrategy.BEST_2 and self.population_size < 5:
            errors.append("population_size must be at least 5 for DE/best/2")

        return len(errors) == 0, errors

    def __str__(self) -> str:
        return (
            f"DEConfig(pop={self.population_size}, gen={self.generations}, "
            f"F={self.scale_factor}, CR={self.crossover_rate}, "
            f"strategy={self.mutation_strategy.value})"
        )


# ============================================================================
# METRICS
# ============================================================================

@dataclass
class DEMetrics:
    """Metrics for a single DE generation."""

    generation: int
    best_fitness: float
    average_fitness: float
    worst_fitness: float

    # Population statistics
    population_diversity: float = 0.0   # Std of population values
    convergence_rate: float = 0.0       # Rate of improvement

    # DE-specific metrics
    success_rate: float = 0.0           # Fraction of successful mutations
    trials_evaluated: int = 0           # Number of trial vectors evaluated
    improvements: int = 0               # Number of improvements this generation

    # Current parameters (for adaptive DE)
    current_f: float = 0.8
    current_cr: float = 0.9

    # Stagnation tracking
    stagnation_counter: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'generation': self.generation,
            'best_fitness': float(self.best_fitness),
            'average_fitness': float(self.average_fitness),
            'worst_fitness': float(self.worst_fitness),
            'population_diversity': float(self.population_diversity),
            'convergence_rate': float(self.convergence_rate),
            'success_rate': float(self.success_rate),
            'trials_evaluated': self.trials_evaluated,
            'improvements': self.improvements,
            'current_f': float(self.current_f),
            'current_cr': float(self.current_cr),
            'stagnation_counter': self.stagnation_counter,
            'method': 'DE'
        }

    def __str__(self) -> str:
        return (
            f"Gen {self.generation}: best={self.best_fitness:.4f}, "
            f"avg={self.average_fitness:.4f}, success={self.success_rate:.2%}"
        )


# ============================================================================
# RESULT
# ============================================================================

@dataclass
class DEResult:
    """Final result from DE optimization."""

    best_individual: np.ndarray
    best_fitness: float
    worst_fitness: float
    average_fitness: float

    # Execution info
    total_generations: int
    converged: bool
    convergence_generation: Optional[int] = None

    # History
    fitness_history: List[float] = field(default_factory=list)  # Best fitness per generation
    avg_fitness_history: List[float] = field(default_factory=list)
    success_rate_history: List[float] = field(default_factory=list)
    diversity_history: List[float] = field(default_factory=list)
    f_history: List[float] = field(default_factory=list)    # For adaptive DE
    cr_history: List[float] = field(default_factory=list)   # For adaptive DE
    generation_metrics: List[DEMetrics] = field(default_factory=list)

    # Final population
    final_population: Optional[np.ndarray] = None
    final_fitness: Optional[np.ndarray] = None

    # Strategy used
    strategy_used: str = ""

    # Timing
    execution_time: float = 0.0

    # Errors
    errors: List[str] = field(default_factory=list)

    # Config
    config: Optional[DEConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'best_individual': self.best_individual.tolist() if isinstance(self.best_individual, np.ndarray) else self.best_individual,
            'best_fitness': float(self.best_fitness),
            'worst_fitness': float(self.worst_fitness),
            'average_fitness': float(self.average_fitness),
            'total_generations': self.total_generations,
            'converged': self.converged,
            'convergence_generation': self.convergence_generation,
            'fitness_history': [float(f) for f in self.fitness_history],
            'avg_fitness_history': [float(f) for f in self.avg_fitness_history],
            'success_rate_history': [float(s) for s in self.success_rate_history],
            'diversity_history': [float(d) for d in self.diversity_history],
            'f_history': [float(f) for f in self.f_history],
            'cr_history': [float(c) for c in self.cr_history],
            'generation_metrics': [m.to_dict() for m in self.generation_metrics],
            'strategy_used': self.strategy_used,
            'execution_time': self.execution_time,
            'errors': self.errors,
            'method': 'DE'
        }


# ============================================================================
# OPERATOR FUNCTIONS
# ============================================================================

class DEOperators:
    """Static methods for DE operations."""

    # -------------------------------------------------------------------------
    # Mutation Strategies
    # -------------------------------------------------------------------------

    @staticmethod
    def mutate_rand_1(
        population: np.ndarray,
        fitness: np.ndarray,
        target_idx: int,
        F: float
    ) -> Tuple[float, Dict[str, Any]]:
        """
        DE/rand/1 mutation strategy.

        v = x_r1 + F * (x_r2 - x_r3)

        Args:
            population: Current population array
            fitness: Fitness values (not used, for interface consistency)
            target_idx: Index of target individual
            F: Scale factor

        Returns:
            Tuple of (mutant value, stats dict)
        """
        pop_size = len(population)

        # Select 3 distinct random indices, different from target
        candidates = [i for i in range(pop_size) if i != target_idx]
        r1, r2, r3 = np.random.choice(candidates, 3, replace=False)

        # Mutation
        mutant = population[r1] + F * (population[r2] - population[r3])

        stats = {
            'base_idx': r1,
            'diff_indices': [r2, r3],
            'base_value': float(population[r1])
        }

        return float(mutant), stats

    @staticmethod
    def mutate_rand_2(
        population: np.ndarray,
        fitness: np.ndarray,
        target_idx: int,
        F: float
    ) -> Tuple[float, Dict[str, Any]]:
        """
        DE/rand/2 mutation strategy.

        v = x_r1 + F * (x_r2 - x_r3) + F * (x_r4 - x_r5)

        Uses two difference vectors for more exploration.
        """
        pop_size = len(population)

        # Select 5 distinct random indices
        candidates = [i for i in range(pop_size) if i != target_idx]
        r1, r2, r3, r4, r5 = np.random.choice(candidates, 5, replace=False)

        # Mutation with two difference vectors
        mutant = (
            population[r1] +
            F * (population[r2] - population[r3]) +
            F * (population[r4] - population[r5])
        )

        stats = {
            'base_idx': r1,
            'diff_indices': [r2, r3, r4, r5],
            'base_value': float(population[r1])
        }

        return float(mutant), stats

    @staticmethod
    def mutate_best_1(
        population: np.ndarray,
        fitness: np.ndarray,
        target_idx: int,
        F: float
    ) -> Tuple[float, Dict[str, Any]]:
        """
        DE/best/1 mutation strategy.

        v = x_best + F * (x_r1 - x_r2)

        Uses best individual as base - more exploitative.
        """
        pop_size = len(population)
        best_idx = np.argmax(fitness)

        # Select 2 distinct random indices, different from target and best
        candidates = [i for i in range(pop_size) if i not in (target_idx, best_idx)]
        if len(candidates) < 2:
            candidates = [i for i in range(pop_size) if i != target_idx]
        r1, r2 = np.random.choice(candidates, 2, replace=False)

        # Mutation with best as base
        mutant = population[best_idx] + F * (population[r1] - population[r2])

        stats = {
            'base_idx': best_idx,
            'diff_indices': [r1, r2],
            'base_value': float(population[best_idx]),
            'is_best': True
        }

        return float(mutant), stats

    @staticmethod
    def mutate_best_2(
        population: np.ndarray,
        fitness: np.ndarray,
        target_idx: int,
        F: float
    ) -> Tuple[float, Dict[str, Any]]:
        """
        DE/best/2 mutation strategy.

        v = x_best + F * (x_r1 - x_r2) + F * (x_r3 - x_r4)

        Uses best as base with two difference vectors.
        """
        pop_size = len(population)
        best_idx = np.argmax(fitness)

        # Select 4 distinct random indices
        candidates = [i for i in range(pop_size) if i not in (target_idx, best_idx)]
        if len(candidates) < 4:
            candidates = [i for i in range(pop_size) if i != target_idx]
        r1, r2, r3, r4 = np.random.choice(candidates, min(4, len(candidates)), replace=len(candidates) < 4)

        # Mutation
        mutant = (
            population[best_idx] +
            F * (population[r1] - population[r2]) +
            F * (population[r3] - population[r4])
        )

        stats = {
            'base_idx': best_idx,
            'diff_indices': [r1, r2, r3, r4],
            'base_value': float(population[best_idx]),
            'is_best': True
        }

        return float(mutant), stats

    @staticmethod
    def mutate_current_to_best_1(
        population: np.ndarray,
        fitness: np.ndarray,
        target_idx: int,
        F: float
    ) -> Tuple[float, Dict[str, Any]]:
        """
        DE/current-to-best/1 mutation strategy.

        v = x_i + F * (x_best - x_i) + F * (x_r1 - x_r2)

        Combines current individual movement toward best with exploration.
        """
        pop_size = len(population)
        best_idx = np.argmax(fitness)

        # Select 2 distinct random indices
        candidates = [i for i in range(pop_size) if i not in (target_idx, best_idx)]
        if len(candidates) < 2:
            candidates = [i for i in range(pop_size) if i != target_idx]
        r1, r2 = np.random.choice(candidates, 2, replace=False)

        # Mutation: move from current toward best, plus random difference
        mutant = (
            population[target_idx] +
            F * (population[best_idx] - population[target_idx]) +
            F * (population[r1] - population[r2])
        )

        stats = {
            'base_idx': target_idx,
            'best_idx': best_idx,
            'diff_indices': [r1, r2],
            'base_value': float(population[target_idx]),
            'strategy': 'current-to-best'
        }

        return float(mutant), stats

    @staticmethod
    def mutate_current_to_rand_1(
        population: np.ndarray,
        fitness: np.ndarray,
        target_idx: int,
        F: float
    ) -> Tuple[float, Dict[str, Any]]:
        """
        DE/current-to-rand/1 mutation strategy.

        v = x_i + F * (x_r1 - x_i) + F * (x_r2 - x_r3)

        Similar to current-to-best but uses random individual instead of best.
        More exploratory than current-to-best.
        """
        pop_size = len(population)

        # Select 3 distinct random indices
        candidates = [i for i in range(pop_size) if i != target_idx]
        r1, r2, r3 = np.random.choice(candidates, 3, replace=False)

        # Mutation: move from current toward r1, plus random difference
        mutant = (
            population[target_idx] +
            F * (population[r1] - population[target_idx]) +
            F * (population[r2] - population[r3])
        )

        stats = {
            'base_idx': target_idx,
            'direction_idx': r1,
            'diff_indices': [r2, r3],
            'base_value': float(population[target_idx]),
            'strategy': 'current-to-rand'
        }

        return float(mutant), stats

    @staticmethod
    def apply_mutation(
        strategy: DEMutationStrategy,
        population: np.ndarray,
        fitness: np.ndarray,
        target_idx: int,
        F: float
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Apply mutation based on selected strategy.

        Args:
            strategy: The mutation strategy to use
            population: Current population
            fitness: Fitness values
            target_idx: Index of target individual
            F: Scale factor

        Returns:
            Tuple of (mutant value, stats dict)
        """
        strategy_map = {
            DEMutationStrategy.RAND_1: DEOperators.mutate_rand_1,
            DEMutationStrategy.RAND_2: DEOperators.mutate_rand_2,
            DEMutationStrategy.BEST_1: DEOperators.mutate_best_1,
            DEMutationStrategy.BEST_2: DEOperators.mutate_best_2,
            DEMutationStrategy.CURRENT_TO_BEST_1: DEOperators.mutate_current_to_best_1,
            DEMutationStrategy.CURRENT_TO_RAND_1: DEOperators.mutate_current_to_rand_1,
        }

        mutation_func = strategy_map.get(strategy, DEOperators.mutate_rand_1)
        return mutation_func(population, fitness, target_idx, F)

    # -------------------------------------------------------------------------
    # Crossover Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def crossover_binomial(
        target: float,
        mutant: float,
        CR: float
    ) -> Tuple[float, bool]:
        """
        Binomial crossover.

        Each dimension is taken from mutant with probability CR,
        otherwise from target.

        For 1D case, returns mutant with probability CR, otherwise target.

        Args:
            target: Target (current) value
            mutant: Mutant value
            CR: Crossover rate

        Returns:
            Tuple of (trial value, was_from_mutant)
        """
        if np.random.random() < CR:
            return mutant, True
        else:
            return target, False

    @staticmethod
    def crossover_exponential(
        target: float,
        mutant: float,
        CR: float
    ) -> Tuple[float, bool]:
        """
        Exponential crossover.

        For multi-dimensional problems, takes contiguous dimensions from mutant.
        For 1D, equivalent to binomial.

        Args:
            target: Target (current) value
            mutant: Mutant value
            CR: Crossover rate

        Returns:
            Tuple of (trial value, was_from_mutant)
        """
        # For 1D optimization, exponential is same as binomial
        return DEOperators.crossover_binomial(target, mutant, CR)

    @staticmethod
    def apply_crossover(
        crossover_type: DECrossoverType,
        target: float,
        mutant: float,
        CR: float
    ) -> Tuple[float, bool]:
        """
        Apply crossover based on selected type.

        Args:
            crossover_type: Type of crossover
            target: Target value
            mutant: Mutant value
            CR: Crossover rate

        Returns:
            Tuple of (trial value, was_from_mutant)
        """
        if crossover_type == DECrossoverType.EXPONENTIAL:
            return DEOperators.crossover_exponential(target, mutant, CR)
        else:
            return DEOperators.crossover_binomial(target, mutant, CR)

    # -------------------------------------------------------------------------
    # Selection Function
    # -------------------------------------------------------------------------

    @staticmethod
    def greedy_selection(
        target_value: float,
        target_fitness: float,
        trial_value: float,
        trial_fitness: float
    ) -> Tuple[float, float, bool]:
        """
        Greedy selection: keep better individual.

        Args:
            target_value: Current individual value
            target_fitness: Current fitness
            trial_value: Trial individual value
            trial_fitness: Trial fitness

        Returns:
            Tuple of (selected value, selected fitness, trial_was_better)
        """
        if trial_fitness > target_fitness:
            return trial_value, trial_fitness, True
        else:
            return target_value, target_fitness, False

    # -------------------------------------------------------------------------
    # Constraint Handling
    # -------------------------------------------------------------------------

    @staticmethod
    def apply_constraints(
        value: float,
        bounds_min: float,
        bounds_max: float,
        handling: ConstraintHandling = ConstraintHandling.CLAMP
    ) -> float:
        """
        Apply boundary constraints to a value.

        Args:
            value: Value to constrain
            bounds_min: Lower bound
            bounds_max: Upper bound
            handling: Constraint handling method

        Returns:
            Constrained value
        """
        if handling == ConstraintHandling.CLAMP:
            return np.clip(value, bounds_min, bounds_max)

        elif handling == ConstraintHandling.REFLECT:
            if value < bounds_min:
                return 2 * bounds_min - value
            elif value > bounds_max:
                return 2 * bounds_max - value
            return value

        elif handling == ConstraintHandling.RANDOM:
            if value < bounds_min or value > bounds_max:
                return np.random.uniform(bounds_min, bounds_max)
            return value

        else:
            return np.clip(value, bounds_min, bounds_max)

    # -------------------------------------------------------------------------
    # Adaptive Parameter Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def adapt_f(
        current_f: float,
        success_rate: float,
        f_min: float = 0.1,
        f_max: float = 1.0,
        learning_rate: float = 0.1
    ) -> float:
        """
        Adapt F based on success rate.

        If success rate is high, F can be reduced (exploitation).
        If success rate is low, F should be increased (exploration).

        Args:
            current_f: Current F value
            success_rate: Fraction of successful mutations last generation
            f_min: Minimum F value
            f_max: Maximum F value
            learning_rate: How fast to adapt

        Returns:
            Adapted F value
        """
        target_success = 0.2  # Target 20% success rate

        if success_rate > target_success:
            # Too many successes - reduce F for finer search
            new_f = current_f * (1 - learning_rate)
        elif success_rate < target_success * 0.5:
            # Too few successes - increase F for more exploration
            new_f = current_f * (1 + learning_rate)
        else:
            # In acceptable range - keep current
            new_f = current_f

        return np.clip(new_f, f_min, f_max)

    @staticmethod
    def adapt_cr(
        current_cr: float,
        success_rate: float,
        cr_min: float = 0.1,
        cr_max: float = 1.0,
        learning_rate: float = 0.1
    ) -> float:
        """
        Adapt CR based on success rate.

        Higher CR means more components from mutant vector.

        Args:
            current_cr: Current CR value
            success_rate: Fraction of successful mutations
            cr_min: Minimum CR value
            cr_max: Maximum CR value
            learning_rate: How fast to adapt

        Returns:
            Adapted CR value
        """
        target_success = 0.2

        if success_rate > target_success:
            # Good success rate - slightly reduce CR
            new_cr = current_cr * (1 - learning_rate * 0.5)
        elif success_rate < target_success * 0.5:
            # Low success rate - increase CR to take more from mutant
            new_cr = current_cr * (1 + learning_rate)
        else:
            new_cr = current_cr

        return np.clip(new_cr, cr_min, cr_max)

    # -------------------------------------------------------------------------
    # Utility Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_diversity(population: np.ndarray) -> float:
        """Calculate population diversity (standard deviation)."""
        if len(population) == 0:
            return 0.0
        return float(np.std(population))

    @staticmethod
    def calculate_convergence_rate(
        fitness_history: List[float],
        window_size: int = 5
    ) -> float:
        """Calculate rate of fitness improvement."""
        if len(fitness_history) < 2:
            return 0.0

        window = min(window_size, len(fitness_history))
        recent = fitness_history[-window:]

        if len(recent) < 2:
            return 0.0

        x = np.arange(len(recent))
        slope = np.polyfit(x, recent, 1)[0]
        return float(slope)

    @staticmethod
    def initialize_population(
        pop_size: int,
        bounds_min: float,
        bounds_max: float,
        seed_values: Optional[np.ndarray] = None,
        seed_ratio: float = 0.3
    ) -> np.ndarray:
        """
        Initialize DE population.

        Args:
            pop_size: Population size
            bounds_min: Lower bound
            bounds_max: Upper bound
            seed_values: Optional values to seed from
            seed_ratio: Fraction to seed from provided values

        Returns:
            Initial population array
        """
        if seed_values is not None and len(seed_values) > 0:
            n_seeded = int(pop_size * seed_ratio)
            n_random = pop_size - n_seeded

            # Seeded individuals with noise
            range_size = bounds_max - bounds_min
            seeded = np.random.choice(seed_values, n_seeded)
            noise = np.random.normal(0, range_size * 0.1, n_seeded)
            seeded = np.clip(seeded + noise, bounds_min, bounds_max)

            # Random individuals
            random = np.random.uniform(bounds_min, bounds_max, n_random)

            return np.concatenate([seeded, random])
        else:
            return np.random.uniform(bounds_min, bounds_max, pop_size)
