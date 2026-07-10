const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');

// Load .env from the app directory in packaged builds
if (app.isPackaged) {
  require('dotenv').config({ path: path.join(app.getAppPath(), '.env') });
}

const isDev = !app.isPackaged;

let mainWindow;
let overlayWindow;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../build/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (overlayWindow) {
      overlayWindow.close();
    }
  });
}

function createOverlayWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  overlayWindow = new BrowserWindow({
    width: 420,
    height: 300,
    x: width - 440,
    y: 20,
    alwaysOnTop: true,
    visibleOnAllWorkspaces: true,
    skipTaskbar: true,
    frame: false,
    transparent: true,
    backgroundColor: '#00000000',
    resizable: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  overlayWindow.setIgnoreMouseEvents(false);
  overlayWindow.setAlwaysOnTop(true, 'screen-saver');
  overlayWindow.setContentProtection(true);

  if (isDev) {
    overlayWindow.loadURL('http://localhost:3000#/overlay');
  } else {
    overlayWindow.loadFile(path.join(__dirname, '../build/index.html'), {
      hash: 'overlay',
    });
  }

  overlayWindow.on('closed', () => {
    overlayWindow = null;
  });
}

ipcMain.handle('show-overlay', () => {
  if (!overlayWindow || overlayWindow.isDestroyed()) {
    createOverlayWindow();
  } else {
    overlayWindow.show();
  }
});

ipcMain.handle('hide-overlay', () => {
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.hide();
  }
});

ipcMain.handle('close-overlay', () => {
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.close();
  }
});

ipcMain.handle('move-overlay', (event, dx, dy) => {
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    const [x, y] = overlayWindow.getPosition();
    overlayWindow.setPosition(x + dx, y + dy);
  }
});

ipcMain.handle('resize-overlay', (event, width, height) => {
  if (overlayWindow && !overlayWindow.isDestroyed()) {
    overlayWindow.setSize(width, height);
  }
});

ipcMain.handle('get-env', () => ({
  API_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
}));

app.whenReady().then(() => {
  createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
