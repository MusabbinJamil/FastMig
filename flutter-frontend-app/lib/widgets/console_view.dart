import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class ConsoleView extends StatefulWidget {
  const ConsoleView({Key? key}) : super(key: key);

  @override
  State<ConsoleView> createState() => _ConsoleViewState();
}

class _ConsoleViewState extends State<ConsoleView> {
  late ScrollController _scrollController;
  late ApiService _apiService;
  List<String> _logs = [];
  double _fontSize = 16.0;
  static const double _minFontSize = 8.0;
  static const double _maxFontSize = 16.0;

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
    _apiService = ApiService();
    _loadFontSize();
    _fetchLogs();
  }

  Future<void> _loadFontSize() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) {
      setState(() {
        _fontSize = prefs.getDouble('console_font_size') ?? 11.0;
      });
    }
  }

  Future<void> _saveFontSize(double size) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('console_font_size', size);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  Future<void> _fetchLogs() async {
    if (!mounted) return;
    try {
      final logs = await _apiService.getBackendLogs();
      if (mounted) {
        setState(() {
          _logs = logs;
        });
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _scrollToBottom();
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _logs = [
            'Error fetching logs: $e',
            'Make sure backend server is running at http://localhost:5000'
          ];
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Console Header
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey.shade900,
            border: Border(
              bottom: BorderSide(color: Colors.grey.shade700),
            ),
          ),
          child: Row(
            children: [
              Icon(Icons.terminal, color: Colors.green.shade400, size: 20),
              const SizedBox(width: 8),
              const Text(
                'Backend Console',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const Spacer(),
              // Decrease font size button
              Tooltip(
                message: 'Decrease font size',
                child: IconButton(
                  icon: const Icon(Icons.text_decrease),
                  color: Colors.grey.shade400,
                  onPressed: _fontSize > _minFontSize
                      ? () {
                          final newSize = (_fontSize - 0.5)
                              .clamp(_minFontSize, _maxFontSize);
                          setState(() {
                            _fontSize = newSize;
                          });
                          _saveFontSize(newSize);
                        }
                      : null,
                  iconSize: 18,
                  constraints:
                      const BoxConstraints(minWidth: 32, minHeight: 32),
                ),
              ),
              // Font size display
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Text(
                  '${_fontSize.toStringAsFixed(1)}',
                  style: TextStyle(
                    color: Colors.grey.shade400,
                    fontSize: 12,
                  ),
                ),
              ),
              // Increase font size button
              Tooltip(
                message: 'Increase font size',
                child: IconButton(
                  icon: const Icon(Icons.text_increase),
                  color: Colors.grey.shade400,
                  onPressed: _fontSize < _maxFontSize
                      ? () {
                          final newSize = (_fontSize + 0.5)
                              .clamp(_minFontSize, _maxFontSize);
                          setState(() {
                            _fontSize = newSize;
                          });
                          _saveFontSize(newSize);
                        }
                      : null,
                  iconSize: 18,
                  constraints:
                      const BoxConstraints(minWidth: 32, minHeight: 32),
                ),
              ),
              // Refresh button
              Tooltip(
                message: 'Refresh logs',
                child: IconButton(
                  icon: const Icon(Icons.refresh),
                  color: Colors.grey.shade400,
                  onPressed: _fetchLogs,
                  iconSize: 18,
                  constraints:
                      const BoxConstraints(minWidth: 32, minHeight: 32),
                ),
              ),
              // Clear button
              Tooltip(
                message: 'Clear console',
                child: IconButton(
                  icon: const Icon(Icons.delete_outline),
                  color: Colors.grey.shade400,
                  onPressed: () {
                    setState(() => _logs = []);
                  },
                  iconSize: 18,
                  constraints:
                      const BoxConstraints(minWidth: 32, minHeight: 32),
                ),
              ),
            ],
          ),
        ),
        // Console Output Area
        Container(
          color: Colors.grey.shade900,
          padding: const EdgeInsets.all(12),
          constraints: const BoxConstraints(maxHeight: 400),
          child: _logs.isEmpty
              ? Center(
                  child: Text(
                    'No output yet\nBackend print statements will appear here',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 13,
                    ),
                  ),
                )
              : ListView.builder(
                  controller: _scrollController,
                  itemCount: _logs.length,
                  itemBuilder: (context, index) {
                    final log = _logs[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: _buildLogEntry(log),
                    );
                  },
                ),
        ),
        // Footer
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.grey.shade900,
            border: Border(
              top: BorderSide(color: Colors.grey.shade700),
            ),
          ),
          child: Row(
            children: [
              Text(
                'Logs: ${_logs.length}',
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 11,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.green.shade900.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Text(
                  'Backend Output',
                  style: TextStyle(
                    color: Colors.green.shade300,
                    fontSize: 10,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLogEntry(String log) {
    // Color code based on content
    Color textColor = Colors.grey.shade300;
    if (log.contains('Error') || log.contains('error')) {
      textColor = Colors.red.shade300;
    } else if (log.contains('Warning') || log.contains('warning')) {
      textColor = Colors.orange.shade300;
    } else if (log.contains('Success') || log.contains('success')) {
      textColor = Colors.green.shade300;
    }

    return Text(
      log,
      style: TextStyle(
        color: textColor,
        fontSize: _fontSize,
        fontFamily: 'monospace',
      ),
      maxLines: 5,
      overflow: TextOverflow.ellipsis,
    );
  }
}
