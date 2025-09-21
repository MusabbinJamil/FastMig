import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/data_migration_screen.dart';
import 'models/migration_data.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => MigrationData(),
      child: const FastMigApp(),
    ),
  );
}

class FastMigApp extends StatelessWidget {
  const FastMigApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FastMig',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const DataMigrationScreen(),
    );
  }
}
