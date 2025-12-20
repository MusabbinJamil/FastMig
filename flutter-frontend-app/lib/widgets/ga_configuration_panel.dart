import 'package:flutter/material.dart';
import '../models/ga_config_model.dart';

class GAConfigurationPanel extends StatefulWidget {
  final GAConfigModel initialConfig;
  final Function(GAConfigModel) onConfigChanged;
  final VoidCallback? onApplyPressed;

  const GAConfigurationPanel({
    Key? key,
    required this.initialConfig,
    required this.onConfigChanged,
    this.onApplyPressed,
  }) : super(key: key);

  @override
  State<GAConfigurationPanel> createState() => _GAConfigurationPanelState();
}

class _GAConfigurationPanelState extends State<GAConfigurationPanel> {
  late GAConfigModel _config;

  final TextEditingController _populationController = TextEditingController();
  final TextEditingController _generationsController = TextEditingController();
  final TextEditingController _mutationRateController = TextEditingController();
  final TextEditingController _crossoverRateController =
      TextEditingController();
  final TextEditingController _fitnessThresholdController =
      TextEditingController();

  @override
  void initState() {
    super.initState();
    _config = widget.initialConfig;
    _initializeControllers();
  }

  void _initializeControllers() {
    _populationController.text = _config.populationSize.toString();
    _generationsController.text = _config.generations.toString();
    _mutationRateController.text = _config.mutationRate.toStringAsFixed(3);
    _crossoverRateController.text = _config.crossoverRate.toStringAsFixed(3);
    _fitnessThresholdController.text =
        _config.fitnessThreshold.toStringAsFixed(1);
  }

  void _updateConfig() {
    _config = _config.copyWith(
      populationSize:
          int.tryParse(_populationController.text) ?? _config.populationSize,
      generations:
          int.tryParse(_generationsController.text) ?? _config.generations,
      mutationRate:
          double.tryParse(_mutationRateController.text) ?? _config.mutationRate,
      crossoverRate: double.tryParse(_crossoverRateController.text) ??
          _config.crossoverRate,
      fitnessThreshold: double.tryParse(_fitnessThresholdController.text) ??
          _config.fitnessThreshold,
    );
    widget.onConfigChanged(_config);
  }

  void _applyPreset(String presetName) {
    _config = GAConfigModel.getPreset(presetName);
    _initializeControllers();
    _updateConfig();
  }

  @override
  void dispose() {
    _populationController.dispose();
    _generationsController.dispose();
    _mutationRateController.dispose();
    _crossoverRateController.dispose();
    _fitnessThresholdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ===== Preset Buttons =====
            Text(
              'Quick Presets',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.flash_on),
                    label: const Text('Fast'),
                    onPressed: () => _applyPreset('fast'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.scale),
                    label: const Text('Balanced'),
                    onPressed: () => _applyPreset('balanced'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.spa),
                    label: const Text('Quality'),
                    onPressed: () => _applyPreset('quality'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // ===== Population Parameters =====
            Text(
              'Population Parameters',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            _buildIntegerField(
              'Population Size',
              'Number of individuals per generation',
              _populationController,
              20,
              200,
            ),
            const SizedBox(height: 12),
            _buildIntegerField(
              'Generations',
              'Number of evolution generations',
              _generationsController,
              10,
              1000,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('Elitism'),
                    subtitle: const Text('Keep best individuals'),
                    value: _config.elitism,
                    onChanged: (value) {
                      setState(() {
                        _config = _config.copyWith(elitism: value ?? true);
                      });
                      _updateConfig();
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // ===== Evolution Operators =====
            Text(
              'Evolution Operators',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            _buildDoubleField(
              'Mutation Rate',
              'Probability of mutation (0.0 - 1.0)',
              _mutationRateController,
              0.0,
              1.0,
            ),
            const SizedBox(height: 12),
            _buildDoubleField(
              'Crossover Rate',
              'Probability of crossover (0.0 - 1.0)',
              _crossoverRateController,
              0.0,
              1.0,
            ),
            const SizedBox(height: 12),
            _buildDropdown(
              'Selection Method',
              _config.selectionMethod,
              ['tournament', 'roulette_wheel', 'rank_based'],
              (value) {
                setState(() {
                  _config = _config.copyWith(selectionMethod: value);
                });
                _updateConfig();
              },
            ),
            const SizedBox(height: 12),
            _buildDropdown(
              'Crossover Method',
              _config.crossoverMethod,
              ['single_point', 'two_point', 'uniform', 'arithmetic'],
              (value) {
                setState(() {
                  _config = _config.copyWith(crossoverMethod: value);
                });
                _updateConfig();
              },
            ),
            const SizedBox(height: 12),
            _buildDropdown(
              'Mutation Method',
              _config.mutationMethod,
              ['gaussian', 'uniform', 'adaptive'],
              (value) {
                setState(() {
                  _config = _config.copyWith(mutationMethod: value);
                });
                _updateConfig();
              },
            ),
            const SizedBox(height: 24),

            // ===== Convergence Settings =====
            Text(
              'Convergence Settings',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('Early Stopping'),
                    subtitle: const Text('Stop if no improvement'),
                    value: _config.earlyStoppingEnabled,
                    onChanged: (value) {
                      setState(() {
                        _config = _config.copyWith(
                            earlyStoppingEnabled: value ?? true);
                      });
                      _updateConfig();
                    },
                  ),
                ),
              ],
            ),
            if (_config.earlyStoppingEnabled) ...[
              const SizedBox(height: 12),
              _buildIntegerField(
                'Early Stopping Patience',
                'Generations without improvement before stopping',
                TextEditingController(
                    text: _config.earlyStoppingPatience.toString()),
                1,
                50,
              ),
            ],
            const SizedBox(height: 12),
            _buildDoubleField(
              'Fitness Threshold',
              'Target fitness score (0.0 - 100.0)',
              _fitnessThresholdController,
              0.0,
              100.0,
            ),
            const SizedBox(height: 24),

            // ===== Action Buttons =====
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.check_circle),
                    label: const Text('Apply Configuration'),
                    onPressed: () {
                      _updateConfig();
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
                'Config Summary: Pop=${_config.populationSize}, Gen=${_config.generations}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIntegerField(
    String label,
    String hint,
    TextEditingController controller,
    int min,
    int max,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 4),
        TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            hintText: hint,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            suffix: Text('[$min - $max]'),
          ),
          onChanged: (_) => _updateConfig(),
        ),
      ],
    );
  }

  Widget _buildDoubleField(
    String label,
    String hint,
    TextEditingController controller,
    double min,
    double max,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 4),
        TextField(
          controller: controller,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(
            hintText: hint,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            suffix:
                Text('[${min.toStringAsFixed(2)} - ${max.toStringAsFixed(2)}]'),
          ),
          onChanged: (_) => _updateConfig(),
        ),
      ],
    );
  }

  Widget _buildDropdown(
    String label,
    String currentValue,
    List<String> options,
    Function(String) onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 4),
        DropdownButtonFormField<String>(
          value: currentValue,
          items: options.map((option) {
            return DropdownMenuItem(
              value: option,
              child: Text(option.replaceAll('_', ' ').toUpperCase()),
            );
          }).toList(),
          onChanged: (value) {
            if (value != null) {
              onChanged(value);
            }
          },
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ],
    );
  }
}
