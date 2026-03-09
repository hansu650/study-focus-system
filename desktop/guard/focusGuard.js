const path = require("node:path");
const { execFile } = require("node:child_process");
const { promisify } = require("node:util");

const execFileAsync = promisify(execFile);

function createFocusGuard({ emit = () => {} } = {}) {
  const state = {
    active: false,
    lockMode: "NONE",
    sessionId: null,
    blockedApps: [],
    blockedSites: [],
    monitorIntervalMs: 3000,
    monitorTimer: null,
    isChecking: false,
    siteBlockState: "inactive",
    lastViolation: null,
  };

  async function start(payload = {}, windowRef = null) {
    if (state.active || state.monitorTimer || state.siteBlockState === "active") {
      await stop(windowRef);
    }

    state.active = true;
    state.lockMode = payload.lockMode || "NONE";
    state.sessionId = payload.sessionId || null;
    state.blockedApps = normalizeApps(payload.blockedApps || []);
    state.blockedSites = normalizeDomains(payload.blockedSites || []);
    state.lastViolation = null;
    state.siteBlockState = "inactive";

    applyWindowPolicy(windowRef, state.lockMode);

    if (state.blockedSites.length > 0 && supportsSiteBlock()) {
      try {
        await runSiteBlockScript("Apply", state.blockedSites);
        state.siteBlockState = "active";
        emit(buildGuardEvent("site_block_enabled", {
          message: `Blocked ${state.blockedSites.length} distraction domains.`,
        }));
      } catch (error) {
        state.siteBlockState = "error";
        emit(buildGuardEvent("site_block_error", {
          message: `Site block was skipped: ${error.message}`,
        }));
      }
    }

    if (state.blockedApps.length > 0 && supportsProcessWatch()) {
      state.monitorTimer = setInterval(() => {
        void checkBlockedProcesses(windowRef);
      }, state.monitorIntervalMs);
      await checkBlockedProcesses(windowRef);
    }

    emit(buildGuardEvent("guard_state", {
      message: "Desktop focus guard enabled.",
      status: getStatus(),
    }));

    return getStatus();
  }

  async function stop(windowRef = null) {
    const hadActiveGuard = state.active || Boolean(state.monitorTimer) || state.siteBlockState === "active";

    if (state.monitorTimer) {
      clearInterval(state.monitorTimer);
      state.monitorTimer = null;
    }

    if (state.siteBlockState === "active") {
      try {
        await runSiteBlockScript("Clear", []);
      } catch (error) {
        emit(buildGuardEvent("site_block_error", {
          message: `Site block cleanup failed: ${error.message}`,
        }));
      }
    }

    releaseWindowPolicy(windowRef);

    state.active = false;
    state.lockMode = "NONE";
    state.sessionId = null;
    state.blockedApps = [];
    state.blockedSites = [];
    state.siteBlockState = "inactive";

    if (hadActiveGuard) {
      emit(buildGuardEvent("guard_state", {
        message: "Desktop focus guard disabled.",
        status: getStatus(),
      }));
    }

    return getStatus();
  }

  function getStatus() {
    return {
      available: true,
      active: state.active,
      lockMode: state.lockMode,
      sessionId: state.sessionId,
      blockedApps: [...state.blockedApps],
      blockedSites: [...state.blockedSites],
      monitorIntervalMs: state.monitorIntervalMs,
      siteBlockState: state.siteBlockState,
      lastViolation: state.lastViolation,
      platform: process.platform,
      supports: {
        processWatch: supportsProcessWatch(),
        siteBlock: supportsSiteBlock(),
        windowLock: true,
      },
    };
  }

  async function checkBlockedProcesses(windowRef) {
    if (!state.active || state.blockedApps.length === 0 || state.isChecking) {
      return;
    }

    state.isChecking = true;

    try {
      const runningProcesses = await listProcessNames();
      const hit = state.blockedApps.find((item) => runningProcesses.has(item));
      if (!hit) {
        return;
      }

      const violation = buildGuardEvent("blocked_app_detected", {
        processName: hit,
        message: `Blocked app detected: ${hit}. Interrupt this session.`,
      });

      if (!isDuplicateViolation(state.lastViolation, violation)) {
        state.lastViolation = violation;
        focusWindow(windowRef, state.lockMode);
        emit(violation);
      }
    } finally {
      state.isChecking = false;
    }
  }

  async function listProcessNames() {
    const script = [
      "$names = Get-Process | Select-Object -ExpandProperty ProcessName",
      "$names | ConvertTo-Json -Compress",
    ].join("; ");

    const { stdout } = await execFileAsync(
      "powershell.exe",
      ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
      { windowsHide: true, maxBuffer: 1024 * 1024 }
    );

    const parsed = safeParseJson(stdout.trim());
    const names = Array.isArray(parsed) ? parsed : typeof parsed === "string" ? [parsed] : [];
    return new Set(names.map(normalizeAppName).filter(Boolean));
  }

  async function runSiteBlockScript(mode, domains) {
    const scriptPath = path.join(__dirname, "..", "scripts", "windows", "siteBlock.ps1");
    const args = [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      scriptPath,
      "-Mode",
      mode,
      "-DomainsCsv",
      domains.join(","),
    ];

    try {
      await execFileAsync("powershell.exe", args, {
        windowsHide: true,
        maxBuffer: 1024 * 1024,
      });
    } catch (error) {
      const stderr = String(error.stderr || error.message || "Site block failed.").trim();
      throw new Error(stderr || "Site block failed.");
    }
  }

  return {
    start,
    stop,
    getStatus,
  };
}

function buildGuardEvent(type, extra = {}) {
  return {
    type,
    detectedAt: new Date().toISOString(),
    ...extra,
  };
}

function isDuplicateViolation(previousViolation, nextViolation) {
  if (!previousViolation || !nextViolation) {
    return false;
  }

  if (previousViolation.type !== nextViolation.type) {
    return false;
  }

  if (previousViolation.processName !== nextViolation.processName) {
    return false;
  }

  const previousAt = new Date(previousViolation.detectedAt).getTime();
  const nextAt = new Date(nextViolation.detectedAt).getTime();
  return Number.isFinite(previousAt) && Number.isFinite(nextAt) && nextAt - previousAt < 15000;
}

function applyWindowPolicy(windowRef, lockMode) {
  if (!windowRef || windowRef.isDestroyed()) {
    return;
  }

  windowRef.setAlwaysOnTop(true, "screen-saver");
  windowRef.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  if (lockMode === "FULL_LOCK") {
    windowRef.setFullScreen(true);
  } else {
    if (windowRef.isMinimized()) {
      windowRef.restore();
    }
    windowRef.maximize();
  }

  focusWindow(windowRef, lockMode);
}

function releaseWindowPolicy(windowRef) {
  if (!windowRef || windowRef.isDestroyed()) {
    return;
  }

  try {
    windowRef.setFullScreen(false);
    windowRef.setAlwaysOnTop(false);
    windowRef.setVisibleOnAllWorkspaces(false);
    windowRef.flashFrame(false);
  } catch {
    // Ignore release failures when the window is closing.
  }
}

function focusWindow(windowRef, lockMode) {
  if (!windowRef || windowRef.isDestroyed()) {
    return;
  }

  if (windowRef.isMinimized()) {
    windowRef.restore();
  }

  if (lockMode === "FULL_LOCK") {
    windowRef.setFullScreen(true);
  }

  windowRef.show();
  windowRef.focus();
  windowRef.flashFrame(true);
  setTimeout(() => {
    if (!windowRef.isDestroyed()) {
      windowRef.flashFrame(false);
    }
  }, 1200);
}

function normalizeApps(values) {
  return Array.from(new Set(values.map(normalizeAppName).filter(Boolean)));
}

function normalizeDomains(values) {
  return Array.from(new Set(values.map(normalizeDomain).filter(Boolean)));
}

function normalizeAppName(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/\.exe$/u, "");
}

function normalizeDomain(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/^https?:\/\//u, "")
    .replace(/^www\./u, "")
    .replace(/\/.*$/u, "");
}

function supportsProcessWatch() {
  return process.platform === "win32";
}

function supportsSiteBlock() {
  return process.platform === "win32";
}

function safeParseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

module.exports = {
  createFocusGuard,
};
