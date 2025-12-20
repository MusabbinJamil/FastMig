import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../models/ga_config_model.dart';

class ExpressionTreeVisualization extends StatefulWidget {
  final ExpressionTreeNode? rootNode;
  final String? rawExpression;
  final double? fitnessScore;
  final bool isLoading;
  final String? errorMessage;

  const ExpressionTreeVisualization({
    Key? key,
    this.rootNode,
    this.rawExpression,
    this.fitnessScore,
    this.isLoading = false,
    this.errorMessage,
  }) : super(key: key);

  @override
  State<ExpressionTreeVisualization> createState() =>
      _ExpressionTreeVisualizationState();
}

class _ExpressionTreeVisualizationState
    extends State<ExpressionTreeVisualization> {
  late TransformationController _transformationController;
  int _selectedNodeId = -1;
  ExpressionTreeNode? _selectedNode;

  @override
  void initState() {
    super.initState();
    _transformationController = TransformationController();
  }

  @override
  void dispose() {
    _transformationController.dispose();
    super.dispose();
  }

  void _selectNode(ExpressionTreeNode node) {
    setState(() {
      _selectedNode = node;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ===== Header =====
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.account_tree, size: 24),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Expression Tree',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        if (widget.rawExpression != null)
                          Text(
                            widget.rawExpression!,
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      fontFamily: 'monospace',
                                      color: Colors.grey[600],
                                    ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                      ],
                    ),
                  ],
                ),
                if (widget.fitnessScore != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: _getFitnessColor(widget.fitnessScore!)
                          .withOpacity(0.2),
                      border: Border.all(
                        color: _getFitnessColor(widget.fitnessScore!),
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: [
                        const Text('Fitness', style: TextStyle(fontSize: 10)),
                        Text(
                          widget.fitnessScore!.toStringAsFixed(2),
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
          const Divider(),

          // ===== Main Content =====
          Expanded(
            child: widget.isLoading
                ? const Center(child: CircularProgressIndicator())
                : widget.errorMessage != null
                    ? _buildErrorWidget()
                    : widget.rootNode != null
                        ? _buildTreeVisualization()
                        : _buildEmptyWidget(),
          ),

          // ===== Node Details Panel =====
          if (_selectedNode != null) ...[
            const Divider(),
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: _buildNodeDetailsPanel(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTreeVisualization() {
    return InteractiveViewer(
      transformationController: _transformationController,
      minScale: 0.5,
      maxScale: 3.0,
      child: Center(
        child: SizedBox(
          width: 800,
          height: 600,
          child: CustomPaint(
            painter: TreePainter(
              rootNode: widget.rootNode!,
              onNodeTapped: _selectNode,
              selectedNode: _selectedNode,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNodeDetailsPanel() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300] ?? Colors.grey),
        borderRadius: BorderRadius.circular(8),
        color: Colors.grey[50],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Selected: ${_selectedNode!.value}',
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  Text(
                    'Type: ${_selectedNode!.type}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
              if (_selectedNode!.fitnessContribution != null)
                Chip(
                  label: Text(
                      'Fitness: ${_selectedNode!.fitnessContribution!.toStringAsFixed(3)}'),
                  backgroundColor: _getFitnessColor(
                    _selectedNode!.fitnessContribution! * 100,
                  ).withOpacity(0.3),
                ),
            ],
          ),
          if (_selectedNode!.children.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Children: ${_selectedNode!.children.length}',
              style: Theme.of(context).textTheme.labelSmall,
            ),
            Wrap(
              spacing: 4,
              children: _selectedNode!.children.map((child) {
                return Chip(
                  label: Text(child.value),
                  onDeleted: null,
                  avatar: Icon(
                    _getTypeIcon(child.type),
                    size: 16,
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              'Error',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              widget.errorMessage ?? 'Unknown error',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyWidget() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.account_tree, size: 48, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'No Expression Tree',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              'Run GA evolution to generate an expression tree',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getFitnessColor(double fitness) {
    if (fitness >= 80) return Colors.green;
    if (fitness >= 60) return Colors.orange;
    return Colors.red;
  }

  IconData _getTypeIcon(String type) {
    switch (type) {
      case 'operator':
        return Icons.add;
      case 'function':
        return Icons.functions;
      case 'operand':
        return Icons.tag;
      default:
        return Icons.circle;
    }
  }
}

/// Custom painter for rendering the expression tree
class TreePainter extends CustomPainter {
  final ExpressionTreeNode rootNode;
  final Function(ExpressionTreeNode) onNodeTapped;
  final ExpressionTreeNode? selectedNode;

  late Paint _linePaint;
  late Paint _nodePaint;
  late Paint _selectedNodePaint;
  late TextPainter _textPainter;

  TreePainter({
    required this.rootNode,
    required this.onNodeTapped,
    this.selectedNode,
  }) {
    _linePaint = Paint()
      ..color = Colors.grey[400]!
      ..strokeWidth = 2;

    _nodePaint = Paint()
      ..color = Colors.blue[100]!
      ..style = PaintingStyle.fill;

    _selectedNodePaint = Paint()
      ..color = Colors.amber[200]!
      ..style = PaintingStyle.fill;
  }

  @override
  void paint(Canvas canvas, Size size) {
    // Draw tree with hierarchical layout
    _drawNode(canvas, size, rootNode, size.width / 2, 50, size.width / 4);
  }

  void _drawNode(
    Canvas canvas,
    Size canvasSize,
    ExpressionTreeNode node,
    double x,
    double y,
    double offsetX,
  ) {
    // Draw connections to children
    if (node.children.isNotEmpty) {
      final childOffsetX = offsetX / 2;
      for (int i = 0; i < node.children.length; i++) {
        final childX =
            x + (i - node.children.length / 2 + 0.5) * childOffsetX * 2;
        final childY = y + 80;

        // Draw line
        canvas.drawLine(
            Offset(x, y + 20), Offset(childX, childY - 20), _linePaint);

        // Recursively draw child
        _drawNode(
          canvas,
          canvasSize,
          node.children[i],
          childX,
          childY,
          childOffsetX,
        );
      }
    }

    // Draw node circle
    final isSelected =
        selectedNode != null && selectedNode!.value == node.value;
    final nodePaint = isSelected ? _selectedNodePaint : _nodePaint;

    canvas.drawCircle(Offset(x, y), 20, nodePaint);

    // Draw border for selected node
    if (isSelected) {
      canvas.drawCircle(
        Offset(x, y),
        20,
        Paint()
          ..color = Colors.amber
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3,
      );
    }

    // Draw text
    final textPainter = TextPainter(
      text: TextSpan(
        text: node.value.length > 3
            ? '${node.value.substring(0, 3)}'
            : node.value,
        style: const TextStyle(
          color: Colors.black87,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    );

    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        x - textPainter.width / 2,
        y - textPainter.height / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(TreePainter oldDelegate) => true;
}
