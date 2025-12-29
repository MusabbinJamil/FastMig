#\!/usr/bin/env python3
"""Secret Demo Endpoints for Evolutionary Algorithms"""
import logging
from flask import Blueprint, request, jsonify
logger = logging.getLogger(__name__)
demo_bp = Blueprint("demo", __name__, url_prefix="/demo")

def _capture_output(demo_func):
    import io, sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        exit_code = demo_func()
        output = buffer.getvalue()
        success = exit_code == 0
    except Exception as e:
        output = buffer.getvalue() + f"\\nError: {str(e)}"
        success = False
    finally:
        sys.stdout = old_stdout
    return output, success

def _run_demo(algo_name, demo_map, sections):
    import io, sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        print("\\n" + "="*70)
        print(f"  {algo_name} SYSTEM - DEMONSTRATION")
        print("="*70)
        run_sections = demo_map.keys() if "all" in sections else [s for s in sections if s in demo_map]
        for section in run_sections:
            try:
                demo_map[section]()
            except Exception as e:
                print(f"\\n[Error in {section}]: {str(e)}")
        print("\\n" + "="*70)
        print(f"  {algo_name} DEMONSTRATION COMPLETE")
        print("="*70)
        output, success = buffer.getvalue(), True
    except Exception as e:
        output, success = buffer.getvalue() + f"\\nFatal Error: {str(e)}", False
    finally:
        sys.stdout = old_stdout
    return output, success

@demo_bp.route("/ga", methods=["POST"])
def run_ga_demo():
    try:
        from ga_demo import demo_operators, demo_mappers, demo_ga_optimization, demo_selection_methods, demo_crossover_methods, demo_mutation_methods, demo_metrics
        sections = (request.get_json() or {}).get("sections", ["all"])
        output, success = _run_demo("GA", {"operators": demo_operators, "mappers": demo_mappers, "optimization": demo_ga_optimization, "selection": demo_selection_methods, "crossover": demo_crossover_methods, "mutation": demo_mutation_methods, "metrics": demo_metrics}, sections)
        return jsonify({"success": success, "algorithm": "GA", "output": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@demo_bp.route("/pso", methods=["POST"])
def run_pso_demo():
    try:
        from pso_demo import demo_operators, demo_topologies, demo_variants, demo_optimization, demo_inertia_decay, demo_metrics, demo_seed_values
        sections = (request.get_json() or {}).get("sections", ["all"])
        output, success = _run_demo("PSO", {"operators": demo_operators, "topologies": demo_topologies, "variants": demo_variants, "optimization": demo_optimization, "inertia": demo_inertia_decay, "metrics": demo_metrics, "seeding": demo_seed_values}, sections)
        return jsonify({"success": success, "algorithm": "PSO", "output": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@demo_bp.route("/de", methods=["POST"])
def run_de_demo():
    try:
        from de_demo import demo_operators, demo_strategies, demo_crossover, demo_optimization, demo_adaptive, demo_metrics, demo_seed_values
        sections = (request.get_json() or {}).get("sections", ["all"])
        output, success = _run_demo("DE", {"operators": demo_operators, "strategies": demo_strategies, "crossover": demo_crossover, "optimization": demo_optimization, "adaptive": demo_adaptive, "metrics": demo_metrics, "seeding": demo_seed_values}, sections)
        return jsonify({"success": success, "algorithm": "DE", "output": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@demo_bp.route("/es", methods=["POST"])
def run_es_demo():
    try:
        from es_demo import demo_operators, demo_selection_types, demo_recombination_types, demo_optimization, demo_self_adaptive, demo_metrics, demo_seed_values
        sections = (request.get_json() or {}).get("sections", ["all"])
        output, success = _run_demo("ES", {"operators": demo_operators, "selection": demo_selection_types, "recombination": demo_recombination_types, "optimization": demo_optimization, "adaptive": demo_self_adaptive, "metrics": demo_metrics, "seeding": demo_seed_values}, sections)
        return jsonify({"success": success, "algorithm": "ES", "output": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@demo_bp.route("/all", methods=["POST"])
def run_all_demos():
    try:
        results = {}
        for algo in ["ga", "pso", "de", "es"]:
            try:
                if algo == "ga":
                    from ga_demo import main as demo_main
                elif algo == "pso":
                    from pso_demo import main as demo_main
                elif algo == "de":
                    from de_demo import main as demo_main
                elif algo == "es":
                    from es_demo import main as demo_main
                output, success = _capture_output(demo_main)
                results[algo.upper()] = {"success": success, "output": output}
            except Exception as e:
                results[algo.upper()] = {"success": False, "output": str(e)}
        return jsonify({"success": all(r["success"] for r in results.values()), "results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@demo_bp.route("/quick-test", methods=["POST"])
def run_quick_test():
    import numpy as np, io, sys
    try:
        algorithms = (request.get_json() or {}).get("algorithms", ["ga", "pso", "de", "es"])
        results = {}
        old_stdout, sys.stdout = sys.stdout, io.StringIO()
        print("\\n" + "="*70 + "\\n  QUICK ALGORITHM TEST\\n" + "="*70)
        test_fitness = lambda x: -((x - 5) ** 2)
        if "ga" in algorithms:
            print("\\n[GA] Testing...")
            try:
                from ga_engine import GeneticAlgorithmEngine
                from ga_operators import GAConfig
                from ga_genotype_phenotype import RealValuedMapper
                result = GeneticAlgorithmEngine(GAConfig(population_size=10, generations=10), lambda p: -np.sum(np.array(p)**2) if p else -np.inf, RealValuedMapper(min_val=0.0, max_val=10.0)).run()
                print(f"  Best fitness = {result.best_fitness:.4f}")
                results["GA"] = {"success": True, "best_fitness": float(result.best_fitness)}
            except Exception as e:
                print(f"  Error: {e}")
                results["GA"] = {"success": False, "error": str(e)}
        if "pso" in algorithms:
            print("\\n[PSO] Testing...")
            try:
                from pso_engine import optimize_value_pso
                from pso_operators import PSOConfig
                result = optimize_value_pso(test_fitness, 0.0, 10.0, PSOConfig(swarm_size=15, iterations=15))
                print(f"  Best fitness = {result.best_fitness:.4f}")
                results["PSO"] = {"success": True, "best_fitness": float(result.best_fitness)}
            except Exception as e:
                print(f"  Error: {e}")
                results["PSO"] = {"success": False, "error": str(e)}
        if "de" in algorithms:
            print("\\n[DE] Testing...")
            try:
                from de_engine import optimize_value_de
                from de_operators import DEConfig
                result = optimize_value_de(test_fitness, 0.0, 10.0, DEConfig(population_size=15, generations=15))
                print(f"  Best fitness = {result.best_fitness:.4f}")
                results["DE"] = {"success": True, "best_fitness": float(result.best_fitness)}
            except Exception as e:
                print(f"  Error: {e}")
                results["DE"] = {"success": False, "error": str(e)}
        if "es" in algorithms:
            print("\\n[ES] Testing...")
            try:
                from es_engine import optimize_value_es
                from es_operators import ESConfig
                result = optimize_value_es(test_fitness, 0.0, 10.0, ESConfig(mu=10, lambda_=70, generations=15))
                print(f"  Best fitness = {result.best_fitness:.4f}")
                results["ES"] = {"success": True, "best_fitness": float(result.best_fitness)}
            except Exception as e:
                print(f"  Error: {e}")
                results["ES"] = {"success": False, "error": str(e)}
        print("\\n" + "="*70 + "\\n  QUICK TEST COMPLETE\\n" + "="*70)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        return jsonify({"success": all(r.get("success") for r in results.values()), "results": results, "output": output}), 200
    except Exception as e:
        if "old_stdout" in dir():
            sys.stdout = old_stdout
        return jsonify({"error": str(e)}), 500
