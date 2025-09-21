import 'package:flutter/material.dart';

class DataTableSection extends StatelessWidget {
  const DataTableSection({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: SingleChildScrollView(
          child: DataTable(
            columns: const [
              DataColumn(label: Text('Column 1')),
              DataColumn(label: Text('Column 2')),
            ],
            rows: const [
              DataRow(cells: [
                DataCell(Text('Data 1')),
                DataCell(Text('Data 2')),
              ]),
            ],
          ),
        ),
      ),
    );
  }
}
