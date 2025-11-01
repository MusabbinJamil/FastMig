import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';
import '../widgets/fitness_evaluation_section.dart';
import '../widgets/evolutionary_cleaning_section.dart';

class AiDataQualityScreen extends StatefulWidget {
  const AiDataQualityScreen({Key? key}) : super(key: key);

  @override
  State<AiDataQualityScreen> createState() => _AiDataQualityScreenState();
}

class _AiDataQualityScreenState extends State<AiDataQualityScreen> {
  int _currentStep = 0;

  @override
  Widget build(BuildContext context) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        final hasData =
            migrationData.data != null && migrationData.data!.isNotEmpty;

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Workflow Stepper
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AI Data Quality Workflow',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Follow these steps to evaluate and improve your data quality',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 24),
                      _buildWorkflowStepper(),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
              // Current Step Content
              if (!hasData)
                Card(
                  child: Container(
                    padding: const EdgeInsets.all(40),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(
                            Icons.upload_file,
                            size: 64,
                            color: Colors.blue.shade300,
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            'No Data Loaded',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Please load data from the Load Data section to begin',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                )
              else
                _buildStepContent(),
            ],
          ),
        );
      },
    );
  }

  Widget _buildWorkflowStepper() {
    final steps = [
      {'title': 'Evaluate Fitness', 'icon': Icons.health_and_safety},
      {'title': 'Clean Data', 'icon': Icons.auto_fix_high},
      {'title': 'Verify & Export', 'icon': Icons.check_circle},
    ];

    return Row(
      children: List.generate(steps.length * 2 - 1, (index) {
        if (index.isOdd) {
          // Connector line
          final connectorIndex = index ~/ 2;
          return Expanded(
            child: Container(
              height: 2,
              color: connectorIndex < _currentStep
                  ? Colors.green
                  : Colors.grey.shade300,
            ),
          );
        } else {
          // Step circle
          final stepIndex = index ~/ 2;
          final step = steps[stepIndex];
          final isActive = stepIndex == _currentStep;
          final isCompleted = stepIndex < _currentStep;

          return InkWell(
            onTap: () => setState(() => _currentStep = stepIndex),
            child: Column(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: isCompleted
                        ? Colors.green
                        : isActive
                            ? Colors.blue
                            : Colors.grey.shade200,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: isCompleted
                          ? Colors.green
                          : isActive
                              ? Colors.blue
                              : Colors.grey.shade400,
                      width: 2,
                    ),
                  ),
                  child: Icon(
                    isCompleted ? Icons.check : step['icon'] as IconData,
                    color: isCompleted || isActive
                        ? Colors.white
                        : Colors.grey.shade600,
                    size: 28,
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: 100,
                  child: Text(
                    step['title'] as String,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight:
                          isActive ? FontWeight.bold : FontWeight.normal,
                      color: isActive ? Colors.blue : Colors.grey.shade700,
                    ),
                  ),
                ),
              ],
            ),
          );
        }
      }),
    );
  }

  Widget _buildStepContent() {
    switch (_currentStep) {
      case 0:
        return Column(
          children: [
            const FitnessEvaluationSection(),
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                onPressed: () => setState(() => _currentStep = 1),
                icon: const Icon(Icons.arrow_forward),
                label: const Text('Proceed to Cleaning'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 16,
                  ),
                ),
              ),
            ),
          ],
        );
      case 1:
        return Column(
          children: [
            const EvolutionaryCleaningSection(),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton.icon(
                  onPressed: () => setState(() => _currentStep = 0),
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Back to Evaluation'),
                ),
                ElevatedButton.icon(
                  onPressed: () => setState(() => _currentStep = 2),
                  icon: const Icon(Icons.arrow_forward),
                  label: const Text('Verify & Export'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 16,
                    ),
                  ),
                ),
              ],
            ),
          ],
        );
      case 2:
        return Column(
          children: [
            _buildVerifySection(),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () => setState(() => _currentStep = 1),
              icon: const Icon(Icons.arrow_back),
              label: const Text('Back to Cleaning'),
            ),
          ],
        );
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildVerifySection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.check_circle,
                    size: 32, color: Colors.green.shade700),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Verify & Export',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Review your cleaned data and export when ready',
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
            Consumer<MigrationData>(
              builder: (context, migrationData, child) {
                return Column(
                  children: [
                    _buildVerificationCard(
                      'Data Preview',
                      'View your cleaned data in the View Data section',
                      Icons.table_chart,
                      Colors.blue,
                      () {
                        // Navigate to view data section
                      },
                    ),
                    const SizedBox(height: 12),
                    _buildVerificationCard(
                      'Re-evaluate Fitness',
                      'Check the improved fitness scores after cleaning',
                      Icons.health_and_safety,
                      Colors.orange,
                      () => setState(() => _currentStep = 0),
                    ),
                    const SizedBox(height: 12),
                    _buildVerificationCard(
                      'Export Data',
                      'Save your cleaned data to file',
                      Icons.download,
                      Colors.green,
                      () {
                        // Navigate to export section
                      },
                    ),
                    const SizedBox(height: 12),
                    _buildVerificationCard(
                      'Restore Original',
                      'Undo changes and restore original data',
                      Icons.restore,
                      Colors.red,
                      _restoreOriginalData,
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVerificationCard(
    String title,
    String description,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: Colors.white, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade700,
                    ),
                  ),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios, color: color, size: 20),
          ],
        ),
      ),
    );
  }

  Future<void> _restoreOriginalData() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Restore Original Data'),
        content: const Text(
          'Are you sure you want to restore the original data? '
          'All cleaning changes will be lost.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Restore'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final migrationData = Provider.of<MigrationData>(context, listen: false);
      try {
        await migrationData.restoreOriginalData();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Original data restored successfully'),
              backgroundColor: Colors.green,
            ),
          );
          setState(() => _currentStep = 0);
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error restoring data: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }
}
