import os
import sys

# We use the Pandas library, which in turn uses the XLRD library, to read Excel data.
import xlrd
import pandas

args = {}
requiredArgs = ["input","output"]
optionalArgs = []
args["input"] = "."

# Process the command-line arguments.
currentArgName = None
for argItem in sys.argv[1:]:
    if argItem.startswith("--"):
        currentArgName = argItem[2:]
    elif not currentArgName == None:
        args[currentArgName] = argItem
        print(currentArgName + ": " + argItem)
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
            print(argsDataValues[0] + ": " + args[argsDataValues[0]])
            
for requiredArg in requiredArgs:
    if not requiredArg in args.keys():
        print("ERROR: Missing value for argument " + requiredArg)
        print("Usage: scanFolders --config --input --output")
        sys.exit(1)
