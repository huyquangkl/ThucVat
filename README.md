# Danh mục các loài thực vật tại VQG Bạch Mã — v3 Xanh Rừng (Deploy-Ready)

Giao diện tông **xanh rừng**, tiêu đề chữ **vàng nhạt**, logo bên trái – cổng chào bên phải, footer đồng bộ, hiệu ứng nhẹ.

## Tính năng
- Danh sách loài: Tên Việt Nam, *Tên khoa học*, Họ, Thumbnail, Vị trí
- Tìm kiếm: Tên thường gọi / Tên khoa học / Họ
- Xuất CSV theo bộ lọc
- Thêm/Sửa/Xóa (upload ảnh)
- Đăng nhập quản trị
- Tự tạo DB & tài khoản admin khi chạy lần đầu

## Chạy nhanh (Windows)
1) Mở thư mục dự án và **nhấp đúp** `Chay_Ung_dung_VQG_Bach_Ma.bat`
2) Mở http://localhost:5000

> Nếu muốn chạy thủ công:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set ADMIN_USERNAME=ThucvatBM
set ADMIN_PASSWORD=Bachma123
python app.py
```

## Triển khai Render
- Đưa mã nguồn lên GitHub → Tạo Web Service → Render đọc `render.yaml`
- Biến môi trường mặc định: `ADMIN_USERNAME=ThucvatBM`, `ADMIN_PASSWORD=Bachma123` (hãy đổi sau khi deploy).

## Triển khai Heroku
```bash
heroku create bachma-danhmuc-v3
heroku buildpacks:set heroku/python
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set ADMIN_USERNAME=ThucvatBM
heroku config:set ADMIN_PASSWORD=Bachma123
heroku config:set DATABASE_URL=sqlite:///data.db
git add . && git commit -m "deploy v3" && git push heroku HEAD:main
heroku open
```

## Cấu trúc dữ liệu
- common_name, scientific_name, family, genus, location, status, description, image_path

> Bảo mật: đổi mật khẩu admin ngay khi đưa lên Internet.
