import os
import re
import sys
import subprocess

# We use the Pandas library, which in turn uses the XLRD library, to read Excel data.
#import xlrd
#import pandas

# Our own Docs To Markdown library.
import docsToMarkdownLib



args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"scriptRoot":sys.argv[0].rsplit(os.sep, 1)[0], "dataRoot":".", "verbose":"false", "produceFolderIndexes":"false", "validFrontMatterFields":""}, requiredArgs=["input","output"], optionalArgs=["scriptRoot", "verbose", "data", "produceFolderIndexes", "baseURL", "validFrontMatterFields"])
args["dataRoot"] = docsToMarkdownLib.normalisePath(args["dataRoot"])
args["verbose"] = args["verbose"].lower()
args["produceFolderIndexes"] = args["produceFolderIndexes"].lower()
args["validFrontMatterFields"] = args["validFrontMatterFields"].split(",")

# Print a config summary for the user.
print("DocsToMarkdown - arguments:", flush=True)
for arg in args:
    print(" - " + arg + ": " + str(args[arg]), flush=True)
    
matches = docsToMarkdownLib.readDataFile(args["dataRoot"] + os.sep + "matches.csv")
scriptStrings = []
for item in matches:
    if not matches[item][1] in scriptStrings:
        scriptStrings.append(matches[item][1])

previousMatchChanges = docsToMarkdownLib.readDataFile(args["dataRoot"] + os.sep + "matchChanges.csv")
currentMatchChanges = docsToMarkdownLib.getFolderChangeDetails(".")
changedMatchPaths = []
for item in currentMatchChanges:
    if item in previousMatchChanges:
        if not currentMatchChanges[item] == previousMatchChanges[item]:
            if item in scriptStrings:
                changedMatchPaths.append(item)
    else:
        if item in scriptStrings:
            changedMatchPaths.append(item)
print("changedMatchPaths:")
print(changedMatchPaths)
docsToMarkdownLib.writeDataFile(args["dataRoot"] + os.sep + "matchChanges.csv", currentMatchChanges)

previousInputChanges = docsToMarkdownLib.readDataFile(args["dataRoot"] + os.sep + "inputChanges.csv")
currentInputChanges = docsToMarkdownLib.getFolderChangeDetails(docsToMarkdownLib.normalisePath(args["input"]))
changedInputPaths = []
for item in currentInputChanges:
    if item in previousInputChanges:
        if not currentInputChanges[item] == previousInputChanges[item]:
            changedInputPaths.append(item)
    else:
        changedInputPaths.append(item)
print("changedInputPaths:")
print(changedInputPaths)
docsToMarkdownLib.writeDataFile(args["dataRoot"] + os.sep + "inputChanges.csv", currentInputChanges)



def scanFolder(theInput, theOutput):
    inputFolder = docsToMarkdownLib.normalisePath(args["input"] + "/" + theInput)
    print("DocsToMarkdown - scanning folder: " + inputFolder, flush=True)
    unmatchedItems = []

    items = os.listdir(inputFolder)
    items.insert(0, "")
    folderMatched = False
    for item in items:
        matched = False
        for match in matches:
            inputItem = inputFolder + "/" + item
            if (matched == False) and (folderMatched == False) and (not re.match(match, inputItem) == None):
                matched = True
                if item == "":
                    folderMatched = True
                outputItem = docsToMarkdownLib.normalisePath(args["output"] + "/" + theOutput + "/" + item)
                if os.path.isfile(docsToMarkdownLib.platformPath(inputItem)):
                    outputItem = outputItem.rsplit("/", 1)[0]
                commandLine = [docsToMarkdownLib.platformPath(matches[match][0]), docsToMarkdownLib.platformPath(args["scriptRoot"] + "/" + matches[match][1]), docsToMarkdownLib.platformPath(inputItem), docsToMarkdownLib.platformPath(outputItem)]
                if args["verbose"] == "true":
                    print("DocsToMarkdown - matched: " + inputItem + " with " + match, flush=True)
                    print("DocsToMarkdown - running: " + " ".join(commandLine), flush=True)
                subprocess.run(commandLine)
        if (matched == False) and (folderMatched == False) and (not item == ""):
            unmatchedItems.append(item)
    for item in unmatchedItems:
        if os.path.isdir(inputFolder + os.sep + item):
            scanFolder(docsToMarkdownLib.normalisePath(theInput + os.sep + item), docsToMarkdownLib.normalisePath(theOutput + os.sep + item))
scanFolder("", "")
