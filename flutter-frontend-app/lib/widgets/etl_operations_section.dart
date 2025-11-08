import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/migration_data.dart';

class EtlOperationsSection extends StatefulWidget {
  const EtlOperationsSection({Key? key}) : super(key: key);

  @override
  State<EtlOperationsSection> createState() => _EtlOperationsSectionState();
}

class _EtlOperationsSectionState extends State<EtlOperationsSection> {
  String _selectedOperation = 'remove_nulls';
  final _findController = TextEditingController();
  final _replaceController = TextEditingController();
  final _fillValueController = TextEditingController();
  String _fillMethod = 'mean';
  String _caseType = 'upper';
  String _filterOperator = '==';
  final _filterValueController = TextEditingController();
  String _removeNullsHow = 'any';
  String _removeDuplicatesKeep = 'first';
  bool _useRegex = false;

  @override
  void dispose() {
    _findController.dispose();
    _replaceController.dispose();
    _fillValueController.dispose();
    _filterValueController.dispose();
    super.dispose();
  }

  Future<void> _executeOperation(MigrationData migrationData) async {
    try {
      Map<String, dynamic>? report;

      switch (_selectedOperation) {
        case 'remove_nulls':
          report = await migrationData.removeNulls(how: _removeNullsHow);
          break;

        case 'remove_duplicates':
          report =
              await migrationData.removeDuplicates(keep: _removeDuplicatesKeep);
          break;

        case 'trim_whitespace':
          report = await migrationData.trimWhitespace();
          break;

        case 'find_replace':
          if (migrationData.selectedColumn == null) {
            throw Exception('Please select a column first');
          }
          report = await migrationData.findReplace(
            column: migrationData.selectedColumn!,
            findValue: _findController.text,
            replaceValue: _replaceController.text,
            useRegex: _useRegex,
          );
          break;

        case 'fill_nulls':
          if (migrationData.selectedColumn == null) {
            throw Exception('Please select a column first');
          }
          report = await migrationData.fillNulls(
            column: migrationData.selectedColumn!,
            method: _fillMethod,
            value: _fillMethod == 'constant' ? _fillValueController.text : null,
          );
          break;

        case 'change_case':
          if (migrationData.selectedColumn == null) {
            throw Exception('Please select a column first');
          }
          report = await migrationData.changeCase(
            column: migrationData.selectedColumn!,
            caseType: _caseType,
          );
          break;

        case 'filter_rows':
          if (migrationData.selectedColumn == null) {
            throw Exception('Please select a column first');
          }
          report = await migrationData.filterRows(
            column: migrationData.selectedColumn!,
            operator: _filterOperator,
            value: _filterValueController.text,
          );
          break;

        case 'sort_data':
          if (migrationData.selectedColumn == null) {
            throw Exception('Please select a column first');
          }
          report = await migrationData.sortData(
            columns: [migrationData.selectedColumn!],
            ascending: true,
          );
          break;
      }

      if (context.mounted && report != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Operation completed: ${report['operation']}'),
            backgroundColor: Colors.green,
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
                    const Icon(Icons.cleaning_services, color: Colors.blue),
                    const SizedBox(width: 8),
                    const Text(
                      'ETL Operations',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Advanced data cleaning and transformation',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
                const SizedBox(height: 16),

                // Operation Selector
                DropdownButtonFormField<String>(
                  value: _selectedOperation,
                  decoration: const InputDecoration(
                    labelText: 'Select Operation',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(
                        value: 'remove_nulls',
                        child: Text('🗑️ Remove Null Rows')),
                    DropdownMenuItem(
                        value: 'remove_duplicates',
                        child: Text('🔄 Remove Duplicates')),
                    DropdownMenuItem(
                        value: 'trim_whitespace',
                        child: Text('✂️ Trim Whitespace')),
                    DropdownMenuItem(
                        value: 'find_replace',
                        child: Text('🔍 Find & Replace')),
                    DropdownMenuItem(
                        value: 'fill_nulls',
                        child: Text('📝 Fill Null Values')),
                    DropdownMenuItem(
                        value: 'change_case',
                        child: Text('🔠 Change Text Case')),
                    DropdownMenuItem(
                        value: 'filter_rows', child: Text('🔎 Filter Rows')),
                    DropdownMenuItem(
                        value: 'sort_data', child: Text('📊 Sort Data')),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _selectedOperation = value!;
                    });
                  },
                ),
                const SizedBox(height: 16),

                // Operation-specific parameters
                _buildOperationParameters(migrationData),

                const SizedBox(height: 16),

                // Execute Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed:
                        migrationData.data == null || migrationData.isLoading
                            ? null
                            : () => _executeOperation(migrationData),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Execute Operation'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildOperationParameters(MigrationData migrationData) {
    switch (_selectedOperation) {
      case 'remove_nulls':
        return DropdownButtonFormField<String>(
          value: _removeNullsHow,
          decoration: const InputDecoration(
            labelText: 'Remove rows with',
            border: OutlineInputBorder(),
            helperText: 'Choose when to remove rows',
          ),
          items: const [
            DropdownMenuItem(value: 'any', child: Text('Any null value')),
            DropdownMenuItem(value: 'all', child: Text('All null values')),
          ],
          onChanged: (value) {
            setState(() {
              _removeNullsHow = value!;
            });
          },
        );

      case 'remove_duplicates':
        return DropdownButtonFormField<String>(
          value: _removeDuplicatesKeep,
          decoration: const InputDecoration(
            labelText: 'Keep which duplicate',
            border: OutlineInputBorder(),
            helperText: 'Choose which duplicate to keep',
          ),
          items: const [
            DropdownMenuItem(value: 'first', child: Text('First occurrence')),
            DropdownMenuItem(value: 'last', child: Text('Last occurrence')),
          ],
          onChanged: (value) {
            setState(() {
              _removeDuplicatesKeep = value!;
            });
          },
        );

      case 'find_replace':
        return Column(
          children: [
            if (migrationData.selectedColumn != null)
              Chip(
                label: Text('Column: ${migrationData.selectedColumn}'),
                avatar: const Icon(Icons.table_chart, size: 18),
              ),
            const SizedBox(height: 8),
            TextField(
              controller: _findController,
              decoration: const InputDecoration(
                labelText: 'Find value',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.search),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _replaceController,
              decoration: const InputDecoration(
                labelText: 'Replace with',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.edit),
              ),
            ),
            const SizedBox(height: 8),
            CheckboxListTile(
              title: const Text('Use Regular Expression'),
              value: _useRegex,
              onChanged: (value) {
                setState(() {
                  _useRegex = value ?? false;
                });
              },
            ),
          ],
        );

      case 'fill_nulls':
        return Column(
          children: [
            if (migrationData.selectedColumn != null)
              Chip(
                label: Text('Column: ${migrationData.selectedColumn}'),
                avatar: const Icon(Icons.table_chart, size: 18),
              ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _fillMethod,
              decoration: const InputDecoration(
                labelText: 'Fill method',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(
                    value: 'forward',
                    child: Text('Forward fill (use previous)')),
                DropdownMenuItem(
                    value: 'backward', child: Text('Backward fill (use next)')),
                DropdownMenuItem(value: 'mean', child: Text('Mean (average)')),
                DropdownMenuItem(value: 'median', child: Text('Median')),
                DropdownMenuItem(
                    value: 'mode', child: Text('Mode (most common)')),
                DropdownMenuItem(
                    value: 'constant', child: Text('Constant value')),
              ],
              onChanged: (value) {
                setState(() {
                  _fillMethod = value!;
                });
              },
            ),
            if (_fillMethod == 'constant') ...[
              const SizedBox(height: 8),
              TextField(
                controller: _fillValueController,
                decoration: const InputDecoration(
                  labelText: 'Fill value',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ],
        );

      case 'change_case':
        return Column(
          children: [
            if (migrationData.selectedColumn != null)
              Chip(
                label: Text('Column: ${migrationData.selectedColumn}'),
                avatar: const Icon(Icons.table_chart, size: 18),
              ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _caseType,
              decoration: const InputDecoration(
                labelText: 'Case type',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'upper', child: Text('UPPERCASE')),
                DropdownMenuItem(value: 'lower', child: Text('lowercase')),
                DropdownMenuItem(value: 'title', child: Text('Title Case')),
                DropdownMenuItem(
                    value: 'capitalize', child: Text('Capitalize')),
              ],
              onChanged: (value) {
                setState(() {
                  _caseType = value!;
                });
              },
            ),
          ],
        );

      case 'filter_rows':
        return Column(
          children: [
            if (migrationData.selectedColumn != null)
              Chip(
                label: Text('Column: ${migrationData.selectedColumn}'),
                avatar: const Icon(Icons.table_chart, size: 18),
              ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _filterOperator,
              decoration: const InputDecoration(
                labelText: 'Operator',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: '==', child: Text('Equals (==)')),
                DropdownMenuItem(value: '!=', child: Text('Not equals (!=)')),
                DropdownMenuItem(value: '>', child: Text('Greater than (>)')),
                DropdownMenuItem(value: '<', child: Text('Less than (<)')),
                DropdownMenuItem(
                    value: '>=', child: Text('Greater or equal (>=)')),
                DropdownMenuItem(
                    value: '<=', child: Text('Less or equal (<=)')),
                DropdownMenuItem(value: 'contains', child: Text('Contains')),
                DropdownMenuItem(
                    value: 'startswith', child: Text('Starts with')),
                DropdownMenuItem(value: 'endswith', child: Text('Ends with')),
              ],
              onChanged: (value) {
                setState(() {
                  _filterOperator = value!;
                });
              },
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _filterValueController,
              decoration: const InputDecoration(
                labelText: 'Filter value',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.filter_alt),
              ),
            ),
          ],
        );

      case 'sort_data':
        return Column(
          children: [
            if (migrationData.selectedColumn != null)
              Chip(
                label: Text('Sort by: ${migrationData.selectedColumn}'),
                avatar: const Icon(Icons.sort, size: 18),
              ),
            const SizedBox(height: 8),
            const Text(
              'Data will be sorted in ascending order',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        );

      case 'trim_whitespace':
        return const Column(
          children: [
            Text(
              'This will trim leading and trailing whitespace from all text columns',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        );

      default:
        return const SizedBox.shrink();
    }
  }
}
