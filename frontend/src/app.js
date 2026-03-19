const STORAGE_KEYS = {
  apiBase: "study_focus_api_base",
  token: "study_focus_token",
  user: "study_focus_user",
  activeSession: "study_focus_active_session",
  leaderboardPeriod: "study_focus_leaderboard_period",
  leaderboardScope: "study_focus_leaderboard_scope",
  leaderboardSchoolId: "study_focus_leaderboard_school_id",
  leaderboardCollegeId: "study_focus_leaderboard_college_id",
  desktopConsent: "study_focus_desktop_consent",
  browserConsent: "study_focus_browser_consent",
  browserAwayState: "study_focus_browser_away_state",
  browserViolationNotice: "study_focus_browser_violation_notice",
  lastDemoUsername: "study_focus_last_demo_username",
};

function getDefaultApiBase() {
  const { hostname, origin, port, protocol } = window.location;
  const isLocalHost = hostname === "127.0.0.1" || hostname === "localhost";

  if (protocol === "file:" || !origin || origin === "null") {
    return "http://127.0.0.1:8000/api/v1";
  }

  if (isLocalHost && port !== "8000") {
    return "http://127.0.0.1:8000/api/v1";
  }

  return `${origin}/api/v1`;
}

const DEFAULT_API_BASE = getDefaultApiBase();
const DEFAULT_DEMO_PASSWORD = "StudyFocus123!";
const DEFAULT_LOGIN_DEMO_USERNAME = "hubu_mjc_se_101";
const APP_PAGE_VERSION = "sprint4r17";
const FOCUS_PLAN_STORAGE_PREFIX = "study_focus_focus_plan_";
const CURRENT_PAGE = document.body.dataset.page || "landing";

function ensureApiV1Suffix(value) {
  const raw = String(value || "").trim().replace(/\/+$/u, "");
  if (!raw) {
    return "";
  }

  if (raw.endsWith("/api/v1")) {
    return raw;
  }

  if (raw.endsWith("/api")) {
    return `${raw}/v1`;
  }

  return `${raw}/api/v1`;
}

function normalizeApiBaseForCurrentHost(value) {
  const raw = String(value || "").trim().replace(/\/+$/u, "");
  const { hostname, origin, protocol } = window.location;
  const isLocalPage = protocol === "file:" || hostname === "127.0.0.1" || hostname === "localhost";
  const isLocalApi = raw.includes("127.0.0.1:8000") || raw.includes("localhost:8000");

  if (isLocalPage) {
    return isLocalApi ? ensureApiV1Suffix(raw) : "http://127.0.0.1:8000/api/v1";
  }

  if (!raw || isLocalApi) {
    return `${origin}/api/v1`;
  }

  if (raw.startsWith("/")) {
    return `${origin}${raw}`;
  }

  return ensureApiV1Suffix(raw);
}

const PAGE_META = {
  landing: {
    browserTitle: "Study Focus Atlas",
    eyebrow: "Welcome",
    title: "A campus study system that finally behaves like separate workspaces, not one crowded screen.",
    lead:
      "Login and registration stay on the landing page. After that, focus, rankings, learning, rewards, and feedback each get a dedicated destination.",
    tags: ["Login", "Register", "Seeded Accounts", "Campus Demo", "Desktop Guard"],
  },
  home: {
    browserTitle: "Studio Home | Study Focus Atlas",
    eyebrow: "Studio Home",
    title: "Choose the workspace you need and leave the rest out of your way.",
    lead:
      "This overview page keeps the profile, totals, and jump cards visible while the heavy task surfaces live on their own routes.",
    tags: ["Overview", "Quick Jumps", "Campus Metrics", "Cleaner Demo", "Multi-Page"],
  },
  focus: {
    browserTitle: "Learning | Study Focus Atlas",
    eyebrow: "Learning",
    title: "Use one learning page to run the timer, plan tasks, and review guard status.",
    lead:
      "This route keeps the timer, planner, consent gate, and guard log together so the focus flow is easier to explain and use.",
    tags: ["Learning", "Timer", "Plan Notebook", "Guard Events", "Blocked Sites"],
  },
  rankings: {
    browserTitle: "Rankings | Study Focus Atlas",
    eyebrow: "Rankings",
    title: "School and college leaderboards deserve a page that looks presentable in a real demo.",
    lead:
      "Filters, rank cards, and the point ledger are isolated here so the school comparison view is easier to read and explain.",
    tags: ["School Scope", "College Scope", "Day Month Year", "Point Ledger", "Demo Ready"],
  },
  learning: {
    browserTitle: "Break Space | Study Focus Atlas",
    eyebrow: "Break Space",
    title: "Keep the daily question and AI break-space together instead of burying them under operations.",
    lead:
      "This page is calmer by design: question at the top, chat below, and no ranking or redeem noise fighting for attention.",
    tags: ["Daily Question", "AI Chat", "Break Space", "Study Support", "Lighter Layout"],
  },
  rewards: {
    browserTitle: "Rewards | Study Focus Atlas",
    eyebrow: "Rewards",
    title: "Coupon generation should feel like a clean student action, not a crowded side widget.",
    lead:
      "The rewards route centers the redeem form, latest coupon, and recent generated codes so the printing benefit is easy to demonstrate.",
    tags: ["Redeem Code", "Point Spend", "Coupon Copy", "Print Shop", "Student Flow"],
  },
  feedback: {
    browserTitle: "Feedback | Study Focus Atlas",
    eyebrow: "Feedback",
    title: "A product loop page for UI notes, bug reports, and ideas from real student use.",
    lead:
      "Suggestions are separated from the study controls so feedback feels intentional and the recent messages list stays readable.",
    tags: ["Suggestions", "UI Notes", "Bug Reports", "Ideas", "Recent Messages"],
  },
};

const state = {
  apiBase: normalizeApiBaseForCurrentHost(localStorage.getItem(STORAGE_KEYS.apiBase) || DEFAULT_API_BASE),
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
  dailyQuestion: null,
  focusPlanItems: [],
  autoCompleteSessionId: 0,
  guardInterruptInFlight: false,
  desktop: {
    available: Boolean(window.studyFocusDesktop?.isAvailable),
    consent: readDesktopConsentStatus(),
    status: null,
    eventLog: [],
    unsubscribe: null,
    promptInFlight: false,
  },
  web: {
    consent: readBrowserConsentStatus(),
    promptInFlight: false,
    violationTimerId: null,
    awayStartedAt: 0,
    awayTrigger: "",
  },
};

const uiMotion = {
  observer: null,
  mutationObserver: null,
  initialized: false,
  refreshFrame: 0,
};

const elements = {
  apiBaseInput: document.querySelector("#api-base-input"),
  saveApiBaseBtn: document.querySelector("#save-api-base-btn"),
  refreshDashboardBtn: document.querySelector("#refresh-dashboard-btn"),
  logoutBtn: document.querySelector("#logout-btn"),
  fillRegisterDemoBtn: document.querySelector("#fill-register-demo-btn"),
  fillLoginDemoBtn: document.querySelector("#fill-login-demo-btn"),
  quickStartHint: document.querySelector("#quick-start-hint"),
  headlineEyebrow: document.querySelector("#headline-eyebrow"),
  headlineTitle: document.querySelector("#headline-title"),
  headlineLead: document.querySelector("#headline-lead"),
  headlineTags: document.querySelector("#headline-tags"),
  authPanel: document.querySelector("#auth-panel"),
  dashboard: document.querySelector("#dashboard"),
  loginForm: document.querySelector("#login-form"),
  registerForm: document.querySelector("#register-form"),
  focusStartForm: document.querySelector("#focus-start-form"),
  focusPlanForm: document.querySelector("#focus-plan-form"),
  focusPlanList: document.querySelector("#focus-plan-list"),
  interruptSessionBtn: document.querySelector("#interrupt-session-btn"),
  resumeSessionBtn: document.querySelector("#resume-session-btn"),
  abandonSessionBtn: document.querySelector("#abandon-session-btn"),
  refreshQuestionBtn: document.querySelector("#refresh-question-btn"),
  dailyQuestionForm: document.querySelector("#daily-question-form"),
  dailyQuestionOptions: document.querySelector("#daily-question-options"),
  dailyQuestionResult: document.querySelector("#daily-question-result"),
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
  dailyQuestionPoints: document.querySelector("#daily-question-points"),
  dailyQuestionTitle: document.querySelector("#daily-question-title"),
  dailyQuestionBody: document.querySelector("#daily-question-body"),
  dailyQuestionHint: document.querySelector("#daily-question-hint"),
  chatHistory: document.querySelector("#chat-history"),
  periodButtons: Array.from(document.querySelectorAll("#leaderboard-period-tabs .period-tab")),
  scopeButtons: Array.from(document.querySelectorAll("#leaderboard-scope-tabs .scope-tab")),
  desktopConsentBtn: null,
};

void bootstrap();

async function bootstrap() {
  state.apiBase = normalizeApiBaseForCurrentHost(state.apiBase);
  localStorage.setItem(STORAGE_KEYS.apiBase, state.apiBase);
  ensureDesktopConsentControl();
  bindEvents();
  elements.apiBaseInput.value = state.apiBase;
  prefillFormsFromHistory();
  applyPageMeta();

  if (!state.token) {
    clearDesktopConsent();
  }

  if (enforceRouteBoundary()) {
    return;
  }

  ensureHeadlineVisual();
  injectPenguinBrandBadge();
  const loaderBlocksMotion = initializePenguinLoader();
  if (!loaderBlocksMotion) {
    initializeMotionSystem();
  }

  updateAuthView();
  renderDesktopStatus();
  renderFocusPlanner();
  flushBrowserViolationNotice();

  if (state.token && state.desktop.available) {
    if (hasDesktopConsent()) {
      await initDesktopBridge();
    } else {
      const consentGranted = await requestDesktopMonitoringConsent({ showSuccessToast: false });
      if (!consentGranted) {
        return;
      }
    }
  } else if (state.token && CURRENT_PAGE === "focus" && !hasBrowserMonitoringConsent()) {
    await requestBrowserMonitoringConsent({ showSuccessToast: false });
  }

  if (state.token) {
    await refreshDashboard();
    if (CURRENT_PAGE === "focus") {
      await handleBrowserModeReturn();
    }
  }
}

function applyPageMeta() {
  const meta = PAGE_META[CURRENT_PAGE] || PAGE_META.home;
  document.title = meta.browserTitle;

  elements.headlineEyebrow.textContent = meta.eyebrow;
  elements.headlineTitle.textContent = meta.title;
  elements.headlineLead.textContent = meta.lead;
  elements.headlineTags.innerHTML = "";
  elements.headlineTags.hidden = true;
}

function enforceRouteBoundary() {
  if (state.token && CURRENT_PAGE === "landing") {
    goToPage("focus");
    return true;
  }

  if (state.token && CURRENT_PAGE === "home") {
    goToPage("focus");
    return true;
  }

  if (!state.token && CURRENT_PAGE !== "landing") {
    goToPage("landing");
    return true;
  }

  return false;
}

function goToPage(page) {
  const fileName = page === "landing" ? "index.html" : `${page}.html`;
  const nextUrl = new URL(`./${fileName}`, window.location.href);
  nextUrl.searchParams.set("v", APP_PAGE_VERSION);
  window.location.replace(nextUrl.href);
}

function injectPenguinBrandBadge() {
  const brand = document.querySelector(".rail-brand");
  if (!brand || brand.querySelector(".penguin-brand-badge")) {
    return;
  }

  brand.insertAdjacentHTML(
    "afterbegin",
    `
      <div class="penguin-brand-badge" aria-hidden="true">
        <img src="./assets/penguin-mark.svg" alt="" />
      </div>
    `
  );
}

function ensureHeadlineVisual() {
  const banner = document.querySelector(".headline-banner");
  const copy = banner?.querySelector(".headline-copy");

  if (!banner || !copy || banner.querySelector(".headline-visual")) {
    return;
  }

  copy.insertAdjacentHTML(
    "afterend",
    `
      <div class="headline-visual" aria-hidden="true"></div>
    `
  );
}

function ensureDesktopConsentControl() {
  if (!elements.desktopGuardNote) {
    return;
  }

  const existingButton = document.querySelector("#desktop-consent-btn");
  if (existingButton) {
    elements.desktopConsentBtn = existingButton;
    return;
  }

  const actions = document.createElement("div");
  actions.className = "guard-consent-actions";
  actions.hidden = true;

  const button = document.createElement("button");
  button.type = "button";
  button.id = "desktop-consent-btn";
  button.className = "ghost-button secondary-tone";
  button.textContent = "Enable Monitor For This Login";
  actions.appendChild(button);

  elements.desktopGuardNote.insertAdjacentElement("afterend", actions);
  elements.desktopConsentBtn = button;
}

function initializePenguinLoader() {
  const hasSeenIntro = sessionStorage.getItem("study_focus_penguin_intro") === "1";
  if (hasSeenIntro) {
    document.body.classList.add("penguin-loader-complete");
    return false;
  }

  document.body.classList.add("penguin-loader-active");

  const overlay = document.createElement("div");
  overlay.className = "penguin-loader";
  overlay.innerHTML = `
    <div class="penguin-loader-card">
      <img class="penguin-loader-icon" src="./assets/penguin-mark.svg" alt="" />
      <p class="penguin-loader-kicker">Study Focus Atlas</p>
      <h2>Penguin mode is warming up the desk.</h2>
      <p class="penguin-loader-copy">Sea, grass, dawn, and lavender are being layered into the workspace.</p>
      <div class="penguin-loader-bar"><span></span></div>
    </div>
  `;
  document.body.appendChild(overlay);

  window.requestAnimationFrame(() => {
    overlay.classList.add("is-ready");
  });

  window.setTimeout(() => {
    overlay.classList.add("is-leaving");
    document.body.classList.remove("penguin-loader-active");
    document.body.classList.add("penguin-loader-complete");
    sessionStorage.setItem("study_focus_penguin_intro", "1");

    if (!uiMotion.initialized) {
      initializeMotionSystem();
    }

    overlay.addEventListener(
      "transitionend",
      () => {
        overlay.remove();
      },
      { once: true }
    );
  }, 15000);

  return true;
}

function initializeMotionSystem() {
  if (uiMotion.initialized) {
    queueMotionRefresh();
    return;
  }

  uiMotion.initialized = true;
  const root = document.querySelector(".page-shell") || document.body;
  decorateRevealTargets(root);

  if (!("IntersectionObserver" in window)) {
    markAllRevealTargetsVisible();
    return;
  }

  uiMotion.observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        uiMotion.observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.16,
      rootMargin: "0px 0px -8% 0px",
    }
  );

  uiMotion.mutationObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (!(node instanceof Element)) {
          return;
        }

        decorateRevealTargets(node);
      });
    });

    queueMotionRefresh();
  });

  uiMotion.mutationObserver.observe(root, {
    childList: true,
    subtree: true,
  });

  queueMotionRefresh();
}

function decorateRevealTargets(root = document.body) {
  if (!root) {
    return;
  }

  const targets = [];
  const selector = ".surface, .table-row, .chat-bubble, .headline-metric, .metric-panel, .hub-card";

  if (root instanceof Element && root.matches(selector)) {
    targets.push(root);
  }

  if (typeof root.querySelectorAll === "function") {
    targets.push(...root.querySelectorAll(selector));
  }

  targets.forEach((target) => {
    if (target.closest(".penguin-loader")) {
      return;
    }

    target.classList.add("reveal-target");
  });
}

function queueMotionRefresh() {
  if (!uiMotion.initialized) {
    return;
  }

  if (uiMotion.refreshFrame) {
    window.cancelAnimationFrame(uiMotion.refreshFrame);
  }

  uiMotion.refreshFrame = window.requestAnimationFrame(() => {
    const targets = Array.from(document.querySelectorAll(".reveal-target"));
    targets.forEach((target, index) => {
      if (target.dataset.revealBound === "1") {
        return;
      }

      target.style.setProperty("--reveal-delay", `${Math.min(index * 26, 320)}ms`);
      target.dataset.revealBound = "1";

      if (uiMotion.observer) {
        uiMotion.observer.observe(target);
      } else {
        target.classList.add("is-visible");
      }
    });

    uiMotion.refreshFrame = 0;
  });
}

function markAllRevealTargetsVisible() {
  document.querySelectorAll(".reveal-target").forEach((target) => {
    target.classList.add("is-visible");
  });
}

function bindEvents() {
  elements.saveApiBaseBtn.addEventListener("click", handleSaveApiBase);
  elements.refreshDashboardBtn.addEventListener("click", () => void refreshDashboard());
  elements.logoutBtn.addEventListener("click", () => void logout());
  elements.fillRegisterDemoBtn.addEventListener("click", fillRegisterDemoForm);
  elements.fillLoginDemoBtn.addEventListener("click", fillLoginDemoForm);

  if (elements.desktopConsentBtn) {
    elements.desktopConsentBtn.addEventListener("click", () => void handleEnableDesktopMonitoring());
  }

  document.addEventListener("visibilitychange", handleBrowserVisibilityChange);
  window.addEventListener("blur", handleBrowserWindowBlur);
  window.addEventListener("focus", handleBrowserWindowFocus);
  window.addEventListener("pageshow", handleBrowserWindowFocus);
  window.addEventListener("pagehide", handleBrowserPageHide);

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

  if (elements.focusPlanForm) {
    elements.focusPlanForm.addEventListener("submit", (event) => {
      event.preventDefault();
      handleAddFocusPlan(event.currentTarget);
    });
  }

  if (elements.focusPlanList) {
    elements.focusPlanList.addEventListener("click", (event) => {
      const deleteButton = event.target.closest("[data-plan-delete-id]");
      if (deleteButton) {
        deleteFocusPlanItem(deleteButton.dataset.planDeleteId || "");
        return;
      }

      const toggleButton = event.target.closest("[data-plan-item-id]");
      if (!toggleButton) {
        return;
      }

      toggleFocusPlanItem(toggleButton.dataset.planItemId || "");
    });
  }

  elements.interruptSessionBtn.addEventListener("click", () => void settleCurrentSession("interrupt"));
  elements.resumeSessionBtn.addEventListener("click", () => void handleResumeFocus());
  elements.abandonSessionBtn.addEventListener("click", () => void settleCurrentSession("abandon"));

  if (elements.refreshQuestionBtn) {
    elements.refreshQuestionBtn.addEventListener("click", () => void loadDailyQuestion());
  }

  if (elements.dailyQuestionForm) {
    elements.dailyQuestionForm.addEventListener("submit", (event) => {
      event.preventDefault();
      void handleSubmitDailyQuestion(event.currentTarget);
    });
  }

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
  if (!state.desktop.available || !hasDesktopConsent()) {
    disconnectDesktopBridge();
    renderDesktopStatus();
    return;
  }

  try {
    if (!state.desktop.unsubscribe) {
      state.desktop.unsubscribe = window.studyFocusDesktop.onGuardEvent((event) => {
        void handleDesktopGuardEvent(event);
      });
    }

    state.desktop.status = await window.studyFocusDesktop.getStatus();
  } catch (error) {
    pushGuardEvent({
      type: "guard_bridge_error",
      detectedAt: new Date().toISOString(),
      message: `Desktop bridge failed: ${error.message}`,
    });
  }

  renderDesktopStatus();
}

async function handleEnableDesktopMonitoring() {
  if (state.desktop.available) {
    await requestDesktopMonitoringConsent();
    return;
  }

  await requestBrowserMonitoringConsent();
}

function disconnectDesktopBridge() {
  if (typeof state.desktop.unsubscribe === "function") {
    state.desktop.unsubscribe();
  }

  state.desktop.unsubscribe = null;
  state.desktop.status = null;
}

function updateAuthView() {
  const isLoggedIn = Boolean(state.token);
  const isLandingPage = CURRENT_PAGE === "landing";

  elements.authPanel.hidden = isLoggedIn || !isLandingPage;
  elements.dashboard.hidden = !isLoggedIn;
  elements.logoutBtn.hidden = !isLoggedIn;
  elements.refreshDashboardBtn.hidden = !isLoggedIn;
  elements.heroAuthState.textContent = isLoggedIn ? "Authenticated" : "Guest";

  renderLeaderboardTabs();
  renderRunningSession();
  renderFocusPlanner();
}

function handleSaveApiBase() {
  const value = elements.apiBaseInput.value.trim().replace(/\/+$/u, "");
  state.apiBase = normalizeApiBaseForCurrentHost(value || DEFAULT_API_BASE);
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
  const username = localStorage.getItem(STORAGE_KEYS.lastDemoUsername) || state.user?.username || DEFAULT_LOGIN_DEMO_USERNAME;
  setFormValue(elements.loginForm, "username", username);
  setFormValue(elements.loginForm, "password", DEFAULT_DEMO_PASSWORD);
  elements.quickStartHint.textContent = `Login form filled with ${username}.`;
  showToast("Login demo values filled.", "success");
}

function prefillFormsFromHistory() {
  const username = localStorage.getItem(STORAGE_KEYS.lastDemoUsername) || DEFAULT_LOGIN_DEMO_USERNAME;
  setFormValue(elements.loginForm, "username", username);
  setFormValue(elements.loginForm, "password", DEFAULT_DEMO_PASSWORD);
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
  disconnectDesktopBridge();
  clearDesktopConsent();
  state.desktop.eventLog = [];
  state.dailyQuestion = null;
  state.focusPlanItems = [];

  if (CURRENT_PAGE === "landing") {
    goToPage("focus");
    return;
  }

  showToast("Login completed.", "success");
  updateAuthView();
  renderDesktopStatus();

  if (state.desktop.available) {
    const consentGranted = await requestDesktopMonitoringConsent({ showSuccessToast: false });
    if (!consentGranted) {
      return;
    }
  } else if (CURRENT_PAGE === "focus") {
    await requestBrowserMonitoringConsent({ showSuccessToast: false });
  }

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

  const profileResponse = await apiFetch("/users/me").catch(handleUiError);
  const profile = profileResponse || state.user;

  if (profileResponse) {
    state.user = profileResponse;
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(profileResponse));
  }

  loadFocusPlanner();

  if (!state.leaderboardSchoolId) {
    state.leaderboardSchoolId = Number(profile?.school_id || 0) || 0;
  }
  if (!state.leaderboardCollegeId) {
    state.leaderboardCollegeId = Number(profile?.college_id || 0) || 0;
  }

  const schoolIdForQueries = Number(state.leaderboardSchoolId || profile?.school_id || 0) || 0;

  const [points, sessions, ledger, question, orders, feedback, schools, colleges, leaderboard] = await Promise.all([
    apiFetch("/points/balance").catch(handleUiError),
    apiFetch("/focus-sessions?page=1&page_size=8").catch(handleUiError),
    apiFetch("/points/ledger?page=1&page_size=8").catch(handleUiError),
    apiFetch("/learning/daily-question").catch(handleUiError),
    apiFetch("/redeem-orders/my?page=1&page_size=8").catch(handleUiError),
    apiFetch("/feedback/my?page=1&page_size=6").catch(handleUiError),
    apiFetch("/dicts/schools", { auth: false }).catch(handleUiError),
    schoolIdForQueries
      ? apiFetch(`/dicts/colleges?school_id=${schoolIdForQueries}`, { auth: false }).catch(handleUiError)
      : Promise.resolve([]),
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

  state.dailyQuestion = question || null;

  renderProfile();
  renderPoints();
  renderSessions();
  renderLedger();
  renderLeaderboardTabs();
  renderLeaderboard();
  renderDailyQuestion(state.dailyQuestion);
  renderOrders();
  renderFeedback();
  renderRunningSession();
  renderFocusPlanner();
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

  if (state.desktop.available) {
    const consentGranted = await requestDesktopMonitoringConsent({ showSuccessToast: false });
    if (!consentGranted) {
      return;
    }
  } else {
    const consentGranted = await requestBrowserMonitoringConsent({ showSuccessToast: false });
    if (!consentGranted) {
      showToast("Web focus checking is required before starting a website-mode session.", "error");
      return;
    }
  }

  const payload = formDataToObject(new FormData(form));
  payload.planned_minutes = Number(payload.planned_minutes);
  payload.lock_mode = "APP_BLOCK";
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
  state.autoCompleteSessionId = 0;
  syncActiveSessionStorage();
  await startDesktopGuardForSession(session);

  const toastMessage = state.desktop.available
    ? "Focus session started with desktop monitoring."
    : "Focus session started with website-mode page checking.";
  showToast(toastMessage, "success");
  await refreshDashboard();
}

async function handleResumeFocus() {
  if (!state.pausedSession) {
    showToast("No interrupted session found.", "error");
    return;
  }

  if (state.desktop.available) {
    const consentGranted = await requestDesktopMonitoringConsent({ showSuccessToast: false });
    if (!consentGranted) {
      return;
    }
  } else {
    const consentGranted = await requestBrowserMonitoringConsent({ showSuccessToast: false });
    if (!consentGranted) {
      showToast("Web focus checking is required before resuming a website-mode session.", "error");
      return;
    }
  }

  const session = await apiFetch(`/focus-sessions/${state.pausedSession.session_id}/resume`, {
    method: "POST",
  }).catch(handleUiError);

  if (!session) {
    return;
  }

  state.activeSession = session;
  state.pausedSession = null;
  state.autoCompleteSessionId = 0;
  syncActiveSessionStorage();
  await startDesktopGuardForSession(session);

  const toastMessage = state.desktop.available
    ? "Focus session resumed with desktop monitoring."
    : "Focus session resumed with website-mode page checking.";
  showToast(toastMessage, "success");
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
    state.autoCompleteSessionId = 0;
    syncActiveSessionStorage();
    await stopDesktopGuard();
    showToast(options.successMessage || "Session interrupted. Resume will continue from the saved time.", "success");
    await refreshDashboard();
    return result;
  }

  state.activeSession = null;
  state.pausedSession = null;
  state.autoCompleteSessionId = 0;
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

async function handleSubmitDailyQuestion(form) {
  if (!state.dailyQuestion?.question_date) {
    showToast("No daily question is ready yet.", "error");
    return;
  }

  if (state.dailyQuestion?.attempt) {
    showToast("Today's daily question has already been answered.", "error");
    return;
  }

  const selectedOption = String(new FormData(form).get("selected_option") || "").trim();
  if (!selectedOption) {
    showToast("Choose one option before submitting.", "error");
    return;
  }

  const result = await apiFetch("/learning/daily-question/answer", {
    method: "POST",
    body: {
      question_date: state.dailyQuestion.question_date,
      selected_option: selectedOption,
    },
  }).catch(handleUiError);

  if (!result) {
    return;
  }

  state.dailyQuestion = {
    ...state.dailyQuestion,
    attempt: result,
  };
  renderDailyQuestion(state.dailyQuestion);

  const toastMessage = result.is_correct
    ? `Correct answer. ${result.awarded_points} points added.`
    : `Answer saved. Correct option is ${result.correct_option}.`;
  showToast(toastMessage, result.is_correct ? "success" : "info");
  await refreshDashboard();
}

async function handleAskAi(form) {
  const formData = new FormData(form);
  const question = String(formData.get("question") || "").trim();
  if (!question) {
    return;
  }

  appendChatBubble("user", question);
  form.reset();

  const reply = await requestAiReply(question).catch((error) => {
    appendChatBubble("assistant", `Request failed: ${error.message}`);
    handleUiError(error);
    return null;
  });

  if (!reply) {
    return;
  }

  appendChatBubble("assistant", reply.answer);
}

async function requestAiReply(question) {
  let lastError = null;

  for (let attempt = 1; attempt <= 2; attempt += 1) {
    try {
      return await apiFetch("/learning/ai-chat", {
        method: "POST",
        body: { question },
      });
    } catch (error) {
      lastError = error;
      if (attempt >= 2 || !shouldRetryAiRequest(error)) {
        throw error;
      }

      showToast("AI provider response looked unstable. Retrying once...", "info");
      await waitForUi(700);
    }
  }

  throw lastError || new Error("AI request failed.");
}

function shouldRetryAiRequest(error) {
  const status = Number(error?.status || 0);
  const message = String(error?.message || "").trim().toLowerCase();

  if (status >= 500) {
    return true;
  }

  return [
    "no choices",
    "empty answer",
    "no readable answer",
    "connection failed",
    "failed to fetch",
  ].some((token) => message.includes(token));
}

function waitForUi(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, Math.max(0, Number(ms) || 0));
  });
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

  state.feedbacks = [feedback, ...state.feedbacks.filter((item) => item.feedback_id !== feedback.feedback_id)].slice(0, 6);
  renderFeedback();
  showToast("Feedback submitted. Thanks for helping improve the app.", "success");
  form.reset();
  setFormValue(form, "category", "GENERAL");
  setFormValue(form, "contact_email", state.user?.email || feedback.contact_email || "");
  void refreshDashboard();
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
    await syncBrowserPageGuard();
    renderDesktopStatus();
    return;
  }

  if (!hasDesktopConsent()) {
    disconnectDesktopBridge();
    renderDesktopStatus();
    return;
  }

  if (!state.desktop.unsubscribe || !state.desktop.status) {
    await initDesktopBridge();
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
    await syncBrowserPageGuard();
    return;
  }

  if (!hasDesktopConsent()) {
    renderDesktopStatus();
    return;
  }

  if (!state.desktop.unsubscribe) {
    await initDesktopBridge();
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
    clearBrowserViolationTimer();
    return;
  }

  if (!hasDesktopConsent()) {
    disconnectDesktopBridge();
    renderDesktopStatus();
    return;
  }

  if (!state.desktop.status?.active) {
    renderDesktopStatus();
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
  state.dailyQuestion = question || null;

  if (!state.dailyQuestion) {
    if (elements.dailyQuestionSubject) {
      elements.dailyQuestionSubject.textContent = "Subject";
    }
    if (elements.dailyQuestionDifficulty) {
      elements.dailyQuestionDifficulty.textContent = "Difficulty";
    }
    elements.dailyQuestionTitle.textContent = "No question loaded.";
    elements.dailyQuestionBody.textContent = "Start by logging in and loading dashboard data.";
    if (elements.dailyQuestionHint) {
      elements.dailyQuestionHint.textContent = "Hint will appear here.";
    }
    if (elements.dailyQuestionPoints) {
      elements.dailyQuestionPoints.textContent = "5 pts";
    }
    if (elements.dailyQuestionOptions) {
      elements.dailyQuestionOptions.innerHTML = `<div class="empty-state">Daily options will appear here.</div>`;
    }
    if (elements.dailyQuestionResult) {
      elements.dailyQuestionResult.textContent = "Answer once per day. A correct answer adds points to your balance and ranking.";
    }
    return;
  }

  const attempt = state.dailyQuestion.attempt;
  if (elements.dailyQuestionSubject) {
    elements.dailyQuestionSubject.textContent = state.dailyQuestion.subject;
  }
  if (elements.dailyQuestionDifficulty) {
    elements.dailyQuestionDifficulty.textContent = state.dailyQuestion.difficulty;
  }
  elements.dailyQuestionTitle.textContent = state.dailyQuestion.title;
  elements.dailyQuestionBody.textContent = state.dailyQuestion.question;
  if (elements.dailyQuestionHint) {
    elements.dailyQuestionHint.textContent = `Hint: ${state.dailyQuestion.answer_hint}`;
  }

  if (elements.dailyQuestionPoints) {
    elements.dailyQuestionPoints.textContent = `${state.dailyQuestion.reward_points || 0} pts`;
  }

  if (elements.dailyQuestionOptions && Array.isArray(state.dailyQuestion.options)) {
    elements.dailyQuestionOptions.innerHTML = state.dailyQuestion.options
      .map((option) => {
        const isSelected = attempt ? attempt.selected_option === option.option_id : false;
        const isCorrect = attempt ? attempt.correct_option === option.option_id : false;
        const isWrong = Boolean(attempt && isSelected && !attempt.is_correct);
        const optionClasses = ["daily-question-option"];

        if (isCorrect) {
          optionClasses.push("is-correct");
        }
        if (isWrong) {
          optionClasses.push("is-wrong");
        }

        return `
          <label class="${optionClasses.join(" ")}">
            <input
              type="radio"
              name="selected_option"
              value="${escapeHtml(option.option_id)}"
              ${isSelected ? "checked" : ""}
              ${attempt ? "disabled" : ""}
            />
            <span class="daily-question-option-badge">${escapeHtml(option.option_id)}</span>
            <span class="daily-question-option-copy">${escapeHtml(option.content)}</span>
          </label>
        `;
      })
      .join("");
  }

  if (elements.dailyQuestionForm) {
    const submitButton = elements.dailyQuestionForm.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.disabled = Boolean(attempt);
    }
  }

  if (elements.dailyQuestionResult) {
    elements.dailyQuestionResult.textContent = attempt
      ? attempt.is_correct
        ? `Correct answer locked in. +${attempt.awarded_points} points counted in your balance and leaderboard.`
        : `Answer saved for today. Correct option: ${attempt.correct_option}. No points awarded this time.`
      : "Answer once per day. A correct answer adds points to your balance and ranking.";
  }
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
            <span class="feedback-category-pill">${escapeHtml(item.category)}</span>
          </div>
          <div class="row-meta">
            <span>${formatDateTime(item.created_at)}</span>
            <span>${escapeHtml(item.status)}</span>
            ${contact}
          </div>
          <div class="row-meta feedback-content-row">
            <span>${escapeHtml(item.content)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function summarizeGuardList(values) {
  const items = Array.isArray(values) ? values.filter(Boolean) : [];
  if (!items.length) {
    return "None";
  }

  if (items.length === 1) {
    return items[0];
  }

  return `${items[0]} +${items.length - 1}`;
}

function buildSessionSummaryMarkup(status, primaryFacts, blockedApps, blockedSites) {
  const pills = primaryFacts
    .map((item) => `<span class="session-summary-pill">${escapeHtml(item)}</span>`)
    .join("");

  return `
    <div class="session-summary-grid">
      <span class="session-status-pill">${escapeHtml(status)}</span>
      ${pills}
    </div>
    <div class="session-summary-grid">
      <span class="session-summary-pill is-soft">Apps ${escapeHtml(blockedApps)}</span>
      <span class="session-summary-pill is-soft">Sites ${escapeHtml(blockedSites)}</span>
    </div>
  `;
}

function renderRunningSession() {
  const running = state.activeSession;
  const paused = state.pausedSession;

  elements.interruptSessionBtn.disabled = !running;
  elements.resumeSessionBtn.hidden = !paused;
  elements.resumeSessionBtn.disabled = !paused;
  elements.abandonSessionBtn.disabled = !(running || paused);

  if (running) {
    const apps = summarizeGuardList(running.blocked_apps_json);
    const sites = summarizeGuardList(running.blocked_sites_json);

    elements.runningSessionSummary.innerHTML = buildSessionSummaryMarkup(
      running.status,
      [`Planned ${running.planned_minutes} min`],
      apps,
      sites
    );
    elements.focusLiveStatus.textContent = `Started at ${formatDateTime(running.start_at)}`;
    elements.heroTimerState.textContent = running.status;
    startTimer();
    return;
  }

  if (paused) {
    const apps = summarizeGuardList(paused.blocked_apps_json);
    const sites = summarizeGuardList(paused.blocked_sites_json);
    const elapsedMs = getSessionElapsedMs(paused);
    const remainingMs = getSessionRemainingMs(paused);

    elements.runningSessionSummary.innerHTML = buildSessionSummaryMarkup(
      paused.status,
      [`Saved ${formatDuration(elapsedMs)} elapsed`, `${formatDuration(remainingMs)} remaining`],
      apps,
      sites
    );
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
  const consentGranted = hasDesktopConsent();
  const browserConsentGranted = hasBrowserMonitoringConsent();
  const consentActions = elements.desktopConsentBtn?.parentElement || null;

  if (consentActions) {
    consentActions.hidden = true;
  }

  if (!available) {
    if (elements.desktopConsentBtn) {
      elements.desktopConsentBtn.textContent = "Enable Web Check For This Login";
    }

    if (!browserConsentGranted) {
      elements.desktopGuardState.textContent = "Web Consent Required";
      elements.desktopGuardNote.textContent = "Website mode can only detect leaving this study page, switching tabs, or switching windows.";
      elements.heroGuardState.textContent = "Web Consent Required";
      elements.guardSupportBadges.innerHTML = [
        renderSupportBadge("Page Focus", false),
        renderSupportBadge("Process Watch", false),
        renderSupportBadge("Site Block", false),
      ].join("");

      if (consentActions && CURRENT_PAGE === "focus") {
        consentActions.hidden = false;
      }

      if (!state.desktop.eventLog.length) {
        elements.guardEventList.innerHTML = `<div class="empty-state">Web checking is off until you grant consent.</div>`;
      } else {
        renderGuardEventLog();
      }
      return;
    }

    const browserLabel = state.activeSession ? "Web Guard Active" : "Web Guard Ready";
    elements.desktopGuardState.textContent = browserLabel;
    elements.desktopGuardNote.textContent = "Website mode only checks whether you leave this study page. It cannot inspect apps or exact websites.";
    elements.heroGuardState.textContent = browserLabel;
    elements.guardSupportBadges.innerHTML = [
      renderSupportBadge("Page Focus", true),
      renderSupportBadge("Process Watch", false),
      renderSupportBadge("Site Block", false),
    ].join("");
    renderGuardEventLog();
    return;
  }

  if (elements.desktopConsentBtn) {
    elements.desktopConsentBtn.textContent = "Enable Monitor For This Login";
  }

  if (!consentGranted) {
    elements.desktopGuardState.textContent = "Consent Required";
    elements.desktopGuardNote.textContent = "Desktop listening needs your permission for this login. If you refuse, the desktop app will close.";
    elements.heroGuardState.textContent = "Consent Required";
    elements.guardSupportBadges.innerHTML = [
      renderSupportBadge("Window Lock", false),
      renderSupportBadge("Process Watch", false),
      renderSupportBadge("Site Block", false),
    ].join("");

    if (consentActions) {
      consentActions.hidden = false;
    }

    if (!state.desktop.eventLog.length) {
      elements.guardEventList.innerHTML = `<div class="empty-state">Monitoring is off until you grant consent.</div>`;
    } else {
      renderGuardEventLog();
    }
    return;
  }

  const activeLabel = status?.active ? "Desktop Active" : "Desktop Ready";
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
    state.autoCompleteSessionId = 0;
    return;
  }

  const started = new Date(state.activeSession.start_at).getTime();
  const plannedMs = Number(state.activeSession.planned_minutes) * 60 * 1000;
  const endMs = started + plannedMs;
  const remaining = Math.max(0, endMs - Date.now());
  elements.focusLiveTimer.textContent = formatDuration(remaining);

  if (remaining === 0) {
    scheduleSessionAutoComplete(state.activeSession.session_id);
  }
}

function scheduleSessionAutoComplete(sessionId) {
  if (!sessionId || state.autoCompleteSessionId === sessionId) {
    return;
  }

  state.autoCompleteSessionId = sessionId;
  window.setTimeout(async () => {
    if (state.activeSession?.session_id !== sessionId) {
      return;
    }

    const result = await settleCurrentSession(
      "complete",
      {},
      { successMessage: "Session completed automatically. Points awarded." }
    );

    if (!result && state.activeSession?.session_id === sessionId) {
      state.autoCompleteSessionId = 0;
    }
  }, 1200);
}

function appendChatBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role === "user" ? "user-bubble" : "assistant-bubble"}`;
  bubble.textContent = text;
  elements.chatHistory.appendChild(bubble);
  elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
}

async function logout() {
  stopTimer();
  await stopDesktopGuard();
  disconnectDesktopBridge();
  clearDesktopConsent();
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
  state.dailyQuestion = null;
  state.focusPlanItems = [];
  state.desktop.eventLog = [];
  localStorage.removeItem(STORAGE_KEYS.token);
  localStorage.removeItem(STORAGE_KEYS.user);
  localStorage.removeItem(STORAGE_KEYS.activeSession);
  updateAuthView();
  renderFocusPlanner();
  renderDesktopStatus();

  if (CURRENT_PAGE !== "landing") {
    goToPage("landing");
    return;
  }

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
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return data;
}

function handleUiError(error) {
  const rawMessage = String(error?.message || "").trim();
  const message = rawMessage === "Failed to fetch"
    ? `Cannot reach API at ${state.apiBase}. For local testing, it should be http://127.0.0.1:8000/api/v1.`
    : rawMessage || "Unexpected error.";

  showToast(message, "error");
  return null;
}

function showToast(message, type = "info") {
  elements.toast.hidden = false;
  elements.toast.textContent = message;
  elements.toast.className = `toast${type === "error" ? " is-error" : ""}${type === "success" ? " is-success" : ""}`;

  if (type === "success") {
    launchCelebration();
  }

  window.clearTimeout(showToast.timerId);
  showToast.timerId = window.setTimeout(() => {
    elements.toast.hidden = true;
  }, 3600);
}

function ensureCelebrationLayer() {
  let layer = document.querySelector("#celebration-layer");
  if (layer) {
    return layer;
  }

  layer = document.createElement("div");
  layer.id = "celebration-layer";
  layer.className = "celebration-layer";
  document.body.appendChild(layer);
  return layer;
}

function launchCelebration() {
  const now = Date.now();
  if (now - (launchCelebration.lastAt || 0) < 700) {
    return;
  }
  launchCelebration.lastAt = now;

  const layer = ensureCelebrationLayer();
  const toastRect = elements.toast.getBoundingClientRect();
  const originX = Math.min(window.innerWidth - 72, Math.max(72, toastRect.left + toastRect.width / 2));
  const originY = Math.min(window.innerHeight - 120, Math.max(84, toastRect.top + Math.min(toastRect.height / 2, 48)));
  const colors = ["#356df3", "#1d8a70", "#bc6b19", "#7c54d3", "#d95c49", "#f3b246"];

  for (let index = 0; index < 18; index += 1) {
    const spark = document.createElement("span");
    const angle = ((Math.PI * 2) / 18) * index + Math.random() * 0.24;
    const distance = 52 + Math.random() * 66;
    spark.className = "celebration-spark";
    spark.style.left = `${originX}px`;
    spark.style.top = `${originY}px`;
    spark.style.setProperty("--dx", `${Math.cos(angle) * distance}px`);
    spark.style.setProperty("--dy", `${Math.sin(angle) * distance}px`);
    spark.style.setProperty("--spark-size", `${8 + Math.random() * 10}px`);
    spark.style.setProperty("--spark-color", colors[index % colors.length]);
    spark.addEventListener("animationend", () => spark.remove(), { once: true });
    layer.appendChild(spark);
  }
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

function readDesktopConsentStatus() {
  try {
    return sessionStorage.getItem(STORAGE_KEYS.desktopConsent) === "granted";
  } catch {
    return false;
  }
}

function hasDesktopConsent() {
  return Boolean(state.desktop.available && state.desktop.consent);
}

async function requestDesktopMonitoringConsent({ showSuccessToast = true } = {}) {
  if (!state.desktop.available) {
    return false;
  }

  if (hasDesktopConsent()) {
    return true;
  }

  if (state.desktop.promptInFlight) {
    return false;
  }

  state.desktop.promptInFlight = true;

  try {
    const result = typeof window.studyFocusDesktop?.requestMonitoringConsent === "function"
      ? await window.studyFocusDesktop.requestMonitoringConsent()
      : { granted: window.confirm("Allow desktop monitoring for this login session?") };

    if (!result?.granted) {
      disconnectDesktopBridge();
      renderDesktopStatus();

      if (typeof window.studyFocusDesktop?.quitApp === "function") {
        await window.studyFocusDesktop.quitApp();
      }

      return false;
    }

    sessionStorage.setItem(STORAGE_KEYS.desktopConsent, "granted");
    state.desktop.consent = true;
    await initDesktopBridge();
    await syncDesktopGuard();

    if (showSuccessToast) {
      showToast("Desktop monitoring enabled for this login.", "success");
    }

    return true;
  } catch (error) {
    showToast(`Desktop permission prompt failed: ${error.message}`, "error");
    renderDesktopStatus();
    return false;
  } finally {
    state.desktop.promptInFlight = false;
  }
}

async function requestBrowserMonitoringConsent({ showSuccessToast = true } = {}) {
  if (state.desktop.available) {
    return false;
  }

  if (hasBrowserMonitoringConsent()) {
    return true;
  }

  if (state.web.promptInFlight) {
    return false;
  }

  state.web.promptInFlight = true;

  try {
    const granted = window.confirm(
      "Allow website-mode focus checking for this login session? In web mode, we can only detect when you leave this study page, switch tabs, or switch windows."
    );

    if (!granted) {
      renderDesktopStatus();
      return false;
    }

    sessionStorage.setItem(STORAGE_KEYS.browserConsent, "granted");
    state.web.consent = true;
    await syncBrowserPageGuard();
    renderDesktopStatus();

    if (showSuccessToast) {
      showToast("Website-mode focus checking enabled for this login.", "success");
    }

    return true;
  } catch (error) {
    showToast(`Web focus permission prompt failed: ${error.message}`, "error");
    renderDesktopStatus();
    return false;
  } finally {
    state.web.promptInFlight = false;
  }
}

async function syncBrowserPageGuard() {
  if (state.desktop.available) {
    clearBrowserAwayState();
    clearBrowserViolationTimer();
    return;
  }

  if (!hasBrowserMonitoringConsent()) {
    clearBrowserAwayState();
    clearBrowserViolationTimer();
    renderDesktopStatus();
    return;
  }

  if (!state.activeSession) {
    clearBrowserAwayState();
    clearBrowserViolationTimer();
    renderDesktopStatus();
    return;
  }

  if (CURRENT_PAGE !== "focus") {
    await handleBrowserModeViolation("route_change");
    return;
  }

  renderDesktopStatus();
}

function handleBrowserVisibilityChange() {
  if (document.hidden) {
    scheduleBrowserModeViolation("tab_hidden");
    return;
  }

  void handleBrowserModeReturn();
}

function handleBrowserWindowBlur() {
  scheduleBrowserModeViolation("window_blur");
}

function handleBrowserWindowFocus() {
  void handleBrowserModeReturn();
}

function handleBrowserPageHide() {
  scheduleBrowserModeViolation("route_change");
}

function scheduleBrowserModeViolation(trigger) {
  if (state.desktop.available || !hasBrowserMonitoringConsent() || !state.activeSession || CURRENT_PAGE !== "focus") {
    return;
  }

  if (state.web.promptInFlight || state.guardInterruptInFlight) {
    return;
  }

  const existingAwayState = state.web.awayStartedAt
    ? { startedAt: state.web.awayStartedAt, trigger: state.web.awayTrigger }
    : readBrowserAwayState();

  if (existingAwayState.startedAt) {
    return;
  }

  const startedAt = Date.now();
  state.web.awayStartedAt = startedAt;
  state.web.awayTrigger = trigger;
  persistBrowserAwayState(startedAt, trigger);
}

function clearBrowserViolationTimer() {
  if (state.web.violationTimerId) {
    window.clearTimeout(state.web.violationTimerId);
    state.web.violationTimerId = null;
  }
}

async function handleBrowserModeReturn() {
  clearBrowserViolationTimer();

  const awayState = state.web.awayStartedAt
    ? { startedAt: state.web.awayStartedAt, trigger: state.web.awayTrigger }
    : readBrowserAwayState();

  if (!awayState.startedAt) {
    flushBrowserViolationNotice();
    return;
  }

  if (CURRENT_PAGE !== "focus") {
    return;
  }

  if (state.desktop.available || !hasBrowserMonitoringConsent()) {
    clearBrowserAwayState();
    flushBrowserViolationNotice();
    return;
  }

  if (!state.activeSession) {
    clearBrowserAwayState();
    flushBrowserViolationNotice();
    return;
  }

  clearBrowserAwayState();

  if (Date.now() - awayState.startedAt < 15000) {
    flushBrowserViolationNotice();
    return;
  }

  await handleBrowserModeViolation(awayState.trigger || "window_blur", { presentOnCurrentPage: true });
}

async function handleBrowserModeViolation(trigger, { presentOnCurrentPage = false } = {}) {
  if (state.desktop.available || !hasBrowserMonitoringConsent() || !state.activeSession || state.guardInterruptInFlight) {
    return;
  }

  clearBrowserViolationTimer();
  clearBrowserAwayState();

  const messages = {
    tab_hidden: "You left the Learning page for more than 15 seconds. The website-mode focus session will be abandoned.",
    window_blur: "The Learning page lost focus for more than 15 seconds. The website-mode focus session will be abandoned.",
    route_change: "You left the Learning page during an active website-mode focus session. The session will be abandoned.",
  };

  const event = {
    type: "browser_focus_lost",
    detectedAt: new Date().toISOString(),
    message: messages[trigger] || "Website-mode guard detected that the study page lost focus.",
  };
  const noticeMessage = `${event.message}\n\nSession abandoned and no points were awarded.`;

  pushGuardEvent(event);
  showToast(event.message, "error");
  if (presentOnCurrentPage && CURRENT_PAGE === "focus" && !document.hidden) {
    showBrowserViolationModal(noticeMessage);
  } else {
    persistBrowserViolationNotice(event.message);
  }

  state.guardInterruptInFlight = true;
  try {
    await settleCurrentSession(
      "abandon",
      { remark: `Web guard violation: ${trigger}` },
      { successMessage: "Session ended by website-mode guard. Progress cleared and no points awarded." }
    );
  } finally {
    state.guardInterruptInFlight = false;
  }
}

function persistBrowserViolationNotice(message) {
  try {
    sessionStorage.setItem(STORAGE_KEYS.browserViolationNotice, String(message || "").trim());
  } catch {
    // Ignore storage errors for private sessions.
  }
}

function flushBrowserViolationNotice() {
  if (CURRENT_PAGE !== "focus") {
    return;
  }

  let notice = "";

  try {
    notice = String(sessionStorage.getItem(STORAGE_KEYS.browserViolationNotice) || "").trim();
  } catch {
    notice = "";
  }

  if (!notice) {
    return;
  }

  try {
    sessionStorage.removeItem(STORAGE_KEYS.browserViolationNotice);
  } catch {
    // Ignore storage errors for private sessions.
  }

  showBrowserViolationModal(`${notice}\n\nSession abandoned and no points were awarded.`);
}

function persistBrowserAwayState(startedAt, trigger) {
  const safeStartedAt = Number(startedAt) || 0;
  const safeTrigger = String(trigger || "window_blur").trim() || "window_blur";

  try {
    sessionStorage.setItem(
      STORAGE_KEYS.browserAwayState,
      JSON.stringify({
        startedAt: safeStartedAt,
        trigger: safeTrigger,
      })
    );
  } catch {
    // Ignore storage errors for private sessions.
  }
}

function readBrowserAwayState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEYS.browserAwayState);
    if (!raw) {
      return { startedAt: 0, trigger: "" };
    }

    const parsed = JSON.parse(raw);
    return {
      startedAt: Number(parsed?.startedAt) || 0,
      trigger: String(parsed?.trigger || "").trim(),
    };
  } catch {
    return { startedAt: 0, trigger: "" };
  }
}

function clearBrowserAwayState() {
  state.web.awayStartedAt = 0;
  state.web.awayTrigger = "";

  try {
    sessionStorage.removeItem(STORAGE_KEYS.browserAwayState);
  } catch {
    // Ignore storage errors for private sessions.
  }
}

function ensureBrowserViolationModal() {
  let overlay = document.querySelector("#browser-violation-modal");
  if (overlay) {
    return overlay;
  }

  overlay = document.createElement("div");
  overlay.id = "browser-violation-modal";
  overlay.className = "browser-violation-modal";
  overlay.hidden = true;
  overlay.innerHTML = `
    <div class="browser-violation-modal__card surface" role="alertdialog" aria-modal="true" aria-labelledby="browser-violation-title">
      <div class="browser-violation-modal__head">
        <h3 id="browser-violation-title">Focus Session Abandoned</h3>
        <button type="button" class="browser-violation-modal__close" aria-label="Close">Close</button>
      </div>
      <p class="browser-violation-modal__body"></p>
      <button type="button" class="primary-button browser-violation-modal__action">OK</button>
    </div>
  `;
  document.body.appendChild(overlay);

  const close = () => hideBrowserViolationModal();
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) {
      close();
      return;
    }

    if (event.target.closest(".browser-violation-modal__close") || event.target.closest(".browser-violation-modal__action")) {
      close();
    }
  });

  return overlay;
}

function showBrowserViolationModal(message) {
  const overlay = ensureBrowserViolationModal();
  const body = overlay.querySelector(".browser-violation-modal__body");
  if (body) {
    body.textContent = String(message || "").trim();
  }

  overlay.hidden = false;
  document.body.classList.add("browser-violation-open");
}

function hideBrowserViolationModal() {
  const overlay = document.querySelector("#browser-violation-modal");
  if (!overlay) {
    return;
  }

  overlay.hidden = true;
  document.body.classList.remove("browser-violation-open");
}

function clearDesktopConsent() {
  try {
    sessionStorage.removeItem(STORAGE_KEYS.desktopConsent);
    sessionStorage.removeItem(STORAGE_KEYS.browserConsent);
    sessionStorage.removeItem(STORAGE_KEYS.browserViolationNotice);
  } catch {
    // Ignore storage errors for private sessions.
  }

  state.desktop.consent = false;
  state.desktop.promptInFlight = false;
  state.web.consent = false;
  state.web.promptInFlight = false;
  clearBrowserAwayState();
  clearBrowserViolationTimer();
}

function readBrowserConsentStatus() {
  try {
    return sessionStorage.getItem(STORAGE_KEYS.browserConsent) === "granted";
  } catch {
    return false;
  }
}

function hasBrowserMonitoringConsent() {
  return Boolean(!state.desktop.available && state.web.consent);
}

function getFocusPlanStorageKey() {
  const username = String(state.user?.username || "").trim();
  return username ? `${FOCUS_PLAN_STORAGE_PREFIX}${username}` : "";
}

function loadFocusPlanner() {
  const storageKey = getFocusPlanStorageKey();
  if (!storageKey) {
    state.focusPlanItems = [];
    renderFocusPlanner();
    return;
  }

  try {
    const raw = localStorage.getItem(storageKey);
    const parsed = raw ? JSON.parse(raw) : [];
    state.focusPlanItems = Array.isArray(parsed)
      ? parsed
        .filter((item) => item && typeof item.id === "string" && typeof item.text === "string")
        .map((item) => ({
          id: item.id,
          text: item.text,
          done: Boolean(item.done),
        }))
      : [];
  } catch {
    state.focusPlanItems = [];
  }

  renderFocusPlanner();
}

function persistFocusPlanner() {
  const storageKey = getFocusPlanStorageKey();
  if (!storageKey) {
    return;
  }

  localStorage.setItem(storageKey, JSON.stringify(state.focusPlanItems));
}

function handleAddFocusPlan(form) {
  if (!state.token || !state.user) {
    showToast("Login first to keep a local plan.", "error");
    return;
  }

  const task = String(new FormData(form).get("task") || "").trim();
  if (!task) {
    showToast("Enter one short task first.", "error");
    return;
  }

  state.focusPlanItems = [
    ...state.focusPlanItems,
    {
      id: `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      text: task.slice(0, 120),
      done: false,
    },
  ].slice(-8);

  persistFocusPlanner();
  renderFocusPlanner();
  form.reset();
  showToast("Plan item added.", "success");
}

function toggleFocusPlanItem(itemId) {
  if (!itemId) {
    return;
  }

  state.focusPlanItems = state.focusPlanItems.map((item) => {
    if (item.id !== itemId) {
      return item;
    }

    return {
      ...item,
      done: !item.done,
    };
  });

  persistFocusPlanner();
  renderFocusPlanner();
}

function deleteFocusPlanItem(itemId) {
  if (!itemId) {
    return;
  }

  const nextItems = state.focusPlanItems.filter((item) => item.id !== itemId);
  if (nextItems.length === state.focusPlanItems.length) {
    return;
  }

  state.focusPlanItems = nextItems;
  persistFocusPlanner();
  renderFocusPlanner();
}

function renderFocusPlanner() {
  const taskInput = elements.focusPlanForm?.elements.namedItem("task");
  const addButton = elements.focusPlanForm?.querySelector('button[type="submit"]');
  const isReady = Boolean(state.token && state.user);

  if (taskInput) {
    taskInput.disabled = !isReady;
    taskInput.placeholder = isReady
      ? "Add one task you want to finish in this session."
      : "Login to keep a local study plan.";
  }

  if (addButton) {
    addButton.disabled = !isReady;
  }

  if (!elements.focusPlanList) {
    return;
  }

  if (!isReady) {
    elements.focusPlanList.className = "focus-plan-list empty-state";
    elements.focusPlanList.textContent = "Login to keep a local study plan.";
    return;
  }

  if (!state.focusPlanItems.length) {
    elements.focusPlanList.className = "focus-plan-list empty-state";
    elements.focusPlanList.textContent = "No plan items yet.";
    return;
  }

  elements.focusPlanList.className = "focus-plan-list";
  elements.focusPlanList.innerHTML = state.focusPlanItems
    .map((item) => {
      return `
        <div class="focus-plan-row">
          <button type="button" class="focus-plan-item ${item.done ? "is-done" : ""}" data-plan-item-id="${escapeHtml(item.id)}">
            <span class="focus-plan-mark">${item.done ? "✓" : ""}</span>
            <span class="focus-plan-copy">${escapeHtml(item.text)}</span>
          </button>
          <button type="button" class="focus-plan-delete" data-plan-delete-id="${escapeHtml(item.id)}" aria-label="Delete task">Delete</button>
        </div>
      `;
    })
    .join("");
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












