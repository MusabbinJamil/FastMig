import 'package:flutter/material.dart';
import '../models/ga_config_model.dart';
import '../services/api_service.dart';
import '../widgets/ga_configuration_panel.dart';
import '../widgets/ga_progress_visualization.dart';

class GAEvolutionScreen extends StatefulWidget {
  const GAEvolutionScreen({Key? key}) : super(key: key);

  @override
  State<GAEvolutionScreen> createState() => _GAEvolutionScreenState();
}

class _GAEvolutionScreenState extends State<GAEvolutionScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late GAConfigModel _gaConfig;

  bool _isEvolving = false;
  double _evolutionProgress = 0.0;
  List<GAMetricsModel> _metricsHistory = [];
  Map<String, dynamic>? _fitnessAnalysis;
  String? _errorMessage;

  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _gaConfig = GAConfigModel();
    _loadFitnessAnalysis();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadFitnessAnalysis() async {
    try {
      final analysis = await _apiService.analyzePopulationFitness(
        fitnessThreshold: _gaConfig.fitnessThreshold,
      );
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
    setState(() {
      _isEvolving = true;
      _evolutionProgress = 0.0;
      _metricsHistory = [];
      _errorMessage = null;
    });

    try {
      // Switch to progress tab
      _tabController.animateTo(1);

      // Run GA evolution
      final result = await _apiService.runGeneticAlgorithmEvolution(
        gaConfig: _gaConfig.toJson(),
        trackProgress: true,
      );

      // Process fitness history
      if (result['fitness_history'] is List) {
        final metricsHistory = (result['fitness_history'] as List)
            .map((m) => GAMetricsModel.fromJson(m))
            .toList();
        setState(() {
          _metricsHistory = metricsHistory;
          _evolutionProgress = 1.0;
        });
      }

      setState(() {
        _isEvolving = false;
      });

      // Show success snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('GA Evolution completed successfully!'),
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

  Future<void> _quickEvolve() async {
    setState(() {
      _isEvolving = true;
      _evolutionProgress = 0.0;
      _metricsHistory = [];
      _errorMessage = null;
    });

    try {
      // Switch to progress tab
      _tabController.animateTo(1);

      // Call quick evolve endpoint
      final result = await _apiService.quickEvolve(
        fitnessThreshold: 85.0,
        populationSize: 20,
        generations: 30,
        saveResult: true,
      );

      // Process fitness history
      if (result['fitness_history'] is List) {
        final metricsHistory = (result['fitness_history'] as List)
            .map((m) => GAMetricsModel.fromJson(m))
            .toList();
        setState(() {
          _metricsHistory = metricsHistory;
          _evolutionProgress = 1.0;
        });
      }

      setState(() {
        _isEvolving = false;
      });

      // Show success snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
                'Quick Evolution completed! Best fitness: ${(result["best_fitness"] as num?)?.toStringAsFixed(2) ?? "N/A"}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isEvolving = false;
        _errorMessage = 'Quick evolution failed: $e';
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Genetic Algorithm Evolution'),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(
              icon: Icon(Icons.settings),
              text: 'Configuration',
            ),
            Tab(
              icon: Icon(Icons.show_chart),
              text: 'Progress',
            ),
            Tab(
              icon: Icon(Icons.analytics),
              text: 'Analysis',
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // ===== Configuration Tab =====
          _buildConfigurationTab(),

          // ===== Progress Tab =====
          _buildProgressTab(),

          // ===== Analysis Tab =====
          _buildAnalysisTab(),
        ],
      ),
    );
  }

  Widget _buildConfigurationTab() {
    return SingleChildScrollView(
      child: Column(
        children: [
          DefaultTabController(
            length: 1,
            child: Column(
              children: [
                SizedBox(
                  height: 400,
                  child: GAConfigurationPanel(
                    initialConfig: _gaConfig,
                    onConfigChanged: (config) {
                      setState(() => _gaConfig = config);
                    },
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // Summary
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Configuration Summary',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 12),
                        _buildConfigSummaryRow(
                          'Population Size',
                          '${_gaConfig.populationSize}',
                        ),
                        _buildConfigSummaryRow(
                          'Generations',
                          '${_gaConfig.generations}',
                        ),
                        _buildConfigSummaryRow(
                          'Mutation Rate',
                          '${(_gaConfig.mutationRate * 100).toStringAsFixed(1)}%',
                        ),
                        _buildConfigSummaryRow(
                          'Crossover Rate',
                          '${(_gaConfig.crossoverRate * 100).toStringAsFixed(1)}%',
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.play_circle),
                    label: const Text('Start Evolution'),
                    onPressed: _isEvolving ? null : _startEvolution,
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.bolt),
                    label: const Text('Quick Evolve (Optimized Defaults)'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green.shade700,
                      foregroundColor: Colors.white,
                    ),
                    onPressed: _isEvolving ? null : _quickEvolve,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // Metrics Summary
          if (_metricsHistory.isNotEmpty) ...[
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Evolution Summary',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    _buildStatRow(
                      'Current Generation',
                      '${_metricsHistory.length}',
                      Colors.blue,
                    ),
                    _buildStatRow(
                      'Best Fitness',
                      _metricsHistory.last.bestFitness.toStringAsFixed(2),
                      Colors.green,
                    ),
                    _buildStatRow(
                      'Average Fitness',
                      _metricsHistory.last.averageFitness.toStringAsFixed(2),
                      Colors.orange,
                    ),
                    _buildStatRow(
                      'Worst Fitness',
                      _metricsHistory.last.worstFitness.toStringAsFixed(2),
                      Colors.red,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Progress Visualization
          GAProgressVisualization(
            metricsHistory: _metricsHistory,
            isRunning: _isEvolving,
            progressPercent: _evolutionProgress,
            onStop: _stopEvolution,
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_errorMessage != null) ...[
            Card(
              color: Colors.red[50],
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(_errorMessage!),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
          if (_fitnessAnalysis != null) ...[
            Text(
              'Population Fitness Analysis',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),

            // Summary Card
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Overview',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
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
            ),
            const SizedBox(height: 16),

            // Statistics Card
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Fitness Statistics',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    _buildStatRow(
                      'Average Fitness',
                      (_fitnessAnalysis!['average_fitness'] as num?)
                              ?.toStringAsFixed(2) ??
                          'N/A',
                      Colors.orange,
                    ),
                    _buildStatRow(
                      'Min Fitness',
                      (_fitnessAnalysis!['min_fitness'] as num?)
                              ?.toStringAsFixed(2) ??
                          'N/A',
                      Colors.red,
                    ),
                    _buildStatRow(
                      'Max Fitness',
                      (_fitnessAnalysis!['max_fitness'] as num?)
                              ?.toStringAsFixed(2) ??
                          'N/A',
                      Colors.green,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Distribution Card
            if (_fitnessAnalysis!['fitness_distribution'] != null) ...[
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Fitness Distribution',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 12),
                      _buildFitnessDistribution(
                        _fitnessAnalysis!['fitness_distribution']
                            as Map<String, dynamic>,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Action Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: const Text('Reload Analysis'),
                onPressed: _loadFitnessAnalysis,
              ),
            ),
            const SizedBox(height: 16),

            // Export Section (if evolution was run)
            if (_metricsHistory.isNotEmpty) ...[
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Export Evolved Data',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'After evolution, you can export and load the improved data as your main dataset.',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          ElevatedButton.icon(
                            icon: const Icon(Icons.download),
                            label: const Text('Export as CSV'),
                            onPressed: () => _exportEvolvedData('csv'),
                          ),
                          ElevatedButton.icon(
                            icon: const Icon(Icons.download),
                            label: const Text('Export as JSON'),
                            onPressed: () => _exportEvolvedData('json'),
                          ),
                          ElevatedButton.icon(
                            icon: const Icon(Icons.upload_file),
                            label: const Text('Load to Main Screen'),
                            onPressed: _loadEvolvedDataToMain,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ] else
            Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    Icon(Icons.analytics, size: 48, color: Colors.grey),
                    const SizedBox(height: 16),
                    const Text('No analysis data available'),
                    const SizedBox(height: 16),
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

  Widget _buildConfigSummaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
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

  Widget _buildStatRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
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

  Widget _buildFitnessDistribution(Map<String, dynamic> distribution) {
    final entries = distribution.entries.toList();
    if (entries.isEmpty) {
      return const Text('No distribution data available');
    }

    return Column(
      children: entries.map((entry) {
        final count = entry.value as int;
        final maxCount =
            entries.map((e) => e.value as int).reduce((a, b) => a > b ? a : b);
        final percentage = ((count / maxCount) * 100).toStringAsFixed(1);
        final barWidth = (count / maxCount.toDouble()) * 200;

        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Row(
            children: [
              SizedBox(
                width: 80,
                child: Text(
                  entry.key,
                  style: Theme.of(context).textTheme.bodySmall,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                height: 20,
                width: barWidth,
                decoration: BoxDecoration(
                  color: Colors.blue,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(width: 8),
              Text('$count ($percentage%)',
                  style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        );
      }).toList(),
    );
  }

  /// Export evolved data to file
  Future<void> _exportEvolvedData(String format) async {
    try {
      if (_metricsHistory.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No evolution data to export'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      final result = await _apiService.exportEvolvedData(
        filename: 'evolved_data_${DateTime.now().millisecondsSinceEpoch}',
        format: format,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✓ Data exported: ${result['filename']}'),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Export failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Load evolved data back to main screen
  Future<void> _loadEvolvedDataToMain() async {
    try {
      if (_metricsHistory.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No evolution data to load'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      // First export the data so it's available
      final exportResult = await _apiService.exportEvolvedData(
        filename: 'evolved_data_main',
        format: 'csv',
      );

      if (mounted) {
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '✓ Evolved data exported and ready. File: ${exportResult['filename']}',
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 4),
          ),
        );

        // Pop back to main screen
        Navigator.of(context).pop();
      }
    } catch (e) {
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
}
