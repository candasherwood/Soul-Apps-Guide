@echo off
setlocal
title Soul Apps Quick Reference
cd /d "%~dp0"

rem --- find a Python 3 to run the rebuild script ---------------------------
where py >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD (
  where python >nul 2>nul && set "PYCMD=python"
)
if not defined PYCMD (
  if exist "%LOCALAPPDATA%\Python\pythoncore-3.12-64\python.exe" set "PYCMD="%LOCALAPPDATA%\Python\pythoncore-3.12-64\python.exe""
)

if not defined PYCMD (
  echo ERROR: Python 3 was not found on this machine.
  echo Install it from python.org, then run this file again.
  echo.
  pause
  exit /b 1
)

rem --- called with an argument: do one job and exit, no menu --------------
if not "%~1"=="" (
  if /i "%~1"=="check" (
    set "ARGS=--check"
  ) else (
    set "ARGS=%*"
  )
  goto :run_once
)

:menu
echo.
echo  ==========================================================
echo   Soul Apps quick reference
echo  ==========================================================
echo    1  Rebuild the guide PDF and the quick-reference sheet
echo    2  Check that everything is still in step
echo    3  Open the quick-reference sheet - PDF
echo    4  Open the plain-text sheet - TXT
echo    5  Open the full guide - PDF
echo    6  Quit
echo.
set "PICK="
set /p "PICK=Choose 1-6: "
rem --- no input twice in a row means the window has nothing to read -----
if not defined PICK (
  set /a "EMPTY+=1"
) else (
  set "EMPTY=0"
)
if "%EMPTY%"=="2" goto :no_input
if "%PICK%"=="1" goto :rebuild
if "%PICK%"=="2" goto :check_files
if "%PICK%"=="3" goto :open_sheet
if "%PICK%"=="4" goto :open_txt
if "%PICK%"=="5" goto :open_guide
if "%PICK%"=="6" goto :end
echo.
echo That was not one of the options. Choose 1 to 6.
goto :menu

:rebuild
echo.
echo Rebuilding the guide PDF and the quick-reference sheet...
echo.
%PYCMD% "build_quick_reference.py"
if errorlevel 1 goto :rebuild_failed
%PYCMD% "build_guide_pdf.py"
if errorlevel 1 goto :rebuild_failed
echo.
echo Done. Both PDFs are in step with the guide.
echo Choose 3 for the sheet, 5 for the guide.
goto :menu

:rebuild_failed
echo.
echo Something went wrong - see the message above.
goto :menu

:check_files
echo.
echo Checking that everything is still in step...
echo.
%PYCMD% "build_quick_reference.py" --check
if errorlevel 1 goto :check_stale
%PYCMD% "build_guide_pdf.py" --check
if errorlevel 1 goto :check_stale
echo.
echo In step. Nothing to do.
goto :menu

:check_stale
echo.
echo Something is out of date. Choose 1 to rebuild it.
goto :menu

:open_sheet
if not exist "Soul Apps Quick Reference.pdf" goto :sheet_missing
start "" "Soul Apps Quick Reference.pdf"
goto :menu

:sheet_missing
echo.
echo The quick-reference sheet PDF is not in this folder.
echo Choose 1 to build it.
goto :menu

:open_txt
if not exist "Soul Apps Quick Reference.txt" goto :txt_missing
start "" "Soul Apps Quick Reference.txt"
goto :menu

:txt_missing
echo.
echo The plain-text sheet is not in this folder.
echo Choose 1 to build it.
goto :menu

:open_guide
if not exist "Installing the Soul Apps Manually.pdf" goto :guide_missing
start "" "Installing the Soul Apps Manually.pdf"
goto :menu

:guide_missing
echo.
echo The full guide PDF is not in this folder.
goto :menu

:run_once
%PYCMD% "build_quick_reference.py" %ARGS%
if errorlevel 1 goto :run_failed
if /i "%ARGS%"=="--check" (
  %PYCMD% "build_guide_pdf.py" --check
  if errorlevel 1 goto :run_failed
  exit /b 0
)
%PYCMD% "build_guide_pdf.py"
if errorlevel 1 goto :run_failed
exit /b 0

:run_failed
exit /b 1

:no_input
echo.
echo No choice was read, so there is nothing to do. Closing.
exit /b 0

:end
endlocal
exit /b 0
