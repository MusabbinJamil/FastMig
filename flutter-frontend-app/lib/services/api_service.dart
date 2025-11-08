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

  // =========================================================================
  // ETL OPERATIONS - Advanced data transformations
  // =========================================================================

  /// Remove rows containing null values
  Future<Map<String, dynamic>> removeNulls({
    List<String>? columns,
    String how = 'any',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/remove-nulls'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
          'how': how,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to remove nulls');
      }
    } catch (e) {
      throw Exception('Error removing nulls: $e');
    }
  }

  /// Remove duplicate rows
  Future<Map<String, dynamic>> removeDuplicates({
    List<String>? columns,
    String keep = 'first',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/remove-duplicates'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
          'keep': keep,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to remove duplicates');
      }
    } catch (e) {
      throw Exception('Error removing duplicates: $e');
    }
  }

  /// Find and replace values in a column
  Future<Map<String, dynamic>> findReplace({
    required String column,
    required String findValue,
    required String replaceValue,
    bool useRegex = false,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/find-replace'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'column': column,
          'find_value': findValue,
          'replace_value': replaceValue,
          'use_regex': useRegex,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to find and replace');
      }
    } catch (e) {
      throw Exception('Error in find and replace: $e');
    }
  }

  /// Fill null values in a column
  Future<Map<String, dynamic>> fillNulls({
    required String column,
    required String method,
    dynamic value,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/fill-nulls'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'column': column,
          'method': method,
          if (value != null) 'value': value,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to fill nulls');
      }
    } catch (e) {
      throw Exception('Error filling nulls: $e');
    }
  }

  /// Rename a column
  Future<Map<String, dynamic>> renameColumn({
    required String oldName,
    required String newName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/rename-column'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'old_name': oldName,
          'new_name': newName,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to rename column');
      }
    } catch (e) {
      throw Exception('Error renaming column: $e');
    }
  }

  /// Remove a column
  Future<Map<String, dynamic>> removeColumn({
    required String column,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/remove-column'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'column': column}),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to remove column');
      }
    } catch (e) {
      throw Exception('Error removing column: $e');
    }
  }

  /// Filter rows based on a condition
  Future<Map<String, dynamic>> filterRows({
    required String column,
    required String operator,
    required dynamic value,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/filter-rows'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'column': column,
          'operator': operator,
          'value': value,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to filter rows');
      }
    } catch (e) {
      throw Exception('Error filtering rows: $e');
    }
  }

  /// Trim whitespace from columns
  Future<Map<String, dynamic>> trimWhitespace({
    List<String>? columns,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/trim-whitespace'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to trim whitespace');
      }
    } catch (e) {
      throw Exception('Error trimming whitespace: $e');
    }
  }

  /// Change text case in a column
  Future<Map<String, dynamic>> changeCase({
    required String column,
    required String caseType,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/change-case'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'column': column,
          'case_type': caseType,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to change case');
      }
    } catch (e) {
      throw Exception('Error changing case: $e');
    }
  }

  /// Sort data by columns
  Future<Map<String, dynamic>> sortData({
    required List<String> columns,
    bool ascending = true,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/etl/sort-data'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'columns': columns,
          'ascending': ascending,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to sort data');
      }
    } catch (e) {
      throw Exception('Error sorting data: $e');
    }
  }

  // =========================================================================
  // STEP RECORDING - New endpoints (replaces macro recording)
  // =========================================================================

  /// Start recording transformation steps
  Future<Map<String, dynamic>> startStepRecording() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/steps/start'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to start step recording');
      }
    } catch (e) {
      throw Exception('Error starting step recording: $e');
    }
  }

  /// Stop recording transformation steps
  Future<Map<String, dynamic>> stopStepRecording() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/steps/stop'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to stop step recording');
      }
    } catch (e) {
      throw Exception('Error stopping step recording: $e');
    }
  }

  /// Get recorded steps
  Future<Map<String, dynamic>> getRecordedSteps() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/steps/get'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get recorded steps');
      }
    } catch (e) {
      throw Exception('Error getting recorded steps: $e');
    }
  }

  /// Save recorded steps to file
  Future<Map<String, dynamic>> saveSteps(String name) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/steps/save'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': name}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to save steps');
      }
    } catch (e) {
      throw Exception('Error saving steps: $e');
    }
  }

  /// Load steps from file
  Future<Map<String, dynamic>> loadSteps(String filePath) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/steps/load'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'file_path': filePath}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load steps');
      }
    } catch (e) {
      throw Exception('Error loading steps: $e');
    }
  }

  /// Replay recorded steps on current or new data
  Future<Map<String, dynamic>> replaySteps({String? filePath}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/steps/replay'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (filePath != null) 'file_path': filePath,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to replay steps');
      }
    } catch (e) {
      throw Exception('Error replaying steps: $e');
    }
  }

  /// Clear recorded steps
  Future<Map<String, dynamic>> clearSteps() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/steps/clear'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to clear steps');
      }
    } catch (e) {
      throw Exception('Error clearing steps: $e');
    }
  }

  // =========================================================================
  // MACHINE READABLE TRANSFORM (ENCODING) OPERATIONS
  // =========================================================================

  /// Label encode categorical columns
  Future<Map<String, dynamic>> labelEncode({
    List<String>? columns,
    bool saveMapping = true,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/transform/label-encode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
          'save_mapping': saveMapping,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to label encode');
      }
    } catch (e) {
      throw Exception('Error in label encoding: $e');
    }
  }

  /// One-hot encode categorical columns
  Future<Map<String, dynamic>> oneHotEncode({
    List<String>? columns,
    bool dropFirst = false,
    String prefixSep = '_',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/transform/one-hot-encode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
          'drop_first': dropFirst,
          'prefix_sep': prefixSep,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to one-hot encode');
      }
    } catch (e) {
      throw Exception('Error in one-hot encoding: $e');
    }
  }

  /// Reverse label encoding
  Future<Map<String, dynamic>> reverseLabelEncode({
    List<String>? columns,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/transform/reverse-label-encode'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
        }),
      );

      if (response.statusCode == 200) {
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to reverse label encoding');
      }
    } catch (e) {
      throw Exception('Error reversing label encoding: $e');
    }
  }

  // =========================================================================
  // HELPER METHODS
  // =========================================================================

  /// Parse ETL operation response
  Map<String, dynamic> _parseEtlResponse(http.Response response) {
    final jsonResponse = jsonDecode(response.body);
    return {
      'success': true,
      'data': (jsonResponse['data'] as List)
          .map((row) => List<dynamic>.from(row))
          .toList(),
      'columns': List<String>.from(jsonResponse['columns']),
      'shape': jsonResponse['shape'],
      'report': jsonResponse['report'],
      'message': jsonResponse['message'],
    };
  }
}
