# Study Focus Desktop

## Goal
Provide a desktop shell for the existing Study Focus frontend with medium-strength anti-distraction controls.

## Current Strategy
1. Reuse the existing `frontend/` dashboard.
2. Add an Electron shell in `desktop/`.
3. Add a local focus guard with these responsibilities:
   - keep the window visible and always on top during focus sessions
   - monitor blocked process names on Windows
   - attempt local blocked-site control through the Windows `hosts` file
   - send violation events back to the frontend so the session can be interrupted without points

## Medium-Strength Guard Scope
This is intentionally not a kernel-level lock.
It is designed to be practical, reversible, and easier to deploy on student PCs.

Included:
1. Window maximize / always-on-top behavior
2. Blocked app process watch (`Get-Process` polling)
3. Optional blocked-site `hosts` injection
4. Violation event push to renderer

Not included yet:
1. Kernel or driver-level process blocking
2. Browser extension level URL tracking
3. Group policy or kiosk-mode hard lock
4. Admin service that survives user termination

## Files
1. `package.json`
2. `main.js`
3. `preload.js`
4. `guard/focusGuard.js`
5. `scripts/windows/siteBlock.ps1`

## One-Time Install With Project-Local Cache (CMD)
This method does not write `.npmrc` and does not change long-term npm config.
It uses a one-time environment variable only for the current terminal session.

```bat
cd /d D:\daima\cursor\合作项目\desktop
set npm_config_cache=D:\daima\cursor\合作项目\desktop\.npm-cache
set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
npm install --registry=https://registry.npmmirror.com
```

## Actual Install Result
Installed successfully with:
1. `desktop\node_modules`
2. `desktop\.npm-cache`
3. `desktop\package-lock.json`

No `.npmrc` was created by this flow.

## Start Desktop App (CMD)
After install:

```bat
cd /d D:\daima\cursor\合作项目\desktop
npm run start
```

## Local Syntax Check
```bat
cd /d D:\daima\cursor\合作项目\desktop
npm run check
```

## Verification Status
1. Electron package installed successfully.
2. `npm run check` passed.
3. `guard/focusGuard.js` syntax is valid.
4. `scripts/windows/siteBlock.ps1` parses successfully.

## How Site Blocking Works
1. The app prepares a managed block section in the Windows `hosts` file.
2. Domains are redirected to `127.0.0.1`.
3. The section is removed when the guard stops.

Important:
1. Writing `hosts` normally requires administrator permission.
2. If that permission is unavailable, process watch still works, but site blocking will be skipped.
3. The script only edits the section between `# STUDY_FOCUS_BLOCK_START` and `# STUDY_FOCUS_BLOCK_END`.

## Disk Cleanup
If you want to reclaim space later, delete:
1. `D:\daima\cursor\合作项目\desktop\node_modules`
2. `D:\daima\cursor\合作项目\desktop\.npm-cache`
3. `D:\daima\cursor\合作项目\desktop\package-lock.json`

CMD cleanup:

```bat
rd /s /q D:\daima\cursor\合作项目\desktop\node_modules
rd /s /q D:\daima\cursor\合作项目\desktop\.npm-cache
del D:\daima\cursor\合作项目\desktop\package-lock.json
```

## Live Validation Notes
1. Desktop guard process watch was validated with a real blocked process (`ping.exe`).
2. Electron smoke launch was validated successfully.
3. A live hosts-file modification test was intentionally not run automatically because it requires administrator-level system changes.
