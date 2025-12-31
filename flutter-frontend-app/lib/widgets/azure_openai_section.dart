import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

/// AI Fix Result model - tracks the result of AI data fixing
class AIFixResult {
  final String message;
  final int cellsFixed;
  final int cellsEvolved;
  final double fitnessImprovement;
  final List<Map<String, dynamic>> modifiedCells;
  final bool success;
  final String method;
  final DateTime timestamp;

  AIFixResult({
    required this.message,
    required this.cellsFixed,
    required this.cellsEvolved,
    required this.fitnessImprovement,
    required this.modifiedCells,
    required this.success,
    required this.method,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class AzureOpenAISection extends StatefulWidget {
  const AzureOpenAISection({Key? key}) : super(key: key);

  @override
  State<AzureOpenAISection> createState() => _AzureOpenAISectionState();
}

class _AzureOpenAISectionState extends State<AzureOpenAISection> {
  final ScrollController _scrollController = ScrollController();

  bool _isLoading = false;
  bool _isConfigured = false;
  bool _isChecking = true;
  String? _configMessage;
  AIFixResult? _lastResult;
  String? _analysisResult;
  String? _currentOperation;

  @override
  void initState() {
    super.initState();
    debugPrint('🔵 [AzureOpenAISection] initState called');
    _checkConfiguration();
  }

  Future<void> _checkConfiguration() async {
    debugPrint('🔵 [AzureOpenAISection] _checkConfiguration started');
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    try {
      debugPrint('🔵 [AzureOpenAISection] Calling checkOpenAIStatus...');
      final status = await migrationData.checkOpenAIStatus();
      debugPrint('🔵 [AzureOpenAISection] Status received: $status');
      if (mounted) {
        setState(() {
          _isConfigured = status['configured'] ?? false;
          _configMessage = status['message'];
          _isChecking = false;
        });
        debugPrint('🔵 [AzureOpenAISection] State updated - isConfigured: $_isConfigured, isChecking: $_isChecking');
      }
    } catch (e) {
      debugPrint('🔴 [AzureOpenAISection] Error checking configuration: $e');
      if (mounted) {
        setState(() {
          _isConfigured = false;
          _configMessage = 'Failed to check configuration: $e';
          _isChecking = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  /// Fix data using AI (LLM-powered cell fixing)
  Future<void> _fixDataWithAI() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    // Check if data is loaded
    if (migrationData.data == null || migrationData.data!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please load a dataset first to use AI features'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _currentOperation = 'Fixing data with AI...';
      _analysisResult = null;
    });

    try {
      // Use the AI chat-modify endpoint to fix data
      final response = await migrationData.sendOpenAIChatModify(
        message: 'fix my data',
        autoExecute: true, // Auto-execute the fixes
      );

      if (mounted) {
        // Get the count of modified cells - try multiple response keys
        final fixesCount = response['fixes_count'] as int? ?? 0;
        final totalCellsModified = response['total_cells_modified'] as int? ?? 0;
        final cellsModified = totalCellsModified > 0 ? totalCellsModified : fixesCount;

        // Get modifications list - try multiple response keys
        final appliedMods = response['applied_modifications'] as List<dynamic>?;
        final mods = response['modifications'] as List<dynamic>?;
        final aiModCells = response['ai_modified_cells'] as List<dynamic>?;
        final modifications = (appliedMods ?? mods ?? aiModCells ?? [])
            .map((e) => Map<String, dynamic>.from(e as Map))
            .toList();

        debugPrint('🟢 AI Fix Response: cellsModified=$cellsModified, modifications=${modifications.length}');
        debugPrint('🟢 Response keys: ${response.keys.toList()}');

        setState(() {
          _lastResult = AIFixResult(
            message: response['message'] ?? 'Data fixing completed',
            cellsFixed: cellsModified,
            cellsEvolved: modifications.length,
            fitnessImprovement: 0.0, // LLM doesn't report this
            modifiedCells: modifications,
            success: response['success'] ?? true,
            method: 'AI (LLM)',
          );
          _isLoading = false;
          _currentOperation = null;
        });

        if (cellsModified > 0 || modifications.isNotEmpty) {
          final count = cellsModified > 0 ? cellsModified : modifications.length;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('AI fixed $count cells in your data'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 3),
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('No cells needed fixing - data is already clean!'),
              backgroundColor: Colors.blue,
              duration: Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _lastResult = AIFixResult(
            message: 'Error: ${e.toString()}',
            cellsFixed: 0,
            cellsEvolved: 0,
            fitnessImprovement: 0.0,
            modifiedCells: [],
            success: false,
            method: 'LLM',
          );
          _isLoading = false;
          _currentOperation = null;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Get AI analysis of a specific type
  Future<void> _getAnalysis(String type) async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    // Check if data is loaded
    if (migrationData.data == null || migrationData.data!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please load a dataset first'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _currentOperation = 'Generating ${type.replaceAll('_', ' ')}...';
      _lastResult = null;
    });

    try {
      final result = await migrationData.getOpenAIAnalysis(type);

      if (mounted) {
        setState(() {
          _analysisResult = result['analysis'] ?? 'No analysis generated';
          _isLoading = false;
          _currentOperation = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _analysisResult = 'Error: ${e.toString()}';
          _isLoading = false;
          _currentOperation = null;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final migrationData = Provider.of<MigrationData>(context);
    final hasData = migrationData.data != null && migrationData.data!.isNotEmpty;
    final aiModifiedCells = migrationData.aiModifiedCells ?? [];

    debugPrint('🔵 [AzureOpenAISection] build called - isChecking: $_isChecking, isConfigured: $_isConfigured, aiModifiedCells: ${aiModifiedCells.length}');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Configuration status banner
        if (_isChecking)
          Container(
            padding: const EdgeInsets.all(12),
            color: Colors.blue.shade50,
            child: const Row(
              children: [
                SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
                SizedBox(width: 12),
                Text('Checking Azure OpenAI configuration...'),
              ],
            ),
          )
        else if (!_isConfigured)
          Container(
            padding: const EdgeInsets.all(12),
            color: Colors.orange.shade50,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.warning_amber, color: Colors.orange.shade700),
                    const SizedBox(width: 8),
                    const Text(
                      'Azure OpenAI Not Configured',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  _configMessage ?? 'Please configure Azure OpenAI credentials',
                  style: TextStyle(color: Colors.grey.shade700, fontSize: 12),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Set these environment variables in python-backend/.env:\n'
                  '- AZURE_OPENAI_API_KEY\n'
                  '- AZURE_OPENAI_ENDPOINT\n'
                  '- AZURE_OPENAI_DEPLOYMENT',
                  style: TextStyle(fontFamily: 'monospace', fontSize: 11),
                ),
              ],
            ),
          ),

        // Main action button - Fix Data with AI
        Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton.icon(
            onPressed: (_isConfigured && hasData && !_isLoading) ? _fixDataWithAI : null,
            icon: _isLoading && _currentOperation?.contains('Fixing') == true
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.auto_fix_high, size: 24),
            label: Text(
              _isLoading && _currentOperation?.contains('Fixing') == true
                  ? 'Fixing Data...'
                  : 'Fix Data with AI',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green.shade600,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),

        // Quick action buttons for analysis
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Expanded(
                child: _ActionButton(
                  label: 'Summary',
                  icon: Icons.summarize,
                  isLoading: _isLoading && _currentOperation?.contains('summary') == true,
                  onTap: _isConfigured && hasData && !_isLoading
                      ? () => _getAnalysis('summary')
                      : null,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _ActionButton(
                  label: 'Quality Report',
                  icon: Icons.assessment,
                  isLoading: _isLoading && _currentOperation?.contains('quality') == true,
                  onTap: _isConfigured && hasData && !_isLoading
                      ? () => _getAnalysis('quality_report')
                      : null,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _ActionButton(
                  label: 'Recommendations',
                  icon: Icons.lightbulb,
                  isLoading: _isLoading && _currentOperation?.contains('recommendations') == true,
                  onTap: _isConfigured && hasData && !_isLoading
                      ? () => _getAnalysis('recommendations')
                      : null,
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),
        const Divider(height: 1),

        // Results area
        Expanded(
          child: SingleChildScrollView(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Loading indicator
                if (_isLoading && _currentOperation != null)
                  Container(
                    padding: const EdgeInsets.all(16),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.shade200),
                    ),
                    child: Row(
                      children: [
                        const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(strokeWidth: 3),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Text(
                            _currentOperation!,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.blue.shade800,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                // AI Fix Result
                if (_lastResult != null) _buildFixResult(_lastResult!),

                // Analysis Result
                if (_analysisResult != null) _buildAnalysisResult(_analysisResult!),

                // AI Modified Cells Summary
                if (aiModifiedCells.isNotEmpty) _buildModifiedCellsSummary(aiModifiedCells),

                // Welcome message when no results
                if (_lastResult == null && _analysisResult == null && !_isLoading)
                  _buildWelcomeMessage(hasData),
              ],
            ),
          ),
        ),
      ],
    );
  }

  /// Build the fix result card with green highlighting
  Widget _buildFixResult(AIFixResult result) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: result.success ? Colors.green.shade50 : Colors.red.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: result.success ? Colors.green.shade300 : Colors.red.shade300,
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with success/error icon
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: result.success ? Colors.green.shade100 : Colors.red.shade100,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(10)),
            ),
            child: Row(
              children: [
                Icon(
                  result.success ? Icons.check_circle : Icons.error,
                  color: result.success ? Colors.green.shade700 : Colors.red.shade700,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        result.success ? 'AI Data Fix Complete' : 'Fix Failed',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: result.success ? Colors.green.shade800 : Colors.red.shade800,
                        ),
                      ),
                      Text(
                        'Method: ${result.method}',
                        style: TextStyle(
                          fontSize: 12,
                          color: result.success ? Colors.green.shade600 : Colors.red.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
                // "Modified by AI" tag
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.shade600,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.auto_fix_high, size: 14, color: Colors.white),
                      SizedBox(width: 4),
                      Text(
                        'Modified by AI',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Stats
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Cells fixed stat
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(Icons.healing, color: Colors.green.shade700, size: 20),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '${result.cellsFixed} cells fixed',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                // Message
                Text(
                  result.message,
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade700),
                ),
                // Show modified cells list if available
                if (result.modifiedCells.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  TextButton.icon(
                    onPressed: () => _showModificationDetails(result.modifiedCells),
                    icon: const Icon(Icons.visibility, size: 18),
                    label: Text('View ${result.modifiedCells.length} modified cells'),
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.green.shade700,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build analysis result card
  Widget _buildAnalysisResult(String analysis) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.cyan.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.cyan.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.analytics, color: Colors.cyan.shade700, size: 24),
              const SizedBox(width: 8),
              const Text(
                'AI Analysis',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SelectableText(
            analysis,
            style: TextStyle(fontSize: 14, color: Colors.grey.shade800),
          ),
        ],
      ),
    );
  }

  /// Build summary of all AI-modified cells
  Widget _buildModifiedCellsSummary(List<Map<String, dynamic>> cells) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.shade300, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.green.shade100,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(10)),
            ),
            child: Row(
              children: [
                Icon(Icons.auto_fix_high, color: Colors.green.shade700, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${cells.length} Cells Modified by AI',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.green.shade800,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.shade600,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Text(
                    'Modified by AI',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Cell list preview (show first 5)
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                ...cells.take(5).map((cell) => _buildCellModificationRow(cell)),
                if (cells.length > 5)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: TextButton.icon(
                      onPressed: () => _showModificationDetails(cells),
                      icon: const Icon(Icons.expand_more, size: 18),
                      label: Text('View all ${cells.length} modifications'),
                      style: TextButton.styleFrom(
                        foregroundColor: Colors.green.shade700,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Build a single cell modification row
  Widget _buildCellModificationRow(Map<String, dynamic> cell) {
    final row = cell['row'] ?? '?';
    final colName = cell['col_name'] ?? cell['column'] ?? 'col ${cell['col']}';
    final oldValue = cell['original_value'] ?? cell['old_value'] ?? 'null';
    final newValue = cell['evolved_value'] ?? cell['new_value'] ?? '?';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Row(
        children: [
          // Row/Column info
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.blue.shade100,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              'R$row',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade800,
              ),
            ),
          ),
          const SizedBox(width: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.purple.shade100,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              colName.toString(),
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: Colors.purple.shade800,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 8),
          // Old value (struck through)
          Expanded(
            child: Text(
              oldValue.toString(),
              style: TextStyle(
                fontSize: 12,
                color: Colors.red.shade600,
                decoration: TextDecoration.lineThrough,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Icon(Icons.arrow_forward, size: 14, color: Colors.grey.shade400),
          const SizedBox(width: 4),
          // New value (green, bold)
          Expanded(
            child: Text(
              newValue.toString(),
              style: TextStyle(
                fontSize: 12,
                color: Colors.green.shade700,
                fontWeight: FontWeight.bold,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  /// Build welcome message when no results
  Widget _buildWelcomeMessage(bool hasData) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.auto_fix_high,
            size: 48,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            'AI Data Assistant',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            hasData
                ? 'Click "Fix Data with AI" to automatically fix error cells in your data.\nOr use the analysis buttons to get insights about your dataset.'
                : 'Load a dataset first to use AI features.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }

  /// Show modification details dialog
  void _showModificationDetails(List<Map<String, dynamic>> modifications) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.auto_fix_high, color: Colors.green.shade700),
            const SizedBox(width: 8),
            const Text('AI Cell Modifications'),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.green.shade100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${modifications.length} cells',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.green.shade700,
                ),
              ),
            ),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          height: 400,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: modifications.length,
            itemBuilder: (context, index) {
              final mod = modifications[index];
              final row = mod['row'] ?? '?';
              final colName = mod['col_name'] ?? mod['column'] ?? 'col ${mod['col']}';
              final oldValue = mod['original_value'] ?? mod['old_value'];
              final newValue = mod['evolved_value'] ?? mod['new_value'];

              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                color: Colors.green.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.blue.shade100,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              'Row $row',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue.shade800,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.purple.shade100,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              '$colName',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Colors.purple.shade800,
                              ),
                            ),
                          ),
                          const Spacer(),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.green.shade600,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Text(
                              'AI',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Old value:',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                                Text(
                                  '${oldValue ?? 'null'}',
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Colors.red.shade700,
                                    decoration: TextDecoration.lineThrough,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 8),
                            child: Icon(Icons.arrow_forward, size: 16, color: Colors.grey.shade400),
                          ),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'New value:',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                                Text(
                                  '$newValue',
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Colors.green.shade700,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

/// Action button widget for analysis actions
class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isLoading;
  final VoidCallback? onTap;

  const _ActionButton({
    required this.label,
    required this.icon,
    this.isLoading = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onTap,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.cyan.shade100,
        foregroundColor: Colors.cyan.shade800,
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        elevation: 0,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          isLoading
              ? SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.cyan.shade700,
                  ),
                )
              : Icon(icon, size: 20),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
