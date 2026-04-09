# Xinjing Backend (FastAPI + MySQL)

This is a starter backend skeleton aligned with your frontend modules:
- screening
- report
- mood calendar
- companion chat

## 1. Setup

```powershell
cd xinjing-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update `XJ_DATABASE_URL`.

### MySQL init (Navicat)

Run this SQL file directly in Navicat:

- [sql/init_mysql_auth.sql](d:/pycharm-project/02Depression_Detection/计算机设计大赛/计算机设计大赛/xinjing-backend/sql/init_mysql_auth.sql)

Then set `.env`:

```env
XJ_DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/xinjing?charset=utf8mb4
XJ_JWT_SECRET_KEY=replace_with_a_long_random_key
XJ_DEBUG=true
```

## 2. Run

```powershell
uvicorn app.main:app --reload --port 8000
```

Or use the startup script:

```powershell
.\scripts\start_backend.bat
```

Use test env:

```powershell
.\scripts\start_backend.bat -EnvFile .env.test
```

If you want to use another env file (for example `.env.test`), set `XJ_ENV_FILE` before startup:

```powershell
$env:XJ_ENV_FILE=".env.test"
uvicorn app.main:app --reload --port 8000
```

Swagger:
- http://127.0.0.1:8000/docs

Health checks:
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/api/v1/health/db

## 3. Current API modules

- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/evaluations/sessions`
- `POST /api/v1/evaluations/sessions/{session_id}/submit`
- `GET /api/v1/reports/{report_id}`
- `PUT /api/v1/mood-calendar/{record_date}`
- `GET /api/v1/mood-calendar`
- `POST /api/v1/chat/sessions`
- `POST /api/v1/chat/sessions/{session_id}/messages`
- `GET /api/v1/chat/sessions/{session_id}/messages`

## 4. Notes

- Use Alembic migrations before production.
- Passwords are stored as hash (`password_hash`), not plain text.

## 5. Login/Register request examples

### Register

`POST /api/v1/auth/register`

```json
{
  "username": "test001",
  "email": "test001@example.com",
  "phone": "13800000000",
  "password": "12345678",
  "nickname": "测试用户"
}
```

### Login

`POST /api/v1/auth/login`

```json
{
  "username": "test001",
  "password": "12345678"
}
```

> `username` supports either username or email.
