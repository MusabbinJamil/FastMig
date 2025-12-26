import 'package:flutter/material.dart';
import '../models/evolutionary_config_models.dart';

/// Base class for modular configuration panels
abstract class EvolutionaryConfigPanel extends StatefulWidget {
  final EvolutionaryConfigBase config;
  final Function(EvolutionaryConfigBase) onConfigChanged;

  const EvolutionaryConfigPanel({
    Key? key,
    required this.config,
    required this.onConfigChanged,
  }) : super(key: key);
}

/// ============================================================================
/// GENETIC ALGORITHM CONFIGURATION PANEL
/// ============================================================================

class GAConfigurationPanel extends StatefulWidget {
  final GAConfigModel config;
  final Function(GAConfigModel) onConfigChanged;

  const GAConfigurationPanel({
    Key? key,
    required this.config,
    required this.onConfigChanged,
  }) : super(key: key);

  @override
  State<GAConfigurationPanel> createState() => _GAConfigurationPanelState();
}

class _GAConfigurationPanelState extends State<GAConfigurationPanel> {
  late GAConfigModel _config;

  @override
  void initState() {
    super.initState();
    _config = widget.config;
  }

  void _updateConfig(GAConfigModel newConfig) {
    setState(() => _config = newConfig);
    widget.onConfigChanged(newConfig);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPresetButtons(),
          const SizedBox(height: 20),
          _buildSectionTitle('Population & Generations'),
          _buildSlider(
            label: 'Population Size',
            value: _config.populationSize.toDouble(),
            min: 10,
            max: 100,
            divisions: 9,
            onChanged: (v) => _updateConfig(
              _config.copyWith(populationSize: v.toInt()),
            ),
          ),
          _buildSlider(
            label: 'Generations',
            value: _config.generations.toDouble(),
            min: 10,
            max: 500,
            divisions: 49,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(generations: v.toInt())),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Genetic Operators'),
          _buildSlider(
            label: 'Mutation Rate: ${_config.mutationRate.toStringAsFixed(3)}',
            value: _config.mutationRate,
            min: 0.0,
            max: 1.0,
            divisions: 100,
            onChanged: (v) => _updateConfig(_config.copyWith(mutationRate: v)),
          ),
          _buildSlider(
            label:
                'Crossover Rate: ${_config.crossoverRate.toStringAsFixed(3)}',
            value: _config.crossoverRate,
            min: 0.0,
            max: 1.0,
            divisions: 100,
            onChanged: (v) => _updateConfig(_config.copyWith(crossoverRate: v)),
          ),
          const SizedBox(height: 16),
          _buildDropdown<String>(
            label: 'Selection Method',
            value: _config.selectionMethod,
            items: GAConfigModel.selectionMethods,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(selectionMethod: v)),
          ),
          _buildDropdown<String>(
            label: 'Crossover Method',
            value: _config.crossoverMethod,
            items: GAConfigModel.crossoverMethods,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(crossoverMethod: v)),
          ),
          _buildDropdown<String>(
            label: 'Mutation Method',
            value: _config.mutationMethod,
            items: GAConfigModel.mutationMethods,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(mutationMethod: v)),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Advanced Options'),
          _buildSwitchOption(
            label: 'Elitism',
            value: _config.elitism,
            onChanged: (v) => _updateConfig(_config.copyWith(elitism: v)),
            subtitle: 'Preserve best individuals to next generation',
          ),
          if (_config.elitism)
            _buildSlider(
              label: 'Elite Count',
              value: _config.eliteCount.toDouble(),
              min: 1,
              max: 10,
              divisions: 9,
              onChanged: (v) =>
                  _updateConfig(_config.copyWith(eliteCount: v.toInt())),
            ),
          _buildSwitchOption(
            label: 'Early Stopping',
            value: _config.earlyStoppingEnabled,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(earlyStoppingEnabled: v)),
            subtitle: 'Stop if fitness plateaus',
          ),
          if (_config.earlyStoppingEnabled)
            _buildSlider(
              label: 'Early Stopping Patience',
              value: _config.earlyStoppingPatience.toDouble(),
              min: 1,
              max: 50,
              divisions: 49,
              onChanged: (v) => _updateConfig(
                _config.copyWith(earlyStoppingPatience: v.toInt()),
              ),
            ),
          const SizedBox(height: 16),
          _buildSectionTitle('Fitness Settings'),
          _buildSlider(
            label:
                'Fitness Threshold: ${_config.fitnessThreshold.toStringAsFixed(1)}%',
            value: _config.fitnessThreshold,
            min: 0,
            max: 100,
            divisions: 100,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(fitnessThreshold: v)),
          ),
          _buildSwitchOption(
            label: 'Track Progress',
            value: _config.trackProgress,
            onChanged: (v) => _updateConfig(_config.copyWith(trackProgress: v)),
            subtitle: 'Record metrics for each generation',
          ),
        ],
      ),
    );
  }

  Widget _buildPresetButtons() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Presets',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: ['fast', 'balanced', 'quality']
              .map(
                (preset) => ElevatedButton(
                  onPressed: () =>
                      _updateConfig(GAConfigModel.getPreset(preset)),
                  child: Text(preset.capitalize()),
                ),
              )
              .toList(),
        ),
      ],
    );
  }

  Widget _buildSlider({
    required String label,
    required double value,
    required double min,
    required double max,
    required int divisions,
    required Function(double) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            label: value.toStringAsFixed(
              value > 10 ? 0 : 3,
            ),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown<T>({
    required String label,
    required T value,
    required List<T> items,
    required Function(T) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 4),
          DropdownButton<T>(
            value: value,
            isExpanded: true,
            items: items
                .map(
                  (item) => DropdownMenuItem(
                    value: item,
                    child: Text(item.toString()),
                  ),
                )
                .toList(),
            onChanged: (v) => v != null ? onChanged(v) : null,
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchOption({
    required String label,
    required bool value,
    required Function(bool) onChanged,
    String? subtitle,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: Theme.of(context).textTheme.bodyMedium),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  ],
                ],
              ),
              Switch(value: value, onChanged: onChanged),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade700,
            ),
      ),
    );
  }
}

/// ============================================================================
/// PSO CONFIGURATION PANEL
/// ============================================================================

class PSOConfigurationPanel extends StatefulWidget {
  final PSOConfigModel config;
  final Function(PSOConfigModel) onConfigChanged;

  const PSOConfigurationPanel({
    Key? key,
    required this.config,
    required this.onConfigChanged,
  }) : super(key: key);

  @override
  State<PSOConfigurationPanel> createState() => _PSOConfigurationPanelState();
}

class _PSOConfigurationPanelState extends State<PSOConfigurationPanel> {
  late PSOConfigModel _config;

  @override
  void initState() {
    super.initState();
    _config = widget.config;
  }

  void _updateConfig(PSOConfigModel newConfig) {
    setState(() => _config = newConfig);
    widget.onConfigChanged(newConfig);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Swarm Configuration'),
          _buildSlider(
            label: 'Swarm Size',
            value: _config.swarmSize.toDouble(),
            min: 10,
            max: 100,
            divisions: 9,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(swarmSize: v.toInt())),
          ),
          _buildSlider(
            label: 'Iterations',
            value: _config.iterations.toDouble(),
            min: 10,
            max: 500,
            divisions: 49,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(iterations: v.toInt())),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Cognitive & Social Parameters'),
          Text(
            'Balance between individual experience and swarm knowledge',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey,
                ),
          ),
          const SizedBox(height: 8),
          _buildSlider(
            label:
                'Cognitive Parameter (c1): ${_config.cognitiveParameter.toStringAsFixed(2)}',
            value: _config.cognitiveParameter,
            min: 0.5,
            max: 3.0,
            divisions: 50,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(cognitiveParameter: v)),
          ),
          _buildSlider(
            label:
                'Social Parameter (c2): ${_config.socialParameter.toStringAsFixed(2)}',
            value: _config.socialParameter,
            min: 0.5,
            max: 3.0,
            divisions: 50,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(socialParameter: v)),
          ),
          _buildSlider(
            label:
                'Inertia Weight: ${_config.inertiaWeight.toStringAsFixed(3)}',
            value: _config.inertiaWeight,
            min: 0.0,
            max: 1.0,
            divisions: 100,
            onChanged: (v) => _updateConfig(_config.copyWith(inertiaWeight: v)),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Velocity Bounds'),
          _buildSlider(
            label: 'Velocity Max: ${_config.velocityMax.toStringAsFixed(2)}',
            value: _config.velocityMax,
            min: 0.1,
            max: 5.0,
            divisions: 49,
            onChanged: (v) => _updateConfig(_config.copyWith(velocityMax: v)),
          ),
          _buildSlider(
            label: 'Velocity Min: ${_config.velocityMin.toStringAsFixed(2)}',
            value: _config.velocityMin,
            min: -5.0,
            max: 0.0,
            divisions: 50,
            onChanged: (v) => _updateConfig(_config.copyWith(velocityMin: v)),
          ),
          const SizedBox(height: 16),
          _buildSwitchOption(
            label: 'Use Constriction Factor',
            value: _config.useConstrictionFactor,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(useConstrictionFactor: v)),
            subtitle: 'Apply constriction coefficient χ',
          ),
          if (_config.useConstrictionFactor)
            _buildSlider(
              label:
                  'Constriction: ${_config.constrictionCoefficient.toStringAsFixed(3)}',
              value: _config.constrictionCoefficient,
              min: 0.0,
              max: 1.0,
              divisions: 100,
              onChanged: (v) =>
                  _updateConfig(_config.copyWith(constrictionCoefficient: v)),
            ),
          const SizedBox(height: 16),
          _buildSectionTitle('Topology Settings'),
          _buildDropdown<String>(
            label: 'Topology Type',
            value: _config.topologyType,
            items: PSOConfigModel.topologyTypes,
            onChanged: (v) => _updateConfig(_config.copyWith(topologyType: v)),
          ),
          _buildSlider(
            label: 'Neighborhood Size',
            value: _config.neighborhoodSize.toDouble(),
            min: 2,
            max: 20,
            divisions: 18,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(neighborhoodSize: v.toInt())),
          ),
        ],
      ),
    );
  }

  Widget _buildSlider({
    required String label,
    required double value,
    required double min,
    required double max,
    required int divisions,
    required Function(double) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            label: value.toStringAsFixed(2),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown<T>({
    required String label,
    required T value,
    required List<T> items,
    required Function(T) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 4),
          DropdownButton<T>(
            value: value,
            isExpanded: true,
            items: items
                .map(
                  (item) => DropdownMenuItem(
                    value: item,
                    child: Text(item.toString()),
                  ),
                )
                .toList(),
            onChanged: (v) => v != null ? onChanged(v) : null,
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchOption({
    required String label,
    required bool value,
    required Function(bool) onChanged,
    String? subtitle,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: Theme.of(context).textTheme.bodyMedium),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  ],
                ],
              ),
              Switch(value: value, onChanged: onChanged),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade700,
            ),
      ),
    );
  }
}

/// ============================================================================
/// DIFFERENTIAL EVOLUTION CONFIGURATION PANEL
/// ============================================================================

class DEConfigurationPanel extends StatefulWidget {
  final DEConfigModel config;
  final Function(DEConfigModel) onConfigChanged;

  const DEConfigurationPanel({
    Key? key,
    required this.config,
    required this.onConfigChanged,
  }) : super(key: key);

  @override
  State<DEConfigurationPanel> createState() => _DEConfigurationPanelState();
}

class _DEConfigurationPanelState extends State<DEConfigurationPanel> {
  late DEConfigModel _config;

  @override
  void initState() {
    super.initState();
    _config = widget.config;
  }

  void _updateConfig(DEConfigModel newConfig) {
    setState(() => _config = newConfig);
    widget.onConfigChanged(newConfig);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Population & Generations'),
          _buildSlider(
            label: 'Population Size',
            value: _config.populationSize.toDouble(),
            min: 10,
            max: 100,
            divisions: 9,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(populationSize: v.toInt())),
          ),
          _buildSlider(
            label: 'Generations',
            value: _config.generations.toDouble(),
            min: 10,
            max: 500,
            divisions: 49,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(generations: v.toInt())),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('DE Control Parameters'),
          Text(
            'F: mutation magnitude | CR: parameter selection probability',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey,
                ),
          ),
          const SizedBox(height: 8),
          _buildSlider(
            label:
                'Scale Factor (F): ${_config.scaleFactor.toStringAsFixed(3)}',
            value: _config.scaleFactor,
            min: 0.0,
            max: 2.0,
            divisions: 200,
            onChanged: (v) => _updateConfig(_config.copyWith(scaleFactor: v)),
          ),
          _buildSlider(
            label:
                'Crossover Rate (CR): ${_config.crossoverRate.toStringAsFixed(3)}',
            value: _config.crossoverRate,
            min: 0.0,
            max: 1.0,
            divisions: 100,
            onChanged: (v) => _updateConfig(_config.copyWith(crossoverRate: v)),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Strategy Selection'),
          _buildDropdown<String>(
            label: 'Mutation Strategy',
            value: _config.mutationStrategy,
            items: DEConfigModel.mutationStrategies,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(mutationStrategy: v)),
          ),
          _buildDropdown<String>(
            label: 'Selection Strategy',
            value: _config.selectionStrategy,
            items: ['best', 'tournament', 'random'],
            onChanged: (v) =>
                _updateConfig(_config.copyWith(selectionStrategy: v)),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Advanced Options'),
          _buildSwitchOption(
            label: 'Adaptive Scale Factor (F)',
            value: _config.adaptiveF,
            onChanged: (v) => _updateConfig(_config.copyWith(adaptiveF: v)),
            subtitle: 'Self-adaptive F parameter',
          ),
          _buildSwitchOption(
            label: 'Adaptive Crossover Rate (CR)',
            value: _config.adaptiveCR,
            onChanged: (v) => _updateConfig(_config.copyWith(adaptiveCR: v)),
            subtitle: 'Self-adaptive CR parameter',
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Search Space Bounds'),
          _buildSlider(
            label: 'Lower Bound: ${_config.lowerBound.toStringAsFixed(2)}',
            value: _config.lowerBound,
            min: -10.0,
            max: 0.0,
            divisions: 100,
            onChanged: (v) => _updateConfig(_config.copyWith(lowerBound: v)),
          ),
          _buildSlider(
            label: 'Upper Bound: ${_config.upperBound.toStringAsFixed(2)}',
            value: _config.upperBound,
            min: 0.0,
            max: 10.0,
            divisions: 100,
            onChanged: (v) => _updateConfig(_config.copyWith(upperBound: v)),
          ),
        ],
      ),
    );
  }

  Widget _buildSlider({
    required String label,
    required double value,
    required double min,
    required double max,
    required int divisions,
    required Function(double) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            label: value.toStringAsFixed(2),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown<T>({
    required String label,
    required T value,
    required List<T> items,
    required Function(T) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 4),
          DropdownButton<T>(
            value: value,
            isExpanded: true,
            items: items
                .map(
                  (item) => DropdownMenuItem(
                    value: item,
                    child: Text(item.toString()),
                  ),
                )
                .toList(),
            onChanged: (v) => v != null ? onChanged(v) : null,
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchOption({
    required String label,
    required bool value,
    required Function(bool) onChanged,
    String? subtitle,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: Theme.of(context).textTheme.bodyMedium),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  ],
                ],
              ),
              Switch(value: value, onChanged: onChanged),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade700,
            ),
      ),
    );
  }
}

/// ============================================================================
/// EVOLUTION STRATEGY CONFIGURATION PANEL
/// ============================================================================

class ESConfigurationPanel extends StatefulWidget {
  final ESConfigModel config;
  final Function(ESConfigModel) onConfigChanged;

  const ESConfigurationPanel({
    Key? key,
    required this.config,
    required this.onConfigChanged,
  }) : super(key: key);

  @override
  State<ESConfigurationPanel> createState() => _ESConfigurationPanelState();
}

class _ESConfigurationPanelState extends State<ESConfigurationPanel> {
  late ESConfigModel _config;

  @override
  void initState() {
    super.initState();
    _config = widget.config;
  }

  void _updateConfig(ESConfigModel newConfig) {
    setState(() => _config = newConfig);
    widget.onConfigChanged(newConfig);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Population Configuration'),
          _buildSlider(
            label: 'Population Size (μ)',
            value: _config.populationSize.toDouble(),
            min: 5,
            max: 50,
            divisions: 45,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(populationSize: v.toInt())),
          ),
          _buildSlider(
            label: 'Offspring Size (λ)',
            value: _config.offspringSize.toDouble(),
            min: 10,
            max: 200,
            divisions: 19,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(offspringSize: v.toInt())),
          ),
          _buildSlider(
            label: 'Generations',
            value: _config.generations.toDouble(),
            min: 10,
            max: 500,
            divisions: 49,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(generations: v.toInt())),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Selection Type'),
          Row(
            children: ['plus', 'comma']
                .map(
                  (type) => Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ElevatedButton(
                        onPressed: () => _updateConfig(
                            _config.copyWith(selectionType: type)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _config.selectionType == type
                              ? Colors.blue
                              : Colors.grey.shade300,
                        ),
                        child: Text(
                          type == 'plus' ? '(μ+λ)' : '(μ,λ)',
                          style: TextStyle(
                            color: _config.selectionType == type
                                ? Colors.white
                                : Colors.black,
                          ),
                        ),
                      ),
                    ),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 8),
          Text(
            _config.selectionType == 'plus'
                ? '(μ+λ): Best individuals from parent+offspring'
                : '(μ,λ): Only offspring, must be λ ≥ μ',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey,
                ),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Mutation Settings'),
          _buildSlider(
            label:
                'Initial Mutation Rate: ${_config.initialMutationRate.toStringAsFixed(3)}',
            value: _config.initialMutationRate,
            min: 0.01,
            max: 0.5,
            divisions: 49,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(initialMutationRate: v)),
          ),
          _buildSwitchOption(
            label: 'Self-Adaptive Mutation',
            value: _config.selfAdaptiveMutation,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(selfAdaptiveMutation: v)),
            subtitle: 'Automatically adjust mutation rate',
          ),
          if (_config.selfAdaptiveMutation)
            _buildSlider(
              label:
                  'Learning Rate: ${_config.learningRate.toStringAsFixed(3)}',
              value: _config.learningRate,
              min: 0.01,
              max: 0.5,
              divisions: 49,
              onChanged: (v) =>
                  _updateConfig(_config.copyWith(learningRate: v)),
            ),
          const SizedBox(height: 16),
          _buildSectionTitle('Recombination Settings'),
          _buildDropdown<String>(
            label: 'Recombination Type',
            value: _config.recombinationType,
            items: ESConfigModel.recombinationTypes,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(recombinationType: v)),
          ),
          _buildSlider(
            label: 'Parent Count',
            value: _config.parentCount.toDouble(),
            min: 2,
            max: 10,
            divisions: 8,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(parentCount: v.toInt())),
          ),
        ],
      ),
    );
  }

  Widget _buildSlider({
    required String label,
    required double value,
    required double min,
    required double max,
    required int divisions,
    required Function(double) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            label: value.toStringAsFixed(
              value > 10 ? 0 : 3,
            ),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown<T>({
    required String label,
    required T value,
    required List<T> items,
    required Function(T) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 4),
          DropdownButton<T>(
            value: value,
            isExpanded: true,
            items: items
                .map(
                  (item) => DropdownMenuItem(
                    value: item,
                    child: Text(item.toString()),
                  ),
                )
                .toList(),
            onChanged: (v) => v != null ? onChanged(v) : null,
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchOption({
    required String label,
    required bool value,
    required Function(bool) onChanged,
    String? subtitle,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: Theme.of(context).textTheme.bodyMedium),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  ],
                ],
              ),
              Switch(value: value, onChanged: onChanged),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade700,
            ),
      ),
    );
  }
}

/// ============================================================================
/// HYBRID CONFIGURATION PANEL
/// ============================================================================

class HybridConfigurationPanel extends StatefulWidget {
  final HybridConfigModel config;
  final Function(HybridConfigModel) onConfigChanged;

  const HybridConfigurationPanel({
    Key? key,
    required this.config,
    required this.onConfigChanged,
  }) : super(key: key);

  @override
  State<HybridConfigurationPanel> createState() =>
      _HybridConfigurationPanelState();
}

class _HybridConfigurationPanelState extends State<HybridConfigurationPanel> {
  late HybridConfigModel _config;

  @override
  void initState() {
    super.initState();
    _config = widget.config;
  }

  void _updateConfig(HybridConfigModel newConfig) {
    setState(() => _config = newConfig);
    widget.onConfigChanged(newConfig);
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('Hybrid Strategy'),
          _buildSwitchOption(
            label: 'Auto-Select Algorithm',
            value: _config.autoSelectAlgorithm,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(autoSelectAlgorithm: v)),
            subtitle: 'Automatically choose best algorithm per column type',
          ),
          _buildSwitchOption(
            label: 'Ensemble Mode',
            value: _config.ensembleMode,
            onChanged: (v) => _updateConfig(_config.copyWith(ensembleMode: v)),
            subtitle: 'Run multiple algorithms and blend results',
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Enabled Algorithms'),
          ..._config.enabledAlgorithms.map(
            (algo) => _buildAlgorithmToggle(algo),
          ),
          const SizedBox(height: 16),
          _buildSectionTitle('Global Settings'),
          _buildSlider(
            label:
                'Fitness Threshold: ${_config.fitnessThreshold.toStringAsFixed(1)}%',
            value: _config.fitnessThreshold,
            min: 0,
            max: 100,
            divisions: 100,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(fitnessThreshold: v)),
          ),
          _buildSlider(
            label: 'Max Iterations',
            value: _config.maxIterations.toDouble(),
            min: 10,
            max: 500,
            divisions: 49,
            onChanged: (v) =>
                _updateConfig(_config.copyWith(maxIterations: v.toInt())),
          ),
        ],
      ),
    );
  }

  Widget _buildAlgorithmToggle(String algo) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: CheckboxListTile(
        value: _config.enabledAlgorithms.contains(algo),
        onChanged: (v) {
          final list = List<String>.from(_config.enabledAlgorithms);
          if (v == true) {
            list.add(algo);
          } else {
            list.remove(algo);
          }
          _updateConfig(_config.copyWith(enabledAlgorithms: list));
        },
        title: Text(algo.toUpperCase()),
        contentPadding: EdgeInsets.zero,
      ),
    );
  }

  Widget _buildSlider({
    required String label,
    required double value,
    required double min,
    required double max,
    required int divisions,
    required Function(double) onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodyMedium),
          Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            label: value.toStringAsFixed(
              value > 10 ? 0 : 2,
            ),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchOption({
    required String label,
    required bool value,
    required Function(bool) onChanged,
    String? subtitle,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: Theme.of(context).textTheme.bodyMedium),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  ],
                ],
              ),
              Switch(value: value, onChanged: onChanged),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade700,
            ),
      ),
    );
  }
}

extension _StringExtension on String {
  String capitalize() =>
      '${this[0].toUpperCase()}${substring(1).toLowerCase()}';
}
