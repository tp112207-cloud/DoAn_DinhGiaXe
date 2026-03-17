---
title: AutoVision AI
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# AutoVision.AI - Đồ án AI Dự đoán Giá Xe

Ứng dụng web sử dụng trí tuệ nhân tạo (Machine Learning) để dự đoán giá xe ô tô tại thị trường Việt Nam.

## 🚀 Cách chạy

### 1. Backend (Python Flask)

```bash
# Cài đặt thư viện
cd backend
pip install -r requirements.txt

# Train model (chỉ cần chạy 1 lần)
python model/train_model.py

# Khởi động server
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

### 2. Frontend

Mở file `frontend/index.html` trong trình duyệt (hoặc dùng Live Server extension trong VS Code).

## 📁 Cấu trúc dự án

```
DoAn_DinhGiaXe/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── data/
│   │   └── cars_data.csv   # Dataset (300+ records)
│   └── model/
│       ├── train_model.py  # Script train ML model
│       ├── predict.py      # Prediction class
│       └── *.pkl           # Saved model files
├── frontend/
│   ├── index.html          # Trang chủ
│   ├── du-doan.html        # Trang dự đoán giá
│   ├── phan-tich.html      # Phân tích thị trường
│   ├── lich-su.html        # Lịch sử dự đoán
│   ├── gioi-thieu.html     # Giới thiệu
│   ├── dang-nhap.html      # Đăng nhập/Đăng ký
│   ├── css/styles.css      # Design system
│   └── js/components.js    # Shared components
└── README.md
```

## 🛠️ Công nghệ

- **Backend**: Python, Flask, Flask-CORS
- **ML**: Scikit-learn (Gradient Boosting Regressor)
- **Data**: Pandas, NumPy
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **AI Accuracy**: R² = 87.4%
