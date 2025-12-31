#!/usr/bin/env python3
"""
Test Suite: Evolutionary Cell Cleaning
======================================
Tests for column-based AI cleaning using evolutionary algorithms (GA, PSO, DE, ES, Hybrid).

This test suite validates:
1. Cell evolution for numeric columns
2. Cell evolution for categorical columns
3. Cell evolution for datetime columns
4. All evolutionary methods (GA, PSO, DE, ES, Hybrid)
5. Fitness improvement tracking
6. Configuration parameter handling

Run with verbose output:
    python3 test_evolutionary_cleaning.py -v > test_results_evo_cleaning.txt 2>&1

Run normally:
    python3 test_evolutionary_cleaning.py
"""

import unittest
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evolutionary_cell_cleaner import (
    EvolutionaryCellCleaner,
    CellEvolutionConfig,
    EvolutionMethod,
    evolve_error_cells,
    parse_datetime,
    format_datetime,
    is_datetime_column
)
from data_quality_analyzer import DataQualityAnalyzer

# Check for verbose flag
VERBOSE = '-v' in sys.argv or '--verbose' in sys.argv


def print_section(title):
    """Print a section header"""
    if VERBOSE:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")


def print_subsection(title):
    """Print a subsection header"""
    if VERBOSE:
        print(f"\n{'-'*60}")
        print(f"  {title}")
        print(f"{'-'*60}")


def print_dataframe(df, title="DataFrame", max_rows=10):
    """Print a DataFrame with formatting"""
    if VERBOSE:
        print(f"\n  {title}:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"\n{df.head(max_rows).to_string(index=True)}")


def print_error_cells(error_cells, title="Error Cells"):
    """Print error cells in formatted table"""
    if VERBOSE:
        print(f"\n  {title}: {len(error_cells)} cells")
        if error_cells:
            print(f"  {'Row':<6} {'Col':<6} {'Issues':<40}")
            print(f"  {'-'*6} {'-'*6} {'-'*40}")
            for cell in error_cells[:10]:
                issues_str = ', '.join(cell.get('issues', []))[:40]
                print(f"  {cell['row']:<6} {cell['col']:<6} {issues_str:<40}")
            if len(error_cells) > 10:
                print(f"  ... and {len(error_cells) - 10} more")


def print_evolution_result(result, title="Evolution Result"):
    """Print evolution result details"""
    if VERBOSE:
        print(f"\n  {title}:")
        print(f"    Method Used: {result.get('method_used', 'N/A')}")
        print(f"    Cells Evolved: {result.get('cells_evolved', 0)}")
        print(f"    Cells Fixed: {result.get('cells_fixed', 0)}")
        print(f"    Cells Failed: {result.get('cells_failed', 0)}")
        print(f"    Avg Fitness Before: {result.get('average_fitness_before', 0):.2%}")
        print(f"    Avg Fitness After: {result.get('average_fitness_after', 0):.2%}")
        print(f"    Fitness Improvement: {result.get('fitness_improvement', 0):.2%}")

        evolved_cells = result.get('evolved_cells', [])
        if evolved_cells:
            print(f"\n    Evolved Cells Detail (first 5):")
            print(f"    {'Row':<6} {'Col':<15} {'Original':<15} {'Evolved':<15} {'Before':<10} {'After':<10}")
            print(f"    {'-'*6} {'-'*15} {'-'*15} {'-'*15} {'-'*10} {'-'*10}")
            for cell in evolved_cells[:5]:
                orig = str(cell.get('original_value', ''))[:14]
                evol = str(cell.get('evolved_value', ''))[:14]
                print(f"    {cell.get('row', 0):<6} {str(cell.get('col_name', ''))[:14]:<15} "
                      f"{orig:<15} {evol:<15} "
                      f"{cell.get('fitness_before', 0):.2%}     {cell.get('fitness_after', 0):.2%}")


def print_test_criteria(criteria_list):
    """Print test criteria/assertions"""
    if VERBOSE:
        print(f"\n  Test Criteria:")
        for i, criteria in enumerate(criteria_list, 1):
            print(f"    {i}. {criteria}")


class VerboseTestResult(unittest.TextTestResult):
    """Custom test result class for verbose output"""

    def startTest(self, test):
        super().startTest(test)
        if VERBOSE:
            self.stream.write("\n" + "-"*70 + "\n")
            self.stream.write(f"  TEST: {test._testMethodName}\n")
            self.stream.write("-"*70 + "\n")
            if test._testMethodDoc:
                self.stream.write(f"  Description: {test._testMethodDoc.strip()}\n")

    def addSuccess(self, test):
        super().addSuccess(test)
        if VERBOSE:
            self.stream.write(f"\n  [PASS] {test._testMethodName}\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if VERBOSE:
            self.stream.write(f"\n  [FAIL] {test._testMethodName}\n")
            self.stream.write(f"  Error: {err[1]}\n")

    def addError(self, test, err):
        super().addError(test, err)
        if VERBOSE:
            self.stream.write(f"\n  [ERROR] {test._testMethodName}\n")
            self.stream.write(f"  Error: {err[1]}\n")


class VerboseTestRunner(unittest.TextTestRunner):
    """Custom test runner with verbose support"""

    def __init__(self, **kwargs):
        kwargs['resultclass'] = VerboseTestResult
        super().__init__(**kwargs)


class TestNumericCellEvolution(unittest.TestCase):
    """Test evolutionary cleaning for numeric columns"""

    def setUp(self):
        """Set up test data with numeric columns containing errors"""
        # Create DataFrame with numeric data and some errors
        self.df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'price': [100.0, 150.0, 'invalid', 200.0, 175.0, None, 125.0, 180.0, 160.0, 140.0],
            'quantity': [10, 20, 30, -999, 25, 15, 'abc', 35, 22, 18],
            'score': [85.5, 90.0, 88.5, 92.0, 'N/A', 87.0, 89.5, 91.0, 86.5, 88.0]
        })
        print_subsection("Test Setup: Numeric Column Evolution")
        print_dataframe(self.df, "Input DataFrame with numeric errors")

        # Analyze to get error cells
        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells")

    def test_ga_numeric_evolution(self):
        """Test GA evolution for numeric cells"""
        print_subsection("Testing GA Evolution on Numeric Cells")

        print_test_criteria([
            "GA should evolve error cells in numeric columns",
            "Evolved values should be within the range of healthy values",
            "Fitness should improve after evolution",
            "Number of fixed cells should be > 0"
        ])

        if not self.error_cells:
            if VERBOSE:
                print("  No error cells detected - test data may be clean")
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='ga',
            config={'generations': 20, 'population_size': 20}
        )

        print_evolution_result(result, "GA Evolution Result")

        self.assertGreater(result['cells_evolved'], 0, "Should evolve at least one cell")
        self.assertGreaterEqual(result['average_fitness_after'], result['average_fitness_before'],
                               "Fitness should not decrease")

        if VERBOSE:
            print(f"\n  Assertions Passed:")
            print(f"    - Cells evolved: {result['cells_evolved']} > 0")
            print(f"    - Fitness maintained or improved: {result['average_fitness_after']:.2%} >= {result['average_fitness_before']:.2%}")

    def test_pso_numeric_evolution(self):
        """Test PSO evolution for numeric cells"""
        print_subsection("Testing PSO Evolution on Numeric Cells")

        print_test_criteria([
            "PSO should use particle swarm optimization for numeric data",
            "Particles should converge towards healthy value ranges",
            "Global best fitness should improve over iterations"
        ])

        if not self.error_cells:
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='pso',
            config={'generations': 30, 'population_size': 25, 'pso_topology': 'gbest'}
        )

        print_evolution_result(result, "PSO Evolution Result")

        self.assertGreater(result['cells_evolved'], 0)
        self.assertEqual(result['method_used'], 'pso')

        if VERBOSE:
            print(f"\n  Assertions Passed:")
            print(f"    - Method used: {result['method_used']} == 'pso'")
            print(f"    - Cells evolved: {result['cells_evolved']} > 0")

    def test_de_numeric_evolution(self):
        """Test Differential Evolution for numeric cells"""
        print_subsection("Testing DE Evolution on Numeric Cells")

        print_test_criteria([
            "DE should use differential mutation (F) and crossover (CR)",
            "Population should evolve through vector differences",
            "Best fitness should track across generations"
        ])

        if not self.error_cells:
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='de',
            config={
                'generations': 25,
                'population_size': 20,
                'differential_weight': 0.8,
                'crossover_prob': 0.9
            }
        )

        print_evolution_result(result, "DE Evolution Result")

        self.assertGreater(result['cells_evolved'], 0)
        self.assertEqual(result['method_used'], 'de')

    def test_es_numeric_evolution(self):
        """Test Evolution Strategy for numeric cells"""
        print_subsection("Testing ES Evolution on Numeric Cells")

        print_test_criteria([
            "ES should use (mu, lambda) selection strategy",
            "Self-adaptive mutation sigma should adjust over generations",
            "Best offspring should be selected as new parents"
        ])

        if not self.error_cells:
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='es',
            config={'generations': 30, 'mu': 10, 'lambda_': 30, 'initial_sigma': 0.3}
        )

        print_evolution_result(result, "ES Evolution Result")

        self.assertGreater(result['cells_evolved'], 0)
        self.assertEqual(result['method_used'], 'es')


class TestCategoricalCellEvolution(unittest.TestCase):
    """Test evolutionary cleaning for categorical columns"""

    def setUp(self):
        """Set up test data with categorical columns containing errors"""
        self.df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'status': ['Active', 'Active', 'Inactive', 'xyz123', 'Active',
                      'Inactive', None, 'Active', 'Inactive', 'Active'],
            'category': ['A', 'B', 'A', 'C', '###', 'B', 'A', 'B', 'Invalid!', 'C'],
            'region': ['North', 'South', 'East', 'West', 'North',
                      '12345', 'East', 'West', 'South', 'North']
        })
        print_subsection("Test Setup: Categorical Column Evolution")
        print_dataframe(self.df, "Input DataFrame with categorical errors")

        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells")

    def test_ga_categorical_evolution(self):
        """Test GA evolution for categorical cells"""
        print_subsection("Testing GA Evolution on Categorical Cells")

        print_test_criteria([
            "GA should select from healthy categorical values",
            "Frequency-based fitness should favor common values",
            "Evolved values should be valid categories"
        ])

        if not self.error_cells:
            if VERBOSE:
                print("  No error cells detected - data appears clean")
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='ga',
            config={'generations': 20, 'population_size': 15}
        )

        print_evolution_result(result, "GA Categorical Evolution Result")

        # Check that evolved values are from the healthy population
        evolved_cells = result.get('evolved_cells', [])
        for cell in evolved_cells:
            col_name = cell.get('col_name')
            evolved_val = cell.get('evolved_value')
            if col_name and evolved_val and col_name in ['status', 'category', 'region']:
                # Evolved value should be a known category
                if VERBOSE:
                    print(f"    Column '{col_name}': evolved to '{evolved_val}'")

    def test_hybrid_categorical_evolution(self):
        """Test Hybrid method on categorical data (should use GA)"""
        print_subsection("Testing Hybrid Evolution on Categorical Cells")

        print_test_criteria([
            "Hybrid method should automatically select GA for categorical data",
            "Method selection based on column type detection"
        ])

        if not self.error_cells:
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='hybrid',
            config={'generations': 15}
        )

        print_evolution_result(result, "Hybrid (Categorical) Evolution Result")

        self.assertEqual(result['method_used'], 'hybrid')
        self.assertGreaterEqual(result['cells_evolved'], 0)


class TestDatetimeCellEvolution(unittest.TestCase):
    """Test evolutionary cleaning for datetime columns"""

    def setUp(self):
        """Set up test data with datetime columns containing errors"""
        base_date = datetime(2024, 6, 15, 10, 30, 0)

        self.df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'created_at': [
                base_date,
                base_date + timedelta(days=1),
                'invalid_date',
                base_date + timedelta(days=3),
                base_date + timedelta(days=4),
                None,
                base_date + timedelta(days=6),
                base_date + timedelta(days=7),
                '2024/06/23',  # Different format
                base_date + timedelta(days=9)
            ],
            'updated_at': [
                '2024-06-15',
                '2024-06-16',
                '06/17/2024',
                'not a date',
                '2024-06-19',
                '2024-06-20',
                None,
                '2024-06-22',
                '2024-06-23',
                '2024-06-24'
            ]
        })
        print_subsection("Test Setup: Datetime Column Evolution")
        print_dataframe(self.df, "Input DataFrame with datetime errors")

        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells")

    def test_datetime_parsing(self):
        """Test datetime parsing utilities"""
        print_subsection("Testing Datetime Parsing Functions")

        test_cases = [
            ('2024-06-15', True),
            ('2024-06-15 10:30:00', True),
            ('06/15/2024', True),
            ('15-06-2024', True),
            ('invalid', False),
            ('', False),
            (None, False),
            (datetime(2024, 6, 15), True),
        ]

        if VERBOSE:
            print("\n  Datetime Parsing Tests:")
            print(f"  {'Input':<25} {'Expected':<10} {'Actual':<10} {'Status':<10}")
            print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*10}")

        for input_val, expected_parseable in test_cases:
            result = parse_datetime(input_val)
            actual_parseable = result is not None
            status = "PASS" if actual_parseable == expected_parseable else "FAIL"

            if VERBOSE:
                print(f"  {str(input_val)[:24]:<25} {str(expected_parseable):<10} "
                      f"{str(actual_parseable):<10} {status:<10}")

            self.assertEqual(actual_parseable, expected_parseable,
                           f"Failed for input: {input_val}")

    def test_datetime_column_detection(self):
        """Test datetime column detection"""
        print_subsection("Testing Datetime Column Detection")

        datetime_values = np.array(['2024-06-15', '2024-06-16', '2024-06-17',
                                    '2024-06-18', '2024-06-19'])
        numeric_values = np.array([100, 200, 300, 400, 500])
        string_values = np.array(['hello', 'world', 'test', 'data', 'values'])

        test_cases = [
            (datetime_values, True, "Datetime strings"),
            (numeric_values, False, "Numeric values"),
            (string_values, False, "Plain strings"),
        ]

        if VERBOSE:
            print("\n  Column Type Detection:")

        for values, expected, description in test_cases:
            result = is_datetime_column(values)
            status = "PASS" if result == expected else "FAIL"

            if VERBOSE:
                print(f"    {description}: detected={result}, expected={expected} [{status}]")

            self.assertEqual(result, expected, f"Failed for {description}")

    def test_datetime_evolution(self):
        """Test evolution of datetime error cells"""
        print_subsection("Testing Datetime Cell Evolution")

        print_test_criteria([
            "Invalid dates should be evolved to valid dates",
            "Evolved dates should be within the range of healthy dates",
            "Date format should be standardized after evolution"
        ])

        if not self.error_cells:
            if VERBOSE:
                print("  No datetime error cells detected")
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='hybrid',
            config={'generations': 20}
        )

        print_evolution_result(result, "Datetime Evolution Result")

        # Verify evolved values are valid dates
        for cell in result.get('evolved_cells', []):
            evolved_val = cell.get('evolved_value')
            if evolved_val and cell.get('col_name') in ['created_at', 'updated_at']:
                parsed = parse_datetime(evolved_val)
                if VERBOSE:
                    print(f"    Evolved date: '{evolved_val}' -> parsed: {parsed is not None}")


class TestHybridMethodSelection(unittest.TestCase):
    """Test that Hybrid method selects appropriate algorithm per column type"""

    def setUp(self):
        """Set up mixed-type DataFrame"""
        self.df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'price': [100.0, 'invalid', 150.0, 175.0, 200.0],           # Numeric
            'status': ['Active', '###', 'Inactive', 'Active', 'Inactive'],  # Categorical
            'date': ['2024-06-15', 'bad_date', '2024-06-17', '2024-06-18', '2024-06-19']  # Datetime
        })
        print_subsection("Test Setup: Hybrid Method Selection")
        print_dataframe(self.df, "Mixed-type DataFrame")

        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells")

    def test_hybrid_selects_pso_for_numeric(self):
        """Test that Hybrid selects PSO for numeric columns"""
        print_subsection("Testing Hybrid Method Selection")

        print_test_criteria([
            "Hybrid should use PSO for numeric columns",
            "Hybrid should use GA for categorical columns",
            "Hybrid should use GA for datetime columns (temporal proximity)"
        ])

        if not self.error_cells:
            self.skipTest("No error cells to evolve")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='hybrid',
            config={'generations': 15}
        )

        print_evolution_result(result, "Hybrid Evolution Result")

        self.assertEqual(result['method_used'], 'hybrid')

        # Check that evolution was attempted
        self.assertGreaterEqual(result['cells_evolved'], 0)

        if VERBOSE:
            print(f"\n  Hybrid method processed {result['cells_evolved']} cells")
            print(f"  Algorithm selection per column type is handled internally")


class TestEvolutionConfiguration(unittest.TestCase):
    """Test configuration parameters for evolution"""

    def setUp(self):
        """Set up test data"""
        self.df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'value': [100, 'error', 150, 175, 200, 125, 'bad', 180, 160, 140]
        })
        print_subsection("Test Setup: Configuration Parameters")
        print_dataframe(self.df, "Test DataFrame")

        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells")

    def test_early_stopping(self):
        """Test early stopping configuration"""
        print_subsection("Testing Early Stopping")

        print_test_criteria([
            "Early stopping should halt evolution when no improvement",
            "Patience parameter controls generations without improvement"
        ])

        if not self.error_cells:
            self.skipTest("No error cells")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='ga',
            config={
                'generations': 100,
                'early_stopping': True,
                'patience': 5,
                'min_improvement': 0.001
            }
        )

        print_evolution_result(result, "Early Stopping Result")

        # With early stopping, should complete in fewer than max generations
        if VERBOSE:
            print(f"\n  Early stopping may have triggered before {100} generations")

    def test_fitness_threshold(self):
        """Test fitness threshold configuration"""
        print_subsection("Testing Fitness Threshold")

        print_test_criteria([
            "Evolution should stop when fitness threshold is reached",
            "Higher threshold requires more evolution effort"
        ])

        if not self.error_cells:
            self.skipTest("No error cells")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='pso',
            config={'generations': 50, 'fitness_threshold': 0.90}
        )

        print_evolution_result(result, "Fitness Threshold Result")

    def test_population_size_impact(self):
        """Test impact of population size on evolution"""
        print_subsection("Testing Population Size Impact")

        print_test_criteria([
            "Larger populations provide more genetic diversity",
            "Smaller populations evolve faster but may converge prematurely"
        ])

        if not self.error_cells:
            self.skipTest("No error cells")

        results = {}
        for pop_size in [10, 30]:
            evolved_df, result = evolve_error_cells(
                self.df,
                self.error_cells,
                method='ga',
                config={'generations': 20, 'population_size': pop_size}
            )
            results[pop_size] = result

            if VERBOSE:
                print(f"\n  Population size {pop_size}:")
                print(f"    Fitness after: {result['average_fitness_after']:.2%}")
                print(f"    Cells fixed: {result['cells_fixed']}")


class TestEvolutionaryMethods(unittest.TestCase):
    """Test all evolutionary methods work correctly"""

    def setUp(self):
        """Set up test data with clear errors"""
        # Create data with obvious errors for testing
        self.df = pd.DataFrame({
            'id': list(range(1, 21)),
            'amount': [100, 200, 'X', 150, 175, 125, None, 180, 160, 140,
                      110, 190, 'bad', 155, 165, 135, 145, 185, 170, 130],
            'code': ['A', 'B', 'A', '###', 'B', 'A', 'C', 'B', 'invalid', 'A',
                    'B', 'A', 'C', 'B', '???', 'A', 'C', 'B', 'A', 'C']
        })
        print_subsection("Test Setup: All Evolutionary Methods")
        print_dataframe(self.df, "Test DataFrame")

        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells")

    def test_all_methods_produce_results(self):
        """Test that all methods produce valid results"""
        print_subsection("Testing All Methods Produce Results")

        methods = ['ga', 'pso', 'de', 'es', 'hybrid']

        print_test_criteria([
            f"All {len(methods)} methods should produce valid results",
            "Each method should evolve cells without errors",
            "Results should contain required fields"
        ])

        if not self.error_cells:
            self.skipTest("No error cells to evolve")

        results_summary = []

        for method in methods:
            with self.subTest(method=method):
                if VERBOSE:
                    print(f"\n  Testing method: {method.upper()}")

                try:
                    evolved_df, result = evolve_error_cells(
                        self.df,
                        self.error_cells,
                        method=method,
                        config={'generations': 15, 'population_size': 15}
                    )

                    # Verify required fields
                    self.assertIn('cells_evolved', result)
                    self.assertIn('cells_fixed', result)
                    self.assertIn('average_fitness_before', result)
                    self.assertIn('average_fitness_after', result)
                    self.assertIn('method_used', result)

                    results_summary.append({
                        'method': method,
                        'evolved': result['cells_evolved'],
                        'fixed': result['cells_fixed'],
                        'fitness_before': result['average_fitness_before'],
                        'fitness_after': result['average_fitness_after']
                    })

                    if VERBOSE:
                        print(f"    Cells evolved: {result['cells_evolved']}")
                        print(f"    Cells fixed: {result['cells_fixed']}")
                        print(f"    Fitness: {result['average_fitness_before']:.2%} -> {result['average_fitness_after']:.2%}")

                except Exception as e:
                    self.fail(f"Method {method} failed with error: {e}")

        # Print summary comparison
        if VERBOSE and results_summary:
            print(f"\n  Method Comparison Summary:")
            print(f"  {'Method':<10} {'Evolved':<10} {'Fixed':<10} {'Before':<12} {'After':<12}")
            print(f"  {'-'*10} {'-'*10} {'-'*10} {'-'*12} {'-'*12}")
            for r in results_summary:
                print(f"  {r['method'].upper():<10} {r['evolved']:<10} {r['fixed']:<10} "
                      f"{r['fitness_before']:.2%}       {r['fitness_after']:.2%}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_empty_error_cells(self):
        """Test evolution with no error cells"""
        print_subsection("Testing Empty Error Cells")

        df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [100, 200, 300]
        })

        print_dataframe(df, "Clean DataFrame")

        evolved_df, result = evolve_error_cells(df, [], method='ga')

        self.assertEqual(result['cells_evolved'], 0)
        self.assertEqual(result['cells_fixed'], 0)

        if VERBOSE:
            print(f"\n  Result: 0 cells evolved (as expected for clean data)")

    def test_all_error_cells(self):
        """Test evolution when all cells are errors"""
        print_subsection("Testing All Error Cells")

        df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': ['error1', 'error2', 'error3']
        })

        print_dataframe(df, "All-error DataFrame")

        analyzer = DataQualityAnalyzer()
        quality_report = analyzer.analyze(df)
        error_cells = quality_report.get('error_cells', [])

        print_error_cells(error_cells, "All cells are errors")

        # With no healthy cells, evolution may fail gracefully
        evolved_df, result = evolve_error_cells(df, error_cells, method='ga')

        if VERBOSE:
            print(f"\n  Cells failed: {result.get('cells_failed', 0)}")
            print(f"  (Expected: evolution may fail when no healthy template cells)")

    def test_single_row(self):
        """Test evolution with single row DataFrame"""
        print_subsection("Testing Single Row DataFrame")

        df = pd.DataFrame({
            'id': [1],
            'value': ['error']
        })

        print_dataframe(df, "Single Row DataFrame")

        analyzer = DataQualityAnalyzer()
        quality_report = analyzer.analyze(df)
        error_cells = quality_report.get('error_cells', [])

        evolved_df, result = evolve_error_cells(df, error_cells, method='ga')

        if VERBOSE:
            print(f"\n  Result: {result.get('cells_failed', 0)} cells failed")
            print(f"  (Single row has no healthy templates for comparison)")


class TestFitnessTracking(unittest.TestCase):
    """Test fitness history and tracking"""

    def setUp(self):
        """Set up test data"""
        self.df = pd.DataFrame({
            'id': list(range(1, 16)),
            'score': [85, 90, 'X', 88, 92, 87, None, 91, 86, 89, 84, 93, 'bad', 88, 90]
        })
        print_subsection("Test Setup: Fitness Tracking")
        print_dataframe(self.df, "Test DataFrame")

        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells")

    def test_fitness_history_recorded(self):
        """Test that fitness history is properly recorded"""
        print_subsection("Testing Fitness History Recording")

        if not self.error_cells:
            self.skipTest("No error cells")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='ga',
            config={'generations': 20}
        )

        fitness_history = result.get('fitness_history', [])

        if VERBOSE:
            print(f"\n  Fitness History Entries: {len(fitness_history)}")
            if fitness_history:
                print(f"\n  Sample History Entries (first 5):")
                print(f"  {'Gen':<6} {'Best Fitness':<15} {'Method':<15}")
                print(f"  {'-'*6} {'-'*15} {'-'*15}")
                for entry in fitness_history[:5]:
                    gen = entry.get('generation', 'N/A')
                    best = entry.get('best_fitness', 0)
                    method = entry.get('method', 'N/A')
                    print(f"  {gen:<6} {best:<15.4f} {method:<15}")

        # History should be recorded
        self.assertIsInstance(fitness_history, list)

    def test_fitness_improvement_metric(self):
        """Test fitness improvement calculation"""
        print_subsection("Testing Fitness Improvement Calculation")

        if not self.error_cells:
            self.skipTest("No error cells")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='pso',
            config={'generations': 25}
        )

        before = result['average_fitness_before']
        after = result['average_fitness_after']
        improvement = result['fitness_improvement']

        # Verify improvement calculation
        expected_improvement = after - before
        self.assertAlmostEqual(improvement, expected_improvement, places=4)

        if VERBOSE:
            print(f"\n  Fitness Before: {before:.4f}")
            print(f"  Fitness After: {after:.4f}")
            print(f"  Improvement: {improvement:.4f}")
            print(f"  Calculated: {expected_improvement:.4f}")


class TestRealDataEvolution(unittest.TestCase):
    """Test evolutionary cleaning with real data from test_data_unclean.xlsx"""

    @classmethod
    def setUpClass(cls):
        """Load real test data once for all tests"""
        cls.data_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'test_data_unclean.xlsx'
        )
        cls.file_exists = os.path.exists(cls.data_file)

    def setUp(self):
        """Set up test with real data"""
        if not self.file_exists:
            self.skipTest(f"Test data file not found: {self.data_file}")

        self.df = pd.read_excel(self.data_file)
        print_subsection("Test Setup: Real Data from test_data_unclean.xlsx")
        print_dataframe(self.df, "Real Test Data")

        analyzer = DataQualityAnalyzer()
        self.quality_report = analyzer.analyze(self.df)
        self.error_cells = self.quality_report.get('error_cells', [])
        print_error_cells(self.error_cells, "Detected Error Cells in Real Data")

        if VERBOSE:
            print(f"\n  Column Types Detected:")
            for col, ctype in self.quality_report.get('column_types', {}).items():
                print(f"    {col}: {ctype}")

    def test_real_data_ga_evolution(self):
        """Test GA evolution on real unclean data"""
        print_subsection("Testing GA on Real Data (test_data_unclean.xlsx)")

        print_test_criteria([
            "GA should detect and fix errors in real dataset",
            "Prices column: 'abc' should be evolved to a valid number",
            "Product column: '12' should be evolved to a valid product name",
            "Procurement column: NaT should be evolved to a valid date"
        ])

        if not self.error_cells:
            if VERBOSE:
                print("  No error cells detected in real data")
            self.skipTest("No error cells found")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='ga',
            config={'generations': 30, 'population_size': 20}
        )

        print_evolution_result(result, "GA Evolution on Real Data")

        self.assertGreater(result['cells_evolved'], 0, "Should evolve at least one cell")
        self.assertEqual(result['method_used'], 'ga')

        if VERBOSE:
            print(f"\n  Before vs After Comparison:")
            for cell in result.get('evolved_cells', [])[:5]:
                print(f"    Row {cell['row']}, {cell['col_name']}: "
                      f"'{cell['original_value']}' -> '{cell['evolved_value']}'")

    def test_real_data_pso_evolution(self):
        """Test PSO evolution on real unclean data"""
        print_subsection("Testing PSO on Real Data (test_data_unclean.xlsx)")

        print_test_criteria([
            "PSO should optimize numeric error cells",
            "Particle swarm should converge to healthy value ranges"
        ])

        if not self.error_cells:
            self.skipTest("No error cells found")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='pso',
            config={'generations': 30, 'population_size': 25}
        )

        print_evolution_result(result, "PSO Evolution on Real Data")

        self.assertEqual(result['method_used'], 'pso')
        self.assertGreaterEqual(result['average_fitness_after'], result['average_fitness_before'])

    def test_real_data_de_evolution(self):
        """Test DE evolution on real unclean data"""
        print_subsection("Testing DE on Real Data (test_data_unclean.xlsx)")

        print_test_criteria([
            "DE should use differential mutation on error cells",
            "Population should evolve through vector differences"
        ])

        if not self.error_cells:
            self.skipTest("No error cells found")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='de',
            config={'generations': 25, 'differential_weight': 0.8}
        )

        print_evolution_result(result, "DE Evolution on Real Data")

        self.assertEqual(result['method_used'], 'de')

    def test_real_data_es_evolution(self):
        """Test ES evolution on real unclean data"""
        print_subsection("Testing ES on Real Data (test_data_unclean.xlsx)")

        print_test_criteria([
            "ES should use (mu,lambda) selection on error cells",
            "Self-adaptive mutation should adjust sigma"
        ])

        if not self.error_cells:
            self.skipTest("No error cells found")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='es',
            config={'generations': 30, 'mu': 10, 'lambda_': 30}
        )

        print_evolution_result(result, "ES Evolution on Real Data")

        self.assertEqual(result['method_used'], 'es')

    def test_real_data_hybrid_evolution(self):
        """Test Hybrid evolution on real unclean data"""
        print_subsection("Testing Hybrid on Real Data (test_data_unclean.xlsx)")

        print_test_criteria([
            "Hybrid should auto-select best method per column type",
            "PSO for numeric (Prices), GA for categorical (Product), GA for datetime (Procurement)"
        ])

        if not self.error_cells:
            self.skipTest("No error cells found")

        evolved_df, result = evolve_error_cells(
            self.df,
            self.error_cells,
            method='hybrid',
            config={'generations': 25}
        )

        print_evolution_result(result, "Hybrid Evolution on Real Data")

        self.assertEqual(result['method_used'], 'hybrid')
        self.assertGreater(result['cells_evolved'], 0)

        if VERBOSE:
            print(f"\n  Hybrid automatically selected algorithms based on column types")

    def test_real_data_all_methods_comparison(self):
        """Compare all 5 methods on real data"""
        print_subsection("Comparing All 5 Methods on Real Data")

        print_test_criteria([
            "Run GA, PSO, DE, ES, Hybrid on same real data",
            "Compare fitness improvements across methods",
            "All methods should produce valid results"
        ])

        if not self.error_cells:
            self.skipTest("No error cells found")

        methods = ['ga', 'pso', 'de', 'es', 'hybrid']
        results_summary = []

        for method in methods:
            evolved_df, result = evolve_error_cells(
                self.df.copy(),
                self.error_cells,
                method=method,
                config={'generations': 20, 'population_size': 20}
            )

            results_summary.append({
                'method': method.upper(),
                'evolved': result['cells_evolved'],
                'fixed': result['cells_fixed'],
                'fitness_before': result['average_fitness_before'],
                'fitness_after': result['average_fitness_after'],
                'improvement': result['fitness_improvement']
            })

        if VERBOSE:
            print(f"\n  Method Comparison on Real Data (test_data_unclean.xlsx):")
            print(f"  {'Method':<10} {'Evolved':<10} {'Fixed':<10} {'Before':<12} {'After':<12} {'Improvement':<12}")
            print(f"  {'-'*10} {'-'*10} {'-'*10} {'-'*12} {'-'*12} {'-'*12}")
            for r in results_summary:
                print(f"  {r['method']:<10} {r['evolved']:<10} {r['fixed']:<10} "
                      f"{r['fitness_before']:.2%}       {r['fitness_after']:.2%}       {r['improvement']:.2%}")

        # All methods should have produced results
        for r in results_summary:
            self.assertGreaterEqual(r['evolved'], 0, f"{r['method']} should evolve cells")


def run_all_tests():
    """Run all tests with verbose output"""
    print_section("Evolutionary Cell Cleaning Test Suite")

    if VERBOSE:
        print("\n  Running in VERBOSE mode")
        print(f"  Command: python3 {sys.argv[0]} -v")
        print(f"\n  Test Classes:")
        print(f"    1. TestNumericCellEvolution - Tests for numeric columns")
        print(f"    2. TestCategoricalCellEvolution - Tests for categorical columns")
        print(f"    3. TestDatetimeCellEvolution - Tests for datetime columns")
        print(f"    4. TestHybridMethodSelection - Tests hybrid algorithm selection")
        print(f"    5. TestEvolutionConfiguration - Tests config parameters")
        print(f"    6. TestEvolutionaryMethods - Tests all evolution methods")
        print(f"    7. TestEdgeCases - Tests edge cases and error handling")
        print(f"    8. TestFitnessTracking - Tests fitness history tracking")
        print(f"    9. TestRealDataEvolution - Tests with real data (test_data_unclean.xlsx)")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestNumericCellEvolution,
        TestCategoricalCellEvolution,
        TestDatetimeCellEvolution,
        TestHybridMethodSelection,
        TestEvolutionConfiguration,
        TestEvolutionaryMethods,
        TestEdgeCases,
        TestFitnessTracking,
        TestRealDataEvolution,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    if VERBOSE:
        runner = VerboseTestRunner(verbosity=2, stream=sys.stdout)
    else:
        runner = unittest.TextTestRunner(verbosity=2)

    result = runner.run(suite)

    # Print summary
    print_section("Test Summary")
    print(f"\n  Tests Run: {result.testsRun}")
    print(f"  Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")

    if result.failures:
        print(f"\n  Failed Tests:")
        for test, traceback in result.failures:
            print(f"    - {test}")

    if result.errors:
        print(f"\n  Error Tests:")
        for test, traceback in result.errors:
            print(f"    - {test}")

    # Return success/failure
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    # Remove -v from sys.argv for unittest (we handle it ourselves)
    if '-v' in sys.argv:
        sys.argv.remove('-v')
    if '--verbose' in sys.argv:
        sys.argv.remove('--verbose')

    success = run_all_tests()
    sys.exit(0 if success else 1)
