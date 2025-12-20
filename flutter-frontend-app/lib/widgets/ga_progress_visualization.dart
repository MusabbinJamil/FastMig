import 'package:flutter/material.dart';
import '../models/ga_config_model.dart';

class GAProgressVisualization extends StatefulWidget {
  final List<GAMetricsModel> metricsHistory;
  final bool isRunning;
  final double? progressPercent;
  final VoidCallback? onStop;

  const GAProgressVisualization({
    Key? key,
    required this.metricsHistory,
    this.isRunning = false,
    this.progressPercent,
    this.onStop,
  }) : super(key: key);

  @override
  State<GAProgressVisualization> createState() =>
      _GAProgressVisualizationState();
}

class _GAProgressVisualizationState extends State<GAProgressVisualization>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
    if (widget.isRunning) {
      _animationController.repeat();
    }
  }

  @override
  void didUpdateWidget(GAProgressVisualization oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isRunning && !_animationController.isAnimating) {
      _animationController.repeat();
    } else if (!widget.isRunning && _animationController.isAnimating) {
      _animationController.stop();
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ===== Header with Status =====
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      widget.isRunning ? Icons.play_circle : Icons.pause_circle,
                      color: widget.isRunning ? Colors.green : Colors.orange,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'GA Progress',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ],
                ),
                if (widget.isRunning && widget.onStop != null)
                  IconButton(
                    icon: const Icon(Icons.stop_circle, color: Colors.red),
                    onPressed: widget.onStop,
                  ),
              ],
            ),
            const SizedBox(height: 16),

            // ===== Progress Bar =====
            if (widget.progressPercent != null)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Overall Progress'),
                      Text(
                          '${(widget.progressPercent! * 100).toStringAsFixed(1)}%'),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: widget.progressPercent,
                      minHeight: 8,
                      backgroundColor: Colors.grey[300],
                      valueColor: AlwaysStoppedAnimation<Color>(
                        widget.isRunning ? Colors.green : Colors.blue,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
              ),

            // ===== Metrics Grid =====
            if (widget.metricsHistory.isNotEmpty) ...[
              _buildMetricsGrid(),
              const SizedBox(height: 16),
            ],

            // ===== Generation-by-Generation Chart =====
            if (widget.metricsHistory.length > 1) ...[
              Text(
                'Fitness Progression',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 200,
                child: _buildFitnessChart(),
              ),
              const SizedBox(height: 16),
            ],

            // ===== Detailed Metrics Table =====
            if (widget.metricsHistory.isNotEmpty) ...[
              Text(
                'Recent Generations',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('Gen')),
                    DataColumn(label: Text('Best')),
                    DataColumn(label: Text('Worst')),
                    DataColumn(label: Text('Avg')),
                    DataColumn(label: Text('Variance')),
                  ],
                  rows: widget.metricsHistory.take(10).map((metric) {
                    return DataRow(cells: [
                      DataCell(Text('${metric.generation}')),
                      DataCell(Text(metric.bestFitness.toStringAsFixed(2))),
                      DataCell(Text(metric.worstFitness.toStringAsFixed(2))),
                      DataCell(Text(metric.averageFitness.toStringAsFixed(2))),
                      DataCell(Text(metric.fitnessVariance.toStringAsFixed(4))),
                    ]);
                  }).toList(),
                ),
              ),
            ] else
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24.0),
                  child: Text(
                    'No metrics available yet',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricsGrid() {
    final latest = widget.metricsHistory.last;
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 2,
      children: [
        _buildMetricCard(
          'Generation',
          '${latest.generation}',
          Icons.repeat,
          Colors.blue,
        ),
        _buildMetricCard(
          'Best Fitness',
          latest.bestFitness.toStringAsFixed(2),
          Icons.trending_up,
          Colors.green,
        ),
        _buildMetricCard(
          'Avg Fitness',
          latest.averageFitness.toStringAsFixed(2),
          Icons.equalizer,
          Colors.orange,
        ),
        _buildMetricCard(
          'Population',
          '${latest.populationSize}',
          Icons.people,
          Colors.purple,
        ),
      ],
    );
  }

  Widget _buildMetricCard(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      margin: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        border: Border.all(color: color.withOpacity(0.3)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 4),
            Text(
              value,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFitnessChart() {
    if (widget.metricsHistory.isEmpty) {
      return const Center(child: Text('No data'));
    }

    final metrics = widget.metricsHistory;
    final maxFitness =
        metrics.map((m) => m.bestFitness).reduce((a, b) => a > b ? a : b);
    final minFitness =
        metrics.map((m) => m.worstFitness).reduce((a, b) => a < b ? a : b);
    final range = maxFitness - minFitness;
    final normalizedRange = range > 0 ? range : 1.0;

    return CustomPaint(
      painter: FitnessChartPainter(
        metrics: metrics,
        minFitness: minFitness,
        maxFitness: maxFitness,
        normalizedRange: normalizedRange,
      ),
      size: Size.infinite,
    );
  }
}

/// Custom painter for fitness progression chart
class FitnessChartPainter extends CustomPainter {
  final List<GAMetricsModel> metrics;
  final double minFitness;
  final double maxFitness;
  final double normalizedRange;

  FitnessChartPainter({
    required this.metrics,
    required this.minFitness,
    required this.maxFitness,
    required this.normalizedRange,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (metrics.isEmpty) return;

    final paint = Paint()
      ..color = Colors.blue
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final avgPaint = Paint()
      ..color = Colors.orange
      ..strokeWidth = 1.5;

    final padding = 40.0;
    final graphWidth = size.width - (padding * 2);
    final graphHeight = size.height - (padding * 2);
    final stepX = graphWidth / (metrics.length - 1).clamp(1, double.infinity);

    // Draw axes
    canvas.drawLine(
      Offset(padding, size.height - padding),
      Offset(size.width - padding, size.height - padding),
      paint..color = Colors.grey,
    );
    canvas.drawLine(
      Offset(padding, padding),
      Offset(padding, size.height - padding),
      paint..color = Colors.grey,
    );

    // Draw best fitness line
    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height -
          padding -
          ((metrics[i].bestFitness - minFitness) / normalizedRange) *
              graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height -
          padding -
          ((metrics[i + 1].bestFitness - minFitness) / normalizedRange) *
              graphHeight;

      canvas.drawLine(
          Offset(x1, y1), Offset(x2, y2), paint..color = Colors.green);
    }

    // Draw average fitness line
    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height -
          padding -
          ((metrics[i].averageFitness - minFitness) / normalizedRange) *
              graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height -
          padding -
          ((metrics[i + 1].averageFitness - minFitness) / normalizedRange) *
              graphHeight;

      canvas.drawLine(Offset(x1, y1), Offset(x2, y2), avgPaint);
    }
  }

  @override
  bool shouldRepaint(FitnessChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}
