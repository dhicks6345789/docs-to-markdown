# A script to generate a slideshow (a folder containing index.html and a set of normalised assets) from a folder of assets (images, videos, audio).

# Standard libraries.
import os
import io
import sys
import shutil
import datetime

# Our own Docs To Markdown library.
import docsToMarkdownLib



# Get a timestamp of when we started.
timestamp = int(round(datetime.datetime.now().timestamp()))

# Get any arguments given via the command line.
args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"width":"9", "height":"16", "scale":"true"}, requiredArgs=["input","output"])

print("STATUS: processSlideshow: " + args["input"] + " to " + args["output"], flush=True)

doScale = False
if args["scale"] == "true":
    doScale = True

# Make sure the output folder exists.
os.makedirs(args["output"], exist_ok=True)



# Check through items in the given input folder, recursing into sub-folders.
# Produces an array (in the global "slides" variable) containing tuples of file names and an array of extensions found.
slides = {}
inputFolder = docsToMarkdownLib.normalisePath(args["input"])
def listFileNames(theSubFolder):
    global inputFolder
    global slides
    
    inputPath = inputFolder + os.sep + theSubFolder
    for inputItem in sorted(os.listdir(inputPath)):
        if os.path.isdir(docsToMarkdownLib.normalisePath(inputPath + os.sep + inputItem)):
            listFileNames(docsToMarkdownLib.normalisePath(theSubFolder + os.sep + inputItem))
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
print("List of slides:")
print(slides)

config = []
# Check through the files found above to see if the special "config" file is found anywhere, and if so deal with it and remove it from the list.
for slide in slides:
    if slide.lower() == "config" or slide.lower().endswith("/config"):
        for fileType in slides.pop(slide):
            fullPath = slide + "." + fileType
            if fileType.lower() in ["xls", "xlsx", "csv"]:
                print("Config file found: " + fullPath, flush=True)
                docsToMarkdownLib.processArgsFile(fullPath, defaultArgs=args)

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

slideCount = 1
slideList = []
for slide in slides:
    for fileType in slides[slide]:
        # We add a timestamp string to each filename so that the browser reloads images / videos.
        fileName = str(slideCount) + "-" + str(timestamp)
        if fileType in docsToMarkdownLib.bitmapTypes:
            SVGContent = docsToMarkdownLib.embedBitmapInSVG(inputFolder + os.sep + slide + "." + fileType, args["width"], args["height"])
            docsToMarkdownLib.putFile(args["output"] + os.sep + fileName + ".svg", SVGContent)
            slideList.append(fileName + ".svg")
        elif doScale and fileType in docsToMarkdownLib.videoTypes:
            docsToMarkdownLib.thumbnailVideo(inputFolder + os.sep + slide + "." + fileType, args["output"] + os.sep + fileName + ".mp4", args["width"], args["height"], doScale)
            slideList.append(fileName + ".mp4")
        else:
            shutil.copyfile(inputFolder + os.sep + slide + "." + fileType, args["output"] + os.sep + fileName + "." + fileType.lower())
            slideList.append(fileName + "." + fileType.lower())
        slideCount = slideCount + 1

docsToMarkdownLib.putFile(args["output"] + os.sep + "index.html", docsToMarkdownLib.getFile("slideshow/slideshowIndex.html").replace("<<RESOURCESGOHERE>>", str(slideList).replace("\'", "\"")))
