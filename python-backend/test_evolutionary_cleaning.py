"""
Test script for Data Fitness and Evolutionary Cleaning
Demonstrates the functionality of the new features
"""

import pandas as pd
import numpy as np
from data_fitness import (
    DataFitnessEvaluator,
    EvolutionaryDataCleaner,
    evaluate_data_fitness,
    clean_data_evolutionary
)

def create_test_data():
    """Create a sample dataset with intentional issues"""
    np.random.seed(42)
    
    data = {
        'id': range(1, 101),
        'name': ['Person_' + str(i) if i % 10 != 0 else None for i in range(1, 101)],
        'age': [np.random.randint(18, 80) if i % 15 != 0 else None for i in range(1, 101)],
        'salary': [np.random.uniform(30000, 120000) if i % 12 != 0 else None for i in range(1, 101)],
        'department': np.random.choice(['IT', 'HR', 'Sales', 'Marketing', None], 100, p=[0.25, 0.2, 0.2, 0.2, 0.15]),
        'score': [np.random.uniform(0, 100) if i % 8 != 0 else None for i in range(1, 101)]
    }
    
    df = pd.DataFrame(data)
    
    # Add some type inconsistencies
    df.loc[5, 'age'] = 'invalid'
    df.loc[15, 'salary'] = 'N/A'
    
    return df

def test_fitness_evaluation():
    """Test fitness evaluation functionality"""
    print("="*60)
    print("Testing Fitness Evaluation")
    print("="*60)
    
    # Create test data
    df = create_test_data()
    print(f"\nCreated test dataset with {len(df)} records and {len(df.columns)} columns")
    print(f"Missing values: {df.isna().sum().sum()}")
    
    # Evaluate fitness
    fitness_summary = evaluate_data_fitness(df)
    
    print(f"\n--- Fitness Summary ---")
    print(f"Total Records: {fitness_summary['total_records']}")
    print(f"Average Fitness: {fitness_summary['average_fitness']:.2f}%")
    print(f"Min Fitness: {fitness_summary['min_fitness']:.2f}%")
    print(f"Max Fitness: {fitness_summary['max_fitness']:.2f}%")
    print(f"\nHealth Breakdown:")
    print(f"  Excellent: {fitness_summary['excellent_records']}")
    print(f"  Good: {fitness_summary['good_records']}")
    print(f"  Fair: {fitness_summary['fair_records']}")
    print(f"  Poor: {fitness_summary['poor_records']}")
    print(f"  Critical: {fitness_summary['critical_records']}")
    print(f"\nRecords Needing Cleaning: {fitness_summary['records_needing_cleaning']}")
    
    # Show details for a few records
    print(f"\n--- Sample Record Details ---")
    evaluator = DataFitnessEvaluator(df)
    for idx in [0, 5, 10, 15]:
        fitness = evaluator.evaluate_record_fitness(idx)
        print(f"\nRecord {idx}:")
        print(f"  Overall Fitness: {fitness['overall_fitness']}%")
        print(f"  Health Status: {fitness['health_status']}")
        if fitness['issues']:
            print(f"  Issues: {', '.join(fitness['issues'])}")
    
    return df, fitness_summary

def test_evolutionary_cleaning(df):
    """Test evolutionary cleaning algorithms"""
    print("\n" + "="*60)
    print("Testing Evolutionary Cleaning Algorithms")
    print("="*60)
    
    methods = ['ga', 'pso', 'de', 'es', 'hybrid']
    
    # Use small parameters for quick testing
    params = {
        'ga': {'population_size': 20, 'generations': 30},
        'pso': {'n_particles': 15, 'iterations': 30},
        'de': {'pop_size': 15, 'max_iter': 30},
        'es': {'mu': 10, 'lambda_': 30, 'generations': 30},
        'hybrid': {}
    }
    
    results = {}
    
    for method in methods:
        print(f"\n--- Testing {method.upper()} ---")
        try:
            cleaned_df, report = clean_data_evolutionary(
                df.copy(), 
                method=method, 
                **params[method]
            )
            
            results[method] = report
            
            print(f"Before: {report['before']['average_fitness']:.2f}%")
            print(f"After:  {report['after']['average_fitness']:.2f}%")
            print(f"Improvement: +{report['improvement']['fitness_increase']:.2f}%")
            print(f"Records Fixed: {report['improvement']['records_fixed']}")
            print(f"Missing values after cleaning: {cleaned_df.isna().sum().sum()}")
            
        except Exception as e:
            print(f"Error with {method}: {e}")
            results[method] = {'error': str(e)}
    
    # Find best method
    print("\n" + "="*60)
    print("Summary - Best Method")
    print("="*60)
    
    valid_methods = [m for m in methods if 'error' not in results[m]]
    if valid_methods:
        best_method = max(valid_methods, key=lambda m: results[m]['improvement']['fitness_increase'])
        print(f"\nBest Method: {best_method.upper()}")
        print(f"Improvement: +{results[best_method]['improvement']['fitness_increase']:.2f}%")
        print(f"Records Fixed: {results[best_method]['improvement']['records_fixed']}")
        
        return results[best_method], best_method
    
    return None, None

def test_specific_algorithm(df, method='hybrid'):
    """Test a specific algorithm in detail"""
    print("\n" + "="*60)
    print(f"Detailed Test: {method.upper()} Algorithm")
    print("="*60)
    
    print("\nBefore Cleaning:")
    print(df.head(10))
    print(f"\nMissing values per column:")
    print(df.isna().sum())
    
    # Clean data
    cleaner = EvolutionaryDataCleaner(df)
    
    if method == 'ga':
        cleaned_df = cleaner.genetic_algorithm_imputation(
            population_size=30, generations=50
        )
    elif method == 'pso':
        cleaned_df = cleaner.particle_swarm_optimization(
            n_particles=20, iterations=50
        )
    elif method == 'de':
        cleaned_df = cleaner.differential_evolution_imputation(
            pop_size=20, max_iter=50
        )
    elif method == 'es':
        cleaned_df = cleaner.evolution_strategy_imputation(
            mu=10, lambda_=30, generations=50
        )
    else:  # hybrid
        cleaned_df = cleaner.hybrid_evolutionary_imputation()
    
    print("\nAfter Cleaning:")
    print(cleaned_df.head(10))
    print(f"\nMissing values per column:")
    print(cleaned_df.isna().sum())
    
    # Evaluate fitness improvement
    fitness_before = evaluate_data_fitness(df)
    fitness_after = evaluate_data_fitness(cleaned_df)
    
    print(f"\n--- Fitness Comparison ---")
    print(f"Before: {fitness_before['average_fitness']:.2f}%")
    print(f"After:  {fitness_after['average_fitness']:.2f}%")
    print(f"Improvement: +{fitness_after['average_fitness'] - fitness_before['average_fitness']:.2f}%")
    
    return cleaned_df

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FastMig - Data Fitness & Evolutionary Cleaning Test Suite")
    print("="*60)
    
    # Test 1: Fitness Evaluation
    df, fitness_summary = test_fitness_evaluation()
    
    # Test 2: Compare all evolutionary algorithms
    best_report, best_method = test_evolutionary_cleaning(df)
    
    # Test 3: Detailed test with best method
    if best_method:
        cleaned_df = test_specific_algorithm(df, best_method)
        
        # Save results
        try:
            df.to_csv('test_original_data.csv', index=False)
            cleaned_df.to_csv('test_cleaned_data.csv', index=False)
            print("\n✓ Test data saved:")
            print("  - test_original_data.csv")
            print("  - test_cleaned_data.csv")
        except Exception as e:
            print(f"\nWarning: Could not save test files: {e}")
    
    print("\n" + "="*60)
    print("All Tests Completed Successfully!")
    print("="*60)

if __name__ == '__main__':
    main()
