# 修复 merchant 文件
$merchantDir = "E:\EAMS-Project\eams-desktop\app\merchant"

# 修复 index.html
$htmlFile = "$merchantDir\index.html"
if (Test-Path $htmlFile) {
    $content = Get-Content -Raw -Path $htmlFile
    $content = $content -replace 'src="/assets/', 'src="./assets/'
    $content = $content -replace 'href="/assets/', 'href="./assets/'
    $content | Set-Content -Path $htmlFile -NoNewline
    Write-Host "Fixed merchant/index.html"
}

# 修复所有 JS 文件中的路径
Get-ChildItem -Path "$merchantDir\assets" -Filter "*.js" | ForEach-Object {
    $content = Get-Content -Raw -Path $_.FullName
    # 替换 __vite__mapDeps 中的路径
    $content = $content -replace '\["assets/', '["./assets/'
    $content = $content -replace ',"assets/', ',"./assets/'
    $content | Set-Content -Path $_.FullName -NoNewline
}
Write-Host "Fixed merchant JS files"

# 修复 provider 文件
$providerDir = "E:\EAMS-Project\eams-desktop\app\provider"

# 修复 index.html
$htmlFile = "$providerDir\index.html"
if (Test-Path $htmlFile) {
    $content = Get-Content -Raw -Path $htmlFile
    $content = $content -replace 'src="/assets/', 'src="./assets/'
    $content = $content -replace 'href="/assets/', 'href="./assets/'
    $content | Set-Content -Path $htmlFile -NoNewline
    Write-Host "Fixed provider/index.html"
}

# 修复所有 JS 文件中的路径
Get-ChildItem -Path "$providerDir\assets" -Filter "*.js" | ForEach-Object {
    $content = Get-Content -Raw -Path $_.FullName
    # 替换 __vite__mapDeps 中的路径
    $content = $content -replace '\["assets/', '["./assets/'
    $content = $content -replace ',"assets/', ',"./assets/'
    $content | Set-Content -Path $_.FullName -NoNewline
}
Write-Host "Fixed provider JS files"

Write-Host "All files fixed!"
