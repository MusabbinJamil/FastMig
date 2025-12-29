"""
PSO (Particle Swarm Optimization) Operators Module

This module provides:
- PSOTopology enum for swarm topology types
- PSOVariant enum for PSO algorithm variants
- PSOConfig dataclass for configuration
- PSOMetrics dataclass for iteration metrics
- PSOResult dataclass for final results
- Static operator functions for velocity/position updates
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

class PSOTopology(Enum):
    """Swarm topology types for neighborhood determination."""
    GLOBAL_BEST = "gbest"       # All particles connected (star topology)
    LOCAL_BEST = "lbest"        # Ring topology with limited neighbors
    RING = "ring"               # Alias for lbest
    RANDOM = "random"           # Random neighbors each iteration
    VON_NEUMANN = "von_neumann" # 2D grid topology (4 neighbors)


class PSOVariant(Enum):
    """PSO algorithm variants."""
    STANDARD = "standard"           # Classic PSO with inertia weight
    CONSTRICTION = "constriction"   # Clerc's constriction factor method
    INERTIA_DECAY = "inertia_decay" # Linear inertia weight decay


class ConstraintHandling(Enum):
    """Methods for handling boundary constraints."""
    CLAMP = "clamp"       # Clamp to bounds
    REFLECT = "reflect"   # Reflect off bounds
    ABSORB = "absorb"     # Absorb at bounds (set velocity to 0)
    RANDOM = "random"     # Random position within bounds


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class PSOConfig:
    """Configuration for PSO algorithm."""

    # Swarm parameters
    swarm_size: int = 30
    iterations: int = 100

    # Velocity coefficients
    inertia_weight: float = 0.7      # w (inertia)
    inertia_min: float = 0.4         # For decay variant
    inertia_max: float = 0.9         # For decay variant
    cognitive_coeff: float = 1.5     # c1 (personal best attraction)
    social_coeff: float = 1.5        # c2 (global/local best attraction)

    # Velocity limits
    velocity_clamp: float = 0.2      # Max velocity as fraction of range
    velocity_min: float = -1.0       # Absolute min velocity (computed if not set)
    velocity_max: float = 1.0        # Absolute max velocity (computed if not set)

    # Topology and variant
    topology: PSOTopology = PSOTopology.GLOBAL_BEST
    variant: PSOVariant = PSOVariant.STANDARD

    # Constriction factor (for CONSTRICTION variant)
    constriction_factor: float = 0.729  # Chi (Clerc's constant)

    # Neighborhood (for LOCAL_BEST, RING, VON_NEUMANN)
    neighborhood_size: int = 3       # Number of neighbors on each side

    # Constraint handling
    constraint_handling: ConstraintHandling = ConstraintHandling.CLAMP

    # Early stopping
    early_stopping: bool = True
    patience: int = 10               # Iterations without improvement
    min_improvement: float = 1e-6    # Minimum improvement threshold
    fitness_threshold: float = 0.95  # Stop if best fitness exceeds this

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration parameters."""
        errors = []

        if self.swarm_size < 2:
            errors.append("swarm_size must be at least 2")
        if self.iterations < 1:
            errors.append("iterations must be at least 1")
        if not 0.0 <= self.inertia_weight <= 1.5:
            errors.append("inertia_weight should be between 0.0 and 1.5")
        if self.cognitive_coeff < 0 or self.social_coeff < 0:
            errors.append("cognitive_coeff and social_coeff must be non-negative")
        if self.cognitive_coeff + self.social_coeff > 4.0:
            errors.append("c1 + c2 should not exceed 4.0 for stability")
        if not 0.0 < self.velocity_clamp <= 1.0:
            errors.append("velocity_clamp should be between 0.0 and 1.0")
        if self.neighborhood_size < 1:
            errors.append("neighborhood_size must be at least 1")
        if not 0.0 < self.constriction_factor <= 1.0:
            errors.append("constriction_factor should be between 0.0 and 1.0")

        return len(errors) == 0, errors

    def __str__(self) -> str:
        return (
            f"PSOConfig(swarm={self.swarm_size}, iter={self.iterations}, "
            f"w={self.inertia_weight}, c1={self.cognitive_coeff}, c2={self.social_coeff}, "
            f"topology={self.topology.value}, variant={self.variant.value})"
        )


# ============================================================================
# METRICS
# ============================================================================

@dataclass
class PSOMetrics:
    """Metrics for a single PSO iteration."""

    iteration: int
    global_best_fitness: float
    average_fitness: float
    worst_fitness: float
    best_position: Optional[np.ndarray] = None

    # Velocity statistics
    average_velocity: float = 0.0
    velocity_std: float = 0.0
    max_velocity: float = 0.0

    # Swarm statistics
    swarm_diversity: float = 0.0     # Std of particle positions
    convergence_rate: float = 0.0    # Rate of improvement
    stagnation_counter: int = 0      # Iterations without improvement

    # Inertia tracking (for decay variant)
    current_inertia: float = 0.7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'iteration': self.iteration,
            'global_best_fitness': float(self.global_best_fitness),
            'average_fitness': float(self.average_fitness),
            'worst_fitness': float(self.worst_fitness),
            'average_velocity': float(self.average_velocity),
            'velocity_std': float(self.velocity_std),
            'max_velocity': float(self.max_velocity),
            'swarm_diversity': float(self.swarm_diversity),
            'convergence_rate': float(self.convergence_rate),
            'stagnation_counter': self.stagnation_counter,
            'current_inertia': float(self.current_inertia),
            'method': 'PSO'
        }

    def __str__(self) -> str:
        return (
            f"Iter {self.iteration}: best={self.global_best_fitness:.4f}, "
            f"avg={self.average_fitness:.4f}, div={self.swarm_diversity:.4f}"
        )


# ============================================================================
# RESULT
# ============================================================================

@dataclass
class PSOResult:
    """Final result from PSO optimization."""

    best_position: np.ndarray
    best_fitness: float
    worst_fitness: float
    average_fitness: float

    # Execution info
    total_iterations: int
    converged: bool
    convergence_iteration: Optional[int] = None

    # History
    fitness_history: List[float] = field(default_factory=list)  # Best fitness per iteration
    avg_fitness_history: List[float] = field(default_factory=list)
    velocity_history: List[float] = field(default_factory=list)  # Avg velocity per iteration
    diversity_history: List[float] = field(default_factory=list)
    iteration_metrics: List[PSOMetrics] = field(default_factory=list)

    # Final swarm state
    final_positions: Optional[np.ndarray] = None
    final_velocities: Optional[np.ndarray] = None

    # Timing
    execution_time: float = 0.0

    # Errors
    errors: List[str] = field(default_factory=list)

    # Config used
    config: Optional[PSOConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            'best_position': self.best_position.tolist() if isinstance(self.best_position, np.ndarray) else self.best_position,
            'best_fitness': float(self.best_fitness),
            'worst_fitness': float(self.worst_fitness),
            'average_fitness': float(self.average_fitness),
            'total_iterations': self.total_iterations,
            'converged': self.converged,
            'convergence_iteration': self.convergence_iteration,
            'fitness_history': [float(f) for f in self.fitness_history],
            'avg_fitness_history': [float(f) for f in self.avg_fitness_history],
            'velocity_history': [float(v) for v in self.velocity_history],
            'diversity_history': [float(d) for d in self.diversity_history],
            'iteration_metrics': [m.to_dict() for m in self.iteration_metrics],
            'execution_time': self.execution_time,
            'errors': self.errors,
            'method': 'PSO'
        }


# ============================================================================
# OPERATOR FUNCTIONS
# ============================================================================

class PSOOperators:
    """Static methods for PSO operations."""

    # -------------------------------------------------------------------------
    # Velocity Update Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def update_velocity_standard(
        velocities: np.ndarray,
        positions: np.ndarray,
        personal_best: np.ndarray,
        neighborhood_best: np.ndarray,
        w: float,
        c1: float,
        c2: float,
        v_min: float,
        v_max: float
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Standard PSO velocity update with inertia weight.

        v_new = w * v + c1 * r1 * (pbest - x) + c2 * r2 * (nbest - x)

        Args:
            velocities: Current velocities (n_particles,) or (n_particles, n_dims)
            positions: Current positions
            personal_best: Personal best positions
            neighborhood_best: Neighborhood best position(s)
            w: Inertia weight
            c1: Cognitive coefficient
            c2: Social coefficient
            v_min: Minimum velocity
            v_max: Maximum velocity

        Returns:
            Tuple of (new velocities, statistics dict)
        """
        n_particles = len(velocities)

        # Random factors
        r1 = np.random.random(velocities.shape)
        r2 = np.random.random(velocities.shape)

        # Cognitive component (attraction to personal best)
        cognitive = c1 * r1 * (personal_best - positions)

        # Social component (attraction to neighborhood best)
        social = c2 * r2 * (neighborhood_best - positions)

        # Velocity update
        new_velocities = w * velocities + cognitive + social

        # Clamp velocities
        new_velocities = np.clip(new_velocities, v_min, v_max)

        # Calculate statistics
        stats = {
            'avg_velocity': float(np.mean(np.abs(new_velocities))),
            'velocity_std': float(np.std(new_velocities)),
            'max_velocity': float(np.max(np.abs(new_velocities))),
            'avg_cognitive': float(np.mean(np.abs(cognitive))),
            'avg_social': float(np.mean(np.abs(social)))
        }

        return new_velocities, stats

    @staticmethod
    def update_velocity_constriction(
        velocities: np.ndarray,
        positions: np.ndarray,
        personal_best: np.ndarray,
        neighborhood_best: np.ndarray,
        chi: float,
        c1: float,
        c2: float,
        v_min: float,
        v_max: float
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Constriction factor velocity update (Clerc's method).

        v_new = chi * (v + c1 * r1 * (pbest - x) + c2 * r2 * (nbest - x))

        where chi = 2 / |2 - phi - sqrt(phi^2 - 4*phi)|, phi = c1 + c2 > 4

        Args:
            chi: Constriction factor (typically 0.729)
            Other args same as standard update

        Returns:
            Tuple of (new velocities, statistics dict)
        """
        # Random factors
        r1 = np.random.random(velocities.shape)
        r2 = np.random.random(velocities.shape)

        # Components without inertia (constriction applies to whole thing)
        cognitive = c1 * r1 * (personal_best - positions)
        social = c2 * r2 * (neighborhood_best - positions)

        # Apply constriction factor to everything
        new_velocities = chi * (velocities + cognitive + social)

        # Clamp velocities
        new_velocities = np.clip(new_velocities, v_min, v_max)

        stats = {
            'avg_velocity': float(np.mean(np.abs(new_velocities))),
            'velocity_std': float(np.std(new_velocities)),
            'max_velocity': float(np.max(np.abs(new_velocities))),
            'constriction_factor': chi
        }

        return new_velocities, stats

    @staticmethod
    def calculate_inertia_decay(
        iteration: int,
        max_iterations: int,
        w_max: float = 0.9,
        w_min: float = 0.4
    ) -> float:
        """
        Calculate linearly decaying inertia weight.

        w = w_max - (w_max - w_min) * (iteration / max_iterations)
        """
        return w_max - (w_max - w_min) * (iteration / max_iterations)

    # -------------------------------------------------------------------------
    # Position Update Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def update_position(
        positions: np.ndarray,
        velocities: np.ndarray,
        bounds_min: float,
        bounds_max: float,
        constraint_handling: ConstraintHandling = ConstraintHandling.CLAMP
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Update particle positions with constraint handling.

        Args:
            positions: Current positions
            velocities: Current velocities
            bounds_min: Lower bound
            bounds_max: Upper bound
            constraint_handling: Method for handling bound violations

        Returns:
            Tuple of (new positions, adjusted velocities, statistics)
        """
        new_positions = positions + velocities
        adjusted_velocities = velocities.copy()
        violations = 0

        if constraint_handling == ConstraintHandling.CLAMP:
            # Simple clamping
            violations = np.sum((new_positions < bounds_min) | (new_positions > bounds_max))
            new_positions = np.clip(new_positions, bounds_min, bounds_max)

        elif constraint_handling == ConstraintHandling.REFLECT:
            # Reflect off boundaries
            below_min = new_positions < bounds_min
            above_max = new_positions > bounds_max
            violations = np.sum(below_min | above_max)

            # Reflect positions
            new_positions = np.where(below_min, 2 * bounds_min - new_positions, new_positions)
            new_positions = np.where(above_max, 2 * bounds_max - new_positions, new_positions)

            # Reverse velocities at boundaries
            adjusted_velocities = np.where(below_min | above_max, -velocities, velocities)

            # Ensure still within bounds after reflection
            new_positions = np.clip(new_positions, bounds_min, bounds_max)

        elif constraint_handling == ConstraintHandling.ABSORB:
            # Absorb at boundaries (set velocity to 0)
            below_min = new_positions < bounds_min
            above_max = new_positions > bounds_max
            violations = np.sum(below_min | above_max)

            new_positions = np.clip(new_positions, bounds_min, bounds_max)
            adjusted_velocities = np.where(below_min | above_max, 0.0, velocities)

        elif constraint_handling == ConstraintHandling.RANDOM:
            # Random reinitialization within bounds
            below_min = new_positions < bounds_min
            above_max = new_positions > bounds_max
            out_of_bounds = below_min | above_max
            violations = np.sum(out_of_bounds)

            random_positions = np.random.uniform(bounds_min, bounds_max, new_positions.shape)
            new_positions = np.where(out_of_bounds, random_positions, new_positions)
            adjusted_velocities = np.where(out_of_bounds, 0.0, velocities)

        stats = {
            'boundary_violations': int(violations),
            'violation_rate': float(violations / len(positions)) if len(positions) > 0 else 0.0
        }

        return new_positions, adjusted_velocities, stats

    # -------------------------------------------------------------------------
    # Neighborhood Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def get_global_best(
        personal_best_positions: np.ndarray,
        personal_best_fitness: np.ndarray
    ) -> Tuple[np.ndarray, float, int]:
        """
        Get global best (gbest) - best across all particles.

        Returns:
            Tuple of (best position, best fitness, best index)
        """
        best_idx = np.argmax(personal_best_fitness)
        return personal_best_positions[best_idx], personal_best_fitness[best_idx], best_idx

    @staticmethod
    def get_neighborhood_best_ring(
        particle_idx: int,
        n_particles: int,
        personal_best_positions: np.ndarray,
        personal_best_fitness: np.ndarray,
        neighborhood_size: int = 1
    ) -> Tuple[np.ndarray, float]:
        """
        Get local best for ring topology.

        Each particle is connected to its neighbors in a ring.

        Args:
            particle_idx: Index of current particle
            n_particles: Total number of particles
            personal_best_positions: All personal best positions
            personal_best_fitness: All personal best fitness values
            neighborhood_size: Number of neighbors on each side

        Returns:
            Tuple of (best neighbor position, best neighbor fitness)
        """
        # Get neighbor indices (ring wraps around)
        neighbors = []
        for offset in range(-neighborhood_size, neighborhood_size + 1):
            neighbor_idx = (particle_idx + offset) % n_particles
            neighbors.append(neighbor_idx)

        # Find best in neighborhood
        neighbor_fitness = personal_best_fitness[neighbors]
        best_local_idx = neighbors[np.argmax(neighbor_fitness)]

        return personal_best_positions[best_local_idx], personal_best_fitness[best_local_idx]

    @staticmethod
    def get_neighborhood_best_random(
        particle_idx: int,
        n_particles: int,
        personal_best_positions: np.ndarray,
        personal_best_fitness: np.ndarray,
        neighborhood_size: int = 3
    ) -> Tuple[np.ndarray, float]:
        """
        Get local best with random neighbors (reselected each call).

        Args:
            particle_idx: Index of current particle
            n_particles: Total number of particles
            personal_best_positions: All personal best positions
            personal_best_fitness: All personal best fitness values
            neighborhood_size: Number of random neighbors to consider

        Returns:
            Tuple of (best neighbor position, best neighbor fitness)
        """
        # Select random neighbors (excluding self)
        other_indices = [i for i in range(n_particles) if i != particle_idx]
        k = min(neighborhood_size, len(other_indices))
        neighbors = [particle_idx] + list(np.random.choice(other_indices, k, replace=False))

        # Find best in neighborhood
        neighbor_fitness = personal_best_fitness[neighbors]
        best_local_idx = neighbors[np.argmax(neighbor_fitness)]

        return personal_best_positions[best_local_idx], personal_best_fitness[best_local_idx]

    @staticmethod
    def get_neighborhood_best_von_neumann(
        particle_idx: int,
        n_particles: int,
        personal_best_positions: np.ndarray,
        personal_best_fitness: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """
        Get local best for Von Neumann (2D grid) topology.

        Particles arranged in 2D grid, connected to 4 neighbors (up, down, left, right).
        """
        # Calculate grid dimensions (as square as possible)
        grid_size = int(np.ceil(np.sqrt(n_particles)))
        row = particle_idx // grid_size
        col = particle_idx % grid_size

        # Get 4 neighbors (with wrapping)
        neighbors = [particle_idx]  # Include self

        # Up
        up_row = (row - 1) % grid_size
        up_idx = up_row * grid_size + col
        if up_idx < n_particles:
            neighbors.append(up_idx)

        # Down
        down_row = (row + 1) % grid_size
        down_idx = down_row * grid_size + col
        if down_idx < n_particles:
            neighbors.append(down_idx)

        # Left
        left_col = (col - 1) % grid_size
        left_idx = row * grid_size + left_col
        if left_idx < n_particles:
            neighbors.append(left_idx)

        # Right
        right_col = (col + 1) % grid_size
        right_idx = row * grid_size + right_col
        if right_idx < n_particles:
            neighbors.append(right_idx)

        # Find best in neighborhood
        neighbor_fitness = personal_best_fitness[neighbors]
        best_local_idx = neighbors[np.argmax(neighbor_fitness)]

        return personal_best_positions[best_local_idx], personal_best_fitness[best_local_idx]

    # -------------------------------------------------------------------------
    # Utility Functions
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_swarm_diversity(positions: np.ndarray) -> float:
        """
        Calculate diversity of swarm positions.

        Higher diversity means particles are spread out.
        Lower diversity means particles are converging.
        """
        if len(positions) == 0:
            return 0.0
        return float(np.std(positions))

    @staticmethod
    def calculate_convergence_rate(
        fitness_history: List[float],
        window_size: int = 5
    ) -> float:
        """
        Calculate rate of fitness improvement over recent iterations.

        Returns positive value if improving, negative if getting worse.
        """
        if len(fitness_history) < 2:
            return 0.0

        window = min(window_size, len(fitness_history))
        recent = fitness_history[-window:]

        if len(recent) < 2:
            return 0.0

        # Linear regression slope
        x = np.arange(len(recent))
        slope = np.polyfit(x, recent, 1)[0]

        return float(slope)

    @staticmethod
    def initialize_swarm(
        n_particles: int,
        bounds_min: float,
        bounds_max: float,
        seed_values: Optional[np.ndarray] = None,
        seed_ratio: float = 0.3
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Initialize swarm positions and velocities.

        Args:
            n_particles: Number of particles
            bounds_min: Lower bound
            bounds_max: Upper bound
            seed_values: Optional values to seed some particles (e.g., healthy cell values)
            seed_ratio: Fraction of particles to seed from seed_values

        Returns:
            Tuple of (positions, velocities)
        """
        range_size = bounds_max - bounds_min

        if seed_values is not None and len(seed_values) > 0:
            # Seed some particles from provided values
            n_seeded = int(n_particles * seed_ratio)
            n_random = n_particles - n_seeded

            # Seeded particles (with small noise)
            seeded_positions = np.random.choice(seed_values, n_seeded)
            noise = np.random.normal(0, range_size * 0.1, n_seeded)
            seeded_positions = np.clip(seeded_positions + noise, bounds_min, bounds_max)

            # Random particles
            random_positions = np.random.uniform(bounds_min, bounds_max, n_random)

            positions = np.concatenate([seeded_positions, random_positions])
        else:
            # All random
            positions = np.random.uniform(bounds_min, bounds_max, n_particles)

        # Initialize velocities (small random values)
        velocity_max = range_size * 0.2  # 20% of range
        velocities = np.random.uniform(-velocity_max, velocity_max, n_particles)

        return positions, velocities
