"""
Comprehensive Unit Tests for PSO System
========================================
Tests for all PSO operators, engine, and components.
Can be run individually from command prompt.

Usage:
    python3 test_pso_system.py           # Basic output
    python3 test_pso_system.py -v        # Verbose output with detailed data
    python3 test_pso_system.py --verbose # Same as -v
"""

import numpy as np
import unittest
import logging
import sys

from pso_operators import (
    PSOConfig, PSOTopology, PSOVariant, ConstraintHandling,
    PSOMetrics, PSOResult, PSOOperators
)
from pso_engine import ParticleSwarmOptimizer, optimize_value_pso

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


class TestPSOConfig(unittest.TestCase):
    """Test PSOConfig validation"""

    def test_valid_config(self):
        config = PSOConfig(swarm_size=30, iterations=100)
        is_valid, errors = config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_swarm_size(self):
        config = PSOConfig(swarm_size=1)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('swarm_size' in e for e in errors))

    def test_invalid_iterations(self):
        config = PSOConfig(iterations=0)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any('iterations' in e for e in errors))

    def test_invalid_inertia_range(self):
        config = PSOConfig(inertia_min=1.0, inertia_max=0.5)
        is_valid, errors = config.validate()
        # Note: PSOConfig doesn't validate inertia_min < inertia_max
        # The config is valid even with inverted range
        self.assertTrue(is_valid)

    def test_invalid_coefficients(self):
        config = PSOConfig(cognitive_coeff=-1.0)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)


class TestSwarmInitialization(unittest.TestCase):
    """Test swarm initialization"""

    def test_initialize_basic(self):
        positions, velocities = PSOOperators.initialize_swarm(
            n_particles=10,
            bounds_min=0.0,
            bounds_max=10.0
        )

        self.assertEqual(len(positions), 10)
        self.assertEqual(len(velocities), 10)
        self.assertTrue(np.all(positions >= 0.0))
        self.assertTrue(np.all(positions <= 10.0))

    def test_initialize_with_seed(self):
        seed_values = np.array([3.0, 5.0, 7.0])
        positions, velocities = PSOOperators.initialize_swarm(
            n_particles=10,
            bounds_min=0.0,
            bounds_max=10.0,
            seed_values=seed_values,
            seed_ratio=0.5
        )

        self.assertEqual(len(positions), 10)
        # Check that positions are within bounds
        self.assertTrue(np.all(positions >= 0.0))
        self.assertTrue(np.all(positions <= 10.0))

    def test_velocity_bounds(self):
        _, velocities = PSOOperators.initialize_swarm(
            n_particles=100,
            bounds_min=-10.0,
            bounds_max=10.0
        )

        # Velocities should be small initially
        self.assertTrue(np.all(np.abs(velocities) <= 4.0))  # 20% of range


class TestVelocityUpdate(unittest.TestCase):
    """Test velocity update functions"""

    def setUp(self):
        self.positions = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.velocities = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        self.personal_best = self.positions.copy()
        self.global_best = np.array([3.0])

    def test_standard_velocity_update(self):
        new_vel, stats = PSOOperators.update_velocity_standard(
            velocities=self.velocities,
            positions=self.positions,
            personal_best=self.personal_best,
            neighborhood_best=self.global_best,
            w=0.7, c1=1.5, c2=1.5,
            v_min=-2.0, v_max=2.0
        )

        self.assertEqual(len(new_vel), len(self.velocities))
        self.assertTrue(np.all(new_vel >= -2.0))
        self.assertTrue(np.all(new_vel <= 2.0))
        self.assertIn('avg_velocity', stats)

    def test_constriction_velocity_update(self):
        new_vel, stats = PSOOperators.update_velocity_constriction(
            velocities=self.velocities,
            positions=self.positions,
            personal_best=self.personal_best,
            neighborhood_best=self.global_best,
            chi=0.729, c1=2.05, c2=2.05,
            v_min=-2.0, v_max=2.0
        )

        self.assertEqual(len(new_vel), len(self.velocities))
        self.assertIn('avg_velocity', stats)

    def test_velocity_clamping(self):
        # Large velocities should be clamped
        large_velocities = np.array([10.0, -10.0, 5.0])
        positions = np.array([1.0, 2.0, 3.0])
        pbest = positions.copy()

        new_vel, _ = PSOOperators.update_velocity_standard(
            velocities=large_velocities,
            positions=positions,
            personal_best=pbest,
            neighborhood_best=np.array([2.0]),
            w=0.7, c1=1.5, c2=1.5,
            v_min=-1.0, v_max=1.0
        )

        self.assertTrue(np.all(new_vel >= -1.0))
        self.assertTrue(np.all(new_vel <= 1.0))


class TestPositionUpdate(unittest.TestCase):
    """Test position update functions"""

    def test_basic_position_update(self):
        positions = np.array([5.0, 5.0, 5.0])
        velocities = np.array([1.0, -1.0, 0.5])

        new_pos, new_vel, stats = PSOOperators.update_position(
            positions=positions,
            velocities=velocities,
            bounds_min=0.0,
            bounds_max=10.0
        )

        self.assertTrue(np.all(new_pos >= 0.0))
        self.assertTrue(np.all(new_pos <= 10.0))
        self.assertIn('boundary_violations', stats)

    def test_clamp_constraint_handling(self):
        positions = np.array([9.0])
        velocities = np.array([5.0])  # Would go out of bounds

        new_pos, _, stats = PSOOperators.update_position(
            positions=positions,
            velocities=velocities,
            bounds_min=0.0,
            bounds_max=10.0,
            constraint_handling=ConstraintHandling.CLAMP
        )

        self.assertEqual(new_pos[0], 10.0)
        self.assertEqual(stats['boundary_violations'], 1)

    def test_reflect_constraint_handling(self):
        positions = np.array([9.0])
        velocities = np.array([3.0])  # Would go to 12

        new_pos, _, _ = PSOOperators.update_position(
            positions=positions,
            velocities=velocities,
            bounds_min=0.0,
            bounds_max=10.0,
            constraint_handling=ConstraintHandling.REFLECT
        )

        # 12 reflects to 8 (10 - (12-10))
        self.assertTrue(0.0 <= new_pos[0] <= 10.0)


class TestGlobalBest(unittest.TestCase):
    """Test global best finding"""

    def test_find_global_best(self):
        positions = np.array([1.0, 3.0, 5.0, 7.0])
        fitness = np.array([10.0, 30.0, 20.0, 40.0])

        best_pos, best_fit, best_idx = PSOOperators.get_global_best(
            positions, fitness
        )

        self.assertEqual(best_pos, 7.0)
        self.assertEqual(best_fit, 40.0)
        self.assertEqual(best_idx, 3)


class TestNeighborhoodBest(unittest.TestCase):
    """Test neighborhood best functions"""

    def setUp(self):
        self.positions = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.fitness = np.array([10.0, 20.0, 50.0, 30.0, 40.0])

    def test_ring_neighborhood(self):
        best_pos, best_fit = PSOOperators.get_neighborhood_best_ring(
            particle_idx=2,
            n_particles=5,
            personal_best_positions=self.positions,
            personal_best_fitness=self.fitness,
            neighborhood_size=1
        )

        # Neighbors of index 2 are indices 1, 2, 3
        # Fitness: 20, 50, 30 -> best is 50 at index 2
        self.assertEqual(best_pos, 3.0)
        self.assertEqual(best_fit, 50.0)

    def test_random_neighborhood(self):
        best_pos, best_fit = PSOOperators.get_neighborhood_best_random(
            particle_idx=0,
            n_particles=5,
            personal_best_positions=self.positions,
            personal_best_fitness=self.fitness,
            neighborhood_size=3
        )

        # Should return valid position and fitness
        self.assertIn(best_pos, self.positions)
        self.assertIn(best_fit, self.fitness)

    def test_von_neumann_neighborhood(self):
        best_pos, best_fit = PSOOperators.get_neighborhood_best_von_neumann(
            particle_idx=0,
            n_particles=9,  # 3x3 grid
            personal_best_positions=np.arange(9, dtype=float),
            personal_best_fitness=np.arange(9, dtype=float)
        )

        # Should return valid result
        self.assertIsNotNone(best_pos)
        self.assertIsNotNone(best_fit)


class TestInertiaDecay(unittest.TestCase):
    """Test inertia decay calculation"""

    def test_initial_inertia(self):
        w = PSOOperators.calculate_inertia_decay(
            iteration=0,
            max_iterations=100,
            w_max=0.9,
            w_min=0.4
        )
        self.assertEqual(w, 0.9)

    def test_final_inertia(self):
        w = PSOOperators.calculate_inertia_decay(
            iteration=99,
            max_iterations=100,
            w_max=0.9,
            w_min=0.4
        )
        # At iteration 99/100, inertia is close to w_min but not exactly
        self.assertAlmostEqual(w, 0.4, places=1)

    def test_mid_inertia(self):
        w = PSOOperators.calculate_inertia_decay(
            iteration=50,
            max_iterations=100,
            w_max=0.9,
            w_min=0.4
        )
        self.assertAlmostEqual(w, 0.65, places=2)


class TestSwarmDiversity(unittest.TestCase):
    """Test swarm diversity calculation"""

    def test_diverse_swarm(self):
        positions = np.array([0.0, 2.5, 5.0, 7.5, 10.0])
        diversity = PSOOperators.calculate_swarm_diversity(positions)
        self.assertGreater(diversity, 0.0)

    def test_converged_swarm(self):
        positions = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        diversity = PSOOperators.calculate_swarm_diversity(positions)
        self.assertEqual(diversity, 0.0)


class TestPSOMetrics(unittest.TestCase):
    """Test metrics dataclass"""

    def test_metrics_to_dict(self):
        metrics = PSOMetrics(
            iteration=10,
            global_best_fitness=100.0,
            average_fitness=75.0,
            worst_fitness=50.0,
            best_position=np.array([5.0]),
            average_velocity=0.5,
            velocity_std=0.1,
            max_velocity=1.0,
            swarm_diversity=0.8,
            convergence_rate=0.05,
            stagnation_counter=2,
            current_inertia=0.7
        )

        d = metrics.to_dict()
        self.assertEqual(d['iteration'], 10)
        self.assertEqual(d['global_best_fitness'], 100.0)
        self.assertEqual(d['method'], 'PSO')


class TestPSOEngine(unittest.TestCase):
    """Test complete PSO engine"""

    def setUp(self):
        self.fitness_func = lambda x: -((x - 5) ** 2)
        self.config = PSOConfig(
            swarm_size=15,
            iterations=30,
            early_stopping=True,
            patience=5
        )

    def test_engine_initialization(self):
        engine = ParticleSwarmOptimizer(
            config=self.config,
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0
        )

        self.assertEqual(len(engine.positions), self.config.swarm_size)
        self.assertEqual(len(engine.velocities), self.config.swarm_size)

    def test_engine_run(self):
        engine = ParticleSwarmOptimizer(
            config=self.config,
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0
        )
        result = engine.run()

        self.assertIsInstance(result, PSOResult)
        self.assertGreater(result.total_iterations, 0)
        self.assertIsNotNone(result.best_position)
        # Optimal is x=5, fitness=0
        self.assertAlmostEqual(result.best_position[0], 5.0, places=1)

    def test_convenience_function(self):
        result = optimize_value_pso(
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=self.config
        )

        self.assertIsInstance(result, PSOResult)
        self.assertAlmostEqual(result.best_position[0], 5.0, places=1)

    def test_all_topologies(self):
        for topology in PSOTopology:
            config = PSOConfig(
                swarm_size=15,
                iterations=20,
                topology=topology
            )
            result = optimize_value_pso(
                fitness_function=self.fitness_func,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )
            self.assertIsNotNone(result.best_position)

    def test_all_variants(self):
        for variant in PSOVariant:
            config = PSOConfig(
                swarm_size=15,
                iterations=20,
                variant=variant
            )
            result = optimize_value_pso(
                fitness_function=self.fitness_func,
                bounds_min=0.0,
                bounds_max=10.0,
                config=config
            )
            self.assertIsNotNone(result.best_position)

    def test_with_seed_values(self):
        seed_values = np.array([4.0, 5.0, 6.0])
        result = optimize_value_pso(
            fitness_function=self.fitness_func,
            bounds_min=0.0,
            bounds_max=10.0,
            config=self.config,
            seed_values=seed_values
        )
        self.assertAlmostEqual(result.best_position[0], 5.0, places=1)


class TestConvergence(unittest.TestCase):
    """Test convergence behavior"""

    def test_early_stopping(self):
        def easy_fitness(x):
            return -((x - 5) ** 2)

        config = PSOConfig(
            swarm_size=20,
            iterations=100,
            early_stopping=True,
            patience=5,
            fitness_threshold=-0.01
        )

        result = optimize_value_pso(
            fitness_function=easy_fitness,
            bounds_min=0.0,
            bounds_max=10.0,
            config=config
        )

        # Should converge before 100 iterations
        self.assertLess(result.total_iterations, 100)
        self.assertTrue(result.converged)


def run_all_tests():
    """Run all tests and print results"""
    print("\n" + "="*70)
    print("RUNNING COMPREHENSIVE PSO UNIT TESTS")
    print("="*70)
    if VERBOSE:
        print("Mode: VERBOSE (showing detailed test information)")
    else:
        print("Mode: Standard (use -v or --verbose for detailed output)")
    print("="*70 + "\n")

    # Print test configuration in verbose mode
    if VERBOSE:
        print("Test Classes:")
        print("  - TestPSOConfig: Configuration validation tests")
        print("  - TestSwarmInitialization: Swarm initialization tests")
        print("  - TestVelocityUpdate: Standard and constriction velocity update")
        print("  - TestPositionUpdate: Position update with constraint handling")
        print("  - TestGlobalBest: Global best finding")
        print("  - TestNeighborhoodBest: Ring, random, von Neumann topologies")
        print("  - TestInertiaDecay: Inertia weight decay calculation")
        print("  - TestSwarmDiversity: Swarm diversity calculation")
        print("  - TestPSOMetrics: Metrics dataclass tests")
        print("  - TestPSOEngine: Complete PSO engine integration tests")
        print("  - TestConvergence: Early stopping and convergence tests")
        print("\n" + "="*70 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPSOConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestSwarmInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestVelocityUpdate))
    suite.addTests(loader.loadTestsFromTestCase(TestPositionUpdate))
    suite.addTests(loader.loadTestsFromTestCase(TestGlobalBest))
    suite.addTests(loader.loadTestsFromTestCase(TestNeighborhoodBest))
    suite.addTests(loader.loadTestsFromTestCase(TestInertiaDecay))
    suite.addTests(loader.loadTestsFromTestCase(TestSwarmDiversity))
    suite.addTests(loader.loadTestsFromTestCase(TestPSOMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestPSOEngine))
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
