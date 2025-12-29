"""
Comprehensive Unit Tests for ES System
=======================================
Tests for all ES operators, engine, and components.
Can be run individually from command prompt.
"""

import numpy as np
import unittest
import logging

from es_operators import (
    ESConfig, ESSelectionType, ESRecombinationType,
    ConstraintHandling, ESMetrics, ESResult, ESOperators
)
from es_engine import EvolutionStrategyOptimizer, optimize_value_es

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TestESConfig(unittest.TestCase):
    """Test ESConfig validation"""

    def test_valid_config(self):
        config = ESConfig(mu=15, lambda_=100, generations=100)
        is_valid, errors = config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_mu(self):
        config = ESConfig(mu=0)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('mu' in e for e in errors))

    def test_invalid_lambda(self):
        config = ESConfig(lambda_=0)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('lambda' in e for e in errors))

    def test_comma_selection_requires_large_lambda(self):
        config = ESConfig(
            mu=20,
            lambda_=10,  # lambda < mu
            selection_type=ESSelectionType.COMMA
        )
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('lambda' in e.lower() for e in errors))

    def test_invalid_rho(self):
        config = ESConfig(mu=10, rho=20)  # rho > mu
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('rho' in e for e in errors))

    def test_invalid_sigma(self):
        config = ESConfig(initial_sigma=-0.1)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)

    def test_get_tau_values(self):
        config = ESConfig()
        tau, tau_prime = config.get_tau_values(n_dimensions=1)
        self.assertGreater(tau, 0)
        self.assertGreater(tau_prime, 0)


class TestPopulationInitialization(unittest.TestCase):
    """Test population initialization"""

    def test_initialize_basic(self):
        population, sigmas = ESOperators.initialize_population(
            mu=10,
            bounds_min=0.0,
            bounds_max=10.0,
            initial_sigma=0.3
        )

        self.assertEqual(len(population), 10)
        self.assertEqual(len(sigmas), 10)
        self.assertTrue(np.all(population >= 0.0))
        self.assertTrue(np.all(population <= 10.0))
        self.assertTrue(np.all(sigmas == 0.3))

    def test_initialize_with_seed(self):
        seed_values = np.array([4.0, 5.0, 6.0])
        population, sigmas = ESOperators.initialize_population(
            mu=10,
            bounds_min=0.0,
            bounds_max=10.0,
            initial_sigma=0.3,
            seed_values=seed_values,
            seed_ratio=0.5
        )

        self.assertEqual(len(population), 10)
        self.assertTrue(np.all(population >= 0.0))
        self.assertTrue(np.all(population <= 10.0))


class TestRecombination(unittest.TestCase):
    """Test recombination operators"""

    def setUp(self):
        self.parents = np.array([2.0, 4.0, 6.0, 8.0])
        self.sigmas = np.array([0.2, 0.3, 0.4, 0.5])

    def test_discrete_recombination(self):
        value, sigma = ESOperators.recombine_discrete(
            self.parents, self.sigmas
        )
        self.assertIn(value, self.parents)
        self.assertIn(sigma, self.sigmas)

    def test_intermediate_recombination(self):
        value, sigma = ESOperators.recombine_intermediate(
            self.parents, self.sigmas
        )
        self.assertEqual(value, np.mean(self.parents))
        self.assertEqual(sigma, np.mean(self.sigmas))

    def test_global_discrete_recombination(self):
        population = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
        sigmas = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

        value, sigma = ESOperators.recombine_global_discrete(
            population, sigmas, rho=3
        )
        self.assertIn(value, population)
        self.assertIn(sigma, sigmas)

    def test_apply_recombination_dispatcher(self):
        fitness = np.array([10.0, 20.0, 30.0, 40.0])

        for recomb_type in ESRecombinationType:
            value, sigma, stats = ESOperators.apply_recombination(
                recomb_type=recomb_type,
                population=self.parents,
                sigmas=self.sigmas,
                fitness=fitness,
                rho=2
            )
            self.assertIsInstance(value, float)
            self.assertIsInstance(sigma, float)


class TestMutation(unittest.TestCase):
    """Test mutation operators"""

    def test_gaussian_mutation(self):
        mutated = ESOperators.mutate_gaussian(
            value=5.0,
            sigma=0.5,
            bounds_min=0.0,
            bounds_max=10.0
        )
        self.assertTrue(0.0 <= mutated <= 10.0)

    def test_sigma_self_adaptive(self):
        new_sigma = ESOperators.mutate_sigma_self_adaptive(
            sigma=0.5,
            tau=0.5,
            tau_prime=0.5,
            sigma_min=0.01,
            sigma_max=1.0
        )
        self.assertTrue(0.01 <= new_sigma <= 1.0)

    def test_apply_mutation_fixed(self):
        config = ESConfig(self_adaptive=False, initial_sigma=0.3)
        new_val, new_sigma, stats = ESOperators.apply_mutation(
            value=5.0,
            sigma=0.3,
            config=config,
            bounds_min=0.0,
            bounds_max=10.0
        )
        self.assertEqual(new_sigma, 0.3)  # Sigma unchanged
        self.assertTrue(0.0 <= new_val <= 10.0)

    def test_apply_mutation_adaptive(self):
        config = ESConfig(self_adaptive=True, initial_sigma=0.3)
        new_val, new_sigma, stats = ESOperators.apply_mutation(
            value=5.0,
            sigma=0.3,
            config=config,
            bounds_min=0.0,
            bounds_max=10.0
        )
        # Sigma should potentially change
        self.assertTrue(config.sigma_min <= new_sigma <= config.sigma_max)
        self.assertTrue(0.0 <= new_val <= 10.0)


class TestSelection(unittest.TestCase):
    """Test selection operators"""

    def setUp(self):
        self.parents = np.array([1.0, 2.0, 3.0, 4.0])
        self.parent_sigmas = np.array([0.2, 0.2, 0.2, 0.2])
        self.parent_fitness = np.array([10.0, 20.0, 30.0, 40.0])

        self.offspring = np.array([3.5, 4.5, 5.0, 5.5, 6.0, 6.5])
        self.offspring_sigmas = np.array([0.15, 0.15, 0.15, 0.15, 0.15, 0.15])
        self.offspring_fitness = np.array([35.0, 45.0, 50.0, 45.0, 40.0, 35.0])

    def test_plus_selection(self):
        sel_pop, sel_sig, sel_fit, stats = ESOperators.select_plus(
            parents=self.parents,
            parent_sigmas=self.parent_sigmas,
            parent_fitness=self.parent_fitness,
            offspring=self.offspring,
            offspring_sigmas=self.offspring_sigmas,
            offspring_fitness=self.offspring_fitness,
            mu=3
        )

        self.assertEqual(len(sel_pop), 3)
        self.assertEqual(len(sel_sig), 3)
        self.assertEqual(len(sel_fit), 3)
        # Best 3 should be selected
        self.assertEqual(sel_fit[0], 50.0)
        self.assertEqual(stats['selection_type'], 'plus')

    def test_comma_selection(self):
        sel_pop, sel_sig, sel_fit, stats = ESOperators.select_comma(
            offspring=self.offspring,
            offspring_sigmas=self.offspring_sigmas,
            offspring_fitness=self.offspring_fitness,
            mu=3
        )

        self.assertEqual(len(sel_pop), 3)
        self.assertEqual(stats['selection_type'], 'comma')
        self.assertEqual(stats['parents_retained'], 0)

    def test_comma_selection_requires_enough_offspring(self):
        with self.assertRaises(ValueError):
            ESOperators.select_comma(
                offspring=np.array([1.0, 2.0]),
                offspring_sigmas=np.array([0.1, 0.1]),
                offspring_fitness=np.array([10.0, 20.0]),
                mu=5  # More than offspring
            )

    def test_apply_selection_dispatcher(self):
        for sel_type in ESSelectionType:
            sel_pop, sel_sig, sel_fit, stats = ESOperators.apply_selection(
                selection_type=sel_type,
                parents=self.parents,
                parent_sigmas=self.parent_sigmas,
                parent_fitness=self.parent_fitness,
                offspring=self.offspring,
                offspring_sigmas=self.offspring_sigmas,
                offspring_fitness=self.offspring_fitness,
                mu=3
            )
            self.assertEqual(len(sel_pop), 3)


class TestConstraintHandling(unittest.TestCase):
    """Test constraint handling"""

    def test_clamp(self):
        result = ESOperators.apply_constraints(15.0, 0.0, 10.0, ConstraintHandling.CLAMP)
        self.assertEqual(result, 10.0)

        result = ESOperators.apply_constraints(-5.0, 0.0, 10.0, ConstraintHandling.CLAMP)
        self.assertEqual(result, 0.0)

    def test_reflect(self):
        result = ESOperators.apply_constraints(12.0, 0.0, 10.0, ConstraintHandling.REFLECT)
        self.assertEqual(result, 8.0)

    def test_random(self):
        result = ESOperators.apply_constraints(15.0, 0.0, 10.0, ConstraintHandling.RANDOM)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 10.0)

    def test_in_bounds(self):
        for handling in ConstraintHandling:
            result = ESOperators.apply_constraints(5.0, 0.0, 10.0, handling)
            self.assertEqual(result, 5.0)


class TestDiversity(unittest.TestCase):
    """Test diversity calculation"""

    def test_diverse_population(self):
        population = np.array([0.0, 2.5, 5.0, 7.5, 10.0])
        diversity = ESOperators.calculate_diversity(population)
        self.assertGreater(diversity, 0.0)

    def test_converged_population(self):
        population = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        diversity = ESOperators.calculate_diversity(population)
        self.assertEqual(diversity, 0.0)


class TestSigmaStats(unittest.TestCase):
    """Test sigma statistics"""

    def test_sigma_stats(self):
        sigmas = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        stats = ESOperators.calculate_sigma_stats(sigmas)

        self.assertEqual(stats['average'], 0.3)
        self.assertGreater(stats['std'], 0)
        self.assertEqual(stats['min'], 0.1)
        self.assertEqual(stats['max'], 0.5)


class TestESMetrics(unittest.TestCase):
    """Test metrics dataclass"""

    def test_metrics_to_dict(self):
        metrics = ESMetrics(
            generation=10,
            best_fitness=100.0,
            average_fitness=75.0,
            worst_fitness=50.0,
            population_diversity=0.8,
            convergence_rate=0.05,
            offspring_generated=100,
            parents_selected=15,
            average_sigma=0.25,
            sigma_std=0.05,
            min_sigma=0.1,
            max_sigma=0.4,
            successful_mutations=30,
            success_rate=0.3,
            stagnation_counter=2
        )

        d = metrics.to_dict()
        self.assertEqual(d['generation'], 10)
        self.assertEqual(d['best_fitness'], 100.0)
        self.assertEqual(d['method'], 'ES')


class TestESEngine(unittest.TestCase):
    """Test complete ES engine"""

    def setUp(self):
        self.fitness_func = lambda x: -((x - 5) ** 2)
        self.config = ESConfig(
            mu=15,
            lambda_=100,
            generations=30,
            early_stopping=True,
            patience=5
        )

    def test_engine_initialization(self):
        engine = EvolutionStrategyOptimizer(
            config=self.config,
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0
        )

        self.assertEqual(len(engine.population), self.config.mu)
        self.assertEqual(len(engine.sigmas), self.config.mu)

    def test_engine_run(self):
        engine = EvolutionStrategyOptimizer(
            config=self.config,
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0
        )
        result = engine.run()

        self.assertIsInstance(result, ESResult)
        self.assertGreater(result.total_generations, 0)
        self.assertIsNotNone(result.best_individual)
        # Optimal is x=5, fitness=0
        self.assertAlmostEqual(result.best_individual[0], 5.0, places=1)

    def test_convenience_function(self):
        result = optimize_value_es(
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=self.config
        )

        self.assertIsInstance(result, ESResult)
        self.assertAlmostEqual(result.best_individual[0], 5.0, places=1)

    def test_all_selection_types(self):
        for selection in ESSelectionType:
            config = ESConfig(
                mu=10,
                lambda_=70,
                generations=20,
                selection_type=selection
            )
            result = optimize_value_es(
                fitness_function=self.fitness_func,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )
            self.assertIsNotNone(result.best_individual)

    def test_all_recombination_types(self):
        for recomb in ESRecombinationType:
            config = ESConfig(
                mu=10,
                lambda_=70,
                generations=20,
                recombination_type=recomb
            )
            result = optimize_value_es(
                fitness_function=self.fitness_func,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )
            self.assertIsNotNone(result.best_individual)

    def test_self_adaptive_mutation(self):
        config = ESConfig(
            mu=15,
            lambda_=100,
            generations=40,
            self_adaptive=True,
            early_stopping=False
        )
        result = optimize_value_es(
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        self.assertEqual(len(result.sigma_history), result.total_generations)

    def test_with_seed_values(self):
        seed_values = np.array([4.0, 5.0, 6.0])
        result = optimize_value_es(
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

        config = ESConfig(
            mu=20,
            lambda_=140,
            generations=100,
            early_stopping=True,
            patience=5,
            fitness_threshold=-0.01
        )

        result = optimize_value_es(
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
    print("RUNNING COMPREHENSIVE ES UNIT TESTS")
    print("="*70 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestESConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestPopulationInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestRecombination))
    suite.addTests(loader.loadTestsFromTestCase(TestMutation))
    suite.addTests(loader.loadTestsFromTestCase(TestSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestConstraintHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDiversity))
    suite.addTests(loader.loadTestsFromTestCase(TestSigmaStats))
    suite.addTests(loader.loadTestsFromTestCase(TestESMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestESEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestConvergence))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
