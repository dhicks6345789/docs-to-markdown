# A script to generate a slideshow (video file) from a folder of source files (images, videos, audio).

# Standard libraries.
import os
import io
import sys

# Our own Docs To Markdown library.
import docsToMarkdownLib

# We use the Pandas library to load in Excel / CSV files for the configuration settings.
import pandas

# An array of "image file" types.
bitmapTypes = ["jpg", "jpeg", "png", "ico"]
imageTypes =  bitmapTypes + ["svg"]

# Get any arguments given via the command line.
args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={}, requiredArgs=["input","output"])

print("STATUS: processSlideshow: " + args["input"] + " to " + args["output"], flush=True)

# Make sure the output folder exists.
os.makedirs(args["output"], exist_ok=True)



# Check through items in the given input folder, recursing into sub-folders.
# Produces an array (in the global "sections" variable) of dicts containing tuples of file names and an array of extensions found.
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
listFileNames(args["input"])

config = []
# Check through the files found above to see if the special "config" file is found anywhere, and if so deal with it and remove it from the list.
for section in sections:
    for fileName in sorted(section[1].keys()):
        if fileName.lower() == "config":
            for fileType in section[1].pop("items"):
                fullPath = section[0] + os.sep + fileName + "." + fileType
                if fileType.lower() in ["xls", "xlsx", "csv"]:
                    print("Config found: " + fullPath, flush=True)

itemsList = []
# Check through the files found above to see if the special "items" file is found anywhere, and if so deal with it and remove it from the list.
for section in sections:
    for fileName in sorted(section[1].keys()):
        if fileName.lower() == "items":
            for fileType in section[1].pop("items"):
                fullPath = section[0] + os.sep + fileName + "." + fileType
                if fileType.lower() in ["xls", "xlsx", "csv"]:
                    print("Items file found: " + fullPath, flush=True)
                    if fileType.lower() in ["xls", "xlsx"]:
                        itemsSheet = pandas.read_excel(fullPath)
                    else:
                        itemsSheet = pandas.read_csv(fullPath)
                    # Convert the Pandas dataframe to an array of dicts, lowercasing all the keys and replacing all "NaN" values with empty string.
                    for itemsIndex, itemsRow in itemsSheet.iterrows():
                        newItem = {}
                        for colName in itemsRow.keys():
                            if pandas.isna(itemsRow[colName]):
                                newItem[colName.lower()] = ""
                            else:
                                newItem[colName.lower()] = itemsRow[colName]
                        itemsList.append(newItem)
