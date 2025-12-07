# 🎯 Quick Reference: Side Panel Layout

## Layout at a Glance

### No Panel Open
```
┌──────────────────────────────────────┐
│  RIBBON: All Features                │
├──────────────────────────────────────┤
│                                       │
│         DATA TABLE (100%)             │
│                                       │
└──────────────────────────────────────┘
```

### Panel Open
```
┌──────────────────────────────────────┐
│  RIBBON: All Features                │
├──────────────────┬───────────────────┤
│  DATA (60%)      │  PANEL (40%)      │
│                  │                   │
│  [Your data]     │  [Feature]        │
└──────────────────┴───────────────────┘
```

## How It Works

| Action | Result |
|--------|--------|
| Click feature button | Panel opens → Data shrinks to 60% |
| Click X in panel | Panel closes → Data expands to 100% |
| Click different feature | Panel content changes (stays open) |
| Work in panel | Data visible on left side |

## Width Distribution

- **Panel Closed:** Data = 100%
- **Panel Open:** Data = 60% + Panel = 40%

## Key Benefits

✅ Data always visible  
✅ Side-by-side workflow  
✅ No overlays or dimming  
✅ Modern split-screen design  

## All Features Available

Click any ribbon button to open its panel:
- 📤 Load Data
- 📥 Export
- 🔄 Convert Fields
- ✨ ETL Operations
- 🎥 Record Steps
- 🏥 Data Fitness
- 🔧 AI Cleaning
- ❓ Help

## Pro Tips

💡 **See changes instantly** - Data table updates while panel is open  
💡 **Reference data** - Read data while configuring features  
💡 **Quick close** - Click X or press Esc (if implemented)  
💡 **Switch features** - Click new button without closing panel  

---

**Ready to use!** Run `flutter run` and enjoy the new split-screen experience! 🚀
