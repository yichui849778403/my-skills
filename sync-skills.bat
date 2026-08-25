@echo off
setlocal
REM ============================================================
REM  One-click sync: local custom skills -> GitHub
REM  Usage: double-click this file (needs network)
REM ============================================================
set "REPO=C:\Users\84977\WorkBuddy\my-skills-sync"
set "SRC=C:\Users\84977\.workbuddy\skills"
set SKILLS=app-pentest data-classification-risk-assessment dongjian pentest-report ppt-notes-polish retest-report

cd /d "%REPO%" || (echo [error] clone dir missing: %REPO% & pause & exit /b 1)

git pull --ff-only 2>nul
if errorlevel 1 echo [warn] pull failed or not needed, continue

for %%s in (%SKILLS%) do (
  if exist "%SRC%\%%s\SKILL.md" (
    copy /Y "%SRC%\%%s\SKILL.md" "%%s\SKILL.md" >nul && echo [ok] copied %%s
  ) else (
    echo [skip] local missing: %%s
  )
)

git add -A
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "sync skills: update to local latest"
  git push origin main
  if errorlevel 1 (echo [error] push failed, check network & pause & exit /b 1) else (echo [done] pushed)
) else (
  echo no content change, skip commit/push
)
endlocal
