---
title: AutoVision AI
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: static
pinned: false
---

# 🚗 AutoVision.AI - Hệ Thống Định Giá Xe Thông Minh (AI Smart Valuation)

**AutoVision.AI** là nền tảng số hóa ứng dụng trí tuệ nhân tạo (Mô hình Gradient Boosting) nhằm hỗ trợ người dùng và các chuyên gia định giá xe ô tô đã qua sử dụng một cách chính xác, minh bạch và nhanh chóng tại thị trường Việt Nam. Dự án được thiết kế với giao diện Dashboard hiện đại, mang lại trải nghiệm tối ưu cho cả cá nhân và các đại lý kinh doanh xe.

---

## 🌟 TÍNH NĂNG NỔI BẬT (Key Features)

### 1. 🤖 Lõi AI Dự Đoán Siêu Tốc (Smart Predictor)
- Sử dụng thuật toán **Gradient Boosting Regressor** từ thư viện Scikit-learn đã được tinh chỉnh (Fine-tuning) kỹ lưỡng.
- Tốc độ xử lý siêu nhanh: Trả kết quả dự đoán cùng khoảng tin cậy (Confidence Interval) chỉ trong **< 1 giây**.
- Độ chính xác (**$R^2$ Score**) đạt trên **87.4%** từ tập dữ liệu thực tế hơn 300+ mẫu xe phổ biến.

### 2. 📊 Bảng Điều Khiển Phân Tích (Market Dashboard)
- Không chỉ đưa ra con số, hệ thống còn cung cấp cái nhìn toàn cảnh về thị trường thông qua các biểu đồ (Charts) trực quan.
- Tự động thống kê xu hướng giá theo: **Năm sản xuất, Loại nhiên liệu, Kiểu truyền động** và **Thương hiệu phổ biến**.
- Giúp người dùng đưa ra quyết định mua/bán dựa trên dữ liệu (Data-driven decisions) thay vì cảm tính.

### 3. 💬 Trợ Lý Ảo AutoVision (Gemini Inside)
- Tích hợp mô hình ngôn ngữ lớn **Google Gemini AI** (Smart Chatbot).
- Hỗ trợ giải đáp thắc mắc về kỹ thuật xe, tư vấn lựa chọn dòng xe phù hợp và hướng dẫn sử dụng hệ thống một cách thông minh.
- Phản hồi bằng tiếng Việt tự nhiên, chuyên sâu về lĩnh vực ô tô.

### 4. 🗄️ Quản Lý Lịch Sử & Tài Khoản (Smart CRM)
- Tích hợp hệ thống quản lý người dùng (Login/Register) thông qua **SQL Server**.
- Mọi lịch sử định giá đều được lưu lại chi tiết theo từng tài khoản cá nhân.
- Tính năng **Báo cáo lịch sử**: Dễ dàng tra cứu lại các phiên định giá cũ để so sánh sự biến động của giá trị xe theo thời gian.

### 5. 🏥 Hệ Thống Tra Cứu & Xác Thực OTP
- Bảo mật thông tin người dùng bằng hệ thống xác thực OTP qua email khi đổi mật khẩu (SMTP Server).
- Đảm bảo an toàn dữ liệu cá nhân cho mọi giao dịch và thông tin trên nền tảng.

### 6. 🌍 Giao Diện Tùy Biến Chuyên Sâu (UX/UI Premium)
- Cấu trúc **SPA (Single Page Application)** chuyển tab mượt mà, không giật lag.
- Hỗ trợ **Dark/Light Mode** bảo vệ mắt cho người dùng khi làm việc ban đêm.
- Tích hợp các hiệu ứng Micro-animations (AOS, GSAP) tạo cảm giác cao cấp và chuyên nghiệp.

---

## 🛠️ CÔNG NGHỆ SỬ DỤNG (Tech Stack)

| Thành phần | Công nghệ tiêu biểu |
| :--- | :--- |
| **Trí tuệ nhân tạo (AI/ML)** | Scikit-learn, Pandas, NumPy, Matplotlib |
| **Backend (Máy chủ)** | Python, Flask, Flask-CORS, SMTP |
| **Cơ sở dữ liệu** | Microsoft SQL Server (Hoặc CSV Fallback) |
| **Bảo mật** | Password Hashing (SHA256), OTP Verification, .env secrets |
| **Frontend (Giao diện)** | HTML5, CSS3, Vanilla JS (ES6+), Chart.js, AOS Library |
| **Hạ tầng (Deployment)** | Cloudflare Tunnel (Fixed Custom Domain) |

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG

### ⚠️ LƯU Ý QUAN TRỌNG VỀ DỮ LIỆU & MÔ HÌNH (QUAN TRỌNG)
> Do kích thước Model AI và Dataset thực tế lớn, Quý thầy vui lòng tải bổ sung các file cần thiết tại link Google Drive dưới đây:
> 
> 👉 **[(Link Google Drive)](https://drive.google.com/drive/folders/1PWORDBUVwevrJs9JYlhpedKBEoupsIfrtHZtVJhagNv8t5fQ7sJQdD1f_kmpHeImSake1Kbq?hl=vi)**

**Sau khi tải về, vui lòng đặt vào đúng vị trí:**
1. Chép file `cardekho.csv` (Dataset) vào thư mục **`backend/data/`**
2. Chép file `car_price_model.pkl` (Model AI) vào thư mục **`backend/model/`**
3. Tạo file **`.env`** tại thư mục **`backend/`** và điền `GEMINI_API_KEY` (nếu cần dùng chatbot).

---

### **Các bước khởi chạy:**
1. **Khởi động Backend (Não bộ AI):**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
2. **Khởi chạy Launcher (All-in-one):**
   Hoặc đơn giản nhất, bạn chỉ cần chạy file **`run.py`** ở thư mục gốc để hệ thống tự động thiết lập và chạy Web Server.

👉 **Link Demo Trực Tuyến:** [https://th.xurtxinh.id.vn](https://th.xurtxinh.id.vn)


**AutoVision.AI** - *Kiến tạo tương lai định giá xe bằng dữ liệu & AI.*
