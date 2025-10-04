import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class LoadDataSection extends StatelessWidget {
  const LoadDataSection({Key? key}) : super(key: key);

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
                const Text('Load Data',
                    style:
                        TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text(
                  migrationData.fileName ?? 'No file selected',
                  style: TextStyle(
                    color: migrationData.fileName != null
                        ? Colors.green
                        : Colors.grey,
                    fontWeight: migrationData.fileName != null
                        ? FontWeight.bold
                        : FontWeight.normal,
                  ),
                ),
                if (migrationData.data != null &&
                    migrationData.data!.length > 1)
                  Padding(
                    padding: const EdgeInsets.only(top: 4.0),
                    child: Text(
                      '${migrationData.data!.length - 1} rows × ${migrationData.columns?.length ?? 0} columns',
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: migrationData.isLoading
                      ? null
                      : () async {
                          await migrationData.pickAndUploadFile();
                        },
                  child: migrationData.isLoading
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Select & Upload File'),
                ),
                if (migrationData.errorMessage != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(
                      migrationData.errorMessage!,
                      style: const TextStyle(color: Colors.red, fontSize: 12),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}
