from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import json
import sys
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
sys.path.insert(0, BASE_DIR)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# Load env before using
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    GEMINI_LOADED = True
else:
    print("Warning: GEMINI_API_KEY not found in .env")
    GEMINI_LOADED = False

# Email Configuration
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
if EMAIL_USER and EMAIL_PASS:
    print("SMTP Email Configuration found!")
else:
    print("Warning: EMAIL_USER or EMAIL_PASS not found in .env. OTP will only be logged to console.")

# Restart Configuration
RESTART_TOKEN = os.getenv('RESTART_TOKEN')

# Tỷ giá chuyển đổi INR sang VND
INR_TO_VND = 300

# Try SQL Server connection
USE_SQL = False
try:
    from database import (get_all_cars, get_brands, get_models_by_brand,
                          get_stats, get_price_by_fuel, get_price_by_year,
                          get_price_by_transmission, get_top_brands, save_prediction,
                          register_user, authenticate_user, get_predictions_history, delete_all_predictions,
                          check_email_exists, update_password)
    # Test connection
    stats = get_stats()
    USE_SQL = True
    print(f'SQL Server connected! ({stats["total_records"]} records)')
except Exception as e:
    print(f'SQL Server not available: {e}')
    print('Using CSV fallback.')
    
# Store OTPs in memory for simplicity: { "email": { "otp": "123456", "expires_at": datetime } }
OTP_STORE = {}
    
# Load CSV as fallback
DATA_PATH = os.path.join(BASE_DIR, 'data', 'cardekho.csv')
if os.path.exists(DATA_PATH):
    df_csv = pd.read_csv(DATA_PATH)
    df_csv = df_csv.rename(columns={'mileage(km/ltr/kg)': 'mileage'})
    # Extract brand
    def extract_brand(name):
        name = str(name)
        if name.startswith('Mercedes'): return 'Mercedes-Benz'
        if name.startswith('Land Rover'): return 'Land Rover'
        return name.split(' ')[0]
    df_csv['brand'] = df_csv['name'].apply(extract_brand)
else:
    df_csv = pd.DataFrame()

# Auto-train model if not exists
model_path = os.path.join(BASE_DIR, 'model', 'car_price_model.pkl')
if not os.path.exists(model_path):
    print('Model not found. Training now...')
    from model.train_model import train_model
    train_model()

# Load predictor
try:
    from model.predict import CarPricePredictor
    predictor = CarPricePredictor()
    MODEL_LOADED = True
except Exception as e:
    print(f'Model error: {e}')
    MODEL_LOADED = False
    predictor = None


# ===== SERVE FRONTEND =====
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)


# ===== API ENDPOINTS =====
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': MODEL_LOADED,
        'sql_connected': USE_SQL,
        'data_source': 'SQL Server' if USE_SQL else 'CSV'
    })

@app.route('/api/restart', methods=['POST'])
def restart_service():
    """Restart the service (requires token)"""
    auth_header = request.headers.get('Authorization')
    if not RESTART_TOKEN or auth_header != f"Bearer {RESTART_TOKEN}":
        return jsonify({'error': 'Unauthorized'}), 401
    
    print("Restart request received. Service shutting down in 2 seconds...")
    
    # Thread to allow response to be sent before exiting
    import threading
    import time
    def shutdown():
        time.sleep(2)
        print("Exiting now...")
        os._exit(0) # PM2 will restart it
        
    threading.Thread(target=shutdown).start()
    
    return jsonify({'status': 'Restarting...'})


@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict car price"""
    if not MODEL_LOADED:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.json
    
    if predictor is None:
        return jsonify({'error': 'Predictor not initialized'}), 500
        
    result = predictor.predict(
        name=data.get('name', ''),
        year=data.get('year', 2020),
        km_driven=data.get('km_driven', 30000),
        fuel=data.get('fuel', 'Petrol'),
        transmission=data.get('transmission', 'Manual'),
        owner=data.get('owner', 'First Owner'),
        mileage=data.get('mileage'),
        engine=data.get('engine'),
        max_power=data.get('max_power'),
        seats=data.get('seats', 5),
    )
    
    if result is None or result.get('error'):
        return jsonify(result if result else {'error': 'Prediction failed'}), 500
    
    # Price Adjustment Logic based on new fields
    condition = data.get('condition', '')
    origin = data.get('origin', '')
    color = data.get('color', '')
    
    multiplier = 1.0
    
    # 1. Condition
    if 'Mới (New)' in condition:
        multiplier *= 1.25    # +25%
    elif 'Tốt (Good)' in condition:
        multiplier *= 1.05    # +5%
    elif 'Trung bình (Fair)' in condition:
        multiplier *= 0.90    # -10%
    elif 'Kém (Poor)' in condition:
        multiplier *= 0.70    # -30%
    elif 'Rất kém (Damaged)' in condition:
        multiplier *= 0.50    # -50%
        
    # 2. Origin
    if 'Nhập khẩu' in origin:
        multiplier *= 1.15    # +15%
        
    # 3. Color
    if color in ['Trắng Bạch Kim', 'Đen Ngọc Trai', 'Bạc Titan']:
        multiplier *= 1.05    # Phổ biến, giữ giá tốt +5%
    elif color in ['Xanh Dương', 'Đỏ Cherry']:
        multiplier *= 1.02    # Đẹp, cá tính +2%
    elif color == 'Khác':
        multiplier *= 0.95    # Kén khách -5%
        
    # Apply Adjustments
    if multiplier != 1.0:
        result['predicted_price'] = round(result['predicted_price'] * multiplier, 0)
        result['confidence_low'] = round(result['confidence_low'] * multiplier, 0)
        result['confidence_high'] = round(result['confidence_high'] * multiplier, 0)
    
    # Save to SQL if available and user is logged in
    if USE_SQL and data.get('user_id'):
        try:
            save_prediction(
                data.get('name', ''), data.get('year', 2020),
                data.get('km_driven', 30000), data.get('fuel', 'Petrol'),
                data.get('transmission', 'Manual'), data.get('owner', 'First Owner'),
                result['predicted_price'], result['confidence_percent'],
                data.get('user_id')
            )
        except Exception as e:
            print(f"Error saving prediction: {e}")
            pass
    
    result['input'] = data
    return jsonify(result)


@app.route('/api/brands', methods=['GET'])
def api_brands():
    """Get car brands"""
    if USE_SQL:
        brands = get_brands()
    else:
        brands = sorted(df_csv['brand'].unique().tolist()) if not df_csv.empty else []
    
    brand_data = []
    for b in brands:
        if USE_SQL:
            count = len(get_models_by_brand(b))
        else:
            count = len(df_csv[df_csv['brand'] == b]) if not df_csv.empty else 0
        brand_data.append({'name': b, 'count': count})
    
    return jsonify({'brands': brand_data})


@app.route('/api/models/<brand>', methods=['GET'])
def api_models(brand):
    """Get models for a brand"""
    if USE_SQL:
        models = get_models_by_brand(brand)
    else:
        if brand == 'Mercedes-Benz':
            models = sorted(df_csv[df_csv['name'].str.startswith('Mercedes')]['name'].unique().tolist())
        elif brand == 'Land Rover':
            models = sorted(df_csv[df_csv['name'].str.startswith('Land Rover')]['name'].unique().tolist())
        else:
            models = sorted(df_csv[df_csv['brand'] == brand]['name'].unique().tolist())
    
    return jsonify({'models': models, 'brand': brand})


@app.route('/api/fuel-types', methods=['GET'])
def api_fuel_types():
    if predictor and hasattr(predictor, 'get_fuel_types'):
        return jsonify({'fuel_types': predictor.get_fuel_types()})
    return jsonify({'fuel_types': ['Petrol', 'Diesel', 'CNG', 'LPG']})


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Market statistics"""
    df = df_csv
    if USE_SQL:
        try:
            sql_stats = get_stats()
            brands_list = get_brands()
            result = {
                'total_records': sql_stats['total_records'],
                'total_brands': len(brands_list),
                'avg_price': round(sql_stats['avg_price'] * INR_TO_VND, 0),
                'min_price': round(sql_stats['min_price'] * INR_TO_VND, 0),
                'max_price': round(sql_stats['max_price'] * INR_TO_VND, 0),
                'data_source': 'SQL Server',
            }
        except Exception:
            result = _csv_stats(df)
    else:
        result = _csv_stats(df)
    
    if predictor and hasattr(predictor, 'metadata') and predictor.metadata:
        result['model_accuracy'] = float(predictor.metadata.get('r2_score', 0)) * 100
        result['model_mae'] = float(predictor.metadata.get('mae', 0)) * INR_TO_VND
        result['total_models'] = int(predictor.metadata.get('n_samples', 0))
    
    return jsonify(result)

def _csv_stats(df):
    if df.empty:
        return {'total_records': 0, 'total_brands': 0, 'avg_price': 0, 'min_price': 0, 'max_price': 0}
    return {
        'total_records': int(len(df)),
        'total_brands': int(df['brand'].nunique()),
        'avg_price': int(round(float(df['selling_price'].mean()) * INR_TO_VND)),
        'min_price': float(df['selling_price'].min()) * INR_TO_VND,
        'max_price': float(df['selling_price'].max()) * INR_TO_VND,
        'data_source': 'CSV',
    }

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    if not USE_SQL:
        return jsonify({'error': 'Database unavailable'}), 503
        
    data = request.json
    result = register_user(data.get('email'), data.get('password'), data.get('name'))
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate a user"""
    if not USE_SQL:
        return jsonify({'error': 'Database unavailable'}), 503
        
    data = request.json
    result = authenticate_user(data.get('email'), data.get('password'))
    if 'error' in result:
        return jsonify(result), 401
    return jsonify(result)

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Generate and send OTP for forgot password"""
    if not USE_SQL:
        return jsonify({'error': 'Database unavailable'}), 503
        
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
        
    # Check if email exists in database
    if not check_email_exists(email):
        return jsonify({'error': 'Tài khoản không tồn tại!'}), 404
        
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with 5 mins expiration
    expires_at = datetime.now() + timedelta(minutes=5)
    OTP_STORE[email] = {
        'otp': otp,
        'expires_at': expires_at
    }
    
    # Send email
    if EMAIL_USER and EMAIL_PASS:
        try:
            msg = MIMEMultipart()
            msg['From'] = f"AutoVision.AI <{EMAIL_USER}>"
            msg['To'] = email
            msg['Subject'] = "Mã OTP đặt lại mật khẩu - AutoVision.AI"
            
            body = f"""
            <html>
                <body>
                    <h2>Thiết lập lại mật khẩu</h2>
                    <p>Chào bạn,</p>
                    <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản AutoVision.AI.</p>
                    <p>Mã OTP của bạn là: <strong style="font-size: 24px; color: #4F46E5;">{otp}</strong></p>
                    <p>Mã này sẽ hết hạn sau 5 phút.</p>
                    <p>Nếu bạn không yêu cầu điều này, vui lòng bỏ qua email.</p>
                </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server (assuming Gmail, change if different)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, email, text)
            server.quit()
            
            return jsonify({'status': 'Hệ thống đã gửi OTP đến email của bạn!'})
        except Exception as e:
            print(f"Lỗi gửi email: {e}")
            return jsonify({'error': 'Không thể gửi email OTP (Lỗi SMTP)'}), 500
    else:
        # Fallback to console print if no email configured
        print(f"\n======== QUÊN MẬT KHẨU ========")
        print(f"Email: {email}")
        print(f"Mã OTP LÀ: {otp}")
        print(f"=================================\n")
        
        return jsonify({'status': 'Hệ thống đã gửi OTP (kiểm tra Terminal backend)'})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP before allowing password reset"""
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    
    if not all([email, otp]):
        return jsonify({'error': 'Vui lòng cung cấp email và mã OTP'}), 400
        
    if email not in OTP_STORE:
        return jsonify({'error': 'Chưa yêu cầu gửi mã OTP cho email này'}), 400
        
    stored_data = OTP_STORE.get(email)
    if not stored_data:
        return jsonify({'error': 'Phiên xác thực không hợp lệ'}), 400
        
    expires_at = stored_data.get('expires_at')
    if isinstance(expires_at, datetime) and datetime.now() > expires_at:
        OTP_STORE.pop(email, None)
        return jsonify({'error': 'Mã OTP đã hết hạn (quá 5 phút)'}), 400
        
    if str(otp) != str(stored_data.get('otp', '')):
        return jsonify({'error': 'Mã OTP không đúng'}), 400
        
    # Mark as verified
    stored_data['verified'] = True
    
    return jsonify({'status': 'Xác thực OTP thành công'})

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Update new password after OTP is verified"""
    if not USE_SQL:
        return jsonify({'error': 'Database unavailable'}), 503
        
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')
    
    if not all([email, new_password]):
        return jsonify({'error': 'Vui lòng cung cấp đầy đủ thông tin'}), 400
        
    # Check OTP store and verified flag
    if email not in OTP_STORE:
        return jsonify({'error': 'Session đã hết hạn, vui lòng gửi lại mã OTP'}), 400
        
    stored_data = OTP_STORE[email]
    
    if not stored_data.get('verified'):
        return jsonify({'error': 'Bạn chưa xác thực mã OTP thành công'}), 403
        
    expires_at = stored_data.get('expires_at')
    if isinstance(expires_at, datetime) and datetime.now() > expires_at:
        OTP_STORE.pop(email, None)
        return jsonify({'error': 'Phiên đổi mật khẩu đã hết hạn'}), 400
        
    # Update password in database
    result = update_password(email, new_password)
    
    if 'error' in result:
        return jsonify(result), 500
        
    # Delete OTP after successful reset
    OTP_STORE.pop(email, None)
    
    return jsonify({'status': 'Mật khẩu đã được thay đổi thành công'})

@app.route('/api/history', methods=['GET'])
def history():
    """Get prediction history for a user"""
    if not USE_SQL:
        return jsonify([])
        
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
        
    df = get_predictions_history(user_id)
    if df.empty:
        return jsonify([])
    
    # Chuyển đổi dự đoán cũ lưu bằng INR sang VND
    # Nếu predicted_price < 10 triệu VND thì đó là giá INR cũ, cần nhân 300
    if 'predicted_price' in df.columns:
        df['predicted_price'] = df['predicted_price'].apply(
            lambda p: p * INR_TO_VND if p and p < 10000000 else p
        )
        
    # Convert dates to string for JSON serialization
    df['created_at'] = df['created_at'].astype(str)
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Gemini 3 Flash Preview"""
    if not GEMINI_LOADED:
        return jsonify({'error': 'Gemini API not configured'}), 503
        
    data = request.json
    messages = data.get('messages', [])
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400
        
    try:
        system_instruction = """Bạn là AutoVision AI, một trợ lý ảo chuyên gia cho hệ thống dự đoán giá xe ô tô tại Việt Nam (đồ án AutoVision.AI).
Bạn CHỈ được phép trả lời các câu hỏi liên quan đến:
- Đồ án dự đoán giá xe này.
- Dataset của đồ án (Hơn 300+ records xe ô tô các loại, dữ liệu từ Cardekho).
- Machine Learning model được sử dụng (Gradient Boosting Regressor từ thư viện Scikit-learn, độ chính xác R² = 87.4%).
- Cách sử dụng trang web (Trang chủ, Dự đoán giá, Phân tích thị trường, Lịch sử, Giới thiệu).
- Cấu trúc công nghệ: Backend Python (Flask), Frontend HTML/CSS/JS thuần, SQL Server.
- Các kiến thức về xe ô tô, đánh giá xe, giá xe, thị trường xe.

NẾU NGƯỜI DÙNG HỎI NGOÀI CHỦ ĐỀ (chẳng hạn như tổng thống, chính trị, thời tiết không liên quan đến xe, tin tức giải trí...), bạn PHẢI TỪ CHỐI bằng đúng câu:
"Xin lỗi, tôi chỉ hỗ trợ về hệ thống dự đoán giá xe."
Tuyệt đối không giải thích thêm, không trả lời thông tin nào khác."""
        model = genai.GenerativeModel('gemini-3-flash-preview', system_instruction=system_instruction)
        
        contents = []
        for msg in messages:
            role = 'user' if msg.get('role') == 'user' else 'model'
            contents.append({'role': role, 'parts': [msg.get('content', '')]})
            
        response = model.generate_content(contents)
        return jsonify({'response': response.text})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear prediction history for a user"""
    if not USE_SQL:
        return jsonify({'error': 'Database unavailable'}), 503
        
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
        
    try:
        delete_all_predictions(user_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/market-trends', methods=['GET'])
def api_market_trends():
    """Charts data"""
    if USE_SQL:
        try:
            return jsonify(_sql_trends())
        except Exception:
            pass
    return jsonify(_csv_trends())

def _sql_trends():
    fuel_data = get_price_by_fuel()
    year_data = get_price_by_year()
    trans_data = get_price_by_transmission()
    top_data = get_top_brands(15)
    
    return {
        'brand_comparison': [
            {'brand': r['brand'], 'avg_price': float(r['avg_price']) * INR_TO_VND, 'count': int(r['count'])}
            for _, r in top_data.iterrows()
        ],
        'fuel_comparison': [
            {'fuel_type': r['fuel'], 'avg_price': float(r['avg_price']) * INR_TO_VND, 'count': int(r['count'])}
            for _, r in fuel_data.iterrows()
        ],
        'year_trend': [
            {'year': int(r['year']), 'avg_price': float(r['avg_price']) * INR_TO_VND, 'count': int(r['count'])}
            for _, r in year_data.iterrows()
        ],
        'transmission_comparison': [
            {'type': r['transmission'], 'avg_price': float(r['avg_price']) * INR_TO_VND, 'count': int(r['count'])}
            for _, r in trans_data.iterrows()
        ],
        'price_distribution': _get_price_distribution_sql(),
        'top_models': [
            {'full_name': r['name'], 'avg_price': float(r['avg_price']) * INR_TO_VND, 'count': int(r['count'])}
            for r in _get_top_models_sql()
        ],
        'segment_analysis': _get_segment_analysis_sql(),
    }

def _get_price_distribution_sql():
    from database import get_connection
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            CASE 
                WHEN selling_price * 300 < 60000000 THEN N'Dưới 60 Triệu'
                WHEN selling_price * 300 < 150000000 THEN N'60-150 Triệu'
                WHEN selling_price * 300 < 300000000 THEN N'150-300 Triệu'
                WHEN selling_price * 300 < 600000000 THEN N'300-600 Triệu'
                WHEN selling_price * 300 < 1500000000 THEN N'600 Triệu-1.5 Tỷ'
                ELSE N'Trên 1.5 Tỷ'
            END as price_range,
            COUNT(*) as count
        FROM Cars
        GROUP BY 
            CASE 
                WHEN selling_price * 300 < 60000000 THEN N'Dưới 60 Triệu'
                WHEN selling_price * 300 < 150000000 THEN N'60-150 Triệu'
                WHEN selling_price * 300 < 300000000 THEN N'150-300 Triệu'
                WHEN selling_price * 300 < 600000000 THEN N'300-600 Triệu'
                WHEN selling_price * 300 < 1500000000 THEN N'600 Triệu-1.5 Tỷ'
                ELSE N'Trên 1.5 Tỷ'
            END
        ORDER BY MIN(selling_price)
    """, conn)
    conn.close()
    return [{'range': r['price_range'], 'count': int(r['count']), 'label': r['price_range']} for _, r in df.iterrows()]

def _get_segment_analysis_sql():
    from database import get_connection
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            CASE 
                WHEN selling_price * 300 < 150000000 THEN N'Phổ thông (Dưới 150tr)'
                WHEN selling_price * 300 < 300000000 THEN N'Tầm trung (150tr - 300tr)'
                WHEN selling_price * 300 < 600000000 THEN N'Cận cao cấp (300tr - 600tr)'
                WHEN selling_price * 300 < 1500000000 THEN N'Cao cấp (600tr - 1.5tỷ)'
                ELSE N'Hạng sang (Trên 1.5tỷ)'
            END as segment,
            COUNT(*) as count
        FROM Cars
        GROUP BY 
            CASE 
                WHEN selling_price * 300 < 150000000 THEN N'Phổ thông (Dưới 150tr)'
                WHEN selling_price * 300 < 300000000 THEN N'Tầm trung (150tr - 300tr)'
                WHEN selling_price * 300 < 600000000 THEN N'Cận cao cấp (300tr - 600tr)'
                WHEN selling_price * 300 < 1500000000 THEN N'Cao cấp (600tr - 1.5tỷ)'
                ELSE N'Hạng sang (Trên 1.5tỷ)'
            END
        ORDER BY MIN(selling_price)
    """, conn)
    conn.close()
    return [{'segment': r['segment'], 'count': int(r['count'])} for _, r in df.iterrows()]

def _get_top_models_sql():
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 10 name, COUNT(*) as count, AVG(selling_price) as avg_price
        FROM Cars
        GROUP BY name
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{'name': r[0], 'count': r[1], 'avg_price': r[2]} for r in rows]

def _csv_trends():
    df = df_csv
    if df.empty:
        return {'brand_comparison': [], 'fuel_comparison': [], 'year_trend': [], 'price_distribution': [], 'top_models': [], 'segment_analysis': [], 'transmission_comparison': []}
    
    # Brand comparison (chuyển sang VND)
    brand_avg = df.groupby('brand')['selling_price'].agg(['mean', 'count']).sort_values('count', ascending=False).head(15).round(0)
    brand_comparison = [{'brand': b, 'avg_price': float(r['mean']) * INR_TO_VND, 'count': int(r['count'])} for b, r in brand_avg.iterrows()]
    
    # Fuel comparison
    fuel_avg = df.groupby('fuel')['selling_price'].agg(['mean', 'count']).round(0)
    fuel_comparison = [{'fuel_type': f, 'avg_price': float(r['mean']) * INR_TO_VND, 'count': int(r['count'])} for f, r in fuel_avg.iterrows()]
    
    # Year trend
    year_avg = df.groupby('year')['selling_price'].agg(['mean', 'count']).round(0)
    year_trend = [{'year': int(y), 'avg_price': float(r['mean']) * INR_TO_VND, 'count': int(r['count'])} for y, r in year_avg.iterrows()]
    
    # Price distribution (khoảng giá VND)
    ranges = [(0, 200000, 'Dưới 60 Triệu'), (200000, 500000, '60-150 Triệu'), (500000, 1000000, '150-300 Triệu'),
              (1000000, 2000000, '300-600 Triệu'), (2000000, 5000000, '600 Triệu-1.5 Tỷ'), (5000000, 99999999, 'Trên 1.5 Tỷ')]
    price_dist = [{'range': label, 'count': len(df[(df['selling_price'] >= lo) & (df['selling_price'] < hi)]), 'label': label} for lo, hi, label in ranges]
    
    # Transmission
    trans_avg = df.groupby('transmission')['selling_price'].agg(['mean', 'count']).round(0)
    trans_comparison = [{'type': t, 'avg_price': float(r['mean']) * INR_TO_VND, 'count': int(r['count'])} for t, r in trans_avg.iterrows()]
    
    # Top models
    top_names = df.groupby('name')['selling_price'].agg(['mean', 'count']).sort_values('count', ascending=False).head(10).round(0)
    top_models = [{'full_name': n, 'avg_price': float(r['mean']) * INR_TO_VND, 'count': int(r['count'])} for n, r in top_names.iterrows()]
    
    # Segment Analysis (khoảng giá VND)
    ranges2 = [(0, 500000, 'Phổ thông (Dưới 150tr)'), (500000, 1000000, 'Tầm trung (150tr - 300tr)'),
              (1000000, 2000000, 'Cận cao cấp (300tr - 600tr)'), (2000000, 5000000, 'Cao cấp (600tr - 1.5tỷ)'), (5000000, 99999999, 'Hạng sang (Trên 1.5tỷ)')]
    segments = [{'segment': label, 'count': len(df[(df['selling_price'] >= lo) & (df['selling_price'] < hi)])} for lo, hi, label in ranges2]
    
    return {
        'brand_comparison': brand_comparison,
        'fuel_comparison': fuel_comparison,
        'year_trend': year_trend,
        'price_distribution': price_dist,
        'top_models': top_models,
        'segment_analysis': segments,
        'transmission_comparison': trans_comparison,
    }


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    print('\n=== AutoVision.AI ===')
    print(f'Data: {"SQL Server" if USE_SQL else "CSV"} ({len(df_csv)} records)')
    print(f'Model: {"Loaded" if MODEL_LOADED else "Not loaded"}')
    print(f'Open: http://localhost:{port}')
    print('====================\n')
    app.run(debug=False, port=port, host='0.0.0.0')
