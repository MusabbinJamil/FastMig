import 'package:flutter/foundation.dart';
import '../services/file_picker_service.dart';

class MigrationData with ChangeNotifier {
  final FilePickerService _filePickerService = FilePickerService();
  List<List<dynamic>>? _data;
  String? _selectedColumn;
  String? _selectedDataType;
  String? _filePath;

  List<List<dynamic>>? get data => _data;
  String? get selectedColumn => _selectedColumn;
  String? get selectedDataType => _selectedDataType;
  String? get filePath => _filePath;

  void setData(List<List<dynamic>> newData) {
    _data = newData;
    notifyListeners();
  }

  void selectColumn(String column) {
    _selectedColumn = column;
    notifyListeners();
  }

  void setDataType(String dataType) {
    _selectedDataType = dataType;
    notifyListeners();
  }

  void setFilePath(String path) {
    _filePath = path;
    notifyListeners();
  }

  Future<void> pickFile() async {
    final String? path = await _filePickerService.pickFile();
    if (path != null) {
      setFilePath(path);
    }
  }
}
