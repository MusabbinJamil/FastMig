"""
Interactive GA Testing CLI
===========================
Command-line interface for testing GA components interactively.

Usage:
    python ga_cli.py

Then follow the interactive prompts to:
- Test individual GA operators
- Run complete GA experiments
- Analyze results
- Test custom fitness functions
"""

import numpy as np
import sys
import json
from typing import List, Dict, Any, Optional, Callable
import traceback

from ga_operators import (
    GAOperators, GAConfig, SelectionMethod, CrossoverMethod,
    MutationMethod
)
from ga_genotype_phenotype import (
    RealValuedMapper, BinaryMapper, GrammarMapper
)
from ga_engine import GeneticAlgorithmEngine


class GAInteractiveCLI:
    """Interactive CLI for GA testing"""
    
    def __init__(self):
        self.current_config: Optional[GAConfig] = None
        self.current_mapper: Optional[Any] = None
        self.current_population: Optional[List[np.ndarray]] = None
        self.fitness_function: Optional[Callable] = None
        self.last_result: Optional[Any] = None
    
    def print_menu(self):
        """Print main menu"""
        print("\n" + "="*70)
        print("GA INTERACTIVE TESTING CLI")
        print("="*70)
        print("\n1. Test GA Operators")
        print("2. Configure GA Parameters")
        print("3. Create/Load Population")
        print("4. Select Fitness Function")
        print("5. Run GA Engine")
        print("6. View Results")
        print("7. Save Results")
        print("8. Run Unit Tests")
        print("9. Exit")
        print("-"*70)
    
    def test_operators_menu(self):
        """Menu for testing individual operators"""
        print("\n" + "-"*70)
        print("TEST GA OPERATORS")
        print("-"*70)
        print("\n1. Test Selection Methods")
        print("2. Test Crossover Methods")
        print("3. Test Mutation Methods")
        print("4. Test Metrics Calculation")
        print("5. Back to Main Menu")
        print("-"*70)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            self.test_selection()
        elif choice == "2":
            self.test_crossover()
        elif choice == "3":
            self.test_mutation()
        elif choice == "4":
            self.test_metrics()
        elif choice == "5":
            return
        else:
            print("Invalid choice")
    
    def test_selection(self):
        """Test selection operators"""
        print("\n" + "-"*70)
        print("TEST SELECTION OPERATORS")
        print("-"*70)
        
        # Create test population
        population = [np.random.randn(5) for _ in range(8)]
        fitness_scores = [float(np.sum(ind**2)) for ind in population]
        
        print(f"\nTest Population: {len(population)} individuals")
        print(f"Fitness Scores: {[f'{f:.2f}' for f in fitness_scores]}")
        
        # Tournament
        try:
            selected, stats = GAOperators.selection_tournament(
                population, fitness_scores, 4, tournament_size=2
            )
            print(f"\n✓ Tournament Selection: selected {len(selected)} parents")
            print(f"  Stats: {stats}")
        except Exception as e:
            print(f"✗ Tournament Selection failed: {e}")
        
        # Roulette Wheel
        try:
            selected, stats = GAOperators.selection_roulette_wheel(
                population, fitness_scores, 4
            )
            print(f"\n✓ Roulette Wheel Selection: selected {len(selected)} parents")
            print(f"  Stats: {stats}")
        except Exception as e:
            print(f"✗ Roulette Wheel Selection failed: {e}")
        
        # Rank-Based
        try:
            selected, stats = GAOperators.selection_rank_based(
                population, fitness_scores, 4
            )
            print(f"\n✓ Rank-Based Selection: selected {len(selected)} parents")
            print(f"  Stats: {stats}")
        except Exception as e:
            print(f"✗ Rank-Based Selection failed: {e}")
    
    def test_crossover(self):
        """Test crossover operators"""
        print("\n" + "-"*70)
        print("TEST CROSSOVER OPERATORS")
        print("-"*70)
        
        parent1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        parent2 = np.array([6.0, 7.0, 8.0, 9.0, 10.0])
        
        print(f"\nParent 1: {parent1}")
        print(f"Parent 2: {parent2}")
        
        # Single-point
        try:
            c1, c2 = GAOperators.crossover_single_point(parent1, parent2)
            print(f"\n✓ Single-Point Crossover:")
            print(f"  Child 1: {c1}")
            print(f"  Child 2: {c2}")
        except Exception as e:
            print(f"✗ Single-Point failed: {e}")
        
        # Two-point
        try:
            c1, c2 = GAOperators.crossover_two_point(parent1, parent2)
            print(f"\n✓ Two-Point Crossover:")
            print(f"  Child 1: {c1}")
            print(f"  Child 2: {c2}")
        except Exception as e:
            print(f"✗ Two-Point failed: {e}")
        
        # Uniform
        try:
            c1, c2 = GAOperators.crossover_uniform(parent1, parent2)
            print(f"\n✓ Uniform Crossover:")
            print(f"  Child 1: {c1}")
            print(f"  Child 2: {c2}")
        except Exception as e:
            print(f"✗ Uniform failed: {e}")
        
        # Arithmetic
        try:
            c1, c2 = GAOperators.crossover_arithmetic(parent1, parent2, weight=0.7)
            print(f"\n✓ Arithmetic Crossover (weight=0.7):")
            print(f"  Child 1: {c1}")
            print(f"  Child 2: {c2}")
        except Exception as e:
            print(f"✗ Arithmetic failed: {e}")
    
    def test_mutation(self):
        """Test mutation operators"""
        print("\n" + "-"*70)
        print("TEST MUTATION OPERATORS")
        print("-"*70)
        
        individual = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        
        print(f"\nOriginal: {individual}")
        
        # Gaussian
        try:
            mutated = GAOperators.mutation_gaussian(individual, mutation_rate=0.6, std=0.2)
            print(f"\n✓ Gaussian Mutation (rate=0.6, std=0.2):")
            print(f"  Mutated: {mutated}")
            print(f"  Changed genes: {np.sum(~np.isclose(individual, mutated))}")
        except Exception as e:
            print(f"✗ Gaussian failed: {e}")
        
        # Uniform
        try:
            mutated = GAOperators.mutation_uniform(individual, mutation_rate=0.6, min_val=0.0, max_val=1.0)
            print(f"\n✓ Uniform Mutation (rate=0.6):")
            print(f"  Mutated: {mutated}")
            print(f"  Changed genes: {np.sum(~np.isclose(individual, mutated))}")
        except Exception as e:
            print(f"✗ Uniform failed: {e}")
        
        # Adaptive
        try:
            mutated = GAOperators.mutation_adaptive(individual, mutation_rate=0.6, generation=30, max_generations=100)
            print(f"\n✓ Adaptive Mutation (gen=30/100):")
            print(f"  Mutated: {mutated}")
        except Exception as e:
            print(f"✗ Adaptive failed: {e}")
    
    def test_metrics(self):
        """Test metrics calculation"""
        print("\n" + "-"*70)
        print("TEST METRICS")
        print("-"*70)
        
        # Convergence rate
        fitness_history = [100.0, 90.0, 85.0, 83.0, 82.0, 81.8, 81.7]
        convergence = GAOperators.calculate_convergence_rate(fitness_history)
        print(f"\nFitness History: {fitness_history}")
        print(f"Convergence Rate: {convergence:.4f}")
        
        # Diversity
        population = [np.random.randn(5) for _ in range(5)]
        diversity = GAOperators.calculate_population_diversity(population)
        print(f"\nPopulation: {len(population)} individuals")
        print(f"Population Diversity: {diversity:.4f}")
    
    def configure_ga(self):
        """Configure GA parameters"""
        print("\n" + "-"*70)
        print("CONFIGURE GA PARAMETERS")
        print("-"*70)
        
        try:
            pop_size = int(input(f"\nPopulation size (default 50): ") or "50")
            generations = int(input(f"Generations (default 100): ") or "100")
            cross_rate = float(input(f"Crossover rate (default 0.8): ") or "0.8")
            mut_rate = float(input(f"Mutation rate (default 0.1): ") or "0.1")
            
            print("\nSelection Methods: tournament, roulette_wheel, rank_based")
            sel_method = input("Selection method (default tournament): ").strip() or "tournament"
            
            print("\nCrossover Methods: single_point, two_point, uniform, arithmetic")
            cross_method = input("Crossover method (default single_point): ").strip() or "single_point"
            
            print("\nMutation Methods: gaussian, uniform, adaptive")
            mut_method = input("Mutation method (default gaussian): ").strip() or "gaussian"
            
            early_stop = input("\nEnable early stopping? (y/n, default n): ").strip().lower() == "y"
            
            self.current_config = GAConfig(
                population_size=pop_size,
                generations=generations,
                crossover_rate=cross_rate,
                mutation_rate=mut_rate,
                selection_method=SelectionMethod[sel_method.upper()],
                crossover_method=CrossoverMethod[cross_method.upper()],
                mutation_method=MutationMethod[mut_method.upper()],
                early_stopping=early_stop
            )
            
            is_valid, errors = self.current_config.validate()
            if is_valid:
                print(f"\n✓ Config valid: {self.current_config}")
            else:
                print(f"✗ Config invalid: {errors}")
                self.current_config = None
        
        except Exception as e:
            print(f"✗ Error: {e}")
            traceback.print_exc()
    
    def create_population(self):
        """Create or load population"""
        print("\n" + "-"*70)
        print("CREATE/LOAD POPULATION")
        print("-"*70)
        
        try:
            print("\n1. Create random population")
            print("2. Load from file")
            choice = input("\nSelect option (1-2): ").strip()
            
            if choice == "1":
                mapper_type = input("\nMapper type (real_valued, binary, grammar): ").strip() or "real_valued"
                
                if mapper_type == "real_valued":
                    min_val = float(input("Min value (default -5): ") or "-5")
                    max_val = float(input("Max value (default 5): ") or "5")
                    self.current_mapper = RealValuedMapper(min_val, max_val)
                
                elif mapper_type == "binary":
                    interpretation = input("Interpretation (decimal, bits): ").strip() or "decimal"
                    self.current_mapper = BinaryMapper(interpretation)
                
                else:
                    print("Grammar mapper requires custom grammar definition")
                    return
                
                pop_size = int(input("Population size (default 20): ") or "20")
                genotype_length = int(input("Genotype length (default 10): ") or "10")
                
                self.current_population = [
                    self.current_mapper.create_random_genotype(genotype_length)
                    for _ in range(pop_size)
                ]
                
                print(f"\n✓ Created random population: {len(self.current_population)} individuals")
                print(f"  Mapper: {mapper_type}")
                print(f"  Genotype length: {genotype_length}")
            
            elif choice == "2":
                filename = input("Filename: ").strip()
                # TODO: Implement file loading
                print("File loading not implemented yet")
        
        except Exception as e:
            print(f"✗ Error: {e}")
            traceback.print_exc()
    
    def select_fitness_function(self):
        """Select or define fitness function"""
        print("\n" + "-"*70)
        print("SELECT FITNESS FUNCTION")
        print("-"*70)
        
        print("\nPredefined Functions:")
        print("1. Sphere (minimize sum of squares)")
        print("2. Rosenbrock")
        print("3. Rastrigin")
        print("4. Custom (enter code)")
        choice = input("\nSelect option (1-4): ").strip()
        
        try:
            if choice == "1":
                self.fitness_function = lambda x: -np.sum(np.array(x)**2) if x is not None else -np.inf
                print("✓ Fitness: Sphere function (minimize)")
            
            elif choice == "2":
                def rosenbrock(x):
                    x = np.array(x)
                    return -sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
                self.fitness_function = rosenbrock
                print("✓ Fitness: Rosenbrock function")
            
            elif choice == "3":
                def rastrigin(x):
                    x = np.array(x)
                    return -(10 * len(x) + sum(x**2 - 10 * np.cos(2 * np.pi * x)))
                self.fitness_function = rastrigin
                print("✓ Fitness: Rastrigin function")
            
            elif choice == "4":
                code = input("\nEnter fitness function (use 'x' as parameter):\n> ").strip()
                self.fitness_function = lambda x: eval(code, {"x": x, "np": np})
                print("✓ Fitness: Custom function")
            
            else:
                print("Invalid choice")
        
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def run_ga(self):
        """Run GA engine"""
        print("\n" + "-"*70)
        print("RUN GA ENGINE")
        print("-"*70)
        
        if self.current_config is None:
            print("✗ GA configuration not set")
            return
        
        if self.current_mapper is None:
            print("✗ Mapper not selected")
            return
        
        if self.fitness_function is None:
            print("✗ Fitness function not selected")
            return
        
        try:
            print(f"\nConfiguration: {self.current_config}")
            print(f"Mapper: {self.current_mapper.genotype_type.value}")
            print(f"\nRunning GA...")
            
            engine = GeneticAlgorithmEngine(
                self.current_config,
                self.fitness_function,
                self.current_mapper,
                self.current_population
            )
            
            use_async = input("Use async evaluation? (y/n, default n): ").strip().lower() == "y"
            
            self.last_result = engine.run(use_async=use_async)
            
            print(f"\n{self.last_result}")
            print(f"\n✓ GA completed successfully")
        
        except Exception as e:
            print(f"✗ Error: {e}")
            traceback.print_exc()
    
    def view_results(self):
        """View last GA results"""
        print("\n" + "-"*70)
        print("GA RESULTS")
        print("-"*70)
        
        if self.last_result is None:
            print("✗ No results available")
            return
        
        result = self.last_result
        print(f"\n{result}")
        
        print(f"\nBest Phenotype: {result.best_phenotype}")
        print(f"Best Fitness: {result.best_fitness:.6f}")
        print(f"Worst Fitness: {result.worst_fitness:.6f}")
        print(f"Average Fitness: {result.average_fitness:.6f}")
        
        if result.generation_metrics:
            print(f"\nLast 5 Generations:")
            for metric in result.generation_metrics[-5:]:
                if isinstance(metric, dict):
                    gen = metric.get('generation', '?')
                    best = metric.get('best_fitness', 0)
                    avg = metric.get('average_fitness', 0)
                    print(f"  Gen {gen}: best={best:.4f}, avg={avg:.4f}")
        
        print(f"\nErrors: {len(result.errors)}")
        if result.errors:
            for i, err in enumerate(result.errors[:3]):
                print(f"  {i+1}. {err}")
    
    def save_results(self):
        """Save results to file"""
        print("\n" + "-"*70)
        print("SAVE RESULTS")
        print("-"*70)
        
        if self.last_result is None:
            print("✗ No results to save")
            return
        
        try:
            filename = input("Filename (default ga_results.json): ").strip() or "ga_results.json"
            
            result_dict = self.last_result.to_dict()
            with open(filename, 'w') as f:
                json.dump(result_dict, f, indent=2)
            
            print(f"✓ Results saved to {filename}")
        
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def run_tests(self):
        """Run unit tests"""
        print("\n" + "-"*70)
        print("RUNNING UNIT TESTS")
        print("-"*70)
        
        import subprocess
        try:
            result = subprocess.run([sys.executable, "test_ga_system.py"], cwd=".")
            print(f"\nTests completed with exit code: {result.returncode}")
        except Exception as e:
            print(f"✗ Error running tests: {e}")
    
    def run(self):
        """Main CLI loop"""
        print("\n" + "="*70)
        print("Welcome to GA Interactive Testing CLI")
        print("="*70)
        
        while True:
            self.print_menu()
            choice = input("Select option (1-9): ").strip()
            
            if choice == "1":
                self.test_operators_menu()
            elif choice == "2":
                self.configure_ga()
            elif choice == "3":
                self.create_population()
            elif choice == "4":
                self.select_fitness_function()
            elif choice == "5":
                self.run_ga()
            elif choice == "6":
                self.view_results()
            elif choice == "7":
                self.save_results()
            elif choice == "8":
                self.run_tests()
            elif choice == "9":
                print("\nGoodbye!\n")
                break
            else:
                print("Invalid choice, please try again")


if __name__ == "__main__":
    cli = GAInteractiveCLI()
    cli.run()
