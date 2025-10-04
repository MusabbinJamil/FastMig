import 'package:http/http.dart' as http;
import 'dart:convert';
import 'file_picker_service.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5000';

  /// Upload a file to the backend and get its data (Web-only)
  Future<Map<String, dynamic>> uploadFile(PickedFileData fileData) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/upload'),
      );

      // Add file bytes to request
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        fileData.bytes,
        filename: fileData.fileName,
      ));

      // Send request
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return {
          'success': true,
          'data': (jsonResponse['data'] as List)
              .map((row) => List<dynamic>.from(row))
              .toList(),
          'columns': List<String>.from(jsonResponse['columns']),
          'dtypes': Map<String, String>.from(jsonResponse['dtypes']),
          'filename': jsonResponse['filename'],
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to upload file');
      }
    } catch (e) {
      throw Exception('Error uploading file: $e');
    }
  }

  /// Process data with column conversion
  Future<Map<String, dynamic>> processData(String column, String format) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/process'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'column': column,
          'format': format,
        }),
      );

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return {
          'success': true,
          'data': (jsonResponse['data'] as List)
              .map((row) => List<dynamic>.from(row))
              .toList(),
          'columns': List<String>.from(jsonResponse['columns']),
          'dtypes': Map<String, String>.from(jsonResponse['dtypes']),
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to process data');
      }
    } catch (e) {
      throw Exception('Error processing data: $e');
    }
  }

  /// Get column information
  Future<Map<String, dynamic>> getColumns() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/columns'));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to get columns');
      }
    } catch (e) {
      throw Exception('Error getting columns: $e');
    }
  }

  /// Check backend health
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
