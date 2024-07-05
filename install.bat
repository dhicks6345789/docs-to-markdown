@echo off
echo Installing DocsToMarkdown as a Windows service...

rem Parse any parameters.
if "%1"=="" (
  echo Installs DocsToMarkdown as a Windows periodic task.
  echo Usage: install PathToDocsToMarkdownExecutable
  goto end
)
set docsToMarkdownPath=%1

schtasks /query /tn DocsToMarkdown

rem rem Stop any existing running service.
rem net stop DocsToMarkdown > nul 2>&1

rem NSSM\2.24\win64\nssm install DocsToMarkdown "C:\Program Files\WebConsole\webconsole.exe" > nul 2>&1
rem NSSM\2.24\win64\nssm set DocsToMarkdown DisplayName "Docs To Markdown" > nul 2>&1
rem NSSM\2.24\win64\nssm set DocsToMarkdown AppNoConsole 1 > nul 2>&1
rem NSSM\2.24\win64\nssm set DocsToMarkdown Start SERVICE_AUTO_START > nul 2>&1
rem net start DocsToMarkdown

:end
