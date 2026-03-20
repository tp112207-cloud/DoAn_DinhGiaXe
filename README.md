---
title: AutoVision AI
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: static
pinned: false
---

# 🚗 AutoVision.AI: Hệ Thống Dự Đoán Giá Xe Ô Tô Thông Minh

**AutoVision.AI** là một ứng dụng web tích hợp trí tuệ nhân tạo (Machine Learning) nhằm hỗ trợ người dùng định giá xe ô tô đã qua sử dụng tại thị trường Việt Nam một cách chính xác và nhanh chóng.

---

## 🌟 Tính Năng Cốt Lõi

1. **Dự đoán giá xe nhanh**: Sử dụng mô hình Machine Learning bậc cao để ước tính giá trị xe dựa trên nhiều thông số kỹ thuật.
2. **Phân tích thị trường**: Hệ thống biểu đồ trực quan về xu hướng giá xe theo năm, dòng xe và loại nhiên liệu.
3. **Trợ lý ảo AI (Gemini)**: Tích hợp Chatbot thông minh hỗ trợ giải đáp các thắc mắc về thị trường xe và cách sử dụng hệ thống.
4. **Quản lý lịch sử**: Lưu trữ và quản lý các kết quả dự đoán cá nhân (yêu cầu đăng nhập).
5. **Giao diện hiện đại**: Thiết kế Premium, hỗ trợ đa thiết bị và trải nghiệm người dùng tối ưu.

---

## 🛠️ Cấu Trúc Công Nghệ (Tech Stack)

### **Backend (Hệ thống máy chủ)**
- **Ngôn ngữ**: Python 3.x
- **Framework**: Flask (Web API)
- **Cơ sở dữ liệu**: SQL Server (Lưu trữ người dùng/lịch sử) & CSV (Dữ liệu thị trường)
- **AI/ML**: Scikit-Learn (Gradient Boosting Regressor), Pandas, NumPy

### **Frontend (Giao diện người dùng)**
- **Cơ bản**: HTML5, Vanilla CSS3 (Custom Design System), Modern JavaScript (ES6+)
- **Đồ họa**: Chart.js (Biểu đồ phân tích)
- **Animation**: AOS, GSAP (Micro-interactions)

### **AI Integration**
- **LLM**: Google Gemini AI (Cung cấp giải pháp hội thoại thông minh)

---

## 📊 Mô Hình Machine Learning

Mô hình được huấn luyện dựa trên tập dữ liệu thị trường thực tế với hơn 300+ bản ghi chi tiết.
- **Thuật toán**: Gradient Boosting Regressor.
- **Độ chính xác (Accuracy)**: $R^2 \approx 87.4\%$.
- **Các đặc trưng đầu vào**: Thương hiệu, Năm sản xuất, Số Km đã đi, Loại nhiên liệu, Kiểu truyền động, Tình trạng xe, Nguồn gốc xuất xứ.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### **1. Yêu cầu hệ thống**
- Python 3.8+
- SQL Server (Tùy chọn, hệ thống tự động fallback sang CSV nếu không có)

### **2. Cài đặt môi trường**
Mở terminal và thực hiện các lệnh sau:
```bash
# Di chuyển vào thư mục backend
cd backend

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Cấu hình môi trường (Tạo file .env)
# Điền GEMINI_API_KEY, EMAIL_USER, EMAIL_PASS
```

### **3. Khởi chạy hệ thống**
Bạn có thể dùng Launcher tích hợp sẵn tại thư mục gốc:
```bash
python run.py
```
Hệ thống sẽ tự động thực hiện:
- Kiểm tra & Cài đặt thư viện còn thiếu.
- Khởi tạo Database.
- Huấn luyện Model AI (nếu chưa có).
- Khởi chạy Web Server tại cổng `7860`.

---

## 🌐 Truy Cập Trực Tuyến

Ứng dụng hiện đang được public để demo tại địa chỉ:
👉 **[https://th.xurtxinh.id.vn](https://th.xurtxinh.id.vn)**

*(Lưu ý: Hệ thống tunnel được cài đặt tự động dưới dạng nền (Service) thông qua Cloudflare Tunnel, đảm bảo kết nối ổn định mà không cần mở port mạng).*

---

## 📁 Tổ Chức Thư Mục

```bash
DoAn_DinhGiaXe/
├── backend/            # Mã nguồn máy chủ và xử lý AI
│   ├── app.py          # Flask Main Entry
│   ├── database.py     # Xử lý SQL Server
│   ├── model/          # Định nghĩa và lưu trữ Model ML
│   └── data/           # Dataset huấn luyện
├── frontend/           # Toàn bộ giao diện người dùng
│   ├── index.html      # Trang chủ (Dashboard)
│   ├── du-doan.html    # Giao diện dự đoán giá
│   ├── css/            # UI/UX Styles
│   └── js/             # Logic tương tác phía client
├── run.py              # Launcher tự động (Mọi thứ trong một)
└── README.md           # Tài liệu kỹ thuật
```

---
**AutoVision.AI** - *Đồ án định giá xe thông minh - 2026*
