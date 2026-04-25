const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');

// 开发模式标志
const isDev = process.argv.includes('--dev');

// 窗口引用
let mainWindow = null;
let loginWindow = null;
let currentUserType = null;

// 创建登录窗口
function createLoginWindow() {
  loginWindow = new BrowserWindow({
    width: 1000,
    height: 720,
    minWidth: 1000,
    minHeight: 720,
    title: 'EAMSCLAW - 企业级AI跨电商客服智能体',
    icon: path.join(__dirname, 'assets/icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false,
    center: true,
    resizable: false,
    maximizable: false,
    fullscreenable: false,
    frame: false,
    autoHideMenuBar: true
  });

  loginWindow.loadFile(path.join(__dirname, 'renderer/login.html'));

  loginWindow.once('ready-to-show', () => {
    loginWindow.show();
  });

  loginWindow.on('closed', () => {
    loginWindow = null;
    // 只有在没有主窗口时才退出应用
    if (!mainWindow) {
      app.quit();
    }
  });

  loginWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// 创建主窗口
function createMainWindow(userType) {
  currentUserType = userType;
  
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    title: userType === 'provider' ? 'EAMSCLAW 服务商管理后台' : 'EAMSCLAW 商家管理后台',
    icon: path.join(__dirname, 'assets/icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: false
    },
    show: false,
    center: true,
    frame: true,
    autoHideMenuBar: true
  });

  if (isDev) {
    const basePath = 'http://localhost:5176';
    const appPath = userType === 'provider' ? `${basePath}/#/provider/dashboard` : basePath;
    mainWindow.loadURL(appPath);
  } else {
    const indexPath = path.join(__dirname, 'app/merchant/index.html');
    if (userType === 'provider') {
      mainWindow.loadURL(`file://${indexPath}#/provider/dashboard`);
    } else {
      mainWindow.loadFile(indexPath);
    }
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (loginWindow) {
      loginWindow.close();
      loginWindow = null;
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    currentUserType = null;
    // 不退出应用，让用户可以重新登录
    if (!loginWindow) {
      createLoginWindow();
    }
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// 存储用户登录信息（使用内存存储）
let storedUserType = null;
let storedUsername = null;
let rememberAccount = false;

// IPC 处理
ipcMain.handle('login', async (event, { userType, username, password, rememberMe }) => {
  console.log('[Login]', userType, username);
  storedUserType = userType;
  if (rememberMe) {
    storedUsername = username;
    rememberAccount = true;
  }
  createMainWindow(userType);
  return { success: true };
});

ipcMain.handle('logout', () => {
  if (mainWindow) {
    mainWindow.close();
    mainWindow = null;
  }
  // 不清除存储的信息，这样重新打开登录窗口时可以恢复
  if (!loginWindow) createLoginWindow();
  return { success: true };
});

ipcMain.handle('get-user-type', () => {
  return storedUserType || 'merchant';
});

ipcMain.handle('save-user-type', (event, type) => {
  storedUserType = type;
});

ipcMain.handle('get-saved-account', () => {
  return {
    username: rememberAccount ? storedUsername : null,
    userType: storedUserType,
    rememberMe: rememberAccount
  };
});

ipcMain.handle('save-account', (event, { username, userType, rememberMe }) => {
  storedUsername = username;
  storedUserType = userType;
  rememberAccount = rememberMe;
});

ipcMain.handle('minimize-window', () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) win.minimize();
});

ipcMain.handle('maximize-window', () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) {
    if (win.isMaximized()) win.unmaximize();
    else win.maximize();
  }
});

ipcMain.handle('close-window', () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) win.close();
});

// 应用启动
app.whenReady().then(() => {
  createLoginWindow();
});

app.on('window-all-closed', () => {
  app.quit();
});

// 防止多开
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
}
