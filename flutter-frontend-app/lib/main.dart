import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'models/migration_data.dart';
import 'screens/splash_screen.dart';
import 'screens/main_screen.dart';

void main() {
  runApp(const FastMigApp());
}

class FastMigApp extends StatelessWidget {
  const FastMigApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => MigrationData(),
      child: MaterialApp(
        title: 'FastMig - Data Migration',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
          scaffoldBackgroundColor: Colors.grey.shade50,
          cardTheme: CardThemeData(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        home: const SplashScreen(),
      ),
    );
  }
}
