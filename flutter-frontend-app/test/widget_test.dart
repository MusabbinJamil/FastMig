import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_frontend_app/main.dart';
import 'package:flutter_frontend_app/screens/data_migration_screen.dart';

void main() {
  testWidgets('FastMig app renders correctly', (WidgetTester tester) async {
    await tester.pumpWidget(const FastMigApp());

    expect(find.text('FastMig'), findsOneWidget);
    expect(find.byType(DataMigrationScreen), findsOneWidget);
    expect(find.text('Load Data'), findsOneWidget);
    expect(find.text('No file selected'), findsOneWidget);
  });

  testWidgets('Load Data section works correctly', (WidgetTester tester) async {
    await tester.pumpWidget(const FastMigApp());

    expect(find.text('Select File'), findsOneWidget);
    expect(find.text('No file selected'), findsOneWidget);
  });
}
