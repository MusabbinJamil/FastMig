"""
Quick validation script to verify the Modified_by_AI tracking fix
"""

import pandas as pd
import numpy as np
from data_fitness import clean_data_evolutionary

print("="*60)
print("Validating Modified_by_AI Tracking Fix")
print("="*60)

# Create simple test data
np.random.seed(42)
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', None, 'Charlie', 'David', None],  # 2 missing
    'age': [25, 30, None, 40, 45],  # 1 missing
    'score': [90, 85, 88, None, 92]  # 1 missing
}

df = pd.DataFrame(data)

print("\n📊 Original Data:")
print(df)
print(f"\nMissing values per column:")
print(df.isna().sum())
print(f"\nTotal records with missing values: {df.isna().any(axis=1).sum()}")

# Clean with tracking enabled
print("\n" + "="*60)
print("🔧 Cleaning with GA (tracking enabled)...")
print("="*60)

cleaned_df, report = clean_data_evolutionary(
    df, 
    method='ga',
    track_modifications=True,
    population_size=20,
    generations=30
)

print("\n✅ Cleaned Data:")
print(cleaned_df)

print("\n📈 Tracking Results:")
print(f"Modified_by_AI column present: {'Modified_by_AI' in cleaned_df.columns}")
print(f"Records marked as modified: {cleaned_df['Modified_by_AI'].sum()}")
print(f"Records NOT modified: {(~cleaned_df['Modified_by_AI']).sum()}")

# Show which records were modified
modified_indices = cleaned_df[cleaned_df['Modified_by_AI']].index.tolist()
print(f"\nModified record indices: {modified_indices}")

# Verify logic
original_records_with_missing = df[df.isna().any(axis=1)].index.tolist()
print(f"Original records with missing values: {original_records_with_missing}")

# Check if tracking is accurate
if set(modified_indices) == set(original_records_with_missing):
    print("\n✅ SUCCESS: All and only records with missing values were marked!")
else:
    print("\n❌ WARNING: Mismatch between modified records and records with missing values")
    print(f"   Expected: {original_records_with_missing}")
    print(f"   Got: {modified_indices}")

# Show modification statistics from report
print("\n📊 Report Statistics:")
print(f"Modifications tracked: {report['modifications']['tracked']}")
print(f"Records modified: {report['modifications']['records_modified']}")
print(f"Modification rate: {report['modifications']['modification_rate']}")

print("\n" + "="*60)
print("✅ Fix Validation Complete!")
print("="*60)
