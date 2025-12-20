import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';
import 'sensitive_data_warning.dart';

class EvolutionaryCleaningSection extends StatefulWidget {
  const EvolutionaryCleaningSection({Key? key}) : super(key: key);

  @override
  State<EvolutionaryCleaningSection> createState() =>
      _EvolutionaryCleaningSectionState();
}

class _EvolutionaryCleaningSectionState
    extends State<EvolutionaryCleaningSection> {
  String _selectedMethod = 'hybrid';
  bool _trackModifications = true;
  bool _isCleaning = false;
  bool _isComparing = false;
  bool _isLoadingSensitiveColumns = false;
  bool _isQuickEvolving = false;
  Map<String, dynamic>? _cleaningReport;
  Map<String, dynamic>? _comparisonResults;
  Map<String, dynamic>? _sensitiveColumns;
  Map<String, dynamic>? _quickEvolveResult;

  final Map<String, Map<String, dynamic>> _methodInfo = {
    'hybrid': {
      'name': 'Hybrid (Recommended)',
      'description': 'Automatically selects best algorithm per column type',
      'icon': Icons.auto_awesome,
      'color': Colors.purple,
    },
    'ga': {
      'name': 'Genetic Algorithm',
      'description': 'Evolves populations using selection, crossover, mutation',
      'icon': Icons.biotech,
      'color': Colors.green,
    },
    'pso': {
      'name': 'Particle Swarm',
      'description': 'Best for numeric data and continuous values',
      'icon': Icons.scatter_plot,
      'color': Colors.blue,
    },
    'de': {
      'name': 'Differential Evolution',
      'description': 'Robust global optimization for numeric data',
      'icon': Icons.functions,
      'color': Colors.orange,
    },
    'es': {
      'name': 'Evolution Strategy',
      'description': 'Consistent improvements with self-adaptive mutation',
      'icon': Icons.trending_up,
      'color': Colors.teal,
    },
  };

  Future<void> _loadSensitiveColumns() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isLoadingSensitiveColumns = true;
    });

    try {
      final result = await migrationData.detectSensitiveColumns();

      setState(() {
        _sensitiveColumns = result['sensitive_columns'] ?? {};
        _isLoadingSensitiveColumns = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingSensitiveColumns = false;
        _sensitiveColumns = {};
      });
    }
  }

  @override
  void initState() {
    super.initState();
    // Load sensitive columns when widget initializes
    Future.microtask(() => _loadSensitiveColumns());
  }

  Future<void> _cleanData() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isCleaning = true;
      _cleaningReport = null;
    });

    try {
      final report = await migrationData.cleanDataEvolutionary(
        method: _selectedMethod,
        trackModifications: _trackModifications,
      );

      setState(() {
        _cleaningReport = report;
        _isCleaning = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Data cleaned successfully! Fitness improved by ${report['improvement']['fitness_increase'].toStringAsFixed(2)}%',
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isCleaning = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error cleaning data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _compareMethodsDialog() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isComparing = true;
      _comparisonResults = null;
    });

    try {
      final results = await migrationData.compareCleaningMethods();

      setState(() {
        _comparisonResults = results;
        _isComparing = false;
      });

      if (mounted) {
        _showComparisonDialog();
      }
    } catch (e) {
      setState(() {
        _isComparing = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error comparing methods: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _quickEvolveData() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isQuickEvolving = true;
      _quickEvolveResult = null;
    });

    try {
      // Import ApiService for quick evolve
      final apiService = migrationData.apiService;

      // Call quick evolve with sensible defaults for fastest evolution
      // fitness_threshold: 85.0 (default), population_size: 20 (small for speed), generations: 30 (quick)
      final result = await apiService.quickEvolve(
        fitnessThreshold: 85.0,
        populationSize: 20,
        generations: 30,
        saveResult: true,
      );

      setState(() {
        _quickEvolveResult = result;
        _isQuickEvolving = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Quick Evolution completed! Best fitness: ${(result['best_fitness'] as num?)?.toStringAsFixed(2) ?? 'N/A'}',
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isQuickEvolving = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Quick Evolution failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showComparisonDialog() {
    if (_comparisonResults == null) return;

    final results = _comparisonResults!['results'] as Map<String, dynamic>;
    final bestMethod = _comparisonResults!['best_method'] as String;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Method Comparison Results'),
        content: SizedBox(
          width: 600,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.emoji_events, color: Colors.green.shade700),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Best Method: ${_methodInfo[bestMethod]?['name'] ?? bestMethod.toUpperCase()}',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade700,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              ...results.entries.map((entry) {
                final methodData = entry.value as Map<String, dynamic>;
                return _buildComparisonCard(
                  entry.key,
                  methodData,
                  entry.key == bestMethod,
                );
              }),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _selectedMethod = bestMethod;
              });
              Navigator.of(context).pop();
            },
            child: const Text('Use Best Method'),
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonCard(
      String method, Map<String, dynamic> data, bool isBest) {
    final improvement = data['improvement'] as double;
    final recordsFixed = data['records_fixed'] as int;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isBest ? Colors.green.shade50 : Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isBest ? Colors.green.shade300 : Colors.grey.shade300,
          width: isBest ? 2 : 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            _methodInfo[method]?['icon'] ?? Icons.science,
            color: _methodInfo[method]?['color'] ?? Colors.grey,
            size: 28,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _methodInfo[method]?['name'] ?? method.toUpperCase(),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Improvement: ${improvement.toStringAsFixed(2)}% • $recordsFixed records fixed',
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          if (isBest)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.green,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'BEST',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        final hasData =
            migrationData.data != null && migrationData.data!.isNotEmpty;

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.auto_fix_high,
                        size: 32, color: Colors.purple.shade700),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Evolutionary Data Cleaning',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Use AI algorithms to intelligently clean and impute missing values',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Quick Evolve Card
                if (hasData)
                  Card(
                    elevation: 2,
                    color: Colors.green.shade50,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.bolt,
                                color: Colors.green.shade700,
                                size: 28,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Quick Evolve (Genetic Algorithm)',
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.green.shade800,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Automatically clean & improve data with optimized GA defaults (20 population, 30 generations)',
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.grey.shade700,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'One-click evolution with sensible defaults for fastest results:',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              const SizedBox(width: 8),
                              Icon(Icons.check_circle,
                                  size: 16, color: Colors.green.shade700),
                              const SizedBox(width: 8),
                              Text(
                                'Population Size: 20 (small for speed)',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade700,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              const SizedBox(width: 8),
                              Icon(Icons.check_circle,
                                  size: 16, color: Colors.green.shade700),
                              const SizedBox(width: 8),
                              Text(
                                'Generations: 30 (quick convergence)',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade700,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              const SizedBox(width: 8),
                              Icon(Icons.check_circle,
                                  size: 16, color: Colors.green.shade700),
                              const SizedBox(width: 8),
                              Text(
                                'Fitness Threshold: 85%',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey.shade700,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed: hasData && !_isQuickEvolving
                                  ? _quickEvolveData
                                  : null,
                              icon: _isQuickEvolving
                                  ? const SizedBox(
                                      width: 16,
                                      height: 16,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        valueColor:
                                            AlwaysStoppedAnimation<Color>(
                                                Colors.white),
                                      ),
                                    )
                                  : const Icon(Icons.play_circle),
                              label: Text(
                                _isQuickEvolving
                                    ? 'Evolving Data...'
                                    : 'Start Quick Evolution',
                              ),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green.shade700,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 24,
                                  vertical: 16,
                                ),
                              ),
                            ),
                          ),
                          // Quick Evolve Result
                          if (_quickEvolveResult != null) ...[
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(8),
                                border:
                                    Border.all(color: Colors.green.shade200),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Icon(Icons.check_circle,
                                          color: Colors.green.shade700),
                                      const SizedBox(width: 8),
                                      const Text(
                                        'Evolution Complete',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 14,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  _buildQuickEvolveResultRow(
                                    'Best Fitness',
                                    '${(_quickEvolveResult!['best_fitness'] as num?)?.toStringAsFixed(2) ?? 'N/A'}%',
                                    Colors.green,
                                  ),
                                  _buildQuickEvolveResultRow(
                                    'Generations Run',
                                    '${_quickEvolveResult!['total_generations'] ?? 'N/A'}',
                                    Colors.blue,
                                  ),
                                  if (_quickEvolveResult!['execution_time'] !=
                                      null)
                                    _buildQuickEvolveResultRow(
                                      'Time Taken',
                                      '${(_quickEvolveResult!['execution_time'] as num?)?.toStringAsFixed(2) ?? 'N/A'}s',
                                      Colors.orange,
                                    ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                const SizedBox(height: 24),
                if (!hasData)
                  Container(
                    padding: const EdgeInsets.all(32),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.orange.shade200),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline,
                            color: Colors.orange.shade700, size: 32),
                        const SizedBox(width: 16),
                        const Expanded(
                          child: Text(
                            'Please load data first to use evolutionary cleaning',
                            style: TextStyle(fontSize: 16),
                          ),
                        ),
                      ],
                    ),
                  )
                else ...[
                  const Text(
                    'Select Cleaning Method',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: _methodInfo.entries.map((entry) {
                      final isSelected = _selectedMethod == entry.key;
                      return InkWell(
                        onTap: () =>
                            setState(() => _selectedMethod = entry.key),
                        child: Container(
                          width: 220,
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? entry.value['color'].withOpacity(0.1)
                                : Colors.grey.shade50,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: isSelected
                                  ? entry.value['color']
                                  : Colors.grey.shade300,
                              width: isSelected ? 2 : 1,
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    entry.value['icon'],
                                    color: entry.value['color'],
                                    size: 24,
                                  ),
                                  const Spacer(),
                                  if (isSelected)
                                    Icon(Icons.check_circle,
                                        color: entry.value['color']),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Text(
                                entry.value['name'],
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                entry.value['description'],
                                style: TextStyle(
                                  color: Colors.grey.shade700,
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),
                  CheckboxListTile(
                    title: const Text('Track AI Modifications'),
                    subtitle: const Text(
                      'Add "Modified_by_AI" column to track which records were modified',
                    ),
                    value: _trackModifications,
                    onChanged: (value) {
                      setState(() {
                        _trackModifications = value ?? true;
                      });
                    },
                  ),
                  const SizedBox(height: 24),
                  // Sensitive Data Warning
                  if (_isLoadingSensitiveColumns)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Row(
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          ),
                          SizedBox(width: 8),
                          Text('Checking for sensitive data...'),
                        ],
                      ),
                    )
                  else if (_sensitiveColumns != null &&
                      (_sensitiveColumns as Map).isNotEmpty)
                    SensitiveDataWarning(
                      sensitiveColumns:
                          _sensitiveColumns as Map<String, dynamic>,
                      onDismiss: () {
                        setState(() {
                          _sensitiveColumns = {};
                        });
                      },
                    ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      ElevatedButton.icon(
                        onPressed: hasData && !_isCleaning ? _cleanData : null,
                        icon: _isCleaning
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                      Colors.white),
                                ),
                              )
                            : const Icon(Icons.cleaning_services),
                        label: Text(_isCleaning ? 'Cleaning...' : 'Clean Data'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.purple.shade700,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 32,
                            vertical: 20,
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      OutlinedButton.icon(
                        onPressed: hasData && !_isComparing
                            ? _compareMethodsDialog
                            : null,
                        icon: _isComparing
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child:
                                    CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.compare_arrows),
                        label: Text(
                            _isComparing ? 'Comparing...' : 'Compare Methods'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 32,
                            vertical: 20,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (_cleaningReport != null) ...[
                    const SizedBox(height: 32),
                    const Divider(),
                    const SizedBox(height: 16),
                    _buildCleaningReport(_cleaningReport!),
                  ],
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCleaningReport(Map<String, dynamic> report) {
    final before = report['before'] as Map<String, dynamic>;
    final after = report['after'] as Map<String, dynamic>;
    final improvement = report['improvement'] as Map<String, dynamic>;
    final modifications = report['modifications'] as Map<String, dynamic>?;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Cleaning Report',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildReportCard(
                'Before',
                '${before['average_fitness'].toStringAsFixed(2)}%',
                '${before['records_with_issues']} issues',
                Colors.red,
                Icons.error_outline,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildReportCard(
                'After',
                '${after['average_fitness'].toStringAsFixed(2)}%',
                '${after['records_with_issues']} issues',
                Colors.green,
                Icons.check_circle_outline,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildReportCard(
                'Improvement',
                '+${improvement['fitness_increase'].toStringAsFixed(2)}%',
                '${improvement['records_fixed']} fixed',
                Colors.blue,
                Icons.trending_up,
              ),
            ),
            if (modifications != null && modifications['tracked'] == true) ...[
              const SizedBox(width: 16),
              Expanded(
                child: _buildReportCard(
                  'AI Modified',
                  '${modifications['records_modified']} records',
                  '${modifications['modification_rate']}',
                  Colors.purple,
                  Icons.smart_toy,
                ),
              ),
            ],
          ],
        ),
      ],
    );
  }

  Widget _buildReportCard(
      String label, String value, String subtitle, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 12),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          Text(
            subtitle,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickEvolveResultRow(String label, String value, Color color) {
    return Row(
      children: [
        Icon(Icons.info, size: 14, color: color),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
