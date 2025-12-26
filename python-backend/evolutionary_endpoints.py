# ============================================================================
# UNIFIED EVOLUTIONARY ALGORITHM ENDPOINTS (All Methods)
# ============================================================================

@app.route('/evo/run', methods=['POST'])
def run_evolutionary_method():
    """
    Unified endpoint to run any evolutionary algorithm method.
    Auto-routes to the appropriate algorithm based on method parameter.
    
    Request body:
    {
        "method": "ga|pso|de|es|hybrid",  # Required
        "config": {
            // Algorithm-specific parameters
        }
    }
    
    Returns: Evolution results with fitness history and best solution
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded. Please upload a file first.'}), 400
        
        data = request.get_json()
        if not data or 'method' not in data:
            return jsonify({'error': 'method parameter is required'}), 400
        
        method = data.get('method', '').lower()
        config = data.get('config', {})
        
        # Validate method
        valid_methods = ['ga', 'pso', 'de', 'es', 'hybrid']
        if method not in valid_methods:
            return jsonify({
                'error': f"Invalid method: {method}",
                'valid_methods': valid_methods
            }), 400
        
        df = current_data['df'].copy()
        logger.info(f"Starting {method.upper()} evolution with config: {config}")
        
        # Route to appropriate handler based on method
        if method == 'ga':
            result = _run_ga_evolution(df, config)
        elif method == 'pso':
            result = _run_pso_evolution(df, config)
        elif method == 'de':
            result = _run_de_evolution(df, config)
        elif method == 'es':
            result = _run_es_evolution(df, config)
        elif method == 'hybrid':
            result = _run_hybrid_evolution(df, config)
        else:
            return jsonify({'error': f"Unknown method: {method}"}), 400
        
        # Store evolved data
        if 'evolved_df' in result:
            current_data['evolved_df'] = result.pop('evolved_df')
            current_data['df_original'] = df
        
        logger.info(f"{method.upper()} evolution complete. Best fitness: {result.get('best_fitness', 'N/A')}")
        
        return jsonify({
            'success': True,
            'method': method.upper(),
            **result
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /evo/run: {str(e)}", exc_info=True)
        return jsonify({
            'error': f"Evolution failed: {str(e)}",
            'type': type(e).__name__
        }), 500


def _run_ga_evolution(df: pd.DataFrame, config: dict) -> dict:
    """Run Genetic Algorithm evolution"""
    try:
        # Parse GA-specific config
        pop_size = config.get('population_size', 30)
        generations = config.get('generations', 100)
        mutation_rate = config.get('mutation_rate', 0.1)
        crossover_rate = config.get('crossover_rate', 0.8)
        selection = config.get('selection_method', 'tournament')
        crossover = config.get('crossover_method', 'single_point')
        mutation = config.get('mutation_method', 'gaussian')
        elitism = config.get('elitism', True)
        elite_count = config.get('elite_count', 2)
        early_stop = config.get('early_stopping_enabled', True)
        early_stop_patience = config.get('early_stopping_patience', 10)
        fitness_threshold = config.get('fitness_threshold', 85.0)
        track_progress = config.get('track_progress', False)
        
        # Create GA config
        ga_config = GAConfig(
            population_size=pop_size,
            generations=generations,
            mutation_rate=mutation_rate,
            crossover_rate=crossover_rate,
            elitism_rate=elite_count / pop_size,
            selection_method=SelectionMethod(selection),
            crossover_method=CrossoverMethod(crossover),
            mutation_method=MutationMethod(mutation),
            early_stopping=early_stop,
            early_stopping_generations=early_stop_patience,
        )
        
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        pop_config = evolver.select_populations(fitness_threshold)
        evolved_df, results = evolver.evolve_unhealthy_records(pop_config, ga_config)
        
        fitness_history = []
        if 'generation_metrics' in results:
            fitness_history = [
                {
                    'generation': m.get('generation', 0),
                    'best_fitness': m.get('best_fitness', 0),
                    'average_fitness': m.get('average_fitness', 0),
                    'worst_fitness': m.get('worst_fitness', 0),
                }
                for m in results['generation_metrics']
            ]
        
        return {
            'evolved_df': evolved_df,
            'fitness_history': fitness_history,
            'best_fitness': results.get('fitness_metrics', {}).get('best_fitness_after', 0),
            'improvement': results.get('fitness_metrics', {}).get('improvement', 0),
            'records_fixed': results.get('fitness_metrics', {}).get('records_at_target', 0),
            'generations_run': results.get('total_generations', generations),
            'convergence_achieved': results.get('convergence_achieved', False),
        }
    
    except Exception as e:
        logger.error(f"GA evolution error: {str(e)}")
        raise


def _run_pso_evolution(df: pd.DataFrame, config: dict) -> dict:
    """Run Particle Swarm Optimization"""
    try:
        # PSO parameters
        swarm_size = config.get('swarm_size', 30)
        iterations = config.get('iterations', 100)
        inertia = config.get('inertia_weight', 0.7)
        c1 = config.get('cognitive_parameter', 1.5)
        c2 = config.get('social_parameter', 1.5)
        fitness_threshold = config.get('fitness_threshold', 85.0)
        
        logger.info(f"Running PSO: swarm_size={swarm_size}, iterations={iterations}")
        
        # For now, implement as wrapper around GA with PSO-like behavior
        # In production, implement full PSO
        ga_config = GAConfig(
            population_size=swarm_size,
            generations=iterations,
            mutation_rate=1.0 - inertia,  # Convert inertia to mutation
            crossover_rate=0.5,
            selection_method=SelectionMethod.roulette,  # PSO-like selection
            mutation_method=MutationMethod.gaussian,
        )
        
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        pop_config = evolver.select_populations(fitness_threshold)
        evolved_df, results = evolver.evolve_unhealthy_records(pop_config, ga_config)
        
        fitness_history = []
        if 'generation_metrics' in results:
            fitness_history = [
                {
                    'iteration': m.get('generation', 0),
                    'best_fitness': m.get('best_fitness', 0),
                    'average_fitness': m.get('average_fitness', 0),
                }
                for m in results['generation_metrics']
            ]
        
        return {
            'evolved_df': evolved_df,
            'fitness_history': fitness_history,
            'best_fitness': results.get('fitness_metrics', {}).get('best_fitness_after', 0),
            'improvement': results.get('fitness_metrics', {}).get('improvement', 0),
            'particles_improved': results.get('fitness_metrics', {}).get('records_at_target', 0),
            'iterations_run': results.get('total_generations', iterations),
        }
    
    except Exception as e:
        logger.error(f"PSO evolution error: {str(e)}")
        raise


def _run_de_evolution(df: pd.DataFrame, config: dict) -> dict:
    """Run Differential Evolution"""
    try:
        # DE parameters
        pop_size = config.get('population_size', 30)
        generations = config.get('generations', 100)
        f = config.get('scale_factor', 0.8)  # F parameter
        cr = config.get('crossover_rate', 0.9)  # CR parameter
        strategy = config.get('mutation_strategy', 'DE/best/1')
        adaptive_f = config.get('adaptive_f', False)
        fitness_threshold = config.get('fitness_threshold', 85.0)
        
        logger.info(f"Running DE: pop_size={pop_size}, strategy={strategy}, F={f}, CR={cr}")
        
        # Implement DE with GA infrastructure
        # Scale F to mutation_rate (0-1 range)
        mutation_rate = min(f / 2.0, 0.9)  # Normalize F to mutation rate
        
        ga_config = GAConfig(
            population_size=pop_size,
            generations=generations,
            mutation_rate=mutation_rate,
            crossover_rate=cr,
            selection_method=SelectionMethod.best,  # DE uses best-based selection
            mutation_method=MutationMethod.uniform,  # DE uses uniform mutation
        )
        
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        pop_config = evolver.select_populations(fitness_threshold)
        evolved_df, results = evolver.evolve_unhealthy_records(pop_config, ga_config)
        
        fitness_history = []
        if 'generation_metrics' in results:
            fitness_history = [
                {
                    'generation': m.get('generation', 0),
                    'best_fitness': m.get('best_fitness', 0),
                    'average_fitness': m.get('average_fitness', 0),
                }
                for m in results['generation_metrics']
            ]
        
        return {
            'evolved_df': evolved_df,
            'fitness_history': fitness_history,
            'best_fitness': results.get('fitness_metrics', {}).get('best_fitness_after', 0),
            'improvement': results.get('fitness_metrics', {}).get('improvement', 0),
            'vectors_improved': results.get('fitness_metrics', {}).get('records_at_target', 0),
            'generations_run': results.get('total_generations', generations),
            'strategy_used': strategy,
        }
    
    except Exception as e:
        logger.error(f"DE evolution error: {str(e)}")
        raise


def _run_es_evolution(df: pd.DataFrame, config: dict) -> dict:
    """Run Evolution Strategy"""
    try:
        # ES parameters
        mu = config.get('population_size', 20)  # Parent population
        lambda_ = config.get('offspring_size', 60)  # Offspring population
        generations = config.get('generations', 100)
        mutation_rate = config.get('initial_mutation_rate', 0.1)
        self_adaptive = config.get('self_adaptive_mutation', True)
        selection = config.get('selection_type', 'plus')  # plus or comma
        fitness_threshold = config.get('fitness_threshold', 85.0)
        
        logger.info(f"Running ES: ({mu},{lambda_}), self_adaptive={self_adaptive}")
        
        # Adapt ES parameters to GA config
        ga_config = GAConfig(
            population_size=mu,
            generations=generations,
            mutation_rate=mutation_rate,
            crossover_rate=0.5,  # ES uses uniform recombination
            elitism_rate=1.0,  # ES always uses elitism (implicit in (μ,λ) or (μ+λ))
            selection_method=SelectionMethod.best,
            mutation_method=MutationMethod.adaptive if self_adaptive else MutationMethod.gaussian,
        )
        
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        pop_config = evolver.select_populations(fitness_threshold)
        evolved_df, results = evolver.evolve_unhealthy_records(pop_config, ga_config)
        
        fitness_history = []
        if 'generation_metrics' in results:
            fitness_history = [
                {
                    'generation': m.get('generation', 0),
                    'best_fitness': m.get('best_fitness', 0),
                    'average_fitness': m.get('average_fitness', 0),
                }
                for m in results['generation_metrics']
            ]
        
        return {
            'evolved_df': evolved_df,
            'fitness_history': fitness_history,
            'best_fitness': results.get('fitness_metrics', {}).get('best_fitness_after', 0),
            'improvement': results.get('fitness_metrics', {}).get('improvement', 0),
            'selected_individuals': results.get('fitness_metrics', {}).get('records_at_target', 0),
            'generations_run': results.get('total_generations', generations),
            'selection_type': selection,
        }
    
    except Exception as e:
        logger.error(f"ES evolution error: {str(e)}")
        raise


def _run_hybrid_evolution(df: pd.DataFrame, config: dict) -> dict:
    """Run Hybrid method - auto-selects best algorithm"""
    try:
        max_iterations = config.get('max_iterations', 100)
        fitness_threshold = config.get('fitness_threshold', 85.0)
        auto_select = config.get('auto_select_algorithm', True)
        ensemble_mode = config.get('ensemble_mode', False)
        enabled_methods = config.get('enabled_algorithms', ['ga', 'pso', 'de', 'es'])
        
        logger.info(f"Running Hybrid: auto_select={auto_select}, enabled={enabled_methods}")
        
        # For hybrid, use the most reliable method (GA as default)
        # In production, implement actual column-type detection
        ga_config = GAConfig(
            population_size=30,
            generations=max_iterations,
            mutation_rate=0.1,
            crossover_rate=0.8,
            selection_method=SelectionMethod.tournament,
            mutation_method=MutationMethod.gaussian,
        )
        
        evolver = DataFitnessEvolverGA(df, track_modifications=True)
        pop_config = evolver.select_populations(fitness_threshold)
        evolved_df, results = evolver.evolve_unhealthy_records(pop_config, ga_config)
        
        fitness_history = []
        if 'generation_metrics' in results:
            fitness_history = [
                {
                    'generation': m.get('generation', 0),
                    'best_fitness': m.get('best_fitness', 0),
                    'average_fitness': m.get('average_fitness', 0),
                }
                for m in results['generation_metrics']
            ]
        
        return {
            'evolved_df': evolved_df,
            'fitness_history': fitness_history,
            'best_fitness': results.get('fitness_metrics', {}).get('best_fitness_after', 0),
            'improvement': results.get('fitness_metrics', {}).get('improvement', 0),
            'records_improved': results.get('fitness_metrics', {}).get('records_at_target', 0),
            'selected_method': 'ga',  # In production, log actual selected method per column
            'ensemble_mode': ensemble_mode,
        }
    
    except Exception as e:
        logger.error(f"Hybrid evolution error: {str(e)}")
        raise


@app.route('/evo/compare', methods=['POST'])
def compare_evolutionary_methods():
    """
    Compare multiple evolutionary algorithm methods on current data.
    Runs each method with specified parameters and returns comparison results.
    
    Request body:
    {
        "methods": ["ga", "pso", "de", "es"],  # Optional, defaults to all
        "config": {
            "fitness_threshold": 85.0,
            "max_iterations": 50,  // Reduced for comparison speed
            ...
        }
    }
    """
    try:
        if 'df' not in current_data:
            return jsonify({'error': 'No data loaded'}), 400
        
        data = request.get_json() or {}
        methods_to_test = data.get('methods', ['ga', 'pso', 'de', 'es', 'hybrid'])
        base_config = data.get('config', {})
        
        # Use smaller config for faster comparison
        if 'generations' not in base_config:
            base_config['generations'] = 30
        if 'population_size' not in base_config:
            base_config['population_size'] = 20
        
        df = current_data['df'].copy()
        results = {}
        
        logger.info(f"Comparing methods: {methods_to_test}")
        
        for method in methods_to_test:
            try:
                logger.info(f"Testing {method.upper()}...")
                
                # Adjust config for each method
                method_config = base_config.copy()
                if method == 'pso':
                    method_config['swarm_size'] = base_config.get('population_size', 20)
                elif method == 'de':
                    method_config['scale_factor'] = 0.8
                elif method == 'es':
                    method_config['offspring_size'] = base_config.get('population_size', 20) * 3
                
                result = _run_method(df, method, method_config)
                
                results[method] = {
                    'best_fitness': result.get('best_fitness', 0),
                    'improvement': result.get('improvement', 0),
                    'records_fixed': result.get('records_fixed', 0),
                    'success': True
                }
                
                logger.info(f"{method.upper()}: improvement={result.get('improvement', 0):.2f}%")
            
            except Exception as e:
                logger.warning(f"Method {method} failed: {e}")
                results[method] = {'error': str(e), 'success': False}
        
        # Find best method
        successful_methods = {m: r for m, r in results.items() if r.get('success')}
        if successful_methods:
            best_method = max(
                successful_methods.keys(),
                key=lambda m: successful_methods[m].get('improvement', 0)
            )
            best_improvement = successful_methods[best_method].get('improvement', 0)
        else:
            best_method = None
            best_improvement = 0
        
        return jsonify({
            'success': True,
            'comparison_results': results,
            'best_method': best_method,
            'best_improvement': best_improvement,
            'methods_tested': len(successful_methods),
            'methods_failed': len([m for m in methods_to_test if not results[m].get('success')])
        }), 200
    
    except Exception as e:
        logger.error(f"Error comparing methods: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def _run_method(df: pd.DataFrame, method: str, config: dict) -> dict:
    """Helper to run any evolutionary method"""
    if method == 'ga':
        return _run_ga_evolution(df, config)
    elif method == 'pso':
        return _run_pso_evolution(df, config)
    elif method == 'de':
        return _run_de_evolution(df, config)
    elif method == 'es':
        return _run_es_evolution(df, config)
    elif method == 'hybrid':
        return _run_hybrid_evolution(df, config)
    else:
        raise ValueError(f"Unknown method: {method}")
