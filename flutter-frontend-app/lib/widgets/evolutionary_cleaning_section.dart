import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';
import '../models/evolutionary_config_models.dart';
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
  bool _useCellLevelEvolution = true; // NEW: Toggle for cell-level vs column-level
  bool _isCleaning = false;
  bool _isComparing = false;
  bool _isPreviewing = false;
  bool _isLoadingSensitiveColumns = false;
  bool _showAdvancedSettings = false;
  Map<String, dynamic>? _cleaningReport;
  Map<String, dynamic>? _cellEvolutionReport;
  Map<String, dynamic>? _comparisonResults;
  Map<String, dynamic>? _sensitiveColumns;
  Map<String, dynamic>? _previewResults;

  // GA Configuration State
  GAConfigModel _gaConfig = GAConfigModel();

  // PSO Configuration State
  PSOConfigModel _psoConfig = PSOConfigModel();

  // DE Configuration State
  DEConfigModel _deConfig = DEConfigModel();

  // ES Configuration State
  ESConfigModel _esConfig = ESConfigModel();

  final Map<String, Map<String, dynamic>> _methodInfo = {
    'hybrid': {
      'name': 'Hybrid (Recommended)',
      'description': 'PSO for numeric columns, GA for categorical',
      'cellDescription': 'Auto-selects best algorithm per cell type',
      'icon': Icons.auto_awesome,
      'color': Colors.purple,
    },
    'ga': {
      'name': 'Genetic Algorithm',
      'description': 'Evolves populations using selection, crossover, mutation',
      'cellDescription': 'Crossover & mutation from healthy cell populations',
      'icon': Icons.biotech,
      'color': Colors.green,
    },
    'pso': {
      'name': 'Particle Swarm',
      'description': 'Best for numeric data and continuous values',
      'cellDescription': 'Velocity-based movement towards healthy cell values',
      'icon': Icons.scatter_plot,
      'color': Colors.blue,
    },
    'de': {
      'name': 'Differential Evolution',
      'description': 'Robust global optimization for numeric data',
      'cellDescription': 'Vector differences between healthy cells',
      'icon': Icons.functions,
      'color': Colors.orange,
    },
    'es': {
      'name': 'Evolution Strategy',
      'description': 'Consistent improvements with self-adaptive mutation',
      'cellDescription': 'Self-adaptive mutation strength per cell',
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
    Future.microtask(() => _loadSensitiveColumns());
  }

  /// Get method-specific configuration for API calls
  Map<String, dynamic> _getMethodConfig() {
    switch (_selectedMethod) {
      case 'ga':
        return _gaConfig.toJson();
      case 'pso':
        return _psoConfig.toJson();
      case 'de':
        return _deConfig.toJson();
      case 'es':
        return _esConfig.toJson();
      default:
        return {};
    }
  }

  Future<void> _cleanData() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isCleaning = true;
      _cleaningReport = null;
      _cellEvolutionReport = null;
    });

    try {
      if (_useCellLevelEvolution) {
        // Use new cell-level evolution with method-specific config
        final result = await migrationData.evolveErrorCells(
          method: _selectedMethod,
          saveResult: true,
          config: _getMethodConfig(),
        );

        setState(() {
          _cellEvolutionReport = result;
          _isCleaning = false;
        });

        if (mounted) {
          final cellsFixed = result['cells_fixed'] ?? 0;
          final cellsEvolved = result['cells_evolved'] ?? 0;
          final improvement = result['fitness_improvement'] ?? 0.0;

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Cell evolution complete! Fixed $cellsFixed/$cellsEvolved cells. '
                'Fitness improved by ${(improvement * 100).toStringAsFixed(2)}%',
              ),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      } else {
        // Use original column-level cleaning
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

  /// Apply the previewed changes using the cached preview results
  /// This ensures consistency between preview and apply operations
  Future<void> _applyPreviewedChanges() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isCleaning = true;
      _cellEvolutionReport = null;
    });

    try {
      final result = await migrationData.applyPreviewedChanges(
        saveResult: true,
      );

      setState(() {
        _cellEvolutionReport = result;
        _isCleaning = false;
      });

      if (mounted) {
        final cellsFixed = result['cells_fixed'] ?? 0;
        final cellsEvolved = result['cells_evolved'] ?? 0;
        final improvement = result['fitness_improvement'] ?? 0.0;

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Applied previewed changes! Fixed $cellsFixed/$cellsEvolved cells. '
              'Fitness improved by ${(improvement * 100).toStringAsFixed(2)}%',
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
            content: Text('Error applying previewed changes: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _previewEvolution() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isPreviewing = true;
      _previewResults = null;
    });

    try {
      final result = await migrationData.previewCellEvolution(
        method: _selectedMethod,
        maxCells: 10,
      );

      setState(() {
        _previewResults = result;
        _isPreviewing = false;
      });

      if (mounted) {
        _showPreviewDialog();
      }
    } catch (e) {
      setState(() {
        _isPreviewing = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error previewing: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showPreviewDialog() {
    if (_previewResults == null) return;

    final preview = _previewResults!['preview'] as List? ?? [];
    final wouldFix = _previewResults!['would_fix'] ?? 0;
    final total = _previewResults!['total_error_cells'] ?? 0;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.preview, color: Colors.blue.shade700),
            const SizedBox(width: 12),
            const Text('Evolution Preview'),
          ],
        ),
        content: SizedBox(
          width: 700,
          height: 500,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Would fix $wouldFix out of ${preview.length} previewed cells '
                        '(Total error cells: $total)',
                        style: TextStyle(
                          color: Colors.blue.shade700,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: ListView.builder(
                  itemCount: preview.length,
                  itemBuilder: (context, index) {
                    final cell = preview[index] as Map<String, dynamic>;
                    final wouldBeFix = cell['would_be_fixed'] ?? false;

                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: wouldBeFix ? Colors.green.shade50 : Colors.grey.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: wouldBeFix ? Colors.green.shade300 : Colors.grey.shade300,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            wouldBeFix ? Icons.check_circle : Icons.remove_circle,
                            color: wouldBeFix ? Colors.green : Colors.grey,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Row ${cell['row']}, Column: ${cell['column']}',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    Text(
                                      '"${cell['original_value'] ?? 'null'}"',
                                      style: TextStyle(color: Colors.red.shade700),
                                    ),
                                    const Icon(Icons.arrow_forward, size: 16),
                                    Text(
                                      '"${cell['evolved_value'] ?? 'null'}"',
                                      style: TextStyle(color: Colors.green.shade700),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Fitness: ${cell['fitness_before']} → ${cell['fitness_after']}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).pop();
              _applyPreviewedChanges();
            },
            icon: const Icon(Icons.play_arrow),
            label: const Text('Apply Evolution'),
          ),
        ],
      ),
    );
  }

  Future<void> _compareMethodsDialog() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isComparing = true;
      _comparisonResults = null;
    });

    try {
      Map<String, dynamic> results;

      if (_useCellLevelEvolution) {
        results = await migrationData.compareCellEvolutionMethods(quickMode: true);
      } else {
        results = await migrationData.compareCleaningMethods();
      }

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

  void _showComparisonDialog() {
    if (_comparisonResults == null) return;

    final results = _comparisonResults!['results'] as Map<String, dynamic>;
    final bestMethod = _comparisonResults!['best_method'] as String?;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Method Comparison Results'),
        content: SizedBox(
          width: 600,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (bestMethod != null)
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
          if (bestMethod != null)
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
    if (data.containsKey('error')) {
      return Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.red.shade300),
        ),
        child: Row(
          children: [
            Icon(Icons.error, color: Colors.red.shade700),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '${method.toUpperCase()}: ${data['error']}',
                style: TextStyle(color: Colors.red.shade700),
              ),
            ),
          ],
        ),
      );
    }

    // Handle both column-level and cell-level results
    final improvement = data['improvement'] ?? data['fix_rate'] ?? 0.0;
    final recordsFixed = data['records_fixed'] ?? data['cells_fixed'] ?? 0;

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
                  _useCellLevelEvolution
                      ? 'Fix rate: ${(improvement * 100).toStringAsFixed(1)}% • $recordsFixed cells fixed'
                      : 'Improvement: ${improvement.toStringAsFixed(2)}% • $recordsFixed records fixed',
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
        final errorCellCount = migrationData.errorCells?.length ?? 0;

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
                            'Use evolutionary algorithms to evolve corrupted cells into healthy ones',
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
                  // Error cells info banner
                  if (errorCellCount > 0)
                    Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red.shade200),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.warning_amber,
                              color: Colors.red.shade700, size: 28),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '$errorCellCount Error Cells Detected',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.red.shade700,
                                    fontSize: 16,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'These cells contain missing values, type mismatches, or other issues that can be evolved to healthy values.',
                                  style: TextStyle(
                                    color: Colors.red.shade600,
                                    fontSize: 13,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    )
                  else
                    Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.green.shade200),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.check_circle,
                              color: Colors.green.shade700, size: 28),
                          const SizedBox(width: 12),
                          Text(
                            'No error cells detected - data appears healthy!',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.green.shade700,
                            ),
                          ),
                        ],
                      ),
                    ),

                  // Cleaning mode toggle
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Text(
                              'Cleaning Mode:',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            const Spacer(),
                            Tooltip(
                              message: _useCellLevelEvolution
                                  ? 'Evolves individual error cells using healthy cells as templates'
                                  : 'Imputes missing values at the column level',
                              child: Icon(Icons.help_outline,
                                  color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            ChoiceChip(
                              label: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.grid_on,
                                    size: 18,
                                    color: _useCellLevelEvolution
                                        ? Colors.white
                                        : Colors.purple.shade700,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Cell-Level (Recommended)',
                                    style: TextStyle(
                                      color: _useCellLevelEvolution
                                          ? Colors.white
                                          : Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                              selected: _useCellLevelEvolution,
                              selectedColor: Colors.purple.shade700,
                              onSelected: (selected) {
                                setState(() => _useCellLevelEvolution = true);
                              },
                            ),
                            ChoiceChip(
                              label: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.view_column,
                                    size: 18,
                                    color: !_useCellLevelEvolution
                                        ? Colors.white
                                        : Colors.grey.shade700,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Column-Level',
                                    style: TextStyle(
                                      color: !_useCellLevelEvolution
                                          ? Colors.white
                                          : Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                              selected: !_useCellLevelEvolution,
                              selectedColor: Colors.grey.shade700,
                              onSelected: (selected) {
                                setState(() => _useCellLevelEvolution = false);
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const Text(
                    'Select Evolution Algorithm',
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
                                _useCellLevelEvolution
                                    ? entry.value['cellDescription']
                                    : entry.value['description'],
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

                  // Advanced Settings Section (GA/PSO/DE/ES specific)
                  if (_selectedMethod == 'ga' || _selectedMethod == 'pso' || _selectedMethod == 'de' || _selectedMethod == 'es')
                    _buildAdvancedSettingsSection(),

                  if (!_useCellLevelEvolution)
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
                  if (!_useCellLevelEvolution) const SizedBox(height: 24),
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
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      ElevatedButton.icon(
                        onPressed: hasData && !_isCleaning && errorCellCount > 0
                            ? _cleanData
                            : null,
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
                            : Icon(_useCellLevelEvolution
                                ? Icons.auto_fix_high
                                : Icons.cleaning_services),
                        label: Text(_isCleaning
                            ? 'Evolving...'
                            : _useCellLevelEvolution
                                ? 'Evolve Error Cells'
                                : 'Clean Data'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.purple.shade700,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 32,
                            vertical: 20,
                          ),
                        ),
                      ),
                      if (_useCellLevelEvolution && errorCellCount > 0)
                        OutlinedButton.icon(
                          onPressed: hasData && !_isPreviewing
                              ? _previewEvolution
                              : null,
                          icon: _isPreviewing
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child:
                                      CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.preview),
                          label: Text(
                              _isPreviewing ? 'Loading...' : 'Preview Changes'),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24,
                              vertical: 20,
                            ),
                          ),
                        ),
                      OutlinedButton.icon(
                        onPressed: hasData && !_isComparing && errorCellCount > 0
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
                            horizontal: 24,
                            vertical: 20,
                          ),
                        ),
                      ),
                    ],
                  ),
                  // Cell-level evolution report
                  if (_cellEvolutionReport != null) ...[
                    const SizedBox(height: 32),
                    const Divider(),
                    const SizedBox(height: 16),
                    _buildCellEvolutionReport(_cellEvolutionReport!),
                  ],
                  // Column-level cleaning report
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

  /// Build Advanced Settings Section for GA/PSO/DE/ES
  Widget _buildAdvancedSettingsSection() {
    String title;
    String subtitle;
    Color iconColor;

    switch (_selectedMethod) {
      case 'ga':
        title = 'GA Parameters';
        subtitle = 'Population, crossover, mutation, and selection';
        iconColor = Colors.green;
        break;
      case 'pso':
        title = 'PSO Parameters';
        subtitle = 'Swarm size, inertia, topology, and more';
        iconColor = Colors.blue;
        break;
      case 'de':
        title = 'DE Parameters';
        subtitle = 'Scale factor, mutation strategy, and more';
        iconColor = Colors.orange;
        break;
      case 'es':
        title = 'ES Parameters';
        subtitle = 'Population, offspring, mutation, and recombination';
        iconColor = Colors.teal;
        break;
      default:
        title = 'Parameters';
        subtitle = 'Algorithm settings';
        iconColor = Colors.grey;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: ExpansionTile(
        initiallyExpanded: _showAdvancedSettings,
        onExpansionChanged: (expanded) {
          setState(() => _showAdvancedSettings = expanded);
        },
        leading: Icon(
          Icons.tune,
          color: iconColor,
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          subtitle,
          style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: _selectedMethod == 'ga'
                ? _buildGASettings()
                : _selectedMethod == 'pso'
                    ? _buildPSOSettings()
                    : _selectedMethod == 'de'
                        ? _buildDESettings()
                        : _buildESSettings(),
          ),
        ],
      ),
    );
  }

  /// Build GA-specific settings UI
  Widget _buildGASettings() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Preset buttons
        _buildPresetRow(
          'GA Presets',
          ['fast', 'balanced', 'quality'],
          (preset) {
            setState(() {
              _gaConfig = GAConfigModel.getPreset(preset);
            });
          },
        ),
        const SizedBox(height: 16),

        // Population Size and Generations
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Population Size',
                _gaConfig.populationSize.toDouble(),
                10,
                100,
                (value) => setState(() {
                  _gaConfig = _gaConfig.copyWith(populationSize: value.round());
                }),
                suffix: ' individuals',
                divisions: 90,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Generations',
                _gaConfig.generations.toDouble(),
                10,
                500,
                (value) => setState(() {
                  _gaConfig = _gaConfig.copyWith(generations: value.round());
                }),
                suffix: ' gen',
                divisions: 49,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Mutation Rate and Crossover Rate
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Mutation Rate',
                _gaConfig.mutationRate,
                0.0,
                0.5,
                (value) => setState(() {
                  _gaConfig = _gaConfig.copyWith(mutationRate: value);
                }),
                decimals: 2,
                tooltip: 'Probability of random gene mutation',
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Crossover Rate',
                _gaConfig.crossoverRate,
                0.0,
                1.0,
                (value) => setState(() {
                  _gaConfig = _gaConfig.copyWith(crossoverRate: value);
                }),
                decimals: 2,
                tooltip: 'Probability of crossover between parents',
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Selection Method and Crossover Method
        Row(
          children: [
            Expanded(
              child: _buildDropdown(
                'Selection Method',
                _gaConfig.selectionMethod,
                GAConfigModel.selectionMethods,
                GAConfigModel.selectionMethodDisplayNames,
                (value) => setState(() {
                  _gaConfig = _gaConfig.copyWith(selectionMethod: value);
                }),
                icon: Icons.people,
                color: Colors.green,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildDropdown(
                'Crossover Method',
                _gaConfig.crossoverMethod,
                GAConfigModel.crossoverMethods,
                GAConfigModel.crossoverMethodDisplayNames,
                (value) => setState(() {
                  _gaConfig = _gaConfig.copyWith(crossoverMethod: value);
                }),
                icon: Icons.shuffle,
                color: Colors.green,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Mutation Method
        Row(
          children: [
            Expanded(
              child: _buildDropdown(
                'Mutation Method',
                _gaConfig.mutationMethod,
                GAConfigModel.mutationMethods,
                GAConfigModel.mutationMethodDisplayNames,
                (value) => setState(() {
                  _gaConfig = _gaConfig.copyWith(mutationMethod: value);
                }),
                icon: Icons.change_circle,
                color: Colors.green,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Container(), // Placeholder for alignment
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Elitism settings
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.green.shade50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.green.shade200),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Elitism Settings',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: CheckboxListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Enable Elitism', style: TextStyle(fontSize: 13)),
                      subtitle: const Text('Preserve best individuals', style: TextStyle(fontSize: 11)),
                      value: _gaConfig.elitism,
                      onChanged: (value) => setState(() {
                        _gaConfig = _gaConfig.copyWith(elitism: value ?? true);
                      }),
                    ),
                  ),
                  if (_gaConfig.elitism)
                    Expanded(
                      child: _buildSliderWithLabel(
                        'Elite Count',
                        _gaConfig.eliteCount.toDouble(),
                        1,
                        10,
                        (value) => setState(() {
                          _gaConfig = _gaConfig.copyWith(eliteCount: value.round());
                        }),
                        suffix: ' best',
                        divisions: 9,
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Early Stopping settings
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey.shade100,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Early Stopping',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: CheckboxListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Enable Early Stopping', style: TextStyle(fontSize: 13)),
                      subtitle: const Text('Stop if no improvement', style: TextStyle(fontSize: 11)),
                      value: _gaConfig.earlyStoppingEnabled,
                      onChanged: (value) => setState(() {
                        _gaConfig = _gaConfig.copyWith(earlyStoppingEnabled: value ?? true);
                      }),
                    ),
                  ),
                  if (_gaConfig.earlyStoppingEnabled)
                    Expanded(
                      child: _buildSliderWithLabel(
                        'Patience',
                        _gaConfig.earlyStoppingPatience.toDouble(),
                        3,
                        30,
                        (value) => setState(() {
                          _gaConfig = _gaConfig.copyWith(earlyStoppingPatience: value.round());
                        }),
                        suffix: ' gen',
                        divisions: 27,
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Build PSO-specific settings UI
  Widget _buildPSOSettings() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Preset buttons
        _buildPresetRow(
          'PSO Presets',
          ['fast', 'balanced', 'quality'],
          (preset) {
            setState(() {
              _psoConfig = PSOConfigModel.getPreset(preset);
            });
          },
        ),
        const SizedBox(height: 16),

        // Swarm Size and Iterations
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Swarm Size',
                _psoConfig.swarmSize.toDouble(),
                10,
                100,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(swarmSize: value.round());
                }),
                suffix: ' particles',
                divisions: 90,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Iterations',
                _psoConfig.iterations.toDouble(),
                10,
                500,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(iterations: value.round());
                }),
                suffix: ' gen',
                divisions: 49,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Inertia Weight and Velocity Clamp
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Inertia Weight (w)',
                _psoConfig.inertiaWeight,
                0.0,
                1.0,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(inertiaWeight: value);
                }),
                decimals: 2,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Velocity Clamp',
                _psoConfig.velocityClamp,
                0.0,
                1.0,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(velocityClamp: value);
                }),
                decimals: 2,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Cognitive and Social Coefficients
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Cognitive (c1)',
                _psoConfig.cognitiveParameter,
                0.0,
                4.0,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(cognitiveParameter: value);
                }),
                decimals: 2,
                tooltip: 'Individual best influence',
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Social (c2)',
                _psoConfig.socialParameter,
                0.0,
                4.0,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(socialParameter: value);
                }),
                decimals: 2,
                tooltip: 'Global best influence',
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Topology and Variant Dropdowns
        Row(
          children: [
            Expanded(
              child: _buildDropdown(
                'Topology',
                _psoConfig.topologyType,
                PSOConfigModel.topologyTypes,
                PSOConfigModel.topologyDisplayNames,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(topologyType: value);
                }),
                icon: Icons.hub,
                color: Colors.blue,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildDropdown(
                'Variant',
                _psoConfig.variant,
                PSOConfigModel.variants,
                PSOConfigModel.variantDisplayNames,
                (value) => setState(() {
                  _psoConfig = _psoConfig.copyWith(variant: value);
                }),
                icon: Icons.settings,
                color: Colors.blue,
              ),
            ),
          ],
        ),

        // Constriction factor (only for constriction variant)
        if (_psoConfig.variant == 'constriction') ...[
          const SizedBox(height: 16),
          _buildSliderWithLabel(
            'Constriction Factor',
            _psoConfig.constrictionFactor,
            0.5,
            1.0,
            (value) => setState(() {
              _psoConfig = _psoConfig.copyWith(constrictionFactor: value);
            }),
            decimals: 3,
            tooltip: 'Clerc\'s constriction factor (typical: 0.729)',
          ),
        ],

        // Inertia decay settings (only for inertia_decay variant)
        if (_psoConfig.variant == 'inertia_decay') ...[
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSliderWithLabel(
                  'Inertia Min',
                  _psoConfig.inertiaMin,
                  0.0,
                  1.0,
                  (value) => setState(() {
                    _psoConfig = _psoConfig.copyWith(inertiaMin: value);
                  }),
                  decimals: 2,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildSliderWithLabel(
                  'Inertia Max',
                  _psoConfig.inertiaMax,
                  0.0,
                  1.0,
                  (value) => setState(() {
                    _psoConfig = _psoConfig.copyWith(inertiaMax: value);
                  }),
                  decimals: 2,
                ),
              ),
            ],
          ),
        ],

        // Neighborhood size (for local topologies)
        if (_psoConfig.topologyType == 'lbest' ||
            _psoConfig.topologyType == 'ring' ||
            _psoConfig.topologyType == 'random') ...[
          const SizedBox(height: 16),
          _buildSliderWithLabel(
            'Neighborhood Size',
            _psoConfig.neighborhoodSize.toDouble(),
            2,
            10,
            (value) => setState(() {
              _psoConfig = _psoConfig.copyWith(neighborhoodSize: value.round());
            }),
            suffix: ' neighbors',
            divisions: 8,
          ),
        ],
      ],
    );
  }

  /// Build DE-specific settings UI
  Widget _buildDESettings() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Preset buttons
        _buildPresetRow(
          'DE Presets',
          ['fast', 'balanced', 'quality'],
          (preset) {
            setState(() {
              _deConfig = DEConfigModel.getPreset(preset);
            });
          },
        ),
        const SizedBox(height: 16),

        // Population Size and Generations
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Population Size',
                _deConfig.populationSize.toDouble(),
                10,
                100,
                (value) => setState(() {
                  _deConfig = _deConfig.copyWith(populationSize: value.round());
                }),
                suffix: ' individuals',
                divisions: 90,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Generations',
                _deConfig.generations.toDouble(),
                10,
                500,
                (value) => setState(() {
                  _deConfig = _deConfig.copyWith(generations: value.round());
                }),
                suffix: ' gen',
                divisions: 49,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Scale Factor (F) and Crossover Rate (CR)
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Scale Factor (F)',
                _deConfig.scaleFactor,
                0.0,
                2.0,
                (value) => setState(() {
                  _deConfig = _deConfig.copyWith(scaleFactor: value);
                }),
                decimals: 2,
                tooltip: 'Controls mutation magnitude',
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Crossover Rate (CR)',
                _deConfig.crossoverRate,
                0.0,
                1.0,
                (value) => setState(() {
                  _deConfig = _deConfig.copyWith(crossoverRate: value);
                }),
                decimals: 2,
                tooltip: 'Probability of parameter selection from mutant',
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Mutation Strategy and Crossover Type
        Row(
          children: [
            Expanded(
              child: _buildDropdown(
                'Mutation Strategy',
                _deConfig.mutationStrategy,
                DEConfigModel.mutationStrategies,
                DEConfigModel.mutationStrategyDisplayNames,
                (value) => setState(() {
                  _deConfig = _deConfig.copyWith(mutationStrategy: value);
                }),
                icon: Icons.shuffle,
                color: Colors.orange,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildDropdown(
                'Crossover Type',
                _deConfig.crossoverType,
                DEConfigModel.crossoverTypes,
                DEConfigModel.crossoverTypeDisplayNames,
                (value) => setState(() {
                  _deConfig = _deConfig.copyWith(crossoverType: value);
                }),
                icon: Icons.merge_type,
                color: Colors.orange,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Adaptive toggles
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.orange.shade50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.orange.shade200),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Adaptive Parameters',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: CheckboxListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Adaptive F', style: TextStyle(fontSize: 13)),
                      subtitle: const Text('Auto-adjust scale factor', style: TextStyle(fontSize: 11)),
                      value: _deConfig.adaptiveF,
                      onChanged: (value) => setState(() {
                        _deConfig = _deConfig.copyWith(adaptiveF: value ?? false);
                      }),
                    ),
                  ),
                  Expanded(
                    child: CheckboxListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Adaptive CR', style: TextStyle(fontSize: 13)),
                      subtitle: const Text('Auto-adjust crossover', style: TextStyle(fontSize: 11)),
                      value: _deConfig.adaptiveCR,
                      onChanged: (value) => setState(() {
                        _deConfig = _deConfig.copyWith(adaptiveCR: value ?? false);
                      }),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        // Adaptive F range (only if adaptive F is enabled)
        if (_deConfig.adaptiveF) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSliderWithLabel(
                  'F Min',
                  _deConfig.fMin,
                  0.0,
                  1.0,
                  (value) => setState(() {
                    _deConfig = _deConfig.copyWith(fMin: value);
                  }),
                  decimals: 2,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildSliderWithLabel(
                  'F Max',
                  _deConfig.fMax,
                  0.5,
                  2.0,
                  (value) => setState(() {
                    _deConfig = _deConfig.copyWith(fMax: value);
                  }),
                  decimals: 2,
                ),
              ),
            ],
          ),
        ],

        // Adaptive CR range (only if adaptive CR is enabled)
        if (_deConfig.adaptiveCR) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSliderWithLabel(
                  'CR Min',
                  _deConfig.crMin,
                  0.0,
                  1.0,
                  (value) => setState(() {
                    _deConfig = _deConfig.copyWith(crMin: value);
                  }),
                  decimals: 2,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildSliderWithLabel(
                  'CR Max',
                  _deConfig.crMax,
                  0.0,
                  1.0,
                  (value) => setState(() {
                    _deConfig = _deConfig.copyWith(crMax: value);
                  }),
                  decimals: 2,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  /// Build ES-specific settings UI
  Widget _buildESSettings() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Preset buttons
        _buildPresetRow(
          'ES Presets',
          ['fast', 'balanced', 'quality'],
          (preset) {
            setState(() {
              _esConfig = ESConfigModel.getPreset(preset);
            });
          },
        ),
        const SizedBox(height: 16),

        // Population Size (μ) and Offspring Size (λ)
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Population Size (μ)',
                _esConfig.populationSize.toDouble(),
                5,
                50,
                (value) => setState(() {
                  _esConfig = _esConfig.copyWith(populationSize: value.round());
                }),
                suffix: ' parents',
                divisions: 45,
                tooltip: 'Number of parent individuals',
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Offspring Size (λ)',
                _esConfig.offspringSize.toDouble(),
                10,
                200,
                (value) => setState(() {
                  _esConfig = _esConfig.copyWith(offspringSize: value.round());
                }),
                suffix: ' children',
                divisions: 38,
                tooltip: 'Number of offspring per generation',
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Generations
        _buildSliderWithLabel(
          'Generations',
          _esConfig.generations.toDouble(),
          10,
          500,
          (value) => setState(() {
            _esConfig = _esConfig.copyWith(generations: value.round());
          }),
          suffix: ' gen',
          divisions: 49,
        ),
        const SizedBox(height: 16),

        // Selection Type and Recombination Type
        Row(
          children: [
            Expanded(
              child: _buildDropdown(
                'Selection Type',
                _esConfig.selectionType,
                ESConfigModel.selectionTypes,
                ESConfigModel.selectionTypeDisplayNames,
                (value) => setState(() {
                  _esConfig = _esConfig.copyWith(selectionType: value);
                }),
                icon: Icons.filter_list,
                color: Colors.teal,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildDropdown(
                'Recombination Type',
                _esConfig.recombinationType,
                ESConfigModel.recombinationTypes,
                ESConfigModel.recombinationTypeDisplayNames,
                (value) => setState(() {
                  _esConfig = _esConfig.copyWith(recombinationType: value);
                }),
                icon: Icons.merge,
                color: Colors.teal,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Initial Mutation Rate and Learning Rate
        Row(
          children: [
            Expanded(
              child: _buildSliderWithLabel(
                'Initial Mutation Rate',
                _esConfig.initialMutationRate,
                0.01,
                0.5,
                (value) => setState(() {
                  _esConfig = _esConfig.copyWith(initialMutationRate: value);
                }),
                decimals: 2,
                tooltip: 'Starting mutation strength (σ)',
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSliderWithLabel(
                'Learning Rate (τ)',
                _esConfig.learningRate,
                0.01,
                0.5,
                (value) => setState(() {
                  _esConfig = _esConfig.copyWith(learningRate: value);
                }),
                decimals: 2,
                tooltip: 'Rate of self-adaptation for mutation',
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Parent Count
        _buildSliderWithLabel(
          'Parent Count (ρ)',
          _esConfig.parentCount.toDouble(),
          1,
          5,
          (value) => setState(() {
            _esConfig = _esConfig.copyWith(parentCount: value.round());
          }),
          suffix: ' parents',
          divisions: 4,
          tooltip: 'Number of parents for recombination',
        ),
        const SizedBox(height: 16),

        // Self-Adaptive Mutation toggle
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.teal.shade50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.teal.shade200),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Self-Adaptation',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              const SizedBox(height: 8),
              CheckboxListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                title: const Text('Enable Self-Adaptive Mutation', style: TextStyle(fontSize: 13)),
                subtitle: const Text('Mutation rates evolve with individuals', style: TextStyle(fontSize: 11)),
                value: _esConfig.selfAdaptiveMutation,
                onChanged: (value) => setState(() {
                  _esConfig = _esConfig.copyWith(selfAdaptiveMutation: value ?? true);
                }),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// Build a preset selection row
  Widget _buildPresetRow(
    String title,
    List<String> presets,
    Function(String) onSelect,
  ) {
    return Row(
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
        const SizedBox(width: 16),
        ...presets.map((preset) {
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: OutlinedButton(
              onPressed: () => onSelect(preset),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                minimumSize: Size.zero,
              ),
              child: Text(
                preset[0].toUpperCase() + preset.substring(1),
                style: const TextStyle(fontSize: 12),
              ),
            ),
          );
        }),
      ],
    );
  }

  /// Build a slider with label and value display
  Widget _buildSliderWithLabel(
    String label,
    double value,
    double min,
    double max,
    Function(double) onChanged, {
    String? suffix,
    int? divisions,
    int decimals = 0,
    String? tooltip,
  }) {
    final displayValue = decimals > 0
        ? value.toStringAsFixed(decimals)
        : value.round().toString();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
            if (tooltip != null) ...[
              const SizedBox(width: 4),
              Tooltip(
                message: tooltip,
                child: Icon(Icons.info_outline, size: 14, color: Colors.grey.shade500),
              ),
            ],
            const Spacer(),
            Text(
              '$displayValue${suffix ?? ''}',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            trackHeight: 4,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
          ),
          child: Slider(
            value: value.clamp(min, max),
            min: min,
            max: max,
            divisions: divisions ?? ((max - min) * 100).round(),
            onChanged: onChanged,
          ),
        ),
      ],
    );
  }

  /// Build a dropdown selector
  Widget _buildDropdown(
    String label,
    String value,
    List<String> options,
    Map<String, String> displayNames,
    Function(String) onChanged, {
    IconData? icon,
    Color? color,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            if (icon != null) ...[
              Icon(icon, size: 16, color: color ?? Colors.grey),
              const SizedBox(width: 4),
            ],
            Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              isExpanded: true,
              value: value,
              items: options.map((option) {
                return DropdownMenuItem(
                  value: option,
                  child: Text(
                    displayNames[option] ?? option,
                    style: const TextStyle(fontSize: 13),
                    overflow: TextOverflow.ellipsis,
                  ),
                );
              }).toList(),
              onChanged: (newValue) {
                if (newValue != null) onChanged(newValue);
              },
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCellEvolutionReport(Map<String, dynamic> report) {
    final cellsEvolved = report['cells_evolved'] ?? 0;
    final cellsFixed = report['cells_fixed'] ?? 0;
    final cellsFailed = report['cells_failed'] ?? 0;
    final fitnessBefore = report['average_fitness_before'] ?? 0.0;
    final fitnessAfter = report['average_fitness_after'] ?? 0.0;
    final improvement = report['fitness_improvement'] ?? 0.0;
    final method = report['method'] ?? 'UNKNOWN';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.science, color: Colors.purple.shade700),
            const SizedBox(width: 8),
            Text(
              'Cell Evolution Report ($method)',
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildReportCard(
                'Cells Processed',
                '$cellsEvolved',
                'Total error cells',
                Colors.blue,
                Icons.grid_on,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildReportCard(
                'Cells Fixed',
                '$cellsFixed',
                '${cellsFailed > 0 ? '$cellsFailed failed' : 'All successful'}',
                Colors.green,
                Icons.check_circle,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildReportCard(
                'Fitness Before',
                '${(fitnessBefore * 100).toStringAsFixed(1)}%',
                'Average',
                Colors.red,
                Icons.trending_down,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildReportCard(
                'Fitness After',
                '${(fitnessAfter * 100).toStringAsFixed(1)}%',
                '+${(improvement * 100).toStringAsFixed(2)}%',
                Colors.teal,
                Icons.trending_up,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        // Show evolved cells details
        if (report['evolved_cells'] != null &&
            (report['evolved_cells'] as List).isNotEmpty)
          ExpansionTile(
            title: Text('View ${(report['evolved_cells'] as List).length} Evolved Cells'),
            leading: const Icon(Icons.list_alt),
            children: [
              Container(
                height: 200,
                child: ListView.builder(
                  itemCount: (report['evolved_cells'] as List).length,
                  itemBuilder: (context, index) {
                    final cell =
                        (report['evolved_cells'] as List)[index] as Map<String, dynamic>;
                    return ListTile(
                      dense: true,
                      leading: Icon(
                        cell['fitness_after'] > cell['fitness_before']
                            ? Icons.arrow_upward
                            : Icons.arrow_forward,
                        color: cell['fitness_after'] > cell['fitness_before']
                            ? Colors.green
                            : Colors.grey,
                        size: 20,
                      ),
                      title: Text(
                        'Row ${cell['row']}, ${cell['col_name']}',
                        style: const TextStyle(fontWeight: FontWeight.w500),
                      ),
                      subtitle: Text(
                        '"${cell['original_value']}" → "${cell['evolved_value']}"',
                      ),
                      trailing: Text(
                        '${((cell['fitness_after'] - cell['fitness_before']) * 100).toStringAsFixed(0)}%',
                        style: TextStyle(
                          color: cell['fitness_after'] > cell['fitness_before']
                              ? Colors.green
                              : Colors.grey,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
      ],
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
}
