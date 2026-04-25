const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 登录相关
  login: (data) => ipcRenderer.invoke('login', data),
  logout: () => ipcRenderer.invoke('logout'),
  getUserType: () => ipcRenderer.invoke('get-user-type'),
  saveUserType: (type) => ipcRenderer.invoke('save-user-type', type),
  getSavedAccount: () => ipcRenderer.invoke('get-saved-account'),
  saveAccount: (data) => ipcRenderer.invoke('save-account', data),
  
  // 窗口控制
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),
  
  // 平台信息
  platform: process.platform,
  
  // 监听事件
  onLoginSuccess: (callback) => ipcRenderer.on('login-success', callback),
  onLogout: (callback) => ipcRenderer.on('logout', callback)
});
