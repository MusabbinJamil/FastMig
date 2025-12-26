import 'package:flutter/foundation.dart';
import '../services/file_picker_service.dart';
import '../services/api_service.dart';
import '../services/console_log_service.dart';

class MigrationData with ChangeNotifier {
  final FilePickerService _filePickerService = FilePickerService();
  final ApiService _apiService = ApiService();
  final ConsoleLogService _consoleLogService = ConsoleLogService();

  List<List<dynamic>>? _data;
  List<String>? _columns;
  Map<String, String>? _dtypes;
  List<Map<String, dynamic>>? _errorCells;
  String? _selectedColumn;
  String? _selectedDataType;
  String? _fileName;
  String? _encoding;
  String? _fileFormat;
  List<int>? _shape;
  bool _isLoading = false;
  String? _errorMessage;
  bool _isRecording = false;
  int _recordedActionsCount = 0;

  // Development features flags
  bool _enableETL = true;
  bool _enableAIFeatures = true;
  bool _enableMacroRecording = true;
  bool _enableConvertFields = true;
  bool _enableDataFitness = true;
  bool _enableAICleaning = true;
  bool _enableEncoding = true;
  bool _enableExport = true;
  bool _enableConsole = true;

  // Getters
  List<List<dynamic>>? get data => _data;
  List<String>? get columns => _columns;
  Map<String, String>? get dtypes => _dtypes;
  List<Map<String, dynamic>>? get errorCells => _errorCells;
  String? get selectedColumn => _selectedColumn;
  String? get selectedDataType => _selectedDataType;
  String? get fileName => _fileName;
  String? get encoding => _encoding;
  String? get fileFormat => _fileFormat;
  List<int>? get shape => _shape;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isRecording => _isRecording;
  int get recordedActionsCount => _recordedActionsCount;
  ApiService get apiService => _apiService;

  // Development features getters
  bool get enableETL => _enableETL;
  bool get enableAIFeatures => _enableAIFeatures;
  bool get enableMacroRecording => _enableMacroRecording;
  bool get enableConvertFields => _enableConvertFields;
  bool get enableDataFitness => _enableDataFitness;
  bool get enableAICleaning => _enableAICleaning;
  bool get enableEncoding => _enableEncoding;
  bool get enableExport => _enableExport;
  bool get enableConsole => _enableConsole;
  ConsoleLogService get consoleLogService => _consoleLogService;

  void selectColumn(String column) {
    _selectedColumn = column;
    if (_dtypes != null && _dtypes!.containsKey(column)) {
      _selectedDataType = _dtypes![column];
    }
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Pick and upload a file
  Future<void> pickAndUploadFile() async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final fileData = await _filePickerService.pickFile();
      if (fileData == null) {
        _isLoading = false;
        notifyListeners();
        return;
      }

      _fileName = fileData.fileName;

      final result = await _apiService.uploadFile(fileData);

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _dtypes = result['dtypes'];
        _errorCells = result['error_cells'] != null
            ? List<Map<String, dynamic>>.from(result['error_cells'] ?? [])
            : [];
        _encoding = result['encoding'];
        _fileFormat = result['format'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
        _errorMessage = null;

        // DEBUG: Log error cells
        debugPrint(
            '🔍 DEBUG: Upload result error_cells: ${result['error_cells']}');
        debugPrint('🔍 DEBUG: Parsed _errorCells: $_errorCells');
        debugPrint(
            '🔍 DEBUG: Data shape: ${_shape}, Columns: ${_columns?.length}');
      } else {
        _errorMessage = 'Failed to upload file';
      }
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error uploading file: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Process data with selected column and format
  Future<void> processData(String targetFormat, {String? dateFormat}) async {
    if (_selectedColumn == null) {
      _errorMessage = 'Please select a column first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.processData(
        _selectedColumn!,
        targetFormat,
        dateFormat: dateFormat,
      );

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _dtypes = result['dtypes'];
        _errorMessage = null;
      } else {
        _errorMessage = 'Failed to process data';
      }
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error processing data: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Export data to file
  Future<void> exportData(String outputPath) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.exportData(outputPath);

      if (result['success'] == true) {
        _errorMessage = null;
        // Success message will be handled by the UI
      } else {
        _errorMessage = 'Failed to export data';
      }
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error exporting data: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Start recording macro
  Future<void> startRecording() async {
    try {
      final result = await _apiService.startRecording();
      _isRecording = result['is_recording'] ?? false;
      _recordedActionsCount = 0;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error starting recording: $e');
      notifyListeners();
    }
  }

  /// Stop recording macro
  Future<void> stopRecording() async {
    try {
      final result = await _apiService.stopRecording();
      _isRecording = result['is_recording'] ?? false;
      _recordedActionsCount = result['actions_count'] ?? 0;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error stopping recording: $e');
      notifyListeners();
    }
  }

  /// Save recording
  Future<void> saveRecording(String recordingName) async {
    try {
      await _apiService.saveRecording(recordingName);
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error saving recording: $e');
      notifyListeners();
    }
  }

  /// Refresh status from backend
  Future<void> refreshStatus() async {
    try {
      final status = await _apiService.getStatus();
      _isRecording = status['is_recording'] ?? false;
      _recordedActionsCount = status['recorded_actions_count'] ?? 0;
      notifyListeners();
    } catch (e) {
      debugPrint('Error refreshing status: $e');
    }
  }

  /// Evaluate data fitness
  Future<Map<String, dynamic>> evaluateDataFitness() async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.evaluateFitness();
      return result;
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error evaluating fitness: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Get fitness of a specific record
  Future<Map<String, dynamic>> getRecordFitness(int rowIndex) async {
    try {
      final result = await _apiService.getRecordFitness(rowIndex);
      return result;
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error getting record fitness: $e');
      rethrow;
    }
  }

  /// Detect sensitive columns that shouldn't be AI-imputed
  /// Returns columns like Date of Birth, NIC, Passport numbers, etc.
  Future<Map<String, dynamic>> detectSensitiveColumns() async {
    try {
      final result = await _apiService.detectSensitiveColumns();
      return result;
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error detecting sensitive columns: $e');
      // Return empty result on error - this is non-critical
      return {
        'success': false,
        'sensitive_columns': {},
        'count': 0,
        'error': e.toString()
      };
    }
  }

  /// Clean data using evolutionary algorithms
  Future<Map<String, dynamic>> cleanDataEvolutionary({
    required String method,
    bool saveResult = true,
    bool trackModifications = true,
    Map<String, dynamic>? parameters,
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.cleanDataEvolutionary(
        method: method,
        saveResult: saveResult,
        trackModifications: trackModifications,
        parameters: parameters,
      );

      if (result['success'] == true && saveResult) {
        _data = result['data'];
        _columns = result['columns'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error cleaning data: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Compare different evolutionary cleaning methods
  Future<Map<String, dynamic>> compareCleaningMethods() async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.compareCleaningMethods();
      return result;
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error comparing methods: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Restore original data before cleaning
  Future<void> restoreOriginalData() async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.restoreOriginalData();

      if (result['success'] == true && result['data'] != null) {
        _data = result['data'];
        _columns = result['columns'];
      }
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error restoring data: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // =========================================================================
  // ETL OPERATIONS
  // =========================================================================

  /// Remove rows containing null values
  Future<Map<String, dynamic>> removeNulls({
    List<String>? columns,
    String how = 'any',
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.removeNulls(columns: columns, how: how);

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error removing nulls: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Remove duplicate rows
  Future<Map<String, dynamic>> removeDuplicates({
    List<String>? columns,
    String keep = 'first',
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result =
          await _apiService.removeDuplicates(columns: columns, keep: keep);

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error removing duplicates: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Find and replace values
  Future<Map<String, dynamic>> findReplace({
    required String column,
    required String findValue,
    required String replaceValue,
    bool useRegex = false,
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.findReplace(
        column: column,
        findValue: findValue,
        replaceValue: replaceValue,
        useRegex: useRegex,
      );

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error in find and replace: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Fill null values
  Future<Map<String, dynamic>> fillNulls({
    required String column,
    required String method,
    dynamic value,
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.fillNulls(
        column: column,
        method: method,
        value: value,
      );

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error filling nulls: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Trim whitespace from columns
  Future<Map<String, dynamic>> trimWhitespace({List<String>? columns}) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.trimWhitespace(columns: columns);

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error trimming whitespace: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Change text case
  Future<Map<String, dynamic>> changeCase({
    required String column,
    required String caseType,
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.changeCase(
        column: column,
        caseType: caseType,
      );

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error changing case: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Filter rows
  Future<Map<String, dynamic>> filterRows({
    required String column,
    required String operator,
    required dynamic value,
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.filterRows(
        column: column,
        operator: operator,
        value: value,
      );

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error filtering rows: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Sort data
  Future<Map<String, dynamic>> sortData({
    required List<String> columns,
    bool ascending = true,
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.sortData(
        columns: columns,
        ascending: ascending,
      );

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error sorting data: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Rename column
  Future<Map<String, dynamic>> renameColumn({
    required String oldName,
    required String newName,
  }) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.renameColumn(
        oldName: oldName,
        newName: newName,
      );

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error renaming column: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Remove column
  Future<Map<String, dynamic>> removeColumn({required String column}) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.removeColumn(column: column);

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
      }

      return result['report'];
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error removing column: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // =========================================================================
  // STEP RECORDING (New - replaces macro recording)
  // =========================================================================

  /// Start recording steps (using new endpoint)
  Future<void> startStepRecording() async {
    try {
      final result = await _apiService.startStepRecording();
      _isRecording = result['is_recording'] ?? false;
      _recordedActionsCount = 0;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error starting step recording: $e');
      notifyListeners();
    }
  }

  /// Stop recording steps (using new endpoint)
  Future<void> stopStepRecording() async {
    try {
      final result = await _apiService.stopStepRecording();
      _isRecording = result['is_recording'] ?? false;
      _recordedActionsCount = result['steps_count'] ?? 0;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error stopping step recording: $e');
      notifyListeners();
    }
  }

  /// Get recorded steps
  Future<Map<String, dynamic>> getRecordedSteps() async {
    try {
      final result = await _apiService.getRecordedSteps();
      _recordedActionsCount = result['steps_count'] ?? 0;
      notifyListeners();
      return result;
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error getting recorded steps: $e');
      rethrow;
    }
  }

  /// Save recorded steps
  Future<void> saveSteps(String name) async {
    try {
      await _apiService.saveSteps(name);
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error saving steps: $e');
      notifyListeners();
    }
  }

  /// Replay steps on current or new data
  Future<Map<String, dynamic>> replaySteps({String? filePath}) async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result = await _apiService.replaySteps(filePath: filePath);

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
      }

      return result;
    } catch (e) {
      _errorMessage = e.toString();
      debugPrint('Error replaying steps: $e');
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Development features setters
  void toggleETL() {
    _enableETL = !_enableETL;
    _consoleLogService.info(
        'ETL Operations ${_enableETL ? 'enabled' : 'disabled'}',
        function: 'toggleETL');
    notifyListeners();
  }

  void toggleAIFeatures() {
    _enableAIFeatures = !_enableAIFeatures;
    _consoleLogService.info(
        'AI Features ${_enableAIFeatures ? 'enabled' : 'disabled'}',
        function: 'toggleAIFeatures');
    notifyListeners();
  }

  void toggleMacroRecording() {
    _enableMacroRecording = !_enableMacroRecording;
    _consoleLogService.info(
        'Macro Recording ${_enableMacroRecording ? 'enabled' : 'disabled'}',
        function: 'toggleMacroRecording');
    notifyListeners();
  }

  void toggleConvertFields() {
    _enableConvertFields = !_enableConvertFields;
    _consoleLogService.info(
        'Convert Fields ${_enableConvertFields ? 'enabled' : 'disabled'}',
        function: 'toggleConvertFields');
    notifyListeners();
  }

  void toggleDataFitness() {
    _enableDataFitness = !_enableDataFitness;
    _consoleLogService.info(
        'Data Fitness ${_enableDataFitness ? 'enabled' : 'disabled'}',
        function: 'toggleDataFitness');
    notifyListeners();
  }

  void toggleAICleaning() {
    _enableAICleaning = !_enableAICleaning;
    _consoleLogService.info(
        'AI Cleaning ${_enableAICleaning ? 'enabled' : 'disabled'}',
        function: 'toggleAICleaning');
    notifyListeners();
  }

  void setETL(bool value) {
    _enableETL = value;
    notifyListeners();
  }

  void setAIFeatures(bool value) {
    _enableAIFeatures = value;
    notifyListeners();
  }

  void setMacroRecording(bool value) {
    _enableMacroRecording = value;
    notifyListeners();
  }

  void setConvertFields(bool value) {
    _enableConvertFields = value;
    notifyListeners();
  }

  void setDataFitness(bool value) {
    _enableDataFitness = value;
    notifyListeners();
  }

  void setAICleaning(bool value) {
    _enableAICleaning = value;
    notifyListeners();
  }

  void toggleEncoding() {
    _enableEncoding = !_enableEncoding;
    _consoleLogService.info(
        'Encoding ${_enableEncoding ? 'enabled' : 'disabled'}',
        function: 'toggleEncoding');
    notifyListeners();
  }

  void toggleExport() {
    _enableExport = !_enableExport;
    _consoleLogService.info('Export ${_enableExport ? 'enabled' : 'disabled'}',
        function: 'toggleExport');
    notifyListeners();
  }

  void toggleConsole() {
    _enableConsole = !_enableConsole;
    _consoleLogService.info(
        'Console ${_enableConsole ? 'enabled' : 'disabled'}',
        function: 'toggleConsole');
    notifyListeners();
  }

  void setEncoding(bool value) {
    _enableEncoding = value;
    notifyListeners();
  }

  void setExport(bool value) {
    _enableExport = value;
    notifyListeners();
  }

  void setConsole(bool value) {
    _enableConsole = value;
    notifyListeners();
  }
}
