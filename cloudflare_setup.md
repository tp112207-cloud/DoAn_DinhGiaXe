# Hướng dẫn tích hợp Cloudflare Tunnel cho AutoVision.AI

Tài liệu này hướng dẫn cách public ứng dụng AI của bạn ra internet mà không cần deploy server hay Docker.

## 1. Cài đặt cloudflared (Windows)

Mở **PowerShell (Admin)** và chạy lệnh sau:

```powershell
winget install Cloudflare.cloudflared
```

*Hoặc nếu bạn không dùng winget, có thể tải file `.msi` tại: [cloudflare/cloudflared](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi)*

Sau khi cài đặt, hãy kiểm tra bằng cách mở CMD mới và gõ: `cloudflared --version`

---

## 2. Cách chạy Tunnel (trycloudflare)

Không cần tạo tài khoản, bạn có thể tạo một URL public ngẫu nhiên bằng lệnh:

1. Chạy ứng dụng web locally trước: `python run.py` (đảm bảo chạy tại port 7860).
2. Mở một terminal khác, di chuyển đến thư mục dự án và chạy:
   ```cmd
   cloudflared tunnel --url http://localhost:7860
   ```
3. Tìm dòng output có dạng:
   `+  Your quick tunnel has been created! Visit it at: https://something-random.trycloudflare.com`
4. Copy link đó và gửi cho bạn bè.

---

## 3. Chạy tự động khi mở máy (Tuỳ chọn)

Để ứng dụng và tunnel tự khởi động, bạn có thể:

### Cách A: Dùng Task Scheduler (Khuyên dùng)
1. Nhấn `Win + R`, gõ `taskschd.msc`.
2. Chọn **Create Basic Task...**
3. Tên: `AutoVision_Tunnel`
4. Trigger: **When I log on**
5. Action: **Start a program**
6. Program/script: Chọn file `start_tunnel.bat` trong thư mục dự án.
7. Nhấn Finish.

### Cách B: Startup Folder
1. Nhấn `Win + R`, gõ `shell:startup`.
2. Tạo một Shortcut trỏ đến file `start_tunnel.bat` vào thư mục này.

---

## Lưu ý:
* URL `trycloudflare` sẽ thay đổi mỗi khi bạn khởi động lại tunnel.
* Nếu muốn dùng URL cố định (ví dụ: `ai.yourdomain.com`), bạn cần đăng ký tài khoản Cloudflare và mua domain.
