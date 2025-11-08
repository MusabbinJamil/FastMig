# Side Panel Layout Guide

## Overview

The FastMig UI now uses a **split-screen side panel** layout instead of modal overlays. This means your data is always visible alongside the feature you're working with.

## Layout Breakdown

### Without Side Panel (Default View)
```
┌─────────────────────────────────────────────────────┐
│  HEADER BAR (Top Ribbon)                            │
├─────────────────────────────────────────────────────┤
│                                                      │
│                  DATA TABLE                          │
│                  (100% WIDTH)                        │
│                                                      │
│              [All your data visible]                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### With Side Panel Open
```
┌─────────────────────────────────────────────────────┐
│  HEADER BAR (Top Ribbon)                            │
├──────────────────────────┬──────────────────────────┤
│                          │                          │
│    DATA TABLE            │    FEATURE PANEL         │
│    (60% WIDTH)           │    (40% WIDTH)           │
│                          │                          │
│  [Your data stays        │  [Feature controls       │
│   fully visible and      │   and interface]         │
│   interactive]           │                          │
│                          │                          │
└──────────────────────────┴──────────────────────────┘
```

## Width Distribution

| State | Data Table | Side Panel | Total |
|-------|-----------|------------|-------|
| **No Panel** | 100% | - | 100% |
| **Panel Open** | 60% | 40% | 100% |

The data table is set to `flex: 6` and the side panel to `flex: 4`, creating a 60/40 split.

## Side Panel Features

### Header
- Icon with feature color
- Feature title
- Close button (X)

### Content Area
- Full feature interface
- Scrollable if needed
- All controls accessible

### Behavior
- Opens from right side
- Slides in smoothly
- Data table automatically resizes
- Close button returns to full-width view

## Visual Example

### Example 1: Load Data Panel Open
```
┌──────────────────────────────────────────────────────────────┐
│ ⚡ FastMig  [No file]                            ❓          │
├───────────────────────────┬──────────────────────────────────┤
│                           │  📤 Load Data                  ✕ │
│  😄 No Data - Fun Data!   │  ────────────────────────────────│
│  ─────────────────────    │                                  │
│  Superhero  │ Power       │  📁 Select File                  │
│  ──────────┼──────        │  ┌────────────────────────┐     │
│  Captain   │ 9001         │  │ Browse...              │     │
│  Debugger  │ ∞            │  └────────────────────────┘     │
│  Coffee    │ Unlimited    │                                  │
│  ──────────┴──────        │  Supported Formats:              │
│                           │  • CSV, Excel, JSON, XML         │
│  [Can scroll data]        │                                  │
│                           │  [Load Button]                   │
└───────────────────────────┴──────────────────────────────────┘
```

### Example 2: Convert Fields Panel Open
```
┌──────────────────────────────────────────────────────────────┐
│ ⚡ FastMig  [mydata.csv]                         ❓          │
├───────────────────────────┬──────────────────────────────────┤
│                           │  🔄 Convert Fields             ✕ │
│  Name     │ Age │ Salary  │  ────────────────────────────────│
│  ─────────┼─────┼────────  │                                  │
│  John     │ 25  │ 50000   │  Select Column:                  │
│  Jane     │ 30  │ 60000   │  ┌────────────────────────┐     │
│  Bob      │ 35  │ 70000   │  │ Age ▼                  │     │
│  Alice    │ 28  │ 55000   │  └────────────────────────┘     │
│  ─────────┴─────┴────────  │                                  │
│                           │  Convert To:                     │
│  [Data visible while      │  ● Integer                       │
│   converting columns]     │  ○ String                        │
│                           │  ○ Float                         │
│                           │                                  │
│                           │  [Convert Button]                │
└───────────────────────────┴──────────────────────────────────┘
```

### Example 3: ETL Operations Panel Open
```
┌──────────────────────────────────────────────────────────────┐
│ ⚡ FastMig  [sales.csv]                          ❓          │
├───────────────────────────┬──────────────────────────────────┤
│                           │  ✨ ETL Operations             ✕ │
│  Product│Qty│Price│Region │  ────────────────────────────────│
│  ───────┼───┼─────┼────── │                                  │
│  Laptop │ 5 │ 1200│ North │  Operation:                      │
│  Mouse  │10 │   25│ South │  ┌────────────────────────┐     │
│  Laptop │ 3 │ 1200│ North │  │ Remove Duplicates ▼    │     │
│  Keyboard│8 │   45│ East  │  └────────────────────────┘     │
│  ───────┴───┴─────┴────── │                                  │
│                           │  Settings:                       │
│  [See which rows will be  │  ☑ Based on all columns          │
│   affected by operation]  │  ☐ Keep first occurrence         │
│                           │  ☑ Keep last occurrence          │
│                           │                                  │
│                           │  [Apply Operation]               │
└───────────────────────────┴──────────────────────────────────┘
```

## Advantages of Side Panel Design

### ✅ Always See Your Data
- Data table never hidden
- Watch changes in real-time
- Reference data while configuring

### ✅ Better Workflow
- No context switching
- Compare before/after side-by-side
- Verify selections instantly

### ✅ More Professional
- Modern split-screen interface
- Similar to VS Code, Figma, etc.
- Intuitive for users

### ✅ Flexible
- Panel closes to give full width
- Data table adjusts automatically
- Responsive design

## Code Implementation

The layout uses Flutter's `Row` widget with `Expanded` children:

```dart
Row(
  children: [
    // Data Table - 60% when panel open, 100% when closed
    Expanded(
      flex: _activeDialog.isNotEmpty ? 6 : 10,
      child: DataTableSection(),
    ),
    // Side Panel - 40% when open, hidden when closed
    if (_activeDialog.isNotEmpty)
      Expanded(
        flex: 4,
        child: SidePanel(),
      ),
  ],
)
```

The `flex` values create the 60/40 split:
- Data: `flex: 6` = 60% of available space
- Panel: `flex: 4` = 40% of available space
- When panel closed: Data gets `flex: 10` = 100%

## User Actions

### Opening a Panel
1. Click any feature button in ribbon
2. Side panel slides in from right
3. Data table smoothly resizes to 60%
4. Both are fully interactive

### Closing a Panel
1. Click X button in panel header
2. Panel disappears
3. Data table expands to 100%
4. Focus returns to data

### Switching Panels
1. Click different feature button
2. Current panel content changes
3. Layout stays split-screen
4. No jarring transitions

## Responsive Behavior

The split maintains proportions on different screen sizes:

| Screen Width | Data Table | Side Panel |
|-------------|-----------|------------|
| 1920px | 1152px (60%) | 768px (40%) |
| 1600px | 960px (60%) | 640px (40%) |
| 1366px | 820px (60%) | 546px (40%) |
| 1280px | 768px (60%) | 512px (40%) |

## Comparison with Old Overlay System

### Old (Modal Overlay)
```
┌─────────────────────────────────┐
│     Data (dimmed background)    │
│                                  │
│   ┌─────────────────────┐       │
│   │   Feature Dialog    │       │
│   │   (centered)        │       │
│   └─────────────────────┘       │
│                                  │
└─────────────────────────────────┘
```
**Issues:**
- Data partially obscured
- Dialog blocks view
- Hard to reference data

### New (Side Panel)
```
┌───────────────────┬─────────────┐
│   Data (clear)    │   Feature   │
│                   │   Panel     │
│   Fully visible   │   (right)   │
│                   │             │
└───────────────────┴─────────────┘
```
**Benefits:**
- Data fully visible
- Side-by-side view
- Easy to reference

## Summary

The side panel layout provides a superior user experience by:
- Keeping data always visible
- Enabling side-by-side workflows
- Reducing cognitive load
- Matching modern app standards
- Improving productivity

Users can work with features while continuously viewing their data, making the application more efficient and user-friendly.
