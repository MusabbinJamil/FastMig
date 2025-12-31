"""
Genetic Algorithm Fitness Evolver for Data Cleaning
====================================================
Integrates GA with data fitness evaluation to evolve
unhealthy records toward 100% health using healthy
records as evolutionary templates.

Key Features:
  - Identifies unhealthy records (health score < threshold)
  - Selects healthy records as evolutionary reference population
  - Configurable population sizes for user control
  - Evolves unhealthy records to match healthy record patterns
  - Tracks modifications and improvements
  - Returns evolved DataFrame with fitness metrics

Usage:
    from ga_fitness_evolver import DataFitnessEvolverGA, PopulationConfig
    
    # Initialize
    evolver = DataFitnessEvolverGA(df, track_modifications=True)
    
    # Analyze
    analysis = evolver.analyze_population(fitness_threshold=85.0)
    
    # Select populations
    config = evolver.select_populations(
        fitness_threshold=85.0,
        healthy_sample_size=1000
    )
    
    # Evolve
    evolved_df, results = evolver.evolve_unhealthy_records(
        config,
        ga_config=GAConfig(population_size=50, generations=100)
    )
"""

import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Optional, Any
from pathlib import Path

from data_fitness import DataFitnessEvaluator
from ga_engine import GeneticAlgorithmEngine
from ga_genotype_phenotype import RealValuedMapper
from ga_operators import GAConfig, SelectionMethod

logger = logging.getLogger(__name__)


@dataclass
class PopulationConfig:
    """Configuration for population selection"""
    unhealthy_indices: List[int]
    healthy_indices: List[int]
    unhealthy_count: int
    healthy_count: int
    target_columns: List[str]
    fitness_threshold: float
    column_bounds: Dict[str, Tuple[float, float]]
    
    def __repr__(self):
        return (f"PopulationConfig("
                f"unhealthy={self.unhealthy_count}, "
                f"healthy={self.healthy_count}, "
                f"columns={len(self.target_columns)}, "
                f"threshold={self.fitness_threshold})")


class DataFitnessEvolverGA:
    """Main class for GA-based data fitness evolution"""
    
    def __init__(self, df: pd.DataFrame, track_modifications: bool = True):
        """
        Initialize the evolver with a dataset.
        
        Args:
            df: DataFrame to evolve
            track_modifications: Whether to track which records were modified
        """
        self.df = df.copy()
        self.track_modifications = track_modifications
        self.fitness_evaluator = DataFitnessEvaluator(df)
        self.evolution_history = []
        
        logger.info(f"Initialized DataFitnessEvolverGA with {len(df)} records")
    
    def analyze_population(self, fitness_threshold: float = 85.0) -> Dict[str, Any]:
        """
        Analyze the population's fitness distribution.
        
        Args:
            fitness_threshold: Score threshold for "healthy" (0-100 scale)
        
        Returns:
            Dictionary with analysis metrics
        """
        logger.info(f"Analyzing population with threshold={fitness_threshold}")
        
        # Calculate fitness for all records
        fitness_scores = []
        for idx in range(len(self.df)):
            try:
                result = self.fitness_evaluator.evaluate_record_fitness(idx)
                score = result['overall_fitness']
                fitness_scores.append(score)
            except Exception as e:
                logger.warning(f"Could not calculate fitness for record {idx}: {e}")
                fitness_scores.append(0)
        
        fitness_scores = np.array(fitness_scores)
        
        # Categorize
        unhealthy = fitness_scores < fitness_threshold
        healthy = fitness_scores >= fitness_threshold
        
        unhealthy_count = unhealthy.sum()
        healthy_count = healthy.sum()
        
        # Distribution
        distribution = {}
        for threshold in [50, 75, 85, 95, 100]:
            count = (fitness_scores >= threshold).sum()
            distribution[f"{threshold}+"] = int(count)
        
        analysis = {
            'total_records': len(self.df),
            'healthy_records': int(healthy_count),
            'unhealthy_records': int(unhealthy_count),
            'healthy_percentage': float((healthy_count / len(self.df)) * 100),
            'unhealthy_percentage': float((unhealthy_count / len(self.df)) * 100),
            'fitness_scores': fitness_scores,
            'fitness_threshold': fitness_threshold,
            'avg_fitness': float(fitness_scores.mean()),
            'min_fitness': float(fitness_scores.min()),
            'max_fitness': float(fitness_scores.max()),
            'std_fitness': float(fitness_scores.std()),
            'fitness_distribution': distribution,
            'unhealthy_indices': np.where(unhealthy)[0].tolist(),
            'healthy_indices': np.where(healthy)[0].tolist(),
        }
        
        logger.info(f"Population analysis: {unhealthy_count} unhealthy, {healthy_count} healthy")
        return analysis
    
    def select_populations(self,
                          fitness_threshold: float = 85.0,
                          healthy_sample_size: Optional[int] = None) -> PopulationConfig:
        """
        Select unhealthy and healthy populations.
        
        Args:
            fitness_threshold: Score threshold for "healthy"
            healthy_sample_size: How many healthy records to sample.
                                If None, use all. If > total, use all.
        
        Returns:
            PopulationConfig with selected populations
        """
        logger.info(f"Selecting populations (threshold={fitness_threshold}, sample_size={healthy_sample_size})")
        
        # Get fitness scores
        fitness_scores = []
        for idx in range(len(self.df)):
            try:
                result = self.fitness_evaluator.evaluate_record_fitness(idx)
                score = result['overall_fitness']
                fitness_scores.append(score)
            except:
                fitness_scores.append(0)
        
        fitness_scores = np.array(fitness_scores)
        
        # Identify populations
        unhealthy_mask = fitness_scores < fitness_threshold
        healthy_mask = fitness_scores >= fitness_threshold
        
        unhealthy_indices = np.where(unhealthy_mask)[0].tolist()
        healthy_indices = np.where(healthy_mask)[0].tolist()
        
        # Sample healthy if requested
        if healthy_sample_size is not None and len(healthy_indices) > 0:
            healthy_sample_size = min(healthy_sample_size, len(healthy_indices))
            healthy_indices = np.random.choice(
                healthy_indices,
                size=healthy_sample_size,
                replace=False
            ).tolist()
        
        # Identify numeric columns that can be evolved
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude ID columns
        target_columns = [col for col in numeric_cols if 'id' not in col.lower()]
        
        # Get column bounds from healthy records
        column_bounds = {}
        if len(healthy_indices) > 0:
            healthy_df = self.df.iloc[healthy_indices]
            for col in target_columns:
                col_min = healthy_df[col].min()
                col_max = healthy_df[col].max()
                column_bounds[col] = (float(col_min), float(col_max))
        else:
            # Use full dataset bounds
            for col in target_columns:
                col_min = self.df[col].min()
                col_max = self.df[col].max()
                column_bounds[col] = (float(col_min), float(col_max))
        
        config = PopulationConfig(
            unhealthy_indices=unhealthy_indices,
            healthy_indices=healthy_indices,
            unhealthy_count=len(unhealthy_indices),
            healthy_count=len(healthy_indices),
            target_columns=target_columns,
            fitness_threshold=fitness_threshold,
            column_bounds=column_bounds
        )
        
        logger.info(f"Selected {config.unhealthy_count} unhealthy, "
                   f"{config.healthy_count} healthy records, "
                   f"{len(target_columns)} evolution columns")
        
        return config
    
    def evolve_unhealthy_records(self,
                                 config: PopulationConfig,
                                 ga_config: Optional[GAConfig] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Evolve unhealthy records toward healthy patterns using GA.
        
        Args:
            config: PopulationConfig from select_populations()
            ga_config: GAConfig for GA parameters. If None, uses defaults.
        
        Returns:
            Tuple of (evolved_dataframe, results_dictionary)
        """
        if ga_config is None:
            ga_config = GAConfig(
                population_size=20,
                generations=50,
                early_stopping=True,
                early_stopping_generations=5
            )
        
        logger.info(f"Starting evolution: {config.unhealthy_count} records, "
                   f"GA config: pop_size={ga_config.population_size}, gens={ga_config.generations}")
        
        if config.unhealthy_count == 0:
            logger.warning("No unhealthy records to evolve")
            return self.df.copy(), {"evolved_records": 0}
        
        evolved_df = self.df.copy()
        detailed_results = []
        
        # Track fitness before evolution
        fitness_before = []
        for idx in config.unhealthy_indices:
            try:
                result = self.fitness_evaluator.evaluate_record_fitness(idx)
                score = result['overall_fitness']
                fitness_before.append(score)
            except:
                fitness_before.append(0)
        
        # Evolve each unhealthy record
        for record_idx, unhealthy_idx in enumerate(config.unhealthy_indices, 1):
            unhealthy_record = self.df.iloc[unhealthy_idx].copy()
            healthy_records = self.df.iloc[config.healthy_indices]
            
            # Create fitness function
            def record_fitness_func(phenotype: np.ndarray) -> float:
                """Fitness = similarity to healthy records' average values"""
                try:
                    # Compare to average of healthy records
                    healthy_avg = healthy_records[config.target_columns].mean()
                    
                    # Normalize differences
                    differences = 0
                    for i, col in enumerate(config.target_columns):
                        col_min, col_max = config.column_bounds[col]
                        col_range = col_max - col_min if col_max > col_min else 1
                        
                        # Difference as percentage of range
                        diff = abs(phenotype[i] - healthy_avg.iloc[i]) / col_range if col_range > 0 else 0
                        differences += diff
                    
                    # Fitness: how close to healthy average (higher = better)
                    avg_difference = differences / len(config.target_columns)
                    fitness = max(0, 100 * (1 - avg_difference))
                    return fitness
                
                except Exception as e:
                    logger.debug(f"Fitness calculation error: {e}")
                    return 0
            
            # Create mapper for this record
            initial_phenotype = unhealthy_record[config.target_columns].values.astype(float)
            mapper = RealValuedMapper(
                min_val=0.0, 
                max_val=100.0
            )
            
            # Create GA engine
            try:
                engine = GeneticAlgorithmEngine(
                    config=ga_config,
                    fitness_function=record_fitness_func,
                    genotype_mapper=mapper,
                    population=None
                )
                
                # Run evolution
                ga_result = engine.run(use_async=False)
                
                # Apply evolved values back to record
                evolved_values = ga_result.best_phenotype
                if evolved_values is not None:
                    for i, col in enumerate(config.target_columns):
                        if i < len(evolved_values):
                            # Clip to column bounds
                            col_min, col_max = config.column_bounds[col]
                            evolved_val = np.clip(evolved_values[i], col_min, col_max)
                            evolved_df.at[unhealthy_idx, col] = evolved_val
                
                # Mark as modified if tracking
                if self.track_modifications and 'Modified_by_AI' not in evolved_df.columns:
                    evolved_df['Modified_by_AI'] = 'No'
                if self.track_modifications:
                    evolved_df.at[unhealthy_idx, 'Modified_by_AI'] = 'Yes'
                
                # Calculate new fitness
                try:
                    new_result = self.fitness_evaluator.evaluate_record_fitness(unhealthy_idx)
                    new_score = new_result['overall_fitness']
                except:
                    new_score = 0
                
                original_score = fitness_before[record_idx - 1] if record_idx - 1 < len(fitness_before) else 0
                
                detail = {
                    'record_index': unhealthy_idx,
                    'original_fitness': float(original_score),
                    'evolved_fitness': float(new_score),
                    'improvement': float(new_score - original_score),
                    'generations': ga_result.generation,
                    'converged': ga_result.converged if hasattr(ga_result, 'converged') else False,
                }
                detailed_results.append(detail)
                
                if record_idx % max(1, len(config.unhealthy_indices) // 5) == 0:
                    logger.info(f"Evolved {record_idx}/{config.unhealthy_count} records")
            
            except Exception as e:
                logger.warning(f"Failed to evolve record {unhealthy_idx}: {e}")
                detail = {
                    'record_index': unhealthy_idx,
                    'original_fitness': float(fitness_before[record_idx - 1]) if record_idx - 1 < len(fitness_before) else 0,
                    'evolved_fitness': float(fitness_before[record_idx - 1]) if record_idx - 1 < len(fitness_before) else 0,
                    'improvement': 0.0,
                    'generations': 0,
                    'converged': False,
                    'error': str(e)
                }
                detailed_results.append(detail)
        
        # Calculate summary metrics
        improvements = [r['improvement'] for r in detailed_results if 'error' not in r]
        avg_improvement = float(np.mean(improvements)) if improvements else 0.0
        
        fitness_after = []
        for idx in config.unhealthy_indices:
            try:
                result = self.fitness_evaluator.evaluate_record_fitness(idx)
                score = result['overall_fitness']
                fitness_after.append(score)
            except:
                fitness_after.append(0)
        
        records_at_target = sum(1 for f in fitness_after if f >= 90)  # 90+ = good
        
        results = {
            'evolved_records': len([r for r in detailed_results if 'error' not in r]),
            'fitness_metrics': {
                'avg_initial_fitness': float(np.mean(fitness_before)) if fitness_before else 0,
                'avg_evolved_fitness': float(np.mean(fitness_after)) if fitness_after else 0,
                'improvement': avg_improvement,
                'records_at_target': int(records_at_target),
                'target_achievement_rate': (records_at_target / len(fitness_after) * 100) if fitness_after else 0,
                'min_improvement': float(min(improvements)) if improvements else 0,
                'max_improvement': float(max(improvements)) if improvements else 0,
            },
            'detailed_results': detailed_results,
            'evolution_configs': {
                'unhealthy_count': config.unhealthy_count,
                'healthy_count': config.healthy_count,
                'target_columns': config.target_columns,
                'ga_config': str(ga_config)
            }
        }
        
        logger.info(f"Evolution complete: avg improvement = {avg_improvement:.2f}, "
                   f"records at target = {records_at_target}/{len(fitness_after)}")
        
        return evolved_df, results


# Convenience function for quick evolution
def evolve_records(df: pd.DataFrame,
                  fitness_threshold: float = 85.0,
                  healthy_sample_size: Optional[int] = None,
                  ga_config: Optional[GAConfig] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Quick function to evolve unhealthy records in a DataFrame.
    
    Args:
        df: Input DataFrame
        fitness_threshold: Health score threshold (0-100)
        healthy_sample_size: How many healthy records to use as templates
        ga_config: GA configuration (uses defaults if None)
    
    Returns:
        Tuple of (evolved_df, results)
    
    Example:
        evolved_df, results = evolve_records(df, fitness_threshold=85.0, healthy_sample_size=1000)
        print(f"Improved by {results['fitness_metrics']['improvement']:.2f} points")
    """
    evolver = DataFitnessEvolverGA(df, track_modifications=True)
    config = evolver.select_populations(fitness_threshold, healthy_sample_size)
    evolved_df, results = evolver.evolve_unhealthy_records(config, ga_config)
    return evolved_df, results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("DataFitnessEvolverGA module loaded successfully")
    print("Use: from ga_fitness_evolver import DataFitnessEvolverGA, PopulationConfig")
