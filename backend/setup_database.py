"""
Setup SQL Server Database for AutoVision.AI
============================================
- Creates database 'AutoVisionAI' on SQL Server
- Creates table 'Cars' and imports data from cardekho.csv
- Run once: python setup_database.py
"""
import pyodbc
import pandas as pd
import os
import sys

# SQL Server connection config
SERVER = 'DESKTOP-DHPAOGN'
DATABASE = 'AutoVisionAI'
DRIVER = 'ODBC Driver 17 for SQL Server'

def get_connection(database=None):
    """Connect to SQL Server"""
    db = database or 'master'
    conn_str = f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={db};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str, autocommit=True)

def create_database():
    """Create AutoVisionAI database"""
    print(f'Connecting to SQL Server: {SERVER}...')
    conn = get_connection('master')
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT name FROM sys.databases WHERE name = ?", DATABASE)
    if cursor.fetchone():
        print(f'Database [{DATABASE}] already exists.')
    else:
        cursor.execute(f'CREATE DATABASE [{DATABASE}]')
        print(f'Database [{DATABASE}] created!')
    
    conn.close()

def create_table():
    """Create Cars table"""
    conn = get_connection(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Cars' AND xtype='U')
    CREATE TABLE Cars (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        year INT NOT NULL,
        selling_price BIGINT NOT NULL,
        km_driven INT NOT NULL,
        fuel NVARCHAR(50) NOT NULL,
        seller_type NVARCHAR(50) NOT NULL,
        transmission NVARCHAR(50) NOT NULL,
        owner NVARCHAR(50) NOT NULL,
        mileage FLOAT NULL,
        engine FLOAT NULL,
        max_power NVARCHAR(50) NULL,
        seats FLOAT NULL,
        created_at DATETIME DEFAULT GETDATE()
    )
    """)
    print('Table [Cars] ready.')

    # Create Predictions table for logging
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Predictions' AND xtype='U')
    CREATE TABLE Predictions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        car_name NVARCHAR(255),
        year INT,
        km_driven INT,
        fuel NVARCHAR(50),
        transmission NVARCHAR(50),
        owner NVARCHAR(50),
        predicted_price FLOAT,
        confidence FLOAT,
        created_at DATETIME DEFAULT GETDATE()
    )
    """)
    print('Table [Predictions] ready.')
    
    conn.close()

def import_data():
    """Import cardekho.csv into Cars table"""
    conn = get_connection(DATABASE)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM Cars')
    count = cursor.fetchone()[0]
    if count > 0:
        print(f'Cars table already has {count} records. Skipping import.')
        print('To re-import, run: DELETE FROM Cars')
        conn.close()
        return count
    
    # Load CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'cardekho.csv')
    if not os.path.exists(csv_path):
        print(f'ERROR: {csv_path} not found!')
        conn.close()
        return 0
    
    df = pd.read_csv(csv_path)
    print(f'Loading {len(df)} records from cardekho.csv...')
    
    # Clean data
    df = df.rename(columns={'mileage(km/ltr/kg)': 'mileage'})
    
    # Insert in batches
    inserted = 0
    batch_size = 100
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        for _, row in batch.iterrows():
            try:
                cursor.execute("""
                INSERT INTO Cars (name, year, selling_price, km_driven, fuel, 
                                  seller_type, transmission, owner, mileage, 
                                  engine, max_power, seats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                str(row['name']),
                int(row['year']),
                int(row['selling_price']),
                int(row['km_driven']),
                str(row['fuel']),
                str(row['seller_type']),
                str(row['transmission']),
                str(row['owner']),
                float(row['mileage']) if pd.notna(row['mileage']) else None,
                float(row['engine']) if pd.notna(row['engine']) else None,
                str(row['max_power']) if pd.notna(row['max_power']) else None,
                float(row['seats']) if pd.notna(row['seats']) else None,
                )
                inserted += 1
            except Exception as e:
                print(f'  Skip row {i}: {e}')
        
        if (i + batch_size) % 1000 == 0:
            print(f'  Imported {inserted} records...')
    
    conn.commit()
    print(f'Done! Imported {inserted} records into [Cars] table.')
    conn.close()
    return inserted

def verify():
    """Verify database setup"""
    conn = get_connection(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM Cars')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT fuel) FROM Cars')
    fuels = cursor.fetchone()[0]
    
    cursor.execute('SELECT MIN(year), MAX(year) FROM Cars')
    row = cursor.fetchone()
    
    cursor.execute('SELECT MIN(selling_price), MAX(selling_price), AVG(selling_price) FROM Cars')
    price = cursor.fetchone()
    
    print(f'\n--- Database Verification ---')
    print(f'Total records: {total}')
    print(f'Fuel types: {fuels}')
    print(f'Year range: {row[0]} - {row[1]}')
    print(f'Price range: {price[0]:,} - {price[1]:,} (avg: {price[2]:,.0f})')
    print(f'Database OK!')
    
    conn.close()

if __name__ == '__main__':
    try:
        create_database()
        create_table()
        import_data()
        verify()
        print('\nSetup complete!')
    except pyodbc.Error as e:
        print(f'\nSQL Server Error: {e}')
        print(f'Make sure SQL Server is running on {SERVER}')
        sys.exit(1)
