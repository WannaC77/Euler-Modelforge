@echo off
rem ============================================================
rem  Math-modeling LaTeX template smoke test (pre-competition)
rem  Compiles BOTH templates end-to-end and asserts the PDFs.
rem  Usage: double-click, or run from cmd.  Exit 0 = both PASS.
rem  NOTE: ASCII-only on purpose (cmd.exe mangles non-ANSI batch
rem  content); template dirs are found by wildcard instead.
rem ============================================================
setlocal enableextensions enabledelayedexpansion
set "ROOT=%~dp0"
set "TLBIN=<TeX 安装目录>/"
set "MKBIN=%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64"
set "FAIL=0"
set "SKIPPED=0"

if exist "%TLBIN%\xelatex.exe" (
  set "TEXBIN=%TLBIN%"
  set "ENGINE=TeX Live 2026"
) else if exist "%MKBIN%\xelatex.exe" (
  set "TEXBIN=%MKBIN%"
  set "ENGINE=MiKTeX (fallback)"
) else (
  echo [FATAL] No TeX engine found ^(looked for TeX Live and MiKTeX^).
  echo         Install TeX Live, or point MiKTeX at a CTAN mirror.
  exit /b 2
)
set "PATH=%TEXBIN%;%PATH%"

set "GSDIR="
set "MSDIR="
for /d %%D in ("%ROOT%*-CUMCM") do set "GSDIR=%%~fD"
for /d %%D in ("%ROOT%*-MCM-ICM") do set "MSDIR=%%~fD"

echo ============================================
echo  Engine : %ENGINE%
echo  Bin    : %TEXBIN%
echo  CUMCM  : %GSDIR%
echo  MCM/ICM: %MSDIR%
echo ============================================

rem ---------- CUMCM (Chinese, XeLaTeX required) ----------
echo.
echo [1/2] CUMCM template  (xelatex, 2 passes) ...
if not defined GSDIR (echo   [SKIP] CUMCM template dir not present & set "SKIPPED=1" & goto :meisai)
if not exist "%GSDIR%\example.tex" (echo   [SKIP] CUMCM template not bundled - see README in the CUMCM template dir & set "SKIPPED=1" & goto :meisai)
cd /d "%GSDIR%"
del /q example.pdf 2>nul
xelatex -interaction=nonstopmode example.tex >nul 2>&1
xelatex -interaction=nonstopmode example.tex >nul 2>&1
if not exist example.pdf (echo   [FAIL] example.pdf not produced & set "FAIL=1" & goto :meisai)
findstr /C:"Output written on" example.log >nul 2>&1
if errorlevel 1 (echo   [FAIL] log has no "Output written on" - compile did not finish & set "FAIL=1" & goto :meisai)
findstr /C:"Fatal error" example.log >nul 2>&1
if not errorlevel 1 (echo   [FAIL] log reports Fatal error & set "FAIL=1" & goto :meisai)
for %%A in (example.pdf) do echo   [PASS] example.pdf  %%~zA bytes

:meisai
rem ---------- MCM/ICM (English, pdfLaTeX) ----------
echo.
echo [2/2] MCM/ICM template  (pdflatex, 2 passes) ...
if not defined MSDIR (echo   [SKIP] MCM/ICM template dir not present & set "SKIPPED=1" & goto :summary)
if not exist "%MSDIR%\mcmthesis-template.tex" (echo   [SKIP] MCM/ICM template file not found & set "SKIPPED=1" & goto :summary)
cd /d "%MSDIR%"
del /q mcmthesis-template.pdf 2>nul
pdflatex -interaction=nonstopmode mcmthesis-template.tex >nul 2>&1
pdflatex -interaction=nonstopmode mcmthesis-template.tex >nul 2>&1
if not exist mcmthesis-template.pdf (echo   [FAIL] mcmthesis-template.pdf not produced & set "FAIL=1" & goto :summary)
findstr /C:"Output written on" mcmthesis-template.log >nul 2>&1
if errorlevel 1 (echo   [FAIL] log has no "Output written on" - compile did not finish & set "FAIL=1" & goto :summary)
findstr /C:"Fatal error" mcmthesis-template.log >nul 2>&1
if not errorlevel 1 (echo   [FAIL] log reports Fatal error & set "FAIL=1" & goto :summary)
for %%A in (mcmthesis-template.pdf) do echo   [PASS] mcmthesis-template.pdf  %%~zA bytes

:summary
echo.
if not "%SKIPPED%"=="0" echo NOTE: one or more templates were SKIPPED ^(not bundled / not found^) - see lines above.
if "%FAIL%"=="0" (
  echo ============ ALL AVAILABLE TEMPLATES PASS ============
  exit /b 0
) else (
  echo ============ SMOKE TEST FAILED ============
  exit /b 1
)
