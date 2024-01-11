import os
import re
import sys

# We use the Pandas library, which in turn uses the XLRD library, to read Excel data.
import xlrd
import pandas

# Our own Docs To Markdown library.
import docsToMarkdownLib



args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"scriptRoot":sys.argv[0].rsplit(os.sep, 1)[0], "verbose":"false"}, requiredArgs=["input","output"], optionalArgs=["scriptRoot", "verbose"])
args["verbose"] = args["verbose"].lower()

# Print a config summary for the user.
for arg in args:
    print(arg + ": " + args[arg])            

matches = []
matches.append([".docx", "python3", "processDOCFile.py"])
matches.append(["faq", "python3", "FAQ/processFAQ.py"])

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

scanFolder("", "")
