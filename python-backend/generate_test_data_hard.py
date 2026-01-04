"""
Generate Hard Difficulty Test Data for FastMig
-----------------------------------------------
Creates a dataset with severe data quality issues:
- ~30% missing values
- Many type mismatches
- Lots of null strings
- Extreme outliers
- Many duplicate rows
- Mixed content chaos
- Invalid datetime formats everywhere
- Inconsistent encoding issues
- Numbers in string columns
- Strings in number columns
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(123)
random.seed(123)

# Configuration
NUM_ROWS = 75
MISSING_RATE = 0.30  # 30% missing values

# Sample data pools
FIRST_NAMES = ['Ahmed', 'Fatima', 'Ali', 'Ayesha', 'Hassan', 'Zainab', 'Omar', 'Sara',
               'Bilal', 'Mariam', 'Usman', 'Hira', 'Imran', 'Sana', 'Farhan', 'Nadia',
               'Kashif', 'Mehreen', 'Asad', 'Sadia']
LAST_NAMES = ['Khan', 'Ahmed', 'Ali', 'Malik', 'Sheikh', 'Syed', 'Hussain', 'Iqbal',
              'Butt', 'Chaudhry', 'Qureshi', 'Rizvi', 'Jafri', 'Zaidi', 'Mirza', 'Shah']
DEPARTMENTS = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'IT', 'Research']
CITIES = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Peshawar', 'Quetta']
PRODUCTS = ['Laptop Pro X1', 'Wireless Mouse', 'Mechanical Keyboard', 'USB Hub', 'Monitor 27"',
            'Webcam HD', 'Headphones Elite', 'Docking Station', 'SSD 1TB', 'RAM 16GB',
            'Graphics Card RTX', 'Power Supply 750W', 'CPU Cooler', 'Network Switch']

# Chaos data for injection
NULL_VARIANTS = ['null', 'NULL', 'Null', 'none', 'None', 'NONE', 'N/A', 'n/a', 'NA',
                 '#N/A', '#NA', 'unknown', 'Unknown', 'UNKNOWN', '-', '--', '???',
                 'missing', 'MISSING', 'not available', 'TBD', 'TBA', 'pending']

GARBAGE_VALUES = ['!@#$%^', '...', '   ', '\t', 'error', 'ERROR', '#REF!', '#VALUE!',
                  'undefined', 'NaN', 'inf', '-inf', '0xDEADBEEF', '<blank>', '[empty]']

def generate_hard_data():
    """Generate hard difficulty unclean dataset with severe issues"""

    data = {
        'Record_ID': [],
        'Customer_Name': [],
        'Age': [],
        'Annual_Income': [],
        'Credit_Score': [],
        'Account_Type': [],
        'Email_Address': [],
        'Phone_Number': [],
        'Registration_Date': [],
        'Last_Transaction': [],
        'City': [],
        'Postal_Code': [],
        'Loyalty_Points': [],
        'Status': []
    }

    for i in range(NUM_ROWS):
        # Record ID (many duplicates and invalid)
        rec_id = i + 5001
        if random.random() < 0.15:  # 15% duplicates
            rec_id = random.choice(range(5001, 5001 + max(1, i)))
        if random.random() < 0.08:  # 8% invalid IDs
            rec_id = random.choice(['ID-ERROR', 'TEMP', -999, 'abc123', ''])

        # Customer Name (numbers mixed in, special chars)
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if random.random() < 0.12:  # 12% garbage names
            name = random.choice([
                '12345',  # Pure number in name field
                '67890',
                'Customer_#123',
                '???',
                'Test Test Test',
                '   ',
                random.choice(NULL_VARIANTS),
                f"{random.randint(100,999)}"  # Just a number
            ])

        # Age (lots of invalid)
        age = random.randint(18, 75)
        if random.random() < 0.18:  # 18% invalid ages
            age = random.choice([
                'twenty-five', 'thirty', 'N/A', -10, 200, 999,
                '25 years', 'approx 30', '', 'minor', 'adult',
                random.choice(NULL_VARIANTS), 0, 1, 150
            ])

        # Annual Income (extreme outliers, text, negative)
        income = round(random.uniform(20000, 500000), 2)
        if random.random() < 0.15:  # 15% problematic
            income = random.choice([
                9999999999, -100000, 0, 'classified', 'high',
                'low income', random.choice(NULL_VARIANTS),
                '50,000', '$75000', 'Rs. 100000', '1e6', 'millions'
            ])

        # Credit Score (should be 300-850)
        credit = random.randint(300, 850)
        if random.random() < 0.15:  # 15% invalid
            credit = random.choice([
                0, 1000, -500, 'excellent', 'good', 'poor',
                'A+', 'B-', random.choice(NULL_VARIANTS),
                '750+', '>800', 'pending review'
            ])

        # Account Type
        account = random.choice(['Savings', 'Checking', 'Premium', 'Business', 'Student'])
        if random.random() < 0.1:  # 10% invalid
            account = random.choice([
                123, 456, random.choice(NULL_VARIANTS),
                'Type_A', 'UNKNOWN_TYPE', ''
            ])

        # Email (many invalid formats)
        email = f"{name.lower().replace(' ', '.')}@email.com"
        if random.random() < 0.2:  # 20% invalid
            email = random.choice([
                'invalid', 'not@valid', '@domain.com', 'test@',
                'spaces in@email.com', 'double@@at.com',
                random.choice(NULL_VARIANTS), '', '   ',
                'noemail', 'fake_email', '12345'
            ])

        # Phone (wildly inconsistent)
        phone = f"03{random.randint(0,9)}{random.randint(0,9)}-{random.randint(1000000, 9999999)}"
        if random.random() < 0.2:  # 20% inconsistent
            phone = random.choice([
                f"+92{random.randint(3000000000, 3999999999)}",
                f"0{random.randint(3000000000, 3999999999)}",
                f"(042) {random.randint(1000000, 9999999)}",
                '0000000000', '1234567890', 'call me',
                random.choice(NULL_VARIANTS), '', 'no phone',
                f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            ])

        # Registration Date (chaos)
        reg_date = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 5000))
        reg_date_str = reg_date.strftime('%Y-%m-%d')
        if random.random() < 0.2:  # 20% invalid dates
            reg_date_str = random.choice([
                '2025-13-45', '2024-02-30', '13/25/2023',
                '01-15-2020', 'Jan 15, 2020', '15th January 2020',
                '2020/01/15', 'yesterday', 'last year',
                random.choice(NULL_VARIANTS), '', 'TBD',
                '1/1/20', '2020', '01-2020', str(random.randint(1000000000, 9999999999))
            ])

        # Last Transaction (numeric timestamps mixed with strings)
        trans_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 700))
        trans_str = trans_date.strftime('%Y-%m-%d')
        if random.random() < 0.25:  # 25% problematic
            trans_str = random.choice([
                str(int(trans_date.timestamp() * 1000)),  # Unix timestamp ms
                str(int(trans_date.timestamp())),  # Unix timestamp s
                'never', 'recent', 'long ago',
                random.choice(NULL_VARIANTS), '',
                '2024-99-99', 'N/A'
            ])

        # City (null variants and numbers)
        city = random.choice(CITIES)
        if random.random() < 0.12:  # 12% problematic
            city = random.choice([
                random.choice(NULL_VARIANTS),
                str(random.randint(1, 100)),  # Number as city
                '', '   ', 'City_123', 'Unknown City'
            ])

        # Postal Code (should be 5 digits)
        postal = str(random.randint(10000, 99999))
        if random.random() < 0.15:  # 15% invalid
            postal = random.choice([
                'ABCDE', '1234', '123456789', random.choice(NULL_VARIANTS),
                '', 'N/A', 'unknown', '0000', '00000'
            ])

        # Loyalty Points (negative, extreme, text)
        points = random.randint(0, 10000)
        if random.random() < 0.12:  # 12% invalid
            points = random.choice([
                -500, 999999999, 'gold', 'silver', 'bronze',
                random.choice(NULL_VARIANTS), '', 'pending',
                '1,500', '2.5K', 'many'
            ])

        # Status
        status = random.choice(['Active', 'Inactive', 'Pending', 'Suspended'])
        if random.random() < 0.1:  # 10% invalid
            status = random.choice([
                1, 0, -1, random.choice(NULL_VARIANTS),
                '', 'YES', 'NO', 'MAYBE'
            ])

        # Add to data
        data['Record_ID'].append(rec_id)
        data['Customer_Name'].append(name)
        data['Age'].append(age)
        data['Annual_Income'].append(income)
        data['Credit_Score'].append(credit)
        data['Account_Type'].append(account)
        data['Email_Address'].append(email)
        data['Phone_Number'].append(phone)
        data['Registration_Date'].append(reg_date_str)
        data['Last_Transaction'].append(trans_str)
        data['City'].append(city)
        data['Postal_Code'].append(postal)
        data['Loyalty_Points'].append(points)
        data['Status'].append(status)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Introduce aggressive random missing values (30%)
    for col in df.columns:
        mask = np.random.random(len(df)) < MISSING_RATE
        mask_indices = np.where(mask)[0]
        # Cap at 40% per column
        if len(mask_indices) > len(df) * 0.4:
            mask_indices = mask_indices[:int(len(df) * 0.4)]
        df.loc[mask_indices, col] = np.nan

    # Add many duplicate rows (8-10 duplicates)
    num_duplicates = random.randint(8, 10)
    duplicate_indices = random.sample(range(len(df)), min(num_duplicates, len(df)))
    duplicates = df.iloc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # Add some completely garbage rows
    garbage_rows = []
    for _ in range(3):
        garbage_row = {col: random.choice(GARBAGE_VALUES + NULL_VARIANTS) for col in df.columns}
        garbage_rows.append(garbage_row)

    garbage_df = pd.DataFrame(garbage_rows)
    df = pd.concat([df, garbage_df], ignore_index=True)

    # Shuffle the dataframe to mix garbage throughout
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df

if __name__ == "__main__":
    print("Generating HARD difficulty test data...")
    print("=" * 50)
    df = generate_hard_data()

    # Save to CSV and Excel
    df.to_csv('test_data_hard.csv', index=False)
    df.to_excel('test_data_hard.xlsx', index=False)

    print(f"\nGenerated {len(df)} rows with the following columns:")
    print(df.columns.tolist())
    print(f"\nMissing values per column:")
    print(df.isnull().sum())
    print(f"\nTotal missing cells: {df.isnull().sum().sum()}")
    print(f"\nTotal cells: {df.shape[0] * df.shape[1]}")
    print(f"Missing percentage: {(df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100:.1f}%")
    print(f"\nSample data (first 15 rows):")
    print(df.head(15).to_string())
    print("\n" + "=" * 50)
    print("Files saved: test_data_hard.csv, test_data_hard.xlsx")
    print("\nThis dataset includes:")
    print("  - ~30% missing values")
    print("  - Many type mismatches")
    print("  - Null string variants (null, None, N/A, etc.)")
    print("  - Extreme outliers")
    print("  - Duplicate rows")
    print("  - Numbers in string columns")
    print("  - Strings in number columns")
    print("  - Invalid dates in multiple formats")
    print("  - Garbage/corrupted rows")
    print("  - Inconsistent formatting")
