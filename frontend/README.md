# Frontend MVP


## Stack
1. Static HTML
2. Vanilla JavaScript
3. CSS

This frontend is a zero-install MVP.
It avoids Node.js build tooling for now so local validation stays simple.
The next stage can migrate it to Vue 3 + Electron after the interaction flow is stable.

## Directory
1. `index.html`
2. `src/app.js`
3. `src/styles.css`

## What Is New
1. Better visual hierarchy and layout polish
2. Quick-fill demo account buttons
3. Desktop guard status area
4. Guard event log area
5. Browser mode and Electron mode can share the same UI

## Start Backend (CMD)
Open a new `cmd` window and run:

```bat
cd /d D:\daima\cursor\合作项目\backend
call D:\kaifagongju\Anaconda\Scripts\activate.bat study_focus_backend

set AI_PROVIDER=anthropic_compatible
set AI_API_BASE=https://api-inference.modelscope.cn
set AI_API_KEY=REPLACE_WITH_YOUR_NEW_MODELSCOPE_KEY
set AI_MODEL=ZhipuAI/GLM-5

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend docs:
1. `http://127.0.0.1:8000/docs`
2. `http://127.0.0.1:8000/health`

## Start Frontend (CMD)
Open another `cmd` window and run:

```bat
cd /d D:\daima\cursor\合作项目\frontend
call D:\kaifagongju\Anaconda\Scripts\activate.bat study_focus_backend
python -m http.server 5173
```

Frontend page:
1. `http://127.0.0.1:5173`

## Quick Test Flow
1. Open the frontend page.
2. Confirm API Base is `http://127.0.0.1:8000/api/v1`.
3. Click `Fill Register Demo`.
4. Submit the register form once.
5. Click `Fill Login Demo`.
6. Login with the same username and password.
7. Start a focus session.
8. Complete the session.
9. Check points, ledger, leaderboard, daily question, AI chat, and redeem order.

## Browser Mode Vs Desktop Mode
Browser mode:
1. Full feature API flow
2. No real desktop process guard
3. No real site block

Desktop mode:
1. Same UI inside Electron
2. Window always-on-top focus mode
3. Blocked app detection
4. Optional blocked-site control through the Windows hosts file

## Notes
1. The frontend stores token and lightweight UI state in `localStorage`.
2. If you rotate the AI key, restart the backend window.
3. If port `5173` is occupied, replace it with another port such as `5174`.
4. Desktop install steps are documented in `D:\daima\cursor\合作项目\desktop\README.md`.
