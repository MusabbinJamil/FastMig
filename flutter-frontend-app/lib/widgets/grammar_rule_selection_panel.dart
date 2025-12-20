import 'package:flutter/material.dart';
import '../models/ga_config_model.dart';

class GrammarRuleSelectionPanel extends StatefulWidget {
  final GrammarConfigModel initialConfig;
  final Function(GrammarConfigModel) onConfigChanged;
  final VoidCallback? onApplyPressed;

  const GrammarRuleSelectionPanel({
    Key? key,
    required this.initialConfig,
    required this.onConfigChanged,
    this.onApplyPressed,
  }) : super(key: key);

  @override
  State<GrammarRuleSelectionPanel> createState() =>
      _GrammarRuleSelectionPanelState();
}

class _GrammarRuleSelectionPanelState extends State<GrammarRuleSelectionPanel> {
  late GrammarConfigModel _config;
  late TextEditingController _customGrammarController;
  final TextEditingController _ruleController = TextEditingController();
  final TextEditingController _maxDepthController = TextEditingController();

  final Map<String, List<String>> _grammarPresets = {
    'standard': [
      '<expr> ::= <expr> + <term> | <expr> - <term> | <term>',
      '<term> ::= <term> * <factor> | <term> / <factor> | <factor>',
      '<factor> ::= ( <expr> ) | <number>',
      '<number> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9',
    ],
    'boolean': [
      '<expr> ::= <expr> AND <term> | <expr> OR <term> | <term>',
      '<term> ::= NOT <term> | <comparison>',
      '<comparison> ::= <value> > <value> | <value> < <value> | <value> = <value>',
      '<value> ::= x | y | z',
    ],
    'trigonometric': [
      '<expr> ::= sin(<expr>) | cos(<expr>) | tan(<expr>) | <base>',
      '<base> ::= x | pi | e | <number>',
      '<number> ::= 0.1 | 0.5 | 1.0 | 2.0 | 3.0',
    ],
    'data_cleaning': [
      '<operation> ::= <filter> | <transform> | <aggregate>',
      '<filter> ::= filter_null | filter_outliers | filter_duplicates',
      '<transform> ::= normalize | standardize | encode',
      '<aggregate> ::= sum | mean | median | mode',
    ],
    'statistical': [
      '<expr> ::= mean(<data>) | std(<data>) | median(<data>) | <stat>',
      '<stat> ::= variance | skewness | kurtosis',
      '<data> ::= column1 | column2 | column3',
    ],
  };

  @override
  void initState() {
    super.initState();
    _config = widget.initialConfig;
    _customGrammarController =
        TextEditingController(text: _config.customGrammarPath ?? '');
    _maxDepthController.text = _config.maxTreeDepth.toString();
  }

  @override
  void dispose() {
    _customGrammarController.dispose();
    _ruleController.dispose();
    _maxDepthController.dispose();
    super.dispose();
  }

  void _applyPreset(String presetName) {
    final rules = _grammarPresets[presetName] ?? [];
    setState(() {
      _config = _config.copyWith(
        grammarType: presetName,
        rules: rules,
      );
    });
    widget.onConfigChanged(_config);
  }

  void _addCustomRule() {
    if (_ruleController.text.isNotEmpty) {
      setState(() {
        _config = _config.copyWith(
          rules: [..._config.rules, _ruleController.text],
        );
      });
      _ruleController.clear();
      widget.onConfigChanged(_config);
    }
  }

  void _removeRule(int index) {
    setState(() {
      final updatedRules = List<String>.from(_config.rules);
      updatedRules.removeAt(index);
      _config = _config.copyWith(rules: updatedRules);
    });
    widget.onConfigChanged(_config);
  }

  void _updateMaxDepth() {
    final newDepth =
        int.tryParse(_maxDepthController.text) ?? _config.maxTreeDepth;
    setState(() {
      _config = _config.copyWith(maxTreeDepth: newDepth);
    });
    widget.onConfigChanged(_config);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ===== Grammar Type Selection =====
            Text(
              'Grammar Type',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _grammarPresets.keys.map((preset) {
                final isSelected = _config.grammarType == preset;
                return FilterChip(
                  label: Text(preset.replaceAll('_', ' ').toUpperCase()),
                  selected: isSelected,
                  onSelected: (_) => _applyPreset(preset),
                  backgroundColor: Colors.grey[200],
                  selectedColor: Colors.blue[100],
                  side: BorderSide(
                    color: isSelected ? Colors.blue : Colors.transparent,
                    width: 2,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // ===== Tree Parameters =====
            Text(
              'Expression Tree Parameters',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Max Tree Depth',
                    style: Theme.of(context).textTheme.labelLarge),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _maxDepthController,
                        keyboardType: TextInputType.number,
                        decoration: InputDecoration(
                          hintText: 'Maximum derivation tree depth',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        onChanged: (_) => _updateMaxDepth(),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        children: [
                          const Icon(Icons.account_tree, size: 20),
                          const SizedBox(height: 4),
                          Text(
                            '${2 << _config.maxTreeDepth}',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const Text('Max nodes',
                              style: TextStyle(fontSize: 10)),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            CheckboxListTile(
              title: const Text('Type Checking'),
              subtitle:
                  const Text('Validate expression types during evolution'),
              value: _config.enableTypeChecking,
              onChanged: (value) {
                setState(() {
                  _config = _config.copyWith(enableTypeChecking: value ?? true);
                });
                widget.onConfigChanged(_config);
              },
            ),
            const SizedBox(height: 24),

            // ===== Rules Management =====
            Text(
              'Grammar Rules',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            if (_config.rules.isEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey[300] ?? Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                  color: Colors.grey[50],
                ),
                child: const Center(
                  child: Text(
                    'No rules defined. Select a preset or add custom rules.',
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _config.rules.length,
                itemBuilder: (context, index) {
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: Container(
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          color: Colors.blue[100],
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Center(
                          child: Text(
                            '${index + 1}',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                      title: Text(
                        _config.rules[index],
                        style: const TextStyle(
                            fontFamily: 'monospace', fontSize: 12),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () => _removeRule(index),
                      ),
                    ),
                  );
                },
              ),
            const SizedBox(height: 16),

            // ===== Add Custom Rule =====
            Text(
              'Add Custom Rule',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ruleController,
                    decoration: InputDecoration(
                      hintText: 'BNF rule (e.g., <expr> ::= ...)',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    maxLines: null,
                  ),
                ),
                const SizedBox(width: 8),
                FloatingActionButton.small(
                  onPressed: _addCustomRule,
                  child: const Icon(Icons.add),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // ===== Action Buttons =====
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.check_circle),
                    label: const Text('Apply Grammar Config'),
                    onPressed: () {
                      widget.onConfigChanged(_config);
                      widget.onApplyPressed?.call();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                'Rules: ${_config.rules.length}, Max Depth: ${_config.maxTreeDepth}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
