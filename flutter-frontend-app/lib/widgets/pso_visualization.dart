import 'package:flutter/material.dart';

/// Data model for PSO iteration metrics
class PSOMetrics {
  final int iteration;
  final double globalBestFitness;
  final double averageFitness;
  final double worstFitness;
  final double averageVelocity;
  final double swarmDiversity;
  final int swarmSize;

  PSOMetrics({
    required this.iteration,
    required this.globalBestFitness,
    required this.averageFitness,
    required this.worstFitness,
    this.averageVelocity = 0.0,
    this.swarmDiversity = 0.0,
    this.swarmSize = 30,
  });

  factory PSOMetrics.fromJson(Map<String, dynamic> json) {
    return PSOMetrics(
      iteration: json['iteration'] ?? json['generation'] ?? 0,
      globalBestFitness: (json['global_best_fitness'] ?? json['best_fitness'] ?? 0.0).toDouble(),
      averageFitness: (json['average_fitness'] ?? 0.0).toDouble(),
      worstFitness: (json['worst_fitness'] ?? 0.0).toDouble(),
      averageVelocity: (json['average_velocity'] ?? json['avg_velocity'] ?? 0.0).toDouble(),
      swarmDiversity: (json['swarm_diversity'] ?? json['population_diversity'] ?? 0.0).toDouble(),
      swarmSize: json['swarm_size'] ?? json['population_size'] ?? 30,
    );
  }
}

/// PSO Progress Visualization Widget
/// Shows global best convergence, mean fitness, velocity, and diversity charts
class PSOVisualization extends StatefulWidget {
  final List<PSOMetrics> metricsHistory;
  final bool isRunning;
  final double? progressPercent;
  final VoidCallback? onStop;
  final String? topologyType;
  final String? variant;

  const PSOVisualization({
    Key? key,
    required this.metricsHistory,
    this.isRunning = false,
    this.progressPercent,
    this.onStop,
    this.topologyType,
    this.variant,
  }) : super(key: key);

  @override
  State<PSOVisualization> createState() => _PSOVisualizationState();
}

class _PSOVisualizationState extends State<PSOVisualization>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  String _selectedChart = 'fitness'; // fitness, velocity, diversity

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
  void didUpdateWidget(PSOVisualization oldWidget) {
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
            // Header with Status
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.scatter_plot,
                      color: widget.isRunning ? Colors.blue : Colors.blue.shade300,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'PSO Progress',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    if (widget.topologyType != null) ...[
                      const SizedBox(width: 8),
                      Chip(
                        label: Text(
                          widget.topologyType!.toUpperCase(),
                          style: const TextStyle(fontSize: 10),
                        ),
                        backgroundColor: Colors.blue.shade100,
                        padding: EdgeInsets.zero,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                    ],
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

            // Progress Bar
            if (widget.progressPercent != null)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Swarm Progress'),
                      Text('${(widget.progressPercent! * 100).toStringAsFixed(1)}%'),
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
                        widget.isRunning ? Colors.blue : Colors.blue.shade300,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
              ),

            // Metrics Grid
            if (widget.metricsHistory.isNotEmpty) ...[
              _buildMetricsGrid(),
              const SizedBox(height: 16),
            ],

            // Chart Type Selector
            if (widget.metricsHistory.length > 1) ...[
              _buildChartSelector(),
              const SizedBox(height: 12),
              SizedBox(
                height: 200,
                child: _buildSelectedChart(),
              ),
              const SizedBox(height: 16),
            ],

            // Recent Iterations Table
            if (widget.metricsHistory.isNotEmpty) ...[
              Text(
                'Recent Iterations',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('Iter')),
                    DataColumn(label: Text('GBest')),
                    DataColumn(label: Text('Avg')),
                    DataColumn(label: Text('Velocity')),
                    DataColumn(label: Text('Diversity')),
                  ],
                  rows: widget.metricsHistory.reversed.take(10).map((metric) {
                    return DataRow(cells: [
                      DataCell(Text('${metric.iteration}')),
                      DataCell(Text(metric.globalBestFitness.toStringAsFixed(3))),
                      DataCell(Text(metric.averageFitness.toStringAsFixed(3))),
                      DataCell(Text(metric.averageVelocity.toStringAsFixed(4))),
                      DataCell(Text(metric.swarmDiversity.toStringAsFixed(4))),
                    ]);
                  }).toList(),
                ),
              ),
            ] else
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24.0),
                  child: Text(
                    'No PSO metrics available yet',
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
    final improvement = widget.metricsHistory.length > 1
        ? latest.globalBestFitness - widget.metricsHistory.first.globalBestFitness
        : 0.0;

    return GridView.count(
      crossAxisCount: 4,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.5,
      crossAxisSpacing: 8,
      mainAxisSpacing: 8,
      children: [
        _buildMetricCard(
          'Iteration',
          '${latest.iteration}',
          Icons.repeat,
          Colors.blue,
        ),
        _buildMetricCard(
          'Global Best',
          latest.globalBestFitness.toStringAsFixed(3),
          Icons.emoji_events,
          Colors.amber,
        ),
        _buildMetricCard(
          'Avg Fitness',
          latest.averageFitness.toStringAsFixed(3),
          Icons.equalizer,
          Colors.green,
        ),
        _buildMetricCard(
          'Improvement',
          '${improvement >= 0 ? '+' : ''}${(improvement * 100).toStringAsFixed(2)}%',
          improvement >= 0 ? Icons.trending_up : Icons.trending_down,
          improvement >= 0 ? Colors.green : Colors.red,
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
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
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
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: color.withOpacity(0.8),
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

  Widget _buildChartSelector() {
    return Row(
      children: [
        Text(
          'Chart View:',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(width: 16),
        _buildChartToggle('Fitness', 'fitness', Icons.trending_up, Colors.green),
        const SizedBox(width: 8),
        _buildChartToggle('Velocity', 'velocity', Icons.speed, Colors.blue),
        const SizedBox(width: 8),
        _buildChartToggle('Diversity', 'diversity', Icons.scatter_plot, Colors.purple),
      ],
    );
  }

  Widget _buildChartToggle(String label, String value, IconData icon, Color color) {
    final isSelected = _selectedChart == value;
    return InkWell(
      onTap: () => setState(() => _selectedChart = value),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.2) : Colors.transparent,
          border: Border.all(
            color: isSelected ? color : Colors.grey.shade300,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: isSelected ? color : Colors.grey),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: isSelected ? color : Colors.grey,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectedChart() {
    switch (_selectedChart) {
      case 'velocity':
        return _buildVelocityChart();
      case 'diversity':
        return _buildDiversityChart();
      default:
        return _buildFitnessChart();
    }
  }

  Widget _buildFitnessChart() {
    if (widget.metricsHistory.isEmpty) {
      return const Center(child: Text('No data'));
    }

    final metrics = widget.metricsHistory;
    final maxFitness = metrics.map((m) => m.globalBestFitness).reduce((a, b) => a > b ? a : b);
    final minFitness = metrics.map((m) => m.worstFitness).reduce((a, b) => a < b ? a : b);

    return CustomPaint(
      painter: PSOFitnessChartPainter(
        metrics: metrics,
        minFitness: minFitness,
        maxFitness: maxFitness,
      ),
      size: Size.infinite,
    );
  }

  Widget _buildVelocityChart() {
    if (widget.metricsHistory.isEmpty) {
      return const Center(child: Text('No data'));
    }

    final metrics = widget.metricsHistory;
    final maxVelocity = metrics.map((m) => m.averageVelocity).reduce((a, b) => a > b ? a : b);

    return CustomPaint(
      painter: PSOVelocityChartPainter(
        metrics: metrics,
        maxVelocity: maxVelocity > 0 ? maxVelocity : 1.0,
      ),
      size: Size.infinite,
    );
  }

  Widget _buildDiversityChart() {
    if (widget.metricsHistory.isEmpty) {
      return const Center(child: Text('No data'));
    }

    final metrics = widget.metricsHistory;
    final maxDiversity = metrics.map((m) => m.swarmDiversity).reduce((a, b) => a > b ? a : b);

    return CustomPaint(
      painter: PSODiversityChartPainter(
        metrics: metrics,
        maxDiversity: maxDiversity > 0 ? maxDiversity : 1.0,
      ),
      size: Size.infinite,
    );
  }
}

/// Custom painter for PSO fitness progression chart
class PSOFitnessChartPainter extends CustomPainter {
  final List<PSOMetrics> metrics;
  final double minFitness;
  final double maxFitness;

  PSOFitnessChartPainter({
    required this.metrics,
    required this.minFitness,
    required this.maxFitness,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (metrics.isEmpty) return;

    final range = (maxFitness - minFitness).clamp(0.001, double.infinity);
    final padding = 40.0;
    final graphWidth = size.width - (padding * 2);
    final graphHeight = size.height - (padding * 2);
    final stepX = graphWidth / (metrics.length - 1).clamp(1, double.infinity);

    final axisPaint = Paint()
      ..color = Colors.grey.shade400
      ..strokeWidth = 1;

    // Draw axes
    canvas.drawLine(
      Offset(padding, size.height - padding),
      Offset(size.width - padding, size.height - padding),
      axisPaint,
    );
    canvas.drawLine(
      Offset(padding, padding),
      Offset(padding, size.height - padding),
      axisPaint,
    );

    // Draw global best line (gold/amber)
    final gbestPaint = Paint()
      ..color = Colors.amber
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;

    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height - padding -
          ((metrics[i].globalBestFitness - minFitness) / range) * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding -
          ((metrics[i + 1].globalBestFitness - minFitness) / range) * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), gbestPaint);
    }

    // Draw average fitness line (green)
    final avgPaint = Paint()
      ..color = Colors.green
      ..strokeWidth = 1.5;

    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height - padding -
          ((metrics[i].averageFitness - minFitness) / range) * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding -
          ((metrics[i + 1].averageFitness - minFitness) / range) * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), avgPaint);
    }

    // Draw legend
    _drawLegend(canvas, size, padding);
  }

  void _drawLegend(Canvas canvas, Size size, double padding) {
    final textPainter = TextPainter(textDirection: TextDirection.ltr);

    // Global Best legend
    canvas.drawLine(
      Offset(size.width - 120, padding),
      Offset(size.width - 100, padding),
      Paint()..color = Colors.amber..strokeWidth = 2,
    );
    textPainter.text = const TextSpan(
      text: 'Global Best',
      style: TextStyle(color: Colors.amber, fontSize: 10),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 95, padding - 5));

    // Average legend
    canvas.drawLine(
      Offset(size.width - 120, padding + 15),
      Offset(size.width - 100, padding + 15),
      Paint()..color = Colors.green..strokeWidth = 1.5,
    );
    textPainter.text = const TextSpan(
      text: 'Average',
      style: TextStyle(color: Colors.green, fontSize: 10),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 95, padding + 10));
  }

  @override
  bool shouldRepaint(PSOFitnessChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}

/// Custom painter for PSO velocity chart
class PSOVelocityChartPainter extends CustomPainter {
  final List<PSOMetrics> metrics;
  final double maxVelocity;

  PSOVelocityChartPainter({
    required this.metrics,
    required this.maxVelocity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (metrics.isEmpty) return;

    final padding = 40.0;
    final graphWidth = size.width - (padding * 2);
    final graphHeight = size.height - (padding * 2);
    final stepX = graphWidth / (metrics.length - 1).clamp(1, double.infinity);

    final axisPaint = Paint()
      ..color = Colors.grey.shade400
      ..strokeWidth = 1;

    // Draw axes
    canvas.drawLine(
      Offset(padding, size.height - padding),
      Offset(size.width - padding, size.height - padding),
      axisPaint,
    );
    canvas.drawLine(
      Offset(padding, padding),
      Offset(padding, size.height - padding),
      axisPaint,
    );

    // Draw velocity line (blue)
    final velocityPaint = Paint()
      ..color = Colors.blue
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;

    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height - padding -
          (metrics[i].averageVelocity / maxVelocity) * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding -
          (metrics[i + 1].averageVelocity / maxVelocity) * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), velocityPaint);
    }

    // Draw label
    final textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = const TextSpan(
      text: 'Avg Velocity',
      style: TextStyle(color: Colors.blue, fontSize: 11, fontWeight: FontWeight.bold),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 90, padding));
  }

  @override
  bool shouldRepaint(PSOVelocityChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}

/// Custom painter for PSO diversity chart
class PSODiversityChartPainter extends CustomPainter {
  final List<PSOMetrics> metrics;
  final double maxDiversity;

  PSODiversityChartPainter({
    required this.metrics,
    required this.maxDiversity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (metrics.isEmpty) return;

    final padding = 40.0;
    final graphWidth = size.width - (padding * 2);
    final graphHeight = size.height - (padding * 2);
    final stepX = graphWidth / (metrics.length - 1).clamp(1, double.infinity);

    final axisPaint = Paint()
      ..color = Colors.grey.shade400
      ..strokeWidth = 1;

    // Draw axes
    canvas.drawLine(
      Offset(padding, size.height - padding),
      Offset(size.width - padding, size.height - padding),
      axisPaint,
    );
    canvas.drawLine(
      Offset(padding, padding),
      Offset(padding, size.height - padding),
      axisPaint,
    );

    // Draw diversity line (purple)
    final diversityPaint = Paint()
      ..color = Colors.purple
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;

    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height - padding -
          (metrics[i].swarmDiversity / maxDiversity) * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding -
          (metrics[i + 1].swarmDiversity / maxDiversity) * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), diversityPaint);
    }

    // Draw label
    final textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = const TextSpan(
      text: 'Swarm Diversity',
      style: TextStyle(color: Colors.purple, fontSize: 11, fontWeight: FontWeight.bold),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 105, padding));
  }

  @override
  bool shouldRepaint(PSODiversityChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}
