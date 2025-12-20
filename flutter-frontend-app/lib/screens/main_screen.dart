import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';
import '../widgets/data_table_section.dart';
import '../widgets/load_data_section.dart';
import '../widgets/process_data_section.dart';
import '../widgets/macro_recording_section.dart';
import '../widgets/etl_operations_section.dart';
import '../widgets/encoding_section.dart';
import '../widgets/export_section.dart';
import '../widgets/fitness_evaluation_section.dart';
import '../widgets/evolutionary_cleaning_section.dart';
import '../widgets/console_view.dart';
import '../widgets/dev_settings_panel.dart';
import 'ga_evolution_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({Key? key}) : super(key: key);

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  String _activeDialog = '';

  void _showDialog(String dialogType) {
    setState(() {
      _activeDialog = dialogType;
    });
  }

  void _closeDialog() {
    setState(() {
      _activeDialog = '';
    });
  }

  void _navigateToGAScreen() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const GAEvolutionScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      body: Column(
        children: [
          // Top Header Bar (Excel-like ribbon)
          _buildHeaderBar(),
          // Main Content Area - Data Table with Side Panel
          Expanded(
            child: Row(
              children: [
                // Data Table (left side, takes remaining space)
                Expanded(
                  flex: _activeDialog.isNotEmpty ? 6 : 10,
                  child: const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: DataTableSection(),
                  ),
                ),
                // Side Panel (right side, appears when dialog is active)
                if (_activeDialog.isNotEmpty)
                  Expanded(
                    flex: 4,
                    child: _buildSidePanel(_activeDialog),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderBar() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // Title Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.blue.shade700, Colors.blue.shade800],
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.flash_on, color: Colors.white, size: 24),
                const SizedBox(width: 8),
                const Text(
                  'FastMig',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 16),
                Consumer<MigrationData>(
                  builder: (context, migrationData, child) {
                    if (migrationData.fileName != null) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.description,
                                size: 16, color: Colors.white),
                            const SizedBox(width: 6),
                            Text(
                              migrationData.fileName!,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                      );
                    }
                    return const SizedBox.shrink();
                  },
                ),
                const Spacer(),
                Consumer<MigrationData>(
                  builder: (context, migrationData, child) {
                    if (migrationData.isRecording) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                color: Colors.white,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 8),
                            const Text(
                              'Recording Steps',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      );
                    }
                    return const SizedBox.shrink();
                  },
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.engineering, color: Colors.white),
                  onPressed: () => _showDialog('devsettings'),
                  tooltip: 'Development Settings',
                ),
                IconButton(
                  icon: const Icon(Icons.help_outline, color: Colors.white),
                  onPressed: () => _showDialog('help'),
                  tooltip: 'Help',
                ),
              ],
            ),
          ),
          // Feature Ribbon
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildRibbonSection(
                    'Data',
                    [
                      _RibbonButton(
                        icon: Icons.upload_file,
                        label: 'Load Data',
                        color: Colors.green,
                        onPressed: () => _showDialog('load'),
                        featureKey: 'none',
                      ),
                      _RibbonButton(
                        icon: Icons.download,
                        label: 'Export',
                        color: Colors.blue,
                        onPressed: () => _showDialog('export'),
                        featureKey: 'export',
                      ),
                    ],
                  ),
                  const VerticalDivider(width: 24),
                  _buildRibbonSection(
                    'Transform',
                    [
                      _RibbonButton(
                        icon: Icons.transform,
                        label: 'Convert Fields',
                        color: Colors.orange,
                        onPressed: () => _showDialog('convert'),
                        featureKey: 'convert',
                      ),
                      _RibbonButton(
                        icon: Icons.auto_awesome,
                        label: 'ETL Operations',
                        color: Colors.purple,
                        onPressed: () => _showDialog('etl'),
                        featureKey: 'etl',
                      ),
                      _RibbonButton(
                        icon: Icons.code,
                        label: 'Encoding',
                        color: Colors.indigo,
                        onPressed: () => _showDialog('encoding'),
                        featureKey: 'encoding',
                      ),
                    ],
                  ),
                  const VerticalDivider(width: 24),
                  _buildRibbonSection(
                    'Automation',
                    [
                      _RibbonButton(
                        icon: Icons.video_camera_back,
                        label: 'Record Steps',
                        color: Colors.red,
                        onPressed: () => _showDialog('record'),
                        featureKey: 'record',
                      ),
                    ],
                  ),
                  const VerticalDivider(width: 24),
                  _buildRibbonSection(
                    'AI Features',
                    [
                      _RibbonButton(
                        icon: Icons.health_and_safety,
                        label: 'Data Fitness',
                        color: Colors.teal,
                        onPressed: () => _showDialog('fitness'),
                        featureKey: 'fitness',
                      ),
                      _RibbonButton(
                        icon: Icons.auto_fix_high,
                        label: 'AI Cleaning',
                        color: Colors.pink,
                        onPressed: () => _showDialog('cleaning'),
                        featureKey: 'cleaning',
                      ),
                      _RibbonButton(
                        icon: Icons.biotech,
                        label: 'GA Evolution',
                        color: Colors.deepPurple,
                        onPressed: () => _navigateToGAScreen(),
                        featureKey: 'ga',
                      ),
                    ],
                  ),
                  const VerticalDivider(width: 24),
                  _buildRibbonSection(
                    'Tools',
                    [
                      _RibbonButton(
                        icon: Icons.terminal,
                        label: 'Console',
                        color: Colors.green,
                        onPressed: () => _showDialog('console'),
                        featureKey: 'console',
                      ),
                      _RibbonButton(
                        icon: Icons.engineering,
                        label: 'Dev Settings',
                        color: Colors.amber,
                        onPressed: () => _showDialog('devsettings'),
                        featureKey: 'none',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRibbonSection(String title, List<_RibbonButton> buttons) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey.shade600,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: buttons
                .map((btn) => Padding(
                      padding: const EdgeInsets.only(right: 4),
                      child: _buildRibbonButton(btn),
                    ))
                .toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildRibbonButton(_RibbonButton button) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        bool isEnabled = button.isEnabled(migrationData);

        return Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isEnabled ? button.onPressed : null,
            borderRadius: BorderRadius.circular(8),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                border: Border.all(
                  color:
                      isEnabled ? Colors.grey.shade300 : Colors.grey.shade200,
                ),
                borderRadius: BorderRadius.circular(8),
                color: isEnabled ? Colors.transparent : Colors.grey.shade100,
              ),
              child: Opacity(
                opacity: isEnabled ? 1.0 : 0.5,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(button.icon, color: button.color, size: 28),
                    const SizedBox(height: 4),
                    Text(
                      button.label,
                      style: const TextStyle(fontSize: 11),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSidePanel(String dialogType) {
    return Container(
      margin: const EdgeInsets.only(top: 16, right: 16, bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(-2, 0),
          ),
        ],
      ),
      child: Column(
        children: [
          // Panel Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
              border: Border(
                bottom: BorderSide(color: Colors.grey.shade300),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  _getDialogIcon(dialogType),
                  color: _getDialogColor(dialogType),
                  size: 24,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _getDialogTitle(dialogType),
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: _closeDialog,
                  tooltip: 'Close Panel',
                ),
              ],
            ),
          ),
          // Panel Content
          Expanded(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: _getDialogContent(dialogType),
              ),
            ),
          ),
        ],
      ),
    );
  }

  IconData _getDialogIcon(String dialogType) {
    switch (dialogType) {
      case 'load':
        return Icons.upload_file;
      case 'export':
        return Icons.download;
      case 'convert':
        return Icons.transform;
      case 'etl':
        return Icons.auto_awesome;
      case 'encoding':
        return Icons.code;
      case 'record':
        return Icons.video_camera_back;
      case 'fitness':
        return Icons.health_and_safety;
      case 'cleaning':
        return Icons.auto_fix_high;
      case 'console':
        return Icons.terminal;
      case 'devsettings':
        return Icons.engineering;
      case 'help':
        return Icons.help_outline;
      default:
        return Icons.info;
    }
  }

  Color _getDialogColor(String dialogType) {
    switch (dialogType) {
      case 'load':
        return Colors.green;
      case 'export':
        return Colors.blue;
      case 'convert':
        return Colors.orange;
      case 'etl':
        return Colors.purple;
      case 'encoding':
        return Colors.indigo;
      case 'record':
        return Colors.red;
      case 'fitness':
        return Colors.teal;
      case 'cleaning':
        return Colors.pink;
      case 'console':
        return Colors.green;
      case 'devsettings':
        return Colors.amber;
      default:
        return Colors.blue;
    }
  }

  String _getDialogTitle(String dialogType) {
    switch (dialogType) {
      case 'load':
        return 'Load Data';
      case 'export':
        return 'Export Data';
      case 'convert':
        return 'Convert Fields';
      case 'etl':
        return 'ETL Operations';
      case 'encoding':
        return 'Machine Readable Encoding';
      case 'record':
        return 'Record & Replay Steps';
      case 'fitness':
        return 'Data Fitness Evaluation';
      case 'cleaning':
        return 'AI Data Cleaning';
      case 'console':
        return 'Console Output';
      case 'devsettings':
        return 'Development Settings';
      case 'help':
        return 'Help & Documentation';
      default:
        return 'Dialog';
    }
  }

  Widget _getDialogContent(String dialogType) {
    switch (dialogType) {
      case 'load':
        return const LoadDataSection();
      case 'export':
        return const ExportSection();
      case 'convert':
        return const ProcessDataSection();
      case 'etl':
        return const EtlOperationsSection();
      case 'encoding':
        return Consumer<MigrationData>(
          builder: (context, migrationData, child) {
            return EncodingSection(
              columns: migrationData.columns ?? [],
            );
          },
        );
      case 'record':
        return const StepRecordingSection();
      case 'fitness':
        return const FitnessEvaluationSection();
      case 'cleaning':
        return const EvolutionaryCleaningSection();
      case 'console':
        return const ConsoleView();
      case 'devsettings':
        return const DevSettingsPanel();
      case 'help':
        return _buildHelpContent();
      default:
        return const Center(child: Text('Content not available'));
    }
  }

  Widget _buildHelpContent() {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHelpSection(
              'Supported File Formats',
              [
                'CSV (any delimiter)',
                'Excel (.xlsx, .xls)',
                'JSON (standard and line-delimited)',
                'XML',
                'TSV',
                'TXT (delimited)',
              ],
            ),
            const SizedBox(height: 24),
            _buildHelpSection(
              'Data Type Conversions',
              [
                'String/Text',
                'Integer',
                'Decimal/Float',
                'DateTime (with custom format support)',
                'Boolean',
                'Category',
                'Object',
              ],
            ),
            const SizedBox(height: 24),
            _buildHelpSection(
              'AI-Powered Features',
              [
                'Data Fitness Evaluation - Assess health scores (0-100%) for each record',
                'Missing Values Detection - Identify and categorize data quality issues',
                'Genetic Algorithm (GA) - Evolve populations for mixed data types',
                'Particle Swarm Optimization (PSO) - Best for numeric continuous values',
                'Differential Evolution (DE) - Robust optimization for complex distributions',
                'Evolution Strategy (ES) - Consistent improvements with self-adaptation',
                'Hybrid Method (Recommended) - Auto-selects best algorithm per column',
                'AI Modification Tracking - Transparent "Modified_by_AI" column tracking',
              ],
            ),
            const SizedBox(height: 24),
            _buildHelpSection(
              'ETL Operations',
              [
                'Remove Duplicates',
                'Fill Missing Values',
                'Replace Values',
                'Filter Rows',
                'Sort Data',
                'Group By Columns',
                'Add Custom Columns',
                'Merge Columns',
                'Split Columns',
                'Pivot & Unpivot',
              ],
            ),
            const SizedBox(height: 24),
            _buildHelpSection(
              'Key Features',
              [
                'Automatic encoding detection',
                'Automatic delimiter detection',
                'Macro recording for repeated workflows',
                'Real-time data preview',
                'Multiple export formats',
                'Error handling and validation',
                'Evolutionary data cleaning with 5 algorithms',
                'Statistical distribution preservation',
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHelpSection(String title, List<String> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...items.map(
          (item) => Padding(
            padding: const EdgeInsets.only(left: 16, bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.check_circle,
                    size: 18, color: Colors.green.shade600),
                const SizedBox(width: 8),
                Expanded(child: Text(item)),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _RibbonButton {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onPressed;
  final String featureKey;

  _RibbonButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onPressed,
    required this.featureKey,
  });

  bool isEnabled(MigrationData migrationData) {
    switch (featureKey) {
      case 'etl':
        return migrationData.enableETL;
      case 'convert':
        return migrationData.enableConvertFields;
      case 'record':
        return migrationData.enableMacroRecording;
      case 'fitness':
        return migrationData.enableDataFitness;
      case 'cleaning':
        return migrationData.enableAICleaning;
      case 'encoding':
        return migrationData.enableEncoding;
      case 'export':
        return migrationData.enableExport;
      case 'console':
        return migrationData.enableConsole;
      default:
        return true;
    }
  }
}
