const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("studyFocusDesktop", {
  isAvailable: true,
  getStatus() {
    return ipcRenderer.invoke("desktop:get-status");
  },
  requestMonitoringConsent() {
    return ipcRenderer.invoke("desktop:request-monitoring-consent");
  },
  startGuard(payload) {
    return ipcRenderer.invoke("desktop:start-guard", payload);
  },
  listBlockingApps() {
    return ipcRenderer.invoke("desktop:list-blocking-apps");
  },
  stopGuard() {
    return ipcRenderer.invoke("desktop:stop-guard");
  },
  quitApp() {
    return ipcRenderer.invoke("desktop:quit-app");
  },
  onGuardEvent(callback) {
    const listener = (_, event) => callback(event);
    ipcRenderer.on("guard:event", listener);

    return () => {
      ipcRenderer.removeListener("guard:event", listener);
    };
  },
});
