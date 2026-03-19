# Backend Deployment Guide (FastAPI + MySQL + Nginx + systemd)

## 1. Target environment
1. Linux server (Ubuntu 22.04+ / CentOS 9+)
2. Python 3.11+
3. MySQL 8.0
4. Nginx

## 2. Prepare code
```bash
git clone <your-repo-url>
cd backend
cp .env.example .env
```

Update `.env` values:
1. `MYSQL_*`
2. `SECRET_KEY`
3. `AI_API_BASE` / `AI_API_KEY` / `AI_MODEL`

## 3. Install dependencies
### 3.1 Conda (recommended)
```bash
conda create -n study_focus_backend python=3.11 -y
conda activate study_focus_backend
pip install -r requirements.txt
pip install -e .
```

### 3.2 venv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## 4. Initialize database
```bash
pwsh ./scripts/init_db.ps1 -MysqlExe mysql -DbHost 127.0.0.1 -DbPort 3306 -DbUser root -DbPassword <your-password>
pwsh ./scripts/seed_demo.ps1 -MysqlExe mysql -DbHost 127.0.0.1 -DbPort 3306 -DbUser root -DbPassword <your-password>
```

`seed_demo.ps1` now loads the base dictionaries, the daily-question attempt table migration, and the richer showcase data used for rankings, rewards, feedback, and redeem demos.

If you only want to refresh the ranking/showcase records after the schema already exists, you can also run:
```bash
pwsh ./scripts/seed_leaderboard_demo.ps1 -MysqlExe mysql -DbHost 127.0.0.1 -DbPort 3306 -DbUser root -DbPassword <your-password>
```

## 5. Start service manually
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 6. systemd service
1. Edit `deploy/systemd/study-focus-api.service`.
2. Update `WorkingDirectory`, `EnvironmentFile`, and `ExecStart`.
3. Install and start:
```bash
sudo cp deploy/systemd/study-focus-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable study-focus-api
sudo systemctl start study-focus-api
sudo systemctl status study-focus-api
```

## 7. Nginx reverse proxy
1. Edit `deploy/nginx/study-focus.conf`.
2. Enable config:
```bash
sudo cp deploy/nginx/study-focus.conf /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Post-deploy checks
1. `GET /health` returns `{"status":"ok"}`.
2. `/docs` is reachable.
3. Register -> Login -> Get profile flow works.
4. Rankings, Break Space, Rewards, and Feedback all show seeded showcase content after the seed step.

## 9. Troubleshooting
1. `Access denied for user`: check DB user/password/privileges.
2. `ModuleNotFoundError`: verify active env and dependency install.
3. `401 Unauthorized`: token invalid/expired or wrong `SECRET_KEY`.
4. AI call failure: check OpenAI-compatible endpoint and key.
5. Empty rankings or empty demo tables: rerun `seed_demo.ps1` or `seed_leaderboard_demo.ps1` against the target database.
