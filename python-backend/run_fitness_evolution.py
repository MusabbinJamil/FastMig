"""
Quick Start Guide for Data Fitness Evolution
=============================================

This script demonstrates the complete data cleaning pipeline with GA-based evolution.
Run with: python run_fitness_evolution.py
"""

import pandas as pd
import numpy as np
import logging
from ga_fitness_evolver import DataFitnessEvolverGA
from ga_operators import GAConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_demo_dataset():
    """Create a demo dataset with healthy and unhealthy records"""
    np.random.seed(42)
    
    # Healthy records (good data quality)
    healthy_data = {
        'customer_id': range(1, 501),
        'age': np.random.normal(35, 8, 500).astype(int).clip(18, 80),
        'income': np.random.normal(60000, 15000, 500).astype(int).clip(20000, 150000),
        'credit_score': np.random.normal(720, 40, 500).astype(int).clip(300, 850),
        'account_duration': np.random.normal(8, 3, 500).astype(int).clip(0, 40),
        'transaction_count': np.random.poisson(25, 500),
        'avg_transaction': np.random.normal(750, 200, 500).clip(100, 3000),
    }
    
    # Unhealthy records (problematic data)
    unhealthy_data = {
        'customer_id': range(501, 551),
        'age': [150, 5, 300, 1000, -50] + list(np.random.normal(35, 15, 45).astype(int).clip(10, 100)),
        'income': [-50000, 999999999, 0, -1000, 5000000] + list(np.random.normal(60000, 25000, 45).astype(int).clip(0, 500000)),
        'credit_score': [2000, -500, 3000, 0, -100] + list(np.random.normal(720, 80, 45).astype(int).clip(0, 900)),
        'account_duration': [-10, 5000, 0, -5, 999] + list(np.random.normal(8, 5, 45).astype(int).clip(0, 50)),
        'transaction_count': [1000000, 0, -50, -1000, 10000] + list(np.random.poisson(25, 45)),
        'avg_transaction': [9999999, -1000, 0, -500, 888888] + list(np.random.normal(750, 250, 45).clip(0, 10000)),
    }
    
    healthy_df = pd.DataFrame(healthy_data)
    unhealthy_df = pd.DataFrame(unhealthy_data)
    
    df = pd.concat([healthy_df, unhealthy_df], ignore_index=True)
    return df


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("DATA FITNESS EVOLUTION WITH GENETIC ALGORITHM")
    print("=" * 80)
    
    # Step 1: Create demo dataset
    print("\n[1/5] Creating demo dataset...")
    df = create_demo_dataset()
    print(f"[OK] Created dataset with {len(df)} records")
    print(f"  - Healthy records: ~500")
    print(f"  - Unhealthy records: ~50")
    
    # Step 2: Initialize evolver
    print("\n[2/5] Initializing fitness evolver...")
    evolver = DataFitnessEvolverGA(df, track_modifications=True)
    print("[OK] Evolver initialized")
    
    # Step 3: Analyze population
    print("\n[3/5] Analyzing population fitness...")
    analysis = evolver.analyze_population(fitness_threshold=50.0)
    print(f"[OK] Analysis complete:")
    print(f"  - Total records: {analysis['total_records']}")
    print(f"  - Healthy (>=50): {analysis['healthy_records']} ({analysis['healthy_percentage']:.1f}%)")
    print(f"  - Unhealthy (<50): {analysis['unhealthy_records']} ({analysis['unhealthy_percentage']:.1f}%)")
    print(f"  - Average fitness: {analysis['avg_fitness']:.2f}")
    
    # Step 4: Select populations
    print("\n[4/5] Selecting populations for evolution...")
    # Use all healthy records as templates, or a sample if you prefer
    config = evolver.select_populations(
        fitness_threshold=50.0,
        healthy_sample_size=None  # None = use all healthy records
    )
    print(f"[OK] Populations selected:")
    print(f"  - Unhealthy records to evolve: {config.unhealthy_count}")
    print(f"  - Healthy templates available: {config.healthy_count}")
    print(f"  - Target columns: {len(config.target_columns)}")
    
    # Step 5: Run evolution
    print("\n[5/5] Evolving unhealthy records toward health...")
    print("  (This may take 1-2 minutes depending on dataset size)")
    
    ga_config = GAConfig(
        population_size=20,
        generations=50,
        early_stopping=True,
        early_stopping_generations=5
    )
    
    evolved_df, results = evolver.evolve_unhealthy_records(
        config,
        ga_config=ga_config
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("EVOLUTION RESULTS")
    print("=" * 80)
    
    metrics = results.get('fitness_metrics', {})
    if not metrics:
        print("\n[WARNING] No unhealthy records were found or evolved.")
        print(f"Evolved: {results.get('evolved_records', 0)} records")
        return
    print(f"\nFitness Improvement:")
    print(f"  Initial average fitness: {metrics['avg_initial_fitness']:.2f}")
    print(f"  Evolved average fitness: {metrics['avg_evolved_fitness']:.2f}")
    print(f"  Average improvement: {metrics['improvement']:+.2f} points")
    print(f"\nTarget Achievement (>=95 health score):")
    print(f"  Records achieving target: {metrics['records_at_target']}/{config.unhealthy_count}")
    print(f"  Achievement rate: {metrics['target_achievement_rate']:.1f}%")
    
    # Save results
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    
    # Save evolved dataset
    evolved_csv = "evolved_data.csv"
    evolved_df.to_csv(evolved_csv, index=False)
    print(f"[OK] Saved evolved dataset to: {evolved_csv}")
    
    # Save detailed report
    report_file = "evolution_report.txt"
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("DATA FITNESS EVOLUTION REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("DATASET SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total records processed: {len(df)}\n")
        f.write(f"Unhealthy records evolved: {config.unhealthy_count}\n")
        f.write(f"Healthy templates used: {config.healthy_count}\n")
        f.write(f"Target columns: {len(config.target_columns)}\n\n")
        
        f.write("FITNESS METRICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Initial average fitness: {metrics['avg_initial_fitness']:.2f}/100\n")
        f.write(f"Evolved average fitness: {metrics['avg_evolved_fitness']:.2f}/100\n")
        f.write(f"Average improvement: {metrics['improvement']:+.2f} points\n")
        f.write(f"Best improvement: {metrics['max_improvement']:+.2f} points\n")
        f.write(f"Worst improvement: {metrics['min_improvement']:+.2f} points\n\n")
        
        f.write("TARGET ACHIEVEMENT\n")
        f.write("-" * 80 + "\n")
        f.write(f"Records at 95+ health: {metrics['records_at_target']}/{config.unhealthy_count}\n")
        f.write(f"Achievement rate: {metrics['target_achievement_rate']:.1f}%\n\n")
        
        f.write("TOP 10 IMPROVEMENTS\n")
        f.write("-" * 80 + "\n")
        sorted_results = sorted(
            results['detailed_results'],
            key=lambda x: x['improvement'],
            reverse=True
        )
        for i, result in enumerate(sorted_results[:10], 1):
            f.write(f"{i:2d}. {result['original_fitness']:6.2f} -> {result['evolved_fitness']:6.2f} "
                   f"(+{result['improvement']:6.2f}) - {result['generations']} generations\n")
    
    print(f"[OK] Saved detailed report to: {report_file}")
    
    print("\n" + "=" * 80)
    print("EVOLUTION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print(f"1. Review the evolved dataset ({evolved_csv})")
    print(f"2. Check the detailed report ({report_file})")
    print(f"3. Validate the improvements in your application")
    print(f"4. Deploy the cleaned data\n")


if __name__ == "__main__":
    main()
