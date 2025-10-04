import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';

class PickedFileData {
  final String fileName;
  final Uint8List bytes;

  PickedFileData({
    required this.fileName,
    required this.bytes,
  });
}

class FilePickerService {
  Future<PickedFileData?> pickFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv', 'xlsx', 'xls'],
        withData: true, // Always load bytes for web
      );

      if (result != null) {
        final file = result.files.single;
        if (file.bytes == null) {
          throw Exception('Unable to read file data');
        }
        return PickedFileData(
          fileName: file.name,
          bytes: file.bytes!,
        );
      }
      return null;
    } catch (e) {
      debugPrint('Error picking file: $e');
      return null;
    }
  }
}
