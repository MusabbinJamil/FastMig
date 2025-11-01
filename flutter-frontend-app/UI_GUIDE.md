# UI Screenshots Guide

## Navigation

### Side Menu - Updated

```
┌─────────────────────────────────┐
│ ⚡ FastMig                      │
│    Data Migration               │
├─────────────────────────────────┤
│                                 │
│ 📁  Load Data                   │
│ 🔄  Convert Fields              │
│ ⏺   Record Macro                │
│ 📊  View Data                   │
│ ⬇️  Export Data                 │
│ ─────────────────────────────── │
│ AI FEATURES                     │
│ 🏥  Data Fitness           ← NEW│
│ ✨  AI Cleaning            ← NEW│
│ ─────────────────────────────── │
│ ⚙️  Settings                    │
│ ❓  Help                        │
│                                 │
├─────────────────────────────────┤
│ ✅ Backend Connected            │
└─────────────────────────────────┘
```

## Data Fitness Screen

### Layout

```
┌────────────────────────────────────────────────────────────────┐
│ 🏥 Data Fitness Evaluation                   [Evaluate Fitness]│
│    Assess the health and quality of your data                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Fitness Summary                                                │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│ │ 📈 87.50%    │  │ 📊 1000      │  │ ⚠️  350      │        │
│ │ Average      │  │ Total        │  │ Need         │        │
│ │ Fitness      │  │ Records      │  │ Cleaning     │        │
│ └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
│ Health Status Breakdown                                        │
│ Excellent ████████████████████░░░░░░ 650 (65.0%)              │
│ Good      ████████░░░░░░░░░░░░░░░░░ 200 (20.0%)              │
│ Fair      ████░░░░░░░░░░░░░░░░░░░░░ 100 (10.0%)              │
│ Poor      ██░░░░░░░░░░░░░░░░░░░░░░░  40 (4.0%)               │
│ Critical  ░░░░░░░░░░░░░░░░░░░░░░░░░  10 (1.0%)               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## AI Cleaning Screen

### Method Selection

```
┌────────────────────────────────────────────────────────────────┐
│ ✨ Evolutionary Data Cleaning                                  │
│    Use AI algorithms to intelligently clean and impute values  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ Select Cleaning Method                                         │
│                                                                │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│ │ ✨ ✓        │  │ 🧬          │  │ 📍          │           │
│ │             │  │             │  │             │           │
│ │ Hybrid      │  │ Genetic     │  │ Particle    │           │
│ │ (Recommended)│ │ Algorithm   │  │ Swarm       │           │
│ │             │  │             │  │             │           │
│ │ Auto-selects │  │ Evolves     │  │ Best for    │           │
│ │ best algo   │  │ populations │  │ numeric     │           │
│ └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                │
│ ┌─────────────┐  ┌─────────────┐                             │
│ │ 📐          │  │ 📊          │                             │
│ │ Differential│  │ Evolution   │                             │
│ │ Evolution   │  │ Strategy    │                             │
│ └─────────────┘  └─────────────┘                             │
│                                                                │
│ ☑ Track AI Modifications                                      │
│   Add "Modified_by_AI" column to track changes                │
│                                                                │
│ [🧹 Clean Data]  [⚖️ Compare Methods]                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Cleaning Report

```
┌────────────────────────────────────────────────────────────────┐
│ Cleaning Report                                                │
│                                                                │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐│
│ │ ❌ Before   │  │ ✅ After    │  │ 📈 Improve  │  │ 🤖 AI  ││
│ │             │  │             │  │             │  │ Modified││
│ │ 75.50%      │  │ 96.80%      │  │ +21.30%     │  │ 23 recs ││
│ │ 25 issues   │  │ 2 issues    │  │ 23 fixed    │  │ 23.00% ││
│ └─────────────┘  └─────────────┘  └─────────────┘  └────────┘│
└────────────────────────────────────────────────────────────────┘
```

### Method Comparison Dialog

```
┌────────────────────────────────────────────────────────────────┐
│ Method Comparison Results                                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ 🏆 Best Method: Hybrid (Recommended)                           │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 🧬 Genetic Algorithm                                      │  │
│ │    Improvement: 16.80% • 200 records fixed                │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 📍 Particle Swarm Optimization                            │  │
│ │    Improvement: 18.60% • 220 records fixed                │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 📐 Differential Evolution                                 │  │
│ │    Improvement: 18.20% • 215 records fixed                │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 📊 Evolution Strategy                                     │  │
│ │    Improvement: 16.30% • 195 records fixed                │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ ✨ Hybrid (Recommended)                           [BEST] │  │
│ │    Improvement: 21.30% • 235 records fixed                │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│                                [Close]  [Use Best Method]     │
└────────────────────────────────────────────────────────────────┘
```

## Workflow Screen

### 3-Step Process

```
┌────────────────────────────────────────────────────────────────┐
│ AI Data Quality Workflow                                       │
│ Follow these steps to evaluate and improve your data quality   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│    ●────────────●────────────●                                │
│    │            │            │                                │
│    1            2            3                                │
│ Evaluate    Clean Data   Verify &                             │
│ Fitness                  Export                               │
│                                                                │
│ Current Step: 1. Evaluate Fitness                             │
│                                                                │
│ [Fitness Evaluation Section Content Here]                     │
│                                                                │
│                                   [Proceed to Cleaning →]     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Verify Step

```
┌────────────────────────────────────────────────────────────────┐
│ ✅ Verify & Export                                             │
│    Review your cleaned data and export when ready              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 📊  Data Preview                                        →│  │
│ │     View your cleaned data in the View Data section      │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 🏥  Re-evaluate Fitness                                 →│  │
│ │     Check the improved fitness scores after cleaning     │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ ⬇️  Export Data                                          →│  │
│ │     Save your cleaned data to file                       │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ 🔄  Restore Original                                     →│  │
│ │     Undo changes and restore original data               │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                │
│ [← Back to Cleaning]                                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Fitness Colors
- 🟢 Green (95-100%): Excellent
- 🟢 Light Green (80-95%): Good
- 🟠 Orange (60-80%): Fair
- 🟠 Deep Orange (40-60%): Poor
- 🔴 Red (0-40%): Critical

### Method Colors
- 🟣 Purple: Hybrid
- 🟢 Green: Genetic Algorithm
- 🔵 Blue: Particle Swarm
- 🟠 Orange: Differential Evolution
- 🔵 Teal: Evolution Strategy

### Status Colors
- 🔵 Blue: Information, Active
- 🟢 Green: Success, Completed
- 🟠 Orange: Warning, Needs Attention
- 🔴 Red: Error, Critical
- ⚫ Grey: Inactive, Disabled

## Icons Reference

### Main Features
- 📁 Load Data
- 🔄 Convert Fields
- ⏺ Record Macro
- 📊 View Data
- ⬇️ Export Data
- 🏥 Data Fitness
- ✨ AI Cleaning
- ⚙️ Settings
- ❓ Help

### Actions
- ▶️ Start/Play
- ⏸ Pause
- ⏹ Stop
- 🔄 Refresh/Reload
- ✅ Confirm/Success
- ❌ Cancel/Error
- ⚠️ Warning
- 📈 Trending Up
- 📉 Trending Down
- 🧹 Clean
- ⚖️ Compare
- 🔙 Back
- ➡️ Forward

### Status
- 🟢 Connected/Good
- 🔴 Disconnected/Bad
- 🟡 Processing/Warning
- ⚪ Neutral/Inactive

## Responsive Breakpoints

### Desktop (>1200px)
- Side menu: 250px fixed width
- Content area: Remaining space
- Cards: Full width with padding

### Tablet (768px - 1200px)
- Side menu: Collapsible
- Content area: Full width when menu hidden
- Cards: Stacked vertically

### Mobile (<768px)
- Bottom navigation instead of side menu
- Single column layout
- Compact cards

## Accessibility

### Features
- Clear color contrast
- Icon + text labels
- Keyboard navigation
- Screen reader support
- Focus indicators
- Large touch targets (48px minimum)

### ARIA Labels
- All buttons have descriptive labels
- Progress bars show percentage
- Status indicators have text alternatives
- Error messages are announced

## Animation & Transitions

### Timing
- Fast (200ms): Button hovers, icon changes
- Medium (300ms): Card expansions, color changes
- Slow (600ms): Screen transitions, content slides

### Effects
- Slide transitions between screens
- Fade in/out for content
- Scale on button press
- Smooth color transitions
- Progress bar animations

## Loading States

### Indicators
```
┌────────────────────────────────┐
│ [⏳ Evaluating...]             │
│ [⏳ Cleaning...]               │
│ [⏳ Comparing...]              │
│ [⏳ Loading...]                │
└────────────────────────────────┘
```

### Buttons
```
[🔄 Processing...]  (disabled, with spinner)
[✨ Clean Data]     (enabled, ready)
[⏳ Cleaning...]    (processing)
```

## Error States

### Messages
```
┌────────────────────────────────────────┐
│ ❌ Error                               │
│                                        │
│ Failed to evaluate fitness:            │
│ No data loaded. Please upload a file  │
│ first.                                 │
│                                        │
│                            [OK]        │
└────────────────────────────────────────┘
```

### Inline Errors
```
⚠️ No data loaded. Please load data first to use this feature.
```

## Success States

### Snackbar
```
┌────────────────────────────────────────┐
│ ✅ Data cleaned successfully!          │
│    Fitness improved by 21.30%          │
└────────────────────────────────────────┘
```

### Inline Success
```
✅ Data cleaned successfully! 23 records fixed.
```

---

This guide provides a visual reference for all UI elements in the AI features implementation.
