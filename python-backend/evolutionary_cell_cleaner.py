"""
Evolutionary Cell Cleaner Pipeline
===================================
Evolves corrupted/error cells to become healthy using evolutionary algorithms.
Each algorithm uses its unique mechanism:
- GA: Crossover and mutation from healthy cell populations
- PSO: Velocity-based particle movement towards healthy cell values
- DE: Differential evolution with vector differences from healthy cells
- ES: Evolution strategy with self-adaptive mutation

The pipeline:
1. Takes error cells detected by DataQualityAnalyzer
2. Groups healthy cells per column as templates
3. Evolves each error cell using the selected algorithm
4. Validates improvements and tracks modifications
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats
import random
from datetime import datetime, timedelta
import re

# Import new PSO and DE engines
from pso_operators import PSOConfig, PSOTopology, PSOVariant, ConstraintHandling as PSOConstraintHandling
from pso_engine import ParticleSwarmOptimizer
from de_operators import DEConfig, DEMutationStrategy, DECrossoverType, ConstraintHandling as DEConstraintHandling
from de_engine import DifferentialEvolutionOptimizer

logger = logging.getLogger(__name__)

# Standard datetime output format
STANDARD_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Common datetime formats to try when parsing
DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%d %b %Y",
    "%d %B %Y",
    "%b %d, %Y",
    "%B %d, %Y",
]


def parse_datetime(value: Any) -> Optional[datetime]:
    """
    Parse a value into a datetime object, trying multiple formats.
    Returns None if parsing fails.
    """
    if value is None or pd.isna(value):
        return None

    # If already a datetime
    if isinstance(value, datetime):
        return value

    # If pandas Timestamp
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    # Handle numeric timestamps (nanoseconds, milliseconds, or seconds since epoch)
    # Only convert if the value is large enough to be a reasonable timestamp
    if isinstance(value, (int, float)):
        try:
            numeric_val = float(value)
            # Determine the unit based on magnitude
            # Nanoseconds: typically > 1e15 (year ~2001+)
            # Milliseconds: typically > 1e12
            # Seconds: typically > 1e9 (year ~2001+)
            # Small numbers (< 1e9) are likely regular data, not timestamps
            if abs(numeric_val) > 1e15:  # Nanoseconds (pandas datetime64[ns])
                return datetime.fromtimestamp(numeric_val / 1e9)
            elif abs(numeric_val) > 1e12:  # Milliseconds
                return datetime.fromtimestamp(numeric_val / 1e3)
            elif abs(numeric_val) > 1e9:  # Seconds (year ~2001+)
                return datetime.fromtimestamp(numeric_val)
            # Don't convert small numbers - they're likely regular numeric data
        except (ValueError, OSError, OverflowError):
            pass

    # Try string parsing
    value_str = str(value).strip()
    if not value_str:
        return None

    # Check if the string looks like a numeric timestamp (exponential notation)
    # e.g., "1.7047584e+18"
    try:
        numeric_val = float(value_str)
        if abs(numeric_val) > 1e15:  # Nanoseconds
            return datetime.fromtimestamp(numeric_val / 1e9)
        elif abs(numeric_val) > 1e12:  # Milliseconds
            return datetime.fromtimestamp(numeric_val / 1e3)
        elif abs(numeric_val) > 1e9:  # Seconds
            return datetime.fromtimestamp(numeric_val)
    except (ValueError, OSError, OverflowError):
        pass

    # Try pandas first (it's very flexible)
    try:
        parsed = pd.to_datetime(value_str)
        if pd.notna(parsed):
            return parsed.to_pydatetime()
    except:
        pass

    # Try explicit formats
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value_str, fmt)
        except ValueError:
            continue

    return None


def format_datetime(dt: datetime, output_format: str = STANDARD_DATETIME_FORMAT) -> str:
    """Format a datetime object to a standardized string format."""
    if dt is None:
        return ""
    return dt.strftime(output_format)


def is_datetime_column(values: np.ndarray, threshold: float = 0.6) -> bool:
    """
    Check if an array of values represents datetime data.
    Returns True if at least `threshold` fraction can be parsed as datetime.
    """
    if len(values) == 0:
        return False

    parseable_count = 0
    sample_size = min(len(values), 20)  # Check up to 20 values
    sample = np.random.choice(values, size=sample_size, replace=False) if len(values) > sample_size else values

    for val in sample:
        if parse_datetime(val) is not None:
            parseable_count += 1

    return (parseable_count / len(sample)) >= threshold


class EvolutionMethod(Enum):
    GA = "ga"
    PSO = "pso"
    DE = "de"
    ES = "es"
    HYBRID = "hybrid"


@dataclass
class CellEvolutionConfig:
    """Configuration for cell evolution"""
    # Common parameters
    population_size: int = 30
    generations: int = 50
    fitness_threshold: float = 0.95  # Target fitness for evolved cells

    # GA parameters
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    tournament_size: int = 3
    elitism_count: int = 2

    # PSO parameters
    inertia_weight: float = 0.7
    inertia_min: float = 0.4          # For decay variant
    inertia_max: float = 0.9          # For decay variant
    cognitive_coeff: float = 1.5      # c1 - Personal best attraction
    social_coeff: float = 1.5         # c2 - Global best attraction
    velocity_clamp: float = 0.2       # Max velocity as fraction of range
    pso_topology: str = "gbest"       # gbest, lbest, ring, random, von_neumann
    pso_variant: str = "standard"     # standard, constriction, inertia_decay
    constriction_factor: float = 0.729
    neighborhood_size: int = 3

    # DE parameters
    differential_weight: float = 0.8  # F parameter (scale factor)
    crossover_prob: float = 0.9       # CR parameter
    de_mutation_strategy: str = "DE/rand/1"  # rand/1, rand/2, best/1, best/2, current-to-best/1, current-to-rand/1
    de_crossover_type: str = "binomial"      # binomial, exponential
    adaptive_f: bool = False          # Enable adaptive F
    adaptive_cr: bool = False         # Enable adaptive CR
    f_min: float = 0.1
    f_max: float = 1.0
    cr_min: float = 0.1
    cr_max: float = 1.0

    # ES parameters
    mu: int = 10      # Number of parents
    lambda_: int = 30  # Number of offspring
    initial_sigma: float = 0.3  # Initial mutation strength

    # Early stopping
    early_stopping: bool = True
    patience: int = 10
    min_improvement: float = 0.001


@dataclass
class ErrorCell:
    """Represents a single error cell"""
    row: int
    col: int
    col_name: str
    original_value: Any
    issues: List[str]
    evolved_value: Any = None
    fitness_before: float = 0.0
    fitness_after: float = 0.0
    evolution_method: str = ""


@dataclass
class EvolutionResult:
    """Results from cell evolution"""
    cells_evolved: int = 0
    cells_fixed: int = 0
    cells_failed: int = 0
    average_fitness_before: float = 0.0
    average_fitness_after: float = 0.0
    fitness_improvement: float = 0.0
    method_used: str = ""
    generations_run: int = 0
    converged: bool = False
    evolved_cells: List[ErrorCell] = field(default_factory=list)
    fitness_history: List[Dict] = field(default_factory=list)


class EvolutionaryCellCleaner:
    """
    Evolves corrupted/error cells using healthy cells as templates.
    Each algorithm uses its unique evolutionary mechanism.
    """

    def __init__(self, df: pd.DataFrame, error_cells: List[Dict],
                 config: Optional[CellEvolutionConfig] = None):
        """
        Initialize the cell cleaner.

        Args:
            df: DataFrame with data
            error_cells: List of error cells from DataQualityAnalyzer
                        Format: [{'row': int, 'col': int, 'issues': List[str]}, ...]
            config: Evolution configuration
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.error_cells = error_cells
        self.config = config or CellEvolutionConfig()

        # Group error cells by column for batch processing
        self.error_cells_by_column: Dict[int, List[Dict]] = {}
        for cell in error_cells:
            col_idx = cell['col']
            if col_idx not in self.error_cells_by_column:
                self.error_cells_by_column[col_idx] = []
            self.error_cells_by_column[col_idx].append(cell)

        # Extract healthy cells per column (cells NOT in error list)
        self.healthy_cells_by_column: Dict[int, np.ndarray] = {}
        self._extract_healthy_cells()

        # Track modifications
        self.modifications: List[ErrorCell] = []

        logger.info(f"Initialized EvolutionaryCellCleaner with {len(error_cells)} error cells across {len(self.error_cells_by_column)} columns")

    def _extract_healthy_cells(self):
        """Extract healthy (non-error) cells for each column"""
        error_rows_by_col = {}
        for cell in self.error_cells:
            col_idx = cell['col']
            if col_idx not in error_rows_by_col:
                error_rows_by_col[col_idx] = set()
            # Subtract 1 from row index because DataQualityAnalyzer adds +1 for display
            # (row 0 in display = headers, row 1 in display = DataFrame index 0)
            df_row_idx = cell['row'] - 1
            error_rows_by_col[col_idx].add(df_row_idx)

        for col_idx in range(len(self.df.columns)):
            col_name = self.df.columns[col_idx]
            error_rows = error_rows_by_col.get(col_idx, set())

            # Get all non-error, non-null values
            healthy_mask = ~self.df.index.isin(error_rows) & self.df[col_name].notna()
            healthy_values = self.df.loc[healthy_mask, col_name].values

            # For numeric columns or columns that look numeric, filter to only numeric values
            # This handles mixed-type columns better
            if pd.api.types.is_numeric_dtype(self.df[col_name]):
                try:
                    healthy_values = healthy_values.astype(float)
                    healthy_values = healthy_values[~np.isnan(healthy_values)]
                except (ValueError, TypeError):
                    # Column has mixed types, filter to only numeric values
                    numeric_values = []
                    for v in healthy_values:
                        try:
                            if v is not None and not pd.isna(v):
                                numeric_values.append(float(v))
                        except (ValueError, TypeError):
                            pass
                    healthy_values = np.array(numeric_values) if numeric_values else np.array([])
            else:
                # For non-numeric columns, try to detect if most values are numeric
                # and if so, extract only numeric values for comparison
                numeric_count = 0
                string_count = 0
                for v in healthy_values:
                    try:
                        if v is not None and not pd.isna(v):
                            float(v)
                            numeric_count += 1
                    except (ValueError, TypeError):
                        string_count += 1

                # If majority are numeric, treat as numeric column
                if numeric_count > string_count and numeric_count > 0:
                    numeric_values = []
                    for v in healthy_values:
                        try:
                            if v is not None and not pd.isna(v):
                                numeric_values.append(float(v))
                        except (ValueError, TypeError):
                            pass
                    healthy_values = np.array(numeric_values) if numeric_values else np.array([])
                else:
                    # Keep as string array, but convert all to strings for consistency
                    healthy_values = np.array([str(v) for v in healthy_values if v is not None and not pd.isna(v)])

            self.healthy_cells_by_column[col_idx] = healthy_values
            logger.debug(f"Column {col_name}: {len(healthy_values)} healthy cells, {len(error_rows)} error cells")

    def evolve(self, method: EvolutionMethod = EvolutionMethod.HYBRID) -> Tuple[pd.DataFrame, EvolutionResult]:
        """
        Evolve all error cells using the specified method.

        Args:
            method: Evolution method to use

        Returns:
            Tuple of (evolved DataFrame, EvolutionResult)
        """
        logger.info(f"Starting cell evolution using {method.value.upper()}")

        result = EvolutionResult(method_used=method.value)
        evolved_df = self.df.copy()

        # Process each column with errors
        for col_idx, error_cells in self.error_cells_by_column.items():
            col_name = self.df.columns[col_idx]
            healthy_cells = self.healthy_cells_by_column.get(col_idx, np.array([]))

            if len(healthy_cells) < 3:
                logger.warning(f"Column {col_name}: Not enough healthy cells ({len(healthy_cells)}), skipping evolution")
                result.cells_failed += len(error_cells)
                continue

            # Determine column type based on the healthy cells we extracted
            # Check datetime first, then numeric, then categorical
            is_numeric = False
            is_datetime = False

            # Check if it's a datetime column first
            if len(healthy_cells) > 0:
                # Check if pandas already detected it as datetime
                original_col = self.df[col_name]
                if pd.api.types.is_datetime64_any_dtype(original_col):
                    is_datetime = True
                    logger.info(f"Column '{col_name}' detected as datetime (pandas dtype)")
                else:
                    # Try to detect datetime from values
                    if is_datetime_column(healthy_cells):
                        is_datetime = True
                        logger.info(f"Column '{col_name}' detected as datetime (value analysis)")

            # If not datetime, check if numeric
            if not is_datetime and len(healthy_cells) > 0:
                try:
                    # Check if healthy cells are numeric (floats)
                    if healthy_cells.dtype in [np.float64, np.float32, np.int64, np.int32]:
                        is_numeric = True
                    else:
                        # Try to convert a sample to float
                        test_val = healthy_cells[0]
                        float(test_val)
                        is_numeric = True
                except (ValueError, TypeError):
                    is_numeric = False

            # Select appropriate method for this column
            actual_method = method
            if method == EvolutionMethod.HYBRID:
                if is_datetime:
                    actual_method = EvolutionMethod.GA   # GA for datetime (uses temporal proximity)
                elif is_numeric:
                    actual_method = EvolutionMethod.PSO  # PSO best for numeric
                else:
                    actual_method = EvolutionMethod.GA   # GA best for categorical

            col_type = "datetime" if is_datetime else ("numeric" if is_numeric else "categorical")
            logger.info(f"Evolving {len(error_cells)} error cells in column '{col_name}' ({col_type}) using {actual_method.value.upper()}")

            # Evolve cells in this column
            for error_cell in error_cells:
                # Convert display row index to DataFrame index
                # DataQualityAnalyzer adds +1 for display (row 0 = headers)
                display_row_idx = error_cell['row']
                df_row_idx = display_row_idx - 1
                original_value = self.df.iloc[df_row_idx, col_idx]

                try:
                    if is_datetime:
                        evolved_value, cell_result = self._evolve_datetime_cell(
                            original_value, healthy_cells, col_name
                        )
                    elif is_numeric:
                        evolved_value, cell_result = self._evolve_numeric_cell(
                            original_value, healthy_cells, actual_method, col_name
                        )
                    else:
                        evolved_value, cell_result = self._evolve_categorical_cell(
                            original_value, healthy_cells, actual_method, col_name
                        )

                    # Create error cell record (store DataFrame index for internal use)
                    evolved_cell = ErrorCell(
                        row=df_row_idx,
                        col=col_idx,
                        col_name=col_name,
                        original_value=original_value,
                        issues=error_cell.get('issues', []),
                        evolved_value=evolved_value,
                        fitness_before=cell_result.get('fitness_before', 0),
                        fitness_after=cell_result.get('fitness_after', 0),
                        evolution_method=actual_method.value
                    )

                    # Update DataFrame if evolution improved the cell
                    if cell_result.get('improved', False):
                        evolved_df.iloc[df_row_idx, col_idx] = evolved_value
                        result.cells_fixed += 1
                        self.modifications.append(evolved_cell)

                    result.cells_evolved += 1
                    result.evolved_cells.append(evolved_cell)
                    result.fitness_history.extend(cell_result.get('history', []))

                except Exception as e:
                    logger.error(f"Failed to evolve cell at row {df_row_idx}, col {col_idx}: {e}")
                    result.cells_failed += 1

            # After processing all error cells in a datetime column, standardize the entire column
            if is_datetime:
                evolved_df = self._standardize_datetime_column(evolved_df, col_name)

        # Calculate summary statistics
        if result.evolved_cells:
            result.average_fitness_before = np.mean([c.fitness_before for c in result.evolved_cells])
            result.average_fitness_after = np.mean([c.fitness_after for c in result.evolved_cells])
            result.fitness_improvement = result.average_fitness_after - result.average_fitness_before

        # Add Modified_by_AI tracking column
        if 'Modified_by_AI' not in evolved_df.columns:
            evolved_df['Modified_by_AI'] = 'No'

        for cell in self.modifications:
            evolved_df.loc[cell.row, 'Modified_by_AI'] = 'Yes'

        logger.info(f"Evolution complete: {result.cells_fixed}/{result.cells_evolved} cells fixed, "
                   f"Fitness improved by {result.fitness_improvement:.2%}")

        return evolved_df, result

    def _evolve_datetime_cell(self, original_value: Any, healthy_cells: np.ndarray,
                              col_name: str) -> Tuple[str, Dict]:
        """
        Evolve a datetime cell by finding the best matching datetime from healthy cells.
        Uses temporal proximity and distribution matching.

        Returns:
            Tuple of (evolved value as standardized string, result dict with fitness info)
        """
        # Parse all healthy cells into datetime objects
        healthy_datetimes = []
        for val in healthy_cells:
            parsed = parse_datetime(val)
            if parsed is not None:
                healthy_datetimes.append(parsed)

        if len(healthy_datetimes) < 2:
            # Not enough datetime values, fall back to most common string
            unique_vals, counts = np.unique(healthy_cells.astype(str), return_counts=True)
            most_common = unique_vals[np.argmax(counts)]
            return most_common, {
                'fitness_before': 0.0,
                'fitness_after': 0.5,
                'improved': True,
                'history': [{'method': 'datetime_fallback'}]
            }

        # Convert to timestamps for numerical operations
        timestamps = np.array([dt.timestamp() for dt in healthy_datetimes])
        mean_timestamp = np.mean(timestamps)
        std_timestamp = np.std(timestamps) if len(timestamps) > 1 else 86400  # 1 day default
        min_timestamp = np.min(timestamps)
        max_timestamp = np.max(timestamps)

        # Fitness function for datetime values
        def datetime_fitness(ts: float) -> float:
            if ts < min_timestamp or ts > max_timestamp:
                # Penalize out-of-range values
                distance = min(abs(ts - min_timestamp), abs(ts - max_timestamp))
                range_size = max_timestamp - min_timestamp + 1
                penalty = min(distance / range_size, 1.0) * 0.4
                bounds_score = 1.0 - penalty
            else:
                bounds_score = 1.0

            # Distribution similarity
            if std_timestamp > 0:
                z_score = abs(ts - mean_timestamp) / std_timestamp
                dist_score = np.exp(-0.5 * z_score)
            else:
                dist_score = 1.0 if ts == mean_timestamp else 0.5

            return 0.3 * bounds_score + 0.7 * dist_score

        # Calculate fitness of original value
        original_parsed = parse_datetime(original_value)
        if original_parsed is not None:
            fitness_before = datetime_fitness(original_parsed.timestamp())
        else:
            fitness_before = 0.0

        # Evolutionary approach: Use PSO-like particle swarm in timestamp space
        config = self.config
        n_particles = min(config.population_size, 20)

        # Initialize particles from healthy timestamps with small variation
        particles = np.random.choice(timestamps, size=n_particles)
        particles = particles + np.random.normal(0, std_timestamp * 0.1, n_particles)
        particles = np.clip(particles, min_timestamp, max_timestamp)

        # Velocities
        velocity_max = (max_timestamp - min_timestamp) * 0.1
        velocities = np.random.uniform(-velocity_max, velocity_max, n_particles)

        # Personal and global bests
        personal_best = particles.copy()
        personal_best_fitness = np.array([datetime_fitness(p) for p in particles])
        global_best_idx = np.argmax(personal_best_fitness)
        global_best = personal_best[global_best_idx]
        global_best_fitness = personal_best_fitness[global_best_idx]

        history = []
        for gen in range(min(config.generations, 30)):  # Fewer generations for datetime
            # PSO update
            r1, r2 = np.random.random(n_particles), np.random.random(n_particles)
            cognitive = 1.5 * r1 * (personal_best - particles)
            social = 1.5 * r2 * (global_best - particles)
            velocities = 0.7 * velocities + cognitive + social
            velocities = np.clip(velocities, -velocity_max, velocity_max)

            particles = particles + velocities
            particles = np.clip(particles, min_timestamp, max_timestamp)

            # Evaluate and update bests
            fitness_values = np.array([datetime_fitness(p) for p in particles])
            improved_mask = fitness_values > personal_best_fitness
            personal_best[improved_mask] = particles[improved_mask]
            personal_best_fitness[improved_mask] = fitness_values[improved_mask]

            current_best_idx = np.argmax(personal_best_fitness)
            if personal_best_fitness[current_best_idx] > global_best_fitness:
                global_best_fitness = personal_best_fitness[current_best_idx]
                global_best = personal_best[current_best_idx]

            history.append({
                'generation': gen,
                'best_fitness': global_best_fitness,
                'method': 'datetime_pso'
            })

            if global_best_fitness >= config.fitness_threshold:
                break

        # Convert best timestamp back to datetime and format
        evolved_datetime = datetime.fromtimestamp(global_best)
        evolved_value = format_datetime(evolved_datetime)

        logger.debug(f"Datetime evolution: '{original_value}' -> '{evolved_value}' "
                    f"(fitness: {fitness_before:.2f} -> {global_best_fitness:.2f})")

        return evolved_value, {
            'fitness_before': fitness_before,
            'fitness_after': global_best_fitness,
            'improved': global_best_fitness > fitness_before + 0.01,
            'history': history
        }

    def _standardize_datetime_column(self, df: pd.DataFrame, col_name: str) -> pd.DataFrame:
        """
        Standardize all datetime values in a column to a consistent format.
        This ensures all dates use the same format after evolution.

        Args:
            df: DataFrame to modify
            col_name: Name of the datetime column

        Returns:
            DataFrame with standardized datetime values
        """
        standardized_count = 0

        for idx in df.index:
            value = df.loc[idx, col_name]

            if pd.isna(value) or value is None:
                continue

            # Try to parse and reformat
            parsed = parse_datetime(value)
            if parsed is not None:
                standardized = format_datetime(parsed)
                if str(value) != standardized:
                    df.loc[idx, col_name] = standardized
                    standardized_count += 1

        if standardized_count > 0:
            logger.info(f"Standardized {standardized_count} datetime values in column '{col_name}' "
                       f"to format: {STANDARD_DATETIME_FORMAT}")

        return df

    def _evolve_numeric_cell(self, original_value: Any, healthy_cells: np.ndarray,
                            method: EvolutionMethod, col_name: str) -> Tuple[float, Dict]:
        """
        Evolve a numeric cell using the specified method.

        Returns:
            Tuple of (evolved value, result dict with fitness info)
        """
        healthy_cells = healthy_cells.astype(float)
        healthy_mean = np.mean(healthy_cells)
        healthy_std = np.std(healthy_cells) if len(healthy_cells) > 1 else healthy_mean * 0.1
        healthy_min = np.min(healthy_cells)
        healthy_max = np.max(healthy_cells)

        # Fitness function: how well does the value fit the healthy distribution?
        def fitness_func(value: float) -> float:
            if np.isnan(value) or np.isinf(value):
                return 0.0

            # Check bounds
            if value < healthy_min or value > healthy_max:
                # Penalize out-of-bounds but don't fully reject
                distance = min(abs(value - healthy_min), abs(value - healthy_max))
                range_size = healthy_max - healthy_min
                penalty = min(distance / (range_size + 1e-6), 1.0) * 0.3
                bounds_score = 1.0 - penalty
            else:
                bounds_score = 1.0

            # Distribution similarity (z-score based)
            if healthy_std > 0:
                z_score = abs(value - healthy_mean) / healthy_std
                dist_score = np.exp(-0.5 * z_score)  # Gaussian decay
            else:
                dist_score = 1.0 if value == healthy_mean else 0.5

            return 0.4 * bounds_score + 0.6 * dist_score

        # Calculate initial fitness
        try:
            if pd.isna(original_value):
                fitness_before = 0.0
            else:
                fitness_before = fitness_func(float(original_value))
        except (ValueError, TypeError):
            fitness_before = 0.0

        # Run evolution based on method
        if method == EvolutionMethod.GA:
            evolved_value, history = self._ga_evolve_numeric(
                healthy_cells, fitness_func, healthy_min, healthy_max
            )
        elif method == EvolutionMethod.PSO:
            evolved_value, history = self._pso_evolve_numeric(
                healthy_cells, fitness_func, healthy_min, healthy_max
            )
        elif method == EvolutionMethod.DE:
            evolved_value, history = self._de_evolve_numeric(
                healthy_cells, fitness_func, healthy_min, healthy_max
            )
        elif method == EvolutionMethod.ES:
            evolved_value, history = self._es_evolve_numeric(
                healthy_cells, fitness_func, healthy_min, healthy_max
            )
        else:
            # Default to PSO for numeric
            evolved_value, history = self._pso_evolve_numeric(
                healthy_cells, fitness_func, healthy_min, healthy_max
            )

        fitness_after = fitness_func(evolved_value)

        return evolved_value, {
            'fitness_before': fitness_before,
            'fitness_after': fitness_after,
            'improved': fitness_after > fitness_before + 0.01,
            'history': history
        }

    def _ga_evolve_numeric(self, healthy_cells: np.ndarray, fitness_func: Callable,
                          min_val: float, max_val: float) -> Tuple[float, List[Dict]]:
        """
        Genetic Algorithm evolution for numeric cells.
        Uses crossover and mutation from healthy cell population.
        """
        config = self.config
        history = []

        # Initialize population from healthy cells with variation
        population = []
        for _ in range(config.population_size):
            # Sample from healthy cells and add small variation
            base_value = np.random.choice(healthy_cells)
            variation = np.random.normal(0, (max_val - min_val) * 0.1)
            value = np.clip(base_value + variation, min_val, max_val)
            population.append(value)

        population = np.array(population)
        best_value = population[0]
        best_fitness = fitness_func(best_value)
        no_improvement_count = 0

        for gen in range(config.generations):
            # Evaluate fitness
            fitness_values = np.array([fitness_func(v) for v in population])

            # Update best
            gen_best_idx = np.argmax(fitness_values)
            if fitness_values[gen_best_idx] > best_fitness:
                best_fitness = fitness_values[gen_best_idx]
                best_value = population[gen_best_idx]
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            history.append({
                'generation': gen,
                'best_fitness': best_fitness,
                'avg_fitness': np.mean(fitness_values),
                'method': 'GA'
            })

            # Early stopping
            if config.early_stopping and no_improvement_count >= config.patience:
                logger.debug(f"GA: Early stopping at generation {gen}")
                break

            if best_fitness >= config.fitness_threshold:
                break

            # Selection: Tournament
            new_population = []

            # Elitism: keep best individuals
            sorted_indices = np.argsort(fitness_values)[::-1]
            for i in range(config.elitism_count):
                new_population.append(population[sorted_indices[i]])

            # Generate rest through crossover and mutation
            while len(new_population) < config.population_size:
                # Tournament selection for parents
                parent1 = self._tournament_select(population, fitness_values, config.tournament_size)
                parent2 = self._tournament_select(population, fitness_values, config.tournament_size)

                # Crossover: arithmetic blend
                if np.random.random() < config.crossover_rate:
                    alpha = np.random.random()
                    child = alpha * parent1 + (1 - alpha) * parent2
                else:
                    child = parent1

                # Mutation: Gaussian perturbation
                if np.random.random() < config.mutation_rate:
                    mutation = np.random.normal(0, (max_val - min_val) * 0.1)
                    child = child + mutation

                # Clip to bounds
                child = np.clip(child, min_val, max_val)
                new_population.append(child)

            population = np.array(new_population[:config.population_size])

        return best_value, history

    def _pso_evolve_numeric(self, healthy_cells: np.ndarray, fitness_func: Callable,
                           min_val: float, max_val: float) -> Tuple[float, List[Dict]]:
        """
        Particle Swarm Optimization for numeric cells.
        Uses the new PSO engine with multiple topology and variant support.
        """
        config = self.config

        # Map string topology to enum
        topology_map = {
            'gbest': PSOTopology.GLOBAL_BEST,
            'lbest': PSOTopology.LOCAL_BEST,
            'ring': PSOTopology.RING,
            'random': PSOTopology.RANDOM,
            'von_neumann': PSOTopology.VON_NEUMANN
        }
        topology = topology_map.get(config.pso_topology, PSOTopology.GLOBAL_BEST)

        # Map string variant to enum
        variant_map = {
            'standard': PSOVariant.STANDARD,
            'constriction': PSOVariant.CONSTRICTION,
            'inertia_decay': PSOVariant.INERTIA_DECAY
        }
        variant = variant_map.get(config.pso_variant, PSOVariant.STANDARD)

        # Create PSO config
        pso_config = PSOConfig(
            swarm_size=config.population_size,
            iterations=config.generations,
            inertia_weight=config.inertia_weight,
            inertia_min=config.inertia_min,
            inertia_max=config.inertia_max,
            cognitive_coeff=config.cognitive_coeff,
            social_coeff=config.social_coeff,
            velocity_clamp=config.velocity_clamp,
            topology=topology,
            variant=variant,
            constriction_factor=config.constriction_factor,
            neighborhood_size=config.neighborhood_size,
            constraint_handling=PSOConstraintHandling.CLAMP,
            early_stopping=config.early_stopping,
            patience=config.patience,
            min_improvement=config.min_improvement,
            fitness_threshold=config.fitness_threshold
        )

        # Run PSO optimization
        try:
            optimizer = ParticleSwarmOptimizer(
                config=pso_config,
                fitness_function=fitness_func,
                bounds_min=min_val,
                bounds_max=max_val,
                seed_values=healthy_cells
            )
            result = optimizer.run()

            # Convert result to history format
            history = []
            for metrics in result.iteration_metrics:
                history.append({
                    'generation': metrics.iteration,
                    'best_fitness': metrics.global_best_fitness,
                    'avg_fitness': metrics.average_fitness,
                    'avg_velocity': metrics.average_velocity,
                    'swarm_diversity': metrics.swarm_diversity,
                    'current_inertia': metrics.current_inertia,
                    'method': 'PSO'
                })

            # Get best value (scalar)
            best_value = result.best_position[0] if isinstance(result.best_position, np.ndarray) else result.best_position

            return float(best_value), history

        except Exception as e:
            logger.error(f"PSO engine error: {e}, falling back to simple PSO")
            # Fallback to simple PSO if engine fails
            return self._simple_pso_evolve(healthy_cells, fitness_func, min_val, max_val)

    def _simple_pso_evolve(self, healthy_cells: np.ndarray, fitness_func: Callable,
                          min_val: float, max_val: float) -> Tuple[float, List[Dict]]:
        """Simple PSO fallback implementation."""
        config = self.config
        history = []

        n_particles = config.population_size
        particles = np.random.choice(healthy_cells, size=n_particles)
        particles = particles + np.random.normal(0, (max_val - min_val) * 0.1, n_particles)
        particles = np.clip(particles, min_val, max_val)

        velocity_max = (max_val - min_val) * config.velocity_clamp
        velocities = np.random.uniform(-velocity_max, velocity_max, n_particles)

        personal_best = particles.copy()
        personal_best_fitness = np.array([fitness_func(p) for p in particles])

        global_best_idx = np.argmax(personal_best_fitness)
        global_best = personal_best[global_best_idx]
        global_best_fitness = personal_best_fitness[global_best_idx]

        no_improvement_count = 0

        for gen in range(config.generations):
            r1 = np.random.random(n_particles)
            r2 = np.random.random(n_particles)

            cognitive = config.cognitive_coeff * r1 * (personal_best - particles)
            social = config.social_coeff * r2 * (global_best - particles)

            velocities = config.inertia_weight * velocities + cognitive + social
            velocities = np.clip(velocities, -velocity_max, velocity_max)

            particles = particles + velocities
            particles = np.clip(particles, min_val, max_val)

            fitness_values = np.array([fitness_func(p) for p in particles])

            improved_mask = fitness_values > personal_best_fitness
            personal_best[improved_mask] = particles[improved_mask]
            personal_best_fitness[improved_mask] = fitness_values[improved_mask]

            current_best_idx = np.argmax(personal_best_fitness)
            if personal_best_fitness[current_best_idx] > global_best_fitness:
                global_best_fitness = personal_best_fitness[current_best_idx]
                global_best = personal_best[current_best_idx]
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            history.append({
                'generation': gen,
                'best_fitness': global_best_fitness,
                'avg_fitness': np.mean(fitness_values),
                'avg_velocity': np.mean(np.abs(velocities)),
                'method': 'PSO'
            })

            if config.early_stopping and no_improvement_count >= config.patience:
                break

            if global_best_fitness >= config.fitness_threshold:
                break

        return global_best, history

    def _de_evolve_numeric(self, healthy_cells: np.ndarray, fitness_func: Callable,
                          min_val: float, max_val: float) -> Tuple[float, List[Dict]]:
        """
        Differential Evolution for numeric cells.
        Uses the new DE engine with all 6 mutation strategies and adaptive parameters.
        """
        config = self.config

        # Map string strategy to enum
        strategy_map = {
            'DE/rand/1': DEMutationStrategy.RAND_1,
            'DE/rand/2': DEMutationStrategy.RAND_2,
            'DE/best/1': DEMutationStrategy.BEST_1,
            'DE/best/2': DEMutationStrategy.BEST_2,
            'DE/current-to-best/1': DEMutationStrategy.CURRENT_TO_BEST_1,
            'DE/current-to-rand/1': DEMutationStrategy.CURRENT_TO_RAND_1,
        }
        strategy = strategy_map.get(config.de_mutation_strategy, DEMutationStrategy.RAND_1)

        # Map string crossover type to enum
        crossover_map = {
            'binomial': DECrossoverType.BINOMIAL,
            'exponential': DECrossoverType.EXPONENTIAL,
        }
        crossover_type = crossover_map.get(config.de_crossover_type, DECrossoverType.BINOMIAL)

        # Create DE config
        de_config = DEConfig(
            population_size=config.population_size,
            generations=config.generations,
            scale_factor=config.differential_weight,
            crossover_rate=config.crossover_prob,
            mutation_strategy=strategy,
            crossover_type=crossover_type,
            adaptive_f=config.adaptive_f,
            adaptive_cr=config.adaptive_cr,
            f_min=config.f_min,
            f_max=config.f_max,
            cr_min=config.cr_min,
            cr_max=config.cr_max,
            constraint_handling=DEConstraintHandling.CLAMP,
            early_stopping=config.early_stopping,
            patience=config.patience,
            min_improvement=config.min_improvement,
            fitness_threshold=config.fitness_threshold
        )

        # Run DE optimization
        try:
            optimizer = DifferentialEvolutionOptimizer(
                config=de_config,
                fitness_function=fitness_func,
                bounds_min=min_val,
                bounds_max=max_val,
                seed_values=healthy_cells
            )
            result = optimizer.run()

            # Convert result to history format
            history = []
            for metrics in result.generation_metrics:
                history.append({
                    'generation': metrics.generation,
                    'best_fitness': metrics.best_fitness,
                    'avg_fitness': metrics.average_fitness,
                    'diversity': metrics.population_diversity,
                    'success_rate': metrics.success_rate,
                    'current_f': metrics.current_f,
                    'current_cr': metrics.current_cr,
                    'method': 'DE'
                })

            # Get best value (scalar)
            best_value = result.best_individual[0] if isinstance(result.best_individual, np.ndarray) else result.best_individual

            return float(best_value), history

        except Exception as e:
            logger.error(f"DE engine error: {e}, falling back to simple DE")
            # Fallback to simple DE if engine fails
            return self._simple_de_evolve(healthy_cells, fitness_func, min_val, max_val)

    def _simple_de_evolve(self, healthy_cells: np.ndarray, fitness_func: Callable,
                         min_val: float, max_val: float) -> Tuple[float, List[Dict]]:
        """Simple DE fallback implementation (DE/rand/1)."""
        config = self.config
        history = []

        pop_size = config.population_size
        population = np.random.choice(healthy_cells, size=pop_size)
        population = population + np.random.normal(0, (max_val - min_val) * 0.1, pop_size)
        population = np.clip(population, min_val, max_val)

        fitness_values = np.array([fitness_func(p) for p in population])

        best_idx = np.argmax(fitness_values)
        best_value = population[best_idx]
        best_fitness = fitness_values[best_idx]
        no_improvement_count = 0

        for gen in range(config.generations):
            new_population = population.copy()
            new_fitness = fitness_values.copy()

            for i in range(pop_size):
                candidates = list(range(pop_size))
                candidates.remove(i)
                a, b, c = np.random.choice(candidates, 3, replace=False)

                mutant = population[a] + config.differential_weight * (population[b] - population[c])
                mutant = np.clip(mutant, min_val, max_val)

                if np.random.random() < config.crossover_prob:
                    trial = mutant
                else:
                    trial = population[i]

                trial_fitness = fitness_func(trial)
                if trial_fitness > fitness_values[i]:
                    new_population[i] = trial
                    new_fitness[i] = trial_fitness

            population = new_population
            fitness_values = new_fitness

            gen_best_idx = np.argmax(fitness_values)
            if fitness_values[gen_best_idx] > best_fitness:
                best_fitness = fitness_values[gen_best_idx]
                best_value = population[gen_best_idx]
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            history.append({
                'generation': gen,
                'best_fitness': best_fitness,
                'avg_fitness': np.mean(fitness_values),
                'diversity': np.std(population),
                'method': 'DE'
            })

            if config.early_stopping and no_improvement_count >= config.patience:
                break

            if best_fitness >= config.fitness_threshold:
                break

        return best_value, history

    def _es_evolve_numeric(self, healthy_cells: np.ndarray, fitness_func: Callable,
                          min_val: float, max_val: float) -> Tuple[float, List[Dict]]:
        """
        Evolution Strategy for numeric cells.
        Uses (μ, λ) selection with self-adaptive mutation.
        """
        config = self.config
        history = []

        mu = config.mu  # Number of parents
        lambda_ = config.lambda_  # Number of offspring

        # Initialize parents from healthy cells
        parents = np.random.choice(healthy_cells, size=mu)
        parents = parents + np.random.normal(0, (max_val - min_val) * 0.1, mu)
        parents = np.clip(parents, min_val, max_val)

        # Self-adaptive mutation strengths (one per parent)
        sigmas = np.full(mu, config.initial_sigma * (max_val - min_val))

        best_value = parents[0]
        best_fitness = fitness_func(best_value)
        no_improvement_count = 0

        for gen in range(config.generations):
            # Generate offspring
            offspring = []
            offspring_sigmas = []

            for _ in range(lambda_):
                # Select random parent
                parent_idx = np.random.randint(mu)
                parent = parents[parent_idx]
                sigma = sigmas[parent_idx]

                # Self-adaptation of sigma (ES 1/5 success rule approximation)
                tau = 1.0 / np.sqrt(2)
                new_sigma = sigma * np.exp(tau * np.random.normal())
                new_sigma = max(new_sigma, 0.001 * (max_val - min_val))  # Prevent too small

                # Mutation with self-adapted sigma
                child = parent + new_sigma * np.random.normal()
                child = np.clip(child, min_val, max_val)

                offspring.append(child)
                offspring_sigmas.append(new_sigma)

            offspring = np.array(offspring)
            offspring_sigmas = np.array(offspring_sigmas)

            # Evaluate offspring
            offspring_fitness = np.array([fitness_func(o) for o in offspring])

            # (μ, λ) selection: select best μ offspring as new parents
            sorted_indices = np.argsort(offspring_fitness)[::-1][:mu]
            parents = offspring[sorted_indices]
            sigmas = offspring_sigmas[sorted_indices]

            # Update best
            if offspring_fitness[sorted_indices[0]] > best_fitness:
                best_fitness = offspring_fitness[sorted_indices[0]]
                best_value = parents[0]
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            history.append({
                'generation': gen,
                'best_fitness': best_fitness,
                'avg_fitness': np.mean(offspring_fitness),
                'avg_sigma': np.mean(sigmas),
                'method': 'ES'
            })

            # Early stopping
            if config.early_stopping and no_improvement_count >= config.patience:
                logger.debug(f"ES: Early stopping at generation {gen}")
                break

            if best_fitness >= config.fitness_threshold:
                break

        return best_value, history

    def _evolve_categorical_cell(self, original_value: Any, healthy_cells: np.ndarray,
                                 method: EvolutionMethod, col_name: str) -> Tuple[Any, Dict]:
        """
        Evolve a categorical cell using the specified method.
        Uses frequency-based fitness for categorical values.
        """
        # Get unique values and their frequencies
        unique_values, counts = np.unique(healthy_cells, return_counts=True)
        freq_dict = dict(zip(unique_values, counts / len(healthy_cells)))

        # Fitness function: frequency in healthy population
        def fitness_func(value: Any) -> float:
            if pd.isna(value) or value is None:
                return 0.0
            return freq_dict.get(value, 0.0)

        # Calculate initial fitness
        fitness_before = fitness_func(original_value)

        # For categorical, GA with selection is most appropriate
        if method in [EvolutionMethod.GA, EvolutionMethod.HYBRID]:
            evolved_value, history = self._ga_evolve_categorical(unique_values, freq_dict)
        else:
            # For other methods, use weighted random selection as approximation
            evolved_value, history = self._weighted_selection_categorical(unique_values, counts)

        fitness_after = fitness_func(evolved_value)

        return evolved_value, {
            'fitness_before': fitness_before,
            'fitness_after': fitness_after,
            'improved': fitness_after > fitness_before,
            'history': history
        }

    def _ga_evolve_categorical(self, unique_values: np.ndarray,
                               freq_dict: Dict) -> Tuple[Any, List[Dict]]:
        """
        GA evolution for categorical cells.
        Uses tournament selection based on frequency fitness.
        """
        config = self.config
        history = []

        # Population is indices into unique_values
        pop_size = min(config.population_size, len(unique_values) * 3)

        # Initialize population with frequency-weighted sampling
        probs = np.array([freq_dict.get(v, 0.001) for v in unique_values])
        probs = probs / probs.sum()
        population = np.random.choice(len(unique_values), size=pop_size, p=probs)

        best_idx = population[0]
        best_fitness = freq_dict.get(unique_values[best_idx], 0)

        for gen in range(config.generations):
            # Evaluate fitness (frequency-based)
            fitness_values = np.array([freq_dict.get(unique_values[i], 0) for i in population])

            # Update best
            gen_best_idx = np.argmax(fitness_values)
            if fitness_values[gen_best_idx] > best_fitness:
                best_fitness = fitness_values[gen_best_idx]
                best_idx = population[gen_best_idx]

            history.append({
                'generation': gen,
                'best_fitness': best_fitness,
                'method': 'GA-Categorical'
            })

            if best_fitness >= config.fitness_threshold:
                break

            # Selection and reproduction
            new_population = []

            # Elitism
            sorted_indices = np.argsort(fitness_values)[::-1]
            for i in range(min(2, len(sorted_indices))):
                new_population.append(population[sorted_indices[i]])

            # Generate rest through selection
            while len(new_population) < pop_size:
                # Tournament selection
                candidates = np.random.choice(pop_size, size=config.tournament_size)
                winner = candidates[np.argmax(fitness_values[candidates])]
                selected = population[winner]

                # Mutation: random switch with probability
                if np.random.random() < config.mutation_rate:
                    selected = np.random.choice(len(unique_values), p=probs)

                new_population.append(selected)

            population = np.array(new_population[:pop_size])

        return unique_values[best_idx], history

    def _weighted_selection_categorical(self, unique_values: np.ndarray,
                                        counts: np.ndarray) -> Tuple[Any, List[Dict]]:
        """
        Weighted random selection for categorical values.
        Used when other methods aren't appropriate for categorical data.
        """
        probs = counts / counts.sum()
        selected_idx = np.random.choice(len(unique_values), p=probs)
        return unique_values[selected_idx], [{'method': 'WeightedSelection'}]

    def _tournament_select(self, population: np.ndarray, fitness_values: np.ndarray,
                          tournament_size: int) -> float:
        """Tournament selection helper"""
        candidates = np.random.choice(len(population), size=tournament_size, replace=False)
        winner = candidates[np.argmax(fitness_values[candidates])]
        return population[winner]


def evolve_error_cells(df: pd.DataFrame, error_cells: List[Dict],
                       method: str = "hybrid",
                       config: Optional[Dict] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to evolve error cells in a DataFrame.

    Args:
        df: DataFrame with data
        error_cells: List of error cells from DataQualityAnalyzer
        method: Evolution method ('ga', 'pso', 'de', 'es', 'hybrid')
        config: Optional configuration dict

    Returns:
        Tuple of (evolved DataFrame, result dict)
    """
    # Parse method
    try:
        evolution_method = EvolutionMethod(method.lower())
    except ValueError:
        evolution_method = EvolutionMethod.HYBRID

    # Parse config
    cell_config = CellEvolutionConfig()
    if config:
        for key, value in config.items():
            if hasattr(cell_config, key):
                setattr(cell_config, key, value)

    # Run evolution
    cleaner = EvolutionaryCellCleaner(df, error_cells, cell_config)
    evolved_df, result = cleaner.evolve(evolution_method)

    # Convert result to dict for JSON serialization
    result_dict = {
        'cells_evolved': result.cells_evolved,
        'cells_fixed': result.cells_fixed,
        'cells_failed': result.cells_failed,
        'average_fitness_before': result.average_fitness_before,
        'average_fitness_after': result.average_fitness_after,
        'fitness_improvement': result.fitness_improvement,
        'method_used': result.method_used,
        'converged': result.converged,
        'evolved_cells': [
            {
                'row': c.row + 1,  # Convert DataFrame index back to display index for frontend
                'col': c.col,
                'col_name': c.col_name,
                'original_value': str(c.original_value) if c.original_value is not None else None,
                'evolved_value': str(c.evolved_value) if c.evolved_value is not None else None,
                'fitness_before': c.fitness_before,
                'fitness_after': c.fitness_after,
                'evolution_method': c.evolution_method,
                'issues': c.issues
            }
            for c in result.evolved_cells[:100]  # Limit for response size
        ],
        'fitness_history': result.fitness_history[-50:] if result.fitness_history else []  # Last 50 entries
    }

    return evolved_df, result_dict
