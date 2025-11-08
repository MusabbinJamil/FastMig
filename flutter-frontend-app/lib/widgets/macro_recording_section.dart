import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class StepRecordingSection extends StatefulWidget {
  const StepRecordingSection({Key? key}) : super(key: key);

  @override
  State<StepRecordingSection> createState() => _StepRecordingSectionState();
}

class _StepRecordingSectionState extends State<StepRecordingSection> {
  final TextEditingController _stepNameController = TextEditingController();

  @override
  void dispose() {
    _stepNameController.dispose();
    super.dispose();
  }

  Future<void> _saveSteps(MigrationData migrationData) async {
    final name = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Save Steps'),
        content: TextField(
          controller: _stepNameController,
          decoration: const InputDecoration(
            labelText: 'Pipeline Name',
            hintText: 'Enter a name for this pipeline',
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
              Navigator.pop(context, _stepNameController.text);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );

    if (name != null && name.isNotEmpty) {
      await migrationData.saveSteps(name);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Steps "$name" saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
      _stepNameController.clear();
    }
  }

  Future<void> _viewSteps(MigrationData migrationData) async {
    try {
      final result = await migrationData.getRecordedSteps();
      if (context.mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Recorded Steps'),
            content: SizedBox(
              width: double.maxFinite,
              child: result['steps'] != null &&
                      (result['steps'] as List).isNotEmpty
                  ? ListView.builder(
                      shrinkWrap: true,
                      itemCount: (result['steps'] as List).length,
                      itemBuilder: (context, index) {
                        final step = (result['steps'] as List)[index];
                        return Card(
                          child: ListTile(
                            leading: CircleAvatar(
                              child: Text('${index + 1}'),
                            ),
                            title: Text(step['operation'] ?? 'Unknown'),
                            subtitle: Text(
                              'Parameters: ${step['parameters']?.toString() ?? 'None'}',
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        );
                      },
                    )
                  : const Center(
                      child: Text('No steps recorded yet'),
                    ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
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
                Row(
                  children: [
                    const Icon(Icons.video_camera_back, color: Colors.blue),
                    const SizedBox(width: 8),
                    const Text(
                      'Step Recording',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Record transformation steps and replay on new data',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
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
                        label:
                            Text('${migrationData.recordedActionsCount} steps'),
                        backgroundColor: Colors.blue[100],
                        avatar: const Icon(Icons.list, size: 18),
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
                        await migrationData.stopStepRecording();
                      } else {
                        await migrationData.startStepRecording();
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

                // Action Buttons (only when stopped and has steps)
                if (!migrationData.isRecording &&
                    migrationData.recordedActionsCount > 0) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _viewSteps(migrationData),
                          icon: const Icon(Icons.visibility),
                          label: const Text('View Steps'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => _saveSteps(migrationData),
                          icon: const Icon(Icons.save),
                          label: const Text('Save Steps'),
                        ),
                      ),
                    ],
                  ),
                ],

                // Info box
                if (!migrationData.isRecording) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue.shade200),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline,
                            color: Colors.blue.shade700, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Click "Start Recording" then perform your data transformations. Each operation will be recorded.',
                            style: TextStyle(
                              color: Colors.blue.shade700,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
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
