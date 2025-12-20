"""
GA Core Operators Module
========================
Refactored Genetic Algorithm operators with standardized parameters,
consistent metrics, and error handling.

Operators:
- Selection (Tournament, Roulette Wheel, Rank-based)
- Crossover (Single-point, Two-point, Uniform)
- Mutation (Gaussian, Uniform, Adaptive)
- Evaluation (Fitness scoring)
"""

import numpy as np
import logging
from typing import Tuple, List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import warnings

logger = logging.getLogger(__name__)


class SelectionMethod(Enum):
    """Selection methods available"""
    TOURNAMENT = "tournament"
    ROULETTE_WHEEL = "roulette_wheel"
    RANK_BASED = "rank_based"
    ELITISM = "elitism"


class CrossoverMethod(Enum):
    """Crossover methods available"""
    SINGLE_POINT = "single_point"
    TWO_POINT = "two_point"
    UNIFORM = "uniform"
    ARITHMETIC = "arithmetic"


class MutationMethod(Enum):
    """Mutation methods available"""
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    ADAPTIVE = "adaptive"


@dataclass
class GAMetrics:
    """Container for GA metrics across generations"""
    generation: int
    best_fitness: float
    worst_fitness: float
    average_fitness: float
    population_diversity: float
    selections_performed: int
    crossovers_performed: int
    mutations_performed: int
    convergence_rate: float
    
    def __str__(self) -> str:
        return (f"Gen {self.generation} | Best: {self.best_fitness:.4f} | "
                f"Avg: {self.average_fitness:.4f} | Div: {self.population_diversity:.4f} | "
                f"Conv: {self.convergence_rate:.4f}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'generation': self.generation,
            'best_fitness': float(self.best_fitness),
            'worst_fitness': float(self.worst_fitness),
            'average_fitness': float(self.average_fitness),
            'population_diversity': float(self.population_diversity),
            'selections_performed': self.selections_performed,
            'crossovers_performed': self.crossovers_performed,
            'mutations_performed': self.mutations_performed,
            'convergence_rate': float(self.convergence_rate)
        }


@dataclass
class GAConfig:
    """Standardized GA Configuration"""
    population_size: int = 50
    generations: int = 100
    selection_method: SelectionMethod = SelectionMethod.TOURNAMENT
    crossover_method: CrossoverMethod = CrossoverMethod.SINGLE_POINT
    mutation_method: MutationMethod = MutationMethod.GAUSSIAN
    
    # Probabilities
    crossover_rate: float = 0.8  # 0.0-1.0
    mutation_rate: float = 0.1   # 0.0-1.0
    elitism_rate: float = 0.05   # Keep top 5% without modification
    
    # Selection parameters
    tournament_size: int = 3
    selection_pressure: float = 1.5  # For rank-based selection
    
    # Mutation parameters
    mutation_std: float = 1.0  # Standard deviation for Gaussian mutation
    mutation_min: float = 0.0  # Min value for uniform mutation
    mutation_max: float = 1.0  # Max value for uniform mutation
    adaptive_mutation: bool = False  # Adapt mutation rate during evolution
    
    # Convergence
    early_stopping: bool = False
    early_stopping_generations: int = 20
    early_stopping_threshold: float = 1e-6
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration parameters"""
        errors = []
        
        if self.population_size < 4:
            errors.append("population_size must be >= 4")
        if self.generations < 1:
            errors.append("generations must be >= 1")
        if not (0.0 <= self.crossover_rate <= 1.0):
            errors.append("crossover_rate must be between 0.0 and 1.0")
        if not (0.0 <= self.mutation_rate <= 1.0):
            errors.append("mutation_rate must be between 0.0 and 1.0")
        if not (0.0 <= self.elitism_rate <= 1.0):
            errors.append("elitism_rate must be between 0.0 and 1.0")
        if self.tournament_size < 2:
            errors.append("tournament_size must be >= 2")
        if self.mutation_std <= 0:
            errors.append("mutation_std must be > 0")
        if self.early_stopping_generations < 1:
            errors.append("early_stopping_generations must be >= 1")
        
        return len(errors) == 0, errors
    
    def __str__(self) -> str:
        return (f"GAConfig(pop={self.population_size}, gen={self.generations}, "
                f"sel={self.selection_method.value}, cross={self.crossover_method.value}, "
                f"mut={self.mutation_method.value}, cr={self.crossover_rate}, mr={self.mutation_rate})")


class GAOperators:
    """
    Core GA operators with standardized interfaces.
    All methods are stateless and can be used independently.
    """
    
    @staticmethod
    def validate_population(population: List[np.ndarray], 
                          fitness_scores: Optional[List[float]] = None) -> Tuple[bool, List[str]]:
        """Validate population integrity"""
        errors = []
        
        if not population:
            errors.append("Population is empty")
            return False, errors
        
        if not all(isinstance(ind, np.ndarray) for ind in population):
            errors.append("All individuals must be numpy arrays")
        
        if fitness_scores and len(fitness_scores) != len(population):
            errors.append(f"Fitness scores ({len(fitness_scores)}) don't match population size ({len(population)})")
        
        if fitness_scores and not all(isinstance(f, (int, float, np.number)) for f in fitness_scores):
            errors.append("All fitness scores must be numeric")
        
        if fitness_scores and any(np.isnan(f) or np.isinf(f) for f in fitness_scores):
            errors.append("Fitness scores contain NaN or Inf values")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def selection_tournament(population: List[np.ndarray],
                           fitness_scores: List[float],
                           num_parents: int,
                           tournament_size: int = 3) -> Tuple[List[np.ndarray], Dict[str, int]]:
        """
        Tournament Selection
        
        Randomly select tournament_size individuals and pick the best.
        Repeat num_parents times.
        
        Args:
            population: List of individual solutions
            fitness_scores: Fitness for each individual
            num_parents: Number of parents to select
            tournament_size: Size of tournament (higher = more pressure)
        
        Returns:
            (Selected parents, statistics dict)
        """
        if not population or not fitness_scores:
            raise ValueError("Population and fitness_scores cannot be empty")
        
        if tournament_size > len(population):
            logger.warning(f"Tournament size ({tournament_size}) > population size ({len(population)}), "
                         f"reducing to population size")
            tournament_size = len(population)
        
        selected = []
        for _ in range(num_parents):
            # Randomly select tournament_size indices
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            # Find the best individual in tournament
            best_idx = tournament_indices[np.argmax([fitness_scores[i] for i in tournament_indices])]
            selected.append(population[best_idx].copy())
        
        stats = {
            'method': 'tournament',
            'tournament_size': tournament_size,
            'parents_selected': len(selected)
        }
        
        logger.debug(f"Tournament selection: selected {len(selected)} parents (tournament_size={tournament_size})")
        return selected, stats
    
    @staticmethod
    def selection_roulette_wheel(population: List[np.ndarray],
                                fitness_scores: List[float],
                                num_parents: int) -> Tuple[List[np.ndarray], Dict[str, Any]]:
        """
        Roulette Wheel Selection (Fitness-Proportionate Selection)
        
        Probability of selection proportional to fitness.
        
        Args:
            population: List of individual solutions
            fitness_scores: Fitness for each individual (must be positive)
            num_parents: Number of parents to select
        
        Returns:
            (Selected parents, statistics dict)
        """
        if not population or not fitness_scores:
            raise ValueError("Population and fitness_scores cannot be empty")
        
        fitness_array = np.array(fitness_scores, dtype=float)
        
        # Handle negative fitness by shifting to positive range
        min_fitness = np.min(fitness_array)
        if min_fitness <= 0:
            fitness_array = fitness_array - min_fitness + 1
        
        # Calculate selection probabilities
        total_fitness = np.sum(fitness_array)
        if total_fitness <= 0:
            logger.warning("Total fitness <= 0, using uniform selection")
            probabilities = np.ones(len(population)) / len(population)
        else:
            probabilities = fitness_array / total_fitness
        
        # Select parents based on probabilities
        selected_indices = np.random.choice(len(population), size=num_parents, 
                                          p=probabilities, replace=True)
        selected = [population[i].copy() for i in selected_indices]
        
        stats = {
            'method': 'roulette_wheel',
            'parents_selected': len(selected),
            'avg_probability': float(np.mean(probabilities)),
            'min_probability': float(np.min(probabilities)),
            'max_probability': float(np.max(probabilities))
        }
        
        logger.debug(f"Roulette wheel selection: selected {len(selected)} parents")
        return selected, stats
    
    @staticmethod
    def selection_rank_based(population: List[np.ndarray],
                            fitness_scores: List[float],
                            num_parents: int,
                            selection_pressure: float = 1.5) -> Tuple[List[np.ndarray], Dict[str, Any]]:
        """
        Rank-Based Selection
        
        Selection probability based on rank (position when sorted by fitness),
        not absolute fitness values. More stable than roulette wheel.
        
        Args:
            population: List of individual solutions
            fitness_scores: Fitness for each individual
            num_parents: Number of parents to select
            selection_pressure: Controls selection pressure (>1 = higher pressure towards best)
        
        Returns:
            (Selected parents, statistics dict)
        """
        if not population or not fitness_scores:
            raise ValueError("Population and fitness_scores cannot be empty")
        
        # Get ranks (1 = worst, N = best)
        fitness_array = np.array(fitness_scores)
        ranks = np.argsort(np.argsort(fitness_array)) + 1  # Convert to 1-based ranks
        
        # Calculate selection probabilities using exponential rank selection
        n = len(population)
        probabilities = np.exp(selection_pressure * (ranks - 1) / (n - 1))
        probabilities = probabilities / np.sum(probabilities)
        
        # Select parents based on rank probabilities
        selected_indices = np.random.choice(len(population), size=num_parents,
                                          p=probabilities, replace=True)
        selected = [population[i].copy() for i in selected_indices]
        
        stats = {
            'method': 'rank_based',
            'parents_selected': len(selected),
            'selection_pressure': selection_pressure,
            'avg_rank_selected': float(np.mean([ranks[i] for i in selected_indices]))
        }
        
        logger.debug(f"Rank-based selection: selected {len(selected)} parents")
        return selected, stats
    
    @staticmethod
    def crossover_single_point(parent1: np.ndarray,
                              parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Single-Point Crossover
        
        Randomly select a point and swap genetic material after that point.
        
        Args:
            parent1: First parent solution
            parent2: Second parent solution
        
        Returns:
            (child1, child2) offspring
        """
        if len(parent1) != len(parent2):
            raise ValueError(f"Parents must have same length: {len(parent1)} vs {len(parent2)}")
        
        if len(parent1) < 2:
            # Can't crossover single element
            return parent1.copy(), parent2.copy()
        
        # Select random crossover point
        crossover_point = np.random.randint(1, len(parent1))
        
        # Create offspring
        child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
        
        logger.debug(f"Single-point crossover at position {crossover_point}")
        return child1, child2
    
    @staticmethod
    def crossover_two_point(parent1: np.ndarray,
                           parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Two-Point Crossover
        
        Randomly select two points and swap genetic material between them.
        
        Args:
            parent1: First parent solution
            parent2: Second parent solution
        
        Returns:
            (child1, child2) offspring
        """
        if len(parent1) != len(parent2):
            raise ValueError(f"Parents must have same length: {len(parent1)} vs {len(parent2)}")
        
        if len(parent1) < 3:
            # Fall back to single-point
            return GAOperators.crossover_single_point(parent1, parent2)
        
        # Select two random crossover points
        point1, point2 = sorted(np.random.choice(len(parent1), 2, replace=False))
        
        # Create offspring by swapping middle segment
        child1 = np.concatenate([
            parent1[:point1],
            parent2[point1:point2],
            parent1[point2:]
        ])
        child2 = np.concatenate([
            parent2[:point1],
            parent1[point1:point2],
            parent2[point2:]
        ])
        
        logger.debug(f"Two-point crossover at positions {point1}, {point2}")
        return child1, child2
    
    @staticmethod
    def crossover_uniform(parent1: np.ndarray,
                         parent2: np.ndarray,
                         swap_rate: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Uniform Crossover
        
        For each position, randomly choose genetic material from either parent.
        
        Args:
            parent1: First parent solution
            parent2: Second parent solution
            swap_rate: Probability of swapping each position
        
        Returns:
            (child1, child2) offspring
        """
        if len(parent1) != len(parent2):
            raise ValueError(f"Parents must have same length: {len(parent1)} vs {len(parent2)}")
        
        # Generate random mask
        mask = np.random.random(len(parent1)) < swap_rate
        
        # Create offspring
        child1 = np.where(mask, parent2, parent1)
        child2 = np.where(mask, parent1, parent2)
        
        swaps = np.sum(mask)
        logger.debug(f"Uniform crossover: {swaps} positions swapped")
        return child1, child2
    
    @staticmethod
    def crossover_arithmetic(parent1: np.ndarray,
                            parent2: np.ndarray,
                            weight: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Arithmetic (Blending) Crossover
        
        Create offspring as weighted average of parents. Good for continuous optimization.
        
        Args:
            parent1: First parent solution (numeric)
            parent2: Second parent solution (numeric)
            weight: How much of parent1 vs parent2 (0.0-1.0)
        
        Returns:
            (child1, child2) offspring
        """
        if len(parent1) != len(parent2):
            raise ValueError(f"Parents must have same length: {len(parent1)} vs {len(parent2)}")
        
        if not (0.0 <= weight <= 1.0):
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {weight}")
        
        # Create offspring as weighted averages
        child1 = weight * parent1 + (1 - weight) * parent2
        child2 = (1 - weight) * parent1 + weight * parent2
        
        logger.debug(f"Arithmetic crossover with weight {weight}")
        return child1, child2
    
    @staticmethod
    def mutation_gaussian(individual: np.ndarray,
                         mutation_rate: float,
                         std: float = 1.0) -> np.ndarray:
        """
        Gaussian (Normal) Mutation
        
        Add Gaussian noise to random positions.
        
        Args:
            individual: Solution to mutate
            mutation_rate: Probability of mutating each gene
            std: Standard deviation of Gaussian noise
        
        Returns:
            Mutated individual
        """
        if not (0.0 <= mutation_rate <= 1.0):
            raise ValueError(f"mutation_rate must be between 0.0 and 1.0, got {mutation_rate}")
        
        if std <= 0:
            raise ValueError(f"std must be > 0, got {std}")
        
        mutated = individual.copy()
        mutation_mask = np.random.random(len(mutated)) < mutation_rate
        mutated[mutation_mask] += np.random.normal(0, std, np.sum(mutation_mask))
        
        mutations = np.sum(mutation_mask)
        logger.debug(f"Gaussian mutation: {mutations} genes mutated")
        return mutated
    
    @staticmethod
    def mutation_uniform(individual: np.ndarray,
                        mutation_rate: float,
                        min_val: float = 0.0,
                        max_val: float = 1.0) -> np.ndarray:
        """
        Uniform Mutation
        
        Replace random genes with random values from [min_val, max_val].
        
        Args:
            individual: Solution to mutate
            mutation_rate: Probability of mutating each gene
            min_val: Minimum value for new genes
            max_val: Maximum value for new genes
        
        Returns:
            Mutated individual
        """
        if not (0.0 <= mutation_rate <= 1.0):
            raise ValueError(f"mutation_rate must be between 0.0 and 1.0, got {mutation_rate}")
        
        if min_val >= max_val:
            raise ValueError(f"min_val ({min_val}) must be < max_val ({max_val})")
        
        mutated = individual.copy()
        mutation_mask = np.random.random(len(mutated)) < mutation_rate
        mutated[mutation_mask] = np.random.uniform(min_val, max_val, np.sum(mutation_mask))
        
        mutations = np.sum(mutation_mask)
        logger.debug(f"Uniform mutation: {mutations} genes mutated")
        return mutated
    
    @staticmethod
    def mutation_adaptive(individual: np.ndarray,
                         mutation_rate: float,
                         generation: int,
                         max_generations: int,
                         std: float = 1.0) -> np.ndarray:
        """
        Adaptive Mutation
        
        Mutation rate decreases over time to balance exploration and exploitation.
        
        Args:
            individual: Solution to mutate
            mutation_rate: Initial mutation rate
            generation: Current generation
            max_generations: Total generations
            std: Standard deviation
        
        Returns:
            Mutated individual
        """
        # Decrease mutation rate over time (linear decay)
        adapted_rate = mutation_rate * (1.0 - generation / max_generations)
        
        mutated = GAOperators.mutation_gaussian(individual, adapted_rate, std)
        logger.debug(f"Adaptive mutation: rate={adapted_rate:.4f}")
        return mutated
    
    @staticmethod
    def calculate_convergence_rate(fitness_history: List[float],
                                  window_size: int = 5) -> float:
        """
        Calculate convergence rate based on recent fitness improvements.
        
        Args:
            fitness_history: Best fitness values across generations
            window_size: Number of generations to consider
        
        Returns:
            Convergence rate (0.0 = stagnation, 1.0 = fast improvement)
        """
        if len(fitness_history) < window_size:
            return 0.0
        
        recent_improvements = []
        for i in range(len(fitness_history) - window_size + 1, len(fitness_history)):
            if i > 0:
                improvement = (fitness_history[i] - fitness_history[i-1]) / (abs(fitness_history[i-1]) + 1e-10)
                recent_improvements.append(abs(improvement))
        
        if not recent_improvements:
            return 0.0
        
        # Average relative improvement
        convergence = np.mean(recent_improvements)
        return min(convergence, 1.0)  # Cap at 1.0
    
    @staticmethod
    def calculate_population_diversity(population: List[np.ndarray]) -> float:
        """
        Calculate population diversity using average pairwise distance.
        
        Args:
            population: List of individual solutions
        
        Returns:
            Diversity metric (0.0 = identical, 1.0 = fully diverse)
        """
        if len(population) < 2:
            return 0.0
        
        population_array = np.array([ind.flatten() for ind in population])
        
        # Calculate average Euclidean distance between all pairs
        distances = []
        for i in range(len(population_array)):
            for j in range(i + 1, len(population_array)):
                dist = np.linalg.norm(population_array[i] - population_array[j])
                distances.append(dist)
        
        if not distances:
            return 0.0
        
        # Normalize by maximum possible distance
        avg_distance = np.mean(distances)
        max_distance = np.max([np.linalg.norm(population_array[i] - population_array[j])
                              for i in range(len(population_array))
                              for j in range(i + 1, len(population_array))])
        
        if max_distance == 0:
            return 0.0
        
        return float(avg_distance / max_distance)


def test_ga_operators():
    """Test GA operators interactively in command prompt"""
    print("\n" + "="*60)
    print("GA OPERATORS TEST SUITE")
    print("="*60)
    
    # Create test population
    population = [np.random.randn(10) for _ in range(5)]
    fitness_scores = [float(np.sum(ind**2)) for ind in population]  # Negative: we want to minimize
    
    print(f"\nTest Population: {len(population)} individuals, 10 genes each")
    print(f"Fitness Scores: {[f'{f:.2f}' for f in fitness_scores]}")
    
    # Test configurations
    config = GAConfig(population_size=10, generations=5)
    is_valid, errors = config.validate()
    print(f"\nConfiguration Valid: {is_valid}")
    if errors:
        for e in errors:
            print(f"  - {e}")
    print(f"  {config}")
    
    # Test selection methods
    print("\n" + "-"*60)
    print("SELECTION METHODS")
    print("-"*60)
    
    selected, stats = GAOperators.selection_tournament(population, fitness_scores, 3, tournament_size=2)
    print(f"\nTournament Selection: {stats}")
    
    selected, stats = GAOperators.selection_roulette_wheel(population, fitness_scores, 3)
    print(f"Roulette Wheel Selection: {stats}")
    
    selected, stats = GAOperators.selection_rank_based(population, fitness_scores, 3)
    print(f"Rank-Based Selection: {stats}")
    
    # Test crossover methods
    print("\n" + "-"*60)
    print("CROSSOVER METHODS")
    print("-"*60)
    
    p1, p2 = population[0], population[1]
    
    c1, c2 = GAOperators.crossover_single_point(p1, p2)
    print(f"\nSingle-Point Crossover: Parent1[0]={p1[0]:.4f}, Parent2[0]={p2[0]:.4f}, "
          f"Child1[0]={c1[0]:.4f}, Child2[0]={c2[0]:.4f}")
    
    c1, c2 = GAOperators.crossover_two_point(p1, p2)
    print(f"Two-Point Crossover: Parent1[0]={p1[0]:.4f}, Parent2[0]={p2[0]:.4f}, "
          f"Child1[0]={c1[0]:.4f}, Child2[0]={c2[0]:.4f}")
    
    c1, c2 = GAOperators.crossover_uniform(p1, p2)
    print(f"Uniform Crossover: Parent1[0]={p1[0]:.4f}, Parent2[0]={p2[0]:.4f}, "
          f"Child1[0]={c1[0]:.4f}, Child2[0]={c2[0]:.4f}")
    
    c1, c2 = GAOperators.crossover_arithmetic(p1, p2, weight=0.7)
    print(f"Arithmetic Crossover (w=0.7): Parent1[0]={p1[0]:.4f}, Parent2[0]={p2[0]:.4f}, "
          f"Child1[0]={c1[0]:.4f}, Child2[0]={c2[0]:.4f}")
    
    # Test mutation methods
    print("\n" + "-"*60)
    print("MUTATION METHODS")
    print("-"*60)
    
    ind = population[0].copy()
    
    m1 = GAOperators.mutation_gaussian(ind, mutation_rate=0.3, std=0.5)
    print(f"\nGaussian Mutation: Original[0]={ind[0]:.4f}, Mutated[0]={m1[0]:.4f}")
    
    m2 = GAOperators.mutation_uniform(ind, mutation_rate=0.3, min_val=0.0, max_val=1.0)
    print(f"Uniform Mutation: Original[0]={ind[0]:.4f}, Mutated[0]={m2[0]:.4f}")
    
    m3 = GAOperators.mutation_adaptive(ind, mutation_rate=0.3, generation=5, max_generations=100, std=0.5)
    print(f"Adaptive Mutation (gen=5/100): Original[0]={ind[0]:.4f}, Mutated[0]={m3[0]:.4f}")
    
    # Test metrics
    print("\n" + "-"*60)
    print("METRICS")
    print("-"*60)
    
    fitness_history = [100.0, 85.0, 75.0, 72.0, 71.0]
    convergence = GAOperators.calculate_convergence_rate(fitness_history)
    diversity = GAOperators.calculate_population_diversity(population)
    
    print(f"\nConvergence Rate: {convergence:.4f}")
    print(f"Population Diversity: {diversity:.4f}")
    
    metrics = GAMetrics(
        generation=10,
        best_fitness=71.0,
        worst_fitness=120.0,
        average_fitness=85.0,
        population_diversity=diversity,
        selections_performed=5,
        crossovers_performed=3,
        mutations_performed=8,
        convergence_rate=convergence
    )
    print(f"\nMetrics: {metrics}")
    print(f"Metrics Dict: {metrics.to_dict()}")
    
    print("\n" + "="*60)
    print("✓ GA OPERATORS TEST COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s - %(message)s'
    )
    test_ga_operators()
