const STORAGE_KEYS = {
  apiBase: "study_focus_api_base",
  token: "study_focus_token",
  user: "study_focus_user",
  activeSession: "study_focus_active_session",
  leaderboardPeriod: "study_focus_leaderboard_period",
  leaderboardScope: "study_focus_leaderboard_scope",
  leaderboardSchoolId: "study_focus_leaderboard_school_id",
  leaderboardCollegeId: "study_focus_leaderboard_college_id",
  lastDemoUsername: "study_focus_last_demo_username",
};

const DEFAULT_API_BASE = "http://127.0.0.1:8000/api/v1";
const DEFAULT_DEMO_PASSWORD = "Test123456";

const state = {
  apiBase: localStorage.getItem(STORAGE_KEYS.apiBase) || DEFAULT_API_BASE,
  token: localStorage.getItem(STORAGE_KEYS.token) || "",
  user: readJson(STORAGE_KEYS.user),
  activeSession: readJson(STORAGE_KEYS.activeSession),
  pausedSession: null,
  timerId: null,
  leaderboardPeriod: localStorage.getItem(STORAGE_KEYS.leaderboardPeriod) || "day",
  leaderboardScope: localStorage.getItem(STORAGE_KEYS.leaderboardScope) || "school",
  leaderboardSchoolId: Number(localStorage.getItem(STORAGE_KEYS.leaderboardSchoolId) || 0) || 0,
  leaderboardCollegeId: Number(localStorage.getItem(STORAGE_KEYS.leaderboardCollegeId) || 0) || 0,
  leaderboardMeta: null,
  schools: [],
  colleges: [],
  points: null,
  sessions: [],
  ledger: [],
  leaderboard: [],
  orders: [],
  feedbacks: [],
  guardInterruptInFlight: false,
  desktop: {
    available: Boolean(window.studyFocusDesktop?.isAvailable),
    status: null,
    eventLog: [],
    unsubscribe: null,
  },
};

const elements = {
  apiBaseInput: document.querySelector("#api-base-input"),
  saveApiBaseBtn: document.querySelector("#save-api-base-btn"),
  refreshDashboardBtn: document.querySelector("#refresh-dashboard-btn"),
  logoutBtn: document.querySelector("#logout-btn"),
  fillRegisterDemoBtn: document.querySelector("#fill-register-demo-btn"),
  fillLoginDemoBtn: document.querySelector("#fill-login-demo-btn"),
  quickStartHint: document.querySelector("#quick-start-hint"),
  authPanel: document.querySelector("#auth-panel"),
  dashboard: document.querySelector("#dashboard"),
  loginForm: document.querySelector("#login-form"),
  registerForm: document.querySelector("#register-form"),
  focusStartForm: document.querySelector("#focus-start-form"),
  completeSessionBtn: document.querySelector("#complete-session-btn"),
  interruptSessionBtn: document.querySelector("#interrupt-session-btn"),
  resumeSessionBtn: document.querySelector("#resume-session-btn"),
  abandonSessionBtn: document.querySelector("#abandon-session-btn"),
  refreshQuestionBtn: document.querySelector("#refresh-question-btn"),
  aiChatForm: document.querySelector("#ai-chat-form"),
  redeemForm: document.querySelector("#redeem-form"),
  feedbackForm: document.querySelector("#feedback-form"),
  leaderboardContext: document.querySelector("#leaderboard-context"),
  leaderboardSchoolSelect: document.querySelector("#leaderboard-school-select"),
  leaderboardCollegeSelect: document.querySelector("#leaderboard-college-select"),
  leaderboardCollegeWrap: document.querySelector("#leaderboard-college-wrap"),
  latestCouponToken: document.querySelector("#latest-coupon-token"),
  latestCouponNote: document.querySelector("#latest-coupon-note"),
  toast: document.querySelector("#toast"),
  heroAuthState: document.querySelector("#hero-auth-state"),
  heroTimerState: document.querySelector("#hero-timer-state"),
  heroRedeemState: document.querySelector("#hero-redeem-state"),
  heroGuardState: document.querySelector("#hero-guard-state"),
  profileName: document.querySelector("#profile-name"),
  profileUsername: document.querySelector("#profile-username"),
  profileSchool: document.querySelector("#profile-school"),
  profileCollege: document.querySelector("#profile-college"),
  pointsBalance: document.querySelector("#points-balance"),
  pointsNote: document.querySelector("#points-note"),
  focusMinutesTotal: document.querySelector("#focus-minutes-total"),
  focusNote: document.querySelector("#focus-note"),
  focusLiveTimer: document.querySelector("#focus-live-timer"),
  focusLiveStatus: document.querySelector("#focus-live-status"),
  desktopGuardState: document.querySelector("#desktop-guard-state"),
  desktopGuardNote: document.querySelector("#desktop-guard-note"),
  guardSupportBadges: document.querySelector("#guard-support-badges"),
  guardEventList: document.querySelector("#guard-event-list"),
  runningSessionSummary: document.querySelector("#running-session-summary"),
  sessionList: document.querySelector("#session-list"),
  ledgerList: document.querySelector("#ledger-list"),
  leaderboardList: document.querySelector("#leaderboard-list"),
  redeemList: document.querySelector("#redeem-list"),
  feedbackList: document.querySelector("#feedback-list"),
  dailyQuestionSubject: document.querySelector("#daily-question-subject"),
  dailyQuestionDifficulty: document.querySelector("#daily-question-difficulty"),
  dailyQuestionTitle: document.querySelector("#daily-question-title"),
  dailyQuestionBody: document.querySelector("#daily-question-body"),
  dailyQuestionHint: document.querySelector("#daily-question-hint"),
  chatHistory: document.querySelector("#chat-history"),
  periodButtons: Array.from(document.querySelectorAll("#leaderboard-period-tabs .period-tab")),
  scopeButtons: Array.from(document.querySelectorAll("#leaderboard-scope-tabs .scope-tab")),
};

bootstrap();

function bootstrap() {
  bindEvents();
  elements.apiBaseInput.value = state.apiBase;
  prefillFormsFromHistory();
  updateAuthView();
  renderDesktopStatus();
  void initDesktopBridge();

  if (state.token) {
    void refreshDashboard();
  }
}

function bindEvents() {
  elements.saveApiBaseBtn.addEventListener("click", handleSaveApiBase);
  elements.refreshDashboardBtn.addEventListener("click", () => void refreshDashboard());
  elements.logoutBtn.addEventListener("click", logout);
  elements.fillRegisterDemoBtn.addEventListener("click", fillRegisterDemoForm);
  elements.fillLoginDemoBtn.addEventListener("click", fillLoginDemoForm);

  elements.loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    void handleLogin(event.currentTarget);
  });

  elements.registerForm.addEventListener("submit", (event) => {
    event.preventDefault();
    void handleRegister(event.currentTarget);
  });

  elements.focusStartForm.addEventListener("submit", (event) => {
    event.preventDefault();
    void handleStartFocus(event.currentTarget);
  });

  elements.completeSessionBtn.addEventListener("click", () => void settleCurrentSession("complete"));
  elements.interruptSessionBtn.addEventListener("click", () => void settleCurrentSession("interrupt"));
  elements.resumeSessionBtn.addEventListener("click", () => void handleResumeFocus());
  elements.abandonSessionBtn.addEventListener("click", () => void settleCurrentSession("abandon"));

  elements.refreshQuestionBtn.addEventListener("click", () => void loadDailyQuestion());
  elements.aiChatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    void handleAskAi(event.currentTarget);
  });

  elements.redeemForm.addEventListener("submit", (event) => {
    event.preventDefault();
    void handleCreateRedeem(event.currentTarget);
  });

  elements.feedbackForm.addEventListener("submit", (event) => {
    event.preventDefault();
    void handleCreateFeedback(event.currentTarget);
  });

  elements.redeemList.addEventListener("click", (event) => {
    const copyTokenButton = event.target.closest("[data-copy-token]");

    if (copyTokenButton) {
      void handleCopyCouponToken(copyTokenButton.dataset.copyToken || "");
    }
  });

  elements.periodButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const nextPeriod = button.dataset.period;
      if (!nextPeriod || nextPeriod === state.leaderboardPeriod) {
        return;
      }

      state.leaderboardPeriod = nextPeriod;
      persistLeaderboardFilters();
      renderLeaderboardTabs();
      void loadLeaderboard();
    });
  });

  elements.scopeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const nextScope = button.dataset.scope;
      if (!nextScope || nextScope === state.leaderboardScope) {
        return;
      }

      state.leaderboardScope = nextScope;
      persistLeaderboardFilters();
      renderLeaderboardTabs();
      void loadLeaderboard();
    });
  });

  elements.leaderboardSchoolSelect.addEventListener("change", async (event) => {
    state.leaderboardSchoolId = Number(event.currentTarget.value || 0) || 0;
    await loadCollegesForSelectedSchool();
    persistLeaderboardFilters();
    renderLeaderboardTabs();
    await loadLeaderboard();
  });

  elements.leaderboardCollegeSelect.addEventListener("change", async (event) => {
    state.leaderboardCollegeId = Number(event.currentTarget.value || 0) || 0;
    persistLeaderboardFilters();
    renderLeaderboardTabs();
    await loadLeaderboard();
  });
}

async function initDesktopBridge() {
  if (!state.desktop.available) {
    renderDesktopStatus();
    return;
  }

  try {
    state.desktop.unsubscribe = window.studyFocusDesktop.onGuardEvent((event) => {
      void handleDesktopGuardEvent(event);
    });

    state.desktop.status = await window.studyFocusDesktop.getStatus();
    renderDesktopStatus();
  } catch (error) {
    pushGuardEvent({
      type: "guard_bridge_error",
      detectedAt: new Date().toISOString(),
      message: `Desktop bridge failed: ${error.message}`,
    });
    renderDesktopStatus();
  }
}

function updateAuthView() {
  const isLoggedIn = Boolean(state.token);

  elements.authPanel.hidden = isLoggedIn;
  elements.dashboard.hidden = !isLoggedIn;
  elements.logoutBtn.hidden = !isLoggedIn;
  elements.refreshDashboardBtn.hidden = !isLoggedIn;
  elements.heroAuthState.textContent = isLoggedIn ? "Authenticated" : "Guest";

  renderLeaderboardTabs();
  renderRunningSession();
}

function handleSaveApiBase() {
  const value = elements.apiBaseInput.value.trim().replace(/\/+$/u, "");
  state.apiBase = value || DEFAULT_API_BASE;
  localStorage.setItem(STORAGE_KEYS.apiBase, state.apiBase);
  elements.apiBaseInput.value = state.apiBase;
  showToast("API base saved.", "success");
}

function fillRegisterDemoForm() {
  const suffix = Date.now().toString().slice(-6);
  setFormValue(elements.registerForm, "username", `demo_user_${suffix}`);
  setFormValue(elements.registerForm, "password", DEFAULT_DEMO_PASSWORD);
  setFormValue(elements.registerForm, "nickname", `demo-${suffix}`);
  setFormValue(elements.registerForm, "email", `demo_user_${suffix}@example.com`);
  setFormValue(elements.registerForm, "phone", `138${suffix.padStart(8, "0")}`.slice(0, 11));
  setFormValue(elements.registerForm, "student_no", `2026${suffix}`);
  setFormValue(elements.registerForm, "grade_year", "2026");
  setFormValue(elements.registerForm, "major_name", "Software Engineering");
  setFormValue(elements.registerForm, "region_id", "1");
  setFormValue(elements.registerForm, "school_id", "1");
  setFormValue(elements.registerForm, "college_id", "1");
  elements.quickStartHint.textContent = "Register form filled. Submit it once, then use the left form to login.";
  showToast("Register demo values filled.", "success");
}

function fillLoginDemoForm() {
  const username = localStorage.getItem(STORAGE_KEYS.lastDemoUsername) || (state.user?.username || "demo_user_1001");
  setFormValue(elements.loginForm, "username", username);
  setFormValue(elements.loginForm, "password", DEFAULT_DEMO_PASSWORD);
  elements.quickStartHint.textContent = `Login form filled with ${username}.`;
  showToast("Login demo values filled.", "success");
}

function prefillFormsFromHistory() {
  const username = localStorage.getItem(STORAGE_KEYS.lastDemoUsername);
  if (username) {
    setFormValue(elements.loginForm, "username", username);
    setFormValue(elements.loginForm, "password", DEFAULT_DEMO_PASSWORD);
  }
}

async function handleLogin(form) {
  const payload = Object.fromEntries(new FormData(form).entries());
  const response = await apiFetch("/auth/login", {
    method: "POST",
    body: payload,
    auth: false,
  }).catch(handleUiError);

  if (!response) {
    return;
  }

  state.token = response.access_token;
  localStorage.setItem(STORAGE_KEYS.token, state.token);
  localStorage.setItem(STORAGE_KEYS.lastDemoUsername, payload.username);
  showToast("Login completed.", "success");
  updateAuthView();
  await refreshDashboard();
}

async function handleRegister(form) {
  const payload = formDataToObject(new FormData(form));
  payload.grade_year = Number(payload.grade_year);
  payload.region_id = Number(payload.region_id);
  payload.school_id = Number(payload.school_id);
  payload.college_id = Number(payload.college_id);

  const response = await apiFetch("/auth/register", {
    method: "POST",
    body: payload,
    auth: false,
  }).catch(handleUiError);

  if (!response) {
    return;
  }

  localStorage.setItem(STORAGE_KEYS.lastDemoUsername, response.username);
  setFormValue(elements.loginForm, "username", response.username);
  setFormValue(elements.loginForm, "password", DEFAULT_DEMO_PASSWORD);
  elements.quickStartHint.textContent = `Registered ${response.username}. Use the left form to login with the same password.`;
  showToast(`Registered ${response.username}. You can log in now.`, "success");
}

async function refreshDashboard() {
  if (!state.token) {
    return;
  }

  const profile = await apiFetch("/users/me").catch(handleUiError);
  if (!profile) {
    return;
  }

  state.user = profile;
  localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(profile));

  if (!state.leaderboardSchoolId) {
    state.leaderboardSchoolId = Number(profile.school_id || 0) || 0;
  }
  if (!state.leaderboardCollegeId) {
    state.leaderboardCollegeId = Number(profile.college_id || 0) || 0;
  }

  const [points, sessions, ledger, question, orders, feedback, schools, colleges, leaderboard] = await Promise.all([
    apiFetch("/points/balance").catch(handleUiError),
    apiFetch("/focus-sessions?page=1&page_size=8").catch(handleUiError),
    apiFetch("/points/ledger?page=1&page_size=8").catch(handleUiError),
    apiFetch("/learning/daily-question").catch(handleUiError),
    apiFetch("/redeem-orders/my?page=1&page_size=8").catch(handleUiError),
    apiFetch("/feedback/my?page=1&page_size=6").catch(handleUiError),
    apiFetch("/dicts/schools", { auth: false }).catch(handleUiError),
    apiFetch(`/dicts/colleges?school_id=${state.leaderboardSchoolId || profile.school_id}`, { auth: false }).catch(handleUiError),
    apiFetch(buildLeaderboardPath()).catch(handleUiError),
  ]);

  if (points) {
    state.points = points;
  }

  if (sessions) {
    state.sessions = sessions.items || [];
    state.activeSession = state.sessions.find((item) => item.status === "RUNNING") || null;
    state.pausedSession = state.sessions.find((item) => item.status === "INTERRUPTED" && item.settle_status === 0) || null;
    syncActiveSessionStorage();
  }

  if (ledger) {
    state.ledger = ledger.items || [];
  }

  if (schools) {
    state.schools = schools;
  }

  if (colleges) {
    state.colleges = colleges;
    if (state.leaderboardScope === "college" && !state.colleges.some((item) => item.college_id === state.leaderboardCollegeId)) {
      state.leaderboardCollegeId = Number(state.colleges[0]?.college_id || 0) || 0;
      persistLeaderboardFilters();
    }
  }

  if (leaderboard) {
    state.leaderboard = leaderboard.items || [];
    state.leaderboardMeta = leaderboard;
  }

  if (orders) {
    state.orders = orders.items || [];
  }

  if (feedback) {
    state.feedbacks = feedback.items || [];
  }

  renderProfile();
  renderPoints();
  renderSessions();
  renderLedger();
  renderLeaderboardTabs();
  renderLeaderboard();
  renderDailyQuestion(question);
  renderOrders();
  renderFeedback();
  renderRunningSession();
  await syncDesktopGuard();
}
async function handleStartFocus(form) {
  if (state.activeSession) {
    showToast("A running session already exists.", "error");
    return;
  }

  if (state.pausedSession) {
    showToast("An interrupted session is waiting. Resume or abandon it before starting a new one.", "error");
    return;
  }

  const payload = formDataToObject(new FormData(form));
  payload.planned_minutes = Number(payload.planned_minutes);
  payload.blocked_apps = parseCsvList(payload.blocked_apps);
  payload.blocked_sites = parseCsvList(payload.blocked_sites);

  const session = await apiFetch("/focus-sessions/start", {
    method: "POST",
    body: payload,
  }).catch(handleUiError);

  if (!session) {
    return;
  }

  state.activeSession = session;
  syncActiveSessionStorage();
  await startDesktopGuardForSession(session);
  showToast("Focus session started.", "success");
  await refreshDashboard();
}

async function handleResumeFocus() {
  if (!state.pausedSession) {
    showToast("No interrupted session found.", "error");
    return;
  }

  const session = await apiFetch(`/focus-sessions/${state.pausedSession.session_id}/resume`, {
    method: "POST",
  }).catch(handleUiError);

  if (!session) {
    return;
  }

  state.activeSession = session;
  state.pausedSession = null;
  syncActiveSessionStorage();
  await startDesktopGuardForSession(session);
  showToast("Focus session resumed from the interrupted time.", "success");
  await refreshDashboard();
}

async function settleCurrentSession(action, extraBody = {}, options = {}) {
  const targetSession = action === "abandon" ? (state.activeSession || state.pausedSession) : state.activeSession;

  if (!targetSession) {
    const message = action === "abandon" ? "No running or interrupted session found." : "No running session found.";
    showToast(message, "error");
    return null;
  }

  const labelMap = {
    complete: "complete",
    interrupt: "interrupt",
    abandon: "abandon",
  };

  const path = `/focus-sessions/${targetSession.session_id}/${labelMap[action]}`;
  const result = await apiFetch(path, {
    method: "POST",
    body: extraBody,
  }).catch(handleUiError);

  if (!result) {
    return null;
  }

  if (action === "interrupt") {
    state.activeSession = null;
    state.pausedSession = result;
    syncActiveSessionStorage();
    await stopDesktopGuard();
    showToast(options.successMessage || "Session interrupted. Resume will continue from the saved time.", "success");
    await refreshDashboard();
    return result;
  }

  state.activeSession = null;
  state.pausedSession = null;
  syncActiveSessionStorage();
  await stopDesktopGuard();
  showToast(options.successMessage || `Session ${labelMap[action]}ed.`, "success");
  await refreshDashboard();
  return result;
}

async function loadDailyQuestion() {
  const question = await apiFetch("/learning/daily-question").catch(handleUiError);
  if (!question) {
    return;
  }

  renderDailyQuestion(question);
  showToast("Daily question refreshed.", "success");
}

async function handleAskAi(form) {
  const formData = new FormData(form);
  const question = String(formData.get("question") || "").trim();
  if (!question) {
    return;
  }

  appendChatBubble("user", question);
  form.reset();

  const reply = await apiFetch("/learning/ai-chat", {
    method: "POST",
    body: { question },
  }).catch((error) => {
    appendChatBubble("assistant", `Request failed: ${error.message}`);
    handleUiError(error);
    return null;
  });

  if (!reply) {
    return;
  }

  appendChatBubble("assistant", reply.answer);
}

async function handleCreateRedeem(form) {
  const payload = formDataToObject(new FormData(form));
  payload.points_cost = Number(payload.points_cost);
  payload.print_quota_pages = Number(payload.print_quota_pages);
  payload.expire_minutes = Number(payload.expire_minutes);

  const order = await apiFetch("/redeem-orders", {
    method: "POST",
    body: payload,
  }).catch(handleUiError);

  if (!order) {
    return;
  }

  showToast(`Coupon code generated: ${order.coupon_token.slice(0, 12)}...`, "success");
  await refreshDashboard();
}

async function handleCreateFeedback(form) {
  const payload = formDataToObject(new FormData(form));

  const feedback = await apiFetch("/feedback", {
    method: "POST",
    body: payload,
  }).catch(handleUiError);

  if (!feedback) {
    return;
  }

  showToast("Feedback submitted. Thanks for helping improve the app.", "success");
  form.reset();
  setFormValue(form, "category", "GENERAL");
  setFormValue(form, "contact_email", state.user?.email || "");
  await refreshDashboard();
}

async function handleDesktopGuardEvent(event) {
  if (!event) {
    return;
  }

  pushGuardEvent(event);

  if (event.type === "guard_state" && event.status) {
    state.desktop.status = event.status;
  }

  if (event.type === "blocked_app_detected" || event.type === "blocked_site_detected") {
    showToast(event.message || "Blocked focus violation detected.", "error");
    if (state.activeSession && !state.guardInterruptInFlight) {
      state.guardInterruptInFlight = true;
      try {
        const violationRemark = event.type === "blocked_site_detected"
          ? `Guard violation: blocked site ${event.domain || event.windowTitle || "unknown"}`
          : `Guard violation: blocked app ${event.processName || "unknown"}`;
        await settleCurrentSession(
          "abandon",
          { remark: violationRemark },
          { successMessage: "Session ended by desktop guard. Progress cleared and no points awarded." }
        );
      } finally {
        state.guardInterruptInFlight = false;
      }
    }
  }

  renderDesktopStatus();
}

async function syncDesktopGuard() {
  if (!state.desktop.available) {
    renderDesktopStatus();
    return;
  }

  const status = state.desktop.status;

  if (state.activeSession) {
    if (!status?.active || status.sessionId !== state.activeSession.session_id) {
      await startDesktopGuardForSession(state.activeSession);
    }
  } else if (status?.active) {
    await stopDesktopGuard();
  }

  renderDesktopStatus();
}

async function startDesktopGuardForSession(session) {
  if (!state.desktop.available || !session) {
    return;
  }

  const current = state.desktop.status;
  if (current?.active && current.sessionId === session.session_id) {
    return;
  }

  const payload = {
    sessionId: session.session_id,
    lockMode: session.lock_mode,
    blockedApps: session.blocked_apps_json || [],
    blockedSites: session.blocked_sites_json || [],
  };

  const status = await window.studyFocusDesktop.startGuard(payload).catch((error) => {
    pushGuardEvent({
      type: "guard_start_error",
      detectedAt: new Date().toISOString(),
      message: `Desktop guard start failed: ${error.message}`,
    });
    showToast(`Desktop guard start failed: ${error.message}`, "error");
    return null;
  });

  if (status) {
    state.desktop.status = status;
    renderDesktopStatus();
  }
}

async function stopDesktopGuard() {
  if (!state.desktop.available) {
    return;
  }

  const status = await window.studyFocusDesktop.stopGuard().catch((error) => {
    pushGuardEvent({
      type: "guard_stop_error",
      detectedAt: new Date().toISOString(),
      message: `Desktop guard stop failed: ${error.message}`,
    });
    return null;
  });

  if (status) {
    state.desktop.status = status;
    renderDesktopStatus();
  }
}
function renderProfile() {
  if (!state.user) {
    return;
  }

  elements.profileName.textContent = state.user.nickname || "Anonymous";
  elements.profileUsername.textContent = state.user.username || "-";
  elements.profileSchool.textContent = getSchoolNameById(state.user.school_id) || `School ID ${state.user.school_id}`;
  elements.profileCollege.textContent = getCollegeNameById(state.user.college_id) || `College ID ${state.user.college_id}`;

  const feedbackEmailInput = elements.feedbackForm.elements.namedItem("contact_email");
  if (!String(feedbackEmailInput.value || "").trim()) {
    feedbackEmailInput.value = state.user.email || "";
  }
}

function renderPoints() {
  const points = state.points || { total_points: 0, total_focus_minutes: 0 };
  elements.pointsBalance.textContent = String(points.total_points);
  elements.pointsNote.textContent = `${state.ledger.length} ledger records loaded.`;
  elements.focusMinutesTotal.textContent = String(points.total_focus_minutes);
  elements.focusNote.textContent = `${state.sessions.filter((item) => item.status === "COMPLETED").length} completed sessions found.`;
}

function renderSessions() {
  if (!state.sessions.length) {
    elements.sessionList.innerHTML = `<div class="empty-state">No sessions loaded.</div>`;
    return;
  }

  elements.sessionList.innerHTML = state.sessions
    .map((session) => {
      const meta = [
        `Actual ${session.actual_minutes} min`,
        `Points ${session.awarded_points}`,
        `Lock ${session.lock_mode}`,
      ];
      const blockedApps = (session.blocked_apps_json || []).slice(0, 2).join(", ") || "none";
      const blockedSites = (session.blocked_sites_json || []).slice(0, 2).join(", ") || "none";
      const remark = session.remark ? `<span>Remark ${escapeHtml(session.remark)}</span>` : "";

      return `
        <div class="table-row">
          <div class="row-main">
            <span class="row-title">${escapeHtml(session.status)} - ${session.planned_minutes} min</span>
            <span>${formatDateTime(session.start_at)}</span>
          </div>
          <div class="row-meta">${meta.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div>
          <div class="row-meta">
            <span>Apps ${escapeHtml(blockedApps)}</span>
            <span>Sites ${escapeHtml(blockedSites)}</span>
            ${remark}
          </div>
        </div>
      `;
    })
    .join("");
}

function renderLedger() {
  if (!state.ledger.length) {
    elements.ledgerList.innerHTML = `<div class="empty-state">No ledger items yet.</div>`;
    return;
  }

  elements.ledgerList.innerHTML = state.ledger
    .map((item) => {
      const sign = item.change_points > 0 ? "+" : "";
      return `
        <div class="table-row">
          <div class="row-main">
            <span class="row-title">${escapeHtml(item.biz_type)}</span>
            <span>${sign}${item.change_points}</span>
          </div>
          <div class="row-meta">
            <span>Balance ${item.balance_after}</span>
            <span>${formatDateTime(item.occurred_at)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderLeaderboard() {
  if (!state.leaderboard.length) {
    elements.leaderboardList.innerHTML = `<div class="empty-state">No ranking data found for the current filter.</div>`;
    return;
  }

  elements.leaderboardList.innerHTML = state.leaderboard
    .map((item) => {
      const campus = [item.school_name, item.college_name].filter(Boolean).join(" / ");
      const toneClass = item.rank === 1
        ? "is-gold"
        : item.rank === 2
          ? "is-silver"
          : item.rank === 3
            ? "is-bronze"
            : "";
      const medalLabel = item.rank === 1
        ? "Champion"
        : item.rank === 2
          ? "Runner-up"
          : item.rank === 3
            ? "Top 3"
            : "Focused";
      const collegeChip = item.college_name
        ? `<span class="leaderboard-stat-pill is-soft">${escapeHtml(item.college_name)}</span>`
        : "";

      return `
        <div class="table-row leaderboard-entry ${toneClass}">
          <div class="leaderboard-entry-head">
            <div class="leaderboard-rank-block">
              <span class="leaderboard-rank">#${item.rank}</span>
              <span class="leaderboard-medal">${medalLabel}</span>
            </div>
            <div class="leaderboard-identity">
              <span class="row-title">${escapeHtml(item.nickname)}</span>
              <span class="leaderboard-handle">@${escapeHtml(item.username)}</span>
            </div>
            <div class="leaderboard-points">
              <strong>${item.total_points}</strong>
              <span>pts</span>
            </div>
          </div>
          <div class="leaderboard-stats">
            <span class="leaderboard-stat-pill">Focus ${item.total_focus_minutes} min</span>
            <span class="leaderboard-stat-pill is-soft">${escapeHtml(item.school_name || "School unavailable")}</span>
            ${collegeChip}
          </div>
          <div class="row-meta leaderboard-campus">
            <span>${escapeHtml(campus || "Campus info unavailable")}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderDailyQuestion(question) {
  if (!question) {
    return;
  }

  elements.dailyQuestionSubject.textContent = question.subject;
  elements.dailyQuestionDifficulty.textContent = question.difficulty;
  elements.dailyQuestionTitle.textContent = question.title;
  elements.dailyQuestionBody.textContent = question.question;
  elements.dailyQuestionHint.textContent = question.answer_hint;
}

function renderOrders() {
  const latestOrder = state.orders[0] || null;
  elements.heroRedeemState.textContent = latestOrder ? "Code Ready" : "Waiting";
  elements.latestCouponToken.textContent = latestOrder ? latestOrder.coupon_token : "No code yet.";
  elements.latestCouponToken.classList.toggle("coupon-token", Boolean(latestOrder));
  elements.latestCouponNote.textContent = latestOrder
    ? `${latestOrder.store_name} / ${latestOrder.print_quota_pages} pages / expires ${formatDateTime(latestOrder.expire_at)}`
    : "Create a redeem order and the latest coupon code will appear here.";

  if (!state.orders.length) {
    elements.redeemList.innerHTML = `<div class="empty-state">No coupon codes generated yet.</div>`;
    return;
  }

  elements.redeemList.innerHTML = state.orders
    .map((order) => {
      return `
        <div class="table-row">
          <div class="row-main">
            <span class="row-title">${escapeHtml(order.store_name)}</span>
            <span>${order.points_cost} pts</span>
          </div>
          <div class="row-meta">
            <span>${order.print_quota_pages} pages</span>
            <span>${escapeHtml(order.status)}</span>
            <span>Expire ${formatDateTime(order.expire_at)}</span>
          </div>
          <div class="row-meta">
            <span class="coupon-token">${escapeHtml(order.coupon_token)}</span>
          </div>
          <div class="row-actions">
            <button class="mini-button" type="button" data-copy-token="${escapeHtml(order.coupon_token)}">Copy Code</button>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderFeedback() {
  if (!state.feedbacks.length) {
    elements.feedbackList.innerHTML = `<div class="empty-state">No feedback submitted yet.</div>`;
    return;
  }

  elements.feedbackList.innerHTML = state.feedbacks
    .map((item) => {
      const contact = item.contact_email ? `<span>${escapeHtml(item.contact_email)}</span>` : "";

      return `
        <div class="table-row">
          <div class="row-main">
            <span class="row-title">${escapeHtml(item.title)}</span>
            <span>${escapeHtml(item.category)}</span>
          </div>
          <div class="row-meta">
            <span>${formatDateTime(item.created_at)}</span>
            <span>${escapeHtml(item.status)}</span>
            ${contact}
          </div>
          <div class="row-meta">
            <span>${escapeHtml(item.content)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderRunningSession() {
  const running = state.activeSession;
  const paused = state.pausedSession;

  elements.completeSessionBtn.disabled = !running;
  elements.interruptSessionBtn.disabled = !running;
  elements.resumeSessionBtn.hidden = !paused;
  elements.resumeSessionBtn.disabled = !paused;
  elements.abandonSessionBtn.disabled = !(running || paused);

  if (running) {
    const apps = (running.blocked_apps_json || []).join(", ") || "none";
    const sites = (running.blocked_sites_json || []).join(", ") || "none";

    elements.runningSessionSummary.innerHTML = `
      <strong>${escapeHtml(running.status)}</strong> - Planned ${running.planned_minutes} min - Lock ${escapeHtml(running.lock_mode)}<br />
      <span class="meta-label">Apps ${escapeHtml(apps)} | Sites ${escapeHtml(sites)}</span>
    `;
    elements.focusLiveStatus.textContent = `Started at ${formatDateTime(running.start_at)}`;
    elements.heroTimerState.textContent = running.status;
    startTimer();
    return;
  }

  if (paused) {
    const apps = (paused.blocked_apps_json || []).join(", ") || "none";
    const sites = (paused.blocked_sites_json || []).join(", ") || "none";
    const elapsedMs = getSessionElapsedMs(paused);
    const remainingMs = getSessionRemainingMs(paused);

    elements.runningSessionSummary.innerHTML = `
      <strong>${escapeHtml(paused.status)}</strong> - Saved ${formatDuration(elapsedMs)} elapsed - ${formatDuration(remainingMs)} remaining - Lock ${escapeHtml(paused.lock_mode)}<br />
      <span class="meta-label">Apps ${escapeHtml(apps)} | Sites ${escapeHtml(sites)}</span>
    `;
    elements.focusLiveTimer.textContent = formatDuration(remainingMs);
    elements.focusLiveStatus.textContent = `Interrupted at ${formatDateTime(paused.end_at)}. Resume continues from ${formatDuration(remainingMs)} remaining.`;
    elements.heroTimerState.textContent = paused.status;
    stopTimer();
    return;
  }

  elements.runningSessionSummary.textContent = "No running session.";
  elements.focusLiveTimer.textContent = "00:00:00";
  elements.focusLiveStatus.textContent = "No running session.";
  elements.heroTimerState.textContent = "Idle";
  stopTimer();
}

function renderDesktopStatus() {
  const available = state.desktop.available;
  const status = state.desktop.status;

  if (!available) {
    elements.desktopGuardState.textContent = "Browser Only";
    elements.desktopGuardNote.textContent = "Open this page inside Electron to enable app watch and optional site block.";
    elements.heroGuardState.textContent = "Browser Only";
    elements.guardSupportBadges.innerHTML = [
      renderSupportBadge("Window Lock", false),
      renderSupportBadge("Process Watch", false),
      renderSupportBadge("Site Block", false),
    ].join("");
    renderGuardEventLog();
    return;
  }

  const activeLabel = status?.active ? `Active - ${status.lockMode}` : "Desktop Ready";
  const siteBlockText = status?.siteBlockState === "active"
    ? (status?.siteBlockReason || "Site block active.")
    : status?.siteBlockState === "permission_required"
      ? (status?.siteBlockReason || "Site blocking requires running Electron as administrator.")
      : status?.siteBlockState === "error"
        ? (status?.siteBlockReason || "Site block failed.")
        : "Process watch ready. Site block is optional.";
  const siteBlockWarning = status?.siteBlockState === "permission_required" || status?.siteBlockState === "error";

  elements.desktopGuardState.textContent = activeLabel;
  elements.desktopGuardNote.textContent = siteBlockText;
  elements.heroGuardState.textContent = activeLabel;
  elements.guardSupportBadges.innerHTML = [
    renderSupportBadge("Window Lock", true),
    renderSupportBadge("Process Watch", Boolean(status?.supports?.processWatch)),
    renderSupportBadge("Site Block", Boolean(status?.supports?.siteBlock), siteBlockWarning),
  ].join("");
  renderGuardEventLog();
}

function renderGuardEventLog() {
  if (!state.desktop.eventLog.length) {
    elements.guardEventList.innerHTML = `<div class="empty-state">No guard events yet.</div>`;
    return;
  }

  elements.guardEventList.innerHTML = state.desktop.eventLog
    .map((event) => {
      return `
        <div class="table-row">
          <div class="row-main">
            <span class="row-title">${escapeHtml(formatGuardEventType(event.type))}</span>
            <span>${formatDateTime(event.detectedAt)}</span>
          </div>
          <div class="row-meta">
            <span>${escapeHtml(event.message || "No details")}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderLeaderboardTabs() {
  elements.periodButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.period === state.leaderboardPeriod);
  });

  elements.scopeButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.scope === state.leaderboardScope);
  });

  renderSelectOptions(
    elements.leaderboardSchoolSelect,
    state.schools.map((item) => ({ value: item.school_id, label: item.school_name })),
    state.leaderboardSchoolId || state.user?.school_id || 0,
    "No school data"
  );

  const shouldShowSchool = state.leaderboardScope !== "global";
  const shouldShowCollege = state.leaderboardScope === "college";
  elements.leaderboardSchoolSelect.disabled = !shouldShowSchool;
  elements.leaderboardCollegeWrap.hidden = !shouldShowCollege;

  renderSelectOptions(
    elements.leaderboardCollegeSelect,
    state.colleges.map((item) => ({ value: item.college_id, label: item.college_name })),
    state.leaderboardCollegeId || state.user?.college_id || 0,
    "No college data"
  );
  elements.leaderboardCollegeSelect.disabled = !shouldShowCollege;

  const meta = state.leaderboardMeta;
  if (!meta) {
    elements.leaderboardContext.textContent = "Choose a time window and ranking scope.";
    return;
  }

  if (meta.scope === "college") {
    elements.leaderboardContext.textContent = `College leaderboard / ${meta.selected_college_name || "Selected college"} / ${meta.selected_school_name || "Selected school"}`;
    return;
  }

  if (meta.scope === "school") {
    elements.leaderboardContext.textContent = `School leaderboard / ${meta.selected_school_name || "Selected school"}`;
    return;
  }

  elements.leaderboardContext.textContent = "All schools leaderboard across demo campuses.";
}

async function loadLeaderboard() {
  const leaderboard = await apiFetch(buildLeaderboardPath()).catch(handleUiError);

  if (!leaderboard) {
    return;
  }

  state.leaderboard = leaderboard.items || [];
  state.leaderboardMeta = leaderboard;
  renderLeaderboardTabs();
  renderLeaderboard();
}

function pushGuardEvent(event) {
  const list = [event, ...state.desktop.eventLog];
  state.desktop.eventLog = list.slice(0, 8);
}
function startTimer() {
  stopTimer();
  tickTimer();
  state.timerId = window.setInterval(tickTimer, 1000);
}

function stopTimer() {
  if (state.timerId) {
    window.clearInterval(state.timerId);
    state.timerId = null;
  }
}

function tickTimer() {
  if (!state.activeSession) {
    return;
  }

  const started = new Date(state.activeSession.start_at).getTime();
  const plannedMs = Number(state.activeSession.planned_minutes) * 60 * 1000;
  const endMs = started + plannedMs;
  const remaining = Math.max(0, endMs - Date.now());
  elements.focusLiveTimer.textContent = formatDuration(remaining);
}

function appendChatBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role === "user" ? "user-bubble" : "assistant-bubble"}`;
  bubble.textContent = text;
  elements.chatHistory.appendChild(bubble);
  elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
}

function logout() {
  stopTimer();
  void stopDesktopGuard();
  state.token = "";
  state.user = null;
  state.activeSession = null;
  state.pausedSession = null;
  state.points = null;
  state.sessions = [];
  state.ledger = [];
  state.leaderboard = [];
  state.leaderboardMeta = null;
  state.schools = [];
  state.colleges = [];
  state.orders = [];
  state.feedbacks = [];
  localStorage.removeItem(STORAGE_KEYS.token);
  localStorage.removeItem(STORAGE_KEYS.user);
  localStorage.removeItem(STORAGE_KEYS.activeSession);
  updateAuthView();
  renderDesktopStatus();
  showToast("Logged out.", "success");
}

async function apiFetch(path, options = {}) {
  const { method = "GET", body, auth = true, headers: extraHeaders = {} } = options;
  const headers = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };

  if (auth && state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(`${state.apiBase}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const text = await response.text();
  const data = text ? parseJson(text) : null;

  if (!response.ok) {
    if (response.status === 401) {
      logout();
    }

    const message = data?.detail || `Request failed with status ${response.status}.`;
    throw new Error(message);
  }

  return data;
}

function handleUiError(error) {
  showToast(error.message || "Unexpected error.", "error");
  return null;
}

function showToast(message, type = "info") {
  elements.toast.hidden = false;
  elements.toast.textContent = message;
  elements.toast.className = `toast${type === "error" ? " is-error" : ""}${type === "success" ? " is-success" : ""}`;

  window.clearTimeout(showToast.timerId);
  showToast.timerId = window.setTimeout(() => {
    elements.toast.hidden = true;
  }, 3600);
}

function syncActiveSessionStorage() {
  if (state.activeSession) {
    localStorage.setItem(STORAGE_KEYS.activeSession, JSON.stringify(state.activeSession));
  } else {
    localStorage.removeItem(STORAGE_KEYS.activeSession);
  }
}

function renderSupportBadge(label, enabled, warning = false) {
  const className = warning ? "support-badge is-warn" : enabled ? "support-badge" : "support-badge is-off";
  const suffix = warning ? "Limited" : enabled ? "Ready" : "Unavailable";
  return `<span class="${className}">${escapeHtml(label)}: ${escapeHtml(suffix)}</span>`;
}

function formatGuardEventType(value) {
  return String(value || "guard_event")
    .split("_")
    .map((item) => item.charAt(0).toUpperCase() + item.slice(1))
    .join(" ");
}

async function handleCopyCouponToken(token) {
  if (!token) {
    return;
  }

  try {
    await navigator.clipboard.writeText(token);
    showToast("Coupon code copied.", "success");
  } catch {
    showToast("Copy failed. Please copy the code manually.", "error");
  }
}

async function loadCollegesForSelectedSchool() {
  const schoolId = Number(state.leaderboardSchoolId || state.user?.school_id || 0) || 0;
  if (!schoolId) {
    state.colleges = [];
    state.leaderboardCollegeId = 0;
    return;
  }

  const colleges = await apiFetch(`/dicts/colleges?school_id=${schoolId}`, { auth: false }).catch(handleUiError);
  if (!colleges) {
    return;
  }

  state.colleges = colleges;
  if (!state.colleges.some((item) => item.college_id === state.leaderboardCollegeId)) {
    state.leaderboardCollegeId = Number(state.colleges[0]?.college_id || 0) || 0;
  }
}

function persistLeaderboardFilters() {
  localStorage.setItem(STORAGE_KEYS.leaderboardPeriod, state.leaderboardPeriod);
  localStorage.setItem(STORAGE_KEYS.leaderboardScope, state.leaderboardScope);
  localStorage.setItem(STORAGE_KEYS.leaderboardSchoolId, String(state.leaderboardSchoolId || 0));
  localStorage.setItem(STORAGE_KEYS.leaderboardCollegeId, String(state.leaderboardCollegeId || 0));
}

function buildLeaderboardPath() {
  const params = new URLSearchParams({
    period: state.leaderboardPeriod,
    scope: state.leaderboardScope,
    limit: "10",
  });

  if (state.leaderboardScope !== "global") {
    params.set("school_id", String(state.leaderboardSchoolId || state.user?.school_id || 0));
  }

  if (state.leaderboardScope === "college") {
    params.set("college_id", String(state.leaderboardCollegeId || state.user?.college_id || 0));
  }

  return `/leaderboards/focus?${params.toString()}`;
}

function renderSelectOptions(select, items, selectedValue, emptyLabel) {
  if (!select) {
    return;
  }

  if (!items.length) {
    select.innerHTML = `<option value="">${escapeHtml(emptyLabel)}</option>`;
    return;
  }

  select.innerHTML = items
    .map((item) => `<option value="${escapeHtml(item.value)}">${escapeHtml(item.label)}</option>`)
    .join("");

  const targetValue = String(selectedValue || items[0].value);
  select.value = targetValue;
}

function getSchoolNameById(schoolId) {
  const match = state.schools.find((item) => Number(item.school_id) === Number(schoolId));
  return match ? match.school_name : "";
}

function getCollegeNameById(collegeId) {
  const match = state.colleges.find((item) => Number(item.college_id) === Number(collegeId));
  if (match) {
    return match.college_name;
  }

  const leaderboardMatch = state.leaderboard.find((item) => Number(item.college_id) === Number(collegeId));
  return leaderboardMatch?.college_name || "";
}

function setFormValue(form, name, value) {
  const input = form.elements.namedItem(name);
  if (input) {
    input.value = value;
  }
}

function formatDuration(milliseconds) {
  const totalSeconds = Math.max(0, Math.floor(milliseconds / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return [hours, minutes, seconds].map((value) => String(value).padStart(2, "0")).join(":");
}

function getSessionElapsedMs(session) {
  if (!session) {
    return 0;
  }

  const startMs = Date.parse(session.start_at || "");
  const stopCandidate = session.status === "INTERRUPTED" && session.end_at ? session.end_at : new Date().toISOString();
  const stopMs = Date.parse(stopCandidate || "");

  if (Number.isFinite(startMs) && Number.isFinite(stopMs)) {
    const plannedMs = Number(session.planned_minutes || 0) * 60 * 1000;
    return Math.max(0, Math.min(stopMs - startMs, plannedMs));
  }

  return Math.max(0, Number(session.actual_minutes || 0) * 60 * 1000);
}

function getSessionRemainingMs(session) {
  const plannedMs = Math.max(0, Number(session?.planned_minutes || 0) * 60 * 1000);
  return Math.max(0, plannedMs - getSessionElapsedMs(session));
}

function formatDateTime(value) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function parseCsvList(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formDataToObject(formData) {
  return Object.fromEntries(formData.entries());
}

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function readJson(key) {
  const raw = localStorage.getItem(key);
  return raw ? parseJson(raw) : null;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
