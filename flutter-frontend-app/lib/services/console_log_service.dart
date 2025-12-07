import 'package:flutter/foundation.dart';

/// Console log entry to track operations
class ConsoleLogEntry {
  final String message;
  final String level; // 'INFO', 'WARNING', 'ERROR', 'SUCCESS'
  final DateTime timestamp;
  final String? function;

  ConsoleLogEntry({
    required this.message,
    required this.level,
    required this.timestamp,
    this.function,
  });
}

/// Service to manage console logs similar to server logs
class ConsoleLogService extends ChangeNotifier {
  static final ConsoleLogService _instance = ConsoleLogService._internal();

  factory ConsoleLogService() {
    return _instance;
  }

  ConsoleLogService._internal();

  final List<ConsoleLogEntry> _logs = [];
  static const int maxLogs = 500; // Keep last 500 logs

  List<ConsoleLogEntry> get logs => List.unmodifiable(_logs);

  /// Add a log entry
  void log(
    String message, {
    String level = 'INFO',
    String? function,
  }) {
    _logs.add(
      ConsoleLogEntry(
        message: message,
        level: level,
        timestamp: DateTime.now(),
        function: function,
      ),
    );

    // Keep memory usage reasonable
    if (_logs.length > maxLogs) {
      _logs.removeRange(0, _logs.length - maxLogs);
    }

    notifyListeners();
  }

  /// Log info level
  void info(String message, {String? function}) {
    log(message, level: 'INFO', function: function);
  }

  /// Log success level
  void success(String message, {String? function}) {
    log(message, level: 'SUCCESS', function: function);
  }

  /// Log warning level
  void warning(String message, {String? function}) {
    log(message, level: 'WARNING', function: function);
  }

  /// Log error level
  void error(String message, {String? function}) {
    log(message, level: 'ERROR', function: function);
  }

  /// Clear all logs
  void clear() {
    _logs.clear();
    notifyListeners();
  }

  /// Export logs as text
  String exportLogs() {
    return _logs
        .map((log) =>
            '[${log.timestamp.toString().split('.')[0]}] [${log.level}] ${log.function != null ? '(${log.function})' : ''} ${log.message}')
        .join('\n');
  }
}
