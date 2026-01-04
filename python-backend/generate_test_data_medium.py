"""
Generate Medium Difficulty Test Data for FastMig
-------------------------------------------------
Creates a dataset with moderate data quality issues:
- ~15% missing values
- Some type mismatches
- A few null strings
- Moderate outliers
- Some duplicate rows
- Minor formatting inconsistencies
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_ROWS = 50
MISSING_RATE = 0.15  # 15% missing values

# Sample data pools
FIRST_NAMES = ['Ahmed', 'Fatima', 'Ali', 'Ayesha', 'Hassan', 'Zainab', 'Omar', 'Sara',
               'Bilal', 'Mariam', 'Usman', 'Hira', 'Imran', 'Sana', 'Farhan', 'Nadia']
LAST_NAMES = ['Khan', 'Ahmed', 'Ali', 'Malik', 'Sheikh', 'Syed', 'Hussain', 'Iqbal',
              'Butt', 'Chaudhry', 'Qureshi', 'Rizvi', 'Jafri', 'Zaidi', 'Mirza', 'Shah']
DEPARTMENTS = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'IT', 'Research']
CITIES = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar', 'Quetta']
PRODUCTS = ['Laptop Pro X1', 'Wireless Mouse', 'Mechanical Keyboard', 'USB Hub', 'Monitor 27"',
            'Webcam HD', 'Headphones Elite', 'Docking Station', 'SSD 1TB', 'RAM 16GB']

def generate_medium_data():
    """Generate medium difficulty unclean dataset"""

    data = {
        'Employee_ID': [],
        'Full_Name': [],
        'Age': [],
        'Department': [],
        'Salary': [],
        'Email': [],
        'Phone': [],
        'Hire_Date': [],
        'City': [],
        'Performance_Score': []
    }

    for i in range(NUM_ROWS):
        # Employee ID (some duplicates)
        emp_id = i + 1001
        if random.random() < 0.08:  # 8% chance of duplicate ID
            emp_id = random.choice(range(1001, 1001 + i)) if i > 0 else emp_id

        # Full Name
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

        # Age (some invalid values)
        age = random.randint(22, 60)
        if random.random() < 0.06:  # 6% chance of invalid age
            age = random.choice(['twenty-five', 'N/A', -5, 150, ''])

        # Department
        dept = random.choice(DEPARTMENTS)

        # Salary (some outliers)
        salary = round(random.uniform(30000, 150000), 2)
        if random.random() < 0.05:  # 5% outliers
            salary = random.choice([999999, -50000, 'confidential', 0])

        # Email (some invalid)
        email = f"{name.lower().replace(' ', '.')}@company.com"
        if random.random() < 0.08:  # 8% invalid emails
            email = random.choice(['invalid-email', 'test@', '@domain.com', 'no_email', ''])

        # Phone (inconsistent formats)
        phone = f"03{random.randint(0,9)}{random.randint(0,9)}-{random.randint(1000000, 9999999)}"
        if random.random() < 0.1:  # 10% formatting issues
            phone = random.choice([
                f"+923{random.randint(100000000, 999999999)}",
                f"03{random.randint(100000000, 999999999)}",
                'N/A',
                'unknown',
                ''
            ])

        # Hire Date (some invalid)
        hire_date = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 3000))
        hire_date_str = hire_date.strftime('%Y-%m-%d')
        if random.random() < 0.08:  # 8% invalid dates
            hire_date_str = random.choice(['2025-13-45', 'not_available', '01/15/2020', 'TBD', ''])

        # City
        city = random.choice(CITIES)
        if random.random() < 0.05:  # 5% null-like strings
            city = random.choice(['null', 'None', 'N/A'])

        # Performance Score (1-10, some invalid)
        score = round(random.uniform(1, 10), 1)
        if random.random() < 0.07:  # 7% invalid scores
            score = random.choice(['excellent', 'A+', -2, 15, 'pending'])

        # Add to data
        data['Employee_ID'].append(emp_id)
        data['Full_Name'].append(name)
        data['Age'].append(age)
        data['Department'].append(dept)
        data['Salary'].append(salary)
        data['Email'].append(email)
        data['Phone'].append(phone)
        data['Hire_Date'].append(hire_date_str)
        data['City'].append(city)
        data['Performance_Score'].append(score)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Introduce random missing values (15%)
    for col in df.columns:
        mask = np.random.random(len(df)) < MISSING_RATE
        # Don't make ALL values in a column null
        mask_indices = np.where(mask)[0]
        if len(mask_indices) > len(df) * 0.3:  # Cap at 30% per column
            mask_indices = mask_indices[:int(len(df) * 0.3)]
        df.loc[mask_indices, col] = np.nan

    # Add a few complete duplicate rows
    duplicate_indices = random.sample(range(len(df)), 3)
    duplicates = df.iloc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    return df

if __name__ == "__main__":
    print("Generating medium difficulty test data...")
    df = generate_medium_data()

    # Save to CSV and Excel
    df.to_csv('test_data_medium.csv', index=False)
    df.to_excel('test_data_medium.xlsx', index=False)

    print(f"\nGenerated {len(df)} rows with the following columns:")
    print(df.columns.tolist())
    print(f"\nMissing values per column:")
    print(df.isnull().sum())
    print(f"\nTotal missing cells: {df.isnull().sum().sum()}")
    print(f"\nSample data:")
    print(df.head(10))
    print("\nFiles saved: test_data_medium.csv, test_data_medium.xlsx")
