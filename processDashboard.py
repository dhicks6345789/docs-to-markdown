# A script to help generate a "dashboard" style web page. Doesn't produce an HTML file directly, but instead produces Markdown documents ready for use with
# a static site generation tool (Hugo, Jekyll, Eleventy). Produces Hugo-ready files by default.

# Standard libraries.
import os
import io
import sys
import base64

# The Pillow image-handling library.
import PIL.Image

# Our own Docs To Markdown library.
import docsToMarkdownLib

# Get any arguments given via the command line.
args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"generator":"hugo"}, requiredArgs=["input","output"])

print("STATUS: processDashboard: " + args["input"] + " to " + args["output"])

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
                    print("Config: " + fullPath)

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

# Takes a dict of filenames and array of types, plus an array of match strings.
def getFileNameMatches(theFileNames, theMatches):
    result = []
    for fileName in theFileNames.keys():
        for match in theFileNames[fileName]:
            if match.lower() in theMatches:
                result.append(fileName + "." + match)
    return(result)

# Sort the items found into rows, producing one Markdown file per row.
for section in sections:
    if not section[1] == {}:
        if not section[0] == args["input"]:
            rowTitle = docsToMarkdownLib.removeNumericWord(section[0][len(args["input"])+1:])
        for fileName in getFileNameMatches(section[1], ["url"]):
            width = 1
            height = 1
            if rowX + width > 12:
                newRow()
            if height > rowHeight:
                rowHeight = height
            if docsToMarkdownLib.removeNumericWord(filename.lower()) == "blank":
                rowItems.append((width, "blank"))
            else:
                iconFound = False
                for iconFileName in getFileNameMatches(section[1], ["png", "jpg"]):
                    if fileName.rsplit(".", 1)[0].lower() == iconFileName.rsplit(".", 1)[0].lower():
                        print("Found icon: " + iconFileName)
                        iconFound = True
                        rowItems.append((width, "link", fileName))
                        iconBitmap = PIL.Image.open(section[0] + os.sep + iconFileName)
                        iconBitmap.thumbnail((100,100))
                        iconBuffered = io.BytesIO()
                        iconBitmap.save(iconBuffered, format="PNG")
                        iconString = "<svg width=\"100\" height=\"100\" version=\"1.1\" viewBox=\"0 0 26.458 26.458\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n"
                        iconString = iconString + "    <image width=\"26.458\" height=\"26.458\" preserveAspectRatio=\"none\" xlink:href=\"data:image/png;base64," + base64.b64encode(iconBuffered.getvalue()).decode("utf-8") + "\"/>\n"
                        iconString = iconString + "</svg>"
                        os.makedirs(args["output"] + os.sep + "static" + os.sep + "icons", exist_ok=True)
                        docsToMarkdownLib.putFile(args["output"] + os.sep + "static" + os.sep + "icons" + os.sep + str(rowCount) + "-" + str(rowX) + "-icon.svg", iconString)
                if not iconFound:
                    rowItems.append((width, "iframe", fileName))
            rowX = rowX + width
        newRow()
