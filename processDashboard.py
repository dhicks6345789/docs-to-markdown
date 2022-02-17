import os
import sys

# Our own Docs To Markdown library.
import docsToMarkdownLib

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]

print("STATUS: processDashboard: " + inputFolder + " to " + outputFolder)

# Make sure the output folder exists.
os.makedirs(outputFolder, exist_ok=True)

fileNames = {}
for inputItem in os.listdir(inputFolder):
    if os.path.isdir(inputFolder + os.sep + inputItem):
        print("Folder: " + inputItem)
    else:
        fileType = ""
        fileSplit = inputItem.rsplit(".", 1)
        fileName = fileSplit[0]
        if len(fileSplit) == 2:
            fileType = fileSplit[1]
        if not fileName in fileNames.keys():
            fileNames[fileName] = []
        fileNames[fileName].append(fileType)

for fileName in sorted(fileNames.keys()):
    if fileName.lower() == "config":
        for fileType in fileNames["config"]:
            fullName = fileName + "." + fileType
            if fileType.lower() in ["xls", "xlsx", "csv"]:
                print("Config: " + fullName)

for fileName in sorted(fileNames.keys()):
    for fileType in fileNames[fileName]:
        fullName = fileName + "." + fileType
        if fileType.lower() in ["url"]:
            print("URL: " + fullName)
