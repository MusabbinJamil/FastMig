# Frontend-Backend GA Integration Guide

## Available Backend Endpoints for Flutter Frontend

### Base URL
```
http://localhost:5000
```

## Endpoint Workflow

### Step 1: Upload Data
**Endpoint:** `POST /upload`
- Upload CSV file for processing
- Response includes filename

### Step 2: Analyze Population
**Endpoint:** `POST /ga/analyze-population`
- Analyzes fitness distribution
- Shows healthy vs unhealthy records

**Flutter Code:**
```dart
final analysis = await _apiService.analyzePopulationFitness(
  fitnessThreshold: _gaConfig.fitnessThreshold,
);
```

### Step 3: Select Populations
**Endpoint:** `POST /ga/select-populations`
- Selects healthy templates and unhealthy records

**Flutter Code:**
```dart
final config = await _apiService.selectPopulations(
  fitnessThreshold: 85.0,
  healthySampleSize: null,
);
```

### Step 4: Run GA Evolution
**Endpoint:** `POST /ga/run-evolution`
- Executes GA with customizable parameters
- Returns fitness history and results

**Flutter Code:**
```dart
final result = await _apiService.runGeneticAlgorithmEvolution(
  gaConfig: _gaConfig.toJson(),
  grammarConfig: _grammarConfig.toJson(),
  trackProgress: true,
);

// Response includes:
// - fitness_history: List of generation metrics
// - fitness_metrics: Overall improvement stats
// - expression_tree: Best individual found
// - total_generations: Generations completed
// - convergence_achieved: Boolean convergence status
```

### Step 5: Export Results
**Endpoint:** `POST /ga/export-evolved`
- Exports evolved dataset in CSV or JSON

**Flutter Code:**
```dart
final export = await _apiService.exportEvolvedData(
  filename: 'evolved_data',
  format: 'csv',
);
```

## API Service Methods to Implement

Update your Flutter `api_service.dart` with these methods:

```dart
// Analyze population fitness
Future<Map<String, dynamic>> analyzePopulationFitness({
  required double fitnessThreshold,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ga/analyze-population'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'fitness_threshold': fitnessThreshold}),
  );
  
  if (response.statusCode != 200) {
    throw Exception('Failed to analyze population');
  }
  
  return jsonDecode(response.body);
}

// Select populations for evolution
Future<Map<String, dynamic>> selectPopulations({
  required double fitnessThreshold,
  int? healthySampleSize,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ga/select-populations'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'fitness_threshold': fitnessThreshold,
      'healthy_sample_size': healthySampleSize,
    }),
  );
  
  if (response.statusCode != 200) {
    throw Exception('Failed to select populations');
  }
  
  return jsonDecode(response.body);
}

// Run GA evolution
Future<Map<String, dynamic>> runGeneticAlgorithmEvolution({
  required Map<String, dynamic> gaConfig,
  Map<String, dynamic>? grammarConfig,
  required bool trackProgress,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ga/run-evolution'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      ...gaConfig,
      'track_progress': trackProgress,
      if (grammarConfig != null) 'grammar_config': grammarConfig,
    }),
  );
  
  if (response.statusCode != 200) {
    throw Exception('GA Evolution failed');
  }
  
  return jsonDecode(response.body);
}

// Export evolved data
Future<Map<String, dynamic>> exportEvolvedData({
  required String filename,
  required String format,
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ga/export-evolved'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'filename': filename,
      'format': format,
    }),
  );
  
  if (response.statusCode != 200) {
    throw Exception('Export failed');
  }
  
  return jsonDecode(response.body);
}
```

## Configuration Models

### GAConfigModel (from ga_config_model.dart)
```dart
GAConfigModel(
  populationSize: 30,
  generations: 100,
  mutationRate: 0.1,
  crossoverRate: 0.8,
  elitism: true,
  eliteCount: 2,
  selectionMethod: 'tournament',
  crossoverMethod: 'single_point',
  mutationMethod: 'gaussian',
  earlyStoppingEnabled: true,
  earlyStoppingPatience: 10,
  fitnessThreshold: 85.0,
)
```

### Response Data Structure

**fitness_history (List):**
```json
{
  "generation": 0,
  "best_fitness": 45.2,
  "worst_fitness": 20.1,
  "average_fitness": 35.8,
  "fitness_variance": 50.5,
  "population_size": 30
}
```

**fitness_metrics (Dict):**
```json
{
  "improvement": 22.5,
  "records_at_target": 45,
  "records_fixed": 45,
  "average_improvement_per_record": 2.1
}
```

## Error Handling

All endpoints return error responses in this format:
```json
{
  "error": "Error message",
  "type": "ErrorType"
}
```

Implement in Flutter:
```dart
try {
  final result = await _apiService.runGeneticAlgorithmEvolution(...);
  
  if (!result['success']) {
    throw Exception(result['error']);
  }
  
  // Process results
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Error: $e')),
  );
}
```

## Performance Tips

1. **Batch Size**: Keep evolution data < 10,000 records for responsive UI
2. **Population Size**: Start with 20-30, increase for more accuracy
3. **Generations**: 50-100 for quick tests, 200+ for production
4. **Progress**: Use `trackProgress: true` for real-time updates
5. **Timeout**: Set appropriate timeout for long-running evolutions

## Testing with Postman

Import the included Postman collection:
```
FastMig_ModifiedByAI_Tests.postman_collection.json
```

Sequence:
1. Upload test data
2. POST /ga/analyze-population
3. POST /ga/select-populations
4. POST /ga/run-evolution
5. POST /ga/export-evolved

## Common Issues & Solutions

### Issue: No data loaded
**Solution:** Always upload data first via `/upload` endpoint

### Issue: Invalid GA config
**Solution:** Ensure all required fields are provided in gaConfig

### Issue: Timeout
**Solution:** Increase timeout values for large datasets or many generations

### Issue: No evolved data to export
**Solution:** Run evolution via `/ga/run-evolution` before exporting

## Quick Reference: Required Parameters by Endpoint

| Endpoint | Required Params | Optional Params |
|----------|-----------------|-----------------|
| `/ga/analyze-population` | fitness_threshold | - |
| `/ga/select-populations` | fitness_threshold | healthy_sample_size |
| `/ga/run-evolution` | population_size, generations, mutation_rate, crossover_rate | All GA config params |
| `/ga/quick-evolve` | fitness_threshold | population_size, generations, save_result |
| `/ga/export-evolved` | filename, format | - |

## Next Steps

1. Update `api_service.dart` with the method implementations
2. Test each endpoint individually
3. Integrate into the GA evolution screen
4. Display results in the visualization widgets
5. Add download functionality for evolved data
