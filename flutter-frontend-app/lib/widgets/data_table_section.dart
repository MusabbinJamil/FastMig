import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class DataTableSection extends StatelessWidget {
  const DataTableSection({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        // If no data is loaded
        if (migrationData.data == null || migrationData.data!.isEmpty) {
          return Card(
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.table_chart, size: 64, color: Colors.grey[400]),
                  const SizedBox(height: 16),
                  Text(
                    'No data loaded',
                    style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Upload a file to see data here',
                    style: TextStyle(fontSize: 14, color: Colors.grey[500]),
                  ),
                ],
              ),
            ),
          );
        }

        final data = migrationData.data!;
        final columns = migrationData.columns ?? [];

        // Check if we have at least headers
        if (data.length < 1) {
          return const Card(
            child: Center(child: Text('Invalid data format')),
          );
        }

        // Extract data rows (skip the first row which contains headers)
        final dataRows = data.length > 1 ? data.sublist(1) : [];

        return Card(
          child: Column(
            children: [
              // Header with info
              Container(
                padding: const EdgeInsets.all(8.0),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  border: Border(
                    bottom: BorderSide(color: Colors.grey[300]!),
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.table_rows, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      '${dataRows.length} rows × ${columns.length} columns',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const Spacer(),
                    if (migrationData.selectedColumn != null)
                      Chip(
                        label:
                            Text('Selected: ${migrationData.selectedColumn}'),
                        backgroundColor: Colors.blue[100],
                        deleteIcon: const Icon(Icons.close, size: 18),
                        onDeleted: () {
                          // Clear selection (you might want to add this method)
                        },
                      ),
                  ],
                ),
              ),
              // Data table
              Expanded(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: SingleChildScrollView(
                    child: DataTable(
                      headingRowColor:
                          MaterialStateProperty.all(Colors.grey[200]),
                      columns: columns
                          .map((col) => DataColumn(
                                label: InkWell(
                                  onTap: () {
                                    migrationData.selectColumn(col);
                                  },
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: migrationData.selectedColumn == col
                                          ? Colors.blue[100]
                                          : null,
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Column(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          col,
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            color:
                                                migrationData.selectedColumn ==
                                                        col
                                                    ? Colors.blue[900]
                                                    : Colors.black,
                                          ),
                                        ),
                                        if (migrationData.dtypes != null &&
                                            migrationData.dtypes!
                                                .containsKey(col))
                                          Text(
                                            migrationData.dtypes![col]!,
                                            style: TextStyle(
                                              fontSize: 10,
                                              color: Colors.grey[600],
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                ),
                              ))
                          .toList(),
                      rows: dataRows
                          .map(
                            (row) => DataRow(
                              cells: (row as List<dynamic>)
                                  .map((cell) => DataCell(
                                        Text(
                                          cell?.toString() ?? 'null',
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ))
                                  .toList()
                                  .cast<DataCell>(),
                            ),
                          )
                          .toList(),
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
