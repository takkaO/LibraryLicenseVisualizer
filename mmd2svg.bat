@echo off

set CURRENT_DIR=%~dp0
set CURRENT_DIR=%CURRENT_DIR:~0,-1%

@rem パス区切りをスラッシュ形式に変換
set A=%~1
set INPUT_PATH=%A:\=/%

@rem mmd -> svg
docker run --rm -v %CURRENT_DIR%:/data ghcr.io/mermaid-js/mermaid-cli/mermaid-cli:11.4.2 -i %INPUT_PATH% -o /data/%INPUT_PATH%.svg --configFile="mermaidRenderConfig.json"

@rem svg のスタイルを調整
set "inputfile=%INPUT_PATH%.svg"
set "oldstring=max-width:"
set "newstring=height:auto; max-width:"
powershell -Command "$content = Get-Content '%inputfile%' -Encoding UTF8; $content -replace '%oldstring%', '%newstring%' | Set-Content '%inputfile%' -Encoding UTF8"