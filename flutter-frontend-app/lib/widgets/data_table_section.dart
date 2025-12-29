import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';
import 'dart:math';

class DataTableSection extends StatefulWidget {
  const DataTableSection({Key? key}) : super(key: key);

  @override
  State<DataTableSection> createState() => _DataTableSectionState();
}

class _DataTableSectionState extends State<DataTableSection> {
  late List<List<String>> _funnyData;
  late List<String> _funnyColumns;

  @override
  void initState() {
    super.initState();
    _generateFunnyData();
  }

  void _generateFunnyData() {
    final random = Random();
    final dataSetIndex = random.nextInt(5);

    switch (dataSetIndex) {
      case 0:
        _funnyColumns = [
          'Superhero',
          'Power Level',
          'Arch Nemesis',
          'Favorite Food'
        ];
        _funnyData = [
          ['Captain Obvious', '9001', 'The Confuser', 'Clarity Cereal'],
          ['Procrastinator', '42', 'Deadlines', 'Yesterday\'s Coffee'],
          ['Debugger Supreme', '∞', 'Semicolon Thief', 'Stack Overflow'],
          ['Coffee Man', 'Unlimited', 'Sleep', 'More Coffee'],
          ['The Committer', '404', 'Merge Conflicts', 'Pull Requests'],
        ];
        break;
      case 1:
        _funnyColumns = ['Pet', 'Skill', 'Mood', 'Dream Job'];
        _funnyData = [
          ['Keyboard Cat', 'Typing', 'Purr-plexed', 'Stack Overflow Moderator'],
          ['Rubber Duck', 'Debugging', 'Floating', 'Chief Debug Officer'],
          ['Office Plant', 'Photosynthesis', 'Wilting', 'Window Manager'],
          ['Bug', 'Hiding', 'Elusive', 'Production Environment'],
          ['Code Monkey', 'Banana.js', 'Caffeinated', 'Tech Lead'],
        ];
        break;
      case 2:
        _funnyColumns = ['Emotion', 'Trigger', 'Solution', 'Side Effect'];
        _funnyData = [
          ['Excitement', 'Code Works First Try', 'Celebrate!', 'Suspicion'],
          ['Panic', 'Prod is Down', 'Rollback', 'Existential Crisis'],
          ['Joy', 'Merge Approved', 'Dance', 'Imposter Syndrome'],
          ['Confusion', 'Legacy Code', 'Google It', 'More Confusion'],
          ['Relief', 'Tests Pass', 'Ship It', 'New Bug Appears'],
        ];
        break;
      case 3:
        _funnyColumns = [
          'Tool',
          'Promised Feature',
          'Reality',
          'Documentation'
        ];
        _funnyData = [
          [
            'AI Assistant',
            'Writes Perfect Code',
            'Needs Debugging',
            'In Progress'
          ],
          [
            'Framework v2',
            'Backwards Compatible',
            'Rewrite Everything',
            'Coming Soon'
          ],
          [
            'New Package',
            'Solves All Problems',
            'Dependency Hell',
            'See Examples'
          ],
          [
            'IDE Plugin',
            'Increases Productivity',
            'Increases RAM Usage',
            'README.md'
          ],
          ['Code Generator', 'Saves Time', 'Generates Bugs', 'It\'s Obvious'],
        ];
        break;
      default:
        _funnyColumns = ['Error Code', 'Meaning', 'Real Meaning', 'Fix'];
        _funnyData = [
          ['404', 'Not Found', 'I Give Up', 'Check Spelling'],
          ['500', 'Server Error', 'Oops', 'Turn Off & On'],
          ['418', 'I\'m a Teapot', 'Easter Egg', 'Be a Teapot'],
          ['401', 'Unauthorized', 'You Shall Not Pass', 'Use Sudo'],
          ['200', 'OK', 'Surprisingly Working', 'Don\'t Touch It'],
        ];
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<MigrationData>(
      builder: (context, migrationData, child) {
        // If no data is loaded, show funny data
        if (migrationData.data == null || migrationData.data!.isEmpty) {
          return Card(
            elevation: 2,
            child: Column(
              children: [
                // Header with info banner
                Container(
                  padding: const EdgeInsets.all(16.0),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Colors.orange.shade50, Colors.orange.shade100],
                    ),
                    border: Border(
                      bottom: BorderSide(color: Colors.orange.shade300),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.sentiment_very_satisfied,
                          color: Colors.orange.shade700, size: 24),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'No Data Loaded - Here\'s Some Fun Instead! 😄',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.orange.shade900,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Load your data using the "Load Data" button in the toolbar above',
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.orange.shade700,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon:
                            Icon(Icons.refresh, color: Colors.orange.shade700),
                        onPressed: () {
                          setState(() {
                            _generateFunnyData();
                          });
                        },
                        tooltip: 'Generate New Funny Data',
                      ),
                    ],
                  ),
                ),
                // Funny Data Table
                Expanded(
                  child: SingleChildScrollView(
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: DataTable(
                        headingRowColor: MaterialStateProperty.all(
                          Colors.purple.shade50,
                        ),
                        columns: _funnyColumns
                            .map((col) => DataColumn(
                                  label: Text(
                                    col,
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.purple.shade900,
                                    ),
                                  ),
                                ))
                            .toList(),
                        rows: _funnyData
                            .map(
                              (row) => DataRow(
                                cells: row
                                    .map((cell) => DataCell(
                                          Text(
                                            cell,
                                            style: TextStyle(
                                              color: Colors.grey.shade800,
                                            ),
                                          ),
                                        ))
                                    .toList(),
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
                    const SizedBox(width: 16),
                    // Color legend
                    if (migrationData.errorCells != null &&
                            migrationData.errorCells!.isNotEmpty ||
                        migrationData.aiModifiedCells != null &&
                            migrationData.aiModifiedCells!.isNotEmpty)
                      Row(
                        children: [
                          if (migrationData.errorCells != null &&
                              migrationData.errorCells!.isNotEmpty)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 4),
                              margin: const EdgeInsets.only(right: 8),
                              decoration: BoxDecoration(
                                color: Colors.red.shade100,
                                border:
                                    Border.all(color: Colors.red.shade400),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.warning,
                                      size: 14, color: Colors.red.shade700),
                                  const SizedBox(width: 4),
                                  Text(
                                    '${migrationData.errorCells!.length} Issues',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.red.shade900,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          if (migrationData.aiModifiedCells != null &&
                              migrationData.aiModifiedCells!.isNotEmpty)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.green.shade100,
                                border:
                                    Border.all(color: Colors.green.shade400),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.check_circle,
                                      size: 14, color: Colors.green.shade700),
                                  const SizedBox(width: 4),
                                  Text(
                                    '${migrationData.aiModifiedCells!.length} AI Fixed',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.green.shade900,
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
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
                      rows: dataRows.asMap().entries.map(
                        (entry) {
                          final rowIndex = entry.key;
                          final row = entry.value;

                          // Build a set of problem cell positions for this row
                          final problemCells = <int>{};
                          if (migrationData.errorCells != null) {
                            for (final error in migrationData.errorCells!) {
                              // error['row'] is 1-indexed (header is row 0)
                              // rowIndex is 0-indexed for data rows
                              if (error['row'] == rowIndex + 1) {
                                problemCells.add(error['col']);
                              }
                            }
                          }

                          // Build a set of AI-modified cell positions for this row
                          final aiModifiedCells = <int>{};
                          if (migrationData.aiModifiedCells != null) {
                            for (final modified
                                in migrationData.aiModifiedCells!) {
                              // Handle both old format (row/col indices) and new format (row/column name)
                              final modRow = modified['row'];
                              final modCol = modified['col'];
                              final modColumnName = modified['column'];

                              // Check if this modification applies to this row
                              // rowIndex is 0-indexed for data rows
                              // Old format: row is 1-indexed, New format: row is 0-indexed
                              final rowMatch = modRow == rowIndex + 1 || modRow == rowIndex;

                              if (rowMatch) {
                                if (modCol != null) {
                                  // Old format: use column index directly
                                  aiModifiedCells.add(modCol);
                                } else if (modColumnName != null && columns.isNotEmpty) {
                                  // New format: find column index by name
                                  final colIdx = columns.indexOf(modColumnName);
                                  if (colIdx >= 0) {
                                    aiModifiedCells.add(colIdx);
                                  }
                                }
                              }
                            }
                          }

                          return DataRow(
                            cells: (row as List<dynamic>)
                                .asMap()
                                .entries
                                .map((cellEntry) {
                                  final colIndex = cellEntry.key;
                                  final cell = cellEntry.value;
                                  final isProblematic =
                                      problemCells.contains(colIndex);
                                  final isAiModified =
                                      aiModifiedCells.contains(colIndex);

                                  // Determine cell styling based on state
                                  Color? bgColor;
                                  Color? borderColor;
                                  Color? textColor;
                                  FontWeight fontWeight = FontWeight.normal;
                                  String tooltipMessage = '';

                                  if (isAiModified) {
                                    // AI-modified cells: green styling
                                    bgColor = Colors.green.shade100;
                                    borderColor = Colors.green.shade400;
                                    textColor = Colors.green.shade900;
                                    fontWeight = FontWeight.w600;

                                    // Try to get modification details for tooltip
                                    final modDetails = migrationData.getCellModificationDetails(rowIndex, columns[colIndex]);
                                    if (modDetails != null && modDetails['modified_by'] == 'AI') {
                                      final oldVal = modDetails['old_value'] ?? 'null';
                                      final operation = modDetails['operation'] ?? 'modification';
                                      tooltipMessage = '✅ Modified by AI Chat\nOperation: $operation\nOld value: $oldVal';
                                    } else {
                                      tooltipMessage = '✅ Fixed by AI';
                                    }
                                  } else if (isProblematic) {
                                    // Problem cells: red styling
                                    bgColor = Colors.red.shade100;
                                    borderColor = Colors.red.shade400;
                                    textColor = Colors.red.shade900;
                                    fontWeight = FontWeight.w600;
                                    tooltipMessage =
                                        '⚠️ Data quality issue detected';
                                  }

                                  return DataCell(
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 4,
                                        vertical: 2,
                                      ),
                                      decoration: BoxDecoration(
                                        color: bgColor,
                                        border: borderColor != null
                                            ? Border.all(
                                                color: borderColor,
                                                width: 1.5,
                                              )
                                            : null,
                                        borderRadius: (isProblematic ||
                                                isAiModified)
                                            ? BorderRadius.circular(2)
                                            : null,
                                      ),
                                      child: Tooltip(
                                        message: tooltipMessage,
                                        child: SelectableText(
                                          cell?.toString() ?? 'null',
                                          maxLines: 1,
                                          onSelectionChanged:
                                              (selection, cause) {},
                                          style: TextStyle(
                                            color: textColor,
                                            fontWeight: fontWeight,
                                          ),
                                        ),
                                      ),
                                    ),
                                  );
                                })
                                .toList()
                                .cast<DataCell>(),
                          );
                        },
                      ).toList(),
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
