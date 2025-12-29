import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// Secret Demo Panel - Accessible via secret gesture
/// Allows running evolutionary algorithm demos and tests
class SecretDemoPanel extends StatefulWidget {
  const SecretDemoPanel({Key? key}) : super(key: key);

  @override
  State<SecretDemoPanel> createState() => _SecretDemoPanelState();
}

class _SecretDemoPanelState extends State<SecretDemoPanel> {
  final ApiService _apiService = ApiService();
  final TextEditingController _secretKeyController = TextEditingController();

  bool _isAuthenticated = false;
  bool _isLoading = false;
  String _selectedAlgorithm = 'ga';
  String _selectedDemoType = 'quick';
  String _selectedProblem = 'sphere';
  int _stressIterations = 5;

  List<String> _outputLines = [];
  Map<String, dynamic>? _lastResults;
  String? _errorMessage;

  final List<Map<String, dynamic>> _algorithms = [
    {'id': 'ga', 'name': 'Genetic Algorithm', 'icon': Icons.schema},
    {'id': 'pso', 'name': 'Particle Swarm', 'icon': Icons.bubble_chart},
    {'id': 'de', 'name': 'Differential Evolution', 'icon': Icons.difference},
    {'id': 'es', 'name': 'Evolution Strategy', 'icon': Icons.trending_up},
  ];

  final List<Map<String, dynamic>> _demoTypes = [
    {'id': 'quick', 'name': 'Quick Test', 'description': 'Fast inline demo'},
    {'id': 'demo', 'name': 'Full Demo', 'description': 'Comprehensive demo script'},
    {'id': 'test', 'name': 'Unit Tests', 'description': 'Run unit test suite'},
  ];

  final List<Map<String, dynamic>> _problems = [
    {'id': 'sphere', 'name': 'Sphere', 'target': 0.0},
    {'id': 'shifted', 'name': 'Shifted', 'target': 5.0},
    {'id': 'rastrigin', 'name': 'Rastrigin', 'target': 0.0},
  ];

  void _authenticate() {
    if (_secretKeyController.text == 'fastmig2024') {
      setState(() {
        _isAuthenticated = true;
        _errorMessage = null;
      });
    } else {
      setState(() {
        _errorMessage = 'Invalid secret key';
      });
    }
  }

  Future<void> _runDemo() async {
    setState(() {
      _isLoading = true;
      _outputLines = [];
      _lastResults = null;
      _errorMessage = null;
    });

    try {
      final result = await _apiService.runDemo(
        algorithm: _selectedAlgorithm,
        demoType: _selectedDemoType,
        secretKey: _secretKeyController.text,
      );

      setState(() {
        _outputLines = List<String>.from(result['output'] ?? []);
        _lastResults = result['results'];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _compareAlgorithms() async {
    setState(() {
      _isLoading = true;
      _outputLines = [];
      _lastResults = null;
      _errorMessage = null;
    });

    try {
      final result = await _apiService.compareAlgorithms(
        problem: _selectedProblem,
        secretKey: _secretKeyController.text,
      );

      setState(() {
        _outputLines = List<String>.from(result['output'] ?? []);
        _lastResults = result['results'];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _runStressTest() async {
    setState(() {
      _isLoading = true;
      _outputLines = [];
      _lastResults = null;
      _errorMessage = null;
    });

    try {
      final result = await _apiService.stressTestAlgorithms(
        algorithm: _selectedAlgorithm == 'all' ? 'all' : _selectedAlgorithm,
        iterations: _stressIterations,
        secretKey: _secretKeyController.text,
      );

      setState(() {
        _outputLines = List<String>.from(result['output'] ?? []);
        _lastResults = result['results'];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isAuthenticated) {
      return _buildAuthScreen();
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          _buildDemoControls(),
          const SizedBox(height: 16),
          _buildCompareSection(),
          const SizedBox(height: 16),
          _buildStressTestSection(),
          const SizedBox(height: 16),
          if (_errorMessage != null) _buildErrorMessage(),
          if (_isLoading) _buildLoadingIndicator(),
          if (_outputLines.isNotEmpty) _buildOutputSection(),
          if (_lastResults != null) _buildResultsSection(),
        ],
      ),
    );
  }

  Widget _buildAuthScreen() {
    return Center(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 400),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.lock_outline,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 24),
            const Text(
              'Secret Demo Area',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Enter the secret key to access evolutionary algorithm demos',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _secretKeyController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Secret Key',
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.key),
                errorText: _errorMessage,
              ),
              onSubmitted: (_) => _authenticate(),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _authenticate,
              icon: const Icon(Icons.login),
              label: const Text('Unlock'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.deepPurple.shade700, Colors.purple.shade500],
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Icon(Icons.science, color: Colors.white, size: 32),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Evolutionary Algorithm Lab',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'GA • PSO • DE • ES',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.lock, color: Colors.white70),
            onPressed: () {
              setState(() {
                _isAuthenticated = false;
                _secretKeyController.clear();
              });
            },
            tooltip: 'Lock',
          ),
        ],
      ),
    );
  }

  Widget _buildDemoControls() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Run Demo/Test',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 16),
            // Algorithm Selection
            const Text('Algorithm:', style: TextStyle(fontWeight: FontWeight.w500)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _algorithms.map((algo) {
                final isSelected = _selectedAlgorithm == algo['id'];
                return ChoiceChip(
                  label: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        algo['icon'] as IconData,
                        size: 16,
                        color: isSelected ? Colors.white : Colors.grey,
                      ),
                      const SizedBox(width: 4),
                      Text(algo['name'] as String),
                    ],
                  ),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() => _selectedAlgorithm = algo['id'] as String);
                    }
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            // Demo Type Selection
            const Text('Demo Type:', style: TextStyle(fontWeight: FontWeight.w500)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _demoTypes.map((type) {
                final isSelected = _selectedDemoType == type['id'];
                return ChoiceChip(
                  label: Text(type['name'] as String),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() => _selectedDemoType = type['id'] as String);
                    }
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _runDemo,
              icon: const Icon(Icons.play_arrow),
              label: Text(
                'Run ${_selectedAlgorithm.toUpperCase()} ${_selectedDemoType == 'test' ? 'Tests' : 'Demo'}',
              ),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 44),
                backgroundColor: Colors.deepPurple,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCompareSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Compare All Algorithms',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 8),
            const Text(
              'Run all 4 algorithms on the same optimization problem',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 16),
            const Text('Problem:', style: TextStyle(fontWeight: FontWeight.w500)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _problems.map((problem) {
                final isSelected = _selectedProblem == problem['id'];
                return ChoiceChip(
                  label: Text('${problem['name']} (x=${problem['target']})'),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) {
                      setState(() => _selectedProblem = problem['id'] as String);
                    }
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _compareAlgorithms,
              icon: const Icon(Icons.compare_arrows),
              label: const Text('Compare All Algorithms'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 44),
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStressTestSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Stress Test',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 8),
            const Text(
              'Run multiple iterations to test reliability and performance',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Text('Iterations: ', style: TextStyle(fontWeight: FontWeight.w500)),
                Expanded(
                  child: Slider(
                    value: _stressIterations.toDouble(),
                    min: 1,
                    max: 20,
                    divisions: 19,
                    label: _stressIterations.toString(),
                    onChanged: (value) {
                      setState(() => _stressIterations = value.toInt());
                    },
                  ),
                ),
                Text(
                  '$_stressIterations',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _runStressTest,
                    icon: const Icon(Icons.speed),
                    label: Text('Stress Test ${_selectedAlgorithm.toUpperCase()}'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: _isLoading
                      ? null
                      : () {
                          setState(() => _selectedAlgorithm = 'all');
                          _runStressTest();
                        },
                  icon: const Icon(Icons.all_inclusive),
                  label: const Text('All'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorMessage() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _errorMessage!,
              style: TextStyle(color: Colors.red.shade700),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => setState(() => _errorMessage = null),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingIndicator() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(24),
      child: const Column(
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Running... This may take a moment.'),
        ],
      ),
    );
  }

  Widget _buildOutputSection() {
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.terminal, size: 20),
                const SizedBox(width: 8),
                const Text(
                  'Output',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                Text(
                  '${_outputLines.length} lines',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () => setState(() => _outputLines = []),
                  tooltip: 'Clear',
                ),
              ],
            ),
          ),
          Container(
            height: 300,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
            ),
            child: ListView.builder(
              itemCount: _outputLines.length,
              itemBuilder: (context, index) {
                final line = _outputLines[index];
                Color textColor = Colors.white;
                if (line.contains('✓') || line.contains('success')) {
                  textColor = Colors.greenAccent;
                } else if (line.contains('✗') || line.contains('error') || line.contains('FAILED')) {
                  textColor = Colors.redAccent;
                } else if (line.contains('===') || line.contains('---')) {
                  textColor = Colors.cyanAccent;
                } else if (line.contains('Best') || line.contains('🏆')) {
                  textColor = Colors.amberAccent;
                }
                return Text(
                  line,
                  style: TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 12,
                    color: textColor,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultsSection() {
    if (_lastResults == null) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Results Summary',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            ..._lastResults!.entries.map((entry) {
              if (entry.value is Map) {
                return ExpansionTile(
                  title: Text(entry.key.toUpperCase()),
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: (entry.value as Map).entries.map((subEntry) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(subEntry.key.toString()),
                                Text(
                                  _formatValue(subEntry.value),
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ],
                );
              } else if (entry.key != 'output') {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(entry.key),
                      Text(
                        _formatValue(entry.value),
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                );
              }
              return const SizedBox.shrink();
            }),
          ],
        ),
      ),
    );
  }

  String _formatValue(dynamic value) {
    if (value is double) {
      return value.toStringAsFixed(6);
    } else if (value is List) {
      return '[${value.length} items]';
    }
    return value.toString();
  }

  @override
  void dispose() {
    _secretKeyController.dispose();
    super.dispose();
  }
}
