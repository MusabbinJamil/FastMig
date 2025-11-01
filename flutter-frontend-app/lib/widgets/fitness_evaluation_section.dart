import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class FitnessEvaluationSection extends StatefulWidget {
  const FitnessEvaluationSection({Key? key}) : super(key: key);

  @override
  State<FitnessEvaluationSection> createState() =>
      _FitnessEvaluationSectionState();
}

class _FitnessEvaluationSectionState extends State<FitnessEvaluationSection> {
  bool _isEvaluating = false;
  Map<String, dynamic>? _fitnessResults;

  Future<void> _evaluateFitness() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isEvaluating = true;
    });

    try {
      final results = await migrationData.evaluateDataFitness();
      setState(() {
        _fitnessResults = results;
        _isEvaluating = false;
      });
    } catch (e) {
      setState(() {
        _isEvaluating = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error evaluating fitness: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
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
                    Icon(Icons.health_and_safety,
                        size: 32, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Data Fitness Evaluation',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Assess the health and quality of your data',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed:
                          hasData && !_isEvaluating ? _evaluateFitness : null,
                      icon: _isEvaluating
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Icon(Icons.play_arrow),
                      label: Text(
                          _isEvaluating ? 'Evaluating...' : 'Evaluate Fitness'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue.shade700,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 16,
                        ),
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
                            'Please load data first to evaluate fitness',
                            style: TextStyle(fontSize: 16),
                          ),
                        ),
                      ],
                    ),
                  ),
                if (_fitnessResults != null) ...[
                  const Divider(height: 32),
                  _buildFitnessSummary(_fitnessResults!),
                  const SizedBox(height: 24),
                  _buildHealthBreakdown(_fitnessResults!),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildFitnessSummary(Map<String, dynamic> results) {
    final summary = results['summary'] as Map<String, dynamic>;
    final avgFitness = summary['average_fitness'] as double;
    final totalRecords = summary['total_records'] as int;
    final needsCleaning = summary['records_needing_cleaning'] as int;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Fitness Summary',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildSummaryCard(
                'Average Fitness',
                '${avgFitness.toStringAsFixed(2)}%',
                _getFitnessColor(avgFitness),
                Icons.trending_up,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSummaryCard(
                'Total Records',
                totalRecords.toString(),
                Colors.blue,
                Icons.dataset,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildSummaryCard(
                'Need Cleaning',
                needsCleaning.toString(),
                Colors.orange,
                Icons.warning_amber,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSummaryCard(
      String label, String value, Color color, IconData icon) {
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
          Row(
            children: [
              Icon(icon, color: color, size: 24),
              const Spacer(),
              Text(
                value,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade700,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthBreakdown(Map<String, dynamic> results) {
    final summary = results['summary'] as Map<String, dynamic>;
    final breakdown = summary['health_breakdown'] as Map<String, dynamic>;

    final categories = [
      {
        'label': 'Excellent',
        'count': breakdown['excellent'],
        'color': Colors.green
      },
      {'label': 'Good', 'count': breakdown['good'], 'color': Colors.lightGreen},
      {'label': 'Fair', 'count': breakdown['fair'], 'color': Colors.orange},
      {'label': 'Poor', 'count': breakdown['poor'], 'color': Colors.deepOrange},
      {
        'label': 'Critical',
        'count': breakdown['critical'],
        'color': Colors.red
      },
    ];

    final total = summary['total_records'] as int;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Health Status Breakdown',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        ...categories.map((cat) {
          final count = cat['count'] as int;
          final percentage = total > 0 ? (count / total * 100) : 0.0;
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: _buildHealthBar(
              cat['label'] as String,
              count,
              percentage,
              cat['color'] as Color,
            ),
          );
        }),
      ],
    );
  }

  Widget _buildHealthBar(
      String label, int count, double percentage, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            Text(
              '$count (${percentage.toStringAsFixed(1)}%)',
              style: TextStyle(
                color: Colors.grey.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: percentage / 100,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 12,
          ),
        ),
      ],
    );
  }

  Color _getFitnessColor(double fitness) {
    if (fitness >= 95) return Colors.green;
    if (fitness >= 80) return Colors.lightGreen;
    if (fitness >= 60) return Colors.orange;
    if (fitness >= 40) return Colors.deepOrange;
    return Colors.red;
  }
}
