import 'package:flutter/material.dart';
import '../services/api_service.dart';

class EncodingSection extends StatefulWidget {
  final List<String> columns;

  const EncodingSection({
    Key? key,
    required this.columns,
  }) : super(key: key);

  @override
  State<EncodingSection> createState() => _EncodingSectionState();
}

class _EncodingSectionState extends State<EncodingSection> {
  final ApiService _apiService = ApiService();

  String _encodingType = 'label';
  List<String> _selectedColumns = [];
  bool _saveMapping = true;
  bool _dropFirst = false;
  String _prefixSep = '_';
  bool _isLoading = false;

  String? _errorMessage;
  String? _successMessage;
  Map<String, dynamic>? _lastReport;
  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                const Icon(Icons.transform, color: Colors.blue, size: 28),
                const SizedBox(width: 12),
                const Text(
                  'Machine Readable Transform (Encoding)',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              'Convert categorical data to numeric format for machine learning',
              style: TextStyle(color: Colors.grey, fontSize: 14),
            ),
            const Divider(height: 32),

            // Encoding Type Selection
            _buildEncodingTypeSelector(),
            const SizedBox(height: 16),

            // Column Selection
            _buildColumnSelector(),
            const SizedBox(height: 16),

            // Encoding Options
            _buildEncodingOptions(),
            const SizedBox(height: 24),

            // Action Buttons
            _buildActionButtons(),

            // Messages
            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              _buildErrorMessage(),
            ],
            if (_successMessage != null) ...[
              const SizedBox(height: 16),
              _buildSuccessMessage(),
            ],

            // Report
            if (_lastReport != null) ...[
              const SizedBox(height: 16),
              _buildReport(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildEncodingTypeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Encoding Type',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 12,
          children: [
            ChoiceChip(
              label: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.label, size: 18),
                  SizedBox(width: 6),
                  Text('Label Encoding'),
                ],
              ),
              selected: _encodingType == 'label',
              onSelected: (selected) {
                if (selected) {
                  setState(() {
                    _encodingType = 'label';
                    _clearMessages();
                  });
                }
              },
            ),
            ChoiceChip(
              label: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.grid_on, size: 18),
                  SizedBox(width: 6),
                  Text('One-Hot Encoding'),
                ],
              ),
              selected: _encodingType == 'onehot',
              onSelected: (selected) {
                if (selected) {
                  setState(() {
                    _encodingType = 'onehot';
                    _clearMessages();
                  });
                }
              },
            ),
            ChoiceChip(
              label: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.undo, size: 18),
                  SizedBox(width: 6),
                  Text('Reverse Label Encoding'),
                ],
              ),
              selected: _encodingType == 'reverse',
              onSelected: (selected) {
                if (selected) {
                  setState(() {
                    _encodingType = 'reverse';
                    _clearMessages();
                  });
                }
              },
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          _getEncodingDescription(),
          style: const TextStyle(
              color: Colors.grey, fontSize: 12, fontStyle: FontStyle.italic),
        ),
      ],
    );
  }

  String _getEncodingDescription() {
    switch (_encodingType) {
      case 'label':
        return 'Convert categories to numeric labels (0, 1, 2, ...). Simple and memory-efficient.';
      case 'onehot':
        return 'Create binary columns for each category. No ordinal relationship assumed.';
      case 'reverse':
        return 'Convert previously label-encoded data back to original categories.';
      default:
        return '';
    }
  }

  Widget _buildColumnSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text(
              'Select Columns',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(width: 12),
            TextButton.icon(
              onPressed: () {
                setState(() {
                  if (_selectedColumns.length == widget.columns.length) {
                    _selectedColumns.clear();
                  } else {
                    _selectedColumns = List.from(widget.columns);
                  }
                  _clearMessages();
                });
              },
              icon: Icon(
                _selectedColumns.length == widget.columns.length
                    ? Icons.deselect
                    : Icons.select_all,
                size: 18,
              ),
              label: Text(
                _selectedColumns.length == widget.columns.length
                    ? 'Deselect All'
                    : 'Select All',
              ),
            ),
            const Spacer(),
            Chip(
              label: Text('${_selectedColumns.length} selected'),
              backgroundColor: Colors.blue.shade50,
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          'Leave empty to auto-detect all categorical columns',
          style: TextStyle(color: Colors.grey, fontSize: 12),
        ),
        const SizedBox(height: 12),
        if (widget.columns.isNotEmpty)
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(8),
            ),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: widget.columns.length,
              itemBuilder: (context, index) {
                final column = widget.columns[index];
                final isSelected = _selectedColumns.contains(column);

                return CheckboxListTile(
                  dense: true,
                  title: Text(column),
                  value: isSelected,
                  onChanged: (value) {
                    setState(() {
                      if (value == true) {
                        _selectedColumns.add(column);
                      } else {
                        _selectedColumns.remove(column);
                      }
                      _clearMessages();
                    });
                  },
                );
              },
            ),
          )
        else
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Center(
              child: Text(
                'No columns available. Please load data first.',
                style: TextStyle(color: Colors.grey),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildEncodingOptions() {
    if (_encodingType == 'label') {
      return CheckboxListTile(
        title: const Text('Save Encoding Mapping'),
        subtitle: const Text('Allow reverse transformation later'),
        value: _saveMapping,
        onChanged: (value) {
          setState(() {
            _saveMapping = value ?? true;
            _clearMessages();
          });
        },
      );
    } else if (_encodingType == 'onehot') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CheckboxListTile(
            title: const Text('Drop First Category'),
            subtitle: const Text(
                'Avoid multicollinearity (recommended for regression)'),
            value: _dropFirst,
            onChanged: (value) {
              setState(() {
                _dropFirst = value ?? false;
                _clearMessages();
              });
            },
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                const Text('Prefix Separator: '),
                const SizedBox(width: 12),
                SizedBox(
                  width: 100,
                  child: TextField(
                    controller: TextEditingController(text: _prefixSep),
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                    onChanged: (value) {
                      _prefixSep = value.isEmpty ? '_' : value;
                      _clearMessages();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                const Text(
                  'e.g., "Column_CategoryA"',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      );
    }
    return const SizedBox.shrink();
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        ElevatedButton.icon(
          onPressed:
              (widget.columns.isEmpty || _isLoading) ? null : _applyEncoding,
          icon: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                )
              : const Icon(Icons.play_arrow),
          label: Text(_isLoading ? 'Processing...' : 'Apply Encoding'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          ),
        ),
        const SizedBox(width: 12),
        OutlinedButton.icon(
          onPressed: _isLoading ? null : _clearSelection,
          icon: const Icon(Icons.clear),
          label: const Text('Clear Selection'),
        ),
        const Spacer(),
        IconButton(
          icon: const Icon(Icons.info_outline),
          tooltip: 'Encoding Information',
          onPressed: _showEncodingInfo,
        ),
      ],
    );
  }

  Widget _buildErrorMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        border: Border.all(color: Colors.red.shade200),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _errorMessage!,
              style: TextStyle(color: Colors.red.shade700),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: () {
              setState(() {
                _errorMessage = null;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        border: Border.all(color: Colors.green.shade200),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(Icons.check_circle_outline, color: Colors.green.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _successMessage!,
              style: TextStyle(color: Colors.green.shade700),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: () {
              setState(() {
                _successMessage = null;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildReport() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.analytics, color: Colors.blue.shade700),
              const SizedBox(width: 8),
              Text(
                'Encoding Report',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue.shade700,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const Divider(),
          ..._buildReportContent(),
        ],
      ),
    );
  }

  List<Widget> _buildReportContent() {
    final report = _lastReport!;
    List<Widget> widgets = [];

    if (report['columns_encoded'] != null) {
      widgets.add(_buildReportItem(
        'Columns Encoded',
        '${(report['columns_encoded'] as List).length}',
        Icons.table_chart,
      ));

      if ((report['columns_encoded'] as List).isNotEmpty) {
        widgets.add(const SizedBox(height: 8));
        widgets.add(Wrap(
          spacing: 8,
          runSpacing: 8,
          children: (report['columns_encoded'] as List).map((col) {
            return Chip(
              label: Text(col.toString()),
              backgroundColor: Colors.white,
            );
          }).toList(),
        ));
      }
    }

    if (report['new_columns_created'] != null) {
      widgets.add(const SizedBox(height: 12));
      widgets.add(_buildReportItem(
        'New Columns Created',
        '${(report['new_columns_created'] as List).length}',
        Icons.add_box,
      ));
    }

    if (report['total_encoded'] != null) {
      widgets.add(const SizedBox(height: 12));
      widgets.add(_buildReportItem(
        'Total Encoded',
        report['total_encoded'].toString(),
        Icons.done_all,
      ));
    }

    if (report['columns_decoded'] != null) {
      widgets.add(const SizedBox(height: 12));
      widgets.add(_buildReportItem(
        'Columns Decoded',
        '${(report['columns_decoded'] as List).length}',
        Icons.undo,
      ));
    }

    if (report['mappings'] != null && (report['mappings'] as Map).isNotEmpty) {
      widgets.add(const SizedBox(height: 12));
      widgets.add(const Text(
        'Encoding Mappings:',
        style: TextStyle(fontWeight: FontWeight.bold),
      ));
      widgets.add(const SizedBox(height: 8));

      final mappings = report['mappings'] as Map;
      for (var entry in mappings.entries) {
        widgets.add(ExpansionTile(
          title: Text(entry.key),
          children: [
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Table(
                border: TableBorder.all(color: Colors.grey.shade300),
                children: [
                  TableRow(
                    decoration: BoxDecoration(color: Colors.grey.shade200),
                    children: const [
                      Padding(
                        padding: EdgeInsets.all(8.0),
                        child: Text('Original',
                            style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                      Padding(
                        padding: EdgeInsets.all(8.0),
                        child: Text('Encoded',
                            style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                  ...(entry.value as Map).entries.map((mapEntry) {
                    return TableRow(
                      children: [
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Text(mapEntry.key.toString()),
                        ),
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Text(mapEntry.value.toString()),
                        ),
                      ],
                    );
                  }).toList(),
                ],
              ),
            ),
          ],
        ));
      }
    }

    return widgets;
  }

  Widget _buildReportItem(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.blue.shade700),
        const SizedBox(width: 8),
        Text('$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(value),
      ],
    );
  }

  void _clearMessages() {
    setState(() {
      _errorMessage = null;
      _successMessage = null;
    });
  }

  void _clearSelection() {
    setState(() {
      _selectedColumns.clear();
      _clearMessages();
      _lastReport = null;
    });
  }

  Future<void> _applyEncoding() async {
    _clearMessages();

    setState(() {
      _isLoading = true;
    });

    try {
      Map<String, dynamic> result;
      final columnsToEncode =
          _selectedColumns.isEmpty ? null : _selectedColumns;

      switch (_encodingType) {
        case 'label':
          result = await _apiService.labelEncode(
            columns: columnsToEncode,
            saveMapping: _saveMapping,
          );
          break;
        case 'onehot':
          result = await _apiService.oneHotEncode(
            columns: columnsToEncode,
            dropFirst: _dropFirst,
            prefixSep: _prefixSep,
          );
          break;
        case 'reverse':
          result = await _apiService.reverseLabelEncode(
            columns: columnsToEncode,
          );
          break;
        default:
          throw Exception('Unknown encoding type');
      }

      if (result['success'] == true) {
        setState(() {
          _successMessage =
              result['message'] ?? 'Encoding applied successfully';
          _lastReport = result['report'];
        });

        // Show success notification
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(_successMessage!),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 3),
            ),
          );
        }
      } else {
        setState(() {
          _errorMessage = 'Encoding failed';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showEncodingInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.info, color: Colors.blue),
            SizedBox(width: 12),
            Text('Encoding Information'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildInfoSection(
                'Label Encoding',
                'Converts categorical values to numeric labels (0, 1, 2, ...).',
                [
                  '✓ Simple and memory-efficient',
                  '✓ Works well with tree-based models',
                  '✓ Can be reversed if mapping is saved',
                  '✗ May imply ordinal relationship',
                ],
              ),
              const Divider(height: 24),
              _buildInfoSection(
                'One-Hot Encoding',
                'Creates binary columns for each category value.',
                [
                  '✓ No ordinal relationship assumed',
                  '✓ Works well with linear models',
                  '✓ Interpretable results',
                  '✗ Increases data dimensionality',
                  '✗ Can cause multicollinearity',
                ],
              ),
              const Divider(height: 24),
              _buildInfoSection(
                'Reverse Label Encoding',
                'Converts label-encoded data back to original categories.',
                [
                  '✓ Restores human-readable values',
                  '✓ Uses saved encoding mappings',
                  '⚠ Requires previous label encoding',
                ],
              ),
            ],
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

  Widget _buildInfoSection(
      String title, String description, List<String> points) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 8),
        Text(description, style: const TextStyle(color: Colors.grey)),
        const SizedBox(height: 12),
        ...points.map((point) => Padding(
              padding: const EdgeInsets.only(left: 16, bottom: 4),
              child: Text(point, style: const TextStyle(fontSize: 14)),
            )),
      ],
    );
  }
}
