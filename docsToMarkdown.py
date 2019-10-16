#!/usr/bin/python3

# Standard libraries.
import os
import re
import sys
import shutil
import subprocess

# Handle JSON-formatted files.
import json

# DocsToMarkdown: Converts a set of Word / Excel files (compatability with those produced by Mircosoft Office, Office 365,
# Google Docs or, hopefully, pretty much any other tool) to the Govspeak varient of Markdown as specified by GOV.UK. Can also
# convert some data to CSV format. The Markdown output is intended to be used as the input for static site generation tools such
# as Jeykll, Hugo or Hyde, and various options / assumtions exist to ensure the files produced are suitible for those tools.

# This utility depends on the Ruby-based utility Pandoc, version 2.7 or higher, released Monday, 4th March 2019.
# Earlier versions (as generally packaged in Debian's repositories, for instance) have a bug which stops them parsing DOCX files
# created with Office 365.

# To-do: check here for presence of Pandoc.

# Use the Pandas library to read Excel data. Overkill for simply reading an Excel file, but Pandas is installed so we might as well use it.
import pandas

# Pandas requires Numpy, so that will be available.
import numpy

# Parameter values to be set via the command line.
configFile = "config.json"
inputFolder = ""
outputFolder = ""
templateFolder = ""

# When we examine a Word document, if it starts with what looks like YAML-style variables then we will treat that as Jeykll front matter values.
# We only check for the variables as given below, otherwise every document that starts with a colon in the first line would get treated as front matter.
# Can be added to in the user-defined config file by defining the "validFrontMatterFields" value.
validFrontMatterFields = ["title","lastUpdated"]
defaultFrontMatter = {"layout": "default"}

globalValues = {}

# A utility function to return the contents of the given file.
def getFile(theFilename):
    infile = open(theFilename)
    result = infile.read()
    infile.close()
    return(result)
    
# A utility  function to write the contents of the given string to the given file.
def writeFile(theFilename, theContent):
    if os.sep in theFilename:
        parentFolderName = theFilename.rsplit(os.sep, 1)[0]
        if not os.path.exists(parentFolderName):
            os.makedirs(parentFolderName)
    outfile = open(theFilename, "wt", encoding="utf-8")
    outfile.write(theContent)
    outfile.close()
    
# A utility function to return a given path string in normalised format, i.e. without any double os.sep characters.
def normalisePath(thePath):
    return(thePath.replace("//","/"))
    
# A utility function to convert from a floating-point number to a string. Python (or Pandas, anyway) converts blank Excel cells into floats
# with a value of NaN. Converting those to a string results in the string "nan". We just want a blank string.
def floatToString(theFloat):
    if isinstance(theFloat, float):
        if numpy.isnan(theFloat):
            return("")
    return(str(theFloat))

# Given a dict, returns a YAML string, e.g.:
# ---
# variableName: value
# ---
# Includes any values not otherwise set from the defaultFrontMatter dict defined at the start of this script.
def frontMatterToString(theFrontMatter):
    result = "---\n"
    for defaultFrontMatterField in defaultFrontMatter:
        if not defaultFrontMatterField in theFrontMatter.keys():
            theFrontMatter[defaultFrontMatterField] = defaultFrontMatter[defaultFrontMatterField]
    for frontMatterField in theFrontMatter.keys():
        result = result + frontMatterField + ": " + theFrontMatter[frontMatterField] + "\n"
    result = result + "---\n"
    return(result)

# Takes a file path string pointing to a document file (.DOC, .DOCX, .TXT, etc) file, loads that file and coverts the contents to a Markdown / Govspeak string.
# Returns a tuple of a string of the converted data and a dict of any front matter variables specified in the input file.
# To do: handle more file types.
def documentToGovspeak(inputFile):
    baseURL = ""
    if "baseURL" in globalValues.keys():
        baseURL = globalValues["baseURL"]
    markdown = ""
    frontMatter = {}
    
    # As of around Monday, 4th March 2019, Pandoc 2.7 now seems to work correctly for parsing DOCX files produced by Word Online.
    # Debian's Pandoc package is still on version 2.5, so Pandoc needs to be installed via the .deb file provided on their website.
    # This proved to be a simple enough install, no problems.
    print("pandoc --wrap=none -s " + inputFile + " -t gfm -o -")
    pandocProcess = subprocess.Popen("pandoc --wrap=none -s " + inputFile + " -t gfm -o -", shell=True, stdout=subprocess.PIPE)
    for markdownLine in pandocProcess.communicate()[0].decode("utf-8").split("\n"):
        lineIsFrontMatter = False
        for validFrontMatterField in validFrontMatterFields:
            if markdownLine.lower().startswith(validFrontMatterField.lower() + ":"):
                frontMatter[validFrontMatterField] = markdownLine.split(":")[1].strip()
                lineIsFrontMatter = True
        if not lineIsFrontMatter:
            markdown = markdown + markdownLine.replace(baseURL, "") + "\n"
    return(markdown, frontMatter)
    
# Takes an input Excel / CSV file, loads that as a Pandas dataframe and returns a Markdown / Govspeak string.
def spreadsheetToGovspeak(inputFile):
    inputDataFrame = pandas.read_excel(io=inputFile)
    # First, the header row...
    rowString = ""
    for header in inputDataframe.headers:
        rowString = rowString + "| " + header + " "
    result = rowString + "|\n"
    # ...then a simple line to split the headers from the data...
    rowString = ""
    for header in inputDataframe.headers:
        rowString = rowString + "| --- "
    result = result + rowString + "|\n"
    # ...then add in each row of data.
    for index, row in inputDataframe.iterrows():
        rowString = ""
        for header in inputDataframe.headers:
            rowString = rowString + "| " + floatToString(row[header]) + " "
        result = result + rowString + "|\n"
    return(result)

# Removes the given file from the global filesToProcess array, if it's listed in there in the first place.
def removeFromFilesToProcess(theFile):
    theFile = normalisePath(theFile)
    if theFile in filesToProcess:
        filesToProcess.remove(theFile)

# Recursivly check each sub-folder in the given input folder, returning an array of input files with full paths.
def processInputFolder(rootPath, subPath):
    result = []
    for item in os.listdir(rootPath + os.sep + subPath):
        if os.path.isdir(rootPath + os.sep + subPath + os.sep + item):
            result = result + processInputFolder(rootPath, subPath + os.sep + item)
        else:
            result.append((normalisePath(rootPath + os.sep + subPath + os.sep + item)))
    return(result)

# Recursivly check each sub-folder in the given input folder for files still to be processed (as defined by the filesToProcess array, initially constructed by the processInputFolder function above).
def applyDefaults(rootPath, subPath, filesToProcess):
    folderContents = os.listdir(rootPath + os.sep + subPath)
    for item in folderContents:
        if not os.path.isdir(rootPath + os.sep + subPath + os.sep + item):
            fileToProcess = normalisePath(rootPath + os.sep + subPath + os.sep + item)
            if fileToProcess in filesToProcess:
                print("Applying default behaviour to: " + fileToProcess)
                if fileToProcess.lower().endswith(".docx"):
                    (govspeak, frontMatter) = documentToGovspeak(fileToProcess)
                    writeFile(normalisePath(outputFolder + os.sep + subPath + os.sep + item[:-4] + "md"), frontMatterToString(frontMatter) + "\n" + govspeak)
    for item in folderContents:
        if os.path.isdir(rootPath + os.sep + subPath + os.sep + item):
            applyDefaults(rootPath, subPath + os.sep + item, filesToProcess)
            
# Copy each file from srcFolder to destFolder, and recurse down sub-folders.
# Removes each encountered file from the filesToProcess list as it goes.
def copyFolder(srcFolder, destFolder):
    os.makedirs(destFolder, exist_ok=True)
    for item in os.listdir(srcFolder):
        if os.path.isdir(srcFolder + os.sep + item):
            copyFolder(srcFolder + os.sep + item, destFolder + os.sep + item)
        else:
            # Skip copying if the file already exists and is up-to-date.
            copyFile = True
            if os.path.exists(destFolder + os.sep + item):
                if os.stat(srcFolder + os.sep + item).st_mtime == os.stat(destFolder + os.sep + item).st_mtime:
                    copyFile = False
            if copyFile:
                shutil.copyfile(srcFolder + os.sep + item, destFolder + os.sep + item)
                shutil.copystat(srcFolder + os.sep + item, destFolder + os.sep + item)
            removeFromFilesToProcess(srcFolder + os.sep + item)
            
# Make sure any files or sub-folders not in srcFolder are removed from destFolder.
def matchFolder(srcFolder, destFolder):
    for item in os.listdir(destFolder):
        if not os.path.exists(srcFolder + os.sep + item):
            if os.path.isdir(destFolder + os.sep + item):
                shutil.rmtree(destFolder + os.sep + item)
            else:
                os.remove(destFolder + os.sep + item)
        else:
            if os.path.isdir(destFolder + os.sep + item):
                matchFolder(srcFolder + os.sep + item, destFolder + os.sep + item)
                
# Takes a chunk of Govspeak Markdown text as input, returns that text with any ordered lists converted to legislative lists,
# i.e. lists where numbering is explicitly specified, not restarted from scratch as is the Kramdown / Govspeak default.
def makeLegislativeLists(theGovspeak):
    result = ""
    for theGovspeakLine in theGovspeak.split("\n"):
        result = result + re.sub(r'^(\d*)\. >', r'{:start="\1"}\n\1. >', theGovspeakLine, count=1) + "\n"
    return(result)

def normaliseGovspeak(theGovspeak):
    result = ""
    previousLineWasBlank = True
    for theGovspeakLine in theGovspeak.split("\n"):
        theGovspeakLine = theGovspeakLine.rstrip()
        if theGovspeakLine == "":
            if not previousLineWasBlank:
                result = result + "\n"
            previousLineWasBlank = True
        else:
            result = result + theGovspeakLine + "\n"
            previousLineWasBlank = False
    return(result.rstrip())
                
# Main script execution begins here. Start by processing the command-line arguments.
argNum = 1
while argNum < len(sys.argv):
    if sys.argv[argNum] == "-i":
        argNum = argNum + 1
        inputFolder = sys.argv[argNum]
    elif sys.argv[argNum] == "-o":
        argNum = argNum + 1
        outputFolder = sys.argv[argNum]
    elif sys.argv[argNum] == "-c":
        argNum = argNum + 1
        configFile = sys.argv[argNum]
    elif sys.argv[argNum] == "-t":
        argNum = argNum + 1
        templateFolder = sys.argv[argNum]
    argNum = argNum + 1
if inputFolder == "" or outputFolder == "":
    print("docsToMarkdown. Usage:")
    print("docsToMarkdown -c -o -i -t")
    sys.exit(0)
    
# A quick output message for the user.
print("Config file: " + configFile)
print("Input folder: " + inputFolder)
print("Output folder: " + outputFolder)
print("Template folder: " + templateFolder)
sys.stdout.flush()

# Make sure the defined output folder exists...
os.makedirs(outputFolder, exist_ok=True)
# ...then copy any template files to the output folder.
if not templateFolder == "":
    os.system("cp -r " + templateFolder + "/* " + outputFolder)

# Get a list of all the input files to process.
filesToProcess = processInputFolder(inputFolder, "")
print("Files to process - start:")
print(filesToProcess)
print("---")

# Load and step through the user-provided configuration, removing any files referenced by a function from the to-be-processed list.
config = json.loads(getFile(configFile))
for configItem in config:
    if "global" in configItem.keys():
        if configItem["global"] == "validFrontMatterFields":
            for validFrontMatterField in configItem["value"]:
                validFrontMatterFields.append(validFrontMatterField)
        else:
            globalValues[configItem["global"]] = configItem["value"]
    if "function" in configItem.keys():
        # Recursivly copy a folder's contents from src to dest.
        if configItem["function"] == "copyFolder":
            copyFolder(normalisePath(inputFolder + os.sep + configItem["src"]), normalisePath(outputFolder + os.sep + configItem["dest"]))
            matchFolder(normalisePath(inputFolder + os.sep + configItem["src"]), normalisePath(outputFolder + os.sep + configItem["dest"]))
        # Reads a list of files, of any supported type, and outputs CSV to the given output, with files concatenated together in the given order.
        # If the "jekyllHeaders" option is set to "true", then this function assumes the first row of Excel files are column headings, and the CSV file
        # written will have any spaces in column headings removed to make a valid variable name in Jekyll.
        if configItem["function"] == "filesToCSV":
            outputCSVData = ""
            subRootPath = ""
            if "rootPath" in configItem.keys():
                subRootPath = configItem["rootPath"]
            for inputFile in configItem["inputFiles"]:
                inputFile = normalisePath(inputFolder + os.sep + subRootPath + os.sep + inputFile)
                inputData = pandas.read_excel(io=inputFile)
                if "jekyllHeaders" in configItem.keys() and configItem["jekyllHeaders"].lower() == "true":
                    newColumns = []
                    for columnName in inputData.columns:
                        newColumns.append(columnName.replace(" ", ""))
                    inputData.columns = newColumns
                outputCSVData = outputCSVData + inputData.to_csv() + "\n"
                removeFromFilesToProcess(inputFile)
            writeFile(normalisePath(outputFolder + os.sep + configItem["outputFile"]), outputCSVData.rstrip())
        # Reads a list of files, of any supported type, and outputs (Govspeak) Markdown to the given output, with files concatenated together in the given order.
        # Any front matter defined in any of the input files will be written to the output file, with any front matter defined in the function itself taking precedence.
        if configItem["function"] == "filesToMarkdown":
            outputGovspeak = ""
            outputFrontMatter = {}
            subRootPath = ""
            if "rootPath" in configItem.keys():
                subRootPath = configItem["rootPath"]
            for inputFileMatch in configItem["inputFiles"]:
                inputFileMatch = normalisePath(inputFolder + os.sep + subRootPath + os.sep + inputFileMatch)
                matchedFiles = []
                for inputFile in filesToProcess:
                    if not re.search(inputFileMatch, inputFile) == None:
                        matchedFiles.append(inputFile)
                for inputFile in matchedFiles:
                    if inputFile.lower().endswith(".docx"):
                        (fileGovspeak, fileFrontMatter) = documentToGovspeak(inputFile)
                        outputGovspeak = outputGovspeak + fileGovspeak + "\n\n"
                        for frontMatterItem in fileFrontMatter.keys():
                            outputFrontMatter[frontMatterItem] = fileFrontMatter[frontMatterItem]
                    elif inputFile.lower().endswith(".xlsx"):
                        outputGovspeak = outputGovspeak + spreadsheetToGovspeak(inputFile) + "\n\n"
                for inputFile in matchedFiles:
                    removeFromFilesToProcess(inputFile)
            if "frontMatter" in configItem.keys():
                for frontMatterItem in configItem["frontMatter"].keys():
                    outputFrontMatter[frontMatterItem] = configItem["frontMatter"][frontMatterItem]
            if "produceLegislativeLists" in configItem.keys():
                if configItem["produceLegislativeLists"] == "true":
                    outputGovspeak = makeLegislativeLists(outputGovspeak)
            outputGovspeak = normaliseGovspeak(outputGovspeak)
            writeFile(normalisePath(outputFolder + os.sep + configItem["outputFile"]), frontMatterToString(outputFrontMatter) + "\n" + outputGovspeak.rstrip())

print("Files to process - end:")
print(filesToProcess)
print("---")

# After going through the user-defined config, apply default behaviours to any files still left to be processed.
applyDefaults(inputFolder, "", filesToProcess)
