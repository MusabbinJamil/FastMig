import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'file_picker_service.dart';
import 'console_log_service.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5000';
  final ConsoleLogService _consoleLogService = ConsoleLogService();

  /// Upload a file to the backend and get its data with advanced metadata
  Future<Map<String, dynamic>> uploadFile(PickedFileData fileData) async {
    try {
      _consoleLogService.info('Uploading file: ${fileData.fileName}',
          function: 'uploadFile');
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
        final result = {
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
          'error_cells': jsonResponse['error_cells'] ?? [],
          'column_types': jsonResponse['column_types'] ?? {},
          'warnings': jsonResponse['warnings'] ?? [],
        };
        _consoleLogService.success(
            'File loaded: ${result['filename']} (${result['shape'][0]} rows, ${result['shape'][1]} columns)',
            function: 'uploadFile');
        return result;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Failed to upload file: ${error['error'] ?? 'Unknown error'}',
            function: 'uploadFile');
        throw Exception(error['error'] ?? 'Failed to upload file');
      }
    } catch (e) {
      _consoleLogService.error('Error uploading file: $e',
          function: 'uploadFile');
      throw Exception('Error uploading file: $e');
    }
  }

  /// Process data with column conversion and optional format
  Future<Map<String, dynamic>> processData(String column, String format,
      {String? dateFormat}) async {
    try {
      _consoleLogService.info('Processing column "$column" to format "$format"',
          function: 'processData');
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
        _consoleLogService.success(
            'Column "$column" converted to $format successfully',
            function: 'processData');
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
        _consoleLogService.error('Failed to process column: ${error['error']}',
            function: 'processData');
        throw Exception(error['error'] ?? 'Failed to process data');
      }
    } catch (e) {
      _consoleLogService.error('Error processing data: $e',
          function: 'processData');
      throw Exception('Error processing data: $e');
    }
  }

  /// Export processed data and trigger browser download
  Future<Map<String, dynamic>> exportData(String filename, {String format = 'csv'}) async {
    try {
      _consoleLogService.info('Exporting data as $format: $filename',
          function: 'exportData');

      final response = await http.post(
        Uri.parse('$baseUrl/export'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'format': format,
          'filename': filename,
        }),
      );

      if (response.statusCode == 200) {
        // Get the filename from Content-Disposition header or use default
        String downloadFilename = '$filename.$format';
        final contentDisposition = response.headers['content-disposition'];
        if (contentDisposition != null) {
          final match = RegExp(r'filename="?([^"]+)"?').firstMatch(contentDisposition);
          if (match != null) {
            downloadFilename = match.group(1) ?? downloadFilename;
          }
        }

        // Determine MIME type
        String mimeType;
        switch (format) {
          case 'xlsx':
            mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
            break;
          case 'json':
            mimeType = 'application/json';
            break;
          case 'csv':
          default:
            mimeType = 'text/csv';
        }

        // Create blob and trigger download
        final blob = html.Blob([response.bodyBytes], mimeType);
        final url = html.Url.createObjectUrlFromBlob(blob);
        final anchor = html.AnchorElement(href: url)
          ..setAttribute('download', downloadFilename)
          ..style.display = 'none';

        html.document.body?.append(anchor);
        anchor.click();
        anchor.remove();
        html.Url.revokeObjectUrl(url);

        _consoleLogService.success(
            'Data exported successfully: $downloadFilename',
            function: 'exportData');
        return {
          'success': true,
          'message': 'Data exported successfully',
          'filename': downloadFilename,
        };
      } else {
        // Try to parse error from JSON response
        try {
          final error = jsonDecode(response.body);
          _consoleLogService.error('Failed to export data: ${error['error']}',
              function: 'exportData');
          throw Exception(error['error'] ?? 'Failed to export data');
        } catch (_) {
          throw Exception('Failed to export data: ${response.statusCode}');
        }
      }
    } catch (e) {
      _consoleLogService.error('Error exporting data: $e',
          function: 'exportData');
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
      _consoleLogService.info('Starting macro recording',
          function: 'startRecording');
      final response = await http.post(
        Uri.parse('$baseUrl/recording/start'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        _consoleLogService.success('Macro recording started',
            function: 'startRecording');
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

  /// Apply configurations to the backend
  Future<Map<String, dynamic>> applyConfigurations(
      Map<String, dynamic> settings) async {
    try {
      _consoleLogService.info('Applying configurations',
          function: 'applyConfigurations');
      final response = await http.post(
        Uri.parse('$baseUrl/config/apply'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(settings),
      );

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('Configurations applied successfully',
            function: 'applyConfigurations');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to apply configurations');
      }
    } catch (e) {
      _consoleLogService.error('Error applying configurations: $e',
          function: 'applyConfigurations');
      throw Exception('Error applying configurations: $e');
    }
  }

  /// Evaluate data fitness - assess health and quality of data
  Future<Map<String, dynamic>> evaluateFitness() async {
    try {
      _consoleLogService.info('Evaluating data fitness...',
          function: 'evaluateFitness');
      final response = await http.post(
        Uri.parse('$baseUrl/fitness/evaluate'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        _consoleLogService.success('Data fitness evaluation completed',
            function: 'evaluateFitness');
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

  /// Detect sensitive columns that shouldn't be AI-imputed
  /// Returns columns like Date of Birth, NIC, Passport numbers, etc.
  Future<Map<String, dynamic>> detectSensitiveColumns() async {
    try {
      _consoleLogService.info('Detecting sensitive columns...',
          function: 'detectSensitiveColumns');
      final response = await http.get(
        Uri.parse('$baseUrl/fitness/sensitive-columns'),
      );

      if (response.statusCode == 200) {
        _consoleLogService.success('Sensitive columns detection completed',
            function: 'detectSensitiveColumns');
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        // Return empty result if error, don't throw
        return {
          'success': false,
          'sensitive_columns': {},
          'count': 0,
          'error': error['error'] ?? 'Failed to detect sensitive columns'
        };
      }
    } catch (e) {
      // Log but don't throw - feature is non-critical
      _consoleLogService.warning('Error detecting sensitive columns: $e',
          function: 'detectSensitiveColumns');
      return {
        'success': false,
        'sensitive_columns': {},
        'count': 0,
        'error': 'Error detecting sensitive columns: $e'
      };
    }
  }

  /// Clean data using evolutionary algorithms
  Future<Map<String, dynamic>> cleanDataEvolutionary({
    required String method,
    bool saveResult = true,
    bool trackModifications = true,
    Map<String, dynamic>? parameters,
    List<String>? columns,
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
          if (columns != null && columns.isNotEmpty) 'columns': columns,
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
          'ai_modified_cells': jsonResponse['ai_modified_cells'],
          'error_cells': jsonResponse['error_cells'] ?? [],
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
      _consoleLogService.info('Removing null values from data',
          function: 'removeNulls');
      final response = await http.post(
        Uri.parse('$baseUrl/etl/remove-nulls'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
          'how': how,
        }),
      );

      if (response.statusCode == 200) {
        _consoleLogService.success('Null values removed successfully',
            function: 'removeNulls');
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error('Failed to remove nulls: ${error['error']}',
            function: 'removeNulls');
        throw Exception(error['error'] ?? 'Failed to remove nulls');
      }
    } catch (e) {
      _consoleLogService.error('Error removing nulls: $e',
          function: 'removeNulls');
      throw Exception('Error removing nulls: $e');
    }
  }

  /// Remove duplicate rows
  Future<Map<String, dynamic>> removeDuplicates({
    List<String>? columns,
    String keep = 'first',
  }) async {
    try {
      _consoleLogService.info('Removing duplicate rows from data',
          function: 'removeDuplicates');
      final response = await http.post(
        Uri.parse('$baseUrl/etl/remove-duplicates'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          if (columns != null) 'columns': columns,
          'keep': keep,
        }),
      );

      if (response.statusCode == 200) {
        _consoleLogService.success('Duplicate rows removed successfully',
            function: 'removeDuplicates');
        return _parseEtlResponse(response);
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Failed to remove duplicates: ${error['error']}',
            function: 'removeDuplicates');
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

  /// Get backend logs
  Future<List<String>> getBackendLogs() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/logs'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        if (jsonResponse is Map && jsonResponse.containsKey('logs')) {
          final logs = jsonResponse['logs'];
          if (logs is List && logs.isNotEmpty) {
            return logs.map((log) => log.toString()).toList();
          } else {
            return ['No logs yet - waiting for backend operations...'];
          }
        }
      } else if (response.statusCode == 404) {
        return [
          'Backend logs endpoint not found. Make sure server is updated.'
        ];
      }
      return [
        'Unable to connect to backend logs - received status ${response.statusCode}'
      ];
    } on TimeoutException {
      return ['Error: Backend server request timed out'];
    } catch (e) {
      // Handles network errors (connection refused, etc.) and other exceptions
      final errorMsg = e.toString();
      if (errorMsg.contains('Failed to fetch') || errorMsg.contains('NetworkError')) {
        return ['Error: Cannot connect to backend server at $baseUrl'];
      }
      return ['Error fetching backend logs: $e'];
    }
  }

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

  // ============================================================================
  // GENETIC ALGORITHM ENDPOINTS
  // ============================================================================

  /// Analyze population fitness distribution
  Future<Map<String, dynamic>> analyzePopulationFitness({
    required double fitnessThreshold,
  }) async {
    try {
      _consoleLogService.info(
          'Analyzing population fitness (threshold: $fitnessThreshold)',
          function: 'analyzePopulationFitness');

      final response = await http
          .post(
            Uri.parse('$baseUrl/ga/analyze-population'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'fitness_threshold': fitnessThreshold}),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Population analyzed: ${jsonResponse['healthy_records']} healthy, ${jsonResponse['unhealthy_records']} unhealthy',
            function: 'analyzePopulationFitness');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Failed to analyze population: ${error['error'] ?? 'Unknown error'}',
            function: 'analyzePopulationFitness');
        throw Exception(error['error'] ?? 'Failed to analyze population');
      }
    } catch (e) {
      _consoleLogService.error('Error analyzing population: $e',
          function: 'analyzePopulationFitness');
      throw Exception('Error analyzing population: $e');
    }
  }

  /// Select populations for evolution
  Future<Map<String, dynamic>> selectPopulations({
    required double fitnessThreshold,
    int? healthySampleSize,
  }) async {
    try {
      _consoleLogService.info(
          'Selecting populations (threshold: $fitnessThreshold)',
          function: 'selectPopulations');

      final response = await http
          .post(
            Uri.parse('$baseUrl/ga/select-populations'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'fitness_threshold': fitnessThreshold,
              if (healthySampleSize != null)
                'healthy_sample_size': healthySampleSize,
            }),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Populations selected: ${jsonResponse['unhealthy_count']} to evolve, ${jsonResponse['healthy_count']} templates',
            function: 'selectPopulations');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Failed to select populations: ${error['error'] ?? 'Unknown error'}',
            function: 'selectPopulations');
        throw Exception(error['error'] ?? 'Failed to select populations');
      }
    } catch (e) {
      _consoleLogService.error('Error selecting populations: $e',
          function: 'selectPopulations');
      throw Exception('Error selecting populations: $e');
    }
  }

  /// Run genetic algorithm evolution
  Future<Map<String, dynamic>> runGeneticAlgorithmEvolution({
    required Map<String, dynamic> gaConfig,
    required bool trackProgress,
  }) async {
    try {
      _consoleLogService.info(
          'Starting GA evolution (pop: ${gaConfig['population_size']}, gen: ${gaConfig['generations']})',
          function: 'runGeneticAlgorithmEvolution');

      final requestBody = {
        ...gaConfig,
        'track_progress': trackProgress,
      };

      final response = await http
          .post(
            Uri.parse('$baseUrl/ga/run-evolution'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(requestBody),
          )
          .timeout(const Duration(minutes: 5)); // 5 minute timeout for GA

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'GA evolution completed: ${jsonResponse['total_generations']} generations',
            function: 'runGeneticAlgorithmEvolution');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'GA evolution failed: ${error['error'] ?? 'Unknown error'}',
            function: 'runGeneticAlgorithmEvolution');
        throw Exception(error['error'] ?? 'GA evolution failed');
      }
    } catch (e) {
      _consoleLogService.error('Error running GA evolution: $e',
          function: 'runGeneticAlgorithmEvolution');
      throw Exception('Error running GA evolution: $e');
    }
  }

  /// Quick evolution endpoint (one-call)
  Future<Map<String, dynamic>> quickEvolve({
    required double fitnessThreshold,
    int? populationSize,
    int? generations,
    bool saveResult = true,
  }) async {
    try {
      _consoleLogService.info('Starting quick evolution',
          function: 'quickEvolve');

      final response = await http
          .post(
            Uri.parse('$baseUrl/ga/quick-evolve'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'fitness_threshold': fitnessThreshold,
              if (populationSize != null) 'population_size': populationSize,
              if (generations != null) 'generations': generations,
              'save_result': saveResult,
            }),
          )
          .timeout(const Duration(minutes: 5));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('Quick evolution completed',
            function: 'quickEvolve');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error('Quick evolution failed: ${error['error']}',
            function: 'quickEvolve');
        throw Exception(error['error'] ?? 'Quick evolution failed');
      }
    } catch (e) {
      _consoleLogService.error('Error in quick evolution: $e',
          function: 'quickEvolve');
      throw Exception('Error in quick evolution: $e');
    }
  }

  /// Export evolved data
  Future<Map<String, dynamic>> exportEvolvedData({
    required String filename,
    required String format,
  }) async {
    try {
      _consoleLogService.info('Exporting evolved data ($filename.$format)',
          function: 'exportEvolvedData');

      final response = await http
          .post(
            Uri.parse('$baseUrl/ga/export-evolved'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'filename': filename,
              'format': format,
            }),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('Data exported: ${jsonResponse['filename']}',
            function: 'exportEvolvedData');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Export failed: ${error['error'] ?? 'Unknown error'}',
            function: 'exportEvolvedData');
        throw Exception(error['error'] ?? 'Export failed');
      }
    } catch (e) {
      _consoleLogService.error('Error exporting data: $e',
          function: 'exportEvolvedData');
      throw Exception('Error exporting data: $e');
    }
  }

  // ============================================================================
  // UNIFIED EVOLUTIONARY ALGORITHM ENDPOINTS (All Methods: GA, PSO, DE, ES)
  // ============================================================================

  /// Run any evolutionary algorithm method (unified endpoint)
  /// Supports: GA, PSO, Differential Evolution, Evolution Strategy, Hybrid
  Future<Map<String, dynamic>> runEvolutionaryMethod({
    required String method,
    required Map<String, dynamic> config,
  }) async {
    try {
      _consoleLogService.info(
          'Starting $method evolution with config: ${config.keys}',
          function: 'runEvolutionaryMethod');

      final response = await http
          .post(
            Uri.parse('$baseUrl/evo/run'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'method': method,
              'config': config,
            }),
          )
          .timeout(const Duration(minutes: 10));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            '${method.toUpperCase()} evolution completed',
            function: 'runEvolutionaryMethod');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Evolution failed: ${error['error'] ?? 'Unknown error'}',
            function: 'runEvolutionaryMethod');
        throw Exception(error['error'] ?? 'Evolution failed');
      }
    } catch (e) {
      _consoleLogService.error('Error running evolutionary method: $e',
          function: 'runEvolutionaryMethod');
      throw Exception('Error running evolutionary method: $e');
    }
  }

  /// Compare multiple evolutionary algorithm methods
  /// Returns fitness improvement metrics for each method
  Future<Map<String, dynamic>> compareEvolutionaryMethods({
    List<String> methods = const ['ga', 'pso', 'de', 'es', 'hybrid'],
    Map<String, dynamic>? config,
  }) async {
    try {
      _consoleLogService.info('Comparing methods: $methods',
          function: 'compareEvolutionaryMethods');

      final requestConfig = config ??
          {
            'fitness_threshold': 85.0,
            'max_iterations': 50,
            'population_size': 20,
          };

      final response = await http
          .post(
            Uri.parse('$baseUrl/evo/compare'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'methods': methods,
              'config': requestConfig,
            }),
          )
          .timeout(
              const Duration(minutes: 15)); // Longer timeout for comparison

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Comparison complete: Best method is ${jsonResponse['best_method']}',
            function: 'compareEvolutionaryMethods');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Comparison failed: ${error['error'] ?? 'Unknown error'}',
            function: 'compareEvolutionaryMethods');
        throw Exception(error['error'] ?? 'Comparison failed');
      }
    } catch (e) {
      _consoleLogService.error('Error comparing evolutionary methods: $e',
          function: 'compareEvolutionaryMethods');
      throw Exception('Error comparing evolutionary methods: $e');
    }
  }

  // ============================================================================
  // CELL-LEVEL EVOLUTIONARY CLEANING ENDPOINTS
  // ============================================================================

  /// Evolve error cells using evolutionary algorithms
  /// Each algorithm uses its unique mechanism:
  /// - GA: Crossover and mutation from healthy cell populations
  /// - PSO: Velocity-based particle movement towards healthy cell values
  /// - DE: Differential evolution with vector differences from healthy cells
  /// - ES: Evolution strategy with self-adaptive mutation
  /// - Hybrid: PSO for numeric columns, GA for categorical columns
  Future<Map<String, dynamic>> evolveErrorCells({
    required String method,
    bool saveResult = true,
    List<Map<String, dynamic>>? errorCells,
    Map<String, dynamic>? config,
    List<String>? columns, // NEW: Column filter for targeted cleaning
  }) async {
    try {
      _consoleLogService.info(
          'Evolving error cells using ${method.toUpperCase()}${columns != null && columns.isNotEmpty ? " (columns: ${columns.join(", ")})" : " (all columns)"}',
          function: 'evolveErrorCells');

      final response = await http
          .post(
            Uri.parse('$baseUrl/clean/evolve-cells'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'method': method,
              'save_result': saveResult,
              if (errorCells != null) 'error_cells': errorCells,
              if (config != null) 'config': config,
              if (columns != null && columns.isNotEmpty) 'columns': columns,
            }),
          )
          .timeout(const Duration(minutes: 5));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Cell evolution complete: ${jsonResponse['cells_fixed']}/${jsonResponse['cells_evolved']} cells fixed',
            function: 'evolveErrorCells');
        return {
          'success': true,
          'method': jsonResponse['method'],
          'cells_evolved': jsonResponse['cells_evolved'],
          'cells_fixed': jsonResponse['cells_fixed'],
          'cells_failed': jsonResponse['cells_failed'],
          'average_fitness_before': jsonResponse['average_fitness_before'],
          'average_fitness_after': jsonResponse['average_fitness_after'],
          'fitness_improvement': jsonResponse['fitness_improvement'],
          'evolved_cells': jsonResponse['evolved_cells'],
          'fitness_history': jsonResponse['fitness_history'],
          'data': jsonResponse['data'] != null
              ? (jsonResponse['data'] as List)
                  .map((row) => List<dynamic>.from(row))
                  .toList()
              : null,
          'columns': jsonResponse['columns'] != null
              ? List<String>.from(jsonResponse['columns'])
              : null,
          'shape': jsonResponse['shape'],
          'error_cells': jsonResponse['error_cells'] ?? [],
          'ai_modified_cells': jsonResponse['ai_modified_cells'] ?? jsonResponse['evolved_cells'] ?? [],
          'column_types': jsonResponse['column_types'] ?? {},
          'warnings': jsonResponse['warnings'] ?? [],
          'message': jsonResponse['message'],
          // Algorithm-specific metrics for visualization
          'algorithm_metrics': jsonResponse['algorithm_metrics'],
        };
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Cell evolution failed: ${error['error'] ?? 'Unknown error'}',
            function: 'evolveErrorCells');
        throw Exception(error['error'] ?? 'Failed to evolve cells');
      }
    } catch (e) {
      _consoleLogService.error('Error evolving cells: $e',
          function: 'evolveErrorCells');
      throw Exception('Error evolving cells: $e');
    }
  }

  /// Compare all cell evolution methods
  Future<Map<String, dynamic>> compareCellEvolutionMethods({
    bool quickMode = true,
  }) async {
    try {
      _consoleLogService.info(
          'Comparing cell evolution methods (quick: $quickMode)',
          function: 'compareCellEvolutionMethods');

      final response = await http
          .post(
            Uri.parse('$baseUrl/clean/evolve-cells/compare'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'quick_mode': quickMode}),
          )
          .timeout(const Duration(minutes: 10));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Comparison complete: Best method is ${jsonResponse['best_method']}',
            function: 'compareCellEvolutionMethods');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Comparison failed: ${error['error'] ?? 'Unknown error'}',
            function: 'compareCellEvolutionMethods');
        throw Exception(error['error'] ?? 'Comparison failed');
      }
    } catch (e) {
      _consoleLogService.error('Error comparing cell evolution methods: $e',
          function: 'compareCellEvolutionMethods');
      throw Exception('Error comparing cell evolution methods: $e');
    }
  }

  /// Preview cell evolution without applying changes
  Future<Map<String, dynamic>> previewCellEvolution({
    String method = 'hybrid',
    int maxCells = 10,
  }) async {
    try {
      _consoleLogService.info(
          'Previewing cell evolution using ${method.toUpperCase()}',
          function: 'previewCellEvolution');

      final response = await http
          .post(
            Uri.parse('$baseUrl/clean/evolve-cells/preview'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'method': method,
              'max_cells': maxCells,
            }),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Preview complete: ${jsonResponse['would_fix']}/${jsonResponse['previewed_cells']} would be fixed',
            function: 'previewCellEvolution');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Preview failed: ${error['error'] ?? 'Unknown error'}',
            function: 'previewCellEvolution');
        throw Exception(error['error'] ?? 'Preview failed');
      }
    } catch (e) {
      _consoleLogService.error('Error previewing cell evolution: $e',
          function: 'previewCellEvolution');
      throw Exception('Error previewing cell evolution: $e');
    }
  }

  /// Apply the previewed cell evolution changes
  /// This ensures the exact same changes shown in preview are applied
  Future<Map<String, dynamic>> applyPreviewedChanges({
    bool saveResult = true,
  }) async {
    try {
      _consoleLogService.info(
          'Applying previewed cell evolution changes',
          function: 'applyPreviewedChanges');

      final response = await http
          .post(
            Uri.parse('$baseUrl/clean/apply-preview'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'save_result': saveResult,
            }),
          )
          .timeout(const Duration(minutes: 2));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Applied preview: ${jsonResponse['cells_fixed']}/${jsonResponse['cells_evolved']} cells fixed',
            function: 'applyPreviewedChanges');
        return {
          'success': true,
          'method': jsonResponse['method'],
          'cells_evolved': jsonResponse['cells_evolved'],
          'cells_fixed': jsonResponse['cells_fixed'],
          'cells_failed': jsonResponse['cells_failed'],
          'average_fitness_before': jsonResponse['average_fitness_before'],
          'average_fitness_after': jsonResponse['average_fitness_after'],
          'fitness_improvement': jsonResponse['fitness_improvement'],
          'evolved_cells': jsonResponse['evolved_cells'],
          'fitness_history': jsonResponse['fitness_history'],
          'data': jsonResponse['data'] != null
              ? (jsonResponse['data'] as List)
                  .map((row) => List<dynamic>.from(row))
                  .toList()
              : null,
          'columns': jsonResponse['columns'] != null
              ? List<String>.from(jsonResponse['columns'])
              : null,
          'shape': jsonResponse['shape'],
          'error_cells': jsonResponse['error_cells'] ?? [],
          'ai_modified_cells': jsonResponse['ai_modified_cells'] ?? [],
          'column_types': jsonResponse['column_types'] ?? {},
          'warnings': jsonResponse['warnings'] ?? [],
          'message': jsonResponse['message'],
        };
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Apply preview failed: ${error['error'] ?? 'Unknown error'}',
            function: 'applyPreviewedChanges');
        throw Exception(error['error'] ?? 'Apply preview failed');
      }
    } catch (e) {
      _consoleLogService.error('Error applying previewed changes: $e',
          function: 'applyPreviewedChanges');
      throw Exception('Error applying previewed changes: $e');
    }
  }

  // =========================================================================
  // SECRET DEMO/TEST ENDPOINTS (Development Testing)
  // =========================================================================

  /// Get available demo algorithms
  Future<Map<String, dynamic>> getDemoAlgorithms() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/demo/algorithms'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get demo algorithms');
      }
    } catch (e) {
      throw Exception('Error getting demo algorithms: $e');
    }
  }

  /// Run a demo for an evolutionary algorithm
  Future<Map<String, dynamic>> runDemo({
    required String algorithm,
    required String demoType,
    required String secretKey,
  }) async {
    try {
      _consoleLogService.info(
          'Running $demoType for ${algorithm.toUpperCase()}',
          function: 'runDemo');

      final response = await http
          .post(
            Uri.parse('$baseUrl/demo/run'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'algorithm': algorithm,
              'demo_type': demoType,
              'secret_key': secretKey,
            }),
          )
          .timeout(const Duration(minutes: 3));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            '${algorithm.toUpperCase()} $demoType completed',
            function: 'runDemo');
        return jsonResponse;
      } else if (response.statusCode == 403) {
        throw Exception('Unauthorized: Invalid secret key');
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Demo run failed');
      }
    } catch (e) {
      _consoleLogService.error('Error running demo: $e', function: 'runDemo');
      throw Exception('Error running demo: $e');
    }
  }

  /// Compare all evolutionary algorithms on the same problem
  Future<Map<String, dynamic>> compareAlgorithms({
    required String problem,
    required String secretKey,
  }) async {
    try {
      _consoleLogService.info('Comparing algorithms on $problem problem',
          function: 'compareAlgorithms');

      final response = await http
          .post(
            Uri.parse('$baseUrl/demo/compare'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'problem': problem,
              'secret_key': secretKey,
            }),
          )
          .timeout(const Duration(minutes: 5));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Algorithm comparison completed. Best: ${jsonResponse['best_algorithm']}',
            function: 'compareAlgorithms');
        return jsonResponse;
      } else if (response.statusCode == 403) {
        throw Exception('Unauthorized: Invalid secret key');
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Comparison failed');
      }
    } catch (e) {
      _consoleLogService.error('Error comparing algorithms: $e',
          function: 'compareAlgorithms');
      throw Exception('Error comparing algorithms: $e');
    }
  }

  /// Run stress test on evolutionary algorithms
  Future<Map<String, dynamic>> stressTestAlgorithms({
    required String algorithm,
    required int iterations,
    required String secretKey,
  }) async {
    try {
      _consoleLogService.info(
          'Running stress test: $algorithm ($iterations iterations)',
          function: 'stressTestAlgorithms');

      final response = await http
          .post(
            Uri.parse('$baseUrl/demo/stress-test'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'algorithm': algorithm,
              'iterations': iterations,
              'secret_key': secretKey,
            }),
          )
          .timeout(const Duration(minutes: 10));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('Stress test completed',
            function: 'stressTestAlgorithms');
        return jsonResponse;
      } else if (response.statusCode == 403) {
        throw Exception('Unauthorized: Invalid secret key');
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Stress test failed');
      }
    } catch (e) {
      _consoleLogService.error('Error in stress test: $e',
          function: 'stressTestAlgorithms');
      throw Exception('Error in stress test: $e');
    }
  }

  // =========================================================================
  // AZURE OPENAI CHAT ENDPOINTS
  // =========================================================================

  /// Check Azure OpenAI configuration status
  Future<Map<String, dynamic>> checkOpenAIStatus() async {
    try {
      _consoleLogService.info('Checking Azure OpenAI configuration',
          function: 'checkOpenAIStatus');

      final response = await http
          .get(Uri.parse('$baseUrl/openai/status'))
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'OpenAI status: ${jsonResponse['message']}',
            function: 'checkOpenAIStatus');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        return {
          'available': false,
          'configured': false,
          'message': error['error'] ?? 'Failed to check status',
        };
      }
    } catch (e) {
      _consoleLogService.warning('Error checking OpenAI status: $e',
          function: 'checkOpenAIStatus');
      return {
        'available': false,
        'configured': false,
        'message': 'Backend not reachable: $e',
      };
    }
  }

  /// Send a chat message to Azure OpenAI
  Future<Map<String, dynamic>> sendOpenAIChat({
    required String message,
    bool includeDataContext = true,
    List<Map<String, dynamic>>? conversationHistory,
  }) async {
    try {
      _consoleLogService.info('Sending chat message to Azure OpenAI',
          function: 'sendOpenAIChat');

      final response = await http
          .post(
            Uri.parse('$baseUrl/openai/chat'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'message': message,
              'include_data_context': includeDataContext,
              if (conversationHistory != null)
                'conversation_history': conversationHistory,
            }),
          )
          .timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('Chat response received',
            function: 'sendOpenAIChat');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Chat failed: ${error['error'] ?? 'Unknown error'}',
            function: 'sendOpenAIChat');
        throw Exception(error['error'] ?? 'Failed to send chat message');
      }
    } catch (e) {
      _consoleLogService.error('Error sending chat: $e',
          function: 'sendOpenAIChat');
      throw Exception('Error sending chat: $e');
    }
  }

  /// Execute a natural language data modification command
  Future<Map<String, dynamic>> executeOpenAICommand({
    required String command,
    bool preview = false,
  }) async {
    try {
      _consoleLogService.info('Executing AI command: $command',
          function: 'executeOpenAICommand');

      final response = await http
          .post(
            Uri.parse('$baseUrl/openai/modify-data'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'command': command,
              'preview': preview,
            }),
          )
          .timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Command executed: ${jsonResponse['operation'] ?? 'unknown'}',
            function: 'executeOpenAICommand');
        return {
          'success': jsonResponse['success'] ?? true,
          'operation': jsonResponse['operation'],
          'description': jsonResponse['description'],
          'column': jsonResponse['column'],
          'parameters': jsonResponse['parameters'],
          'report': jsonResponse['report'],
          'preview': jsonResponse['preview'],
          'data': jsonResponse['data'] != null
              ? (jsonResponse['data'] as List)
                  .map((row) => List<dynamic>.from(row))
                  .toList()
              : null,
          'columns': jsonResponse['columns'] != null
              ? List<String>.from(jsonResponse['columns'])
              : null,
          'shape': jsonResponse['shape'],
          'message': jsonResponse['message'],
        };
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Command failed: ${error['error'] ?? 'Unknown error'}',
            function: 'executeOpenAICommand');
        throw Exception(error['error'] ?? 'Failed to execute command');
      }
    } catch (e) {
      _consoleLogService.error('Error executing command: $e',
          function: 'executeOpenAICommand');
      throw Exception('Error executing command: $e');
    }
  }

  /// Get AI analysis of the current dataset
  Future<Map<String, dynamic>> getOpenAIAnalysis({
    required String analysisType,
  }) async {
    try {
      _consoleLogService.info('Getting AI analysis: $analysisType',
          function: 'getOpenAIAnalysis');

      final response = await http
          .post(
            Uri.parse('$baseUrl/openai/analyze'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'analysis_type': analysisType,
            }),
          )
          .timeout(const Duration(seconds: 90));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('Analysis received: $analysisType',
            function: 'getOpenAIAnalysis');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Analysis failed: ${error['error'] ?? 'Unknown error'}',
            function: 'getOpenAIAnalysis');
        throw Exception(error['error'] ?? 'Failed to get analysis');
      }
    } catch (e) {
      _consoleLogService.error('Error getting analysis: $e',
          function: 'getOpenAIAnalysis');
      throw Exception('Error getting analysis: $e');
    }
  }

  // =========================================================================
  // AI CELL-LEVEL MODIFICATION ENDPOINTS
  // =========================================================================

  /// Send a chat message that can directly modify cells in the dataframe
  /// Returns AI response with cell-level modifications tracked
  Future<Map<String, dynamic>> sendOpenAIChatModify({
    required String message,
    bool autoExecute = true,
  }) async {
    try {
      _consoleLogService.info('Sending chat-modify message to Azure OpenAI',
          function: 'sendOpenAIChatModify');

      final response = await http
          .post(
            Uri.parse('$baseUrl/openai/chat-modify'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'message': message,
              'auto_execute': autoExecute,
            }),
          )
          .timeout(const Duration(seconds: 90));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Chat-modify response: ${jsonResponse['total_cells_modified'] ?? 0} cells modified',
            function: 'sendOpenAIChatModify');
        return {
          'success': jsonResponse['success'] ?? true,
          'message': jsonResponse['message'],
          'operation_type': jsonResponse['operation_type'],
          'affected_column': jsonResponse['affected_column'],
          'modifications': jsonResponse['modifications'] ?? [],
          'applied_modifications': jsonResponse['applied_modifications'] ?? [],
          'modifications_applied': jsonResponse['modifications_applied'] ?? false,
          'total_cells_modified': jsonResponse['total_cells_modified'] ?? 0,
          'suggestions': jsonResponse['suggestions'] ?? [],
          'ai_modifications': jsonResponse['ai_modifications'],
          'data': jsonResponse['data'] != null
              ? (jsonResponse['data'] as List)
                  .map((row) => List<dynamic>.from(row))
                  .toList()
              : null,
          'columns': jsonResponse['columns'] != null
              ? List<String>.from(jsonResponse['columns'])
              : null,
          'shape': jsonResponse['shape'],
          'usage': jsonResponse['usage'],
        };
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Chat-modify failed: ${error['error'] ?? 'Unknown error'}',
            function: 'sendOpenAIChatModify');
        throw Exception(error['error'] ?? 'Failed to send chat-modify message');
      }
    } catch (e) {
      _consoleLogService.error('Error in chat-modify: $e',
          function: 'sendOpenAIChatModify');
      throw Exception('Error in chat-modify: $e');
    }
  }

  /// Get all AI modifications tracked in the current session
  Future<Map<String, dynamic>> getAIModifications() async {
    try {
      _consoleLogService.info('Getting AI modifications',
          function: 'getAIModifications');

      final response = await http
          .get(Uri.parse('$baseUrl/openai/modifications'))
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'AI modifications: ${jsonResponse['modifications']?['total_modifications'] ?? 0} total',
            function: 'getAIModifications');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to get AI modifications');
      }
    } catch (e) {
      _consoleLogService.error('Error getting AI modifications: $e',
          function: 'getAIModifications');
      throw Exception('Error getting AI modifications: $e');
    }
  }

  /// Clear all AI modification tracking
  Future<Map<String, dynamic>> clearAIModifications() async {
    try {
      _consoleLogService.info('Clearing AI modifications',
          function: 'clearAIModifications');

      final response = await http
          .post(
            Uri.parse('$baseUrl/openai/modifications/clear'),
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('AI modifications cleared',
            function: 'clearAIModifications');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to clear AI modifications');
      }
    } catch (e) {
      _consoleLogService.error('Error clearing AI modifications: $e',
          function: 'clearAIModifications');
      throw Exception('Error clearing AI modifications: $e');
    }
  }

  /// Apply pending AI modifications after preview confirmation
  Future<Map<String, dynamic>> applyAIModifications() async {
    try {
      _consoleLogService.info('Applying pending AI modifications',
          function: 'applyAIModifications');

      final response = await http
          .post(
            Uri.parse('$baseUrl/openai/apply-modifications'),
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success(
            'Applied ${jsonResponse['total_cells_modified']} modifications',
            function: 'applyAIModifications');
        return {
          'success': jsonResponse['success'] ?? true,
          'message': jsonResponse['message'],
          'total_cells_modified': jsonResponse['total_cells_modified'] ?? 0,
          'data': jsonResponse['data'] != null
              ? (jsonResponse['data'] as List)
                  .map((row) => List<dynamic>.from(row))
                  .toList()
              : null,
          'columns': jsonResponse['columns'] != null
              ? List<String>.from(jsonResponse['columns'])
              : null,
          'error_cells': jsonResponse['error_cells'],
          'ai_modifications': jsonResponse['ai_modifications'],
        };
      } else {
        final error = jsonDecode(response.body);
        _consoleLogService.error(
            'Apply failed: ${error['error'] ?? 'Unknown error'}',
            function: 'applyAIModifications');
        throw Exception(error['error'] ?? 'Failed to apply modifications');
      }
    } catch (e) {
      _consoleLogService.error('Error applying modifications: $e',
          function: 'applyAIModifications');
      throw Exception('Error applying modifications: $e');
    }
  }

  /// Cancel pending AI modifications
  Future<Map<String, dynamic>> cancelAIModifications() async {
    try {
      _consoleLogService.info('Cancelling pending AI modifications',
          function: 'cancelAIModifications');

      final response = await http
          .post(
            Uri.parse('$baseUrl/openai/cancel-modifications'),
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        _consoleLogService.success('Pending modifications cancelled',
            function: 'cancelAIModifications');
        return jsonResponse;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Failed to cancel modifications');
      }
    } catch (e) {
      _consoleLogService.error('Error cancelling modifications: $e',
          function: 'cancelAIModifications');
      throw Exception('Error cancelling modifications: $e');
    }
  }
}
