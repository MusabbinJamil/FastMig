"""Simple test to verify Modified_by_AI tracking works"""

import pandas as pd
import numpy as np
from data_fitness import clean_data_evolutionary

np.random.seed(42)
data = {
    'id': [1, 2, 3, 4, 5],
    'value': [10.5, None, 30.5, None, 50.5]  # Only numeric to avoid other bugs
}

df = pd.DataFrame(data)

print("Original Data:")
print(df)
print(f"\nRecords with missing values: {df['value'].isna().sum()}")

# Clean with DE (which works better with numeric data)
cleaned, report = clean_data_evolutionary(
    df, 
    method='de',
    track_modifications=True,
    pop_size=10,
    max_iter=20
)

print("\n" + "="*50)
print("Cleaned Data:")
print(cleaned)

print("\n" + "="*50)
print("Tracking Results:")
print(f"✓ Modified_by_AI column added: {'Modified_by_AI' in cleaned.columns}")
print(f"✓ Records marked as True: {cleaned['Modified_by_AI'].sum()}")
print(f"✓ Records marked as False: {(~cleaned['Modified_by_AI']).sum()}")
print(f"✓ Modification rate: {report['modifications']['modification_rate']}")

print("\nDetailed view:")
print(cleaned[['id', 'value', 'Modified_by_AI']])

# Verify correctness
expected_modified = [1, 3]  # indices 1 and 3 had missing values
actual_modified = cleaned[cleaned['Modified_by_AI']].index.tolist()

if expected_modified == actual_modified:
    print("\n✅ SUCCESS: Tracking works correctly!")
else:
    print(f"\n⚠️ Expected {expected_modified}, got {actual_modified}")
