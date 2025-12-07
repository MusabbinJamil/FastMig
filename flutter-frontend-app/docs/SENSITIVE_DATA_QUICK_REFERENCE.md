# Sensitive Data Warnings - Quick Reference

## 🎯 What This Feature Does

Displays warnings for sensitive data columns (Date of Birth, NIC, Passport, etc.) that **cannot be reliably imputed** using AI algorithms.

## ⚙️ How It Works

```
User Loads Data
        ↓
User Selects "AI Cleaning"
        ↓
System Scans for Sensitive Columns
        ↓
Warning Displayed (if found)
        ↓
User Reviews & Decides
        ↓
User Proceeds with Cleaning
```

## 🚨 Detected Sensitive Columns

### HIGH Severity (Cannot be reliably imputed)
- ✋ Date of Birth / DOB
- ✋ NIC / National ID  
- ✋ Passport Number
- ✋ Social Security Number (SSN)
- ✋ Tax ID / License Numbers
- ✋ VIN / Serial Numbers
- ✋ Other Unique Identifiers

### MEDIUM Severity (Need verification)
- ⚠️ Phone Numbers (personal)
- ⚠️ Mobile Numbers
- ⚠️ Contact Information

## 📍 Where to Find It

**Screen**: AI Data Quality Workflow → Evolutionary Data Cleaning section

**Display**: Appears automatically when section loads, before cleaning starts

## 🎨 Visual Indicators

| Element | Meaning |
|---------|---------|
| 🔴 RED Border | HIGH severity warning |
| 🟠 ORANGE Border | MEDIUM severity warning |
| [HIGH] Badge | Cannot be imputed |
| [MEDIUM] Badge | Needs verification |
| 🔓 Lock Icon | Sensitive/protected data |

## 💡 Recommended Actions

When you see the warning:

1. **Review the columns** - Check if they should be cleaned
2. **Verify missing values** - See how many need imputation
3. **Choose action**:
   - ✅ Dismiss and manually verify imputed values
   - ✅ Take data back to original source
   - ✅ Exclude sensitive columns from cleaning
   - ✅ Proceed at your own risk

## ✅ Example Warnings

### Warning 1: Date of Birth
```
🔐 date_of_birth [HIGH]

Reason: Date of Birth - Cannot be reliably imputed. 
        Missing dates should be obtained from original source.

Recommendation: Consider manual imputation or excluding from AI cleaning.

Missing: 5 values (2.5%)
```

### Warning 2: NIC Number
```
🔐 nic_number [HIGH]

Reason: Identification Number - These are unique identifiers that cannot 
        be imputed. Missing values must be verified from original documents.

Recommendation: Consider manual imputation or excluding from AI cleaning.

Missing: 3 values (1.5%)
```

## ❓ FAQ

**Q: Can I ignore the warning and clean anyway?**
A: Yes, the feature is non-blocking. You can dismiss and proceed, but be aware the imputed values may be false or invalid.

**Q: Will it prevent cleaning from happening?**
A: No, it's just a warning. You can proceed at your own discretion.

**Q: How accurate is the detection?**
A: Detection is rule-based on keywords and data patterns. Review the warnings carefully for your specific data.

**Q: Can I customize what's considered "sensitive"?**
A: Yes, see `SENSITIVE_DATA_WARNINGS.md` for configuration details.

**Q: What if my data has other sensitive columns?**
A: The feature catches the most common ones. For others, use manual review or document-based verification.

## 🔧 Technical Details

- **Backend Endpoint**: `GET /fitness/sensitive-columns`
- **Response Time**: < 1 second
- **Failure Behavior**: Silently skips (non-critical)
- **Configuration**: Edit `data_fitness.py` keywords

## 📋 Checklist for Users

- [ ] Review all detected sensitive columns
- [ ] Understand why each is flagged
- [ ] Count missing values
- [ ] Decide: Clean, exclude, or verify from source
- [ ] If cleaning, plan for post-cleaning verification
- [ ] Document your decision for audit trail
- [ ] Verify imputed values before using cleaned data

## 🎓 Best Practices

1. **Always review** sensitive data warnings
2. **Verify from source** when possible for IDs/dates
3. **Document decisions** about how sensitive data was handled
4. **Test** with sample data first
5. **Keep backups** of original data
6. **Audit** cleaned data before using in production

## 📞 Support

For issues or questions:
1. Check the full documentation: `SENSITIVE_DATA_WARNINGS.md`
2. Review the implementation: `SENSITIVE_DATA_WARNINGS_IMPLEMENTATION.md`
3. Test with sample data
4. Check console logs for backend errors

---

**Quick Tips**:
- 🚀 Feature loads automatically, no setup needed
- 🔒 Sensitive columns are highlighted in RED
- 📊 Shows exact count of missing values
- 💾 Always keep backup of original data
- ✅ Review before using cleaned data in production
