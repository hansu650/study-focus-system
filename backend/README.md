# Study Focus Backend

Backend service for the Study Focus desktop application (FastAPI + MySQL).

## Implemented modules
1. User register/login (JWT)
2. Region/school/college dictionary APIs
3. Current user profile get/update
4. AI provider adapter placeholder (OpenAI-compatible)

## Project structure
- `app/`: backend source code
- `scripts/`: deployment/bootstrap scripts
- `deploy/`: systemd + nginx templates
- `.env.example`: environment config template

## Environment setup (Anaconda)
```powershell
cd <PROJECT_BACKEND_DIR>
conda create -n study_focus_backend python=3.11 -y
conda activate study_focus_backend
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

## First local integration (quick path)
1. Set `MYSQL_PASSWORD` in `.env`.
2. Initialize schema:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\init_db.ps1 -MysqlExe mysql -DbHost 127.0.0.1 -DbPort 3306 -DbUser root -DbPassword your_password
```
3. Seed minimal dictionary data (path-safe on Windows):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\seed_demo.ps1 -MysqlExe mysql -DbHost 127.0.0.1 -DbPort 3306 -DbUser root -DbPassword your_password
```
4. Start API server:
```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
5. Open docs: `http://127.0.0.1:8000/docs`

## Register request example
`POST /api/v1/auth/register`
```json
{
  "username": "test001",
  "password": "Test123456",
  "nickname": "test-user",
  "email": "test001@example.com",
  "phone": "13800000001",
  "student_no": "20260001",
  "grade_year": 2026,
  "major_name": "Software Engineering",
  "region_id": 1,
  "school_id": 1,
  "college_id": 1
}
```

## Common issues
1. `1045 Access denied`: wrong `MYSQL_PASSWORD` in `.env`.
2. `Region/School/College does not exist`: run `seed_demo.ps1`.
3. `uvicorn is not recognized`: activate conda env first.

## API docs
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Deployment docs
- `DEPLOYMENT.md`
- `deploy/systemd/study-focus-api.service`
- `deploy/nginx/study-focus.conf`

## Notes
1. Database DDL is in `../db/schema.sql`.
2. Replace `SECRET_KEY` in production.
3. Register/login endpoints use JSON body.
4. AI module is pluggable; provide API endpoint/key later.

