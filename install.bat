@echo off
echo Installing DocsToMarkdown as a Wi ndows service...

rem Stop any existing running services.
net stop DocsToMarkdown > nul 2>&1

echo Setting up WebConsole as a Windows service...
NSSM\2.24\win64\nssm install WebConsole "C:\Program Files\WebConsole\webconsole.exe" > nul 2>&1
NSSM\2.24\win64\nssm set WebConsole DisplayName "Web Console" > nul 2>&1
NSSM\2.24\win64\nssm set WebConsole AppNoConsole 1 > nul 2>&1
NSSM\2.24\win64\nssm set WebConsole Start SERVICE_AUTO_START > nul 2>&1
net start DocsToMarkdown
