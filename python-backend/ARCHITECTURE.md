# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FastMig Backend Architecture                         │
│                              with Evolutionary Cleaning                       │
└─────────────────────────────────────────────────────────────────────────────┘

                                   CLIENT
                                     │
                          ┌──────────┴──────────┐
                          │   HTTP Requests     │
                          └──────────┬──────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              server.py (Flask)                               │
│  ┌────────────────────┬──────────────────────┬──────────────────────────┐  │
│  │  Original Routes   │   Fitness Routes     │  Evolutionary Routes     │  │
│  │                    │                      │                          │  │
│  │  /upload           │  /fitness/evaluate   │  /clean/evolutionary     │  │
│  │  /process          │  /fitness/record/:id │  /clean/compare          │  │
│  │  /export           │                      │  /data/restore           │  │
│  │  /columns          │                      │                          │  │
│  └────────┬───────────┴──────────┬───────────┴──────────┬───────────────┘  │
│           │                      │                      │                   │
│           ▼                      ▼                      ▼                   │
│  ┌──────────────┐      ┌────────────────────┐  ┌────────────────────────┐ │
│  │ functions.py │      │  data_fitness.py   │  │  current_data (dict)   │ │
│  │              │      │                    │  │  - df: DataFrame       │ │
│  │ - read_file  │      │ DataFitness        │  │  - df_original: backup │ │
│  │ - convert    │      │ Evaluator          │  │  - file_path           │ │
│  │ - export     │      │                    │  │                        │ │
│  └──────────────┘      └────────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                       data_fitness.py Module Details                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                        DataFitnessEvaluator                                │
├───────────────────────────────────────────────────────────────────────────┤
│  Input: DataFrame                                                          │
│                                                                            │
│  ┌──────────────────────┐                                                 │
│  │ _infer_column_types()│  ──→  {col: 'integer', 'float', 'string', ...}│
│  └──────────────────────┘                                                 │
│                                                                            │
│  ┌──────────────────────────┐                                             │
│  │_calculate_distributions()│  ──→  {col: {mean, std, quartiles, ...}}   │
│  └──────────────────────────┘                                             │
│                                                                            │
│  ┌──────────────────────────┐                                             │
│  │evaluate_record_fitness() │  ──→  {overall: 85%, issues: [...]}        │
│  │                          │       ├─ missing_score (40% weight)         │
│  │  For each record:        │       ├─ type_consistency (30% weight)     │
│  │  1. Count missing        │       └─ sqlite_compat (30% weight)        │
│  │  2. Check type errors    │                                             │
│  │  3. Validate SQLite      │                                             │
│  └──────────────────────────┘                                             │
│                                                                            │
│  Output: Fitness scores + health status                                   │
└───────────────────────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────────────┐
│                       EvolutionaryDataCleaner                              │
├───────────────────────────────────────────────────────────────────────────┤
│  Input: DataFrame with missing/inconsistent data                          │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │               Select Evolutionary Algorithm                          │ │
│  ├─────────────┬──────────────┬──────────────┬──────────┬──────────────┤ │
│  │             │              │              │          │              │ │
│  │     GA      │     PSO      │      DE      │    ES    │   HYBRID     │ │
│  │             │              │              │          │              │ │
│  └──────┬──────┴──────┬───────┴──────┬───────┴────┬─────┴──────┬───────┘ │
│         │             │              │            │            │         │
│         ▼             ▼              ▼            ▼            ▼         │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    EVOLUTIONARY PROCESS                              │ │
│  │                                                                      │ │
│  │  1. Initialize Population                                           │ │
│  │     └─→ Sample from existing data                                   │ │
│  │                                                                      │ │
│  │  2. Evaluate Fitness                                                │ │
│  │     ├─→ KS Test (distribution similarity)                           │ │
│  │     ├─→ Statistical properties (mean, std)                          │ │
│  │     └─→ Value similarity                                            │ │
│  │                                                                      │ │
│  │  3. Apply Operators                                                 │ │
│  │     ├─→ Selection (tournament, roulette, etc.)                      │ │
│  │     ├─→ Crossover (single-point, uniform)                           │ │
│  │     ├─→ Mutation (Gaussian, swap)                                   │ │
│  │     └─→ Velocity/Differential updates (PSO/DE)                      │ │
│  │                                                                      │ │
│  │  4. Iterate Until Convergence                                       │ │
│  │     └─→ Max generations or fitness threshold                        │ │
│  │                                                                      │ │
│  │  5. Select Best Solution                                            │ │
│  │     └─→ Highest fitness score                                       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                     │                                      │
│                                     ▼                                      │
│  Output: Cleaned DataFrame with imputed values                            │
│          + Report (before/after fitness, improvement)                     │
└───────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                           Data Flow Example                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Upload
──────────────
Client uploads CSV ──→ /upload ──→ Store in current_data['df']
                                   │
                                   └─→ Return first 100 rows + metadata

Step 2: Evaluate Fitness
────────────────────────
Client requests ──→ /fitness/evaluate ──→ DataFitnessEvaluator
                                          │
                                          ├─→ Score each record
                                          ├─→ Calculate statistics
                                          └─→ Return summary + details

Step 3: Clean Data
──────────────────
Client requests ──→ /clean/evolutionary ──→ EvolutionaryDataCleaner
  with method       │                        │
  e.g., "hybrid"    │                        ├─→ Run algorithm
                    │                        ├─→ Impute missing values
                    │                        └─→ Evaluate improvement
                    │
                    └─→ Update current_data['df']
                        Store backup in current_data['df_original']
                        Return cleaned data + report

Step 4: Export
─────────────
Client requests ──→ /export ──→ Write current_data['df'] to file
                                │
                                └─→ Return file path


┌─────────────────────────────────────────────────────────────────────────────┐
│                         Fitness Scoring Breakdown                            │
└─────────────────────────────────────────────────────────────────────────────┘

Record: [id=1, name="John", age=NULL, salary=50000, dept="IT"]

Missing Score (40% weight)
├─ Total columns: 5
├─ Missing columns: 1 (age)
├─ Missing rate: 1/5 = 20%
└─ Score: 100 - 20 = 80%

Type Consistency Score (30% weight)
├─ Check each value against expected type
├─ All values match expected types
└─ Score: 100%

SQLite Compatibility Score (30% weight)
├─ No NULL characters
├─ No integer overflow
├─ No invalid floats
└─ Score: 100%

Overall Fitness = (80 × 0.4) + (100 × 0.3) + (100 × 0.3)
                = 32 + 30 + 30
                = 92%  →  Health Status: "Good"


┌─────────────────────────────────────────────────────────────────────────────┐
│                      Algorithm Comparison Matrix                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────┬─────────────┬──────────────┬────────────┬─────────────────┐
│ Algorithm  │  Best For   │  Speed       │  Accuracy  │  Use Case       │
├────────────┼─────────────┼──────────────┼────────────┼─────────────────┤
│ GA         │  Mixed      │  ███░░       │  ████░     │  General        │
│ PSO        │  Numeric    │  ████░       │  █████     │  Continuous     │
│ DE         │  Complex    │  ███░░       │  █████     │  Distributions  │
│ ES         │  Reliable   │  ██░░░       │  ████░     │  Consistency    │
│ HYBRID ⭐  │  Everything │  █████       │  █████     │  Recommended    │
└────────────┴─────────────┴──────────────┴────────────┴─────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                           File Structure                                     │
└─────────────────────────────────────────────────────────────────────────────┘

python-backend/
│
├── Core Server
│   ├── server.py                    ★ Main Flask application
│   ├── functions.py                 ○ Data processing utilities
│   └── app.py                       ○ Entry point
│
├── NEW: Evolutionary Module
│   ├── data_fitness.py              ★★★ Core fitness & cleaning
│   ├── test_evolutionary_cleaning.py   ○ Test suite
│   └── example_client.py               ○ Example usage
│
├── Documentation
│   ├── EVOLUTIONARY_CLEANING_GUIDE.md  ○ Complete guide
│   ├── QUICK_REFERENCE.md              ○ Quick start
│   ├── IMPLEMENTATION_SUMMARY.md       ○ This summary
│   └── README.md                       ★ Updated overview
│
├── Configuration
│   └── requirements.txt               ★ Updated dependencies
│
└── Data Storage
    └── uploads/                       ○ Uploaded files

Legend: ★ = Modified/Important, ○ = New/Reference


┌─────────────────────────────────────────────────────────────────────────────┐
│                         Success Indicators                                   │
└─────────────────────────────────────────────────────────────────────────────┘

✅ Module loads without errors
✅ Server starts successfully
✅ All endpoints respond correctly
✅ Fitness evaluation works
✅ All 5 algorithms execute
✅ Distribution preservation verified (KS test)
✅ Statistical properties maintained
✅ SQLite compatibility validated
✅ Test suite passes
✅ Example client works

Status: PRODUCTION READY ✅
```
