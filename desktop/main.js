const { app, BrowserWindow, dialog, ipcMain, shell } = require("electron");
const path = require("node:path");

const { createFocusGuard } = require("./guard/focusGuard");

let mainWindow = null;
let violationDialogOpen = false;

const VIOLATION_EVENT_TYPES = new Set(["blocked_app_detected", "blocked_site_detected"]);

const guard = createFocusGuard({
  emit(event) {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send("guard:event", event);
    }

    if (VIOLATION_EVENT_TYPES.has(event?.type)) {
      void showViolationDialog(event);
    }
  },
});

async function showViolationDialog(event) {
  if (!mainWindow || mainWindow.isDestroyed() || violationDialogOpen) {
    return;
  }

  violationDialogOpen = true;
  try {
    await dialog.showMessageBox(mainWindow, {
      type: "warning",
      buttons: ["OK"],
      defaultId: 0,
      noLink: true,
      title: "Focus Violation Detected",
      message: "Focus session ended",
      detail: event?.message || "A blocked app or website was detected. Progress has been cleared and no points were awarded.",
    });
  } finally {
    violationDialogOpen = false;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1560,
    height: 980,
    minWidth: 1320,
    minHeight: 860,
    backgroundColor: "#e9dfcf",
    title: "Study Focus Desktop",
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "..", "frontend", "index.html"));

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    void shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function registerIpc() {
  ipcMain.handle("desktop:get-status", () => {
    return guard.getStatus();
  });

  ipcMain.handle("desktop:request-monitoring-consent", async () => {
    if (!mainWindow || mainWindow.isDestroyed()) {
      return { granted: false };
    }

    const result = await dialog.showMessageBox(mainWindow, {
      type: "question",
      buttons: ["Allow Monitoring", "Exit App"],
      defaultId: 0,
      cancelId: 1,
      noLink: true,
      title: "Desktop Monitoring Permission",
      message: "Allow desktop monitoring for this login session?",
      detail:
        "The app will only listen for blocked apps and blocked sites after you agree. If you do not allow monitoring, the desktop app will close.",
    });

    return { granted: result.response === 0 };
  });

  ipcMain.handle("desktop:start-guard", async (_, payload) => {
    return guard.start(payload, mainWindow);
  });

  ipcMain.handle("desktop:stop-guard", async () => {
    return guard.stop(mainWindow);
  });

  ipcMain.handle("desktop:quit-app", async () => {
    await guard.stop(mainWindow);
    app.quit();
    return true;
  });
}

app.whenReady().then(() => {
  registerIpc();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", async () => {
  await guard.stop(mainWindow);
  if (process.platform !== "darwin") {
    app.quit();
  }
});
