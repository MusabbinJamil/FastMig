import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class MacroRecordingSection extends StatefulWidget {
  const MacroRecordingSection({Key? key}) : super(key: key);

  @override
  State<MacroRecordingSection> createState() => _MacroRecordingSectionState();
}

class _MacroRecordingSectionState extends State<MacroRecordingSection> {
  final TextEditingController _recordingNameController =
      TextEditingController();

  @override
  void dispose() {
    _recordingNameController.dispose();
    super.dispose();
  }

  Future<void> _saveRecording(MigrationData migrationData) async {
    final name = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Save Recording'),
        content: TextField(
          controller: _recordingNameController,
          decoration: const InputDecoration(
            labelText: 'Recording Name',
            hintText: 'Enter a name for this recording',
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context, _recordingNameController.text);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );

    if (name != null && name.isNotEmpty) {
      await migrationData.saveRecording(name);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Recording "$name" saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
      _recordingNameController.clear();
    }
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
                  'Macro Recording',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),

                // Recording Status
                Row(
                  children: [
                    Icon(
                      migrationData.isRecording
                          ? Icons.radio_button_checked
                          : Icons.radio_button_unchecked,
                      color:
                          migrationData.isRecording ? Colors.red : Colors.grey,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      migrationData.isRecording
                          ? 'Recording...'
                          : 'Not Recording',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: migrationData.isRecording
                            ? Colors.red
                            : Colors.grey,
                      ),
                    ),
                    if (migrationData.recordedActionsCount > 0) ...[
                      const SizedBox(width: 8),
                      Chip(
                        label: Text(
                            '${migrationData.recordedActionsCount} actions'),
                        backgroundColor: Colors.blue[100],
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 16),

                // Start/Stop Recording Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      if (migrationData.isRecording) {
                        await migrationData.stopRecording();
                      } else {
                        await migrationData.startRecording();
                      }
                    },
                    icon: Icon(
                      migrationData.isRecording
                          ? Icons.stop
                          : Icons.fiber_manual_record,
                    ),
                    label: Text(
                      migrationData.isRecording
                          ? 'Stop Recording'
                          : 'Start Recording',
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor:
                          migrationData.isRecording ? Colors.red : Colors.blue,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),

                // Save Recording Button (only when stopped and has actions)
                if (!migrationData.isRecording &&
                    migrationData.recordedActionsCount > 0) ...[
                  const SizedBox(height: 8),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => _saveRecording(migrationData),
                      icon: const Icon(Icons.save),
                      label: const Text('Save Recording'),
                    ),
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
