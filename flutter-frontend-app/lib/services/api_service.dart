import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl =
      'http://localhost:5000'; // Adjust port as needed

  Future<List<List<dynamic>>> processData(
      String filePath, String column, String format) async {
    final response = await http.post(
      Uri.parse('$baseUrl/process'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'file_path': filePath,
        'column': column,
        'format': format,
      }),
    );

    if (response.statusCode == 200) {
      final List<dynamic> jsonResponse = jsonDecode(response.body);
      return jsonResponse.map((row) => List<dynamic>.from(row)).toList();
    } else {
      throw Exception('Failed to process data');
    }
  }

  Future<List<List<dynamic>>> loadFile(String filePath) async {
    final response = await http.post(
      Uri.parse('$baseUrl/load'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'file_path': filePath}),
    );

    if (response.statusCode == 200) {
      final List<dynamic> jsonResponse = jsonDecode(response.body);
      return jsonResponse.map((row) => List<dynamic>.from(row)).toList();
    } else {
      throw Exception('Failed to load file');
    }
  }
}
