"""
Comprehensive Unit Tests for GA System
=======================================
Tests for all GA operators, engine, and components.
Can be run individually from command prompt.
"""

import numpy as np
import unittest
import logging
from typing import List

from ga_operators import (
    GAOperators, GAMetrics, GAConfig, SelectionMethod,
    CrossoverMethod, MutationMethod
)
from ga_genotype_phenotype import (
    RealValuedMapper, BinaryMapper, GrammarMapper, GenotypeType
)
from ga_engine import GeneticAlgorithmEngine, GAResult

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TestGAConfig(unittest.TestCase):
    """Test GAConfig validation"""
    
    def test_valid_config(self):
        config = GAConfig(population_size=50, generations=100)
        is_valid, errors = config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_population_size(self):
        config = GAConfig(population_size=2, generations=100)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('population_size' in e for e in errors))
    
    def test_invalid_crossover_rate(self):
        config = GAConfig(crossover_rate=1.5)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('crossover_rate' in e for e in errors))
    
    def test_invalid_mutation_rate(self):
        config = GAConfig(mutation_rate=-0.1)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('mutation_rate' in e for e in errors))


class TestSelectionOperators(unittest.TestCase):
    """Test selection operators"""
    
    def setUp(self):
        self.population = [np.array([1.0, 2.0, 3.0]),
                          np.array([4.0, 5.0, 6.0]),
                          np.array([7.0, 8.0, 9.0]),
                          np.array([10.0, 11.0, 12.0])]
        self.fitness_scores = [10.0, 20.0, 30.0, 40.0]
    
    def test_tournament_selection(self):
        selected, stats = GAOperators.selection_tournament(
            self.population, self.fitness_scores, 2, tournament_size=2
        )
        self.assertEqual(len(selected), 2)
        self.assertEqual(stats['method'], 'tournament')
    
    def test_roulette_wheel_selection(self):
        selected, stats = GAOperators.selection_roulette_wheel(
            self.population, self.fitness_scores, 2
        )
        self.assertEqual(len(selected), 2)
        self.assertEqual(stats['method'], 'roulette_wheel')
    
    def test_rank_based_selection(self):
        selected, stats = GAOperators.selection_rank_based(
            self.population, self.fitness_scores, 2
        )
        self.assertEqual(len(selected), 2)
        self.assertEqual(stats['method'], 'rank_based')
    
    def test_roulette_wheel_negative_fitness(self):
        # Should handle negative fitness gracefully
        negative_fitness = [-10.0, -5.0, 0.0, 5.0]
        selected, stats = GAOperators.selection_roulette_wheel(
            self.population, negative_fitness, 2
        )
        self.assertEqual(len(selected), 2)


class TestCrossoverOperators(unittest.TestCase):
    """Test crossover operators"""
    
    def setUp(self):
        self.parent1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.parent2 = np.array([6.0, 7.0, 8.0, 9.0, 10.0])
    
    def test_single_point_crossover(self):
        child1, child2 = GAOperators.crossover_single_point(self.parent1, self.parent2)
        
        self.assertEqual(len(child1), len(self.parent1))
        self.assertEqual(len(child2), len(self.parent2))
        # Children should be different from parents
        self.assertFalse(np.array_equal(child1, self.parent1) and 
                        np.array_equal(child2, self.parent2))
    
    def test_two_point_crossover(self):
        child1, child2 = GAOperators.crossover_two_point(self.parent1, self.parent2)
        
        self.assertEqual(len(child1), len(self.parent1))
        self.assertEqual(len(child2), len(self.parent2))
    
    def test_uniform_crossover(self):
        child1, child2 = GAOperators.crossover_uniform(self.parent1, self.parent2)
        
        self.assertEqual(len(child1), len(self.parent1))
        self.assertEqual(len(child2), len(self.parent2))
    
    def test_arithmetic_crossover(self):
        child1, child2 = GAOperators.crossover_arithmetic(self.parent1, self.parent2, weight=0.5)
        
        self.assertEqual(len(child1), len(self.parent1))
        self.assertEqual(len(child2), len(self.parent2))
        # Should be averages of parents
        expected = (self.parent1 + self.parent2) / 2
        np.testing.assert_array_almost_equal(child1, expected)
    
    def test_crossover_mismatched_length(self):
        short_parent = np.array([1.0, 2.0])
        with self.assertRaises(ValueError):
            GAOperators.crossover_single_point(short_parent, self.parent1)


class TestMutationOperators(unittest.TestCase):
    """Test mutation operators"""
    
    def setUp(self):
        self.individual = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
    
    def test_gaussian_mutation(self):
        mutated = GAOperators.mutation_gaussian(self.individual, mutation_rate=0.5, std=0.1)
        
        self.assertEqual(len(mutated), len(self.individual))
        # Should be different from original
        self.assertFalse(np.allclose(mutated, self.individual))
    
    def test_uniform_mutation(self):
        mutated = GAOperators.mutation_uniform(self.individual, mutation_rate=0.5)
        
        self.assertEqual(len(mutated), len(self.individual))
    
    def test_adaptive_mutation(self):
        mutated = GAOperators.mutation_adaptive(
            self.individual, 
            mutation_rate=0.5, 
            generation=50, 
            max_generations=100
        )
        
        self.assertEqual(len(mutated), len(self.individual))
    
    def test_mutation_rate_zero(self):
        mutated = GAOperators.mutation_gaussian(self.individual, mutation_rate=0.0)
        np.testing.assert_array_equal(mutated, self.individual)


class TestMetrics(unittest.TestCase):
    """Test metrics calculation"""
    
    def test_convergence_rate(self):
        fitness_history = [100.0, 90.0, 85.0, 84.0, 83.5]
        convergence = GAOperators.calculate_convergence_rate(fitness_history)
        
        self.assertGreaterEqual(convergence, 0.0)
        self.assertLessEqual(convergence, 1.0)
    
    def test_population_diversity(self):
        population = [
            np.array([0.0, 0.0]),
            np.array([1.0, 1.0]),
            np.array([0.5, 0.5])
        ]
        diversity = GAOperators.calculate_population_diversity(population)
        
        self.assertGreaterEqual(diversity, 0.0)
        self.assertLessEqual(diversity, 1.0)
    
    def test_ga_metrics_to_dict(self):
        metrics = GAMetrics(
            generation=5,
            best_fitness=100.0,
            worst_fitness=50.0,
            average_fitness=75.0,
            population_diversity=0.8,
            selections_performed=20,
            crossovers_performed=10,
            mutations_performed=5,
            convergence_rate=0.1
        )
        
        metrics_dict = metrics.to_dict()
        self.assertEqual(metrics_dict['generation'], 5)
        self.assertEqual(metrics_dict['best_fitness'], 100.0)


class TestRealValuedMapper(unittest.TestCase):
    """Test real-valued genotype-phenotype mapping"""
    
    def setUp(self):
        self.mapper = RealValuedMapper(min_val=-10.0, max_val=10.0)
    
    def test_mapping_range(self):
        genotype = np.array([0.0, 0.5, 1.0])
        phenotype = self.mapper.genotype_to_phenotype(genotype)
        
        expected = np.array([-10.0, 0.0, 10.0])
        np.testing.assert_array_almost_equal(phenotype, expected)
    
    def test_inverse_mapping(self):
        phenotype = np.array([0.0, 5.0, -5.0])
        genotype = self.mapper.phenotype_to_genotype(phenotype)
        phenotype_back = self.mapper.genotype_to_phenotype(genotype)
        
        np.testing.assert_array_almost_equal(phenotype, phenotype_back)
    
    def test_validate_valid_phenotype(self):
        phenotype = np.array([0.0, 5.0, -5.0])
        is_valid, error = self.mapper.validate_phenotype(phenotype)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_out_of_range_phenotype(self):
        phenotype = np.array([0.0, 15.0])  # 15 > max_val
        is_valid, error = self.mapper.validate_phenotype(phenotype)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_random_genotype_generation(self):
        genotype = self.mapper.create_random_genotype(5)
        
        self.assertEqual(len(genotype), 5)
        self.assertTrue(np.all(genotype >= 0))
        self.assertTrue(np.all(genotype <= 1))


class TestBinaryMapper(unittest.TestCase):
    """Test binary genotype-phenotype mapping"""
    
    def test_binary_to_decimal(self):
        mapper = BinaryMapper(interpretation="decimal")
        genotype = np.array([1.0, 0.0, 1.0, 0.0])  # 1010 in binary = 10 in decimal
        
        phenotype = mapper.genotype_to_phenotype(genotype)
        self.assertEqual(phenotype, 10)
    
    def test_bits_interpretation(self):
        mapper = BinaryMapper(interpretation="bits")
        genotype = np.array([1.0, 0.0, 1.0])
        
        phenotype = mapper.genotype_to_phenotype(genotype)
        np.testing.assert_array_equal(phenotype, genotype)
    
    def test_validate_binary_phenotype(self):
        mapper = BinaryMapper(interpretation="decimal")
        
        is_valid, error = mapper.validate_phenotype(5)
        self.assertTrue(is_valid)
        
        is_valid, error = mapper.validate_phenotype(-5)
        self.assertFalse(is_valid)


class TestGrammarMapper(unittest.TestCase):
    """Test grammar-based genotype-phenotype mapping"""
    
    def setUp(self):
        self.grammar = {
            '<expr>': [
                ['<number>'],
                ['<number>', '+', '<number>']
            ],
            '<number>': [
                ['1'],
                ['2'],
                ['3']
            ]
        }
        self.mapper = GrammarMapper(self.grammar, max_depth=5)
    
    def test_grammar_derivation(self):
        genotype = np.array([0.1, 0.5, 0.9])
        phenotype = self.mapper.genotype_to_phenotype(genotype)
        
        self.assertIsInstance(phenotype, str)
        self.assertGreater(len(phenotype), 0)
        self.assertFalse(phenotype.startswith("<error"))
    
    def test_validate_valid_phenotype(self):
        phenotype = "1+2"
        is_valid, error = self.mapper.validate_phenotype(phenotype)
        self.assertTrue(is_valid)
    
    def test_validate_error_phenotype(self):
        phenotype = "<error: test>"
        is_valid, error = self.mapper.validate_phenotype(phenotype)
        self.assertFalse(is_valid)


class TestGAEngine(unittest.TestCase):
    """Test complete GA engine"""
    
    def setUp(self):
        # Simple fitness function: minimize x^2
        self.fitness_func = lambda x: -float(np.sum(np.array(x)**2)) if x is not None else -np.inf
        self.config = GAConfig(
            population_size=10,
            generations=5,
            crossover_rate=0.8,
            mutation_rate=0.1
        )
        self.mapper = RealValuedMapper(min_val=-5.0, max_val=5.0)
    
    def test_engine_initialization(self):
        engine = GeneticAlgorithmEngine(self.config, self.fitness_func, self.mapper)
        
        self.assertEqual(len(engine.population), self.config.population_size)
        self.assertEqual(engine.generation, 0)
    
    def test_engine_run(self):
        engine = GeneticAlgorithmEngine(self.config, self.fitness_func, self.mapper)
        result = engine.run(use_async=False)
        
        self.assertIsInstance(result, GAResult)
        self.assertGreater(result.total_generations, 0)
        self.assertIsNotNone(result.best_phenotype)
        self.assertGreaterEqual(result.best_fitness, result.worst_fitness)
    
    def test_engine_convergence_detection(self):
        config = GAConfig(
            population_size=10,
            generations=100,
            early_stopping=True,
            early_stopping_generations=5,
            early_stopping_threshold=0.001
        )
        engine = GeneticAlgorithmEngine(config, self.fitness_func, self.mapper)
        result = engine.run()
        
        # Should potentially converge early
        self.assertLessEqual(result.total_generations, 100)
    
    def test_different_selection_methods(self):
        for method in [SelectionMethod.TOURNAMENT, SelectionMethod.ROULETTE_WHEEL, 
                      SelectionMethod.RANK_BASED]:
            config = GAConfig(
                population_size=10,
                generations=3,
                selection_method=method
            )
            engine = GeneticAlgorithmEngine(config, self.fitness_func, self.mapper)
            result = engine.run()
            
            self.assertIsNotNone(result.best_phenotype)
            self.assertEqual(result.total_generations, 3)
    
    def test_different_crossover_methods(self):
        for method in [CrossoverMethod.SINGLE_POINT, CrossoverMethod.TWO_POINT,
                      CrossoverMethod.UNIFORM, CrossoverMethod.ARITHMETIC]:
            config = GAConfig(
                population_size=10,
                generations=3,
                crossover_method=method
            )
            engine = GeneticAlgorithmEngine(config, self.fitness_func, self.mapper)
            result = engine.run()
            
            self.assertIsNotNone(result.best_phenotype)
    
    def test_different_mutation_methods(self):
        for method in [MutationMethod.GAUSSIAN, MutationMethod.UNIFORM,
                      MutationMethod.ADAPTIVE]:
            config = GAConfig(
                population_size=10,
                generations=3,
                mutation_method=method
            )
            engine = GeneticAlgorithmEngine(config, self.fitness_func, self.mapper)
            result = engine.run()
            
            self.assertIsNotNone(result.best_phenotype)


def run_all_tests():
    """Run all tests and print results"""
    print("\n" + "="*70)
    print("RUNNING COMPREHENSIVE GA UNIT TESTS")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGAConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionOperators))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossoverOperators))
    suite.addTests(loader.loadTestsFromTestCase(TestMutationOperators))
    suite.addTests(loader.loadTestsFromTestCase(TestMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestRealValuedMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestBinaryMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestGrammarMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestGAEngine))
    
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
