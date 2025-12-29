"""
ES (Evolution Strategy) Operators Module

This module provides:
- ESSelectionType enum for selection types (plus, comma)
- ESRecombinationType enum for recombination types
- ESConfig dataclass for configuration
- ESMetrics dataclass for generation metrics
- ESResult dataclass for final results
- Static operator functions for mutation, recombination, and selection
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class ESSelectionType(Enum):
    """
    ES selection types.

    - PLUS: (μ+λ) selection - parents and offspring compete
    - COMMA: (μ,λ) selection - only offspring compete (requires λ >= μ)
    """
    PLUS = "plus"       # (μ+λ) - parents and offspring compete
    COMMA = "comma"     # (μ,λ) - only offspring compete


class ESRecombinationType(Enum):
    """
    ES recombination types.

    - DISCRETE: Each component randomly chosen from one parent
    - INTERMEDIATE: Each component is average of parents
    - GLOBAL: Components from all parents (global discrete)
    """
    DISCRETE = "discrete"           # Random parent for each component
    INTERMEDIATE = "intermediate"   # Average of parents
    GLOBAL = "global"              # Global discrete (all parents)


class ConstraintHandling(Enum):
    """Methods for handling boundary constraints."""
    CLAMP = "clamp"       # Clamp to bounds
    REFLECT = "reflect"   # Reflect off bounds
    RANDOM = "random"     # Random position within bounds


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ESConfig:
    """Configuration for Evolution Strategy algorithm."""

    # Population parameters
    mu: int = 15              # Parent population size (μ)
    lambda_: int = 100        # Offspring population size (λ)
    generations: int = 100

    # Selection
    selection_type: ESSelectionType = ESSelectionType.PLUS

    # Recombination
    recombination_type: ESRecombinationType = ESRecombinationType.INTERMEDIATE
    rho: int = 2              # Number of parents for recombination

    # Mutation
    mutation_rate: float = 1.0        # Probability of mutation (typically 1.0 in ES)
    initial_sigma: float = 0.3        # Initial step size (σ)
    sigma_min: float = 1e-10          # Minimum step size
    sigma_max: float = 1.0            # Maximum step size

    # Self-adaptive mutation
    self_adaptive: bool = True        # Enable self-adaptive step sizes
    tau: float = 0.0                  # Learning rate for global step size (0 = auto-calculate)
    tau_prime: float = 0.0            # Learning rate for local step size (0 = auto-calculate)

    # Constraint handling
    constraint_handling: ConstraintHandling = ConstraintHandling.CLAMP

    # Early stopping
    early_stopping: bool = True
    patience: int = 15                # Generations without improvement
    min_improvement: float = 1e-6     # Minimum improvement threshold
    fitness_threshold: float = 0.95   # Stop if best fitness exceeds this

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration parameters."""
        errors = []

        if self.mu < 1:
            errors.append("mu (parent population) must be at least 1")
        if self.lambda_ < 1:
            errors.append("lambda (offspring population) must be at least 1")
        if self.selection_type == ESSelectionType.COMMA and self.lambda_ < self.mu:
            errors.append("For comma selection, lambda must be >= mu")
        if self.generations < 1:
            errors.append("generations must be at least 1")
        if self.rho < 1:
            errors.append("rho (parent count for recombination) must be at least 1")
        if self.rho > self.mu:
            errors.append("rho cannot exceed mu")
        if not 0.0 <= self.mutation_rate <= 1.0:
            errors.append("mutation_rate must be between 0.0 and 1.0")
        if self.initial_sigma <= 0:
            errors.append("initial_sigma must be positive")
        if self.sigma_min <= 0:
            errors.append("sigma_min must be positive")
        if self.sigma_min > self.sigma_max:
            errors.append("sigma_min must be <= sigma_max")

        return len(errors) == 0, errors

    def get_tau_values(self, n_dimensions: int = 1) -> Tuple[float, float]:
        """
        Get tau and tau_prime values, calculating defaults if not set.

        Standard ES uses:
        - tau = 1 / sqrt(2 * n)
        - tau_prime = 1 / sqrt(2 * sqrt(n))
        """
        n = max(1, n_dimensions)

        tau = self.tau if self.tau > 0 else 1.0 / np.sqrt(2 * n)
        tau_prime = self.tau_prime if self.tau_prime > 0 else 1.0 / np.sqrt(2 * np.sqrt(n))

        return tau, tau_prime

    def __str__(self) -> str:
        return (
            f"ESConfig(μ={self.mu}, λ={self.lambda_}, gen={self.generations}, "
            f"selection={self.selection_type.value}, σ₀={self.initial_sigma})"
        )


# ============================================================================
# METRICS
# ============================================================================

@dataclass
class ESMetrics:
    """Metrics for a single ES generation."""

    generation: int
    best_fitness: float
    average_fitness: float
    worst_fitness: float

    # Population statistics
    population_diversity: float = 0.0   # Std of population values
    convergence_rate: float = 0.0       # Rate of improvement

    # ES-specific metrics
    offspring_generated: int = 0        # Number of offspring this generation
    parents_selected: int = 0           # Number of parents selected
    average_sigma: float = 0.0          # Average step size
    sigma_std: float = 0.0              # Std of step sizes
    min_sigma: float = 0.0              # Minimum step size
    max_sigma: float = 0.0              # Maximum step size

    # Success tracking
    successful_mutations: int = 0       # Offspring better than worst parent
    success_rate: float = 0.0           # Fraction of successful mutations

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
            'offspring_generated': self.offspring_generated,
            'parents_selected': self.parents_selected,
            'average_sigma': float(self.average_sigma),
            'sigma_std': float(self.sigma_std),
            'min_sigma': float(self.min_sigma),
            'max_sigma': float(self.max_sigma),
            'successful_mutations': self.successful_mutations,
            'success_rate': float(self.success_rate),
            'stagnation_counter': self.stagnation_counter,
            'method': 'ES'
        }

    def __str__(self) -> str:
        return (
            f"Gen {self.generation}: best={self.best_fitness:.4f}, "
            f"avg={self.average_fitness:.4f}, σ={self.average_sigma:.4f}"
        )


# ============================================================================
# RESULT
# ============================================================================

@dataclass
class ESResult:
    """Final result from ES optimization."""

    best_individual: np.ndarray
    best_fitness: float
    worst_fitness: float
    average_fitness: float

    # Strategy parameters
    best_sigma: float = 0.0

    # Execution info
    total_generations: int = 0
    converged: bool = False
    convergence_generation: Optional[int] = None

    # History
    fitness_history: List[float] = field(default_factory=list)
    avg_fitness_history: List[float] = field(default_factory=list)
    sigma_history: List[float] = field(default_factory=list)
    diversity_history: List[float] = field(default_factory=list)
    generation_metrics: List[ESMetrics] = field(default_factory=list)

    # Final population
    final_population: Optional[np.ndarray] = None
    final_sigmas: Optional[np.ndarray] = None
    final_fitness: Optional[np.ndarray] = None

    # Strategy info
    selection_type_used: str = ""
    recombination_type_used: str = ""

    # Timing
    execution_time: float = 0.0

    # Errors
    errors: List[str] = field(default_factory=list)

    # Config
    config: Optional[ESConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'best_individual': self.best_individual.tolist() if isinstance(self.best_individual, np.ndarray) else self.best_individual,
            'best_fitness': float(self.best_fitness),
            'worst_fitness': float(self.worst_fitness),
            'average_fitness': float(self.average_fitness),
            'best_sigma': float(self.best_sigma),
            'total_generations': self.total_generations,
            'converged': self.converged,
            'convergence_generation': self.convergence_generation,
            'fitness_history': [float(f) for f in self.fitness_history],
            'avg_fitness_history': [float(f) for f in self.avg_fitness_history],
            'sigma_history': [float(s) for s in self.sigma_history],
            'diversity_history': [float(d) for d in self.diversity_history],
            'generation_metrics': [m.to_dict() for m in self.generation_metrics],
            'selection_type_used': self.selection_type_used,
            'recombination_type_used': self.recombination_type_used,
            'execution_time': self.execution_time,
            'errors': self.errors,
            'method': 'ES'
        }


# ============================================================================
# OPERATOR FUNCTIONS
# ============================================================================

class ESOperators:
    """Static methods for ES operations."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    @staticmethod
    def initialize_population(
        mu: int,
        bounds_min: float,
        bounds_max: float,
        initial_sigma: float,
        seed_values: Optional[np.ndarray] = None,
        seed_ratio: float = 0.3
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Initialize ES population with values and strategy parameters (sigmas).

        Args:
            mu: Parent population size
            bounds_min: Lower bound
            bounds_max: Upper bound
            initial_sigma: Initial step size
            seed_values: Optional values to seed from
            seed_ratio: Fraction to seed from provided values

        Returns:
            Tuple of (population values, sigma values)
        """
        if seed_values is not None and len(seed_values) > 0:
            n_seeded = int(mu * seed_ratio)
            n_random = mu - n_seeded

            # Seeded individuals with noise
            range_size = bounds_max - bounds_min
            seeded = np.random.choice(seed_values, n_seeded)
            noise = np.random.normal(0, range_size * 0.1, n_seeded)
            seeded = np.clip(seeded + noise, bounds_min, bounds_max)

            # Random individuals
            random = np.random.uniform(bounds_min, bounds_max, n_random)

            population = np.concatenate([seeded, random])
        else:
            population = np.random.uniform(bounds_min, bounds_max, mu)

        # Initialize sigmas
        sigmas = np.full(mu, initial_sigma)

        return population, sigmas

    # -------------------------------------------------------------------------
    # Recombination Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def recombine_discrete(
        parents: np.ndarray,
        parent_sigmas: np.ndarray
    ) -> Tuple[float, float]:
        """
        Discrete recombination: randomly choose from parents.

        Args:
            parents: Parent values
            parent_sigmas: Parent step sizes

        Returns:
            Tuple of (offspring value, offspring sigma)
        """
        idx = np.random.randint(0, len(parents))
        return float(parents[idx]), float(parent_sigmas[idx])

    @staticmethod
    def recombine_intermediate(
        parents: np.ndarray,
        parent_sigmas: np.ndarray
    ) -> Tuple[float, float]:
        """
        Intermediate recombination: average of parents.

        Args:
            parents: Parent values
            parent_sigmas: Parent step sizes

        Returns:
            Tuple of (offspring value, offspring sigma)
        """
        return float(np.mean(parents)), float(np.mean(parent_sigmas))

    @staticmethod
    def recombine_global_discrete(
        population: np.ndarray,
        sigmas: np.ndarray,
        rho: int
    ) -> Tuple[float, float]:
        """
        Global discrete recombination: random parents from entire population.

        Args:
            population: Entire population
            sigmas: All step sizes
            rho: Number of parents to use

        Returns:
            Tuple of (offspring value, offspring sigma)
        """
        indices = np.random.choice(len(population), rho, replace=False)
        return ESOperators.recombine_discrete(
            population[indices],
            sigmas[indices]
        )

    @staticmethod
    def apply_recombination(
        recomb_type: ESRecombinationType,
        population: np.ndarray,
        sigmas: np.ndarray,
        fitness: np.ndarray,
        rho: int
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Apply recombination to create offspring base.

        Args:
            recomb_type: Type of recombination
            population: Current population
            sigmas: Current step sizes
            fitness: Fitness values
            rho: Number of parents

        Returns:
            Tuple of (offspring value, offspring sigma, stats dict)
        """
        # Select best parents for recombination
        sorted_indices = np.argsort(fitness)[::-1]  # Best first
        parent_indices = sorted_indices[:min(rho, len(population))]

        parents = population[parent_indices]
        parent_sigmas = sigmas[parent_indices]

        if recomb_type == ESRecombinationType.DISCRETE:
            value, sigma = ESOperators.recombine_discrete(parents, parent_sigmas)
        elif recomb_type == ESRecombinationType.INTERMEDIATE:
            value, sigma = ESOperators.recombine_intermediate(parents, parent_sigmas)
        elif recomb_type == ESRecombinationType.GLOBAL:
            value, sigma = ESOperators.recombine_global_discrete(population, sigmas, rho)
        else:
            value, sigma = ESOperators.recombine_intermediate(parents, parent_sigmas)

        stats = {
            'parent_indices': parent_indices.tolist(),
            'recombination_type': recomb_type.value
        }

        return value, sigma, stats

    # -------------------------------------------------------------------------
    # Mutation Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def mutate_gaussian(
        value: float,
        sigma: float,
        bounds_min: float,
        bounds_max: float,
        constraint_handling: ConstraintHandling = ConstraintHandling.CLAMP
    ) -> float:
        """
        Apply Gaussian mutation.

        Args:
            value: Value to mutate
            sigma: Step size
            bounds_min: Lower bound
            bounds_max: Upper bound
            constraint_handling: How to handle constraint violations

        Returns:
            Mutated value
        """
        mutated = value + sigma * np.random.randn()
        return ESOperators.apply_constraints(mutated, bounds_min, bounds_max, constraint_handling)

    @staticmethod
    def mutate_sigma_self_adaptive(
        sigma: float,
        tau: float,
        tau_prime: float,
        sigma_min: float,
        sigma_max: float
    ) -> float:
        """
        Self-adaptive mutation of step size.

        σ' = σ * exp(τ' * N(0,1) + τ * N_i(0,1))

        For 1D case, tau_prime term dominates.

        Args:
            sigma: Current step size
            tau: Local learning rate
            tau_prime: Global learning rate
            sigma_min: Minimum step size
            sigma_max: Maximum step size

        Returns:
            Mutated step size
        """
        # Global perturbation (same for all dimensions in multi-D)
        global_factor = tau_prime * np.random.randn()
        # Local perturbation (different for each dimension)
        local_factor = tau * np.random.randn()

        new_sigma = sigma * np.exp(global_factor + local_factor)
        return np.clip(new_sigma, sigma_min, sigma_max)

    @staticmethod
    def apply_mutation(
        value: float,
        sigma: float,
        config: ESConfig,
        bounds_min: float,
        bounds_max: float
    ) -> Tuple[float, float, Dict[str, Any]]:
        """
        Apply ES mutation (mutate both value and sigma if self-adaptive).

        Args:
            value: Value to mutate
            sigma: Current step size
            config: ES configuration
            bounds_min: Lower bound
            bounds_max: Upper bound

        Returns:
            Tuple of (mutated value, mutated sigma, stats dict)
        """
        # Get tau values
        tau, tau_prime = config.get_tau_values(1)

        # Mutate sigma first if self-adaptive
        if config.self_adaptive:
            new_sigma = ESOperators.mutate_sigma_self_adaptive(
                sigma=sigma,
                tau=tau,
                tau_prime=tau_prime,
                sigma_min=config.sigma_min,
                sigma_max=config.sigma_max
            )
        else:
            new_sigma = sigma

        # Mutate value
        if np.random.random() < config.mutation_rate:
            new_value = ESOperators.mutate_gaussian(
                value=value,
                sigma=new_sigma,
                bounds_min=bounds_min,
                bounds_max=bounds_max,
                constraint_handling=config.constraint_handling
            )
        else:
            new_value = value

        stats = {
            'original_sigma': sigma,
            'new_sigma': new_sigma,
            'sigma_change': new_sigma - sigma,
            'value_change': new_value - value,
            'self_adaptive': config.self_adaptive
        }

        return new_value, new_sigma, stats

    # -------------------------------------------------------------------------
    # Selection Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def select_plus(
        parents: np.ndarray,
        parent_sigmas: np.ndarray,
        parent_fitness: np.ndarray,
        offspring: np.ndarray,
        offspring_sigmas: np.ndarray,
        offspring_fitness: np.ndarray,
        mu: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        (μ+λ) selection: select best μ from parents + offspring.

        Args:
            parents: Parent values
            parent_sigmas: Parent step sizes
            parent_fitness: Parent fitness values
            offspring: Offspring values
            offspring_sigmas: Offspring step sizes
            offspring_fitness: Offspring fitness values
            mu: Number to select

        Returns:
            Tuple of (selected values, selected sigmas, selected fitness, stats)
        """
        # Combine parents and offspring
        all_values = np.concatenate([parents, offspring])
        all_sigmas = np.concatenate([parent_sigmas, offspring_sigmas])
        all_fitness = np.concatenate([parent_fitness, offspring_fitness])

        # Select best μ
        sorted_indices = np.argsort(all_fitness)[::-1][:mu]

        selected_values = all_values[sorted_indices]
        selected_sigmas = all_sigmas[sorted_indices]
        selected_fitness = all_fitness[sorted_indices]

        # Count how many offspring were selected
        n_offspring_selected = np.sum(sorted_indices >= len(parents))

        stats = {
            'selection_type': 'plus',
            'total_candidates': len(all_values),
            'offspring_selected': int(n_offspring_selected),
            'parents_retained': mu - int(n_offspring_selected)
        }

        return selected_values, selected_sigmas, selected_fitness, stats

    @staticmethod
    def select_comma(
        offspring: np.ndarray,
        offspring_sigmas: np.ndarray,
        offspring_fitness: np.ndarray,
        mu: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        (μ,λ) selection: select best μ from offspring only.

        Requires λ >= μ.

        Args:
            offspring: Offspring values
            offspring_sigmas: Offspring step sizes
            offspring_fitness: Offspring fitness values
            mu: Number to select

        Returns:
            Tuple of (selected values, selected sigmas, selected fitness, stats)
        """
        if len(offspring) < mu:
            raise ValueError(f"Cannot select {mu} from {len(offspring)} offspring")

        # Select best μ from offspring only
        sorted_indices = np.argsort(offspring_fitness)[::-1][:mu]

        selected_values = offspring[sorted_indices]
        selected_sigmas = offspring_sigmas[sorted_indices]
        selected_fitness = offspring_fitness[sorted_indices]

        stats = {
            'selection_type': 'comma',
            'total_candidates': len(offspring),
            'offspring_selected': mu,
            'parents_retained': 0
        }

        return selected_values, selected_sigmas, selected_fitness, stats

    @staticmethod
    def apply_selection(
        selection_type: ESSelectionType,
        parents: np.ndarray,
        parent_sigmas: np.ndarray,
        parent_fitness: np.ndarray,
        offspring: np.ndarray,
        offspring_sigmas: np.ndarray,
        offspring_fitness: np.ndarray,
        mu: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Apply selection based on type.

        Args:
            selection_type: Plus or comma selection
            parents: Parent values
            parent_sigmas: Parent step sizes
            parent_fitness: Parent fitness values
            offspring: Offspring values
            offspring_sigmas: Offspring step sizes
            offspring_fitness: Offspring fitness values
            mu: Number to select

        Returns:
            Tuple of (selected values, selected sigmas, selected fitness, stats)
        """
        if selection_type == ESSelectionType.COMMA:
            return ESOperators.select_comma(
                offspring, offspring_sigmas, offspring_fitness, mu
            )
        else:
            return ESOperators.select_plus(
                parents, parent_sigmas, parent_fitness,
                offspring, offspring_sigmas, offspring_fitness, mu
            )

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
    def calculate_sigma_stats(sigmas: np.ndarray) -> Dict[str, float]:
        """Calculate statistics about step sizes."""
        return {
            'average': float(np.mean(sigmas)),
            'std': float(np.std(sigmas)),
            'min': float(np.min(sigmas)),
            'max': float(np.max(sigmas))
        }
