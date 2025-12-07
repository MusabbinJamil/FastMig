import 'package:flutter/material.dart';

class SensitiveDataWarning extends StatelessWidget {
  final Map<String, dynamic> sensitiveColumns;
  final VoidCallback? onDismiss;
  final bool isExpanded;

  const SensitiveDataWarning({
    Key? key,
    required this.sensitiveColumns,
    this.onDismiss,
    this.isExpanded = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (sensitiveColumns.isEmpty) {
      return const SizedBox.shrink();
    }

    final highSeverityCount = sensitiveColumns.values
        .where((col) => col['severity'] == 'high')
        .length;
    final mediumSeverityCount = sensitiveColumns.values
        .where((col) => col['severity'] == 'medium')
        .length;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.red.shade300,
          width: 2,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(
                  Icons.warning_rounded,
                  color: Colors.red.shade700,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '⚠️ Sensitive Data Detected',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.red.shade900,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'This data imputation may be false or flawed',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.red.shade700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Summary
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Found ${sensitiveColumns.length} sensitive column(s):',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Colors.red.shade800,
                    ),
                  ),
                  if (highSeverityCount > 0) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(Icons.error, size: 16, color: Colors.red.shade700),
                        const SizedBox(width: 6),
                        Text(
                          'High severity: $highSeverityCount',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.red.shade700,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ],
                  if (mediumSeverityCount > 0) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.warning,
                            size: 16, color: Colors.orange.shade700),
                        const SizedBox(width: 6),
                        Text(
                          'Medium severity: $mediumSeverityCount',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.orange.shade700,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 12),
            // Sensitive columns list
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: sensitiveColumns.entries.map((entry) {
                final colName = entry.key;
                final colData = entry.value;
                final severity = colData['severity'] ?? 'medium';
                final reason = colData['reason'] ?? '';
                final recommendation = colData['recommendation'] ?? '';
                final hasMissing = colData['has_missing'] ?? 0;
                final missingPct = colData['total_missing_pct'] ?? 0;

                final bgColor = severity == 'high'
                    ? Colors.red.shade100
                    : Colors.orange.shade100;
                final borderColor = severity == 'high'
                    ? Colors.red.shade300
                    : Colors.orange.shade300;
                final iconColor = severity == 'high'
                    ? Colors.red.shade700
                    : Colors.orange.shade700;

                return Container(
                  margin: const EdgeInsets.only(top: 8),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: bgColor,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: borderColor),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.lock, size: 18, color: iconColor),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              colName,
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: iconColor,
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: severity == 'high'
                                  ? Colors.red.shade700
                                  : Colors.orange.shade700,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              severity.toUpperCase(),
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        reason,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade800,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Text(
                            '📋 ',
                            style: TextStyle(
                                fontSize: 12, color: Colors.grey.shade700),
                          ),
                          Expanded(
                            child: Text(
                              recommendation,
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade700,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ),
                        ],
                      ),
                      if (hasMissing > 0) ...[
                        const SizedBox(height: 6),
                        Text(
                          '🔴 Missing values: $hasMissing ($missingPct%)',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.red.shade700,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ],
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 12),
            // Warning message
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.orange.shade50,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: Colors.orange.shade200),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.info_outline,
                    color: Colors.orange.shade700,
                    size: 20,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'AI imputation may create false or invalid values for these columns. '
                      'Consider: 1) Manually verifying imputed values, 2) Excluding these columns from cleaning, '
                      '3) Obtaining original data from source documents.',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.orange.shade800,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (onDismiss != null) ...[
              const SizedBox(height: 12),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: onDismiss,
                  child: const Text('Dismiss'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
