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
                Row(
                  children: [
                    const Text('Data Type: ',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    Text(
                      migrationData.selectedDataType ?? 'N/A',
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Text('Format To: ',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(width: 8),
                    DropdownButton<String>(
                      value: _selectedFormat,
                      items: const [
                        DropdownMenuItem(
                            value: 'string', child: Text('String')),
                        DropdownMenuItem(value: 'int', child: Text('Integer')),
                        DropdownMenuItem(
                            value: 'decimal', child: Text('Decimal')),
                        DropdownMenuItem(
                            value: 'datetime', child: Text('DateTime')),
                        DropdownMenuItem(value: 'bool', child: Text('Boolean')),
                        DropdownMenuItem(
                            value: 'category', child: Text('Category')),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            _selectedFormat = value;
                          });
                        }
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                ElevatedButton(
                  onPressed: (migrationData.selectedColumn != null &&
                          !migrationData.isLoading)
                      ? () async {
                          await migrationData.processData(_selectedFormat);
                          if (migrationData.errorMessage == null) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Data processed successfully!'),
                                backgroundColor: Colors.green,
                              ),
                            );
                          }
                        }
                      : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                  child: migrationData.isLoading
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Text('Process Data'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
