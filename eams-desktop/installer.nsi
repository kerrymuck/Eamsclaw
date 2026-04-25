; EAMSCLAW Installer Script
; NSIS Modern UI

!include "MUI2.nsh"
!include "LogicLib.nsh"

; 应用程序信息
!define APPNAME "EAMSCLAW"
!define COMPANYNAME "EAMSCLAW"
!define DESCRIPTION "企业级AI电商客服中控台"
!define VERSION "1.0.0"
!define INSTALLSIZE "300000"

; 安装程序名称
Name "${APPNAME} ${VERSION}"
OutFile "dist\EAMSCLAW-Setup-${VERSION}.exe"

; 默认安装目录
InstallDir "$PROGRAMFILES64\${APPNAME}"

; 请求管理员权限
RequestExecutionLevel admin

; 现代UI配置
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME

; 许可协议页面（可选）
; !insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

; 安装目录选择页面
!insertmacro MUI_PAGE_DIRECTORY

; 安装进度页面
!insertmacro MUI_PAGE_INSTFILES

; 完成页面
!define MUI_FINISHPAGE_RUN "$INSTDIR\EAMSCLAW.exe"
!define MUI_FINISHPAGE_RUN_TEXT "立即运行 EAMSCLAW"
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装部分
Section "Install"
    ; 设置安装目录
    SetOutPath "$INSTDIR"
    
    ; 复制所有文件
    File /r "dist\EAMSCLAW-win32-x64\*"
    
    ; 创建桌面快捷方式
    CreateShortcut "$DESKTOP\EAMSCLAW.lnk" "$INSTDIR\EAMSCLAW.exe"
    
    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\EAMSCLAW.lnk" "$INSTDIR\EAMSCLAW.exe"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\卸载 EAMSCLAW.lnk" "$INSTDIR\uninstall.exe"
    
    ; 写入注册表
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\EAMSCLAW.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "${INSTALLSIZE}"
    
    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; 卸载部分
Section "Uninstall"
    ; 删除桌面快捷方式
    Delete "$DESKTOP\EAMSCLAW.lnk"
    
    ; 删除开始菜单快捷方式
    Delete "$SMPROGRAMS\${APPNAME}\EAMSCLAW.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\卸载 EAMSCLAW.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; 删除安装目录
    RMDir /r "$INSTDIR"
    
    ; 删除注册表项
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
