/// Base class for all evolutionary algorithm configurations
abstract class EvolutionaryConfigBase {
  final double fitnessThreshold;
  final int? healthySampleSize;
  final bool trackProgress;
  final int maxIterations;

  EvolutionaryConfigBase({
    this.fitnessThreshold = 85.0,
    this.healthySampleSize,
    this.trackProgress = false,
    this.maxIterations = 100,
  });

  /// Convert to JSON for API calls
  Map<String, dynamic> toJson();

  /// Create from JSON response
  static EvolutionaryConfigBase fromJson(
    Map<String, dynamic> json,
    String methodType,
  ) {
    switch (methodType.toLowerCase()) {
      case 'ga':
        return GAConfigModel.fromJson(json);
      case 'pso':
        return PSOConfigModel.fromJson(json);
      case 'de':
        return DEConfigModel.fromJson(json);
      case 'es':
        return ESConfigModel.fromJson(json);
      case 'hybrid':
        return HybridConfigModel.fromJson(json);
      default:
        throw Exception('Unknown evolutionary method: $methodType');
    }
  }

  /// Get description for UI display
  String getDescription();

  /// Get icon for UI display
  String getIcon();
}

/// ============================================================================
/// GENETIC ALGORITHM (GA) CONFIGURATION
/// ============================================================================

class GAConfigModel extends EvolutionaryConfigBase {
  final int populationSize;
  final int generations;
  final double mutationRate;
  final double crossoverRate;
  final bool elitism;
  final int eliteCount;
  final String selectionMethod; // tournament, roulette, rank-based
  final String crossoverMethod; // single_point, two_point, uniform, arithmetic
  final String mutationMethod; // gaussian, uniform, adaptive
  final bool earlyStoppingEnabled;
  final int earlyStoppingPatience;
  final List<String>? targetColumns;
  final Map<String, dynamic>? columnBounds;

  GAConfigModel({
    int populationSize = 30,
    int generations = 100,
    double mutationRate = 0.1,
    double crossoverRate = 0.8,
    bool elitism = true,
    int eliteCount = 2,
    String selectionMethod = 'tournament',
    String crossoverMethod = 'single_point',
    String mutationMethod = 'gaussian',
    bool earlyStoppingEnabled = true,
    int earlyStoppingPatience = 10,
    double fitnessThreshold = 85.0,
    int? healthySampleSize,
    bool trackProgress = false,
    int maxIterations = 100,
    List<String>? targetColumns,
    Map<String, dynamic>? columnBounds,
  })  : populationSize = populationSize,
        generations = generations,
        mutationRate = mutationRate,
        crossoverRate = crossoverRate,
        elitism = elitism,
        eliteCount = eliteCount,
        selectionMethod = selectionMethod,
        crossoverMethod = crossoverMethod,
        mutationMethod = mutationMethod,
        earlyStoppingEnabled = earlyStoppingEnabled,
        earlyStoppingPatience = earlyStoppingPatience,
        targetColumns = targetColumns,
        columnBounds = columnBounds,
        super(
          fitnessThreshold: fitnessThreshold,
          healthySampleSize: healthySampleSize,
          trackProgress: trackProgress,
          maxIterations: generations,
        );

  @override
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
      'track_progress': trackProgress,
      if (healthySampleSize != null) 'healthy_sample_size': healthySampleSize,
      if (targetColumns != null) 'target_columns': targetColumns,
      if (columnBounds != null) 'column_bounds': columnBounds,
    };
  }

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
      trackProgress: json['track_progress'] ?? false,
      healthySampleSize: json['healthy_sample_size'],
      targetColumns: json['target_columns'] != null
          ? List<String>.from(json['target_columns'])
          : null,
      columnBounds: json['column_bounds'] as Map<String, dynamic>?,
    );
  }

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
    int? healthySampleSize,
    bool? trackProgress,
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
      healthySampleSize: healthySampleSize ?? this.healthySampleSize,
      trackProgress: trackProgress ?? this.trackProgress,
      targetColumns: targetColumns ?? this.targetColumns,
      columnBounds: columnBounds ?? this.columnBounds,
    );
  }

  @override
  String getDescription() =>
      'Evolves populations using selection, crossover, and mutation operators';

  @override
  String getIcon() => '🧬';

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

  static const List<String> selectionMethods = [
    'tournament',
    'roulette',
    'rank-based'
  ];
  static const List<String> crossoverMethods = [
    'single_point',
    'two_point',
    'uniform',
    'arithmetic'
  ];
  static const List<String> mutationMethods = [
    'gaussian',
    'uniform',
    'adaptive'
  ];
}

/// ============================================================================
/// PARTICLE SWARM OPTIMIZATION (PSO) CONFIGURATION
/// ============================================================================

class PSOConfigModel extends EvolutionaryConfigBase {
  final int swarmSize;
  final int iterations;
  final double inertiaWeight; // w: controls exploration vs exploitation
  final double cognitiveParameter; // c1: individual best influence
  final double socialParameter; // c2: swarm best influence
  final double velocityMax;
  final double velocityMin;
  final bool useConstrictionFactor;
  final double constrictionCoefficient;
  final String topologyType; // global, local, ring, random
  final int neighborhoodSize;

  PSOConfigModel({
    int swarmSize = 30,
    int iterations = 100,
    double inertiaWeight = 0.7,
    double cognitiveParameter = 1.5,
    double socialParameter = 1.5,
    double velocityMax = 1.0,
    double velocityMin = -1.0,
    bool useConstrictionFactor = false,
    double constrictionCoefficient = 0.729,
    String topologyType = 'global',
    int neighborhoodSize = 5,
    double fitnessThreshold = 85.0,
    int? healthySampleSize,
    bool trackProgress = false,
  })  : swarmSize = swarmSize,
        iterations = iterations,
        inertiaWeight = inertiaWeight,
        cognitiveParameter = cognitiveParameter,
        socialParameter = socialParameter,
        velocityMax = velocityMax,
        velocityMin = velocityMin,
        useConstrictionFactor = useConstrictionFactor,
        constrictionCoefficient = constrictionCoefficient,
        topologyType = topologyType,
        neighborhoodSize = neighborhoodSize,
        super(
          fitnessThreshold: fitnessThreshold,
          healthySampleSize: healthySampleSize,
          trackProgress: trackProgress,
          maxIterations: iterations,
        );

  @override
  Map<String, dynamic> toJson() {
    return {
      'swarm_size': swarmSize,
      'iterations': iterations,
      'inertia_weight': inertiaWeight,
      'cognitive_parameter': cognitiveParameter,
      'social_parameter': socialParameter,
      'velocity_max': velocityMax,
      'velocity_min': velocityMin,
      'use_constriction_factor': useConstrictionFactor,
      'constriction_coefficient': constrictionCoefficient,
      'topology_type': topologyType,
      'neighborhood_size': neighborhoodSize,
      'fitness_threshold': fitnessThreshold,
      'track_progress': trackProgress,
      if (healthySampleSize != null) 'healthy_sample_size': healthySampleSize,
    };
  }

  factory PSOConfigModel.fromJson(Map<String, dynamic> json) {
    return PSOConfigModel(
      swarmSize: json['swarm_size'] ?? 30,
      iterations: json['iterations'] ?? 100,
      inertiaWeight: (json['inertia_weight'] ?? 0.7).toDouble(),
      cognitiveParameter: (json['cognitive_parameter'] ?? 1.5).toDouble(),
      socialParameter: (json['social_parameter'] ?? 1.5).toDouble(),
      velocityMax: (json['velocity_max'] ?? 1.0).toDouble(),
      velocityMin: (json['velocity_min'] ?? -1.0).toDouble(),
      useConstrictionFactor: json['use_constriction_factor'] ?? false,
      constrictionCoefficient:
          (json['constriction_coefficient'] ?? 0.729).toDouble(),
      topologyType: json['topology_type'] ?? 'global',
      neighborhoodSize: json['neighborhood_size'] ?? 5,
      fitnessThreshold: (json['fitness_threshold'] ?? 85.0).toDouble(),
      trackProgress: json['track_progress'] ?? false,
      healthySampleSize: json['healthy_sample_size'],
    );
  }

  PSOConfigModel copyWith({
    int? swarmSize,
    int? iterations,
    double? inertiaWeight,
    double? cognitiveParameter,
    double? socialParameter,
    double? velocityMax,
    double? velocityMin,
    bool? useConstrictionFactor,
    double? constrictionCoefficient,
    String? topologyType,
    int? neighborhoodSize,
    double? fitnessThreshold,
    int? healthySampleSize,
    bool? trackProgress,
  }) {
    return PSOConfigModel(
      swarmSize: swarmSize ?? this.swarmSize,
      iterations: iterations ?? this.iterations,
      inertiaWeight: inertiaWeight ?? this.inertiaWeight,
      cognitiveParameter: cognitiveParameter ?? this.cognitiveParameter,
      socialParameter: socialParameter ?? this.socialParameter,
      velocityMax: velocityMax ?? this.velocityMax,
      velocityMin: velocityMin ?? this.velocityMin,
      useConstrictionFactor:
          useConstrictionFactor ?? this.useConstrictionFactor,
      constrictionCoefficient:
          constrictionCoefficient ?? this.constrictionCoefficient,
      topologyType: topologyType ?? this.topologyType,
      neighborhoodSize: neighborhoodSize ?? this.neighborhoodSize,
      fitnessThreshold: fitnessThreshold ?? this.fitnessThreshold,
      healthySampleSize: healthySampleSize ?? this.healthySampleSize,
      trackProgress: trackProgress ?? this.trackProgress,
    );
  }

  @override
  String getDescription() =>
      'Swarm intelligence for numeric data - particles move toward best solutions';

  @override
  String getIcon() => '🐦';

  static const List<String> topologyTypes = [
    'global',
    'local',
    'ring',
    'random'
  ];
}

/// ============================================================================
/// DIFFERENTIAL EVOLUTION (DE) CONFIGURATION
/// ============================================================================

class DEConfigModel extends EvolutionaryConfigBase {
  final int populationSize;
  final int generations;
  final double scaleFactor; // F: [0, 2], controls mutation magnitude
  final double crossoverRate; // CR: [0, 1], probability of parameter selection
  final String mutationStrategy;
  // DE/best/1, DE/rand/1, DE/best/2, DE/rand/2, etc.
  final String selectionStrategy; // best, tournament, random
  final bool adaptiveF; // Self-adaptive F parameter
  final bool adaptiveCR; // Self-adaptive CR parameter
  final double lowerBound;
  final double upperBound;

  DEConfigModel({
    int populationSize = 30,
    int generations = 100,
    double scaleFactor = 0.8,
    double crossoverRate = 0.9,
    String mutationStrategy = 'DE/best/1',
    String selectionStrategy = 'best',
    bool adaptiveF = false,
    bool adaptiveCR = false,
    double lowerBound = 0.0,
    double upperBound = 1.0,
    double fitnessThreshold = 85.0,
    int? healthySampleSize,
    bool trackProgress = false,
  })  : populationSize = populationSize,
        generations = generations,
        scaleFactor = scaleFactor,
        crossoverRate = crossoverRate,
        mutationStrategy = mutationStrategy,
        selectionStrategy = selectionStrategy,
        adaptiveF = adaptiveF,
        adaptiveCR = adaptiveCR,
        lowerBound = lowerBound,
        upperBound = upperBound,
        super(
          fitnessThreshold: fitnessThreshold,
          healthySampleSize: healthySampleSize,
          trackProgress: trackProgress,
          maxIterations: generations,
        );

  @override
  Map<String, dynamic> toJson() {
    return {
      'population_size': populationSize,
      'generations': generations,
      'scale_factor': scaleFactor,
      'crossover_rate': crossoverRate,
      'mutation_strategy': mutationStrategy,
      'selection_strategy': selectionStrategy,
      'adaptive_f': adaptiveF,
      'adaptive_cr': adaptiveCR,
      'lower_bound': lowerBound,
      'upper_bound': upperBound,
      'fitness_threshold': fitnessThreshold,
      'track_progress': trackProgress,
      if (healthySampleSize != null) 'healthy_sample_size': healthySampleSize,
    };
  }

  factory DEConfigModel.fromJson(Map<String, dynamic> json) {
    return DEConfigModel(
      populationSize: json['population_size'] ?? 30,
      generations: json['generations'] ?? 100,
      scaleFactor: (json['scale_factor'] ?? 0.8).toDouble(),
      crossoverRate: (json['crossover_rate'] ?? 0.9).toDouble(),
      mutationStrategy: json['mutation_strategy'] ?? 'DE/best/1',
      selectionStrategy: json['selection_strategy'] ?? 'best',
      adaptiveF: json['adaptive_f'] ?? false,
      adaptiveCR: json['adaptive_cr'] ?? false,
      lowerBound: (json['lower_bound'] ?? 0.0).toDouble(),
      upperBound: (json['upper_bound'] ?? 1.0).toDouble(),
      fitnessThreshold: (json['fitness_threshold'] ?? 85.0).toDouble(),
      trackProgress: json['track_progress'] ?? false,
      healthySampleSize: json['healthy_sample_size'],
    );
  }

  DEConfigModel copyWith({
    int? populationSize,
    int? generations,
    double? scaleFactor,
    double? crossoverRate,
    String? mutationStrategy,
    String? selectionStrategy,
    bool? adaptiveF,
    bool? adaptiveCR,
    double? lowerBound,
    double? upperBound,
    double? fitnessThreshold,
    int? healthySampleSize,
    bool? trackProgress,
  }) {
    return DEConfigModel(
      populationSize: populationSize ?? this.populationSize,
      generations: generations ?? this.generations,
      scaleFactor: scaleFactor ?? this.scaleFactor,
      crossoverRate: crossoverRate ?? this.crossoverRate,
      mutationStrategy: mutationStrategy ?? this.mutationStrategy,
      selectionStrategy: selectionStrategy ?? this.selectionStrategy,
      adaptiveF: adaptiveF ?? this.adaptiveF,
      adaptiveCR: adaptiveCR ?? this.adaptiveCR,
      lowerBound: lowerBound ?? this.lowerBound,
      upperBound: upperBound ?? this.upperBound,
      fitnessThreshold: fitnessThreshold ?? this.fitnessThreshold,
      healthySampleSize: healthySampleSize ?? this.healthySampleSize,
      trackProgress: trackProgress ?? this.trackProgress,
    );
  }

  @override
  String getDescription() =>
      'Robust global optimization with vector differences';

  @override
  String getIcon() => '⚡';

  static const List<String> mutationStrategies = [
    'DE/best/1',
    'DE/best/2',
    'DE/rand/1',
    'DE/rand/2',
    'DE/rand/1/bin',
    'DE/best/1/bin'
  ];
}

/// ============================================================================
/// EVOLUTION STRATEGY (ES) CONFIGURATION
/// ============================================================================

class ESConfigModel extends EvolutionaryConfigBase {
  final int populationSize;
  final int offspringSize;
  final int generations;
  final String selectionType; // plus (μ+λ) or comma (μ,λ)
  final double initialMutationRate;
  final bool selfAdaptiveMutation;
  final double learningRate; // For self-adaptive parameters
  final String recombinationType; // discrete, intermediate, global
  final int parentCount; // Number of parents for recombination

  ESConfigModel({
    int populationSize = 20,
    int offspringSize = 60,
    int generations = 100,
    String selectionType = 'plus',
    double initialMutationRate = 0.1,
    bool selfAdaptiveMutation = true,
    double learningRate = 0.1,
    String recombinationType = 'intermediate',
    int parentCount = 2,
    double fitnessThreshold = 85.0,
    int? healthySampleSize,
    bool trackProgress = false,
  })  : populationSize = populationSize,
        offspringSize = offspringSize,
        generations = generations,
        selectionType = selectionType,
        initialMutationRate = initialMutationRate,
        selfAdaptiveMutation = selfAdaptiveMutation,
        learningRate = learningRate,
        recombinationType = recombinationType,
        parentCount = parentCount,
        super(
          fitnessThreshold: fitnessThreshold,
          healthySampleSize: healthySampleSize,
          trackProgress: trackProgress,
          maxIterations: generations,
        );

  @override
  Map<String, dynamic> toJson() {
    return {
      'population_size': populationSize,
      'offspring_size': offspringSize,
      'generations': generations,
      'selection_type': selectionType,
      'initial_mutation_rate': initialMutationRate,
      'self_adaptive_mutation': selfAdaptiveMutation,
      'learning_rate': learningRate,
      'recombination_type': recombinationType,
      'parent_count': parentCount,
      'fitness_threshold': fitnessThreshold,
      'track_progress': trackProgress,
      if (healthySampleSize != null) 'healthy_sample_size': healthySampleSize,
    };
  }

  factory ESConfigModel.fromJson(Map<String, dynamic> json) {
    return ESConfigModel(
      populationSize: json['population_size'] ?? 20,
      offspringSize: json['offspring_size'] ?? 60,
      generations: json['generations'] ?? 100,
      selectionType: json['selection_type'] ?? 'plus',
      initialMutationRate: (json['initial_mutation_rate'] ?? 0.1).toDouble(),
      selfAdaptiveMutation: json['self_adaptive_mutation'] ?? true,
      learningRate: (json['learning_rate'] ?? 0.1).toDouble(),
      recombinationType: json['recombination_type'] ?? 'intermediate',
      parentCount: json['parent_count'] ?? 2,
      fitnessThreshold: (json['fitness_threshold'] ?? 85.0).toDouble(),
      trackProgress: json['track_progress'] ?? false,
      healthySampleSize: json['healthy_sample_size'],
    );
  }

  ESConfigModel copyWith({
    int? populationSize,
    int? offspringSize,
    int? generations,
    String? selectionType,
    double? initialMutationRate,
    bool? selfAdaptiveMutation,
    double? learningRate,
    String? recombinationType,
    int? parentCount,
    double? fitnessThreshold,
    int? healthySampleSize,
    bool? trackProgress,
  }) {
    return ESConfigModel(
      populationSize: populationSize ?? this.populationSize,
      offspringSize: offspringSize ?? this.offspringSize,
      generations: generations ?? this.generations,
      selectionType: selectionType ?? this.selectionType,
      initialMutationRate: initialMutationRate ?? this.initialMutationRate,
      selfAdaptiveMutation: selfAdaptiveMutation ?? this.selfAdaptiveMutation,
      learningRate: learningRate ?? this.learningRate,
      recombinationType: recombinationType ?? this.recombinationType,
      parentCount: parentCount ?? this.parentCount,
      fitnessThreshold: fitnessThreshold ?? this.fitnessThreshold,
      healthySampleSize: healthySampleSize ?? this.healthySampleSize,
      trackProgress: trackProgress ?? this.trackProgress,
    );
  }

  @override
  String getDescription() =>
      'Self-adaptive mutation rates for consistent improvements';

  @override
  String getIcon() => '🔄';

  static const List<String> selectionTypes = ['plus', 'comma'];
  static const List<String> recombinationTypes = [
    'discrete',
    'intermediate',
    'global'
  ];
}

/// ============================================================================
/// HYBRID CONFIGURATION (Auto-selects best algorithm per column)
/// ============================================================================

class HybridConfigModel extends EvolutionaryConfigBase {
  final bool autoSelectAlgorithm;
  final Map<String, String> columnAlgorithmMapping; // column -> algorithm
  final bool ensembleMode; // Run multiple algorithms and blend results
  final List<String> enabledAlgorithms;

  HybridConfigModel({
    int maxIterations = 100,
    double fitnessThreshold = 85.0,
    int? healthySampleSize,
    bool trackProgress = false,
    bool autoSelectAlgorithm = true,
    Map<String, String> columnAlgorithmMapping = const {},
    bool ensembleMode = false,
    List<String> enabledAlgorithms = const ['ga', 'pso', 'de', 'es'],
  })  : autoSelectAlgorithm = autoSelectAlgorithm,
        columnAlgorithmMapping = columnAlgorithmMapping,
        ensembleMode = ensembleMode,
        enabledAlgorithms = enabledAlgorithms,
        super(
          fitnessThreshold: fitnessThreshold,
          healthySampleSize: healthySampleSize,
          trackProgress: trackProgress,
          maxIterations: maxIterations,
        );

  @override
  Map<String, dynamic> toJson() {
    return {
      'auto_select_algorithm': autoSelectAlgorithm,
      'column_algorithm_mapping': columnAlgorithmMapping,
      'ensemble_mode': ensembleMode,
      'enabled_algorithms': enabledAlgorithms,
      'fitness_threshold': fitnessThreshold,
      'track_progress': trackProgress,
      if (healthySampleSize != null) 'healthy_sample_size': healthySampleSize,
    };
  }

  factory HybridConfigModel.fromJson(Map<String, dynamic> json) {
    return HybridConfigModel(
      autoSelectAlgorithm: json['auto_select_algorithm'] ?? true,
      columnAlgorithmMapping:
          Map<String, String>.from(json['column_algorithm_mapping'] ?? {}),
      ensembleMode: json['ensemble_mode'] ?? false,
      enabledAlgorithms: List<String>.from(
          json['enabled_algorithms'] ?? ['ga', 'pso', 'de', 'es']),
      fitnessThreshold: (json['fitness_threshold'] ?? 85.0).toDouble(),
      trackProgress: json['track_progress'] ?? false,
      healthySampleSize: json['healthy_sample_size'],
    );
  }

  HybridConfigModel copyWith({
    int? maxIterations,
    double? fitnessThreshold,
    int? healthySampleSize,
    bool? trackProgress,
    bool? autoSelectAlgorithm,
    Map<String, String>? columnAlgorithmMapping,
    bool? ensembleMode,
    List<String>? enabledAlgorithms,
  }) {
    return HybridConfigModel(
      maxIterations: maxIterations ?? this.maxIterations,
      fitnessThreshold: fitnessThreshold ?? this.fitnessThreshold,
      healthySampleSize: healthySampleSize ?? this.healthySampleSize,
      trackProgress: trackProgress ?? this.trackProgress,
      autoSelectAlgorithm: autoSelectAlgorithm ?? this.autoSelectAlgorithm,
      columnAlgorithmMapping:
          columnAlgorithmMapping ?? this.columnAlgorithmMapping,
      ensembleMode: ensembleMode ?? this.ensembleMode,
      enabledAlgorithms: enabledAlgorithms ?? this.enabledAlgorithms,
    );
  }

  @override
  String getDescription() =>
      'Intelligently selects best algorithm per column type';

  @override
  String getIcon() => '🚀';
}
