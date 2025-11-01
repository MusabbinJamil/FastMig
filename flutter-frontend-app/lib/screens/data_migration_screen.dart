import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';
import '../widgets/side_menu.dart';
import '../widgets/load_data_section.dart';
import '../widgets/process_data_section.dart';
import '../widgets/macro_recording_section.dart';
import '../widgets/data_table_section.dart';
import '../widgets/export_section.dart';
import '../widgets/fitness_evaluation_section.dart';
import '../widgets/evolutionary_cleaning_section.dart';

class DataMigrationScreen extends StatefulWidget {
  const DataMigrationScreen({Key? key}) : super(key: key);

  @override
  State<DataMigrationScreen> createState() => _DataMigrationScreenState();
}

class _DataMigrationScreenState extends State<DataMigrationScreen>
    with SingleTickerProviderStateMixin {
  int _selectedIndex = 0;
  late AnimationController _animationController;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(1, 0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOutCubic,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _onMenuItemSelected(int index) {
    setState(() {
      _selectedIndex = index;
    });
    _animationController.reset();
    _animationController.forward();
  }

  Widget _getSelectedScreen() {
    switch (_selectedIndex) {
      case 0:
        return const LoadDataSection();
      case 1:
        return const ProcessDataSection();
      case 2:
        return const MacroRecordingSection();
      case 3:
        return const DataTableSection();
      case 4:
        return const ExportSection();
      case 5:
        return const FitnessEvaluationSection();
      case 6:
        return const EvolutionaryCleaningSection();
      case 7:
        return _buildSettingsScreen();
      case 8:
        return _buildHelpScreen();
      default:
        return const LoadDataSection();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Side Menu
          SideMenu(
            selectedIndex: _selectedIndex,
            onItemSelected: _onMenuItemSelected,
          ),
          // Main Content
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.grey.shade50,
                    Colors.grey.shade100,
                  ],
                ),
              ),
              child: Column(
                children: [
                  // Top Bar
                  _buildTopBar(),
                  // Content Area
                  Expanded(
                    child: SlideTransition(
                      position: _slideAnimation,
                      child: FadeTransition(
                        opacity: _animationController,
                        child: Padding(
                          padding: const EdgeInsets.all(20.0),
                          child: _getSelectedScreen(),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Title
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _getPageTitle(),
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _getPageSubtitle(),
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
          const Spacer(),
          // Action Buttons
          Consumer<MigrationData>(
            builder: (context, migrationData, child) {
              return Row(
                children: [
                  // File Info
                  if (migrationData.fileName != null) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.description,
                              size: 16, color: Colors.blue.shade700),
                          const SizedBox(width: 8),
                          Text(
                            migrationData.fileName!,
                            style: TextStyle(
                              color: Colors.blue.shade700,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  // Recording Status
                  if (migrationData.isRecording)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red.shade200),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: Colors.red,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            'Recording',
                            style: TextStyle(
                              color: Colors.red,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  String _getPageTitle() {
    switch (_selectedIndex) {
      case 0:
        return 'Load Data';
      case 1:
        return 'Convert Fields';
      case 2:
        return 'Record Macro';
      case 3:
        return 'View Data';
      case 4:
        return 'Export Data';
      case 5:
        return 'Data Fitness';
      case 6:
        return 'AI Cleaning';
      case 7:
        return 'Settings';
      case 8:
        return 'Help';
      default:
        return 'FastMig';
    }
  }

  String _getPageSubtitle() {
    switch (_selectedIndex) {
      case 0:
        return 'Import your data from various file formats';
      case 1:
        return 'Transform and convert column data types';
      case 2:
        return 'Record actions for automated workflows';
      case 3:
        return 'View and analyze your data';
      case 4:
        return 'Export processed data to desired format';
      case 5:
        return 'Assess the health and quality of your data';
      case 6:
        return 'Use AI algorithms to intelligently clean your data';
      case 7:
        return 'Configure application settings';
      case 8:
        return 'Get help and documentation';
      default:
        return '';
    }
  }

  Widget _buildSettingsScreen() {
    return Center(
      child: Card(
        elevation: 2,
        child: Container(
          padding: const EdgeInsets.all(40),
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.settings, size: 64, color: Colors.blue.shade700),
              const SizedBox(height: 20),
              const Text(
                'Settings',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              Text(
                'Configure your application preferences',
                style: TextStyle(color: Colors.grey.shade600),
              ),
              const SizedBox(height: 30),
              ListTile(
                leading: const Icon(Icons.language),
                title: const Text('Language'),
                subtitle: const Text('English'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {},
              ),
              ListTile(
                leading: const Icon(Icons.palette),
                title: const Text('Theme'),
                subtitle: const Text('Light Mode'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {},
              ),
              ListTile(
                leading: const Icon(Icons.storage),
                title: const Text('Default Export Path'),
                subtitle: const Text('Downloads'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {},
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHelpScreen() {
    return SingleChildScrollView(
      child: Center(
        child: Card(
          elevation: 2,
          child: Container(
            padding: const EdgeInsets.all(40),
            constraints: const BoxConstraints(maxWidth: 800),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.help_outline,
                        size: 48, color: Colors.blue.shade700),
                    const SizedBox(width: 16),
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Help & Documentation',
                          style: TextStyle(
                              fontSize: 24, fontWeight: FontWeight.bold),
                        ),
                        Text('Learn how to use FastMig effectively'),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 30),
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
                const SizedBox(height: 20),
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
                const SizedBox(height: 20),
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
                const SizedBox(height: 20),
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
        const SizedBox(height: 10),
        ...items.map(
          (item) => Padding(
            padding: const EdgeInsets.only(left: 16, bottom: 8),
            child: Row(
              children: [
                Icon(Icons.check_circle,
                    size: 16, color: Colors.green.shade600),
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
