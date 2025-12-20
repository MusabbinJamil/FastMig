FASTMIG GA SYSTEM - QUICK COMMANDS REFERENCE
============================================

TESTING
-------

Run all unit tests:
  cd python-backend
  python test_ga_system.py
  
Expected: 37/37 tests passing in ~0.25 seconds

Test specific components:
  python -m pytest test_ga_system.py -v

DEMONSTRATIONS
--------------

See GA optimization examples:
  python ga_demo.py
  
Features demonstrated:
  - Sphere function optimization
  - Constrained optimization
  - Rastrigin function
  - Convergence tracking

Interactive GA testing:
  python ga_cli.py
  
Menu options:
  1. Test selection operators
  2. Test crossover operators
  3. Test mutation operators
  4. Test mappers
  5. Run complete GA

PRODUCTION USAGE
----------------

Method 1: Interactive Pipeline (Recommended for Users)
  python ga_data_cleaning_pipeline.py
  
  Features:
  - Load CSV or demo data
  - Analyze fitness distribution
  - Select populations
  - Configure GA
  - View results
  - Export to CSV

Method 2: Quick Demo
  python run_fitness_evolution.py
  
  Demonstrates:
  - Complete workflow
  - Results reporting
  - CSV export
  - Takes ~1-2 minutes

Method 3: Python Code
  >>> from ga_fitness_evolver import DataFitnessEvolverGA
  >>> from ga_operators import GAConfig
  >>> 
  >>> evolver = DataFitnessEvolverGA(your_dataframe)
  >>> analysis = evolver.analyze_population(fitness_threshold=85.0)
  >>> config = evolver.select_populations(healthy_sample_size=1000)
  >>> evolved_df, results = evolver.evolve_unhealthy_records(config)

CODE EXAMPLES
-------------

Copy-paste ready examples:
  See GA_EXAMPLES.py for:
  - Simple sphere optimization
  - Constrained optimization
  - Genetic algorithm configuration
  - Mapper usage
  - Complete workflows

Quick Python Example:
  
  import pandas as pd
  from ga_fitness_evolver import evolve_records
  from ga_operators import GAConfig
  
  # Load your data
  df = pd.read_csv('your_data.csv')
  
  # Quick evolution
  evolved_df, results = evolve_records(
      df,
      fitness_threshold=85.0,
      healthy_sample_size=1000,
      ga_config=GAConfig(population_size=30, generations=100)
  )
  
  # Save results
  evolved_df.to_csv('cleaned_data.csv', index=False)
  
  # View metrics
  print(f"Improvement: {results['fitness_metrics']['improvement']:.2f}")

DOCUMENTATION
--------------

System Architecture:
  cat GA_SYSTEM_README.md
  - Complete architecture overview
  - Design patterns explained
  - Operator descriptions
  - Performance notes

User Guide:
  cat GA_FITNESS_EVOLUTION_GUIDE.md
  - Step-by-step usage
  - Parameter explanations
  - Troubleshooting
  - API reference

Project Overview:
  cat README_GA_SYSTEM.md
  - Complete feature list
  - Integration guide
  - Deployment checklist

Quick Reference:
  cat QUICK_REFERENCE.md
  - Common commands
  - Parameter quick lookup
  - Common workflows

Completion Status:
  cat COMPLETION_SUMMARY.md
  - All tasks status
  - Deliverables list
  - Testing summary

DEVELOPMENT
-----------

Import modules:
  from ga_operators import GAConfig, SelectionMethod
  from ga_engine import GeneticAlgorithmEngine
  from ga_genotype_phenotype import RealValuedMapper
  from ga_fitness_evolver import DataFitnessEvolverGA

View module structure:
  python -c "import ga_operators; help(ga_operators.GAConfig)"
  python -c "import ga_engine; help(ga_engine.GeneticAlgorithmEngine)"

Test imports:
  python -c "from ga_operators import GAConfig; print('OK')"
  python -c "from ga_engine import GeneticAlgorithmEngine; print('OK')"
  python -c "from ga_fitness_evolver import DataFitnessEvolverGA; print('OK')"

FILE OPERATIONS
---------------

List all GA files:
  ls -la ga*.py test*.py GA*.py

Check file sizes:
  wc -l ga*.py

View GA module structure:
  grep "^class\|^def" ga_operators.py
  grep "^class\|^def" ga_engine.py
  grep "^class\|^def" ga_fitness_evolver.py

PERFORMANCE TESTING
-------------------

Benchmark GA speed:
  python -c "
  import time
  from ga_operators import GAConfig
  from ga_engine import GeneticAlgorithmEngine
  from ga_genotype_phenotype import RealValuedMapper
  
  mapper = RealValuedMapper()
  config = GAConfig(population_size=30, generations=100)
  engine = GeneticAlgorithmEngine(
      config, 
      lambda x: sum(x**2),  # Sphere function
      mapper
  )
  
  start = time.time()
  result = engine.run()
  elapsed = time.time() - start
  
  print(f'Time: {elapsed:.2f}s, Best fitness: {result.best_fitness:.4f}')
  "

TROUBLESHOOTING
---------------

"ModuleNotFoundError":
  Check that all files are in python-backend/
  All imports relative to current directory

"No module named 'pandas'":
  pip install pandas numpy scipy scikit-learn

"Tests failing":
  Check Python version (3.7+)
  Run: python test_ga_system.py -v

"Slow performance":
  Reduce population_size or generations
  Use smaller healthy_sample_size
  Enable early_stopping (default: True)

"Low fitness improvements":
  Check fitness_threshold value
  Increase GA generations
  Check data quality

DATABASE / DATA OPERATIONS
--------------------------

Convert Excel to CSV:
  python -c "
  import pandas as pd
  df = pd.read_excel('data.xlsx')
  df.to_csv('data.csv', index=False)
  "

Check data fitness:
  python -c "
  import pandas as pd
  from ga_fitness_evolver import DataFitnessEvolverGA
  
  df = pd.read_csv('your_data.csv')
  evolver = DataFitnessEvolverGA(df)
  analysis = evolver.analyze_population()
  
  print(f'Healthy: {analysis[\"healthy_records\"]}')
  print(f'Unhealthy: {analysis[\"unhealthy_records\"]}')
  print(f'Avg fitness: {analysis[\"avg_fitness\"]:.2f}')
  "

API/INTEGRATION
---------------

Check if module is importable:
  python -c "import ga_fitness_evolver; print('Ready')"

Get version info:
  python -c "
  import ga_operators
  import inspect
  print(inspect.getfile(ga_operators))
  "

List all classes:
  python -c "
  import ga_operators
  import inspect
  classes = [c for c in dir(ga_operators) if inspect.isclass(getattr(ga_operators, c))]
  for c in classes:
      print(c)
  "

BATCH OPERATIONS
----------------

Process multiple files:
  python -c "
  import pandas as pd
  from ga_fitness_evolver import evolve_records
  
  files = ['file1.csv', 'file2.csv', 'file3.csv']
  for f in files:
      df = pd.read_csv(f)
      evolved, results = evolve_records(df)
      evolved.to_csv(f'evolved_{f}', index=False)
      print(f'{f}: {results[\"fitness_metrics\"][\"improvement\"]:.2f}')
  "

MONITORING & LOGGING
--------------------

Enable debug logging:
  python -c "
  import logging
  logging.basicConfig(level=logging.DEBUG)
  from ga_fitness_evolver import DataFitnessEvolverGA
  # Now all debug output will show
  "

Track evolution progress:
  The pipeline automatically shows progress:
  'Evolved 10/50 records' every 10% completion

INSTALLATION & SETUP
--------------------

Install dependencies:
  pip install pandas numpy scipy scikit-learn

Verify installation:
  python test_ga_system.py

First run:
  python ga_data_cleaning_pipeline.py

ADVANCED USAGE
--------------

Custom fitness function:
  def my_fitness(phenotype):
      # Your custom logic here
      return score
  
  engine = GeneticAlgorithmEngine(config, my_fitness, mapper)

Custom GA config:
  config = GAConfig(
      population_size=50,
      generations=200,
      crossover_rate=0.8,
      mutation_rate=0.1,
      early_stopping=True,
      early_stopping_generations=20,
      selection_method=SelectionMethod.RANK_BASED
  )

Custom mapper:
  mapper = RealValuedMapper(min_val=0.0, max_val=100.0)

QUICK STATS
-----------

Files created: 14
Lines of code: 5,200+
Lines of docs: 1,500+
Unit tests: 37
Test pass rate: 100%
Execution time: 0.25 sec (tests)

SUMMARY
-------

Everything is ready to use. Start with:

  python ga_data_cleaning_pipeline.py

For detailed help, see documentation:
  GA_FITNESS_EVOLUTION_GUIDE.md
  GA_SYSTEM_README.md
  DELIVERABLE_SUMMARY.txt
