import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

/// Chat message model
class ChatMessage {
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final List<Map<String, dynamic>>? suggestedActions;
  final List<Map<String, dynamic>>? appliedModifications;
  final int? cellsModified;
  final bool needsConfirmation;
  final int? fixesCount;

  ChatMessage({
    required this.content,
    required this.isUser,
    DateTime? timestamp,
    this.suggestedActions,
    this.appliedModifications,
    this.cellsModified,
    this.needsConfirmation = false,
    this.fixesCount,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() => {
        'role': isUser ? 'user' : 'assistant',
        'content': content,
      };
}

class AzureOpenAISection extends StatefulWidget {
  const AzureOpenAISection({Key? key}) : super(key: key);

  @override
  State<AzureOpenAISection> createState() => _AzureOpenAISectionState();
}

class _AzureOpenAISectionState extends State<AzureOpenAISection> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];

  bool _isLoading = false;
  bool _isConfigured = false;
  bool _isChecking = true;
  String? _configMessage;
  bool _hasPendingModifications = false;

  @override
  void initState() {
    super.initState();
    debugPrint('🔵 [AzureOpenAISection] initState called');
    _checkConfiguration();
    _addWelcomeMessage();
    debugPrint('🔵 [AzureOpenAISection] initState complete, messages count: ${_messages.length}');
  }

  void _addWelcomeMessage() {
    _messages.add(ChatMessage(
      content: '''Hello! I'm your AI Data Assistant powered by Azure OpenAI.

I can help you:
- Analyze your data and identify quality issues
- Fill missing values with smart suggestions
- Remove duplicates and clean data
- Transform columns (rename, change case, etc.)
- Answer questions about your dataset

Just type your request or question below!''',
      isUser: false,
    ));
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
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

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

    // Add user message
    setState(() {
      _messages.add(ChatMessage(content: message, isUser: true));
      _isLoading = true;
    });
    _messageController.clear();
    _scrollToBottom();

    try {
      // Use preview mode (autoExecute: false) - user must confirm changes
      final response = await migrationData.sendOpenAIChatModify(
        message: message,
        autoExecute: false,  // Preview mode
      );

      if (mounted) {
        final needsConfirmation = response['needs_confirmation'] ?? false;
        final fixesCount = response['fixes_count'] as int? ?? 0;
        final modifications = (response['modifications'] as List<dynamic>?)
            ?.cast<Map<String, dynamic>>();

        String responseContent = response['message'] ?? 'No response received';

        setState(() {
          _messages.add(ChatMessage(
            content: responseContent,
            isUser: false,
            appliedModifications: modifications,
            needsConfirmation: needsConfirmation,
            fixesCount: fixesCount,
          ));
          _isLoading = false;
          _hasPendingModifications = needsConfirmation;
        });
        _scrollToBottom();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: 'Error: ${e.toString()}',
            isUser: false,
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  Future<void> _applyModifications() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _isLoading = true;
    });

    try {
      final result = await migrationData.applyAIModifications();

      if (mounted) {
        final cellsModified = result['total_cells_modified'] as int? ?? 0;

        setState(() {
          _messages.add(ChatMessage(
            content: '**Applied $cellsModified modifications successfully!**\n\nYour data has been updated.',
            isUser: false,
            cellsModified: cellsModified,
          ));
          _isLoading = false;
          _hasPendingModifications = false;
        });
        _scrollToBottom();

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Applied $cellsModified fixes to your data'),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: 'Error applying modifications: ${e.toString()}',
            isUser: false,
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  Future<void> _cancelModifications() async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    try {
      await migrationData.cancelAIModifications();

      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: 'Modifications cancelled. Your data remains unchanged.',
            isUser: false,
          ));
          _hasPendingModifications = false;
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Error cancelling: $e');
    }
  }

  Future<void> _executeCommand(String command) async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _messages.add(ChatMessage(content: 'Executing: $command', isUser: true));
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      final result = await migrationData.executeOpenAICommand(command);

      if (mounted) {
        final success = result['success'] ?? false;
        final message = result['message'] ?? result['description'] ?? 'Command executed';

        setState(() {
          _messages.add(ChatMessage(
            content: success
                ? 'Done! $message'
                : 'Could not execute: $message',
            isUser: false,
          ));
          _isLoading = false;
        });
        _scrollToBottom();

        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(message),
              backgroundColor: Colors.green,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: 'Error executing command: ${e.toString()}',
            isUser: false,
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  Future<void> _getAnalysis(String type) async {
    final migrationData = Provider.of<MigrationData>(context, listen: false);

    setState(() {
      _messages.add(ChatMessage(
        content: 'Generate ${type.replaceAll('_', ' ')}',
        isUser: true,
      ));
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      final result = await migrationData.getOpenAIAnalysis(type);

      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: result['analysis'] ?? 'No analysis generated',
            isUser: false,
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            content: 'Error: ${e.toString()}',
            isUser: false,
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  void _executeSuggestedAction(Map<String, dynamic> action) {
    final type = action['type'] as String?;
    final column = action['column'] as String?;
    final method = action['method'] as String?;

    String command;
    switch (type) {
      case 'fill_nulls':
        command = 'Fill missing values in $column column with $method';
        break;
      case 'remove_nulls':
        command = 'Remove rows with null values';
        break;
      case 'remove_duplicates':
        command = 'Remove duplicate rows';
        break;
      case 'remove_column':
        command = 'Remove the $column column';
        break;
      default:
        command = 'Apply ${action['type']} to data';
    }

    _executeCommand(command);
  }

  @override
  Widget build(BuildContext context) {
    debugPrint('🔵 [AzureOpenAISection] build called - isChecking: $_isChecking, isConfigured: $_isConfigured, messages: ${_messages.length}');
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

        // Quick action buttons
        Padding(
          padding: const EdgeInsets.all(8),
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _QuickActionChip(
                label: 'Summary',
                icon: Icons.summarize,
                onTap: () => _getAnalysis('summary'),
              ),
              _QuickActionChip(
                label: 'Quality Report',
                icon: Icons.assessment,
                onTap: () => _getAnalysis('quality_report'),
              ),
              _QuickActionChip(
                label: 'Recommendations',
                icon: Icons.lightbulb,
                onTap: () => _getAnalysis('recommendations'),
              ),
            ],
          ),
        ),

        const Divider(height: 1),

        // Chat messages
        Expanded(
          child: ListView.builder(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length + (_isLoading ? 1 : 0),
            itemBuilder: (context, index) {
              if (index == _messages.length && _isLoading) {
                return _buildTypingIndicator();
              }
              return _buildMessageBubble(_messages[index]);
            },
          ),
        ),

        // Input area
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey.shade100,
            border: Border(
              top: BorderSide(color: Colors.grey.shade300),
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _messageController,
                  decoration: InputDecoration(
                    hintText: 'Ask about your data or give a command...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: Colors.white,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                  ),
                  enabled: _isConfigured && !_isLoading,
                  onSubmitted: (_) => _sendMessage(),
                  maxLines: null,
                  textInputAction: TextInputAction.send,
                ),
              ),
              const SizedBox(width: 8),
              IconButton.filled(
                onPressed: _isConfigured && !_isLoading ? _sendMessage : null,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.send),
                style: IconButton.styleFrom(
                  backgroundColor: Colors.cyan,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment:
            message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.cyan,
              child: const Icon(Icons.smart_toy, size: 18, color: Colors.white),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: message.isUser
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: message.isUser
                        ? Colors.cyan.shade100
                        : Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: SelectableText(
                    message.content,
                    style: const TextStyle(fontSize: 14),
                  ),
                ),
                // Confirmation buttons for preview mode
                if (message.needsConfirmation && _hasPendingModifications)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Show modification preview count
                        if (message.fixesCount != null && message.fixesCount! > 0)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            margin: const EdgeInsets.only(bottom: 8),
                            decoration: BoxDecoration(
                              color: Colors.orange.shade50,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.orange.shade200),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.preview, size: 16, color: Colors.orange.shade700),
                                const SizedBox(width: 6),
                                Text(
                                  '${message.fixesCount} fixes ready to apply',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.orange.shade700,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                if (message.appliedModifications != null &&
                                    message.appliedModifications!.isNotEmpty) ...[
                                  const SizedBox(width: 8),
                                  InkWell(
                                    onTap: () => _showModificationDetails(message.appliedModifications!),
                                    child: Text(
                                      'View details',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Colors.orange.shade700,
                                        decoration: TextDecoration.underline,
                                      ),
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ),
                        // Apply/Cancel buttons
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            ElevatedButton.icon(
                              onPressed: _isLoading ? null : _applyModifications,
                              icon: const Icon(Icons.check, size: 18),
                              label: const Text('Apply Changes'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              ),
                            ),
                            const SizedBox(width: 8),
                            OutlinedButton.icon(
                              onPressed: _isLoading ? null : _cancelModifications,
                              icon: const Icon(Icons.close, size: 18),
                              label: const Text('Cancel'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: Colors.red,
                                side: const BorderSide(color: Colors.red),
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                // Cell modification indicator (for already applied changes)
                if (message.cellsModified != null && message.cellsModified! > 0 && !message.needsConfirmation)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.green.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.green.shade200),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.check_circle, size: 16, color: Colors.green.shade700),
                          const SizedBox(width: 6),
                          Text(
                            '${message.cellsModified} cells modified',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.green.shade700,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          if (message.appliedModifications != null &&
                              message.appliedModifications!.isNotEmpty) ...[
                            const SizedBox(width: 8),
                            InkWell(
                              onTap: () => _showModificationDetails(message.appliedModifications!),
                              child: Text(
                                'View details',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.green.shade700,
                                  decoration: TextDecoration.underline,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                // Suggested actions
                if (message.suggestedActions != null &&
                    message.suggestedActions!.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: message.suggestedActions!.map((action) {
                        return ActionChip(
                          avatar: const Icon(Icons.play_arrow, size: 16),
                          label: Text(_getActionLabel(action)),
                          onPressed: () => _executeSuggestedAction(action),
                          backgroundColor: Colors.green.shade50,
                        );
                      }).toList(),
                    ),
                  ),
              ],
            ),
          ),
          if (message.isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.grey.shade400,
              child: const Icon(Icons.person, size: 18, color: Colors.white),
            ),
          ],
        ],
      ),
    );
  }

  void _showModificationDetails(List<Map<String, dynamic>> modifications) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.edit_note, color: Colors.green.shade700),
            const SizedBox(width: 8),
            const Text('AI Cell Modifications'),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          height: 300,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: modifications.length,
            itemBuilder: (context, index) {
              final mod = modifications[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
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
                              'Row ${mod['row']}',
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
                              '${mod['column']}',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Colors.purple.shade800,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
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
                                  '${mod['old_value'] ?? 'null'}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.red.shade700,
                                    decoration: TextDecoration.lineThrough,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Icon(Icons.arrow_forward, size: 16, color: Colors.grey.shade400),
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
                                  '${mod['new_value']}',
                                  style: TextStyle(
                                    fontSize: 12,
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

  String _getActionLabel(Map<String, dynamic> action) {
    final type = action['type'] as String?;
    final column = action['column'] as String?;
    final method = action['method'] as String?;

    switch (type) {
      case 'fill_nulls':
        return 'Fill ${column ?? 'nulls'} with $method';
      case 'remove_nulls':
        return 'Remove null rows';
      case 'remove_duplicates':
        return 'Remove duplicates';
      case 'remove_column':
        return 'Remove $column';
      default:
        return type ?? 'Action';
    }
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: Colors.cyan,
            child: const Icon(Icons.smart_toy, size: 18, color: Colors.white),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade200,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildDot(0),
                _buildDot(1),
                _buildDot(2),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDot(int index) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: Duration(milliseconds: 600 + (index * 200)),
      builder: (context, value, child) {
        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 2),
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: Colors.grey.shade500.withOpacity(0.3 + (value * 0.7)),
            shape: BoxShape.circle,
          ),
        );
      },
    );
  }
}

class _QuickActionChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback onTap;

  const _QuickActionChip({
    required this.label,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ActionChip(
      avatar: Icon(icon, size: 16),
      label: Text(label),
      onPressed: onTap,
    );
  }
}
