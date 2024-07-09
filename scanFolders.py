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

matches = docsToMarkdownLib.readMatchesFile(args["dataRoot"] + os.sep + "matches.csv")
previousChanges = docsToMarkdownLib.readDataFile(args["dataRoot"] + os.sep + "changes.csv")
currentChanges = docsToMarkdownLib.getFolderChangeDetails(docsToMarkdownLib.normalisePath(args["input"]))

print("argv[0]: " + sys.argv[0])
print("ScriptRoot: " + args["scriptRoot"])
print("DataRoot: " + args["dataRoot"])
print(currentChanges)
changedPaths = []
for item in currentChanges:
    if item in previousChanges:
        if not currentChanges[item] == previousChanges[item]:
            changedPaths.append(item)
    else:
        changedPaths.append(item)
print(changedPaths)
docsToMarkdownLib.writeDataFile(args["dataRoot"] + os.sep + "changes.csv", currentChanges)
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
