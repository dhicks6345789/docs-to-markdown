# A script to help generate a "dashboard" style web page. Doesn't produce an HTML file directly, but instead produces Markdown documents ready for use with
# a static site generation tool (Hugo, Jekyll, Eleventy). Produces Hugo-ready files by default.

# Standard libraries.
import os
import io
import sys
import base64
import shutil

# The Pillow image-handling library.
import PIL.Image

# The Requests library, for handling HTTP(S) requests.
import requests

# A library for downloading (not generating) favicons from a site.
import favicon

# Our own Docs To Markdown library.
import docsToMarkdownLib

# We use the Pandas library to load in Excel / CSV files for the configuration settings.
import pandas

# An array of "image file" types.
bitmapTypes = ["jpg", "jpeg", "png", "ico"]
imageTypes =  bitmapTypes + ["svg"]

# An array of "url file" types.
urlTypes = ["url", "txt"]

# Get any arguments given via the command line.
args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"generator":"hugo"}, requiredArgs=["input","output"])

print("STATUS: processDashboard: " + args["input"] + " to " + args["output"], flush=True)

# Make sure the output folder exists.
os.makedirs(args["output"], exist_ok=True)

# Given two ints, returns those two ints divided by their highest common divisor, or simply
# returns the two same ints if there is no common divisor. Checks from the given range downwards.
def reduceInts(theRange, leftInt, rightInt):
    for pl in range(theRange, 2, -1):
        leftDivide = float(leftInt) / float(pl)
        rightDivide = float(rightInt) / float(pl)
        if leftDivide == float(int(leftDivide)) and rightDivide == float(int(rightDivide)):
            return (int(leftDivide), int(rightDivide))
    return (leftInt, rightInt)

# Produce a thmbnail of an image. Differs from PIL.thumbnail() in that thumbnails are returned in a new image padded to match the aspect ratio of
# the given block width and height.
def thumbnailImage(theImage, theBlockWidth, theBlockHeight):
    imageWidth, imageHeight = theImage.size
    imageRatio = float(imageWidth) / float(imageHeight)
    
    blockWidth, blockHeight = reduceInts(12, theBlockWidth, theBlockHeight)
    blockRatio = float(blockWidth) / float(blockHeight)
    
    resultWidth = imageWidth
    resultHeight = imageHeight
    if imageRatio < blockRatio:
        padWidthRatio = 1 + (blockRatio - imageRatio)
        resultWidth = int(imageWidth * padWidthRatio)
    elif imageRatio > blockRatio:
        padHeightRatio = 1 + (imageRatio - blockRatio)
        resultHeight = int(imageHeight * padHeightRatio)
        
    result = PIL.Image.new(mode="RGB", size=(resultWidth, resultHeight), color="WHITE")
    pasteX = 0
    if not resultWidth == imageWidth:
        pasteX = int((resultWidth-imageWidth)/2)
    pasteY = 0
    if not resultHeight == imageHeight:
        pasteY = int((resultHeight-imageHeight)/2)
    result.paste(theImage, (pasteX, pasteY))
    
    return result

# Returns the given image with any background transparency set to the given colour.
def setImageTransparencyToSolid(theImage, theColour):
    RGBABitmap = theImage.convert("RGBA")
    plainColouredBitmap = PIL.Image.new("RGBA", theImage.size, theColour)
    plainColouredBitmap.paste(RGBABitmap, mask=RGBABitmap)
    return plainColouredBitmap

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
            for fileType in section[1].pop("config"):
                fullPath = section[0] + os.sep + fileName + "." + fileType
                if fileType.lower() in ["xls", "xlsx", "csv"]:
                    print("Config found: " + fullPath, flush=True)
                    if fileType.lower() in ["xls", "xlsx"]:
                        configSheet = pandas.read_excel(fullPath)
                    else:
                        configSheet = pandas.read_csv(fullPath)
                    # Convert the Pandas dataframe to a dict, lowercasing all the keys.
                    for configItem in configSheet.to_dict(orient="records"):
                        config.append({k.lower(): v for k, v in configItem.items()})
                    print(config)
                        
# Returns the URL value from a .url file - can either be a Windows-style .url file or simply a text file with a .url extension.
def getURLDetails(theFilename):
    URLLines = docsToMarkdownLib.getFile(theFilename).split("\n")
    for URLLine in URLLines:
        if URLLine.startswith("URL="):
            return URLLine.strip()[4:]
    return URLLines[0].strip()

# The newRow function, used by the row-sorting code section below.
rowX = 1
rowCount = 1
rowHeight = 1
rowTitle = ""
rowItems = []
def newRow():
    global rowX
    global rowCount
    global rowHeight
    global rowItems
    global rowTitle
    
    frontMatter = {}
    if not rowTitle == "":
        frontMatter["title"] = rowTitle
    if args["generator"] == "eleventy":
        frontMatter["tags"] = "row"
        frontMatter["height"] = str(rowHeight)
    colNum = 1
    for item in rowItems:
        frontMatter["col" + str(colNum) + "Width"] = str(item[0])
        frontMatter["col" + str(colNum) + "Type"] = item[1]
        if not item[1] == "blank":
            frontMatter["col" + str(colNum) + "Label"] = item[2]
            if item[1] == "link":
                frontMatter["col" + str(colNum) + "URL"] = item[3]
        colNum = colNum + item[0]
    
    if colNum <= 12:
        frontMatter["col" + str(colNum) + "Width"] = str(13-colNum)
        frontMatter["col" + str(colNum) + "Type"] = "blank"
    
    docsToMarkdownLib.putFile(args["output"] + os.sep + "Row" + docsToMarkdownLib.padInt(rowCount, 3) + ".md", docsToMarkdownLib.frontMatterToString(frontMatter))
    
    rowX = 1
    rowCount = rowCount + 1
    rowHeight = 1
    rowItems = []
    rowTitle = ""

# Compares two arrays of strings, matches are case-insensitive. If any match is found the original item from the first
# array is returned, so a return value might be mixed case.
def arrayIsIn(leftArray, rightArray):
    for leftItem in leftArray:
        for rightItem in rightArray:
            if leftItem.lower() == rightItem.lower():
                return leftItem
    return ""

def sortIconObject(theIcon):
    return (theIcon.size[0] * theIcon.size[1])

# Sort the items found into rows, producing one Markdown file per row.
for section in sections:
    if not section[1] == {}:
        if not section[0] == args["input"]:
            rowTitle = docsToMarkdownLib.removeNumericWord(section[0][len(args["input"])+1:])
        for fileName in section[1].keys():
            # Figure out what type of item we have.
            itemType = "blank"
            fileType = arrayIsIn(section[1][fileName], urlTypes)
            imageType = arrayIsIn(section[1][fileName], imageTypes)
            itemLabel = docsToMarkdownLib.removeNumericWord(fileName.rsplit(".", 1)[0])
            if not itemLabel.lower() == "blank":
                if not fileType == "":
                    section[1][fileName].remove(fileType)
                    itemType = "link"
                elif not imageType == "":
                    itemType = "image"
            
            width = 1
            height = 1
            if itemType == "image":
                width = 4
                height = 4
                
            for configItem in config:
                print(configItem + " == " + fileName)
                if configItem["item"] == fileName:
                    print("Matched config: " + fileName)
                
            if rowX + width > 13:
                newRow()
            if height > rowHeight:
                rowHeight = height
                
            if itemType == "blank":
                rowItems.append((width, "blank"))
            else:
                if itemType == "image":
                    rowItems.append((width, "image", itemLabel))
                elif itemType == "link":
                    URL = getURLDetails(section[0] + os.sep + fileName + "." + fileType)
                    rowItems.append((width, "link", itemLabel, URL))
                if itemType == "image" or itemType == "link":
                    iconString = ""
                    iconBuffered = io.BytesIO()
                    iconInputFileName = fileName + "." + imageType
                    iconOutputPath = args["output"] + os.sep + "static" + os.sep + "icons" + os.sep + str(rowCount) + "-" + str(rowX) + "-icon.svg"
                    if imageType == "" and not os.path.exists(iconOutputPath):
                        print("STATUS: No icon found for link: " + fileName + " - downloading favicon for: " + URL, flush=True)
                        icons = favicon.get(URL)
                        if len(icons) == 0:
                            imageType = "svg"
                            iconInputFileName = "default"
                        else:
                            for icon in icons:
                                if icon.format == "svg":
                                    iconResponse = requests.get(icon.url, stream=True)
                                    for iconChunk in iconResponse.iter_content(1024):
                                        iconString = iconString + iconChunk
                            if iconString == "":
                                iconObjects = []
                                for icon in icons:
                                    response = requests.get(icon.url)
                                    try:
                                        iconObjects.append(PIL.Image.open(io.BytesIO(response.content)))
                                    except PIL.UnidentifiedImageError:
                                        print("Error retrieving Favicon: " + icon.url)
                                if iconObjects == []:
                                    imageType = "svg"
                                    iconInputFileName = "default"
                                else:
                                    iconObjects.sort(key=sortIconObject, reverse=True)
                                    thumbnailedImage = thumbnailImage(setImageTransparencyToSolid(iconObjects[0], "WHITE"), width, height)
                                    thumbnailedImage.save(iconBuffered, format="PNG")
                                    imageType = "png"
                    elif imageType in bitmapTypes:
                        print("Thumbnailing image: " + fileName)
                        thumbnailedImage = thumbnailImage(setImageTransparencyToSolid(PIL.Image.open(section[0] + os.sep + iconInputFileName), "WHITE"), width, height)
                        thumbnailedImage.save(iconBuffered, format="PNG")
                    if imageType == "svg":
                        if iconInputFileName == "default":
                            shutil.copyfile("assets" + os.sep + "default.svg", iconOutputPath)
                        else:
                            shutil.copyfile(section[0] + os.sep + iconInputFileName, iconOutputPath)
                    else:
                        iconString = "<svg width=\"" + str(thumbnailedImage.width) + "\" height=\"" + str(thumbnailedImage.height) + "\" version=\"1.1\" viewBox=\"0 0 " + str(float(width)*26.458) + " " + str(float(height)*26.458) + "\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n"
                        iconString = iconString + "    <image width=\"" + str(float(width)*26.458) + "\" height=\"" + str(float(height)*26.458) + "\" preserveAspectRatio=\"none\" xlink:href=\"data:image/png;base64," + base64.b64encode(iconBuffered.getvalue()).decode("utf-8") + "\"/>\n"
                        iconString = iconString + "</svg>"
                    if not imageType in ["", "svg"]:
                        os.makedirs(args["output"] + os.sep + "static" + os.sep + "icons", exist_ok=True)
                        docsToMarkdownLib.putFile(iconOutputPath, iconString)
                        
            rowX = rowX + width
        newRow()
