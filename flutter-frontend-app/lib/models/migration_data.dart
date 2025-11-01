import 'package:flutter/foundation.dart';
import '../services/file_picker_service.dart';
import '../services/api_service.dart';

class MigrationData with ChangeNotifier {
  final FilePickerService _filePickerService = FilePickerService();
  final ApiService _apiService = ApiService();

  List<List<dynamic>>? _data;
  List<String>? _columns;
  Map<String, String>? _dtypes;
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

  // Getters
  List<List<dynamic>>? get data => _data;
  List<String>? get columns => _columns;
  Map<String, String>? get dtypes => _dtypes;
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
        _encoding = result['encoding'];
        _fileFormat = result['format'];
        _shape =
            result['shape'] != null ? List<int>.from(result['shape']) : null;
        _errorMessage = null;
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
}
