# A script to generate a slideshow (a folder containing index.html and a set of normalised assets) from a folder of assets (images, videos, audio).

# Standard libraries.
import os
import io
import sys
import shutil

# Our own Docs To Markdown library.
import docsToMarkdownLib

# Get any arguments given via the command line.
args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={}, requiredArgs=["input","output"])

print("STATUS: processSlideshow: " + args["input"] + " to " + args["output"], flush=True)

# Make sure the output folder exists.
os.makedirs(args["output"], exist_ok=True)



def normalisePath(thePath):
    result = thePath.replace(os.sep + os.sep, os.sep)
    if result.endswith(os.sep):
        result = result[:-1]
    return result

# Check through items in the given input folder, recursing into sub-folders.
# Produces an array (in the global "slides" variable) containing tuples of file names and an array of extensions found.
slides = {}
inputFolder = normalisePath(args["input"])
def listFileNames(theSubFolder):
    global inputFolder
    global slides
    
    inputPath = inputFolder + os.sep + theSubFolder
    for inputItem in sorted(os.listdir(inputPath)):
        if os.path.isdir(normalisePath(inputPath + os.sep + inputItem)):
            listFileNames(normalisePath(theSubFolder + os.sep + inputItem))
        else:
            fileType = ""
            fileSplit = inputItem.rsplit(".", 1)
            fileName = fileSplit[0]
            if not theSubFolder == "":
                fileName = theSubFolder + os.sep + fileName
            if len(fileSplit) == 2:
                fileType = fileSplit[1]
            if not fileName in slides.keys():
                slides[fileName] = []
            slides[fileName].append(fileType)
listFileNames("")
print(slides)

config = []
# Check through the files found above to see if the special "config" file is found anywhere, and if so deal with it and remove it from the list.
for slide in slides:
    if slide.lower() == "config" or slide.lower().endswith("/config"):
        for fileType in slides.pop(slide):
            fullPath = slide + "." + fileType
            if fileType.lower() in ["xls", "xlsx", "csv"]:
                print("Config file found: " + fullPath, flush=True)

itemsList = []
# Check through the files found above to see if the special "items" file is found anywhere, and if so deal with it and remove it from the list.
for slide in slides:
    if slide.lower() == "items" or slide.lower().endswith("/items"):
        for fileType in slides.pop(slide):
            fullPath = slide + "." + fileType
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

shutil.copyfile("slideshowIndex.html", args["output"] + os.sep + "index.html")
slideCount = 1
for slide in slides:
    for fileType in slides[slide]:
        if fileType in docsToMarkdownLib.bitmapTypes:
            SVGContent = docsToMarkdownLib.embedBitmapInSVG(inputFolder + os.sep + slide + "." + fileType)
            docsToMarkdownLib.putFile(args["output"] + os.sep + str(slideCount) + ".svg", SVGContent)
        else:
            shutil.copyfile(inputFolder + os.sep + slide + "." + fileType, args["output"] + os.sep + str(slideCount) + "." + fileType.lower())
        slideCount = slideCount + 1
