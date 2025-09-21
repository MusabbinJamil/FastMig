import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';

class FilePickerService {
  Future<String?> pickFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv', 'xlsx', 'xls'],
      );

      if (result != null) {
        return result.files.single.path;
      }
      return null;
    } catch (e) {
      debugPrint('Error picking file: $e');
      return null;
    }
  }
}
