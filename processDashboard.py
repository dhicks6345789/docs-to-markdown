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

gridX = 1
gridY = 1
for fileName in sorted(fileNames.keys()):
    for fileType in fileNames[fileName]:
        fullName = fileName + "." + fileType
        fileName = fileName.lower()
        fileNameSplit = fileName.split(" ", 1)
        if fileNameSplit[0].isnumeric() and len(fileNameSplit) == 2:
            fileName = fileNameSplit[1]
        fileType = fileType.lower()
        if os.path.isdir(inputFolder + os.sep + fullName):
            print("Folder: " + fullName)
        else:
            if fileType in ["url"]:
                print("URL: " + fullName)
                print("Config var: " + fileName)
                width = 1
                height = 1
                gridX = gridX + width
