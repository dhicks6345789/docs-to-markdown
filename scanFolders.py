import os
import re
import sys

# We use the Pandas library, which in turn uses the XLRD library, to read Excel data.
import xlrd
import pandas

args = {}
requiredArgs = ["input","output"]
optionalArgs = []
args["input"] = os.getcwd()

matches = []
matches.append(["/faq/.*", "python3 processFAQ.py"])

def normalisePath(thePath):
    result = thePath.replace(os.sep+os.sep, os.sep)
    if result[len(result)-1] == os.sep:
        result = result[:-1]
    return result

def scanFolder(theInput, theOutput):
    inputFolder = normalisePath(baseInput + os.sep + theInput)
    for item in os.listdir(inputFolder):
        if os.path.isdir(inputFolder + os.sep + item):
            for match in matches:
                if not re.match(match[0], theInput + os.sep + item + os.sep) == None:
                    commandLine = match[1] + " " + inputFolder + os.sep + item + " " + normalisePath(baseOutput + os.sep + theOutput + os.sep + item)
                    print("Running: " + commandLine)
                    os.system(commandLine)
    for item in os.listdir(inputFolder):
        if os.path.isdir(inputFolder + os.sep + item):
            scanFolder(normalisePath(theInput + os.sep + item), normalisePath(theOutput + os.sep + item))

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
            args[argsDataValues[0]] = valueToString(argsDataValues[1])

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
