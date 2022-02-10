import os

args = {}
args["input"] = "."
args["output"] = ""

# When we examine a Word document, if it starts with what looks like YAML-style variables then we will treat that as Hugo / Jeykll
# front matter values. We only check for the variables as given below, otherwise every document that starts with a colon in the
# first line would get treated as front matter.
args["validFrontMatterFields"] = ["title","lastUpdated"]
#args["defaultFrontMatter"] = {"layout":"default"}

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
        elif argsDataValues[0] in optionalLists:
            for argsDataValue in argsDataValues[1:].values:
                if not isnan(argsDataValue):
                    args[argsDataValues[0]].append(argsDataValue)
        elif argsDataValues[0] in functionArgs.keys():
            userFunction = {}
            userFunction["function"] = argsDataValues[0]
            functionArgIndex = 1
            for functionArg in functionArgs[argsDataValues[0]]:
                userFunction[functionArg] = argsDataValues[functionArgIndex]
                functionArgIndex = functionArgIndex + 1
            userFunctions.append(userFunction)
