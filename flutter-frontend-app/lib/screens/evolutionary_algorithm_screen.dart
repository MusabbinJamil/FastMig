import 'package:flutter/material.dart';
import '../models/evolutionary_config_models.dart';
import '../services/api_service.dart';
import '../widgets/evolutionary_config_panels.dart';
import '../widgets/ga_progress_visualization.dart';

/// Comprehensive Evolution Configuration & Execution Screen
/// Supports: GA, PSO, Differential Evolution, Evolution Strategy, Hybrid
class EvolutionaryAlgorithmScreen extends StatefulWidget {
  const EvolutionaryAlgorithmScreen({Key? key}) : super(key: key);

  @override
  State<EvolutionaryAlgorithmScreen> createState() =>
      _EvolutionaryAlgorithmScreenState();
}

class _EvolutionaryAlgorithmScreenState
    extends State<EvolutionaryAlgorithmScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late TabController _methodTabController;

  // Current method selection
  String _selectedMethod = 'hybrid';
  EvolutionaryConfigBase _currentConfig = HybridConfigModel();

  // Configs for each method (cached)
  late Map<String, EvolutionaryConfigBase> _methodConfigs;

  // Evolution state
  bool _isEvolving = false;
  double _evolutionProgress = 0.0;
  List<Map<String, dynamic>> _metricsHistory = [];
  Map<String, dynamic>? _fitnessAnalysis;
  Map<String, dynamic>? _lastEvolutionResult;
  String? _errorMessage;

  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _methodTabController = TabController(length: 5, vsync: this);

    // Initialize configs for all methods
    _methodConfigs = {
      'ga': GAConfigModel(),
      'pso': PSOConfigModel(),
      'de': DEConfigModel(),
      'es': ESConfigModel(),
      'hybrid': HybridConfigModel(),
    };

    _currentConfig = _methodConfigs['hybrid']!;
    _loadFitnessAnalysis();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _methodTabController.dispose();
    super.dispose();
  }

  void _setMethod(String method) {
    setState(() {
      _selectedMethod = method;
      _currentConfig = _methodConfigs[method]!;
      _methodTabController.index = _methodIndex(method);
    });
  }

  int _methodIndex(String method) {
    const methods = ['ga', 'pso', 'de', 'es', 'hybrid'];
    return methods.indexOf(method);
  }

  void _updateMethodConfig(EvolutionaryConfigBase config) {
    setState(() {
      _methodConfigs[_selectedMethod] = config;
      _currentConfig = config;
    });
  }

  Future<void> _loadFitnessAnalysis() async {
    try {
      final threshold = _currentConfig.fitnessThreshold;
      final analysis =
          await _apiService.analyzePopulationFitness(fitnessThreshold: threshold);
      setState(() {
        _fitnessAnalysis = analysis;
        _errorMessage = null;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to analyze fitness: $e';
        _fitnessAnalysis = null;
      });
    }
  }

  Future<void> _startEvolution() async {
    if (_selectedMethod.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select an evolutionary method'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isEvolving = true;
      _evolutionProgress = 0.0;
      _metricsHistory = [];
      _errorMessage = null;
      _lastEvolutionResult = null;
    });

    try {
      _tabController.animateTo(1);

      // Call the appropriate endpoint based on method
      Map<String, dynamic> result;

      switch (_selectedMethod.toLowerCase()) {
        case 'ga':
          result = await _apiService.runEvolutionaryMethod(
            method: 'ga',
            config: (_currentConfig as GAConfigModel).toJson(),
          );
          break;
        case 'pso':
          result = await _apiService.runEvolutionaryMethod(
            method: 'pso',
            config: (_currentConfig as PSOConfigModel).toJson(),
          );
          break;
        case 'de':
          result = await _apiService.runEvolutionaryMethod(
            method: 'de',
            config: (_currentConfig as DEConfigModel).toJson(),
          );
          break;
        case 'es':
          result = await _apiService.runEvolutionaryMethod(
            method: 'es',
            config: (_currentConfig as ESConfigModel).toJson(),
          );
          break;
        case 'hybrid':
          result = await _apiService.runEvolutionaryMethod(
            method: 'hybrid',
            config: (_currentConfig as HybridConfigModel).toJson(),
          );
          break;
        default:
          throw Exception('Unknown method: $_selectedMethod');
      }

      // Process fitness history
      if (result['fitness_history'] is List) {
        final history = result['fitness_history'] as List;
        setState(() {
          _metricsHistory = history.cast<Map<String, dynamic>>();
          _evolutionProgress = 1.0;
          _lastEvolutionResult = result;
        });
      }

      setState(() {
        _isEvolving = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '✓ ${_selectedMethod.toUpperCase()} Evolution completed!',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isEvolving = false;
        _errorMessage = 'Evolution failed: $e';
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _stopEvolution() {
    setState(() {
      _isEvolving = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final methodInfo = _getMethodInfo(_selectedMethod);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Evolutionary Algorithm Configuration'),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.settings), text: 'Configuration'),
            Tab(icon: Icon(Icons.show_chart), text: 'Progress'),
            Tab(icon: Icon(Icons.analytics), text: 'Analysis'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildConfigurationTab(),
          _buildProgressTab(),
          _buildAnalysisTab(),
        ],
      ),
    );
  }

  Widget _buildConfigurationTab() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Method Selector
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Select Evolutionary Method',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                _buildMethodSelector(),
              ],
            ),
          ),
          Divider(height: 1, color: Colors.grey.shade300),
          const SizedBox(height: 16),

          // Method-Specific Configuration Panel
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: _buildConfigurationPanel(),
          ),

          // Configuration Summary
          Padding(
            padding: const EdgeInsets.all(16),
            child: _buildConfigurationSummary(),
          ),

          // Action Buttons
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.play_circle),
                    label: Text('Start ${_selectedMethod.toUpperCase()} Evolution'),
                    onPressed: _isEvolving ? null : _startEvolution,
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.refresh),
                    label: Text('Reset ${_selectedMethod.toUpperCase()} Config'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.grey,
                    ),
                    onPressed: () => _resetMethodConfig(_selectedMethod),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMethodSelector() {
    final methods = [
      ('ga', '🧬', 'Genetic Algorithm', 'Selection, Crossover, Mutation'),
      ('pso', '🐦', 'Particle Swarm', 'Swarm intelligence for numeric data'),
      ('de', '⚡', 'Differential Evo', 'Robust global optimization'),
      ('es', '🔄', 'Evolution Strategy', 'Self-adaptive mutation'),
      ('hybrid', '🚀', 'Hybrid', 'Auto-select best per column'),
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: methods
            .map(
              (method) => Padding(
                padding: const EdgeInsets.only(right: 8),
                child: _buildMethodCard(
                  method.$1,
                  method.$2,
                  method.$3,
                  method.$4,
                ),
              ),
            )
            .toList(),
      ),
    );
  }

  Widget _buildMethodCard(
    String id,
    String icon,
    String name,
    String description,
  ) {
    final isSelected = _selectedMethod == id;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _setMethod(id),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: 180,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            border: Border.all(
              color: isSelected ? Colors.blue : Colors.grey.shade300,
              width: isSelected ? 2 : 1,
            ),
            borderRadius: BorderRadius.circular(12),
            color:
                isSelected ? Colors.blue.withOpacity(0.05) : Colors.transparent,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                icon,
                style: const TextStyle(fontSize: 24),
              ),
              const SizedBox(height: 8),
              Text(
                name,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isSelected ? Colors.blue : Colors.black,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey,
                      fontSize: 10,
                    ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              if (isSelected)
                Align(
                  alignment: Alignment.centerRight,
                  child: Icon(Icons.check_circle, color: Colors.blue),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildConfigurationPanel() {
    switch (_selectedMethod) {
      case 'ga':
        return GAConfigurationPanel(
          config: _currentConfig as GAConfigModel,
          onConfigChanged: (config) =>
              _updateMethodConfig(config as EvolutionaryConfigBase),
        );
      case 'pso':
        return PSOConfigurationPanel(
          config: _currentConfig as PSOConfigModel,
          onConfigChanged: (config) =>
              _updateMethodConfig(config as EvolutionaryConfigBase),
        );
      case 'de':
        return DEConfigurationPanel(
          config: _currentConfig as DEConfigModel,
          onConfigChanged: (config) =>
              _updateMethodConfig(config as EvolutionaryConfigBase),
        );
      case 'es':
        return ESConfigurationPanel(
          config: _currentConfig as ESConfigModel,
          onConfigChanged: (config) =>
              _updateMethodConfig(config as EvolutionaryConfigBase),
        );
      case 'hybrid':
        return HybridConfigurationPanel(
          config: _currentConfig as HybridConfigModel,
          onConfigChanged: (config) =>
              _updateMethodConfig(config as EvolutionaryConfigBase),
        );
      default:
        return const Center(child: Text('Unknown method'));
    }
  }

  Widget _buildConfigurationSummary() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Configuration Summary',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildSummaryItem(
              'Method',
              _selectedMethod.toUpperCase(),
              Colors.blue,
            ),
            _buildSummaryItem(
              'Max Iterations',
              '${_currentConfig.maxIterations}',
              Colors.green,
            ),
            _buildSummaryItem(
              'Fitness Threshold',
              '${_currentConfig.fitnessThreshold.toStringAsFixed(1)}%',
              Colors.orange,
            ),
            _buildSummaryItem(
              'Track Progress',
              _currentConfig.trackProgress ? 'Enabled' : 'Disabled',
              _currentConfig.trackProgress ? Colors.green : Colors.grey,
            ),
            if (_currentConfig.healthySampleSize != null)
              _buildSummaryItem(
                'Healthy Sample Size',
                '${_currentConfig.healthySampleSize}',
                Colors.teal,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              border: Border.all(color: color),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          if (_metricsHistory.isNotEmpty) ...[
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${_selectedMethod.toUpperCase()} Evolution Summary',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 16),
                    _buildStatRow(
                      'Current Generation',
                      '${_metricsHistory.length}',
                      Colors.blue,
                    ),
                    if (_metricsHistory.isNotEmpty) ...[
                      _buildStatRow(
                        'Best Fitness',
                        (_lastEvolutionResult?['best_fitness'] as num?)
                                ?.toStringAsFixed(2) ??
                            'N/A',
                        Colors.green,
                      ),
                      _buildStatRow(
                        'Average Fitness',
                        (_metricsHistory.last['average_fitness'] as num?)
                                ?.toStringAsFixed(2) ??
                            'N/A',
                        Colors.orange,
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Fitness Progress Chart',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            _buildFitnessProgressChart(),
            const SizedBox(height: 16),
          ] else
            Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  children: [
                    Icon(
                      Icons.show_chart,
                      size: 64,
                      color: Colors.grey.shade300,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'No evolution data yet',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Run an evolution to see progress here',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  ],
                ),
              ),
            ),
          if (_isEvolving)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  LinearProgressIndicator(
                    value: _evolutionProgress,
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.stop),
                    label: const Text('Stop Evolution'),
                    onPressed: _stopEvolution,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildFitnessProgressChart() {
    if (_metricsHistory.isEmpty) {
      return const Center(
        child: Text('No data to display'),
      );
    }

    final maxFitness = _metricsHistory
        .map((m) => (m['best_fitness'] as num).toDouble())
        .reduce((a, b) => a > b ? a : b);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          height: 300,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
            color: Colors.white,
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: List.generate(
              (_metricsHistory.length / 10).ceil().clamp(1, 5).toInt(),
              (index) {
                final startIdx = index * (_metricsHistory.length ~/
                    ((_metricsHistory.length / 10).ceil().clamp(1, 5).toInt() +
                        1));
                final endIdx = ((index + 1) *
                        (_metricsHistory.length ~/
                            ((_metricsHistory.length / 10)
                                .ceil()
                                .clamp(1, 5)
                                .toInt() +
                                1)))
                    .clamp(0, _metricsHistory.length);

                if (startIdx >= _metricsHistory.length) {
                  return const SizedBox.shrink();
                }

                return Row(
                  children: List.generate(
                    10,
                    (i) {
                      final idx = startIdx + i;
                      if (idx >= _metricsHistory.length) {
                        return Expanded(child: Container());
                      }

                      final fitness =
                          (_metricsHistory[idx]['best_fitness'] as num)
                              .toDouble();
                      final height = (fitness / maxFitness) * 200;

                      return Expanded(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            Container(
                              height: height.clamp(2, 200).toDouble(),
                              decoration: BoxDecoration(
                                color: Colors.blue.withOpacity(0.7),
                                borderRadius: BorderRadius.circular(2),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          'Generation Progress',
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.grey,
              ),
        ),
      ],
    );
  }

  Widget _buildAnalysisTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_errorMessage != null) ...[
            Card(
              color: Colors.red[50],
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(child: Text(_errorMessage!)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
          if (_fitnessAnalysis != null) ...[
            Text(
              'Population Fitness Analysis',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildAnalysisOverview(),
            const SizedBox(height: 16),
            _buildFitnessStatistics(),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: const Text('Reload Analysis'),
                onPressed: _loadFitnessAnalysis,
              ),
            ),
          ] else
            Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  children: [
                    Icon(
                      Icons.analytics,
                      size: 64,
                      color: Colors.grey.shade300,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'No analysis data available',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _loadFitnessAnalysis,
                      child: const Text('Load Analysis'),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildAnalysisOverview() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Population Overview',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildAnalysisRow(
              'Total Records',
              '${_fitnessAnalysis!['total_records'] ?? 0}',
              Colors.blue,
            ),
            _buildAnalysisRow(
              'Healthy Records',
              '${_fitnessAnalysis!['healthy_records'] ?? 0} (${(_fitnessAnalysis!['healthy_percentage'] as num?)?.toStringAsFixed(1) ?? '0'}%)',
              Colors.green,
            ),
            _buildAnalysisRow(
              'Unhealthy Records',
              '${_fitnessAnalysis!['unhealthy_records'] ?? 0} (${(_fitnessAnalysis!['unhealthy_percentage'] as num?)?.toStringAsFixed(1) ?? '0'}%)',
              Colors.red,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFitnessStatistics() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Fitness Statistics',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            _buildStatRow(
              'Average Fitness',
              (_fitnessAnalysis!['average_fitness'] as num?)
                      ?.toStringAsFixed(2) ??
                  'N/A',
              Colors.orange,
            ),
            _buildStatRow(
              'Min Fitness',
              (_fitnessAnalysis!['min_fitness'] as num?)?.toStringAsFixed(2) ??
                  'N/A',
              Colors.red,
            ),
            _buildStatRow(
              'Max Fitness',
              (_fitnessAnalysis!['max_fitness'] as num?)?.toStringAsFixed(2) ??
                  'N/A',
              Colors.green,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              border: Border.all(color: color),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              border: Border.all(color: color),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _resetMethodConfig(String method) {
    setState(() {
      _methodConfigs[method] = _getDefaultConfig(method);
      _currentConfig = _methodConfigs[method]!;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$method configuration reset to defaults'),
        backgroundColor: Colors.blue,
      ),
    );
  }

  EvolutionaryConfigBase _getDefaultConfig(String method) {
    switch (method) {
      case 'ga':
        return GAConfigModel();
      case 'pso':
        return PSOConfigModel();
      case 'de':
        return DEConfigModel();
      case 'es':
        return ESConfigModel();
      case 'hybrid':
        return HybridConfigModel();
      default:
        return HybridConfigModel();
    }
  }

  Map<String, String> _getMethodInfo(String method) {
    const info = {
      'ga': 'Genetic Algorithm - Evolution through selection, crossover, mutation',
      'pso':
          'Particle Swarm Optimization - Best for numeric continuous values',
      'de':
          'Differential Evolution - Robust global optimization strategy',
      'es':
          'Evolution Strategy - Self-adaptive mutation rates',
      'hybrid': 'Hybrid - Auto-selects best algorithm per column type',
    };
    return {'description': info[method] ?? ''};
  }
}
