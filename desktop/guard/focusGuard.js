const path = require("node:path");
const { execFile } = require("node:child_process");
const { promisify } = require("node:util");

const execFileAsync = promisify(execFile);
const BROWSER_PROCESS_NAMES = new Set(["chrome", "msedge", "firefox", "brave", "opera", "iexplore"]);

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
    siteBlockReason: null,
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
    state.siteBlockReason = null;

    applyWindowPolicy(windowRef, state.lockMode);

    if (state.blockedSites.length > 0 && supportsSiteBlock()) {
      try {
        await runSiteBlockScript("Apply", state.blockedSites);
        state.siteBlockState = "active";
        state.siteBlockReason = `Blocked ${state.blockedSites.length} distraction domains.`;
        emit(buildGuardEvent("site_block_enabled", {
          message: state.siteBlockReason,
        }));
      } catch (error) {
        const siteBlockError = interpretSiteBlockError(error);
        state.siteBlockState = siteBlockError.state;
        state.siteBlockReason = siteBlockError.message;
        emit(buildGuardEvent("site_block_error", {
          message: siteBlockError.message,
        }));
      }
    }

    const shouldMonitorViolations = (state.blockedApps.length > 0 || state.blockedSites.length > 0) && supportsProcessWatch();
    if (shouldMonitorViolations) {
      state.monitorTimer = setInterval(() => {
        void checkGuardViolations(windowRef);
      }, state.monitorIntervalMs);
      await checkGuardViolations(windowRef);
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
        const siteBlockError = interpretSiteBlockError(error);
        emit(buildGuardEvent("site_block_error", {
          message: `Site block cleanup failed: ${siteBlockError.message}`,
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
    state.siteBlockReason = null;

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
      siteBlockReason: state.siteBlockReason,
      lastViolation: state.lastViolation,
      platform: process.platform,
      supports: {
        processWatch: supportsProcessWatch(),
        siteBlock: supportsSiteBlock(),
        windowLock: true,
      },
    };
  }

  async function checkGuardViolations(windowRef) {
    if (!state.active || state.isChecking || (!state.blockedApps.length && !state.blockedSites.length)) {
      return;
    }

    state.isChecking = true;

    try {
      if (state.blockedApps.length > 0) {
        const runningProcesses = await listProcessNames();
        const appHit = state.blockedApps.find((item) => runningProcesses.has(item));
        if (appHit) {
          emitViolation(windowRef, buildGuardEvent("blocked_app_detected", {
            processName: appHit,
            message: `Blocked app detected: ${appHit}. This session will be ended with no reward.`,
          }));
          return;
        }
      }

      if (state.blockedSites.length > 0) {
        const browserWindows = await listBrowserWindows();
        const siteHit = findBlockedSiteHit(browserWindows, state.blockedSites);
        if (siteHit) {
          emitViolation(windowRef, buildGuardEvent("blocked_site_detected", {
            domain: siteHit.domain,
            processName: siteHit.processName,
            windowTitle: siteHit.windowTitle,
            message: `Blocked site detected: ${siteHit.domain}. This session will be ended with no reward.`,
          }));
        }
      }
    } finally {
      state.isChecking = false;
    }
  }

  function emitViolation(windowRef, violation) {
    if (isDuplicateViolation(state.lastViolation, violation)) {
      return;
    }

    state.lastViolation = violation;
    focusWindow(windowRef, state.lockMode);
    emit(violation);
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

  async function listBrowserWindows() {
    const script = [
      "$targets = @('chrome','msedge','firefox','brave','opera','iexplore')",
      "$items = Get-Process | Where-Object { $_.MainWindowTitle -and $targets -contains $_.ProcessName.ToLower() } | Select-Object @{Name='processName';Expression={$_.ProcessName}}, @{Name='windowTitle';Expression={$_.MainWindowTitle}}",
      "$items | ConvertTo-Json -Compress",
    ].join("; ");

    const { stdout } = await execFileAsync(
      "powershell.exe",
      ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
      { windowsHide: true, maxBuffer: 1024 * 1024 }
    );

    const parsed = safeParseJson(stdout.trim());
    const items = Array.isArray(parsed) ? parsed : parsed ? [parsed] : [];
    return items
      .map((item) => ({
        processName: normalizeAppName(item.processName),
        windowTitle: String(item.windowTitle || "").trim(),
      }))
      .filter((item) => item.processName && item.windowTitle && BROWSER_PROCESS_NAMES.has(item.processName));
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
      const { stdout } = await execFileAsync("powershell.exe", args, {
        windowsHide: true,
        maxBuffer: 1024 * 1024,
      });
      return String(stdout || "").trim();
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

function interpretSiteBlockError(error) {
  const message = String(error?.message || "Site block failed.").trim();
  const normalized = message.toLowerCase();

  if (
    normalized.includes("administrator") ||
    normalized.includes("access is denied") ||
    normalized.includes("requested operation requires elevation")
  ) {
    return {
      state: "permission_required",
      message: "Site blocking requires running Electron as administrator.",
    };
  }

  return {
    state: "error",
    message: message || "Site block failed.",
  };
}

function isDuplicateViolation(previousViolation, nextViolation) {
  if (!previousViolation || !nextViolation) {
    return false;
  }

  if (previousViolation.type !== nextViolation.type) {
    return false;
  }

  if ((previousViolation.processName || "") !== (nextViolation.processName || "")) {
    return false;
  }

  if ((previousViolation.domain || "") !== (nextViolation.domain || "")) {
    return false;
  }

  const previousAt = new Date(previousViolation.detectedAt).getTime();
  const nextAt = new Date(nextViolation.detectedAt).getTime();
  return Number.isFinite(previousAt) && Number.isFinite(nextAt) && nextAt - previousAt < 15000;
}

function findBlockedSiteHit(browserWindows, blockedSites) {
  for (const browserWindow of browserWindows) {
    const title = String(browserWindow.windowTitle || "").toLowerCase();
    for (const domain of blockedSites) {
      const keywords = buildDomainKeywords(domain);
      if (keywords.some((keyword) => title.includes(keyword))) {
        return {
          domain,
          processName: browserWindow.processName,
          windowTitle: browserWindow.windowTitle,
        };
      }
    }
  }

  return null;
}

function buildDomainKeywords(domain) {
  const normalized = normalizeDomain(domain);
  const parts = normalized.split(".").filter(Boolean);
  const keywords = [normalized];

  if (parts.length >= 2) {
    keywords.push(parts[parts.length - 2]);
  }

  if (parts.length >= 3) {
    keywords.push(parts[0]);
  }

  return Array.from(new Set(keywords.filter((item) => item && item.length >= 3)));
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
