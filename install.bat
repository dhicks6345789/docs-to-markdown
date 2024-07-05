@echo off
echo Installing DocsToMarkdown as a Windows service...

rem Stop any existing running service.
net stop DocsToMarkdown > nul 2>&1

NSSM\2.24\win64\nssm install DocsToMarkdown "C:\Program Files\WebConsole\webconsole.exe" > nul 2>&1
NSSM\2.24\win64\nssm set DocsToMarkdown DisplayName "Docs To Markdown" > nul 2>&1
NSSM\2.24\win64\nssm set DocsToMarkdown AppNoConsole 1 > nul 2>&1
NSSM\2.24\win64\nssm set DocsToMarkdown Start SERVICE_AUTO_START > nul 2>&1
net start DocsToMarkdown
