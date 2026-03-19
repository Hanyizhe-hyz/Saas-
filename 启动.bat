@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo ======================================
echo        灵径智链 Streamlit 启动中
echo ======================================

after_exists:
if not exist "lingjing_platform.py" (
    echo [错误] 未找到 lingjing_platform.py
    pause
    exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PY_CMD=python"
    ) else (
        echo [错误] 未检测到 Python，请先安装 Python 3.10+
        pause
        exit /b 1
    )
)

echo [1/3] 检查 Streamlit...
%PY_CMD% -c "import streamlit" >nul 2>nul
if errorlevel 1 (
    echo [2/3] 正在安装依赖，请稍候...
    if exist "requirements_lingjing.txt" (
        %PY_CMD% -m pip install -r requirements_lingjing.txt
    ) else (
        %PY_CMD% -m pip install streamlit pandas plotly openpyxl python-docx
    )
)

echo [3/3] 启动应用...
start "灵径智链" http://localhost:8501
%PY_CMD% -m streamlit run lingjing_platform.py --server.port 8501

pause
