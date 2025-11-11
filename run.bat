@echo off
echo -------------------------------------------
echo 🚀 TỰ ĐỘNG CHẠY ỨNG DỤNG VƯỜN QUỐC GIA BẠCH MÃ (V3 XANH RỪNG)
echo -------------------------------------------
REM Kiểm tra Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python chưa được cài đặt hoặc chưa thêm vào PATH.
    echo Vui lòng cài đặt Python 3.10+ rồi chạy lại.
    pause
    exit /b
)

REM Tạo môi trường ảo nếu chưa có
IF NOT EXIST .venv (
    echo 🔧 Đang tạo môi trường ảo (.venv)...
    python -m venv .venv --without-pip
    echo 🌱 Cài pip...
    .venv\Scripts\python.exe -m ensurepip
)

REM Kích hoạt môi trường ảo
call .venv\Scripts\activate

REM Thiết lập tài khoản quản trị mặc định (có thể thay đổi sau)
set ADMIN_USERNAME=ThucvatBM
set ADMIN_PASSWORD=Bachma123

REM Cài thư viện cần thiết
echo 📦 Đang cài đặt thư viện...
pip install -r requirements.txt

REM Khởi động ứng dụng
echo 🚀 Đang khởi động ứng dụng...
python app.py

pause
