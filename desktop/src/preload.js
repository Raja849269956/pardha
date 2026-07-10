const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  showOverlay: () => ipcRenderer.invoke('show-overlay'),
  hideOverlay: () => ipcRenderer.invoke('hide-overlay'),
  closeOverlay: () => ipcRenderer.invoke('close-overlay'),
  moveOverlay: (dx, dy) => ipcRenderer.invoke('move-overlay', dx, dy),
  resizeOverlay: (width, height) => ipcRenderer.invoke('resize-overlay', width, height),
  getEnv: () => ipcRenderer.invoke('get-env'),
});
