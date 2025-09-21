import 'package:flutter/material.dart';

class ProcessDataSection extends StatelessWidget {
  const ProcessDataSection({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Text('Selected Column: '),
                Text('No column selected'),
              ],
            ),
            const SizedBox(height: 8),
            const Row(
              children: [
                Text('Data Type: '),
                Text('N/A'),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Text('Format To: '),
                DropdownButton<String>(
                  value: 'string',
                  items: const [
                    DropdownMenuItem(value: 'string', child: Text('String')),
                    DropdownMenuItem(value: 'int', child: Text('Integer')),
                    DropdownMenuItem(value: 'decimal', child: Text('Decimal')),
                    DropdownMenuItem(
                        value: 'datetime', child: Text('DateTime')),
                  ],
                  onChanged: (value) {
                    // Handle format selection
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
