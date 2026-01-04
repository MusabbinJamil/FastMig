import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class ExportSection extends StatefulWidget {
  const ExportSection({Key? key}) : super(key: key);

  @override
  State<ExportSection> createState() => _ExportSectionState();
}

class _ExportSectionState extends State<ExportSection> {
  final TextEditingController _pathController = TextEditingController();
  String _selectedFormat = 'csv';

  @override
  void dispose() {
    _pathController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        return Center(
          child: Card(
            elevation: 2,
            child: Container(
              padding: const EdgeInsets.all(40),
              constraints: const BoxConstraints(maxWidth: 600),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.download,
                          size: 48, color: Colors.blue.shade700),
                      const SizedBox(width: 16),
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Export Data',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text('Save your processed data'),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 30),

                  // Format Selection
                  const Text(
                    'Export Format',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 10,
                    children: [
                      _buildFormatChip('csv', 'CSV', Icons.description),
                      _buildFormatChip('xlsx', 'Excel', Icons.table_chart),
                      _buildFormatChip('json', 'JSON', Icons.code),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Filename
                  TextField(
                    controller: _pathController,
                    decoration: InputDecoration(
                      labelText: 'Filename',
                      hintText: 'e.g., my_data',
                      border: const OutlineInputBorder(),
                      suffixText: '.$_selectedFormat',
                      prefixIcon: const Icon(Icons.insert_drive_file),
                    ),
                  ),
                  const SizedBox(height: 30),

                  // Export Button
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton.icon(
                      onPressed: (migrationData.data != null &&
                              !migrationData.isLoading)
                          ? () async {
                              // Use default filename if empty
                              String filename = _pathController.text.trim();
                              if (filename.isEmpty) {
                                filename = 'exported_data';
                              }
                              // Remove extension if user added one
                              if (filename.contains('.')) {
                                filename = filename.split('.').first;
                              }

                              await migrationData.exportData(
                                filename,
                                format: _selectedFormat,
                              );

                              if (context.mounted && migrationData.errorMessage == null) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                        'Downloaded $filename.$_selectedFormat'),
                                    backgroundColor: Colors.green,
                                  ),
                                );
                              } else if (context.mounted && migrationData.errorMessage != null) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(migrationData.errorMessage!),
                                    backgroundColor: Colors.red,
                                  ),
                                );
                              }
                            }
                          : null,
                      icon: migrationData.isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.download),
                      label: Text('Download as ${_selectedFormat.toUpperCase()}'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),

                  if (migrationData.data == null) ...[
                    const SizedBox(height: 20),
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.orange.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.orange.shade200),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline,
                              color: Colors.orange.shade700),
                          const SizedBox(width: 12),
                          const Expanded(
                            child: Text(
                              'Please load data first before exporting',
                              style: TextStyle(fontSize: 14),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildFormatChip(String format, String label, IconData icon) {
    final isSelected = _selectedFormat == format;
    return FilterChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: isSelected ? Colors.white : Colors.grey),
          const SizedBox(width: 8),
          Text(label),
        ],
      ),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _selectedFormat = format;
        });
      },
      selectedColor: Colors.blue.shade700,
      checkmarkColor: Colors.white,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : Colors.black87,
      ),
    );
  }
}
