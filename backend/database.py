"""
SQL Server Database Connection Module
"""
import pyodbc
import pandas as pd

SERVER = 'DESKTOP-DHPAOGN'
DATABASE = 'AutoVisionAI'
DRIVER = 'ODBC Driver 17 for SQL Server'

def get_connection():
    """Get SQL Server connection"""
    conn_str = f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

def get_all_cars():
    """Get all cars from database as DataFrame"""
    conn = get_connection()
    df = pd.read_sql('SELECT * FROM Cars', conn)
    conn.close()
    return df

def get_brands():
    """Get unique car brands (first word of name)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN name LIKE 'Mercedes%' THEN 'Mercedes-Benz'
                WHEN name LIKE 'Land Rover%' THEN 'Land Rover'
                ELSE SUBSTRING(name, 1, CHARINDEX(' ', name + ' ') - 1)
            END as brand
        FROM Cars
        ORDER BY brand
    """)
    brands = [row[0] for row in cursor.fetchall()]
    conn.close()
    return brands

def get_models_by_brand(brand):
    """Get car models for a specific brand"""
    conn = get_connection()
    cursor = conn.cursor()
    if brand == 'Mercedes-Benz':
        cursor.execute("SELECT DISTINCT name FROM Cars WHERE name LIKE 'Mercedes%' ORDER BY name")
    elif brand == 'Land Rover':
        cursor.execute("SELECT DISTINCT name FROM Cars WHERE name LIKE 'Land Rover%' ORDER BY name")
    else:
        cursor.execute("SELECT DISTINCT name FROM Cars WHERE name LIKE ? ORDER BY name", f'{brand}%')
    models = [row[0] for row in cursor.fetchall()]
    conn.close()
    return models

def get_stats():
    """Get market statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    cursor.execute('SELECT COUNT(*), AVG(selling_price), MIN(selling_price), MAX(selling_price) FROM Cars')
    row = cursor.fetchone()
    stats['total_records'] = row[0]
    stats['avg_price'] = round(row[1], 0) if row[1] else 0
    stats['min_price'] = row[2] or 0
    stats['max_price'] = row[3] or 0
    
    cursor.execute('SELECT COUNT(DISTINCT fuel) FROM Cars')
    stats['fuel_types'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT MIN(year), MAX(year) FROM Cars')
    r = cursor.fetchone()
    stats['min_year'] = r[0]
    stats['max_year'] = r[1]
    
    cursor.execute('SELECT COUNT(DISTINCT transmission) FROM Cars')
    stats['trans_types'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

def register_user(email, password, name):
    """Register a new user in SQL Server"""
    conn = get_connection()
    cursor = conn.cursor()
    # Basic plain-text storing for simplicity, hashes are better but this works for demo
    try:
        cursor.execute("INSERT INTO Users (email, password, name) VALUES (?, ?, ?)", email, password, name)
        conn.commit()
        cursor.execute("SELECT id, name, email FROM Users WHERE email = ?", email)
        row = cursor.fetchone()
        conn.close()
        return {'id': row[0], 'name': row[1], 'email': row[2]}
    except pyodbc.IntegrityError:
        conn.close()
        return {'error': 'Email already exists'}
    except Exception as e:
        conn.close()
        return {'error': str(e)}

def authenticate_user(email, password):
    """Authenticate a single user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM Users WHERE email = ? AND password = ?", email, password)
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'name': row[1], 'email': row[2]}
    return {'error': 'Invalid email or password'}

def save_prediction(car_name, year, km_driven, fuel, transmission, owner, predicted_price, confidence, user_id=None, car_id=None):
    """Save prediction to database, associated with a user and a car if available"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Predictions (car_name, year, km_driven, fuel, transmission, owner, predicted_price, confidence, user_id, car_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, car_name, year, km_driven, fuel, transmission, owner, predicted_price, confidence, user_id, car_id)
    conn.commit()
    conn.close()

def get_predictions_history(user_id, limit=50):
    """Get prediction history for a specific user"""
    if not user_id:
        return pd.DataFrame()
        
    conn = get_connection()
    df = pd.read_sql(f'SELECT TOP {limit} * FROM Predictions WHERE user_id = {user_id} ORDER BY created_at DESC', conn)
    conn.close()
    return df

def delete_all_predictions(user_id):
    """Delete all prediction history for a specific user"""
    if not user_id:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Predictions WHERE user_id = ?", user_id)
    conn.commit()
    conn.close()

def check_email_exists(email):
    """Check if email exists in database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Users WHERE email = ?", email)
    row = cursor.fetchone()
    conn.close()
    return row is not None

def update_password(email, new_password):
    """Update user password"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET password = ? WHERE email = ?", new_password, email)
        conn.commit()
        conn.close()
        return {'status': 'success'}
    except Exception as e:
        return {'error': str(e)}

def get_price_by_fuel():
    """Price statistics by fuel type"""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT fuel, 
               COUNT(*) as count, 
               AVG(selling_price) as avg_price,
               MIN(selling_price) as min_price,
               MAX(selling_price) as max_price
        FROM Cars
        GROUP BY fuel
        ORDER BY avg_price DESC
    """, conn)
    conn.close()
    return df

def get_price_by_year():
    """Price statistics by year"""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT year, 
               COUNT(*) as count, 
               AVG(selling_price) as avg_price
        FROM Cars
        GROUP BY year
        ORDER BY year
    """, conn)
    conn.close()
    return df

def get_price_by_transmission():
    """Price by transmission type"""
    conn = get_connection()
    df = pd.read_sql("""
        SELECT transmission, 
               COUNT(*) as count, 
               AVG(selling_price) as avg_price
        FROM Cars
        GROUP BY transmission
    """, conn)
    conn.close()
    return df

def get_top_brands(limit=15):
    """Top brands by count"""
    conn = get_connection()
    df = pd.read_sql(f"""
        SELECT TOP {limit}
            CASE 
                WHEN name LIKE 'Mercedes%' THEN 'Mercedes-Benz'
                WHEN name LIKE 'Land Rover%' THEN 'Land Rover'
                ELSE SUBSTRING(name, 1, CHARINDEX(' ', name + ' ') - 1)
            END as brand,
            COUNT(*) as count,
            AVG(selling_price) as avg_price
        FROM Cars
        GROUP BY 
            CASE 
                WHEN name LIKE 'Mercedes%' THEN 'Mercedes-Benz'
                WHEN name LIKE 'Land Rover%' THEN 'Land Rover'
                ELSE SUBSTRING(name, 1, CHARINDEX(' ', name + ' ') - 1)
            END
        ORDER BY count DESC
    """, conn)
    conn.close()
    return df
