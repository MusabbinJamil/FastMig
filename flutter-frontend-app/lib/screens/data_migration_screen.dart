import 'package:flutter/material.dart';
import '../widgets/load_data_section.dart';
import '../widgets/process_data_section.dart';
import '../widgets/data_table_section.dart';

class DataMigrationScreen extends StatefulWidget {
  const DataMigrationScreen({Key? key}) : super(key: key);

  @override
  _DataMigrationScreenState createState() => _DataMigrationScreenState();
}

class _DataMigrationScreenState extends State<DataMigrationScreen> {
  // State variables
  String? selectedColumn;
  String? selectedDataType;
  List<List<dynamic>>? tableData;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('FastMig')),
      body: const Column(
        children: [
          Expanded(
            flex: 1,
            child: Row(
              children: [
                Expanded(child: LoadDataSection()),
                Expanded(child: ProcessDataSection()),
              ],
            ),
          ),
          Expanded(
            flex: 2,
            child: DataTableSection(),
          ),
        ],
      ),
    );
  }
}
