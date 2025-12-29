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

  static const Map<String, String> selectionMethodDisplayNames = {
    'tournament': 'Tournament Selection',
    'roulette': 'Roulette Wheel',
    'rank-based': 'Rank-Based Selection',
  };

  static const List<String> crossoverMethods = [
    'single_point',
    'two_point',
    'uniform',
    'arithmetic'
  ];

  static const Map<String, String> crossoverMethodDisplayNames = {
    'single_point': 'Single-Point Crossover',
    'two_point': 'Two-Point Crossover',
    'uniform': 'Uniform Crossover',
    'arithmetic': 'Arithmetic Crossover',
  };

  static const List<String> mutationMethods = [
    'gaussian',
    'uniform',
    'adaptive'
  ];

  static const Map<String, String> mutationMethodDisplayNames = {
    'gaussian': 'Gaussian Mutation',
    'uniform': 'Uniform Mutation',
    'adaptive': 'Adaptive Mutation',
  };
}

/// ============================================================================
/// PARTICLE SWARM OPTIMIZATION (PSO) CONFIGURATION
/// ============================================================================

class PSOConfigModel extends EvolutionaryConfigBase {
  final int swarmSize;
  final int iterations;
  final double inertiaWeight; // w: controls exploration vs exploitation
  final double inertiaMin; // For decay variant
  final double inertiaMax; // For decay variant
  final double cognitiveParameter; // c1: individual best influence
  final double socialParameter; // c2: swarm best influence
  final double velocityClamp; // Max velocity as fraction of range
  final String topologyType; // gbest, lbest, ring, random, von_neumann
  final String variant; // standard, constriction, inertia_decay
  final double constrictionFactor;
  final int neighborhoodSize;
  final bool earlyStoppingEnabled;
  final int earlyStoppingPatience;

  PSOConfigModel({
    int swarmSize = 30,
    int iterations = 100,
    double inertiaWeight = 0.7,
    double inertiaMin = 0.4,
    double inertiaMax = 0.9,
    double cognitiveParameter = 1.5,
    double socialParameter = 1.5,
    double velocityClamp = 0.2,
    String topologyType = 'gbest',
    String variant = 'standard',
    double constrictionFactor = 0.729,
    int neighborhoodSize = 3,
    bool earlyStoppingEnabled = true,
    int earlyStoppingPatience = 10,
    double fitnessThreshold = 85.0,
    int? healthySampleSize,
    bool trackProgress = false,
  })  : swarmSize = swarmSize,
        iterations = iterations,
        inertiaWeight = inertiaWeight,
        inertiaMin = inertiaMin,
        inertiaMax = inertiaMax,
        cognitiveParameter = cognitiveParameter,
        socialParameter = socialParameter,
        velocityClamp = velocityClamp,
        topologyType = topologyType,
        variant = variant,
        constrictionFactor = constrictionFactor,
        neighborhoodSize = neighborhoodSize,
        earlyStoppingEnabled = earlyStoppingEnabled,
        earlyStoppingPatience = earlyStoppingPatience,
        super(
          fitnessThreshold: fitnessThreshold,
          healthySampleSize: healthySampleSize,
          trackProgress: trackProgress,
          maxIterations: iterations,
        );

  @override
  Map<String, dynamic> toJson() {
    return {
      'population_size': swarmSize,
      'generations': iterations,
      'inertia_weight': inertiaWeight,
      'inertia_min': inertiaMin,
      'inertia_max': inertiaMax,
      'cognitive_coeff': cognitiveParameter,
      'social_coeff': socialParameter,
      'velocity_clamp': velocityClamp,
      'pso_topology': topologyType,
      'pso_variant': variant,
      'constriction_factor': constrictionFactor,
      'neighborhood_size': neighborhoodSize,
      'early_stopping': earlyStoppingEnabled,
      'patience': earlyStoppingPatience,
      'fitness_threshold': fitnessThreshold / 100.0, // Convert to 0-1 range
      'track_progress': trackProgress,
      if (healthySampleSize != null) 'healthy_sample_size': healthySampleSize,
    };
  }

  factory PSOConfigModel.fromJson(Map<String, dynamic> json) {
    return PSOConfigModel(
      swarmSize: json['population_size'] ?? json['swarm_size'] ?? 30,
      iterations: json['generations'] ?? json['iterations'] ?? 100,
      inertiaWeight: (json['inertia_weight'] ?? 0.7).toDouble(),
      inertiaMin: (json['inertia_min'] ?? 0.4).toDouble(),
      inertiaMax: (json['inertia_max'] ?? 0.9).toDouble(),
      cognitiveParameter: (json['cognitive_coeff'] ?? json['cognitive_parameter'] ?? 1.5).toDouble(),
      socialParameter: (json['social_coeff'] ?? json['social_parameter'] ?? 1.5).toDouble(),
      velocityClamp: (json['velocity_clamp'] ?? 0.2).toDouble(),
      topologyType: json['pso_topology'] ?? json['topology_type'] ?? 'gbest',
      variant: json['pso_variant'] ?? json['variant'] ?? 'standard',
      constrictionFactor: (json['constriction_factor'] ?? 0.729).toDouble(),
      neighborhoodSize: json['neighborhood_size'] ?? 3,
      earlyStoppingEnabled: json['early_stopping'] ?? json['early_stopping_enabled'] ?? true,
      earlyStoppingPatience: json['patience'] ?? json['early_stopping_patience'] ?? 10,
      fitnessThreshold: (json['fitness_threshold'] ?? 0.85).toDouble() * (json['fitness_threshold'] != null && json['fitness_threshold'] <= 1.0 ? 100.0 : 1.0),
      trackProgress: json['track_progress'] ?? false,
      healthySampleSize: json['healthy_sample_size'],
    );
  }

  PSOConfigModel copyWith({
    int? swarmSize,
    int? iterations,
    double? inertiaWeight,
    double? inertiaMin,
    double? inertiaMax,
    double? cognitiveParameter,
    double? socialParameter,
    double? velocityClamp,
    String? topologyType,
    String? variant,
    double? constrictionFactor,
    int? neighborhoodSize,
    bool? earlyStoppingEnabled,
    int? earlyStoppingPatience,
    double? fitnessThreshold,
    int? healthySampleSize,
    bool? trackProgress,
  }) {
    return PSOConfigModel(
      swarmSize: swarmSize ?? this.swarmSize,
      iterations: iterations ?? this.iterations,
      inertiaWeight: inertiaWeight ?? this.inertiaWeight,
      inertiaMin: inertiaMin ?? this.inertiaMin,
      inertiaMax: inertiaMax ?? this.inertiaMax,
      cognitiveParameter: cognitiveParameter ?? this.cognitiveParameter,
      socialParameter: socialParameter ?? this.socialParameter,
      velocityClamp: velocityClamp ?? this.velocityClamp,
      topologyType: topologyType ?? this.topologyType,
      variant: variant ?? this.variant,
      constrictionFactor: constrictionFactor ?? this.constrictionFactor,
      neighborhoodSize: neighborhoodSize ?? this.neighborhoodSize,
      earlyStoppingEnabled: earlyStoppingEnabled ?? this.earlyStoppingEnabled,
      earlyStoppingPatience: earlyStoppingPatience ?? this.earlyStoppingPatience,
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

  /// Topology types for PSO
  static const List<String> topologyTypes = [
    'gbest',      // Global best - all particles connected
    'lbest',      // Local best - ring topology
    'ring',       // Ring topology (alias for lbest)
    'random',     // Random neighbors
    'von_neumann' // 2D grid topology
  ];

  /// Topology display names
  static const Map<String, String> topologyDisplayNames = {
    'gbest': 'Global Best (Star)',
    'lbest': 'Local Best (Ring)',
    'ring': 'Ring Topology',
    'random': 'Random Neighbors',
    'von_neumann': 'Von Neumann (Grid)',
  };

  /// PSO variants
  static const List<String> variants = [
    'standard',      // Classic PSO with inertia weight
    'constriction',  // Clerc's constriction factor
    'inertia_decay', // Linear inertia weight decay
  ];

  /// Variant display names
  static const Map<String, String> variantDisplayNames = {
    'standard': 'Standard PSO',
    'constriction': 'Constriction Factor PSO',
    'inertia_decay': 'Inertia Decay PSO',
  };

  /// Get preset configurations
  static PSOConfigModel getPreset(String presetName) {
    switch (presetName) {
      case 'fast':
        return PSOConfigModel(
          swarmSize: 20,
          iterations: 30,
          inertiaWeight: 0.8,
          cognitiveParameter: 1.5,
          socialParameter: 1.5,
          topologyType: 'gbest',
          variant: 'standard',
          earlyStoppingPatience: 5,
        );
      case 'balanced':
        return PSOConfigModel(
          swarmSize: 30,
          iterations: 100,
          inertiaWeight: 0.7,
          cognitiveParameter: 1.5,
          socialParameter: 1.5,
          topologyType: 'gbest',
          variant: 'standard',
          earlyStoppingPatience: 10,
        );
      case 'quality':
        return PSOConfigModel(
          swarmSize: 50,
          iterations: 200,
          inertiaWeight: 0.6,
          cognitiveParameter: 1.4,
          socialParameter: 1.6,
          topologyType: 'lbest',
          variant: 'constriction',
          earlyStoppingPatience: 15,
        );
      default:
        return PSOConfigModel();
    }
  }
}

/// ============================================================================
/// DIFFERENTIAL EVOLUTION (DE) CONFIGURATION
/// ============================================================================

class DEConfigModel extends EvolutionaryConfigBase {
  final int populationSize;
  final int generations;
  final double scaleFactor; // F: [0, 2], controls mutation magnitude
  final double crossoverRate; // CR: [0, 1], probability of parameter selection
  final String mutationStrategy; // All 6 DE mutation strategies
  final String crossoverType; // binomial or exponential
  final bool adaptiveF; // Self-adaptive F parameter
  final bool adaptiveCR; // Self-adaptive CR parameter
  final double fMin; // Minimum F for adaptive
  final double fMax; // Maximum F for adaptive
  final double crMin; // Minimum CR for adaptive
  final double crMax; // Maximum CR for adaptive
  final double adaptationRate; // Learning rate for adaptive parameters
  final bool earlyStoppingEnabled;
  final int earlyStoppingPatience;

  DEConfigModel({
    int populationSize = 30,
    int generations = 100,
    double scaleFactor = 0.8,
    double crossoverRate = 0.9,
    String mutationStrategy = 'DE/rand/1',
    String crossoverType = 'binomial',
    bool adaptiveF = false,
    bool adaptiveCR = false,
    double fMin = 0.1,
    double fMax = 1.0,
    double crMin = 0.1,
    double crMax = 1.0,
    double adaptationRate = 0.1,
    bool earlyStoppingEnabled = true,
    int earlyStoppingPatience = 10,
    double fitnessThreshold = 85.0,
    int? healthySampleSize,
    bool trackProgress = false,
  })  : populationSize = populationSize,
        generations = generations,
        scaleFactor = scaleFactor,
        crossoverRate = crossoverRate,
        mutationStrategy = mutationStrategy,
        crossoverType = crossoverType,
        adaptiveF = adaptiveF,
        adaptiveCR = adaptiveCR,
        fMin = fMin,
        fMax = fMax,
        crMin = crMin,
        crMax = crMax,
        adaptationRate = adaptationRate,
        earlyStoppingEnabled = earlyStoppingEnabled,
        earlyStoppingPatience = earlyStoppingPatience,
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
      'de_mutation_strategy': mutationStrategy,
      'de_crossover_type': crossoverType,
      'adaptive_f': adaptiveF,
      'adaptive_cr': adaptiveCR,
      'f_min': fMin,
      'f_max': fMax,
      'cr_min': crMin,
      'cr_max': crMax,
      'adaptation_rate': adaptationRate,
      'early_stopping': earlyStoppingEnabled,
      'patience': earlyStoppingPatience,
      'fitness_threshold': fitnessThreshold / 100.0, // Convert to 0-1 range
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
      mutationStrategy: json['de_mutation_strategy'] ?? json['mutation_strategy'] ?? 'DE/rand/1',
      crossoverType: json['de_crossover_type'] ?? json['crossover_type'] ?? 'binomial',
      adaptiveF: json['adaptive_f'] ?? false,
      adaptiveCR: json['adaptive_cr'] ?? false,
      fMin: (json['f_min'] ?? 0.1).toDouble(),
      fMax: (json['f_max'] ?? 1.0).toDouble(),
      crMin: (json['cr_min'] ?? 0.1).toDouble(),
      crMax: (json['cr_max'] ?? 1.0).toDouble(),
      adaptationRate: (json['adaptation_rate'] ?? 0.1).toDouble(),
      earlyStoppingEnabled: json['early_stopping'] ?? json['early_stopping_enabled'] ?? true,
      earlyStoppingPatience: json['patience'] ?? json['early_stopping_patience'] ?? 10,
      fitnessThreshold: (json['fitness_threshold'] ?? 0.85).toDouble() * (json['fitness_threshold'] != null && json['fitness_threshold'] <= 1.0 ? 100.0 : 1.0),
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
    String? crossoverType,
    bool? adaptiveF,
    bool? adaptiveCR,
    double? fMin,
    double? fMax,
    double? crMin,
    double? crMax,
    double? adaptationRate,
    bool? earlyStoppingEnabled,
    int? earlyStoppingPatience,
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
      crossoverType: crossoverType ?? this.crossoverType,
      adaptiveF: adaptiveF ?? this.adaptiveF,
      adaptiveCR: adaptiveCR ?? this.adaptiveCR,
      fMin: fMin ?? this.fMin,
      fMax: fMax ?? this.fMax,
      crMin: crMin ?? this.crMin,
      crMax: crMax ?? this.crMax,
      adaptationRate: adaptationRate ?? this.adaptationRate,
      earlyStoppingEnabled: earlyStoppingEnabled ?? this.earlyStoppingEnabled,
      earlyStoppingPatience: earlyStoppingPatience ?? this.earlyStoppingPatience,
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

  /// All 6 DE mutation strategies
  static const List<String> mutationStrategies = [
    'DE/rand/1',           // v = x_r1 + F*(x_r2 - x_r3) - Exploration
    'DE/rand/2',           // v = x_r1 + F*(x_r2 - x_r3) + F*(x_r4 - x_r5) - Strong exploration
    'DE/best/1',           // v = x_best + F*(x_r1 - x_r2) - Exploitation
    'DE/best/2',           // v = x_best + F*(x_r1 - x_r2) + F*(x_r3 - x_r4) - Strong exploitation
    'DE/current-to-best/1', // v = x_i + F*(x_best - x_i) + F*(x_r1 - x_r2) - Balanced
    'DE/current-to-rand/1', // v = x_i + F*(x_r1 - x_i) + F*(x_r2 - x_r3) - Explorative balance
  ];

  /// Mutation strategy display names
  static const Map<String, String> mutationStrategyDisplayNames = {
    'DE/rand/1': 'DE/rand/1 (Exploration)',
    'DE/rand/2': 'DE/rand/2 (Strong Exploration)',
    'DE/best/1': 'DE/best/1 (Exploitation)',
    'DE/best/2': 'DE/best/2 (Strong Exploitation)',
    'DE/current-to-best/1': 'DE/current-to-best/1 (Balanced)',
    'DE/current-to-rand/1': 'DE/current-to-rand/1 (Explorative Balance)',
  };

  /// Crossover types
  static const List<String> crossoverTypes = [
    'binomial',    // Standard binomial crossover
    'exponential', // Exponential crossover
  ];

  /// Crossover type display names
  static const Map<String, String> crossoverTypeDisplayNames = {
    'binomial': 'Binomial (Standard)',
    'exponential': 'Exponential',
  };

  /// Get preset configurations
  static DEConfigModel getPreset(String presetName) {
    switch (presetName) {
      case 'fast':
        return DEConfigModel(
          populationSize: 20,
          generations: 30,
          scaleFactor: 0.8,
          crossoverRate: 0.9,
          mutationStrategy: 'DE/best/1',
          crossoverType: 'binomial',
          adaptiveF: false,
          adaptiveCR: false,
          earlyStoppingPatience: 5,
        );
      case 'balanced':
        return DEConfigModel(
          populationSize: 30,
          generations: 100,
          scaleFactor: 0.8,
          crossoverRate: 0.9,
          mutationStrategy: 'DE/rand/1',
          crossoverType: 'binomial',
          adaptiveF: false,
          adaptiveCR: false,
          earlyStoppingPatience: 10,
        );
      case 'quality':
        return DEConfigModel(
          populationSize: 50,
          generations: 200,
          scaleFactor: 0.7,
          crossoverRate: 0.85,
          mutationStrategy: 'DE/current-to-best/1',
          crossoverType: 'binomial',
          adaptiveF: true,
          adaptiveCR: true,
          earlyStoppingPatience: 15,
        );
      default:
        return DEConfigModel();
    }
  }
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

  static const Map<String, String> selectionTypeDisplayNames = {
    'plus': '(μ+λ) Plus Selection',
    'comma': '(μ,λ) Comma Selection',
  };

  static const List<String> recombinationTypes = [
    'discrete',
    'intermediate',
    'global'
  ];

  static const Map<String, String> recombinationTypeDisplayNames = {
    'discrete': 'Discrete Recombination',
    'intermediate': 'Intermediate Recombination',
    'global': 'Global Recombination',
  };

  /// Get preset configurations
  static ESConfigModel getPreset(String presetName) {
    switch (presetName) {
      case 'fast':
        return ESConfigModel(
          populationSize: 15,
          offspringSize: 45,
          generations: 30,
          selectionType: 'plus',
          initialMutationRate: 0.15,
          selfAdaptiveMutation: true,
          learningRate: 0.15,
          recombinationType: 'intermediate',
          parentCount: 2,
        );
      case 'balanced':
        return ESConfigModel(
          populationSize: 20,
          offspringSize: 60,
          generations: 100,
          selectionType: 'plus',
          initialMutationRate: 0.1,
          selfAdaptiveMutation: true,
          learningRate: 0.1,
          recombinationType: 'intermediate',
          parentCount: 2,
        );
      case 'quality':
        return ESConfigModel(
          populationSize: 30,
          offspringSize: 100,
          generations: 200,
          selectionType: 'comma',
          initialMutationRate: 0.08,
          selfAdaptiveMutation: true,
          learningRate: 0.08,
          recombinationType: 'global',
          parentCount: 3,
        );
      default:
        return ESConfigModel();
    }
  }
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
