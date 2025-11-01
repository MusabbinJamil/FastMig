import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class ProcessDataSection extends StatefulWidget {
  const ProcessDataSection({Key? key}) : super(key: key);

  @override
  State<ProcessDataSection> createState() => _ProcessDataSectionState();
}

class _ProcessDataSectionState extends State<ProcessDataSection> {
  String _selectedFormat = 'string';
  final TextEditingController _dateFormatController = TextEditingController();
  bool _showDateFormatInput = false;

  @override
  void dispose() {
    _dateFormatController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Process Data',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),

                // Selected Column Info
                Row(
                  children: [
                    const Text('Selected Column: ',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Expanded(
                      child: Text(
                        migrationData.selectedColumn ?? 'No column selected',
                        style: TextStyle(
                          color: migrationData.selectedColumn != null
                              ? Colors.blue
                              : Colors.grey,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // Current Data Type
                Row(
                  children: [
                    const Text('Current Type: ',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Text(
                      migrationData.selectedDataType ?? 'N/A',
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Format Selector
                Row(
                  children: [
                    const Text('Convert To: ',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: DropdownButton<String>(
                        value: _selectedFormat,
                        isExpanded: true,
                        items: const [
                          DropdownMenuItem(
                              value: 'string', child: Text('String/Text')),
                          DropdownMenuItem(
                              value: 'int', child: Text('Integer')),
                          DropdownMenuItem(
                              value: 'decimal', child: Text('Decimal/Float')),
                          DropdownMenuItem(
                              value: 'datetime', child: Text('DateTime')),
                          DropdownMenuItem(
                              value: 'bool', child: Text('Boolean')),
                          DropdownMenuItem(
                              value: 'category', child: Text('Category')),
                          DropdownMenuItem(
                              value: 'object', child: Text('Object')),
                        ],
                        onChanged: (value) {
                          if (value != null) {
                            setState(() {
                              _selectedFormat = value;
                              _showDateFormatInput = value == 'datetime';
                            });
                          }
                        },
                      ),
                    ),
                  ],
                ),

                // DateTime Format Input (conditional)
                if (_showDateFormatInput) ...[
                  const SizedBox(height: 12),
                  TextField(
                    controller: _dateFormatController,
                    decoration: const InputDecoration(
                      labelText: 'DateTime Format (optional)',
                      hintText: 'e.g., %Y-%m-%d, %d/%m/%Y',
                      helperText: 'Leave empty for auto-detection',
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
                ],

                const SizedBox(height: 16),

                // Process Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: (migrationData.selectedColumn != null &&
                            !migrationData.isLoading)
                        ? () async {
                            await migrationData.processData(
                              _selectedFormat,
                              dateFormat: _dateFormatController.text.isEmpty
                                  ? null
                                  : _dateFormatController.text,
                            );
                            if (migrationData.errorMessage == null) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Data processed successfully!'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            } else {
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
                            height: 16,
                            width: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Icon(Icons.transform),
                    label: const Text('Process Data'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),

                // File Metadata (if available)
                if (migrationData.encoding != null ||
                    migrationData.fileFormat != null) ...[
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 8),
                  const Text(
                    'File Information:',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  if (migrationData.fileFormat != null)
                    Text(
                      'Format: ${migrationData.fileFormat}',
                      style: const TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                  if (migrationData.encoding != null)
                    Text(
                      'Encoding: ${migrationData.encoding}',
                      style: const TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                  if (migrationData.shape != null)
                    Text(
                      'Shape: ${migrationData.shape![0]} rows × ${migrationData.shape![1]} columns',
                      style: const TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}
