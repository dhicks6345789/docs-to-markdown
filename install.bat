@echo off
echo Installing DocsToMarkdown as a Webconsole / Windows Schedualed Task...

rem Parse any parameters.
if [%1]==[] (
  echo Installs DocsToMarkdown as a Windows periodic task.
  echo Usage: install PathToDocsToMarkdownExecutable
  goto end
)
set docsToMarkdownPath=%1

schtasks /query /tn DocsToMarkdown 2>&1 | find /i "ERROR: The system cannot find the file specified." >NUL
if not errorlevel 1 (
  echo DocsToMarkdown Task not present.
)

:end
