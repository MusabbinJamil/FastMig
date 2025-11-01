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

                  // File Path
                  TextField(
                    controller: _pathController,
                    decoration: InputDecoration(
                      labelText: 'Output Path',
                      hintText: 'e.g., output/data.$_selectedFormat',
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.folder_open),
                        onPressed: () {
                          // TODO: Implement file picker for save location
                        },
                      ),
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
                              if (_pathController.text.isEmpty) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content:
                                        Text('Please enter an output path'),
                                    backgroundColor: Colors.orange,
                                  ),
                                );
                                return;
                              }

                              await migrationData
                                  .exportData(_pathController.text);

                              if (migrationData.errorMessage == null) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content:
                                        Text('Data exported successfully!'),
                                    backgroundColor: Colors.green,
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
                      label: const Text('Export Data'),
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
          // Update path extension
          if (_pathController.text.isNotEmpty) {
            final pathWithoutExt = _pathController.text.split('.').first;
            _pathController.text = '$pathWithoutExt.$format';
          }
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
