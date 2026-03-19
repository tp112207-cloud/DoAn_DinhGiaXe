# Hướng dẫn dùng Tên miền riêng (Custom Domain) cho Cloudflare Tunnel

Khi bạn đã có tên miền riêng (ví dụ: `duanai.com`), bạn sẽ không dùng link ngẫu nhiên nữa mà sẽ có một địa chỉ cố định và chuyên nghiệp.

### Bước 1: Trỏ tên miền về Cloudflare (Bắt buộc)
1. Đăng nhập vào [Cloudflare Dash](https://dash.cloudflare.com/).
2. Nhấn **Add a site** và nhập tên miền của bạn. Chọn gói **Free**.
3. Cloudflare sẽ cung cấp cho bạn 2 cái **NameServers** (ví dụ: `abby.ns.cloudflare.com`).
4. Bạn vào trang quản trị tên miền mà bạn vừa mua (ví dụ: Namecheap), tìm phần **DNS/NameServers** và đổi sang 2 cái NameServers của Cloudflare.
5. Đợi khoảng 5-15 phút để DNS cập nhật.

---

### Bước 2: Tạo Tunnel cố định (Nên dùng Dashboard cho dễ)
Thay vì gõ lệnh mỗi lần, hãy dùng giao diện web của Cloudflare:
1. Truy cập: [Cloudflare Zero Trust](https://one.dash.cloudflare.com/).
2. Vào **Networks** -> **Tunnels** -> **Create a Tunnel**.
3. Chọn **Cloudflared** -> Đặt tên (ví dụ: `ai-server`).
4. Tại phần **Install connector**: Nếu bạn đã cài cloudflared trên máy mình rồi, hãy chọn tab Windows và copy đoạn mã ở bước 4 (thường bắt đầu bằng `cloudflared.exe service install ...`).
5. Tại phần **Public Hostname**:
   - **Subdomain**: (để trống hoặc gõ `ai`)
   - **Domain**: Chọn tên miền bạn vừa mua.
   - **Type**: `HTTP`
   - **URL**: `localhost:7860`
6. Nhấn **Save**.

---

### Bước 3: Chạy Tunnel
Sau khi cấu hình trên web xong, bạn chỉ cần chạy lệnh cài đặt connector một lần duy nhất. Sau đó, mỗi khi máy tính mở lên (nếu cài dạng Service), tunnel sẽ tự động chạy và web của bạn sẽ online tại địa chỉ `http://tenmien.com` bạn đã chọn.

---

### Ưu điểm so với cách cũ:
- Link không bao giờ thay đổi.
- Không cần mở terminal gõ lệnh mỗi ngày.
- Tự khởi động cùng Windows (dạng Service).

**Lưu ý:** Nếu bạn gặp khó khăn ở bước nào (ví dụ: không tìm thấy chỗ đổi NameServers trên Namecheap), hãy chụp ảnh màn hình gửi tôi nhé!
