"""
Complete Data Cleaning Pipeline - User Interface
================================================
End-to-end interface for analyzing, selecting populations,
and evolving unhealthy records toward 100% health.

Usage:
    python ga_data_cleaning_pipeline.py
"""

import pandas as pd
import numpy as np
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from data_fitness import DataFitnessEvaluator, evaluate_data_fitness
from ga_fitness_evolver import DataFitnessEvolverGA, PopulationConfig
from ga_operators import GAConfig, SelectionMethod

logger = logging.getLogger(__name__)


class DataCleaningPipeline:
    """Complete pipeline for data cleaning and fitness evolution"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.evolver: Optional[DataFitnessEvolverGA] = None
        self.analysis: Optional[Dict] = None
        self.config: Optional[PopulationConfig] = None
        self.evolved_df: Optional[pd.DataFrame] = None
    
    def print_banner(self, title: str):
        """Print formatted banner"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_section(self, title: str):
        """Print formatted section"""
        print("\n" + "-" * 80)
        print(f"  {title}")
        print("-" * 80)
    
    def load_data(self) -> bool:
        """Load CSV data file"""
        self.print_banner("LOAD DATA")
        
        while True:
            filename = input("\nEnter CSV filename (or 'demo' for demo data): ").strip()
            
            if filename.lower() == 'demo':
                print("\nGenerating demo dataset...")
                self.df = self._generate_demo_data()
                print(f"✓ Demo dataset created: {len(self.df)} records")
                return True
            
            filepath = Path(filename)
            if not filepath.exists():
                print(f"✗ File not found: {filename}")
                continue
            
            try:
                self.df = pd.read_csv(filepath)
                print(f"✓ Loaded: {filename} ({len(self.df)} records, {len(self.df.columns)} columns)")
                
                # Show first few rows
                print("\nFirst 3 rows:")
                print(self.df.head(3).to_string())
                return True
            
            except Exception as e:
                print(f"✗ Error loading file: {e}")
    
    def _generate_demo_data(self) -> pd.DataFrame:
        """Generate synthetic demo dataset"""
        np.random.seed(42)
        
        # Healthy records
        healthy = pd.DataFrame({
            'customer_id': range(1, 1001),
            'age': np.random.normal(35, 10, 1000).astype(int).clip(18, 80),
            'income': np.random.normal(50000, 15000, 1000).astype(int).clip(15000, 200000),
            'credit_score': np.random.normal(720, 50, 1000).astype(int).clip(300, 850),
            'account_duration': np.random.normal(5, 2, 1000).astype(int).clip(0, 50),
            'transaction_count': np.random.poisson(20, 1000),
            'avg_transaction': np.random.normal(500, 200, 1000).clip(10, 5000),
            'health_score': np.random.normal(90, 5, 1000).clip(85, 100)
        })
        
        # Unhealthy records (with anomalies)
        unhealthy = pd.DataFrame({
            'customer_id': range(1001, 1051),
            'age': [150, 5, 200] + [np.random.normal(35, 15) for _ in range(47)],
            'income': [-50000, 5000000, -1000] + [np.random.normal(50000, 30000) for _ in range(47)],
            'credit_score': [2000, -500, 0] + [np.random.normal(720, 100) for _ in range(47)],
            'account_duration': [-5, 1000, 0] + [np.random.normal(5, 5) for _ in range(47)],
            'transaction_count': [10000, 0, -50] + [np.random.poisson(20) for _ in range(47)],
            'avg_transaction': [100000, 0, -500] + [np.random.normal(500, 300) for _ in range(47)],
            'health_score': [30, 20, 15] + [np.random.normal(60, 15) for _ in range(47)]
        })
        
        df = pd.concat([healthy, unhealthy], ignore_index=True)
        return df
    
    def analyze_fitness(self) -> bool:
        """Analyze data fitness"""
        self.print_banner("STEP 1: ANALYZE FITNESS")
        
        if self.df is None:
            print("✗ No data loaded")
            return False
        
        try:
            self.evolver = DataFitnessEvolverGA(self.df, track_modifications=True)
            self.analysis = self.evolver.analyze_population(fitness_threshold=85.0)
            return True
        except Exception as e:
            print(f"✗ Error analyzing fitness: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def configure_populations(self) -> bool:
        """Configure healthy/unhealthy populations"""
        self.print_banner("STEP 2: SELECT POPULATIONS")
        
        if self.analysis is None:
            print("✗ Run analysis first")
            return False
        
        print(f"\nDataset Summary:")
        print(f"  Total records: {self.analysis['total_records']}")
        print(f"  Healthy records: {self.analysis['healthy_records']} ({self.analysis['healthy_percentage']:.1f}%)")
        print(f"  Unhealthy records: {self.analysis['unhealthy_records']} ({self.analysis['unhealthy_percentage']:.1f}%)")
        
        print(f"\nFitness Distribution:")
        for status, count in self.analysis['fitness_distribution'].items():
            pct = (count / self.analysis['total_records']) * 100
            print(f"  {status.capitalize():10} : {count:5d} ({pct:5.1f}%)")
        
        # Ask for healthy sample size
        self.print_section("Select Healthy Template Size")
        
        print(f"\nOptions:")
        print(f"  a) All healthy records ({self.analysis['healthy_records']})")
        print(f"  b) 50% of healthy ({self.analysis['healthy_records'] // 2})")
        print(f"  c) 25% of healthy ({self.analysis['healthy_records'] // 4})")
        print(f"  d) Fixed number (enter manually)")
        print(f"  e) Auto-select (10% of unhealthy, or all if < 100)")
        
        choice = input("\nSelect option (a-e, default=e): ").strip().lower() or 'e'
        
        if choice == 'a':
            healthy_size = None
        elif choice == 'b':
            healthy_size = self.analysis['healthy_records'] // 2
        elif choice == 'c':
            healthy_size = self.analysis['healthy_records'] // 4
        elif choice == 'd':
            try:
                healthy_size = int(input(f"Enter size (1-{self.analysis['healthy_records']}): "))
            except:
                healthy_size = None
        elif choice == 'e':
            # Auto: 10% of unhealthy, capped
            proposed = min(max(10, self.analysis['unhealthy_records'] // 10), self.analysis['healthy_records'])
            healthy_size = proposed
            print(f"→ Auto-selected: {healthy_size} healthy records")
        else:
            healthy_size = None
        
        try:
            self.config = self.evolver.select_populations(
                fitness_threshold=85.0,
                healthy_sample_size=healthy_size
            )
            return True
        except Exception as e:
            print(f"✗ Error selecting populations: {e}")
            return False
    
    def configure_ga(self) -> GAConfig:
        """Configure GA parameters"""
        self.print_banner("STEP 3: CONFIGURE GA")
        
        print(f"\nUnhealthy records to evolve: {self.config.unhealthy_count}")
        print(f"Healthy templates available: {self.config.healthy_count}")
        
        # Recommend population size
        recommended_pop = min(50, max(20, self.config.unhealthy_count // 2))
        
        print(f"\nGA Configuration:")
        print(f"  Recommended population size: {recommended_pop}")
        
        self.print_section("Options")
        print("\nPre-configured GA settings:")
        print("  a) Fast (50 gens, small population) - Quick testing")
        print("  b) Balanced (100 gens, medium population) - Recommended")
        print("  c) Thorough (200 gens, large population) - Best quality")
        print("  d) Custom (enter parameters manually)")
        
        choice = input("\nSelect option (a-d, default=b): ").strip().lower() or 'b'
        
        if choice == 'a':
            return GAConfig(
                population_size=20,
                generations=50,
                early_stopping=True,
                early_stopping_generations=5
            )
        elif choice == 'b':
            return GAConfig(
                population_size=recommended_pop,
                generations=100,
                early_stopping=True,
                early_stopping_generations=10
            )
        elif choice == 'c':
            return GAConfig(
                population_size=min(100, max(50, self.config.unhealthy_count)),
                generations=200,
                early_stopping=True,
                early_stopping_generations=15
            )
        elif choice == 'd':
            try:
                pop_size = int(input(f"Population size (default {recommended_pop}): ") or str(recommended_pop))
                generations = int(input("Generations (default 100): ") or "100")
                
                return GAConfig(
                    population_size=pop_size,
                    generations=generations,
                    early_stopping=True,
                    early_stopping_generations=10
                )
            except:
                return GAConfig()
        else:
            return GAConfig()
    
    def run_evolution(self, ga_config: GAConfig) -> bool:
        """Run the evolution process"""
        self.print_banner("STEP 4: RUN EVOLUTION")
        
        print(f"\nStarting evolution...")
        print(f"  Unhealthy records: {self.config.unhealthy_count}")
        print(f"  Healthy templates: {self.config.healthy_count}")
        print(f"  GA config: {ga_config}")
        
        try:
            self.evolved_df, results = self.evolver.evolve_unhealthy_records(
                self.config,
                ga_config=ga_config
            )
            
            print(f"\n✓ Evolution completed!")
            print(f"\nResults Summary:")
            print(f"  Initial avg fitness: {results['fitness_metrics']['avg_initial_fitness']:.2f}")
            print(f"  Evolved avg fitness: {results['fitness_metrics']['avg_evolved_fitness']:.2f}")
            print(f"  Average improvement: {results['fitness_metrics']['improvement']:+.2f}")
            print(f"  Records at target (100%): {results['fitness_metrics']['records_at_target']}/{self.config.unhealthy_count}")
            print(f"  Target achievement rate: {results['fitness_metrics']['target_achievement_rate']:.1f}%")
            
            # Store results for later
            self.results = results
            
            # Show detailed stats
            show_detail = input("\n\nShow detailed record-by-record results? (y/n, default=n): ").strip().lower()
            if show_detail == 'y':
                self.print_section("Detailed Results")
                for i, result in enumerate(results['detailed_results'][:10], 1):
                    print(f"\nRecord {i}:")
                    print(f"  Original fitness: {result['original_fitness']:.2f}")
                    print(f"  Evolved fitness: {result['evolved_fitness']:.2f}")
                    print(f"  Improvement: {result['improvement']:+.2f}")
                    print(f"  Generations: {result['generations']}")
                if len(results['detailed_results']) > 10:
                    print(f"\n... and {len(results['detailed_results']) - 10} more records")
            
            return True
        
        except Exception as e:
            print(f"✗ Error during evolution: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_results(self) -> bool:
        """Save evolved data"""
        self.print_banner("STEP 5: SAVE RESULTS")
        
        if self.evolved_df is None:
            print("✗ No evolved data to save")
            return False
        
        save_evolved = input("Save evolved dataset? (y/n, default=y): ").strip().lower() or 'y'
        
        if save_evolved == 'y':
            filename = input("Evolved data filename (default: evolved_data.csv): ").strip() or "evolved_data.csv"
            try:
                self.evolved_df.to_csv(filename, index=False)
                print(f"✓ Saved evolved data to: {filename}")
            except Exception as e:
                print(f"✗ Error saving: {e}")
                return False
        
        save_report = input("Save detailed report? (y/n, default=y): ").strip().lower() or 'y'
        
        if save_report == 'y':
            report_file = input("Report filename (default: evolution_report.txt): ").strip() or "evolution_report.txt"
            try:
                with open(report_file, 'w') as f:
                    f.write("=" * 80 + "\n")
                    f.write("DATA FITNESS EVOLUTION REPORT\n")
                    f.write("=" * 80 + "\n\n")
                    
                    f.write("EVOLUTION CONFIGURATION\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Unhealthy records evolved: {self.results['evolved_records']}\n")
                    f.write(f"Healthy templates used: {self.results['evolution_configs']['healthy_count']}\n")
                    f.write(f"Target columns: {', '.join(self.results['evolution_configs']['target_columns'][:5])}")
                    if len(self.results['evolution_configs']['target_columns']) > 5:
                        f.write(f" ... and {len(self.results['evolution_configs']['target_columns']) - 5} more\n\n")
                    else:
                        f.write("\n\n")
                    
                    f.write("FITNESS METRICS\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Initial average fitness: {self.results['fitness_metrics']['avg_initial_fitness']:.2f}\n")
                    f.write(f"Evolved average fitness: {self.results['fitness_metrics']['avg_evolved_fitness']:.2f}\n")
                    f.write(f"Average improvement: {self.results['fitness_metrics']['improvement']:+.2f}\n")
                    f.write(f"Records achieving target (100%): {self.results['fitness_metrics']['records_at_target']}\n")
                    f.write(f"Target achievement rate: {self.results['fitness_metrics']['target_achievement_rate']:.1f}%\n\n")
                    
                    f.write("TOP 10 IMPROVEMENTS\n")
                    f.write("-" * 80 + "\n")
                    sorted_results = sorted(
                        self.results['detailed_results'],
                        key=lambda x: x['improvement'],
                        reverse=True
                    )
                    for i, result in enumerate(sorted_results[:10], 1):
                        f.write(f"{i}. Original fitness: {result['original_fitness']:.2f} "
                               f"→ {result['evolved_fitness']:.2f} "
                               f"(+{result['improvement']:.2f})\n")
                
                print(f"✓ Saved report to: {report_file}")
            except Exception as e:
                print(f"✗ Error saving report: {e}")
                return False
        
        return True
    
    def run(self):
        """Run complete pipeline"""
        self.print_banner("DATA FITNESS EVOLUTION PIPELINE")
        
        steps = [
            ("Load Data", self.load_data),
            ("Analyze Fitness", self.analyze_fitness),
            ("Select Populations", self.configure_populations),
        ]
        
        # Execute initial steps
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n✗ Pipeline stopped at: {step_name}")
                return
        
        # Configure GA and run evolution
        ga_config = self.configure_ga()
        if not self.run_evolution(ga_config):
            print("\n✗ Pipeline stopped at: Run Evolution")
            return
        
        # Save results
        self.save_results()
        
        self.print_banner("PIPELINE COMPLETE")
        print("\n✓ Data cleaning and evolution completed successfully!")
        print("\nNext steps:")
        print("  - Review the evolved dataset")
        print("  - Validate the improvements")
        print("  - Integrate into your data pipeline")
        print()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    pipeline = DataCleaningPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
