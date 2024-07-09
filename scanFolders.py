import os
import re
import sys

# We use the Pandas library, which in turn uses the XLRD library, to read Excel data.
#import xlrd
#import pandas

# Our own Docs To Markdown library.
import docsToMarkdownLib



args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"scriptRoot":sys.argv[0].rsplit(os.sep, 1)[0], "dataRoot":"", "verbose":"false", "produceFolderIndexes":"false", "validFrontMatterFields":""}, requiredArgs=["input","output"], optionalArgs=["scriptRoot", "verbose", "data", "produceFolderIndexes", "baseURL", "validFrontMatterFields"])
args["dataRoot"] = docsToMarkdownLib.normalisePath(args["dataRoot"])
args["verbose"] = args["verbose"].lower()
args["produceFolderIndexes"] = args["produceFolderIndexes"].lower()
args["validFrontMatterFields"] = args["validFrontMatterFields"].split(",")

# Print a config summary for the user.
print("DocsToMarkdown - arguments:", flush=True)
for arg in args:
    print(" - " + arg + ": " + str(args[arg]), flush=True)

matches = docsToMarkdownLib.readDataFile(args["dataRoot"] + os.sep + "matches.csv")
#print("matches:")
#print(matches)
scriptStrings = []
for item in matches:
    if not matches[item][1] in scriptStrings:
        scriptStrings.append(matches[item][1])
#print("scriptStrings:")
#print(scriptStrings)

previousMatchChanges = docsToMarkdownLib.readDataFile(args["dataRoot"] + os.sep + "matchChanges.csv")
#print("previousMatchChanges")
#print(previousMatchChanges)
currentMatchChanges = docsToMarkdownLib.getFolderChangeDetails(".")
#print("currentMatchChanges")
#print(currentMatchChanges)
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

exit(0)



def scanFolder(theInput, theOutput):
    inputFolder = docsToMarkdownLib.normalisePath(args["input"] + os.sep + theInput)
    print("DocsToMarkdown - scanning folder: " + inputFolder, flush=True)
    unmatchedItems = []
    for item in os.listdir(inputFolder):
        matched = False
        for match in matches:
            if item.endswith(match[0]):
                matched = True
                inputItem = inputFolder + os.sep + item
                outputItem = docsToMarkdownLib.normalisePath(args["output"] + os.sep + theOutput + os.sep + item)
                if os.path.isfile(inputItem):
                    outputItem = outputItem.rsplit(os.sep, 1)[0]
                commandLine = match[1] + " \"" + docsToMarkdownLib.normalisePath(args["scriptRoot"] + os.sep + match[2]) + "\" \"" + inputItem + "\" \"" + outputItem + "\""
                if args["verbose"] == "true":
                    print("DocsToMarkdown - running: " + commandLine, flush=True)
                os.system(commandLine + " 2>&1")
        if matched == False:
            unmatchedItems.append(item)
    for item in unmatchedItems:
        if os.path.isdir(inputFolder + os.sep + item):
            scanFolder(docsToMarkdownLib.normalisePath(theInput + os.sep + item), docsToMarkdownLib.normalisePath(theOutput + os.sep + item))
        #else:
            #inputItem = inputFolder + os.sep + item
            #outputItem = docsToMarkdownLib.normalisePath(args["output"] + os.sep + theOutput + os.sep + item)
            #print("DocsToMarkdown - copying file: " + inputItem + " to " + outputItem, flush=True)
            #shutil.copyfile(inputItem, outputItem)

scanFolder("", "")
