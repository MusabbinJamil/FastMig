"""
Comprehensive Unit Tests for DE System
=======================================
Tests for all DE operators, engine, and components.
Can be run individually from command prompt.

Usage:
    python3 test_de_system.py           # Basic output
    python3 test_de_system.py -v        # Verbose output with detailed data
    python3 test_de_system.py --verbose # Same as -v
"""

import numpy as np
import unittest
import logging
import sys

from de_operators import (
    DEConfig, DEMutationStrategy, DECrossoverType,
    ConstraintHandling, DEMetrics, DEResult, DEOperators
)
from de_engine import DifferentialEvolutionOptimizer, optimize_value_de

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global verbose flag
VERBOSE = '-v' in sys.argv or '--verbose' in sys.argv


class VerboseTestResult(unittest.TextTestResult):
    """Custom test result class for verbose output"""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_details = []

    def startTest(self, test):
        super().startTest(test)
        if VERBOSE:
            self.stream.write("\n" + "-"*60 + "\n")
            self.stream.write(f"  TEST: {test._testMethodName}\n")
            self.stream.write("-"*60 + "\n")
            if test._testMethodDoc:
                self.stream.write(f"  Description: {test._testMethodDoc.strip()}\n")

    def addSuccess(self, test):
        super().addSuccess(test)
        if VERBOSE:
            self.stream.write(f"  Result: PASSED\n")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if VERBOSE:
            self.stream.write(f"  Result: FAILED\n")
            self.stream.write(f"  Error: {err[1]}\n")

    def addError(self, test, err):
        super().addError(test, err)
        if VERBOSE:
            self.stream.write(f"  Result: ERROR\n")
            self.stream.write(f"  Error: {err[1]}\n")


class VerboseTestRunner(unittest.TextTestRunner):
    """Custom test runner for verbose output"""

    def __init__(self, **kwargs):
        kwargs['resultclass'] = VerboseTestResult
        super().__init__(**kwargs)


class TestDEConfig(unittest.TestCase):
    """Test DEConfig validation"""

    def test_valid_config(self):
        config = DEConfig(population_size=30, generations=100)
        is_valid, errors = config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_population_size(self):
        config = DEConfig(population_size=2)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('population_size' in e for e in errors))

    def test_invalid_generations(self):
        config = DEConfig(generations=0)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('generations' in e for e in errors))

    def test_invalid_scale_factor(self):
        config = DEConfig(scale_factor=3.0)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('scale_factor' in e for e in errors))

    def test_invalid_crossover_rate(self):
        config = DEConfig(crossover_rate=1.5)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('crossover_rate' in e for e in errors))

    def test_strategy_population_requirements(self):
        # DE/rand/2 requires at least 6 individuals
        config = DEConfig(population_size=5, mutation_strategy=DEMutationStrategy.RAND_2)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)


class TestPopulationInitialization(unittest.TestCase):
    """Test population initialization"""

    def test_initialize_basic(self):
        population = DEOperators.initialize_population(
            pop_size=10,
            bounds_min=0.0,
            bounds_max=10.0
        )

        self.assertEqual(len(population), 10)
        self.assertTrue(np.all(population >= 0.0))
        self.assertTrue(np.all(population <= 10.0))

    def test_initialize_with_seed(self):
        seed_values = np.array([3.0, 5.0, 7.0])
        population = DEOperators.initialize_population(
            pop_size=10,
            bounds_min=0.0,
            bounds_max=10.0,
            seed_values=seed_values,
            seed_ratio=0.5
        )

        self.assertEqual(len(population), 10)
        self.assertTrue(np.all(population >= 0.0))
        self.assertTrue(np.all(population <= 10.0))


class TestMutationStrategies(unittest.TestCase):
    """Test mutation strategies"""

    def setUp(self):
        self.population = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        self.fitness = -((self.population - 5) ** 2)

    def test_rand_1(self):
        mutant, stats = DEOperators.mutate_rand_1(
            population=self.population,
            fitness=self.fitness,
            target_idx=0,
            F=0.8
        )

        self.assertIsInstance(mutant, float)
        self.assertIn('base_idx', stats)

    def test_rand_2(self):
        mutant, stats = DEOperators.mutate_rand_2(
            population=self.population,
            fitness=self.fitness,
            target_idx=0,
            F=0.8
        )

        self.assertIsInstance(mutant, float)
        self.assertEqual(len(stats['diff_indices']), 4)

    def test_best_1(self):
        mutant, stats = DEOperators.mutate_best_1(
            population=self.population,
            fitness=self.fitness,
            target_idx=0,
            F=0.8
        )

        self.assertIsInstance(mutant, float)
        self.assertTrue(stats.get('is_best', False))

    def test_best_2(self):
        mutant, stats = DEOperators.mutate_best_2(
            population=self.population,
            fitness=self.fitness,
            target_idx=0,
            F=0.8
        )

        self.assertIsInstance(mutant, float)

    def test_current_to_best_1(self):
        mutant, stats = DEOperators.mutate_current_to_best_1(
            population=self.population,
            fitness=self.fitness,
            target_idx=0,
            F=0.8
        )

        self.assertIsInstance(mutant, float)
        self.assertEqual(stats['strategy'], 'current-to-best')

    def test_current_to_rand_1(self):
        mutant, stats = DEOperators.mutate_current_to_rand_1(
            population=self.population,
            fitness=self.fitness,
            target_idx=0,
            F=0.8
        )

        self.assertIsInstance(mutant, float)
        self.assertEqual(stats['strategy'], 'current-to-rand')

    def test_apply_mutation_dispatcher(self):
        for strategy in DEMutationStrategy:
            mutant, stats = DEOperators.apply_mutation(
                strategy=strategy,
                population=self.population,
                fitness=self.fitness,
                target_idx=0,
                F=0.8
            )
            self.assertIsInstance(mutant, float)


class TestCrossover(unittest.TestCase):
    """Test crossover functions"""

    def test_binomial_crossover(self):
        target = 3.0
        mutant = 7.0

        # Run multiple times to test both outcomes
        results = []
        for _ in range(100):
            trial, from_mutant = DEOperators.crossover_binomial(target, mutant, CR=0.5)
            results.append((trial, from_mutant))

        # Should have mix of both
        from_mutant_count = sum(1 for _, fm in results if fm)
        self.assertGreater(from_mutant_count, 0)
        self.assertLess(from_mutant_count, 100)

    def test_exponential_crossover(self):
        target = 3.0
        mutant = 7.0

        trial, from_mutant = DEOperators.crossover_exponential(target, mutant, CR=0.9)
        self.assertIn(trial, [target, mutant])

    def test_apply_crossover_dispatcher(self):
        for crossover_type in DECrossoverType:
            trial, from_mutant = DEOperators.apply_crossover(
                crossover_type=crossover_type,
                target=3.0,
                mutant=7.0,
                CR=0.9
            )
            self.assertIsInstance(trial, float)
            self.assertIsInstance(from_mutant, bool)


class TestSelection(unittest.TestCase):
    """Test greedy selection"""

    def test_trial_wins(self):
        selected, fit, improved = DEOperators.greedy_selection(
            target_value=3.0,
            target_fitness=-4.0,
            trial_value=5.0,
            trial_fitness=0.0
        )

        self.assertEqual(selected, 5.0)
        self.assertEqual(fit, 0.0)
        self.assertTrue(improved)

    def test_target_wins(self):
        selected, fit, improved = DEOperators.greedy_selection(
            target_value=5.0,
            target_fitness=0.0,
            trial_value=3.0,
            trial_fitness=-4.0
        )

        self.assertEqual(selected, 5.0)
        self.assertEqual(fit, 0.0)
        self.assertFalse(improved)

    def test_tie_goes_to_target(self):
        selected, fit, improved = DEOperators.greedy_selection(
            target_value=5.0,
            target_fitness=0.0,
            trial_value=6.0,
            trial_fitness=0.0
        )

        self.assertEqual(selected, 5.0)
        self.assertFalse(improved)


class TestConstraintHandling(unittest.TestCase):
    """Test constraint handling"""

    def test_clamp(self):
        result = DEOperators.apply_constraints(15.0, 0.0, 10.0, ConstraintHandling.CLAMP)
        self.assertEqual(result, 10.0)

        result = DEOperators.apply_constraints(-5.0, 0.0, 10.0, ConstraintHandling.CLAMP)
        self.assertEqual(result, 0.0)

    def test_reflect(self):
        result = DEOperators.apply_constraints(12.0, 0.0, 10.0, ConstraintHandling.REFLECT)
        self.assertEqual(result, 8.0)  # 10 - (12-10) = 8

    def test_random(self):
        result = DEOperators.apply_constraints(15.0, 0.0, 10.0, ConstraintHandling.RANDOM)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 10.0)

    def test_in_bounds(self):
        for handling in ConstraintHandling:
            result = DEOperators.apply_constraints(5.0, 0.0, 10.0, handling)
            self.assertEqual(result, 5.0)


class TestAdaptiveParameters(unittest.TestCase):
    """Test adaptive F and CR"""

    def test_adapt_f_high_success(self):
        # High success rate should decrease F
        new_f = DEOperators.adapt_f(
            current_f=0.8,
            success_rate=0.5,  # High success
            f_min=0.1,
            f_max=1.0,
            learning_rate=0.1
        )
        self.assertLess(new_f, 0.8)

    def test_adapt_f_low_success(self):
        # Low success rate should increase F
        new_f = DEOperators.adapt_f(
            current_f=0.5,
            success_rate=0.05,  # Low success
            f_min=0.1,
            f_max=1.0,
            learning_rate=0.1
        )
        self.assertGreater(new_f, 0.5)

    def test_adapt_cr(self):
        # Test CR adaptation
        new_cr = DEOperators.adapt_cr(
            current_cr=0.9,
            success_rate=0.5,
            cr_min=0.1,
            cr_max=1.0,
            learning_rate=0.1
        )
        self.assertLess(new_cr, 0.9)


class TestDiversity(unittest.TestCase):
    """Test diversity calculation"""

    def test_diverse_population(self):
        population = np.array([0.0, 2.5, 5.0, 7.5, 10.0])
        diversity = DEOperators.calculate_diversity(population)
        self.assertGreater(diversity, 0.0)

    def test_converged_population(self):
        population = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        diversity = DEOperators.calculate_diversity(population)
        self.assertEqual(diversity, 0.0)


class TestDEMetrics(unittest.TestCase):
    """Test metrics dataclass"""

    def test_metrics_to_dict(self):
        metrics = DEMetrics(
            generation=10,
            best_fitness=100.0,
            average_fitness=75.0,
            worst_fitness=50.0,
            population_diversity=0.8,
            convergence_rate=0.05,
            success_rate=0.3,
            trials_evaluated=30,
            improvements=9,
            current_f=0.75,
            current_cr=0.85,
            stagnation_counter=2
        )

        d = metrics.to_dict()
        self.assertEqual(d['generation'], 10)
        self.assertEqual(d['best_fitness'], 100.0)
        self.assertEqual(d['method'], 'DE')


class TestDEEngine(unittest.TestCase):
    """Test complete DE engine"""

    def setUp(self):
        self.fitness_func = lambda x: -((x - 5) ** 2)
        self.config = DEConfig(
            population_size=20,
            generations=30,
            early_stopping=True,
            patience=5
        )

    def test_engine_initialization(self):
        engine = DifferentialEvolutionOptimizer(
            config=self.config,
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0
        )

        self.assertEqual(len(engine.population), self.config.population_size)

    def test_engine_run(self):
        engine = DifferentialEvolutionOptimizer(
            config=self.config,
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0
        )
        result = engine.run()

        self.assertIsInstance(result, DEResult)
        self.assertGreater(result.total_generations, 0)
        self.assertIsNotNone(result.best_individual)
        # Optimal is x=5, fitness=0
        self.assertAlmostEqual(result.best_individual[0], 5.0, places=1)

    def test_convenience_function(self):
        result = optimize_value_de(
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=self.config
        )

        self.assertIsInstance(result, DEResult)
        self.assertAlmostEqual(result.best_individual[0], 5.0, places=1)

    def test_all_strategies(self):
        for strategy in DEMutationStrategy:
            pop_size = 30 if '2' in strategy.value else 20
            config = DEConfig(
                population_size=pop_size,
                generations=20,
                mutation_strategy=strategy
            )
            result = optimize_value_de(
                fitness_function=self.fitness_func,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )
            self.assertIsNotNone(result.best_individual)

    def test_all_crossover_types(self):
        for crossover in DECrossoverType:
            config = DEConfig(
                population_size=20,
                generations=20,
                crossover_type=crossover
            )
            result = optimize_value_de(
                fitness_function=self.fitness_func,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )
            self.assertIsNotNone(result.best_individual)

    def test_adaptive_parameters(self):
        config = DEConfig(
            population_size=20,
            generations=40,
            adaptive_f=True,
            adaptive_cr=True,
            early_stopping=False
        )
        result = optimize_value_de(
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        self.assertEqual(len(result.f_history), result.total_generations)
        self.assertEqual(len(result.cr_history), result.total_generations)

    def test_with_seed_values(self):
        seed_values = np.array([4.0, 5.0, 6.0])
        result = optimize_value_de(
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=self.config,
            seed_values=seed_values
        )
        self.assertAlmostEqual(result.best_individual[0], 5.0, places=1)


class TestConvergence(unittest.TestCase):
    """Test convergence behavior"""

    def test_early_stopping(self):
        def easy_fitness(x):
            return -((x - 5) ** 2)

        config = DEConfig(
            population_size=25,
            generations=100,
            early_stopping=True,
            patience=5,
            fitness_threshold=-0.01
        )

        result = optimize_value_de(
            fitness_function=easy_fitness,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        # Should converge before 100 generations
        self.assertLess(result.total_generations, 100)
        self.assertTrue(result.converged)


def run_all_tests():
    """Run all tests and print results"""
    print("\n" + "="*70)
    print("RUNNING COMPREHENSIVE DE UNIT TESTS")
    print("="*70)
    if VERBOSE:
        print("Mode: VERBOSE (showing detailed test information)")
    else:
        print("Mode: Standard (use -v or --verbose for detailed output)")
    print("="*70 + "\n")

    # Print test configuration in verbose mode
    if VERBOSE:
        print("Test Classes:")
        print("  - TestDEConfig: Configuration validation tests")
        print("  - TestPopulationInitialization: Population initialization tests")
        print("  - TestMutationStrategies: rand/1, rand/2, best/1, best/2, current-to-best")
        print("  - TestCrossover: Binomial and exponential crossover")
        print("  - TestSelection: Greedy selection mechanism")
        print("  - TestConstraintHandling: Clamp, reflect, random constraint handling")
        print("  - TestAdaptiveParameters: Adaptive F and CR parameters")
        print("  - TestDiversity: Population diversity calculation")
        print("  - TestDEMetrics: Metrics dataclass tests")
        print("  - TestDEEngine: Complete DE engine integration tests")
        print("  - TestConvergence: Early stopping and convergence tests")
        print("\n" + "="*70 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDEConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestPopulationInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestMutationStrategies))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossover))
    suite.addTests(loader.loadTestsFromTestCase(TestSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestConstraintHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveParameters))
    suite.addTests(loader.loadTestsFromTestCase(TestDiversity))
    suite.addTests(loader.loadTestsFromTestCase(TestDEMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestDEEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestConvergence))

    # Use verbose runner if verbose mode is enabled
    if VERBOSE:
        runner = VerboseTestRunner(verbosity=2)
    else:
        runner = unittest.TextTestRunner(verbosity=2)

    result = runner.run(suite)

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if VERBOSE and result.failures:
        print("\n" + "-"*70)
        print("FAILURE DETAILS:")
        print("-"*70)
        for test, traceback in result.failures:
            print(f"\n  Test: {test}")
            print(f"  Traceback:\n{traceback}")

    if VERBOSE and result.errors:
        print("\n" + "-"*70)
        print("ERROR DETAILS:")
        print("-"*70)
        for test, traceback in result.errors:
            print(f"\n  Test: {test}")
            print(f"  Traceback:\n{traceback}")

    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
