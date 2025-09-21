import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

class LoadDataSection extends StatelessWidget {
  const LoadDataSection({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Load Data',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('No file selected'),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () async {
                final result = await FilePicker.platform.pickFiles();
                if (result != null) {
                  // Handle file selection
                }
              },
              child: const Text('Select File'),
            ),
          ],
        ),
      ),
    );
  }
}
