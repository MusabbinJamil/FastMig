import 'package:flutter/material.dart';

/// Data model for DE generation metrics
class DEMetrics {
  final int generation;
  final double bestFitness;
  final double averageFitness;
  final double worstFitness;
  final double populationDiversity;
  final double successRate;
  final double currentF;
  final double currentCR;
  final int populationSize;

  DEMetrics({
    required this.generation,
    required this.bestFitness,
    required this.averageFitness,
    required this.worstFitness,
    this.populationDiversity = 0.0,
    this.successRate = 0.0,
    this.currentF = 0.8,
    this.currentCR = 0.9,
    this.populationSize = 30,
  });

  factory DEMetrics.fromJson(Map<String, dynamic> json) {
    return DEMetrics(
      generation: json['generation'] ?? 0,
      bestFitness: (json['best_fitness'] ?? 0.0).toDouble(),
      averageFitness: (json['average_fitness'] ?? 0.0).toDouble(),
      worstFitness: (json['worst_fitness'] ?? 0.0).toDouble(),
      populationDiversity: (json['population_diversity'] ?? 0.0).toDouble(),
      successRate: (json['success_rate'] ?? 0.0).toDouble(),
      currentF: (json['current_f'] ?? 0.8).toDouble(),
      currentCR: (json['current_cr'] ?? 0.9).toDouble(),
      populationSize: json['population_size'] ?? 30,
    );
  }
}

/// DE Progress Visualization Widget
/// Shows fitness convergence, success rate, F/CR values, and diversity charts
class DEVisualization extends StatefulWidget {
  final List<DEMetrics> metricsHistory;
  final bool isRunning;
  final double? progressPercent;
  final VoidCallback? onStop;
  final String? mutationStrategy;
  final bool adaptiveF;
  final bool adaptiveCR;

  const DEVisualization({
    Key? key,
    required this.metricsHistory,
    this.isRunning = false,
    this.progressPercent,
    this.onStop,
    this.mutationStrategy,
    this.adaptiveF = false,
    this.adaptiveCR = false,
  }) : super(key: key);

  @override
  State<DEVisualization> createState() => _DEVisualizationState();
}

class _DEVisualizationState extends State<DEVisualization>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  String _selectedChart = 'fitness'; // fitness, success, parameters, diversity

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
  void didUpdateWidget(DEVisualization oldWidget) {
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
                      Icons.functions,
                      color: widget.isRunning ? Colors.orange : Colors.orange.shade300,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'DE Progress',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    if (widget.mutationStrategy != null) ...[
                      const SizedBox(width: 8),
                      Chip(
                        label: Text(
                          widget.mutationStrategy!,
                          style: const TextStyle(fontSize: 9),
                        ),
                        backgroundColor: Colors.orange.shade100,
                        padding: EdgeInsets.zero,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                    ],
                    if (widget.adaptiveF || widget.adaptiveCR) ...[
                      const SizedBox(width: 4),
                      Chip(
                        label: Text(
                          'Adaptive${widget.adaptiveF && widget.adaptiveCR ? ' F+CR' : widget.adaptiveF ? ' F' : ' CR'}',
                          style: const TextStyle(fontSize: 9),
                        ),
                        backgroundColor: Colors.green.shade100,
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
                      const Text('Evolution Progress'),
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
                        widget.isRunning ? Colors.orange : Colors.orange.shade300,
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

            // Recent Generations Table
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
                    DataColumn(label: Text('Avg')),
                    DataColumn(label: Text('Success')),
                    DataColumn(label: Text('F')),
                    DataColumn(label: Text('CR')),
                  ],
                  rows: widget.metricsHistory.reversed.take(10).map((metric) {
                    return DataRow(cells: [
                      DataCell(Text('${metric.generation}')),
                      DataCell(Text(metric.bestFitness.toStringAsFixed(3))),
                      DataCell(Text(metric.averageFitness.toStringAsFixed(3))),
                      DataCell(Text('${(metric.successRate * 100).toStringAsFixed(1)}%')),
                      DataCell(Text(metric.currentF.toStringAsFixed(2))),
                      DataCell(Text(metric.currentCR.toStringAsFixed(2))),
                    ]);
                  }).toList(),
                ),
              ),
            ] else
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24.0),
                  child: Text(
                    'No DE metrics available yet',
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
        ? latest.bestFitness - widget.metricsHistory.first.bestFitness
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
          'Generation',
          '${latest.generation}',
          Icons.repeat,
          Colors.orange,
        ),
        _buildMetricCard(
          'Best Fitness',
          latest.bestFitness.toStringAsFixed(3),
          Icons.emoji_events,
          Colors.amber,
        ),
        _buildMetricCard(
          'Success Rate',
          '${(latest.successRate * 100).toStringAsFixed(1)}%',
          Icons.check_circle,
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
        _buildChartToggle('Success', 'success', Icons.check_circle, Colors.blue),
        const SizedBox(width: 8),
        if (widget.adaptiveF || widget.adaptiveCR)
          _buildChartToggle('F/CR', 'parameters', Icons.tune, Colors.orange),
        if (widget.adaptiveF || widget.adaptiveCR) const SizedBox(width: 8),
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
      case 'success':
        return _buildSuccessRateChart();
      case 'parameters':
        return _buildParametersChart();
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
    final maxFitness = metrics.map((m) => m.bestFitness).reduce((a, b) => a > b ? a : b);
    final minFitness = metrics.map((m) => m.worstFitness).reduce((a, b) => a < b ? a : b);

    return CustomPaint(
      painter: DEFitnessChartPainter(
        metrics: metrics,
        minFitness: minFitness,
        maxFitness: maxFitness,
      ),
      size: Size.infinite,
    );
  }

  Widget _buildSuccessRateChart() {
    if (widget.metricsHistory.isEmpty) {
      return const Center(child: Text('No data'));
    }

    return CustomPaint(
      painter: DESuccessRateChartPainter(metrics: widget.metricsHistory),
      size: Size.infinite,
    );
  }

  Widget _buildParametersChart() {
    if (widget.metricsHistory.isEmpty) {
      return const Center(child: Text('No data'));
    }

    return CustomPaint(
      painter: DEParametersChartPainter(
        metrics: widget.metricsHistory,
        showF: widget.adaptiveF,
        showCR: widget.adaptiveCR,
      ),
      size: Size.infinite,
    );
  }

  Widget _buildDiversityChart() {
    if (widget.metricsHistory.isEmpty) {
      return const Center(child: Text('No data'));
    }

    final metrics = widget.metricsHistory;
    final maxDiversity = metrics.map((m) => m.populationDiversity).reduce((a, b) => a > b ? a : b);

    return CustomPaint(
      painter: DEDiversityChartPainter(
        metrics: metrics,
        maxDiversity: maxDiversity > 0 ? maxDiversity : 1.0,
      ),
      size: Size.infinite,
    );
  }
}

/// Custom painter for DE fitness progression chart
class DEFitnessChartPainter extends CustomPainter {
  final List<DEMetrics> metrics;
  final double minFitness;
  final double maxFitness;

  DEFitnessChartPainter({
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

    // Draw best fitness line (orange)
    final bestPaint = Paint()
      ..color = Colors.orange
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;

    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height - padding -
          ((metrics[i].bestFitness - minFitness) / range) * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding -
          ((metrics[i + 1].bestFitness - minFitness) / range) * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), bestPaint);
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

    // Draw worst fitness line (red, dashed)
    final worstPaint = Paint()
      ..color = Colors.red.withOpacity(0.5)
      ..strokeWidth = 1;

    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height - padding -
          ((metrics[i].worstFitness - minFitness) / range) * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding -
          ((metrics[i + 1].worstFitness - minFitness) / range) * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), worstPaint);
    }

    // Draw legend
    _drawLegend(canvas, size, padding);
  }

  void _drawLegend(Canvas canvas, Size size, double padding) {
    final textPainter = TextPainter(textDirection: TextDirection.ltr);

    // Best legend
    canvas.drawLine(
      Offset(size.width - 100, padding),
      Offset(size.width - 80, padding),
      Paint()..color = Colors.orange..strokeWidth = 2.5,
    );
    textPainter.text = const TextSpan(
      text: 'Best',
      style: TextStyle(color: Colors.orange, fontSize: 10),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 75, padding - 5));

    // Average legend
    canvas.drawLine(
      Offset(size.width - 100, padding + 15),
      Offset(size.width - 80, padding + 15),
      Paint()..color = Colors.green..strokeWidth = 1.5,
    );
    textPainter.text = const TextSpan(
      text: 'Avg',
      style: TextStyle(color: Colors.green, fontSize: 10),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 75, padding + 10));

    // Worst legend
    canvas.drawLine(
      Offset(size.width - 100, padding + 30),
      Offset(size.width - 80, padding + 30),
      Paint()..color = Colors.red.withOpacity(0.5)..strokeWidth = 1,
    );
    textPainter.text = TextSpan(
      text: 'Worst',
      style: TextStyle(color: Colors.red.withOpacity(0.7), fontSize: 10),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 75, padding + 25));
  }

  @override
  bool shouldRepaint(DEFitnessChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}

/// Custom painter for DE success rate chart
class DESuccessRateChartPainter extends CustomPainter {
  final List<DEMetrics> metrics;

  DESuccessRateChartPainter({required this.metrics});

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

    // Draw success rate line (blue)
    final successPaint = Paint()
      ..color = Colors.blue
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;

    for (int i = 0; i < metrics.length - 1; i++) {
      final x1 = padding + (i * stepX);
      final y1 = size.height - padding - metrics[i].successRate * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding - metrics[i + 1].successRate * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), successPaint);
    }

    // Draw 50% reference line
    final refY = size.height - padding - 0.5 * graphHeight;
    canvas.drawLine(
      Offset(padding, refY),
      Offset(size.width - padding, refY),
      Paint()
        ..color = Colors.grey.shade300
        ..strokeWidth = 1
        ..style = PaintingStyle.stroke,
    );

    // Draw label
    final textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = const TextSpan(
      text: 'Success Rate (%)',
      style: TextStyle(color: Colors.blue, fontSize: 11, fontWeight: FontWeight.bold),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 110, padding));
  }

  @override
  bool shouldRepaint(DESuccessRateChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}

/// Custom painter for DE adaptive parameters chart (F and CR)
class DEParametersChartPainter extends CustomPainter {
  final List<DEMetrics> metrics;
  final bool showF;
  final bool showCR;

  DEParametersChartPainter({
    required this.metrics,
    this.showF = true,
    this.showCR = true,
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

    // Draw axes (scale 0-2 for F, 0-1 for CR, so use max 2)
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

    // Draw F line (orange)
    if (showF) {
      final fPaint = Paint()
        ..color = Colors.orange
        ..strokeWidth = 2
        ..strokeCap = StrokeCap.round;

      for (int i = 0; i < metrics.length - 1; i++) {
        final x1 = padding + (i * stepX);
        final y1 = size.height - padding - (metrics[i].currentF / 2.0) * graphHeight;
        final x2 = padding + ((i + 1) * stepX);
        final y2 = size.height - padding - (metrics[i + 1].currentF / 2.0) * graphHeight;
        canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                        Offset(x2, y2.clamp(padding, size.height - padding)), fPaint);
      }
    }

    // Draw CR line (purple)
    if (showCR) {
      final crPaint = Paint()
        ..color = Colors.purple
        ..strokeWidth = 2
        ..strokeCap = StrokeCap.round;

      for (int i = 0; i < metrics.length - 1; i++) {
        final x1 = padding + (i * stepX);
        final y1 = size.height - padding - (metrics[i].currentCR / 2.0) * graphHeight;
        final x2 = padding + ((i + 1) * stepX);
        final y2 = size.height - padding - (metrics[i + 1].currentCR / 2.0) * graphHeight;
        canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                        Offset(x2, y2.clamp(padding, size.height - padding)), crPaint);
      }
    }

    // Draw legend
    final textPainter = TextPainter(textDirection: TextDirection.ltr);
    double legendY = padding;

    if (showF) {
      canvas.drawLine(
        Offset(size.width - 80, legendY),
        Offset(size.width - 60, legendY),
        Paint()..color = Colors.orange..strokeWidth = 2,
      );
      textPainter.text = const TextSpan(
        text: 'F',
        style: TextStyle(color: Colors.orange, fontSize: 10),
      );
      textPainter.layout();
      textPainter.paint(canvas, Offset(size.width - 55, legendY - 5));
      legendY += 15;
    }

    if (showCR) {
      canvas.drawLine(
        Offset(size.width - 80, legendY),
        Offset(size.width - 60, legendY),
        Paint()..color = Colors.purple..strokeWidth = 2,
      );
      textPainter.text = const TextSpan(
        text: 'CR',
        style: TextStyle(color: Colors.purple, fontSize: 10),
      );
      textPainter.layout();
      textPainter.paint(canvas, Offset(size.width - 55, legendY - 5));
    }
  }

  @override
  bool shouldRepaint(DEParametersChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}

/// Custom painter for DE diversity chart
class DEDiversityChartPainter extends CustomPainter {
  final List<DEMetrics> metrics;
  final double maxDiversity;

  DEDiversityChartPainter({
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
          (metrics[i].populationDiversity / maxDiversity) * graphHeight;
      final x2 = padding + ((i + 1) * stepX);
      final y2 = size.height - padding -
          (metrics[i + 1].populationDiversity / maxDiversity) * graphHeight;
      canvas.drawLine(Offset(x1, y1.clamp(padding, size.height - padding)),
                      Offset(x2, y2.clamp(padding, size.height - padding)), diversityPaint);
    }

    // Draw label
    final textPainter = TextPainter(textDirection: TextDirection.ltr);
    textPainter.text = const TextSpan(
      text: 'Population Diversity',
      style: TextStyle(color: Colors.purple, fontSize: 11, fontWeight: FontWeight.bold),
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(size.width - 125, padding));
  }

  @override
  bool shouldRepaint(DEDiversityChartPainter oldDelegate) =>
      oldDelegate.metrics.length != metrics.length;
}
