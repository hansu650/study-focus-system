# Implementation Completion Log

## Project
Study Focus (Desktop Pomodoro + Incentive System)

## Workspace
`D:\daima\cursor\合作项目`

## Date
2026-03-07

## Goal
Record completed backend, frontend, and desktop-guard milestones, plus debugging actions and verification outcomes.

## Completed Milestones

### Milestone A - Base Backend
1. Implemented auth APIs (`register`, `login`) with JWT.
2. Implemented dictionary APIs (`regions`, `schools`, `colleges`).
3. Implemented user profile APIs (`get me`, `update me`).

### Milestone B - Focus, Points, Leaderboard
1. Implemented focus session APIs:
   - start
   - complete
   - interrupt
   - abandon
   - list
2. Implemented point APIs:
   - balance
   - ledger list
3. Implemented leaderboard API:
   - period: day/month/year
   - scope: school/college

### Milestone C - Learning Module
1. Implemented daily question API.
2. Implemented AI chat API.
3. Added provider adapter support:
   - openai-compatible
   - anthropic-compatible

### Milestone D - O2O Redeem Module
1. Implemented redeem order APIs:
   - create order (deduct points)
   - list my orders
   - get order detail
   - verify by coupon token
   - cancel order (refund points)
2. Added anti-repeat verification checks and status transitions.

### Milestone E - Frontend MVP
1. Created standalone frontend workspace in `frontend/`.
2. Implemented dashboard-style single-page UI with:
   - login
   - register
   - profile summary
   - focus controls
   - active countdown timer
   - session history
   - point balance and ledger
   - leaderboard
   - daily question
   - AI chat
   - redeem order create/verify/list
3. Added exact local startup instructions in `frontend/README.md`.

### Milestone F - Desktop Guard Skeleton
1. Created standalone desktop workspace in `desktop/`.
2. Added Electron shell entry files:
   - `main.js`
   - `preload.js`
3. Added medium-strength local guard service:
   - blocked app process watch on Windows
   - always-on-top / maximize focus window policy
   - optional blocked-site control through a managed hosts-file section
4. Wired frontend and desktop bridge together:
   - guard status display
   - guard event log
   - auto-interrupt the running session when a blocked app is detected
5. Upgraded frontend visuals and testing guidance:
   - quick-fill register/login actions
   - better hero and panel hierarchy
   - clearer browser-vs-desktop separation

### Milestone G - Desktop Dependency Install
1. Installed Electron dependencies inside the project workspace.
2. Kept this install cache local to `desktop\.npm-cache` through a one-time environment variable.
3. Avoided creating `.npmrc` and avoided changing long-term npm configuration.
4. Confirmed `npm run check` passed after install.

## Issue and Resolution Summary (Brief)
1. `pip install -e .` failed (`TOMLDecodeError`): fixed by removing BOM from `pyproject.toml`.
2. MySQL connection refused (`10061`): fixed by starting MySQL service and validating port `3306` listening.
3. MySQL access denied (`1045`): fixed by correcting root password and syncing `.env` DB credentials.
4. PowerShell script parameter conflict (`Host` is reserved/read-only): fixed by renaming to `DbHost/DbPort/DbUser`.
5. SQL seed import failed under Chinese path: avoided `SOURCE <path>` dependency and switched to path-safe script execution.
6. `seed_demo.ps1` became corrupted during edits: rewrote the script from scratch and revalidated parser syntax.
7. bcrypt warning/error with passlib (`password > 72 bytes` behavior mismatch): pinned `bcrypt==4.0.1` for compatibility.
8. `uvicorn` command not recognized: fixed by activating conda env and using `python -m uvicorn ...`.
9. Swagger `422` confusion: clarified that `422` in docs is an expected schema response type, not always a runtime failure.
10. AI provider format mismatch (ModelScope uses Anthropic-style messages): added dual-format adapter (`openai_compatible` + `anthropic_compatible`).
11. Local outbound socket restriction during validation: retried with allowed execution mode and completed live API verification.
12. Frontend workspace was missing and startup steps were ambiguous: created `frontend/` and added exact CMD startup commands.
13. A heavy Node-based scaffold would increase local setup friction early: used a zero-install static MVP first so validation can proceed immediately.
14. Frontend needed a real smoke check instead of file-only delivery: served it locally and verified `index.html`, `app.js`, and `styles.css` all returned `200`.
15. Desktop shell implementation needed to stay storage-aware: created the Electron project files and docs first, without installing `node_modules` yet.
16. Medium-strength site blocking needed to be reversible: restricted hosts-file edits to a managed marker section only.
17. Long one-shot shell writes became unreliable for large frontend files: switched to chunked writes for large JS content.
18. PowerShell regex replacement inserted literal newline tokens into desktop guard code: replaced that approach with a clean full-file rewrite.
19. First Electron install attempt timed out against `registry.npmjs.org`: retried with a one-time registry mirror and Electron mirror.
20. User did not want persistent npm cache config: used only `npm_config_cache` environment variable for the current install session and did not create `.npmrc`.
21. Local `npm run check` first failed due tool sandbox refresh, not project code: reran with allowed execution mode and confirmed the script passed.

## End-to-End Verification
1. Backend compile checks passed for all modules.
2. Auth flow passed: register -> login -> current user retrieval.
3. Focus flow passed: start -> complete -> points settled.
4. Redeem flow passed: create -> verify -> cancel(second order) -> ledger consistency.
5. Learning flow passed:
   - daily question returns `200`
   - ai-chat returns `200` with configured ModelScope credentials
6. Frontend delivery smoke test passed:
   - `GET /` -> `200`
   - `GET /src/app.js` -> `200`
   - `GET /src/styles.css` -> `200`
7. Desktop syntax validation passed:
   - `node --check desktop/main.js`
   - `node --check desktop/preload.js`
   - `node --check desktop/guard/focusGuard.js`
8. Desktop Windows script parse passed:
   - `siteBlock.ps1` parsed successfully through PowerShell scriptblock validation
9. Desktop dependency validation passed:
   - `npm install` completed successfully
   - `npm run check` completed successfully

## Current Runtime Notes
1. Database: local MySQL 8, schema initialized and seeded.
2. Python: conda env `study_focus_backend`.
3. Backend API docs: `http://127.0.0.1:8000/docs`.
4. Frontend local entry: `http://127.0.0.1:5173`.
5. Desktop dependency paths now exist inside the workspace:
   - `D:\daima\cursor\合作项目\desktop\node_modules`
   - `D:\daima\cursor\合作项目\desktop\.npm-cache`
   - `D:\daima\cursor\合作项目\desktop\package-lock.json`

## Next Development Phase
1. Run the first real Electron desktop session test.
2. Add merchant role-based auth for redeem verification endpoint.
3. Add automated tests (pytest + frontend smoke checks).
4. Add stronger desktop guard options such as foreground-window checks and optional terminate-on-violation mode.
5. Migrate the frontend MVP to Vue 3 + Electron when interaction details are stable.

## Latest Validation Update - Desktop Live Checks
1. Ran a live desktop guard process-watch test outside the sandbox.
2. Started guard with blocked app list containing `ping.exe`.
3. Spawned a real `ping` process and confirmed guard emitted `blocked_app_detected`.
4. Result: `GUARD_PROCESS_WATCH=OK`.
5. Launched the Electron app once for a smoke test and confirmed an `electron` process started successfully.
6. Result: `ELECTRON_SMOKE=OK`.
7. The smoke test process was then terminated cleanly after validation.
8. Live system hosts-file write was not executed automatically in this round because it is administrator-sensitive and affects machine networking.

## Latest Repository Safety Update
1. Confirmed the real MySQL password exists only in `backend/.env`.
2. Confirmed `.env` is ignored by `.gitignore`, while `backend/.env.example` keeps placeholder values for safe sharing.
3. Confirmed this workspace is not yet initialized as a git repository.
4. Strengthened `.gitignore` to exclude `*.egg-info/` build artifacts before GitHub upload.

## Pre-GitHub Handoff Notes
1. Current browser and desktop core flows are working.
2. AI integration still needs another debugging pass in the user's local environment, even though earlier API validation succeeded in controlled checks.
3. The codebase is being uploaded first so iteration can continue from GitHub with a cleaner collaboration flow.

## Known Open Issues
1. AI call path is not fully stable in the latest user-side manual test and needs follow-up debugging after repository upload.
2. The desktop website blacklist path exists in code, but a full live validation with administrator permission is still pending.

## Pending Manual Validation
1. Browser AI chat should be retested after confirming the active ModelScope key and backend runtime environment.
2. Website blacklist should be retested in Electron under administrator mode with sample domains such as `youtube.com` and `bilibili.com`.
3. Process blacklist validation already passed and should be treated as the current confirmed medium-strength anti-distraction feature.

## Sprint 1 Documentation Update
1. Created and switched to the dedicated working branch `sprint1-qin-tian` for Sprint 1 document preparation.
2. Reviewed `Something_to_write/计划.md` and limited the document scope to Sprint 1 deliverables only.
3. Updated `12_ Project Problem Domain Activity Sheet.docx` to align the group naming with the current Sprint 1 submission set.
4. Completed `SPRINT 1A - Retrospective Activity Sheet.docx` with Sprint 1 summary, accomplishments, and further-work notes.
5. Completed the relevant Sprint 1 section in `Team Leader Report Template.docx` with finished work, pending work, and current schedule status.
6. Added Sprint 1 meeting records to `Team Meeting Summary Template.docx` and kept later unused rows untouched.
7. Confirmed the current open issues are still the AI call follow-up and the pending administrator-mode validation for website blacklist control.

## Sprint 2 Kickoff Review - 2026-03-11
1. Re-read the backend, frontend, Electron guard, schemas, and SQL structure before making Sprint 2 changes.
2. Confirmed the architecture is still a thin static frontend + FastAPI backend + Electron desktop shell, with business logic concentrated in service-layer modules.
3. Identified the first Sprint 2 priority as the focus settlement loophole in `backend/app/services/focus_service.py`.
4. Confirmed that `complete_session()` had been defaulting `actual_minutes` to `planned_minutes`, which meant a user could finish immediately and still receive full points.
5. Identified the second priority as redeem verification authorization in `backend/app/api/v1/redeem_orders.py`, because `/verify` currently requires only a logged-in user and has no merchant-role boundary yet.
6. Confirmed the AI instability issue still matters, but it is lower priority than the focus reward integrity bug.
7. Confirmed the desktop website blacklist path still needs clearer validation messaging and later administrator-mode live testing.
8. Planned Sprint 2 execution order: fix focus reward integrity first, then tighten redeem verification boundaries, then improve AI stability and desktop site-block validation feedback.

## Sprint 2 Update - Focus Reward Integrity Fix - 2026-03-11
1. Updated `backend/app/services/focus_service.py` so a running session can only be completed after the planned duration has actually elapsed.
2. Removed the previous trust in client-provided completion minutes for reward settlement.
3. The backend now rejects early completion attempts with a clear error message and keeps interruption as the intended early-exit path.
4. Added `backend/tests/test_focus_service.py` to cover both failure and success paths for session completion settlement.
5. Verified with `python -m unittest discover -s tests -v` in `backend/` and confirmed both focus completion tests passed.
## Sprint 2 Update - Interrupt Resume Flow - 2026-03-11
1. Adjusted focus lifecycle semantics based on teacher feedback: `interrupt` now preserves elapsed time for resume, while `abandon` clears elapsed time.
2. Updated `backend/app/services/focus_service.py`:
   - interrupted sessions now keep `actual_minutes`, remain unsettled, and can be resumed
   - added `resume_session()` to continue from saved elapsed time
   - abandoned sessions now reset `actual_minutes` to `0`
   - blocked creating a new session when an unfinished interrupted session already exists
3. Added `POST /api/v1/focus-sessions/{id}/resume` in `backend/app/api/v1/focus_sessions.py`.
4. Updated the frontend focus panel so interrupted sessions can be resumed from the dashboard without losing saved progress.
5. Updated the desktop guard interruption flow so a guard-triggered interrupt now pauses the session instead of clearing its saved elapsed time.
6. Expanded `backend/tests/test_focus_service.py` to cover interrupt, resume, abandon, and the interrupted-session start guard.
7. Verified with:
   - `python -m unittest discover -s tests -v`
   - `python -m compileall app tests`
   - `node --check frontend/src/app.js`

## Sprint 2 Update - Redeem Verification Boundary - 2026-03-11
1. Tightened the redeem verification path so `/api/v1/redeem-orders/verify` is no longer available to any logged-in user without extra merchant proof.
2. Added `REDEEM_VERIFY_TOKEN` to backend configuration and `.env.example`.
3. Updated `backend/app/services/redeem_service.py` to require:
   - a configured merchant verify token
   - a valid `X-Merchant-Token` request header
   - `verifier_id` matching the current logged-in username
4. Updated `backend/app/api/v1/redeem_orders.py` to return clearer HTTP statuses for verify failures:
   - `403` for permission problems
   - `503` when merchant verification is not configured
   - `400` for business-state errors such as expired or already-verified orders
5. Updated the frontend verify form to collect the merchant token and send it via `X-Merchant-Token`.
6. Bound the frontend verifier ID to the current logged-in username so the UI no longer encourages verifier spoofing.
7. Added `backend/tests/test_redeem_service.py` to cover token configuration, invalid token rejection, verifier mismatch rejection, and successful verification.

## Sprint 2 Update - Desktop Site Block Feedback - 2026-03-11
1. Improved `desktop/scripts/windows/siteBlock.ps1` so it now checks for administrator permission before editing the Windows hosts file.
2. Switched hosts-file writing to an explicit UTF-8 without BOM write path and wrapped it in clearer error handling.
3. Updated `desktop/guard/focusGuard.js` so site-block failures are classified more clearly, especially the administrator-required case.
4. Added `siteBlockReason` to guard status and surfaced a clearer `permission_required` state for renderer messaging.
5. Updated the frontend desktop-guard status note so Electron now tells the user directly when site blocking needs administrator launch, instead of only showing a vague failure.
6. Updated the blocked-app guard copy to match the new pause/resume semantics introduced earlier in Sprint 2.

## Sprint 2 Scope Note - AI Deferred - 2026-03-11
1. AI stability hardening work was intentionally deferred in this round after the user chose to postpone AI changes and explore cloud deployment options for a distilled model later.

## Sprint 2 Validation - 2026-03-11
1. Verified with `python -m unittest discover -s tests -v`.
2. Verified with `python -m compileall app tests`.
3. Verified frontend syntax with `node --check frontend/src/app.js`.
4. Verified desktop guard syntax with `node --check desktop/guard/focusGuard.js`.
5. Verified PowerShell parsing with `[scriptblock]::Create((Get-Content 'desktop/scripts/windows/siteBlock.ps1' -Raw))`.
## Sprint 2 Update - Feedback Collection Module - 2026-03-11
1. Added a new `feedback_message` table in `db/schema.sql` and created the matching backend model, schema, service, and API route files.
2. Added authenticated feedback APIs so logged-in users can submit improvement suggestions with `POST /api/v1/feedback` and review their recent submissions with `GET /api/v1/feedback/my`.
3. The feedback payload now stores category, title, content, optional contact email, and timestamps, which makes the suggestion box a real data collection path instead of a frontend-only mock.
4. Updated the frontend dashboard with a dedicated feedback panel so users can leave improvement ideas directly inside the product and immediately see their recent messages.
5. Wired feedback loading into the normal dashboard refresh flow so new submissions appear after save without manual page reload.
6. Added `backend/tests/test_feedback_service.py` to cover trim behavior, post-trim validation, and newest-first ordering.

## Sprint 2 Validation Refresh - 2026-03-11
1. Re-verified with `python -m unittest discover -s tests -v` after the feedback module landed.
2. Re-verified with `python -m compileall app tests`.
3. Re-verified frontend syntax with `node --check frontend/src/app.js`.
## Sprint 2 Note - Feedback DB Upgrade Script - 2026-03-11
1. Added `db/add_feedback_message.sql` so an already-initialized local MySQL database can enable the feedback module without a full schema reset.
## Sprint 2 AI Direction Update - 2026-03-11
1. Decided to keep the current AI path on the user's existing free API for Sprint 2 instead of switching to a self-hosted distilled model.
2. The main reason is delivery risk control: the current `backend/app/services/ai_service.py` adapter already supports provider switching, while self-hosting would add new deployment and runtime variables late in the sprint.
3. This keeps the AI feature aligned with the present backend design and leaves self-hosted distilled-model deployment as a later optimization path rather than a Sprint 2 dependency.

## Sprint 2 Manual Test Checklist - 2026-03-11
1. If the local MySQL database was initialized before the feedback module was added, run `db/add_feedback_message.sql` once before testing the new feedback feature.
2. Start the backend with the configured AI API environment variables and verify `http://127.0.0.1:8000/docs` loads successfully.
3. Start the static frontend on port `5173` and confirm login, dashboard refresh, and authenticated API calls work normally.
4. Optional but recommended: start Electron and confirm desktop guard status appears in the dashboard.
5. Focus flow manual check:
   - start a session
   - interrupt it and confirm saved minutes remain
   - resume it and confirm the timer continues
   - abandon it and confirm the session is dropped without retained progress
6. Redeem flow manual check:
   - create a redeem order
   - verify it with the configured merchant token
   - confirm invalid or missing token requests are rejected
7. Feedback flow manual check:
   - submit one message in the new feedback panel
   - refresh the dashboard
   - confirm the message appears in the recent feedback list
8. AI flow manual check:
   - send one simple study question through the dashboard
   - confirm the reply returns through the configured free API
   - if the provider limit is hit, record the error message and treat it as a quota issue rather than a backend routing failure
9. Website blacklist manual check remains pending under administrator-launched Electron and should be tested separately with sample domains such as `youtube.com` and `bilibili.com`.
## Sprint 2 Fix - AI UTF-8 Request Transport - 2026-03-11
1. Replaced the previous `urllib`-based AI HTTP transport in `backend/app/services/ai_service.py` with an explicit UTF-8 JSON request flow.
2. The goal of this change is to avoid the previous request-path encoding failure observed when sending Chinese questions such as `你是谁`.
3. Added `backend/tests/test_ai_service.py` to verify that Chinese prompt content is emitted as UTF-8 in the outbound provider request body.

## Sprint 2 Fix - Resume Exact Remaining Time - 2026-03-11
1. Updated `backend/app/services/focus_service.py` so interrupted sessions now resume from the exact saved elapsed duration instead of only the floored whole-minute value.
2. Updated `frontend/src/app.js` so the paused-session countdown is rendered from the exact saved elapsed time, which means an interrupt at `24:15` remaining will now resume from `24:15` rather than jumping back to `25:00`.
3. Added a backend test for sub-minute pause/resume continuity in `backend/tests/test_focus_service.py`.

## Sprint 2 Validation Refresh 2 - 2026-03-11
1. Re-verified with `python -m unittest discover -s tests -v` after the AI transport and exact-resume fixes.
2. Re-verified with `python -m compileall app tests`.
3. Re-verified frontend syntax with `node --check frontend/src/app.js`.
## Sprint 2 Note - Manual Smoke Scripts - 2026-03-11
1. Added `backend/scripts/smoke_ai_chat.py` for direct login-plus-AI endpoint testing.
2. Added `backend/scripts/smoke_focus_resume.py` for direct interrupt/resume remaining-time testing.
## Sprint 2 Update - Leaderboard Demo Scope Refresh - 2026-03-11
1. Expanded the leaderboard backend to support college, school, and cross-school scopes with optional school and college selection.
2. Enriched leaderboard rows with school and college names so the UI can show full campus labels during demos.
3. Simplified the redeem panel to focus on coupon-code generation and generated-code display instead of making verification the main workflow.
4. Updated demo dictionary seed data to use full campus names such as `Hubei University` and `Wuhan University of Science and Technology`.
5. Added `db/add_demo_leaderboard_dicts.sql` for incremental demo dictionary updates on existing databases.
6. Added `db/add_demo_leaderboard_samples.sql` so existing databases can seed one Hubei University college sample and one Wuhan University of Science and Technology sample for leaderboard demos.

## Sprint 2 Update - Redeem Generate-Only Cleanup - 2026-03-11
1. Removed the remaining dashboard-side redeem verification and cancel actions so the user flow now focuses on generating and copying coupon codes only.
2. Cleaned the leaderboard context strings and campus labels so demo separators render as normal `/` text instead of encoding-garbled characters.
3. Kept the backend redeem verify endpoint available for future merchant flows, but it is no longer part of the main Sprint 2 demo path.
## Sprint 2 Update - Leaderboard Visual Polish - 2026-03-11
1. Refreshed the leaderboard presentation in `frontend/src/app.js` and `frontend/src/styles.css` so ranking entries now render as showcase cards instead of plain rows.
2. Highlighted the top three positions with distinct visual treatment and added clearer score, campus, and focus-stat chips for demo readability.
3. Kept the college, school, and all-schools filter structure unchanged while improving the visual hierarchy for presentation use.
## Sprint 2 Update - Guard Violation Clears Progress - 2026-03-11
1. Adjusted the desktop-guard violation flow so blocked-app detection now abandons the active session instead of creating a resumable interrupt.
2. This means guard-triggered violations now clear saved progress and award zero points, while manual interrupt still remains resumable.
3. Updated the desktop guard event wording to match the new no-reward abandonment behavior for demos and teacher review.
## Sprint 2 Update - Blocked Site Detection And Popup - 2026-03-12
1. Extended the Electron guard so website monitoring now also inspects visible browser window titles for blocked domain keywords such as `bilibili` and `youtube`.
2. Added desktop popup alerts for blocked app and blocked site violations so the user gets an immediate warning window when focus rules are broken.
3. Updated the renderer guard flow so both blocked apps and blocked sites now end the session with abandon-style clearing and zero reward.
## Sprint 2 Update - Relaxed Full-Screen Test Policy - 2026-03-12
1. Adjusted the Electron focus-window policy so the app no longer pins itself above every other window during testing.
2. FULL_LOCK still uses full-screen presentation, but users can now Alt+Tab away to deliberately open blocked apps or blocked websites for validation.
3. This keeps the demo visually strong while making manual guard testing practical.

## Sprint 4 UI + Dual-Mode Update - 2026-03-18
1. Added dual monitoring behavior:
   - website mode now checks whether the user leaves the Guide Page after consent
   - desktop mode still uses Electron for stronger app/site monitoring after consent
2. Added a 15-second grace window before website-mode leave-page violations are settled.
3. Added delete support to the local plan notebook so tasks can now be removed as well as checked off.
4. Simplified the visible daily-question UI on the Learning page by removing extra top badges, refresh action, inline answer-result text, and hint copy.
5. Shortened the feedback headline to `Collect improvement notes.` for a cleaner demo surface.
6. Hardened AI response parsing so OpenAI-compatible providers that return non-`choices` payload shapes can still produce an answer instead of failing immediately.
7. Updated frontend versioned asset references again to force browsers onto the latest static bundle.

## Current Follow-Up Notes - 2026-03-18
1. Website mode is intentionally honest about its limits: it detects leaving the study page, not exact external websites.
2. Desktop mode is still the only path that can inspect blocked apps and browser-window titles locally.
3. AI should now be retested against the user's active provider credentials after restarting the backend process.

## Sprint 4 Browser Popup Follow-Up - 2026-03-19
1. Added a stronger browser-mode violation notice flow so leaving the Guide Page now persists a pending warning and shows a blocking alert when the user returns.
2. Kept the website-mode grace window at 15 seconds, but made the abandon result much more explicit than a background toast.
3. Removed the `NONE` option from the Guide Page lock-mode selector so the public demo no longer suggests an unguarded mode.

## Sprint 4 Guide Page Cleanup - 2026-03-19
1. Removed the visible `Lock Mode` selector from the Guide Page form and now submit `APP_BLOCK` as the default mode behind the scenes so the UI stays simpler for the web demo.
2. Removed visible `Lock ...` badges from the running-session and session-history summaries so the public focus flow no longer exposes extra mode jargon.
3. Reworked website-mode away tracking to persist the leave timestamp and trigger reason, then settle the violation when the user returns to the Guide Page instead of relying on background-tab timers.
4. Bumped the frontend asset version to `sprint4r15` so the updated Guide Page / Learning rename and website-mode popup behavior can break through cached static files.

## Sprint 4 Learning Rename + Return Fix - 2026-03-19
1. Renamed the main focus surface from `Guide Page` to `Learning` and renamed the former daily-question route to `Break Space` so the navigation no longer shows two competing learning labels.
2. Added `pagehide` tracking plus a post-refresh return check so same-tab jumps to external sites like bilibili can still be settled when the user comes back to the Learning page.
3. Changed browser-mode violation notices so they only render on the Learning page itself instead of popping on unrelated routes such as Feedback or Rankings.

## Sprint 4 AI Stability Follow-Up - 2026-03-19
1. Expanded the OpenAI-compatible backend adapter so it now parses more payload shapes, including legacy `choices[].text`, nested response wrappers, and provider error payloads.
2. Added a backend fallback from `chat/completions` to `responses` when the primary endpoint returns an empty-but-successful body, which should reduce the `No choices in OpenAI response` failures seen in the web demo.
3. Added a lightweight frontend retry for AI chat so one transient 5xx or empty-response style failure does not immediately surface as a red error bubble to the user.
4. Bumped the frontend asset version to `sprint4r16` so the AI retry behavior can break through cached static files.

## Sprint 4 Auto-Complete Cleanup - 2026-03-19
1. Removed the visible `Complete Session` button from the Learning page because it was just a manual settlement control that added clutter to the demo.
2. Added automatic session completion when the countdown reaches zero, so points are still awarded without requiring an extra click.
3. Bumped the frontend asset version to `sprint4r17` so the button removal and auto-complete behavior can break through cached static files.

## Sprint 4 Showcase Seed Expansion - 2026-03-19
1. Expanded `db/add_demo_leaderboard_samples.sql` so demo data now covers richer rankings plus at least one row in each major business table: users, focus sessions, point ledger, daily question attempts, redeem orders, and feedback messages.
2. Added extra demo accounts across both schools and colleges so the day leaderboard looks fuller and no longer appears nearly empty during teacher demos.
3. Updated `seed_demo.ps1` to load the daily-question migration and the richer showcase seed set by default, so a fresh deployment can reach the same visible state as local testing with one command.
4. Updated `seed_leaderboard_demo.ps1` and `DEPLOYMENT.md` so existing environments can refresh only the showcase dataset without re-running the full schema bootstrap.
