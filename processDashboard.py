import os
import sys

# Our own Docs To Markdown library.
import docsToMarkdownLib

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]

print("STATUS: processDashboard: " + inputFolder + " to " + outputFolder)

# Make sure the output folder exists.
os.makedirs(outputFolder, exist_ok=True)

sections = []
def listFileNames(theInputFolder):
    global sections
    
    fileNames = {}
    for inputItem in sorted(os.listdir(theInputFolder)):
        if os.path.isdir(theInputFolder + os.sep + inputItem):
            if not fileNames == {}:
                sections.append((theInputFolder, fileNames))
            fileNames = {}
            listFileNames(theInputFolder + os.sep + inputItem)
        else:
            fileType = ""
            fileSplit = inputItem.rsplit(".", 1)
            fileName = fileSplit[0]
            if len(fileSplit) == 2:
                fileType = fileSplit[1]
            if not fileName in fileNames.keys():
                fileNames[fileName] = []
            fileNames[fileName].append(fileType)
    if not fileNames == {}:
        sections.append((theInputFolder, fileNames))

listFileNames(inputFolder)

for section in sections:
    for fileName in sorted(section[1].keys()):
        if fileName.lower() == "config":
            for fileType in section[1].pop("config"):
                fullPath = section[0] + os.sep + fileName + "." + fileType
                if fileType.lower() in ["xls", "xlsx", "csv"]:
                    print("Config: " + fullPath)

rowX = 1
rowHeight = 1
rowItems = []
HTMLString = "<div>\n"
def newRow():
    global rowX
    global rowHeight
    global rowItems
    global HTMLString
    
    if not rowItems == []:
        for item in rowItems:
            HTMLString = HTMLString + "\t\t" + item + "\n"
    rowX = 1
    rowHeight = 1
    rowItems = []

for section in sections:
    if not section[1] == {}:
        HTMLString = HTMLString + "\t<div>\n"
        print(section[0])
        print(section[1])
        for fileName in section[1].keys():
            for fileType in section[1][fileName]:
                fullPath = section[0] + os.sep + fileName + "." + fileType
                fileName = fileName.lower()
                fileNameSplit = fileName.split(" ", 1)
                if fileNameSplit[0].isnumeric() and len(fileNameSplit) == 2:
                    fileName = fileNameSplit[1]
                fileType = fileType.lower()
                if fileType in ["url"]:
                    width = 1
                    height = 1
                    if rowX + width > 12:
                        newRow()
                    rowX = rowX + width
                    if height > rowHeight:
                        rowHeight = height
                    rowItems.append(fileName)
        newRow()
        HTMLString = HTMLString + "\t</div>\n"
HTMLString = HTMLString + "</div>\n"
docsToMarkdownLib.putFile(outputFolder + os.sep + "index.html", HTMLString)
