const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("studyFocusDesktop", {
  isAvailable: true,
  getStatus() {
    return ipcRenderer.invoke("desktop:get-status");
  },
  startGuard(payload) {
    return ipcRenderer.invoke("desktop:start-guard", payload);
  },
  stopGuard() {
    return ipcRenderer.invoke("desktop:stop-guard");
  },
  onGuardEvent(callback) {
    const listener = (_, event) => callback(event);
    ipcRenderer.on("guard:event", listener);

    return () => {
      ipcRenderer.removeListener("guard:event", listener);
    };
  },
});
