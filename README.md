# 🤖 Dobby Setup Bot

Bot Discord tự động thiết lập cấu trúc server bằng form AI.

## ✨ Tính năng
- Form modal `/setup` — nhập số category, tên, mô tả
- Tự động tạo category, text/voice channel, role
- Icon + font chữ fancy Unicode
- Auto role khi member join
- HTTP server giữ Render Free không bị sleep

## 🚀 Deploy lên Render

1. Push code lên GitHub
2. Vào render.com → New → Web Service
3. Kết nối repo GitHub
4. Cấu hình:
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
   - Plan: `Free`
5. Thêm Environment Variables: `DISCORD_TOKEN`, `GUILD_ID`, `PORT=3000`
6. Nhấn Create Web Service

## 🔧 Chạy local

```bash
pip install -r requirements.txt
python bot.py
