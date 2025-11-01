import 'package:http/http.dart' as http;
import 'dart:convert';
import 'file_picker_service.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5000';

  /// Upload a file to the backend and get its data with advanced metadata
  Future<Map<String, dynamic>> uploadFile(PickedFileData fileData) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/upload'),
      );

      request.files.add(http.MultipartFile.fromBytes(
        'file',
        fileData.bytes,
        filename: fileData.fileName,
      ));

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
          'shape': jsonResponse['shape'],
          'encoding': jsonResponse['encoding'] ?? 'utf-8',
          'format': jsonResponse['format'] ?? 'unknown',
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to upload file');
      }
    } catch (e) {
      throw Exception('Error uploading file: $e');
    }
  }

  /// Process data with column conversion and optional format
  Future<Map<String, dynamic>> processData(String column, String format,
      {String? dateFormat}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/process'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'column': column,
          'format': format,
          if (dateFormat != null) 'date_format': dateFormat,
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
          'message': jsonResponse['message'] ?? 'Data processed successfully',
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to process data');
      }
    } catch (e) {
      throw Exception('Error processing data: $e');
    }
  }

  /// Export processed data to file
  Future<Map<String, dynamic>> exportData(String outputPath) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/export'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'output_path': outputPath}),
      );

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return {
          'success': true,
          'message': jsonResponse['message'],
          'file_path': jsonResponse['file_path'],
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to export data');
      }
    } catch (e) {
      throw Exception('Error exporting data: $e');
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

  /// Start recording macro actions
  Future<Map<String, dynamic>> startRecording() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/recording/start'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to start recording');
      }
    } catch (e) {
      throw Exception('Error starting recording: $e');
    }
  }

  /// Stop recording macro actions
  Future<Map<String, dynamic>> stopRecording() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/recording/stop'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to stop recording');
      }
    } catch (e) {
      throw Exception('Error stopping recording: $e');
    }
  }

  /// Save recorded actions
  Future<Map<String, dynamic>> saveRecording(String recordingName) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/recording/save'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': recordingName}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to save recording');
      }
    } catch (e) {
      throw Exception('Error saving recording: $e');
    }
  }

  /// Load and run a recording
  Future<Map<String, dynamic>> loadAndRunRecording(
      String recordingPath, String filePath) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/recording/load'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'recording_path': recordingPath,
          'file_path': filePath,
        }),
      );

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return {
          'success': true,
          'data': (jsonResponse['data'] as List)
              .map((row) => List<dynamic>.from(row))
              .toList(),
          'message': jsonResponse['message'],
          'actions_applied': jsonResponse['actions_applied'],
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to load and run recording');
      }
    } catch (e) {
      throw Exception('Error loading and running recording: $e');
    }
  }

  /// Get application status
  Future<Map<String, dynamic>> getStatus() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/status'));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get status');
      }
    } catch (e) {
      throw Exception('Error getting status: $e');
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

  /// Evaluate data fitness - assess health and quality of data
  Future<Map<String, dynamic>> evaluateFitness() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/fitness/evaluate'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to evaluate fitness');
      }
    } catch (e) {
      throw Exception('Error evaluating fitness: $e');
    }
  }

  /// Get fitness of a specific record
  Future<Map<String, dynamic>> getRecordFitness(int rowIndex) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/fitness/record/$rowIndex'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to get record fitness');
      }
    } catch (e) {
      throw Exception('Error getting record fitness: $e');
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
      final response = await http.post(
        Uri.parse('$baseUrl/clean/evolutionary'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'method': method,
          'save_result': saveResult,
          'track_modifications': trackModifications,
          if (parameters != null) 'parameters': parameters,
        }),
      );

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return {
          'success': true,
          'method': jsonResponse['method'],
          'report': jsonResponse['report'],
          'data': (jsonResponse['data'] as List)
              .map((row) => List<dynamic>.from(row))
              .toList(),
          'columns': List<String>.from(jsonResponse['columns']),
          'shape': jsonResponse['shape'],
          'message': jsonResponse['message'],
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to clean data');
      }
    } catch (e) {
      throw Exception('Error cleaning data: $e');
    }
  }

  /// Compare different evolutionary cleaning methods
  Future<Map<String, dynamic>> compareCleaningMethods() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/clean/compare'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to compare methods');
      }
    } catch (e) {
      throw Exception('Error comparing methods: $e');
    }
  }

  /// Restore original data before cleaning
  Future<Map<String, dynamic>> restoreOriginalData() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/data/restore'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        return {
          'success': true,
          'message': jsonResponse['message'],
          'data': jsonResponse['data'] != null
              ? (jsonResponse['data'] as List)
                  .map((row) => List<dynamic>.from(row))
                  .toList()
              : null,
          'columns': jsonResponse['columns'] != null
              ? List<String>.from(jsonResponse['columns'])
              : null,
        };
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to restore data');
      }
    } catch (e) {
      throw Exception('Error restoring data: $e');
    }
  }
}
