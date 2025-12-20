/// Genetic Algorithm Configuration Model
class GAConfigModel {
  final int populationSize;
  final int generations;
  final double mutationRate;
  final double crossoverRate;
  final bool elitism;
  final int eliteCount;
  final String selectionMethod;
  final String crossoverMethod;
  final String mutationMethod;
  final bool earlyStoppingEnabled;
  final int earlyStoppingPatience;
  final double fitnessThreshold;
  final List<String>? targetColumns;
  final Map<String, dynamic>? columnBounds;

  GAConfigModel({
    this.populationSize = 30,
    this.generations = 100,
    this.mutationRate = 0.1,
    this.crossoverRate = 0.8,
    this.elitism = true,
    this.eliteCount = 2,
    this.selectionMethod = 'tournament',
    this.crossoverMethod = 'single_point',
    this.mutationMethod = 'gaussian',
    this.earlyStoppingEnabled = true,
    this.earlyStoppingPatience = 10,
    this.fitnessThreshold = 85.0,
    this.targetColumns,
    this.columnBounds,
  });

  /// Convert to JSON for API calls
  Map<String, dynamic> toJson() {
    return {
      'population_size': populationSize,
      'generations': generations,
      'mutation_rate': mutationRate,
      'crossover_rate': crossoverRate,
      'elitism': elitism,
      'elite_count': eliteCount,
      'selection_method': selectionMethod,
      'crossover_method': crossoverMethod,
      'mutation_method': mutationMethod,
      'early_stopping_enabled': earlyStoppingEnabled,
      'early_stopping_patience': earlyStoppingPatience,
      'fitness_threshold': fitnessThreshold,
      if (targetColumns != null) 'target_columns': targetColumns,
      if (columnBounds != null) 'column_bounds': columnBounds,
    };
  }

  /// Create from JSON response
  factory GAConfigModel.fromJson(Map<String, dynamic> json) {
    return GAConfigModel(
      populationSize: json['population_size'] ?? 30,
      generations: json['generations'] ?? 100,
      mutationRate: (json['mutation_rate'] ?? 0.1).toDouble(),
      crossoverRate: (json['crossover_rate'] ?? 0.8).toDouble(),
      elitism: json['elitism'] ?? true,
      eliteCount: json['elite_count'] ?? 2,
      selectionMethod: json['selection_method'] ?? 'tournament',
      crossoverMethod: json['crossover_method'] ?? 'single_point',
      mutationMethod: json['mutation_method'] ?? 'gaussian',
      earlyStoppingEnabled: json['early_stopping_enabled'] ?? true,
      earlyStoppingPatience: json['early_stopping_patience'] ?? 10,
      fitnessThreshold: (json['fitness_threshold'] ?? 85.0).toDouble(),
      targetColumns: json['target_columns'] != null
          ? List<String>.from(json['target_columns'])
          : null,
      columnBounds: json['column_bounds'] as Map<String, dynamic>?,
    );
  }

  /// Copy with modifications
  GAConfigModel copyWith({
    int? populationSize,
    int? generations,
    double? mutationRate,
    double? crossoverRate,
    bool? elitism,
    int? eliteCount,
    String? selectionMethod,
    String? crossoverMethod,
    String? mutationMethod,
    bool? earlyStoppingEnabled,
    int? earlyStoppingPatience,
    double? fitnessThreshold,
    List<String>? targetColumns,
    Map<String, dynamic>? columnBounds,
  }) {
    return GAConfigModel(
      populationSize: populationSize ?? this.populationSize,
      generations: generations ?? this.generations,
      mutationRate: mutationRate ?? this.mutationRate,
      crossoverRate: crossoverRate ?? this.crossoverRate,
      elitism: elitism ?? this.elitism,
      eliteCount: eliteCount ?? this.eliteCount,
      selectionMethod: selectionMethod ?? this.selectionMethod,
      crossoverMethod: crossoverMethod ?? this.crossoverMethod,
      mutationMethod: mutationMethod ?? this.mutationMethod,
      earlyStoppingEnabled: earlyStoppingEnabled ?? this.earlyStoppingEnabled,
      earlyStoppingPatience:
          earlyStoppingPatience ?? this.earlyStoppingPatience,
      fitnessThreshold: fitnessThreshold ?? this.fitnessThreshold,
      targetColumns: targetColumns ?? this.targetColumns,
      columnBounds: columnBounds ?? this.columnBounds,
    );
  }

  /// Presets for different optimization strategies
  static GAConfigModel getPreset(String presetName) {
    switch (presetName) {
      case 'fast':
        return GAConfigModel(
          populationSize: 20,
          generations: 30,
          mutationRate: 0.15,
          crossoverRate: 0.75,
          earlyStoppingPatience: 5,
        );
      case 'balanced':
        return GAConfigModel(
          populationSize: 30,
          generations: 100,
          mutationRate: 0.10,
          crossoverRate: 0.80,
          earlyStoppingPatience: 10,
        );
      case 'quality':
        return GAConfigModel(
          populationSize: 50,
          generations: 200,
          mutationRate: 0.08,
          crossoverRate: 0.85,
          earlyStoppingPatience: 15,
        );
      default:
        return GAConfigModel();
    }
  }
}

/// Grammar/Rule Configuration for Grammatical Evolution
class GrammarConfigModel {
  final String grammarType;
  final List<String> rules;
  final int maxTreeDepth;
  final String? customGrammarPath;
  final bool enableTypeChecking;

  GrammarConfigModel({
    this.grammarType = 'standard',
    this.rules = const [],
    this.maxTreeDepth = 8,
    this.customGrammarPath,
    this.enableTypeChecking = true,
  });

  Map<String, dynamic> toJson() {
    return {
      'grammar_type': grammarType,
      'rules': rules,
      'max_tree_depth': maxTreeDepth,
      'custom_grammar_path': customGrammarPath,
      'enable_type_checking': enableTypeChecking,
    };
  }

  factory GrammarConfigModel.fromJson(Map<String, dynamic> json) {
    return GrammarConfigModel(
      grammarType: json['grammar_type'] ?? 'standard',
      rules: json['rules'] != null ? List<String>.from(json['rules']) : [],
      maxTreeDepth: json['max_tree_depth'] ?? 8,
      customGrammarPath: json['custom_grammar_path'],
      enableTypeChecking: json['enable_type_checking'] ?? true,
    );
  }

  /// Copy with modifications
  GrammarConfigModel copyWith({
    String? grammarType,
    List<String>? rules,
    int? maxTreeDepth,
    String? customGrammarPath,
    bool? enableTypeChecking,
  }) {
    return GrammarConfigModel(
      grammarType: grammarType ?? this.grammarType,
      rules: rules ?? this.rules,
      maxTreeDepth: maxTreeDepth ?? this.maxTreeDepth,
      customGrammarPath: customGrammarPath ?? this.customGrammarPath,
      enableTypeChecking: enableTypeChecking ?? this.enableTypeChecking,
    );
  }
}

/// GA Metrics for tracking generation-by-generation progress
class GAMetricsModel {
  final int generation;
  final double bestFitness;
  final double worstFitness;
  final double averageFitness;
  final double fitnessVariance;
  final int populationSize;
  final DateTime timestamp;
  final String? bestIndividual;

  GAMetricsModel({
    required this.generation,
    required this.bestFitness,
    required this.worstFitness,
    required this.averageFitness,
    required this.fitnessVariance,
    required this.populationSize,
    required this.timestamp,
    this.bestIndividual,
  });

  factory GAMetricsModel.fromJson(Map<String, dynamic> json) {
    return GAMetricsModel(
      generation: json['generation'] ?? 0,
      bestFitness: (json['best_fitness'] ?? 0.0).toDouble(),
      worstFitness: (json['worst_fitness'] ?? 0.0).toDouble(),
      averageFitness: (json['average_fitness'] ?? 0.0).toDouble(),
      fitnessVariance: (json['fitness_variance'] ?? 0.0).toDouble(),
      populationSize: json['population_size'] ?? 0,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      bestIndividual: json['best_individual'],
    );
  }
}

/// Expression Tree Node for visualization
class ExpressionTreeNode {
  final String value;
  final String type; // 'operator', 'operand', 'function'
  final List<ExpressionTreeNode> children;
  final double? fitnessContribution;

  ExpressionTreeNode({
    required this.value,
    required this.type,
    this.children = const [],
    this.fitnessContribution,
  });

  factory ExpressionTreeNode.fromJson(Map<String, dynamic> json) {
    final childrenJson = json['children'] as List?;
    return ExpressionTreeNode(
      value: json['value'] ?? 'root',
      type: json['type'] ?? 'operand',
      children: childrenJson != null
          ? childrenJson
              .map((child) => ExpressionTreeNode.fromJson(child))
              .toList()
          : [],
      fitnessContribution: json['fitness_contribution'] != null
          ? (json['fitness_contribution'] as num).toDouble()
          : null,
    );
  }

  bool get isLeaf => children.isEmpty;
  bool get isOperator => type == 'operator';
  bool get isFunction => type == 'function';
}
