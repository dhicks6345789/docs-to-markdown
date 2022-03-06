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

# Check through the files found above to see if the special "config" file is found anywhere, and if so deal with it and remove it from the list.
for section in sections:
    for fileName in sorted(section[1].keys()):
        if fileName.lower() == "config":
            for fileType in section[1].pop("config"):
                fullPath = section[0] + os.sep + fileName + "." + fileType
                if fileType.lower() in ["xls", "xlsx", "csv"]:
                    print("Config: " + fullPath, flush=True)

# Returns the URL value from a Windows-style .url file.
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
            frontMatter["col" + str(colNum) + "Label"] = item[3]
            if item[1] == "link":
                frontMatter["col" + str(colNum) + "URL"] = item[2]
        colNum = colNum + item[0]
    
    if colNum <= 12:
        frontMatter["col" + str(colNum) + "Width"] = str(13-colNum)
        frontMatter["col" + str(colNum) + "Type"] = "blank"
    
    docsToMarkdownLib.putFile(args["output"] + os.sep + "Row" + docsToMarkdownLib.padInt(rowCount, 3) + ".md", docsToMarkdownLib.frontMatterToString(frontMatter))
    
    rowX = 1
    rowCount = rowCount + 1
    rowHeight = 1
    rowItems = []

# Compares two arrays of strings, matches are case-insensitive. If any match is found the original item from the first
# array is returned, so a return value might be mixed case.
def arrayIsIn(leftArray, rightArray):
    for leftItem in leftArray:
        for rightItem in rightArray:
            if leftItem.lower() == rightItem.lower():
                return leftItem
    return ""

# Sort the items found into rows, producing one Markdown file per row.
for section in sections:
    if not section[1] == {}:
        if not section[0] == args["input"]:
            rowTitle = docsToMarkdownLib.removeNumericWord(section[0][len(args["input"])+1:])
        for fileName in section[1].keys():
            # Figure out what type of item we have. If we just have a .url file then we have an "iframe", if we have a .url and a matching image we have a "link",
            # if we just have an image then we have an "image".
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
            if itemType == "iframe":
                width = 4
                height = 4
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
                    rowItems.append((width, "link", URL, itemLabel))
                    iconString = ""
                    iconBuffered = io.BytesIO()
                    iconInputFileName = fileName + "." + imageType
                    iconOutputPath = args["output"] + os.sep + "static" + os.sep + "icons" + os.sep + str(rowCount) + "-" + str(rowX) + "-icon.svg"
                    if imageType == "" and not os.path.exists(iconOutputPath):
                        print("STATUS: No icon found for link: " + fileName + " - downloading favicon for: " + URL, flush=True)
                        icons = favicon.get(URL)
                        print(icons)
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
                                icon = icons[0]
                                imageType = icon.format
                                response = requests.get(icon.url)
                                try:
                                    iconBitmap = PIL.Image.open(io.BytesIO(response.content))
                                    iconBitmap.thumbnail((100,100))
                                    iconBitmap.save(iconBuffered, format="PNG")
                                except PIL.UnidentifiedImageError:
                                    print("Favicon not valid: " + URL, flush=True)
                                    imageType = "svg"
                                    iconInputFileName = "default"
                    elif imageType in bitmapTypes:
                        iconBitmap = PIL.Image.open(section[0] + os.sep + iconInputFileName)
                        iconBitmap.thumbnail((100,100))
                        iconBitmap.save(iconBuffered, format="PNG")
                    if imageType == "svg":
                        if iconInputFileName == "default":
                            shutil.copyfile("assets" + os.sep + "default.svg", iconOutputPath)
                        else:
                            shutil.copyfile(section[0] + os.sep + iconInputFileName, iconOutputPath)
                    else:
                        iconString = "<svg width=\"100\" height=\"100\" version=\"1.1\" viewBox=\"0 0 26.458 26.458\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n"
                        iconString = iconString + "    <image width=\"26.458\" height=\"26.458\" preserveAspectRatio=\"none\" xlink:href=\"data:image/png;base64," + base64.b64encode(iconBuffered.getvalue()).decode("utf-8") + "\"/>\n"
                        iconString = iconString + "</svg>"
                    if not imageType in ["", "svg"]:
                        os.makedirs(args["output"] + os.sep + "static" + os.sep + "icons", exist_ok=True)
                        docsToMarkdownLib.putFile(iconOutputPath, iconString)
                        
            rowX = rowX + width
        newRow()
