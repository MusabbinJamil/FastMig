import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class DevSettingsPanel extends StatelessWidget {
  const DevSettingsPanel({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  border: Border(
                    bottom: BorderSide(color: Colors.amber.shade200),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(Icons.engineering,
                        color: Colors.amber.shade700, size: 24),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Development Settings',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            'Toggle features on/off for development and debugging',
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
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Section: Feature Toggles
                    Text(
                      'Feature Controls',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildToggleTile(
                      icon: Icons.auto_awesome,
                      title: 'ETL Operations',
                      subtitle:
                          'Data transformation and ETL pipeline operations',
                      value: migrationData.enableETL,
                      onChanged: (_) => migrationData.toggleETL(),
                      color: Colors.purple,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.transform,
                      title: 'Convert Fields',
                      subtitle: 'Field type conversion and formatting',
                      value: migrationData.enableConvertFields,
                      onChanged: (_) => migrationData.toggleConvertFields(),
                      color: Colors.orange,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.psychology,
                      title: 'AI Features',
                      subtitle:
                          'Data fitness, AI cleaning, and evolutionary algorithms',
                      value: migrationData.enableAIFeatures,
                      onChanged: (_) => migrationData.toggleAIFeatures(),
                      color: Colors.pink,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.health_and_safety,
                      title: 'Data Fitness',
                      subtitle: 'Analyze and measure data quality',
                      value: migrationData.enableDataFitness,
                      onChanged: (_) => migrationData.toggleDataFitness(),
                      color: Colors.teal,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.auto_fix_high,
                      title: 'AI Cleaning',
                      subtitle: 'Intelligent data cleaning and correction',
                      value: migrationData.enableAICleaning,
                      onChanged: (_) => migrationData.toggleAICleaning(),
                      color: Colors.cyan,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.video_camera_back,
                      title: 'Macro Recording',
                      subtitle: 'Record and replay user action workflows',
                      value: migrationData.enableMacroRecording,
                      onChanged: (_) => migrationData.toggleMacroRecording(),
                      color: Colors.red,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.code,
                      title: 'Encoding',
                      subtitle: 'Character encoding and conversion',
                      value: migrationData.enableEncoding,
                      onChanged: (_) => migrationData.toggleEncoding(),
                      color: Colors.indigo,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.download,
                      title: 'Export',
                      subtitle: 'Export data to files',
                      value: migrationData.enableExport,
                      onChanged: (_) => migrationData.toggleExport(),
                      color: Colors.blue,
                    ),
                    const SizedBox(height: 8),
                    _buildToggleTile(
                      icon: Icons.terminal,
                      title: 'Console',
                      subtitle: 'Developer console and logging',
                      value: migrationData.enableConsole,
                      onChanged: (_) => migrationData.toggleConsole(),
                      color: Colors.green,
                    ),
                    const SizedBox(height: 24),
                    // Section: Feature Status
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        border: Border.all(color: Colors.blue.shade200),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.info_outline,
                                  color: Colors.blue.shade700, size: 18),
                              const SizedBox(width: 8),
                              const Text(
                                'Feature Status',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          _buildStatusBadge(
                            'ETL Operations',
                            migrationData.enableETL,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'Convert Fields',
                            migrationData.enableConvertFields,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'AI Features',
                            migrationData.enableAIFeatures,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'Data Fitness',
                            migrationData.enableDataFitness,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'AI Cleaning',
                            migrationData.enableAICleaning,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'Macro Recording',
                            migrationData.enableMacroRecording,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'Encoding',
                            migrationData.enableEncoding,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'Export',
                            migrationData.enableExport,
                          ),
                          const SizedBox(height: 6),
                          _buildStatusBadge(
                            'Console',
                            migrationData.enableConsole,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Section: Quick Actions
                    Text(
                      'Quick Actions',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildActionButton(
                      icon: Icons.check_circle_outline,
                      label: 'Enable All Features',
                      onPressed: () {
                        migrationData.setETL(true);
                        migrationData.setConvertFields(true);
                        migrationData.setAIFeatures(true);
                        migrationData.setDataFitness(true);
                        migrationData.setAICleaning(true);
                        migrationData.setMacroRecording(true);
                        migrationData.setEncoding(true);
                        migrationData.setExport(true);
                        migrationData.setConsole(true);
                      },
                      color: Colors.green,
                    ),
                    const SizedBox(height: 8),
                    _buildActionButton(
                      icon: Icons.block,
                      label: 'Disable All Features',
                      onPressed: () {
                        migrationData.setETL(false);
                        migrationData.setConvertFields(false);
                        migrationData.setAIFeatures(false);
                        migrationData.setDataFitness(false);
                        migrationData.setAICleaning(false);
                        migrationData.setMacroRecording(false);
                        migrationData.setEncoding(false);
                        migrationData.setExport(false);
                        migrationData.setConsole(false);
                      },
                      color: Colors.red,
                    ),
                    const SizedBox(height: 8),
                    _buildActionButton(
                      icon: Icons.settings_backup_restore,
                      label: 'Reset to Defaults',
                      onPressed: () {
                        migrationData.setETL(true);
                        migrationData.setConvertFields(true);
                        migrationData.setAIFeatures(true);
                        migrationData.setDataFitness(true);
                        migrationData.setAICleaning(true);
                        migrationData.setMacroRecording(true);
                        migrationData.setEncoding(true);
                        migrationData.setExport(true);
                        migrationData.setConsole(true);
                      },
                      color: Colors.blue,
                    ),
                    const SizedBox(height: 24),
                    // Section: Info
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'About Development Features',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                              color: Colors.grey.shade900,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'These settings allow you to enable or disable specific features during development and testing. Disabling features hides their UI elements and prevents their operations from running.\n\n'
                            '• ETL Operations: Transform, filter, and process data\n'
                            '• Convert Fields: Transform field types and formats\n'
                            '• AI Features: Machine learning and evolutionary algorithms\n'
                            '• Data Fitness: Analyze and measure data quality\n'
                            '• AI Cleaning: Intelligent data cleaning and correction\n'
                            '• Macro Recording: Automate and replay user workflows\n'
                            '• Encoding: Character encoding and conversion\n'
                            '• Export: Export data to files\n'
                            '• Console: Developer console and logging\n\n'
                            'Use "Reset to Defaults" to restore all features to enabled state.',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey.shade700,
                              height: 1.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildToggleTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required bool value,
    required Function(bool) onChanged,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(
          color: value ? color.withOpacity(0.3) : Colors.grey.shade300,
        ),
        borderRadius: BorderRadius.circular(8),
        color: value ? color.withOpacity(0.05) : Colors.transparent,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey.shade600,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: color,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(String label, bool isEnabled) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isEnabled ? Colors.green : Colors.grey.shade400,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey.shade800,
          ),
        ),
        const Spacer(),
        Text(
          isEnabled ? 'Enabled' : 'Disabled',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: isEnabled ? Colors.green : Colors.grey,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
    required Color color,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          decoration: BoxDecoration(
            border: Border.all(color: color.withOpacity(0.3)),
            borderRadius: BorderRadius.circular(8),
            color: color.withOpacity(0.05),
          ),
          child: Row(
            children: [
              Icon(icon, color: color, size: 18),
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w600,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
