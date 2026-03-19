# Study Focus Project Plan

## 1. Vision
Build a desktop-first study focus platform for college students with:
1. Pomodoro sessions and anti-distraction controls
2. AI-assisted learning support
3. O2O incentive loop: focus points -> print coupons

## 2. MVP Scope
1. User register/login with region/school/college binding
2. Pomodoro session creation, completion, interruption
3. Point ledger and balance tracking
4. School/college leaderboards (daily/monthly/yearly)
5. Daily question and AI chat (basic version)
6. Coupon redeem order + QR verification simulation
7. Frontend MVP dashboard for the full user flow
8. Desktop guard skeleton for medium-strength anti-distraction

## 3. Architecture
1. Current frontend MVP: static SPA in `frontend/`
2. Desktop shell: Electron in `desktop/`
3. Backend: FastAPI
4. Database: MySQL 8
5. Cache: Redis (optional in MVP)
6. AI adapter: OpenAI-compatible + Anthropic-compatible providers

## 4. Database Status
Completed core schema in `db/schema.sql`:
1. `app_user`
2. `focus_session`
3. `point_ledger`
4. `dict_region`, `dict_school`, `dict_college`
5. `redeem_order`

## 5. Backend Status
Completed in `backend/app`:
1. Auth APIs: register/login
2. Dictionary APIs: region/school/college queries
3. User APIs: get/update current profile
4. Focus session APIs: start/complete/interrupt/abandon/list
5. Point APIs: balance and ledger list
6. Leaderboard API: day/month/year + school/college
7. Learning APIs: daily question + AI chat adapter
8. Redeem APIs: create/list/get/verify/cancel
9. JWT auth dependency and SQLAlchemy session management

## 6. Frontend Status
Completed in `frontend/`:
1. Login form with quick-fill helper
2. Register form with quick-fill helper
3. User profile and summary metrics
4. Focus session controls and active timer
5. Session history panel
6. Point balance and point ledger panel
7. Leaderboard panel with period switching
8. Daily question panel
9. AI chat panel
10. Redeem order create/verify/list panel
11. Desktop guard status and event panel
12. Local API base configuration and token persistence

## 7. Desktop Guard Status
Completed in `desktop/`:
1. Electron shell bootstrap (`main.js`, `preload.js`)
2. Medium-strength guard service (`guard/focusGuard.js`)
3. Windows site-block script (`scripts/windows/siteBlock.ps1`)
4. Frontend bridge hooks for guard events and auto-interrupt behavior

## 8. Milestone Status
1. Milestone A: Completed
2. Milestone B: Completed
3. Milestone C: Completed
4. Milestone D: Completed
5. Milestone E: Frontend MVP Completed
6. Milestone F: Desktop Guard Skeleton Completed

## 9. Quality Gates
1. Schema migration scripts validated on MySQL 8
2. Compile checks passed for backend modules
3. End-to-end flow validated: register -> login -> focus -> points -> redeem -> verify
4. End-to-end flow validated: register -> login -> learning/daily-question -> learning/ai-chat
5. Frontend static delivery validated: `index.html`, `app.js`, `styles.css` return `200`
6. Desktop JS syntax validated: `main.js`, `preload.js`, `guard/focusGuard.js`
7. Windows site-block PowerShell script parsed successfully

## 10. Security
1. bcrypt for password hashing
2. JWT with expiration and secret rotation support
3. Server-side point calculation only
4. Idempotency guard for redeem verification
5. Audit-ready point ledger for deduction/refund events
6. Frontend stores only token and lightweight UI state in `localStorage`
7. Desktop site-block editing is isolated to a managed hosts section

## 11. Deployment
1. `backend/DEPLOYMENT.md` as runbook
2. systemd template in `backend/deploy/systemd/`
3. nginx template in `backend/deploy/nginx/`
4. bootstrap scripts in `backend/scripts/`
5. Frontend local runbook in `frontend/README.md`
6. Desktop local runbook in `desktop/README.md`

## 12. Next Actions
1. Install Electron locally and run the first real desktop session test
2. Add merchant role and permission boundaries for verify endpoint
3. Add automated API tests and frontend smoke tests
4. Add stronger desktop protections such as foreground-window checks and optional terminate-on-violation mode
5. Upgrade the frontend MVP into Vue 3 + Electron packaging when the flow is frozen

## 13. Current Delivery Mode - 2026-03-18
1. The project now supports two parallel focus-monitor modes:
   - Website mode: detect leaving the study page, switching tabs, or switching windows after user consent
   - Desktop mode: Electron-based app/site monitoring after user consent
2. Website mode is the deployable cloud path for the Tencent Cloud web release.
3. Desktop mode remains the stronger local option for demonstrations or stricter anti-distraction checks.
4. Both modes now require explicit user permission before monitoring starts.

## 14. Current UI Direction - 2026-03-18
1. The renamed Learning page remains the primary working surface after login.
2. Learning page is being reduced to the essentials: core question content plus AI chat, without extra quiz chrome.
3. Feedback copy is being simplified to shorter teacher-demo wording.
4. The local plan notebook is now treated as a lightweight session checklist with completion and deletion actions.
5. The website-mode leave-page grace window is now set to 15 seconds for less aggressive interruption during manual testing.
6. Website mode now uses an explicit abandon popup on return so browser-side violations are visible in demos instead of relying only on background toasts.
7. The renamed Learning page no longer exposes a public `Lock Mode` selector; web demos now start with the default lock behavior behind the scenes to keep the form simpler.
8. The former daily-question page is now presented as Break Space so the main work surface can own the `Learning` name without duplicate navigation labels.
9. AI chat now needs a stability layer on top of the provider integration so temporary empty-response failures do not immediately break the web demo.
10. The Learning page should prefer automatic completion when the timer reaches zero, so the demo flow does not depend on an extra manual completion button.

## 15. Demo Showcase Data - 2026-03-19
1. Ranking demos now need richer seed data so the leaderboard is visually convincing during local testing and cloud deployment.
2. The default demo seed path should populate every major business table, not just users, focus sessions, and point ledger rows.
3. The deployment runbook should explicitly mention the showcase seeding path so Tencent Cloud can be refreshed without manual SQL guessing.
