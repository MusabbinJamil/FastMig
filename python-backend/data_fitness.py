"""
Data Fitness and Evolutionary Data Cleaning Module
===================================================
This module provides fitness evaluation for data records and implements
various evolutionary algorithms for data imputation and cleaning.

Features:
- Fitness/Health scoring for data records
- SQLite compatibility validation
- Multiple evolutionary algorithms: GA, PSO, DE, ES
- Probability distribution preservation
- Similar value imputation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import sqlite3
from scipy import stats
from scipy.optimize import differential_evolution
import logging
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class DataFitnessEvaluator:
    """
    Evaluates the fitness/health of data records based on:
    - Missing values
    - Data type consistency
    - SQLite import compatibility
    - Data distribution alignment
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.column_types = self._infer_column_types()
        self.column_distributions = self._calculate_distributions()
        
    def _infer_column_types(self) -> Dict[str, str]:
        """Infer the expected data type for each column"""
        type_map = {}
        for col in self.df.columns:
            non_null = self.df[col].dropna()
            if len(non_null) == 0:
                type_map[col] = 'unknown'
                continue
                
            # Check if numeric
            if pd.api.types.is_numeric_dtype(non_null):
                if pd.api.types.is_integer_dtype(non_null):
                    type_map[col] = 'integer'
                else:
                    type_map[col] = 'float'
            # Check if datetime
            elif pd.api.types.is_datetime64_any_dtype(non_null):
                type_map[col] = 'datetime'
            # Check if boolean
            elif pd.api.types.is_bool_dtype(non_null):
                type_map[col] = 'boolean'
            else:
                # Try to infer from values
                try:
                    pd.to_numeric(non_null)
                    type_map[col] = 'numeric'
                except:
                    try:
                        pd.to_datetime(non_null)
                        type_map[col] = 'datetime'
                    except:
                        type_map[col] = 'string'
        
        return type_map
    
    def _calculate_distributions(self) -> Dict[str, Any]:
        """Calculate probability distributions for numeric columns"""
        distributions = {}
        for col in self.df.columns:
            if self.column_types.get(col) in ['integer', 'float', 'numeric']:
                non_null = self.df[col].dropna()
                if len(non_null) > 0:
                    try:
                        # Store statistics for the distribution
                        distributions[col] = {
                            'mean': float(non_null.mean()),
                            'std': float(non_null.std()),
                            'median': float(non_null.median()),
                            'min': float(non_null.min()),
                            'max': float(non_null.max()),
                            'quartiles': [float(q) for q in non_null.quantile([0.25, 0.5, 0.75])],
                            'mode': float(non_null.mode()[0]) if len(non_null.mode()) > 0 else float(non_null.mean())
                        }
                    except:
                        distributions[col] = None
        return distributions
    
    def evaluate_record_fitness(self, row_idx: int) -> Dict[str, Any]:
        """
        Evaluate fitness/health of a single record
        Returns a dict with overall score and component scores
        """
        row = self.df.iloc[row_idx]
        
        # Initialize scores
        missing_score = 100.0
        type_consistency_score = 100.0
        sqlite_compatibility_score = 100.0
        
        issues = []
        
        # 1. Missing values penalty
        total_cols = len(row)
        missing_cols = row.isna().sum()
        if missing_cols > 0:
            missing_score = max(0, 100 - (missing_cols / total_cols * 100))
            issues.append(f"{missing_cols} missing values")
        
        # 2. Type consistency penalty
        type_mismatches = 0
        for col, value in row.items():
            if pd.isna(value):
                continue
            
            expected_type = self.column_types.get(col, 'unknown')
            if expected_type == 'integer':
                if not isinstance(value, (int, np.integer)):
                    try:
                        int(value)
                    except:
                        type_mismatches += 1
                        issues.append(f"Type mismatch in '{col}'")
            elif expected_type == 'float':
                if not isinstance(value, (int, float, np.integer, np.floating)):
                    try:
                        float(value)
                    except:
                        type_mismatches += 1
                        issues.append(f"Type mismatch in '{col}'")
        
        if type_mismatches > 0:
            type_consistency_score = max(0, 100 - (type_mismatches / total_cols * 100))
        
        # 3. SQLite compatibility check
        sqlite_issues = self._check_sqlite_compatibility(row)
        if sqlite_issues:
            sqlite_compatibility_score = max(0, 100 - len(sqlite_issues) * 20)
            issues.extend(sqlite_issues)
        
        # Calculate overall fitness (weighted average)
        overall_fitness = (
            missing_score * 0.4 +
            type_consistency_score * 0.3 +
            sqlite_compatibility_score * 0.3
        )
        
        return {
            'overall_fitness': round(overall_fitness, 2),
            'missing_score': round(missing_score, 2),
            'type_consistency_score': round(type_consistency_score, 2),
            'sqlite_compatibility_score': round(sqlite_compatibility_score, 2),
            'issues': issues,
            'health_status': self._get_health_status(overall_fitness)
        }
    
    def evaluate_all_records(self) -> pd.DataFrame:
        """Evaluate fitness for all records"""
        results = []
        for idx in range(len(self.df)):
            fitness = self.evaluate_record_fitness(idx)
            results.append({
                'row_index': idx,
                'fitness': fitness['overall_fitness'],
                'health_status': fitness['health_status'],
                'issues_count': len(fitness['issues']),
                'missing_score': fitness['missing_score'],
                'type_score': fitness['type_consistency_score'],
                'sqlite_score': fitness['sqlite_compatibility_score']
            })
        
        return pd.DataFrame(results)
    
    def _check_sqlite_compatibility(self, row: pd.Series) -> List[str]:
        """Check if row values are compatible with SQLite"""
        issues = []
        
        for col, value in row.items():
            if pd.isna(value):
                continue
            
            # SQLite supports: NULL, INTEGER, REAL, TEXT, BLOB
            try:
                if isinstance(value, (int, np.integer)):
                    # Check for integer overflow
                    if abs(value) > 9223372036854775807:  # SQLite max integer
                        issues.append(f"Integer overflow in '{col}'")
                elif isinstance(value, (float, np.floating)):
                    if np.isinf(value) or (np.isnan(value) and not pd.isna(value)):
                        issues.append(f"Invalid float in '{col}'")
                elif isinstance(value, str):
                    # Check for problematic characters
                    if '\x00' in value:
                        issues.append(f"NULL character in '{col}'")
                    if len(value) > 1000000:  # 1MB string limit
                        issues.append(f"String too long in '{col}'")
            except:
                issues.append(f"Unhandled type in '{col}'")
        
        return issues
    
    def _get_health_status(self, fitness: float) -> str:
        """Convert fitness score to health status"""
        if fitness >= 95:
            return "Excellent"
        elif fitness >= 80:
            return "Good"
        elif fitness >= 60:
            return "Fair"
        elif fitness >= 40:
            return "Poor"
        else:
            return "Critical"


class EvolutionaryDataCleaner:
    """
    Implements various evolutionary algorithms for data imputation
    while preserving probability distributions
    """
    
    def __init__(self, df: pd.DataFrame, track_modifications: bool = True):
        self.df = df.copy()
        self.evaluator = DataFitnessEvaluator(df)
        self.original_distributions = self.evaluator.column_distributions
        self.track_modifications = track_modifications
        self.modified_records = set()  # Track which records were modified
        
        # Add tracking column if enabled and not already present
        if self.track_modifications and 'Modified_by_AI' not in self.df.columns:
            self.df['Modified_by_AI'] = False
    
    def _mark_record_as_modified(self, row_idx: int):
        """Mark a record as modified by AI"""
        if self.track_modifications:
            self.modified_records.add(row_idx)
            self.df.loc[row_idx, 'Modified_by_AI'] = True
    
    def genetic_algorithm_imputation(self, 
                                     population_size: int = 50,
                                     generations: int = 100,
                                     mutation_rate: float = 0.1,
                                     crossover_rate: float = 0.8) -> pd.DataFrame:
        """
        Genetic Algorithm for data imputation
        
        Process:
        1. Create population of candidate imputations
        2. Evaluate fitness (distribution preservation + record health)
        3. Selection, crossover, mutation
        4. Repeat for generations
        """
        logger.info("Starting Genetic Algorithm imputation...")
        
        df_cleaned = self.df.copy()
        
        # Find columns with missing values (exclude tracking column)
        cols_with_missing = [col for col in df_cleaned.columns 
                            if col != 'Modified_by_AI' and df_cleaned[col].isna().any()]
        
        for col in cols_with_missing:
            logger.info(f"Imputing column: {col}")
            
            # Get indices of missing values
            missing_idx = df_cleaned[df_cleaned[col].isna()].index.tolist()
            
            if len(missing_idx) == 0:
                continue
            
            # Get non-missing values for this column
            non_missing = df_cleaned[col].dropna().values
            
            if len(non_missing) == 0:
                continue
            
            col_type = self.evaluator.column_types.get(col, 'unknown')
            
            # Initialize population
            population = self._initialize_population(
                non_missing, missing_idx, population_size, col_type
            )
            
            best_solution = None
            best_fitness = -np.inf
            
            # Evolution loop
            for gen in range(generations):
                # Evaluate fitness
                fitness_scores = [
                    self._evaluate_imputation_fitness(df_cleaned, col, solution, non_missing)
                    for solution in population
                ]
                
                # Track best solution
                max_fitness_idx = np.argmax(fitness_scores)
                if fitness_scores[max_fitness_idx] > best_fitness:
                    best_fitness = fitness_scores[max_fitness_idx]
                    best_solution = population[max_fitness_idx].copy()
                
                # Selection
                selected = self._tournament_selection(population, fitness_scores, population_size // 2)
                
                # Crossover
                offspring = []
                for i in range(0, len(selected), 2):
                    if i + 1 < len(selected):
                        if np.random.random() < crossover_rate:
                            child1, child2 = self._crossover(selected[i], selected[i+1])
                            offspring.extend([child1, child2])
                        else:
                            offspring.extend([selected[i], selected[i+1]])
                
                # Mutation
                offspring = [self._mutate(ind, non_missing, mutation_rate, col_type) 
                           for ind in offspring]
                
                # Create new population
                population = offspring + [best_solution]
                population = population[:population_size]
            
            # Apply best solution
            for idx, value in zip(missing_idx, best_solution):
                df_cleaned.loc[idx, col] = value
                self._mark_record_as_modified(idx)
        
        logger.info("Genetic Algorithm imputation completed")
        return df_cleaned
    
    def particle_swarm_optimization(self,
                                   n_particles: int = 30,
                                   iterations: int = 100,
                                   inertia: float = 0.7,
                                   cognitive: float = 1.5,
                                   social: float = 1.5) -> pd.DataFrame:
        """
        Particle Swarm Optimization for data imputation
        
        Each particle represents a set of imputed values
        Particles move through solution space guided by:
        - Personal best position
        - Global best position
        """
        logger.info("Starting PSO imputation...")
        
        df_cleaned = self.df.copy()
        cols_with_missing = [col for col in df_cleaned.columns 
                            if col != 'Modified_by_AI' and df_cleaned[col].isna().any()]
        
        for col in cols_with_missing:
            logger.info(f"Imputing column: {col}")
            
            missing_idx = df_cleaned[df_cleaned[col].isna()].index.tolist()
            if len(missing_idx) == 0:
                continue
            
            non_missing = df_cleaned[col].dropna().values
            if len(non_missing) == 0:
                continue
            
            col_type = self.evaluator.column_types.get(col, 'unknown')
            
            # Initialize particles (positions)
            particles = self._initialize_population(non_missing, missing_idx, n_particles, col_type)
            
            # Initialize velocities
            velocities = [np.random.randn(len(missing_idx)) * 0.1 for _ in range(n_particles)]
            
            # Personal best positions and fitness
            personal_best = particles.copy()
            personal_best_fitness = [
                self._evaluate_imputation_fitness(df_cleaned, col, p, non_missing)
                for p in particles
            ]
            
            # Global best
            global_best_idx = np.argmax(personal_best_fitness)
            global_best = personal_best[global_best_idx].copy()
            global_best_fitness = personal_best_fitness[global_best_idx]
            
            # PSO iterations
            for iteration in range(iterations):
                for i in range(n_particles):
                    # Update velocity
                    r1, r2 = np.random.random(2)
                    
                    cognitive_velocity = cognitive * r1 * (personal_best[i] - particles[i])
                    social_velocity = social * r2 * (global_best - particles[i])
                    
                    velocities[i] = (inertia * velocities[i] + 
                                   cognitive_velocity + 
                                   social_velocity)
                    
                    # Update position
                    particles[i] = particles[i] + velocities[i]
                    
                    # Apply bounds (keep values similar to existing data)
                    particles[i] = self._apply_bounds(particles[i], non_missing, col_type)
                    
                    # Evaluate fitness
                    fitness = self._evaluate_imputation_fitness(
                        df_cleaned, col, particles[i], non_missing
                    )
                    
                    # Update personal best
                    if fitness > personal_best_fitness[i]:
                        personal_best[i] = particles[i].copy()
                        personal_best_fitness[i] = fitness
                        
                        # Update global best
                        if fitness > global_best_fitness:
                            global_best = particles[i].copy()
                            global_best_fitness = fitness
            
            # Apply global best solution
            for idx, value in zip(missing_idx, global_best):
                df_cleaned.loc[idx, col] = value
                self._mark_record_as_modified(idx)
        
        logger.info("PSO imputation completed")
        return df_cleaned
    
    def differential_evolution_imputation(self,
                                         pop_size: int = 30,
                                         max_iter: int = 100) -> pd.DataFrame:
        """
        Differential Evolution for data imputation
        
        Uses mutation and crossover operations to evolve solutions
        """
        logger.info("Starting Differential Evolution imputation...")
        
        df_cleaned = self.df.copy()
        cols_with_missing = [col for col in df_cleaned.columns 
                            if col != 'Modified_by_AI' and df_cleaned[col].isna().any()]
        
        for col in cols_with_missing:
            logger.info(f"Imputing column: {col}")
            
            missing_idx = df_cleaned[df_cleaned[col].isna()].index.tolist()
            if len(missing_idx) == 0:
                continue
            
            non_missing = df_cleaned[col].dropna().values
            if len(non_missing) == 0:
                continue
            
            col_type = self.evaluator.column_types.get(col, 'unknown')
            n_missing = len(missing_idx)
            
            # Define objective function (minimize negative fitness)
            def objective(x):
                x_bounded = self._apply_bounds(x, non_missing, col_type)
                fitness = self._evaluate_imputation_fitness(df_cleaned, col, x_bounded, non_missing)
                return -fitness  # Minimize negative fitness = maximize fitness
            
            # Define bounds based on data range
            if col_type in ['integer', 'float', 'numeric']:
                min_val = float(non_missing.min())
                max_val = float(non_missing.max())
                bounds = [(min_val, max_val) for _ in range(n_missing)]
            else:
                # For non-numeric, use indices to select from existing values
                bounds = [(0, len(non_missing) - 1) for _ in range(n_missing)]
            
            try:
                # Run differential evolution
                result = differential_evolution(
                    objective,
                    bounds,
                    maxiter=max_iter,
                    popsize=pop_size // n_missing if n_missing > 0 else 15,
                    seed=42,
                    workers=1
                )
                
                solution = result.x
                solution = self._apply_bounds(solution, non_missing, col_type)
                
                # Apply solution
                for idx, value in zip(missing_idx, solution):
                    df_cleaned.loc[idx, col] = value
                    self._mark_record_as_modified(idx)
                    
            except Exception as e:
                logger.warning(f"DE failed for column {col}: {e}. Using fallback method.")
                # Fallback to simple imputation
                for idx in missing_idx:
                    df_cleaned.loc[idx, col] = np.random.choice(non_missing)
                    self._mark_record_as_modified(idx)
        
        logger.info("Differential Evolution imputation completed")
        return df_cleaned
    
    def evolution_strategy_imputation(self,
                                     mu: int = 15,
                                     lambda_: int = 45,
                                     generations: int = 100) -> pd.DataFrame:
        """
        Evolution Strategy (μ, λ) for data imputation
        
        Generate λ offspring from μ parents
        Select μ best offspring as new parents
        """
        logger.info("Starting Evolution Strategy imputation...")
        
        df_cleaned = self.df.copy()
        cols_with_missing = [col for col in df_cleaned.columns 
                            if col != 'Modified_by_AI' and df_cleaned[col].isna().any()]
        
        for col in cols_with_missing:
            logger.info(f"Imputing column: {col}")
            
            missing_idx = df_cleaned[df_cleaned[col].isna()].index.tolist()
            if len(missing_idx) == 0:
                continue
            
            non_missing = df_cleaned[col].dropna().values
            if len(non_missing) == 0:
                continue
            
            col_type = self.evaluator.column_types.get(col, 'unknown')
            
            # Initialize parent population
            parents = self._initialize_population(non_missing, missing_idx, mu, col_type)
            
            best_solution = None
            best_fitness = -np.inf
            
            for gen in range(generations):
                # Generate offspring
                offspring = []
                for _ in range(lambda_):
                    # Select random parent
                    parent = parents[np.random.randint(len(parents))].copy()
                    
                    # Mutate (self-adaptive mutation)
                    sigma = 0.1 * (1 - gen / generations)  # Decrease mutation over time
                    mutated = parent + np.random.randn(len(parent)) * sigma
                    mutated = self._apply_bounds(mutated, non_missing, col_type)
                    
                    offspring.append(mutated)
                
                # Evaluate all offspring
                fitness_scores = [
                    self._evaluate_imputation_fitness(df_cleaned, col, ind, non_missing)
                    for ind in offspring
                ]
                
                # Track best
                max_idx = np.argmax(fitness_scores)
                if fitness_scores[max_idx] > best_fitness:
                    best_fitness = fitness_scores[max_idx]
                    best_solution = offspring[max_idx].copy()
                
                # Select μ best offspring as new parents
                sorted_indices = np.argsort(fitness_scores)[-mu:]
                parents = [offspring[i] for i in sorted_indices]
            
            # Apply best solution
            if best_solution is not None:
                for idx, value in zip(missing_idx, best_solution):
                    df_cleaned.loc[idx, col] = value
                    self._mark_record_as_modified(idx)
        
        logger.info("Evolution Strategy imputation completed")
        return df_cleaned
    
    def hybrid_evolutionary_imputation(self,
                                      method: str = 'auto') -> pd.DataFrame:
        """
        Hybrid approach: Uses different algorithms for different column types
        
        - Numeric columns: PSO
        - Categorical/String columns: GA
        - Mixed: Evolution Strategy
        """
        logger.info(f"Starting Hybrid Evolutionary imputation (method={method})...")
        
        df_cleaned = self.df.copy()
        cols_with_missing = [col for col in df_cleaned.columns 
                            if col != 'Modified_by_AI' and df_cleaned[col].isna().any()]
        
        for col in cols_with_missing:
            col_type = self.evaluator.column_types.get(col, 'unknown')
            
            missing_idx = df_cleaned[df_cleaned[col].isna()].index.tolist()
            if len(missing_idx) == 0:
                continue
            
            non_missing = df_cleaned[col].dropna().values
            if len(non_missing) == 0:
                continue
            
            # Choose algorithm based on column type
            if col_type in ['integer', 'float', 'numeric']:
                logger.info(f"Using PSO for numeric column: {col}")
                # Create temporary cleaner for this column only
                temp_df = pd.DataFrame({col: df_cleaned[col]})
                temp_cleaner = EvolutionaryDataCleaner(temp_df, track_modifications=False)
                cleaned_temp = temp_cleaner.particle_swarm_optimization(
                    n_particles=20, iterations=50
                )
                df_cleaned[col] = cleaned_temp[col]
                # Mark records as modified
                for idx in missing_idx:
                    self._mark_record_as_modified(idx)
            else:
                logger.info(f"Using GA for non-numeric column: {col}")
                # Create temporary cleaner for this column only
                temp_df = pd.DataFrame({col: df_cleaned[col]})
                temp_cleaner = EvolutionaryDataCleaner(temp_df, track_modifications=False)
                cleaned_temp = temp_cleaner.genetic_algorithm_imputation(
                    population_size=30, generations=50
                )
                df_cleaned[col] = cleaned_temp[col]
                # Mark records as modified
                for idx in missing_idx:
                    self._mark_record_as_modified(idx)
        
        logger.info("Hybrid Evolutionary imputation completed")
        return df_cleaned
    
    # Helper methods
    
    def _initialize_population(self, non_missing, missing_idx, pop_size, col_type):
        """Initialize population with random samples from existing data"""
        population = []
        for _ in range(pop_size):
            if col_type in ['integer', 'float', 'numeric']:
                # Sample with small random variations
                individual = np.random.choice(non_missing, size=len(missing_idx))
                # Convert to numeric array
                individual = np.array([float(x) for x in individual])
                individual = individual + np.random.randn(len(missing_idx)) * np.std([float(x) for x in non_missing]) * 0.1
            else:
                # Sample directly for categorical - keep as array of original type
                individual = np.random.choice(non_missing, size=len(missing_idx))
            
            population.append(individual)
        
        return population
    
    def _evaluate_imputation_fitness(self, df, col, imputed_values, non_missing):
        """
        Evaluate fitness of imputation based on:
        1. Distribution similarity (KS test)
        2. Statistical properties preservation
        """
        # Combine imputed with existing
        combined = np.concatenate([non_missing, imputed_values])
        
        col_type = self.evaluator.column_types.get(col, 'unknown')
        
        if col_type in ['integer', 'float', 'numeric']:
            # Statistical similarity
            try:
                # Kolmogorov-Smirnov test for distribution similarity
                ks_stat, _ = stats.ks_2samp(non_missing, combined)
                distribution_score = 1 - ks_stat  # Lower KS stat = more similar
            except:
                distribution_score = 0.5
            
            # Mean and std preservation
            mean_diff = abs(np.mean(non_missing) - np.mean(combined)) / (np.std(non_missing) + 1e-6)
            std_diff = abs(np.std(non_missing) - np.std(combined)) / (np.std(non_missing) + 1e-6)
            
            stat_score = 1 / (1 + mean_diff + std_diff)
            
            fitness = 0.6 * distribution_score + 0.4 * stat_score
        else:
            # For categorical: check value frequencies
            original_unique = len(np.unique(non_missing))
            combined_unique = len(np.unique(combined))
            
            # Penalize if introducing too many new unique values
            uniqueness_score = min(1.0, original_unique / (combined_unique + 1))
            
            fitness = uniqueness_score
        
        return fitness
    
    def _tournament_selection(self, population, fitness_scores, n_selected):
        """Tournament selection"""
        selected = []
        for _ in range(n_selected):
            tournament_idx = np.random.choice(len(population), size=3, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_idx]
            winner_idx = tournament_idx[np.argmax(tournament_fitness)]
            selected.append(population[winner_idx].copy())
        return selected
    
    def _crossover(self, parent1, parent2):
        """Single-point crossover"""
        point = np.random.randint(1, len(parent1))
        child1 = np.concatenate([parent1[:point], parent2[point:]])
        child2 = np.concatenate([parent2[:point], parent1[point:]])
        return child1, child2
    
    def _mutate(self, individual, non_missing, mutation_rate, col_type):
        """Mutation operation"""
        mutated = individual.copy()
        for i in range(len(mutated)):
            if np.random.random() < mutation_rate:
                if col_type in ['integer', 'float', 'numeric']:
                    # Add Gaussian noise
                    mutated[i] += np.random.randn() * np.std(non_missing) * 0.2
                else:
                    # Replace with random existing value
                    mutated[i] = np.random.choice(non_missing)
        return mutated
    
    def _apply_bounds(self, values, non_missing, col_type):
        """Apply bounds to keep values within reasonable range"""
        if col_type == 'integer':
            min_val = np.min(non_missing)
            max_val = np.max(non_missing)
            values = np.clip(values, min_val, max_val)
            values = np.round(values).astype(int)
        elif col_type in ['float', 'numeric']:
            min_val = np.min(non_missing)
            max_val = np.max(non_missing)
            values = np.clip(values, min_val, max_val)
        else:
            # For categorical, select nearest existing value
            values = [non_missing[int(np.clip(i, 0, len(non_missing) - 1))] 
                     for i in np.round(values).astype(int)]
            values = np.array(values)
        
        return values


def evaluate_data_fitness(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Main function to evaluate fitness of entire dataset
    Returns detailed fitness report
    """
    evaluator = DataFitnessEvaluator(df)
    fitness_df = evaluator.evaluate_all_records()
    
    # Calculate summary statistics
    summary = {
        'total_records': len(df),
        'average_fitness': float(fitness_df['fitness'].mean()),
        'min_fitness': float(fitness_df['fitness'].min()),
        'max_fitness': float(fitness_df['fitness'].max()),
        'excellent_records': int((fitness_df['fitness'] >= 95).sum()),
        'good_records': int((fitness_df['fitness'] >= 80).sum() - (fitness_df['fitness'] >= 95).sum()),
        'fair_records': int((fitness_df['fitness'] >= 60).sum() - (fitness_df['fitness'] >= 80).sum()),
        'poor_records': int((fitness_df['fitness'] >= 40).sum() - (fitness_df['fitness'] >= 60).sum()),
        'critical_records': int((fitness_df['fitness'] < 40).sum()),
        'records_needing_cleaning': int((fitness_df['fitness'] < 100).sum()),
        'fitness_distribution': fitness_df['fitness'].tolist(),
        'detailed_results': fitness_df.to_dict('records')
    }
    
    return summary


def clean_data_evolutionary(df: pd.DataFrame, 
                            method: str = 'ga',
                            track_modifications: bool = True,
                            **kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Main function to clean data using evolutionary algorithms
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe with missing/inconsistent data
    method : str
        Algorithm to use: 'ga', 'pso', 'de', 'es', 'hybrid'
    track_modifications : bool
        If True, adds 'Modified_by_AI' column to track AI-modified records
    **kwargs : dict
        Algorithm-specific parameters
    
    Returns:
    --------
    cleaned_df : pd.DataFrame
        Cleaned dataframe (includes 'Modified_by_AI' column if track_modifications=True)
    report : dict
        Cleaning report with before/after metrics
    """
    # Evaluate before cleaning
    evaluator_before = DataFitnessEvaluator(df)
    fitness_before = evaluator_before.evaluate_all_records()
    
    # Initialize cleaner
    cleaner = EvolutionaryDataCleaner(df, track_modifications=track_modifications)
    
    # Apply selected algorithm
    if method.lower() == 'ga':
        cleaned_df = cleaner.genetic_algorithm_imputation(**kwargs)
    elif method.lower() == 'pso':
        cleaned_df = cleaner.particle_swarm_optimization(**kwargs)
    elif method.lower() == 'de':
        cleaned_df = cleaner.differential_evolution_imputation(**kwargs)
    elif method.lower() == 'es':
        cleaned_df = cleaner.evolution_strategy_imputation(**kwargs)
    elif method.lower() == 'hybrid':
        cleaned_df = cleaner.hybrid_evolutionary_imputation(**kwargs)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'ga', 'pso', 'de', 'es', or 'hybrid'")
    
    # Evaluate after cleaning
    evaluator_after = DataFitnessEvaluator(cleaned_df)
    fitness_after = evaluator_after.evaluate_all_records()
    
    # Generate report
    report = {
        'method': method,
        'before': {
            'average_fitness': float(fitness_before['fitness'].mean()),
            'records_with_issues': int((fitness_before['fitness'] < 100).sum())
        },
        'after': {
            'average_fitness': float(fitness_after['fitness'].mean()),
            'records_with_issues': int((fitness_after['fitness'] < 100).sum())
        },
        'improvement': {
            'fitness_increase': float(fitness_after['fitness'].mean() - fitness_before['fitness'].mean()),
            'records_fixed': int((fitness_before['fitness'] < 100).sum() - (fitness_after['fitness'] < 100).sum())
        },
        'modifications': {
            'tracked': track_modifications,
            'records_modified': len(cleaner.modified_records) if track_modifications else None,
            'modification_rate': f"{len(cleaner.modified_records) / len(df) * 100:.2f}%" if track_modifications else None
        }
    }
    
    return cleaned_df, report


if __name__ == '__main__':
    # Example usage
    print("Data Fitness and Evolutionary Cleaning Module")
    print("=" * 60)
    print("\nThis module provides:")
    print("1. Fitness evaluation for data records")
    print("2. Multiple evolutionary algorithms for data cleaning:")
    print("   - Genetic Algorithm (GA)")
    print("   - Particle Swarm Optimization (PSO)")
    print("   - Differential Evolution (DE)")
    print("   - Evolution Strategy (ES)")
    print("   - Hybrid approach")
    print("\nImport this module in your server.py to enable these features.")
