# FastMig GA Frontend - Visual Architecture Overview

## Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    FastMig Main Screen                       │
│                                                              │
│  [Load] [Convert] [ETL] [Record] [Fitness] [AI] [GA] [Exp]│
│                                                        ↑     │
│                                                   [NEW]      │
└────────────────────────────────────┬──────────────────────────┘
                                     │
                    ┌────────────────▼──────────────────┐
                    │   GA Evolution Screen (Full)      │
                    └────────────────┬──────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
    ┌────────────┐            ┌──────────────┐          ┌─────────────┐
    │ Config Tab │            │ Progress Tab │          │ Results Tab │
    ├────────────┤            ├──────────────┤          ├─────────────┤
    │ GA Params  │            │ Progress Bar │          │ Tree View   │
    │ Grammar    │            │ Metrics Grid │          │ Analysis    │
    │ Presets    │            │ Fitness Chart│          │ Stats       │
    └────────────┘            └──────────────┘          └─────────────┘
```

## Component Hierarchy

```
GAEvolutionScreen
├── AppBar
│   └── TabBar (4 tabs)
│       ├── Tab 0: "Configuration"
│       ├── Tab 1: "Progress"
│       ├── Tab 2: "Expression Tree"
│       └── Tab 3: "Analysis"
│
├── TabBarView
│   ├── View 0: Configuration
│   │   ├── DefaultTabController
│   │   │   ├── Tab 0.0: GAConfigurationPanel
│   │   │   └── Tab 0.1: GrammarRuleSelectionPanel
│   │   ├── Configuration Summary Card
│   │   └── Start Evolution Button
│   │
│   ├── View 1: Progress
│   │   └── GAProgressVisualization
│   │       ├── Header with status icon
│   │       ├── Progress bar
│   │       ├── Metrics Grid
│   │       │   ├── Generation card
│   │       │   ├── Best fitness card
│   │       │   ├── Avg fitness card
│   │       │   └── Population card
│   │       ├── Fitness Chart (CustomPaint)
│   │       └── Metrics Table
│   │
│   ├── View 2: Expression Tree
│   │   └── ExpressionTreeVisualization
│   │       ├── Header with title & fitness
│   │       ├── InteractiveViewer
│   │       │   └── CustomPaint (TreePainter)
│   │       │       └── Tree rendering with nodes
│   │       └── Node Details Panel
│   │
│   └── View 3: Analysis
│       ├── Error display
│       ├── Fitness analysis cards
│       │   ├── Unhealthy records
│       │   └── Healthy records
│       └── Statistics table
```

## Data Flow Diagram

```
User Input
    │
    ├─→ GAConfigurationPanel
    │   └─→ _gaConfig: GAConfigModel
    │
    ├─→ GrammarRuleSelectionPanel
    │   └─→ _grammarConfig: GrammarConfigModel
    │
    └─→ [Start Evolution] Button
        │
        ▼
    _startEvolution()
        │
        ├─→ apiService.runGeneticAlgorithmEvolution()
        │   │
        │   └─→ Backend: POST /ga/evolve
        │       │
        │       ▼
        │   Response
        │       ├─→ evolved_data: List<List>
        │       ├─→ fitness_history: List<Map>
        │       ├─→ expression_tree: Map
        │       └─→ convergence_info: Map
        │
        ├─→ Parse fitness_history
        │   └─→ _metricsHistory: List<GAMetricsModel>
        │
        ├─→ Parse expression_tree
        │   └─→ _bestExpressionTree: ExpressionTreeNode
        │
        └─→ setState() → Render Visualizations
            │
            ├─→ Progress Tab
            │   └─→ GAProgressVisualization (metrics_history)
            │
            ├─→ Expression Tree Tab
            │   └─→ ExpressionTreeVisualization (best_tree)
            │
            └─→ Analysis Tab
                └─→ Fitness statistics display
```

## Widget Communication Pattern

```
GAEvolutionScreen (State Manager)
    │
    ├─→ GAConfigurationPanel
    │   │   onConfigChanged(config)
    │   └─→ setState(() => _gaConfig = config)
    │
    ├─→ GrammarRuleSelectionPanel
    │   │   onConfigChanged(config)
    │   └─→ setState(() => _grammarConfig = config)
    │
    ├─→ GAProgressVisualization
    │   │   metricsHistory: _metricsHistory
    │   │   isRunning: _isEvolving
    │   │   progressPercent: _evolutionProgress
    │   │   onStop: _stopEvolution()
    │   └─→ [Read-only data display]
    │
    └─→ ExpressionTreeVisualization
        │   rootNode: _bestExpressionTree
        │   fitnessScore: _metricsHistory.last.bestFitness
        │   isLoading: _isEvolving
        │   errorMessage: _errorMessage
        └─→ [Read-only data display]
```

## State Management Model

```
┌─────────────────────────────────────┐
│  GAEvolutionScreen State            │
├─────────────────────────────────────┤
│ _gaConfig: GAConfigModel            │ ← User configures GA
│ _grammarConfig: GrammarConfigModel  │ ← User configures Grammar
│ _isEvolving: bool                   │ ← Evolution running status
│ _evolutionProgress: double          │ ← Progress 0.0-1.0
│ _metricsHistory: List<GAMetricsModel>│ ← Generation metrics
│ _bestExpressionTree: ExpressionTreeNode│ ← Best evolved tree
│ _fitnessAnalysis: Map               │ ← Population analysis
│ _errorMessage: String?              │ ← Error display
└─────────────────────────────────────┘
        │
        │ setState()
        ▼
    UI Rebuild
    └─→ All child widgets re-render with new data
```

## Configuration Parameter Ranges

```
┌──────────────────────────────────────────┐
│  GAConfigModel - Valid Ranges            │
├──────────────────────────────────────────┤
│ populationSize      │  20 - 200          │
│ generations         │  10 - 1000         │
│ mutationRate        │  0.0 - 1.0         │
│ crossoverRate       │  0.0 - 1.0         │
│ eliteCount          │  1 - populationSize│
│ earlyStoppingPatience│ 1 - 50           │
│ fitnessThreshold    │  0.0 - 100.0      │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  GAConfigModel - Discrete Options        │
├──────────────────────────────────────────┤
│ selectionMethod:                         │
│   • tournament                           │
│   • roulette_wheel                       │
│   • rank_based                           │
│                                          │
│ crossoverMethod:                         │
│   • single_point                         │
│   • two_point                            │
│   • uniform                              │
│   • arithmetic                           │
│                                          │
│ mutationMethod:                          │
│   • gaussian                             │
│   • uniform                              │
│   • adaptive                             │
└──────────────────────────────────────────┘
```

## Preset Configurations

```
┌─────────────────────────────────────────────────────┐
│                FAST Preset                          │
├─────────────────────────────────────────────────────┤
│ Population: 20  │  Generations: 30                  │
│ Mutation: 15%   │  Crossover: 75%                   │
│ Early Stopping Patience: 5                          │
│ Result: Quick results in ~1-2 minutes               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              BALANCED Preset (Default)              │
├─────────────────────────────────────────────────────┤
│ Population: 30  │  Generations: 100                 │
│ Mutation: 10%   │  Crossover: 80%                   │
│ Early Stopping Patience: 10                         │
│ Result: Good quality in ~5-10 minutes               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│               QUALITY Preset                        │
├─────────────────────────────────────────────────────┤
│ Population: 50  │  Generations: 200                 │
│ Mutation: 8%    │  Crossover: 85%                   │
│ Early Stopping Patience: 15                         │
│ Result: Best quality in ~20-30 minutes              │
└─────────────────────────────────────────────────────┘
```

## Grammar Presets

```
STANDARD
├─ <expr> ::= <expr> + <term> | <expr> - <term> | <term>
├─ <term> ::= <term> * <factor> | <term> / <factor> | <factor>
├─ <factor> ::= ( <expr> ) | <number>
└─ <number> ::= 0-9

BOOLEAN
├─ <expr> ::= <expr> AND <term> | <expr> OR <term> | <term>
├─ <term> ::= NOT <term> | <comparison>
├─ <comparison> ::= <value> > <value> | <value> < <value> | <value> = <value>
└─ <value> ::= x | y | z

TRIGONOMETRIC
├─ <expr> ::= sin(<expr>) | cos(<expr>) | tan(<expr>) | <base>
├─ <base> ::= x | pi | e | <number>
└─ <number> ::= 0.1 | 0.5 | 1.0 | 2.0 | 3.0

DATA_CLEANING
├─ <operation> ::= <filter> | <transform> | <aggregate>
├─ <filter> ::= filter_null | filter_outliers | filter_duplicates
├─ <transform> ::= normalize | standardize | encode
└─ <aggregate> ::= sum | mean | median | mode

STATISTICAL
├─ <expr> ::= mean(<data>) | std(<data>) | median(<data>) | <stat>
├─ <stat> ::= variance | skewness | kurtosis
└─ <data> ::= column1 | column2 | column3
```

## Visualization Pipeline

```
                 Evolution Running
                      │
                      ▼
        ┌─────────────────────────┐
        │ Progress Visualization  │
        ├─────────────────────────┤
        │ ┌─────────────────────┐ │
        │ │ Progress Bar        │ │  Real-time
        │ │ [████████░░░░░░]75% │ │  feedback
        │ └─────────────────────┘ │
        │ ┌────┬────┬────┬────┐   │
        │ │Gen │Best│Avg │Pop │   │  Metrics
        │ │ 87 │92.5│78.3│ 30│   │  cards
        │ └────┴────┴────┴────┘   │
        │                         │
        │  ▲                       │
        │  │                       │  Fitness
        │ ▲│▲▲  ▲                  │  chart
        │  │ ││   ▲ ▲              │
        │ ─┼─┼┼───┼─┼──            │
        │ ─ ─ ─   ─ ─              │
        │                         │
        │ Gen│Best│Worst│Avg│Var │  Metrics
        │ ─── ─── ─── ─── ─── ─   │  table
        │ 85 │92.5│42.1│78.3│...  │
        │ 86 │93.2│45.3│79.1│...  │
        │ 87 │94.1│46.8│80.2│...  │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │ Best Expression Tree    │
        ├─────────────────────────┤
        │           ○             │
        │          /|\            │
        │         ○ ○ ○           │  Interactive
        │        /| | |\          │  tree with
        │       ○ ○ ○ ○ ○         │  zoom/pan
        │      /| | | | |\        │
        │     ○ ○ ○ ○ ○ ○ ○       │
        │                         │
        │ Node Details:           │
        │ Value: +                │
        │ Type: operator          │  Selected
        │ Children: 2             │  node info
        │ Fitness: 0.95           │
        └─────────────────────────┘
```

## Error Handling Flow

```
                    API Call
                        │
                ┌───────┴────────┐
                ▼                ▼
            Success           Error
                │                │
                ├─→ Parse        └─→ Catch Exception
                │   Response         │
                ├─→ Update State    ├─→ setState()
                │                   │   _errorMessage = error
                ├─→ Render          ├─→ Log error
                │   Results         │
                └─→ Show SnackBar   ├─→ Show SnackBar
                    (Green)         │   (Red)
                                   └─→ Display error
                                      in Error Panel
```

## File Size Summary

```
┌─────────────────────────────────────────┐
│          Code Size Summary              │
├─────────────────────────────────────────┤
│ ga_config_model.dart          ~ 320 ln  │
│ ga_configuration_panel.dart   ~ 320 ln  │
│ ga_progress_visualization.dart~ 400 ln  │
│ grammar_rule_selection_panel.dart~ 350 ln
│ expression_tree_visualization.dart~ 450 ln
│ ga_evolution_screen.dart      ~ 500 ln  │
│ ─────────────────────────────────────── │
│ Total Production Code         ~ 2,500 ln
│ ─────────────────────────────────────── │
│ Documentation                 ~ 2,000 ln
│ ─────────────────────────────────────── │
│ Grand Total                   ~ 4,500 ln
└─────────────────────────────────────────┘
```

## Integration Points

```
FastMig System
├─ Frontend (Flutter)
│  ├─ Main Screen
│  │  └─ GA Evolution Button [NEW]
│  │
│  ├─ GA Evolution Screen [NEW]
│  │  ├─ GAConfigurationPanel [NEW]
│  │  ├─ GAProgressVisualization [NEW]
│  │  ├─ GrammarRuleSelectionPanel [NEW]
│  │  └─ ExpressionTreeVisualization [NEW]
│  │
│  └─ API Service
│     ├─ runGeneticAlgorithmEvolution() [NEW]
│     ├─ getGAProgress() [NEW]
│     ├─ analyzePopulationFitness() [NEW]
│     ├─ getGrammarPresets() [NEW]
│     └─ parseExpressionTree() [NEW]
│
├─ Backend (Python)
│  ├─ POST /ga/evolve
│  ├─ GET /ga/progress
│  ├─ POST /ga/analyze-fitness
│  ├─ GET /ga/grammar-presets
│  └─ POST /ga/parse-tree
│
└─ Database
   └─ Results & metrics storage
```

## User Interaction Flow

```
┌──────────────────────────────────────────┐
│ 1. User Navigates to GA Evolution       │
├──────────────────────────────────────────┤
│ Main Screen → Click "GA Evolution"       │
│           ↓                              │
│ Navigate to full GA Evolution Screen     │
└──────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│ 2. User Configures GA Parameters        │
├──────────────────────────────────────────┤
│ Choose Preset OR Set Manually            │
│   • Fast / Balanced / Quality            │
│   • Adjust Population, Generations, etc. │
│   • Configure Convergence Settings      │
└──────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│ 3. User Selects Grammar                 │
├──────────────────────────────────────────┤
│ Choose Grammar Type:                     │
│   • Standard / Boolean / Trig / etc.    │
│   • Add Custom Rules (optional)         │
│   • Set Max Depth                       │
└──────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│ 4. User Starts Evolution                │
├──────────────────────────────────────────┤
│ Click "Start Evolution"                  │
│   ↓                                      │
│ Switch to Progress Tab                  │
│   ↓                                      │
│ Display Progress Bar & Metrics          │
│   ↓                                      │
│ Update Chart in Real-time               │
└──────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────┐
│ 5. User Views Results                   │
├──────────────────────────────────────────┤
│ After Evolution Completes:               │
│   ↓                                      │
│ Switch to Expression Tree Tab            │
│   ↓                                      │
│ Explore Best Solution Tree               │
│   ↓                                      │
│ View Population Analysis                 │
└──────────────────────────────────────────┘
```

---

**Visual Architecture Overview Complete**
**Status: Ready for Reference**
**Last Updated: December 19, 2025**
