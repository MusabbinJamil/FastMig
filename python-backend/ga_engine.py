"""
Genetic Algorithm Engine
========================
Complete GA framework with:
- Modular core loop (selection → crossover → mutation → evaluation)
- Async batch evaluation
- Error handling for invalid phenotypes
- Convergence optimization
- Comprehensive metrics tracking
"""

import numpy as np
import logging
import asyncio
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

from ga_operators import (
    GAOperators, GAMetrics, GAConfig, SelectionMethod,
    CrossoverMethod, MutationMethod
)
from ga_genotype_phenotype import (
    GenotypeMapper, RealValuedMapper, GrammarMapper
)

logger = logging.getLogger(__name__)


@dataclass
class GAResult:
    """Container for GA execution results"""
    best_phenotype: Any
    best_fitness: float
    worst_fitness: float
    average_fitness: float
    total_generations: int
    generation_metrics: List[Dict[str, Any]] = field(default_factory=list)
    population_history: List[List[np.ndarray]] = field(default_factory=list)
    fitness_history: List[List[float]] = field(default_factory=list)
    execution_time: float = 0.0
    convergence_achieved: bool = False
    errors: List[str] = field(default_factory=list)
    config: Optional[GAConfig] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'best_fitness': float(self.best_fitness),
            'worst_fitness': float(self.worst_fitness),
            'average_fitness': float(self.average_fitness),
            'total_generations': self.total_generations,
            'execution_time': float(self.execution_time),
            'convergence_achieved': self.convergence_achieved,
            'generation_metrics': self.generation_metrics,
            'errors': self.errors,
            'config': str(self.config) if self.config else None
        }
    
    def __str__(self) -> str:
        return (f"GAResult(\n"
                f"  Best Fitness: {self.best_fitness:.6f}\n"
                f"  Avg Fitness: {self.average_fitness:.6f}\n"
                f"  Generations: {self.total_generations}\n"
                f"  Execution Time: {self.execution_time:.2f}s\n"
                f"  Convergence: {self.convergence_achieved}\n"
                f"  Errors: {len(self.errors)}\n"
                f")")


class GeneticAlgorithmEngine:
    """
    Complete GA engine with all operators and features.
    
    Usage:
        engine = GeneticAlgorithmEngine(config, fitness_func, mapper)
        result = engine.run()
    """
    
    def __init__(self, 
                 config: GAConfig,
                 fitness_function: Callable[[Any], float],
                 genotype_mapper: GenotypeMapper,
                 population: Optional[List[np.ndarray]] = None):
        """
        Args:
            config: GA configuration
            fitness_function: Function that evaluates phenotype fitness
            genotype_mapper: Maps genotype to phenotype
            population: Initial population (if None, creates random)
        """
        self.config = config
        self.fitness_function = fitness_function
        self.mapper = genotype_mapper
        
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            raise ValueError(f"Invalid GA config: {errors}")
        
        # Initialize population
        if population is None:
            self.population = [
                self.mapper.create_random_genotype(10)
                for _ in range(config.population_size)
            ]
        else:
            if len(population) != config.population_size:
                logger.warning(f"Population size {len(population)} != config size {config.population_size}")
            self.population = population.copy()
        
        # Tracking
        self.generation = 0
        self.best_fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.population_history: List[List[np.ndarray]] = []
        self.generation_metrics: List[GAMetrics] = []
        self.errors: List[str] = []
        self.invalid_phenotypes: List[Tuple[int, str, str]] = []  # (gen, genotype, error)
    
    def _evaluate_fitness_batch(self, 
                               individuals: List[np.ndarray],
                               generation: int = 0,
                               use_async: bool = False) -> Tuple[List[float], List[Any]]:
        """
        Evaluate fitness for a batch of individuals.
        
        Args:
            individuals: List of genotypes
            generation: Current generation (for error tracking)
            use_async: Whether to use async evaluation
        
        Returns:
            (fitness_scores, phenotypes)
        """
        fitness_scores = []
        phenotypes = []
        
        try:
            if use_async:
                fitness_scores, phenotypes = asyncio.run(
                    self._evaluate_fitness_async(individuals)
                )
            else:
                # Synchronous batch evaluation
                for ind_idx, genotype in enumerate(individuals):
                    try:
                        # Convert to phenotype
                        phenotype = self.mapper.genotype_to_phenotype(genotype)
                        
                        # Validate phenotype
                        is_valid, error_msg = self.mapper.validate_phenotype(phenotype)
                        if not is_valid:
                            self.invalid_phenotypes.append((generation, str(genotype), error_msg))
                            logger.warning(f"Invalid phenotype (gen {generation}, ind {ind_idx}): {error_msg}")
                            # Assign worst fitness for invalid phenotype
                            fitness_scores.append(-np.inf)
                            phenotypes.append(None)
                            continue
                        
                        # Evaluate fitness
                        fitness = float(self.fitness_function(phenotype))
                        
                        # Validate fitness
                        if np.isnan(fitness) or np.isinf(fitness):
                            logger.warning(f"Invalid fitness {fitness} (gen {generation}, ind {ind_idx})")
                            self.errors.append(f"Gen {generation}, Ind {ind_idx}: Invalid fitness {fitness}")
                            fitness_scores.append(-np.inf)
                            phenotypes.append(phenotype)
                        else:
                            fitness_scores.append(fitness)
                            phenotypes.append(phenotype)
                    
                    except Exception as e:
                        error_msg = f"Gen {generation}, Ind {ind_idx}: {str(e)}"
                        logger.error(error_msg)
                        self.errors.append(error_msg)
                        self.invalid_phenotypes.append((generation, str(genotype), str(e)))
                        fitness_scores.append(-np.inf)
                        phenotypes.append(None)
        
        except Exception as e:
            logger.error(f"Batch evaluation failed: {str(e)}")
            self.errors.append(f"Batch evaluation error: {str(e)}")
            # Return worst fitness for all
            fitness_scores = [-np.inf] * len(individuals)
            phenotypes = [None] * len(individuals)
        
        return fitness_scores, phenotypes
    
    async def _evaluate_fitness_async(self,
                                     individuals: List[np.ndarray]) -> Tuple[List[float], List[Any]]:
        """Async batch evaluation (placeholder for concurrent evaluation)"""
        tasks = []
        phenotypes = []
        
        for genotype in individuals:
            phenotype = self.mapper.genotype_to_phenotype(genotype)
            is_valid, _ = self.mapper.validate_phenotype(phenotype)
            if is_valid:
                tasks.append(self._evaluate_single_async(phenotype))
                phenotypes.append(phenotype)
            else:
                tasks.append(asyncio.sleep(0))
                phenotypes.append(None)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        fitness_scores = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                fitness_scores.append(-np.inf)
            elif result is None or (phenotypes[i] is None):
                fitness_scores.append(-np.inf)
            else:
                fitness_scores.append(float(result))
        
        return fitness_scores, phenotypes
    
    async def _evaluate_single_async(self, phenotype: Any) -> float:
        """Async single phenotype evaluation"""
        try:
            fitness = float(self.fitness_function(phenotype))
            return fitness if not (np.isnan(fitness) or np.isinf(fitness)) else -np.inf
        except:
            return -np.inf
    
    def _selection_step(self, fitness_scores: List[float]) -> List[np.ndarray]:
        """Perform selection"""
        if self.config.selection_method == SelectionMethod.TOURNAMENT:
            selected, stats = GAOperators.selection_tournament(
                self.population,
                fitness_scores,
                len(self.population) // 2,
                self.config.tournament_size
            )
        elif self.config.selection_method == SelectionMethod.ROULETTE_WHEEL:
            selected, stats = GAOperators.selection_roulette_wheel(
                self.population,
                fitness_scores,
                len(self.population) // 2
            )
        elif self.config.selection_method == SelectionMethod.RANK_BASED:
            selected, stats = GAOperators.selection_rank_based(
                self.population,
                fitness_scores,
                len(self.population) // 2,
                self.config.selection_pressure
            )
        else:
            logger.warning(f"Unknown selection method {self.config.selection_method}, using tournament")
            selected, stats = GAOperators.selection_tournament(
                self.population,
                fitness_scores,
                len(self.population) // 2
            )
        
        return selected
    
    def _crossover_step(self, selected: List[np.ndarray]) -> List[np.ndarray]:
        """Perform crossover"""
        offspring = []
        crossovers_performed = 0
        
        for i in range(0, len(selected) - 1, 2):
            if np.random.random() < self.config.crossover_rate:
                if self.config.crossover_method == CrossoverMethod.SINGLE_POINT:
                    child1, child2 = GAOperators.crossover_single_point(selected[i], selected[i+1])
                elif self.config.crossover_method == CrossoverMethod.TWO_POINT:
                    child1, child2 = GAOperators.crossover_two_point(selected[i], selected[i+1])
                elif self.config.crossover_method == CrossoverMethod.UNIFORM:
                    child1, child2 = GAOperators.crossover_uniform(selected[i], selected[i+1])
                elif self.config.crossover_method == CrossoverMethod.ARITHMETIC:
                    child1, child2 = GAOperators.crossover_arithmetic(selected[i], selected[i+1])
                else:
                    child1, child2 = selected[i].copy(), selected[i+1].copy()
                
                offspring.extend([child1, child2])
                crossovers_performed += 1
            else:
                offspring.extend([selected[i].copy(), selected[i+1].copy()])
        
        # Handle odd population
        if len(selected) % 2 == 1:
            offspring.append(selected[-1].copy())
        
        logger.debug(f"Crossover: {crossovers_performed} crossovers performed")
        return offspring
    
    def _mutation_step(self, offspring: List[np.ndarray]) -> Tuple[List[np.ndarray], int]:
        """Perform mutation"""
        mutations_performed = 0
        mutated = []
        
        for ind in offspring:
            if np.random.random() < self.config.mutation_rate:
                if self.config.mutation_method == MutationMethod.GAUSSIAN:
                    mutated_ind = GAOperators.mutation_gaussian(
                        ind,
                        self.config.mutation_rate,
                        self.config.mutation_std
                    )
                elif self.config.mutation_method == MutationMethod.UNIFORM:
                    mutated_ind = GAOperators.mutation_uniform(
                        ind,
                        self.config.mutation_rate,
                        self.config.mutation_min,
                        self.config.mutation_max
                    )
                elif self.config.mutation_method == MutationMethod.ADAPTIVE:
                    mutated_ind = GAOperators.mutation_adaptive(
                        ind,
                        self.config.mutation_rate,
                        self.generation,
                        self.config.generations,
                        self.config.mutation_std
                    )
                else:
                    mutated_ind = ind.copy()
                
                mutated.append(mutated_ind)
                mutations_performed += 1
            else:
                mutated.append(ind.copy())
        
        logger.debug(f"Mutation: {mutations_performed} individuals mutated")
        return mutated, mutations_performed
    
    def _calculate_metrics(self, 
                          fitness_scores: List[float],
                          selections_performed: int,
                          crossovers_performed: int,
                          mutations_performed: int) -> GAMetrics:
        """Calculate generation metrics"""
        valid_fitness = [f for f in fitness_scores if f != -np.inf]
        
        if not valid_fitness:
            logger.warning("All fitness scores are invalid")
            valid_fitness = [0.0]
        
        best_fitness = max(valid_fitness)
        worst_fitness = min(valid_fitness)
        avg_fitness = np.mean(valid_fitness)
        
        diversity = GAOperators.calculate_population_diversity(self.population)
        
        self.best_fitness_history.append(best_fitness)
        convergence_rate = GAOperators.calculate_convergence_rate(self.best_fitness_history)
        
        metrics = GAMetrics(
            generation=self.generation,
            best_fitness=best_fitness,
            worst_fitness=worst_fitness,
            average_fitness=avg_fitness,
            population_diversity=diversity,
            selections_performed=selections_performed,
            crossovers_performed=crossovers_performed,
            mutations_performed=mutations_performed,
            convergence_rate=convergence_rate
        )
        
        return metrics
    
    def _apply_elitism(self,
                      new_population: List[np.ndarray],
                      fitness_scores: List[float]) -> List[np.ndarray]:
        """Apply elitism to preserve best individuals"""
        if self.config.elitism_rate == 0:
            return new_population
        
        num_elite = max(1, int(len(self.population) * self.config.elitism_rate))
        elite_indices = np.argsort(fitness_scores)[-num_elite:]
        
        # Replace worst individuals in new population with elite
        for i, elite_idx in enumerate(elite_indices):
            if i < len(new_population):
                new_population[i] = self.population[elite_idx].copy()
        
        logger.debug(f"Elitism: preserved {num_elite} best individuals")
        return new_population
    
    def _check_convergence(self) -> bool:
        """Check if GA has converged"""
        if not self.config.early_stopping or len(self.best_fitness_history) < 2:
            return False
        
        if len(self.best_fitness_history) < self.config.early_stopping_generations:
            return False
        
        # Check if improvements are stagnating
        recent_improvements = []
        for i in range(-self.config.early_stopping_generations, 0):
            if i > -len(self.best_fitness_history):
                improvement = abs(self.best_fitness_history[i] - self.best_fitness_history[i-1])
                recent_improvements.append(improvement)
        
        if recent_improvements and np.mean(recent_improvements) < self.config.early_stopping_threshold:
            logger.info(f"Convergence detected: improvements < {self.config.early_stopping_threshold}")
            return True
        
        return False
    
    def run(self, use_async: bool = False) -> GAResult:
        """
        Run the genetic algorithm.
        
        Args:
            use_async: Whether to use async batch evaluation
        
        Returns:
            GAResult object with all results
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting GA: {self.config}")
        logger.info(f"Population size: {len(self.population)}")
        logger.info(f"Mapper: {self.mapper.genotype_type.value}")
        
        try:
            for gen in range(self.config.generations):
                self.generation = gen
                
                # Evaluation
                logger.debug(f"Generation {gen + 1}/{self.config.generations}")
                fitness_scores, phenotypes = self._evaluate_fitness_batch(
                    self.population,
                    generation=gen,
                    use_async=use_async
                )
                
                # Store history
                self.population_history.append([ind.copy() for ind in self.population])
                self.avg_fitness_history.append(np.mean([f for f in fitness_scores if f != -np.inf]))
                
                # Selection
                selected = self._selection_step(fitness_scores)
                
                # Crossover
                offspring = self._crossover_step(selected)
                
                # Mutation
                mutated, mutations_count = self._mutation_step(offspring)
                
                # Create new population
                new_population = mutated[:len(self.population)]
                
                # Apply elitism
                new_population = self._apply_elitism(new_population, fitness_scores)
                
                # Ensure population size
                while len(new_population) < self.config.population_size:
                    new_population.append(self.mapper.create_random_genotype(len(self.population[0])))
                
                self.population = new_population[:self.config.population_size]
                
                # Calculate metrics
                metrics = self._calculate_metrics(
                    fitness_scores,
                    len(selected),
                    0,  # Will be tracked separately
                    mutations_count
                )
                self.generation_metrics.append(metrics)
                
                # Log progress
                if (gen + 1) % 10 == 0 or gen == 0:
                    logger.info(f"{metrics}")
                
                # Check convergence
                if self._check_convergence():
                    logger.info(f"GA converged at generation {gen + 1}")
                    self.generation = gen + 1
                    break
        
        except Exception as e:
            logger.error(f"Error during GA execution: {str(e)}")
            self.errors.append(f"Execution error: {str(e)}")
        
        # Get final results
        final_fitness_scores, final_phenotypes = self._evaluate_fitness_batch(
            self.population,
            generation=self.generation
        )
        
        valid_indices = [i for i, f in enumerate(final_fitness_scores) if f != -np.inf]
        if not valid_indices:
            valid_indices = [0]
            logger.warning("No valid phenotypes found")
        
        best_idx = valid_indices[np.argmax([final_fitness_scores[i] for i in valid_indices])]
        best_phenotype = final_phenotypes[best_idx]
        best_fitness = final_fitness_scores[best_idx]
        
        execution_time = time.time() - start_time
        
        result = GAResult(
            best_phenotype=best_phenotype,
            best_fitness=best_fitness,
            worst_fitness=min([f for f in final_fitness_scores if f != -np.inf]),
            average_fitness=np.mean([f for f in final_fitness_scores if f != -np.inf]),
            total_generations=self.generation + 1,
            generation_metrics=[m.to_dict() for m in self.generation_metrics],
            population_history=self.population_history,
            fitness_history=[self.best_fitness_history, self.avg_fitness_history],
            execution_time=execution_time,
            convergence_achieved=self._check_convergence(),
            errors=self.errors,
            config=self.config
        )
        
        logger.info(f"GA completed: {result}")
        return result


def test_ga_engine():
    """Test GA engine in command prompt"""
    print("\n" + "="*70)
    print("GENETIC ALGORITHM ENGINE TEST")
    print("="*70)
    
    # Define simple fitness function: minimize Sphere function
    def sphere_fitness(phenotype):
        """Sphere function: minimize sum of squares"""
        try:
            if phenotype is None:
                return -np.inf
            values = np.array(phenotype, dtype=float).flatten()
            # Negate because we want to maximize
            return -np.sum(values**2)
        except:
            return -np.inf
    
    # Setup GA
    config = GAConfig(
        population_size=20,
        generations=30,
        crossover_rate=0.8,
        mutation_rate=0.15,
        early_stopping=True,
        early_stopping_generations=5
    )
    
    mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
    
    print(f"\nConfig: {config}")
    print(f"Mapper: {mapper.genotype_type.value} (range: [{mapper.min_val}, {mapper.max_val}])")
    print(f"Fitness Function: Sphere (minimize sum of squares)")
    
    engine = GeneticAlgorithmEngine(config, sphere_fitness, mapper)
    
    print(f"\nInitial population size: {len(engine.population)}")
    
    print("\nRunning GA...")
    result = engine.run(use_async=False)
    
    print(f"\n{result}")
    print(f"\nBest phenotype found: {result.best_phenotype}")
    print(f"Best fitness: {result.best_fitness:.6f}")
    print(f"Execution time: {result.execution_time:.2f}s")
    print(f"Total errors: {len(result.errors)}")
    if result.errors:
        print(f"First few errors:")
        for err in result.errors[:3]:
            print(f"  - {err}")
    
    print(f"\nGeneration metrics (last 5):")
    for metric in result.generation_metrics[-5:]:
        print(f"  {metric}")
    
    print("\n" + "="*70)
    print("✓ GA ENGINE TEST COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    test_ga_engine()
