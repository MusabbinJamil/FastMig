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
  bool _isLoading = false;
  String? _errorMessage;

  // Getters
  List<List<dynamic>>? get data => _data;
  List<String>? get columns => _columns;
  Map<String, String>? get dtypes => _dtypes;
  String? get selectedColumn => _selectedColumn;
  String? get selectedDataType => _selectedDataType;
  String? get fileName => _fileName;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  void setData(List<List<dynamic>> newData) {
    _data = newData;
    notifyListeners();
  }

  void selectColumn(String column) {
    _selectedColumn = column;
    // Get the data type for the selected column
    if (_dtypes != null && _dtypes!.containsKey(column)) {
      _selectedDataType = _dtypes![column];
    }
    notifyListeners();
  }

  void setDataType(String dataType) {
    _selectedDataType = dataType;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Pick and upload a file (Web-only)
  Future<void> pickAndUploadFile() async {
    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      // Pick file
      final fileData = await _filePickerService.pickFile();
      if (fileData == null) {
        _isLoading = false;
        notifyListeners();
        return;
      }

      _fileName = fileData.fileName;

      // Upload file to backend
      final result = await _apiService.uploadFile(fileData);

      if (result['success'] == true) {
        _data = result['data'];
        _columns = result['columns'];
        _dtypes = result['dtypes'];
        _fileName = result['filename'];
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
  Future<void> processData(String targetFormat) async {
    if (_selectedColumn == null) {
      _errorMessage = 'Please select a column first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _errorMessage = null;
      notifyListeners();

      final result =
          await _apiService.processData(_selectedColumn!, targetFormat);

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
}
