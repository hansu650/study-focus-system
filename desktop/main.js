const { app, BrowserWindow, ipcMain, shell } = require("electron");
const path = require("node:path");

const { createFocusGuard } = require("./guard/focusGuard");

let mainWindow = null;

const guard = createFocusGuard({
  emit(event) {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send("guard:event", event);
    }
  },
});

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

  ipcMain.handle("desktop:start-guard", async (_, payload) => {
    return guard.start(payload, mainWindow);
  });

  ipcMain.handle("desktop:stop-guard", async () => {
    return guard.stop(mainWindow);
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
