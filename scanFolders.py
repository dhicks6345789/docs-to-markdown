import os
import re
import sys

# We use the Pandas library, which in turn uses the XLRD library, to read Excel data.
import xlrd
import pandas

# Our own Docs To Markdown library.
import docsToMarkdownLib

args = {}
requiredArgs = ["input","output"]
optionalArgs = ["scriptRoot"]
args["input"] = os.getcwd()
args["scriptRoot"] = sys.argv[0].rsplit(os.sep, 1)[0]

matches = []
matches.append([".docx", "python3", "processDOCXFile.py"])
matches.append(["faq", "python3", "FAQ/processFAQ.py"])

def scanFolder(theInput, theOutput):
    inputFolder = docsToMarkdownLib.normalisePath(baseInput + os.sep + theInput)
    print("Scanning folder: " + inputFolder, flush=True)
    unmatchedItems = []
    for item in os.listdir(inputFolder):
        matched = False
        for match in matches:
            if item.endswith(match[0]):
                matched = True
                commandLine = match[1] + " " + docsToMarkdownLib.normalisePath(args["scriptRoot"] + os.sep + match[2]) + " " + inputFolder + os.sep + item + " " + docsToMarkdownLib.normalisePath(baseOutput + os.sep + theOutput + os.sep + item)
                print("Running: " + commandLine, flush=True)
                os.system(commandLine + " 2>&1")
        if matched == False:
            unmatchedItems.append(item)
    for item in unmatchedItems:
        if os.path.isdir(inputFolder + os.sep + item):
            scanFolder(docsToMarkdownLib.normalisePath(theInput + os.sep + item), docsToMarkdownLib.normalisePath(theOutput + os.sep + item))

# Process the command-line arguments.
currentArgName = None
for argItem in sys.argv[1:]:
    if argItem.startswith("--"):
        currentArgName = argItem[2:]
    elif not currentArgName == None:
        args[currentArgName] = argItem
        currentArgName = None
    else:
        print("ERROR: unknown argument, " + argItem)
        sys.exit(1)

if "config" in args.keys():
    if args["config"].endswith(".csv"):
        argsData = pandas.read_csv(args["config"], header=0)
    else:
        argsData = pandas.read_excel(args["config"], header=0)
    for argsDataIndex, argsDataValues in argsData.iterrows():
        if argsDataValues[0] in requiredArgs + optionalArgs:
            args[argsDataValues[0]] = str(argsDataValues[1])

# Print a config summary for the user.
for arg in args:
    print(arg + ": " + args[arg])
            
for requiredArg in requiredArgs:
    if not requiredArg in args.keys():
        print("ERROR: Missing value for argument " + requiredArg)
        print("Usage: scanFolders --config --input --output")
        sys.exit(1)

baseInput = args["input"]
baseOutput = args["output"]
scanFolder("", "")
