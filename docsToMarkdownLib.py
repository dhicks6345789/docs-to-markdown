# Standard libraries.
import os
import io
import sys
import base64
import subprocess

# The Pillow image-handling library.
import PIL.Image

# We use the Pandas library, which in turn uses the XLRD library, to read Excel data.
import pandas



# Pandoc escapes Markdown control characters embedded in Word documents, but we want to let people embed chunks of Markdown in
# a document if they want, so we un-escape the Markdown back again - we simply use Python's string.replace to replace characters
# in strings.
markdownReplace = {"\\[":"[","\\]":"]","\\!":"!"}

# An array of "image file" types.
bitmapTypes = ["jpg", "jpeg", "png", "ico"]
imageTypes =  bitmapTypes + ["svg"]

# An array of "video file" types.
videoTypes = ["mp4"]

# An array of "url file" types.
urlTypes = ["url", "txt"]

# A utility function to return the contents of the given file.
def getFile(theFilename):
    infile = open(theFilename)
    result = infile.read()
    infile.close()
    return(result)
    
# A utility function to write the contents of the given string to the given file.
def putFile(theFilename, theContent):
    if os.sep in theFilename:
        parentFolderName = theFilename.rsplit(os.sep, 1)[0]
        if not os.path.exists(parentFolderName):
            os.makedirs(parentFolderName)
    outfile = open(theFilename, "wt", encoding="utf-8")
    outfile.write(theContent)
    outfile.close()

# A utility function to return a given path string in normalised format, i.e. without any double os.sep characters,
# and with no os.sep character at the end of the string.
def normalisePath(thePath):
    thePath = thePath.strip()
    if thePath == "":
        return ""
    result = thePath.replace(os.sep+os.sep, os.sep)
    if result[len(result)-1] == os.sep:
        result = result[:-1]
    return result

# A utility function to determine whether a variable has a value of "NaN" or not.
# Checks if a string has a value of "NaN" (any case) as well as float values.
def isnan(theVal):
    if isinstance(theVal, str):
        if theVal.lower() == "nan":
            return True
        return False
    return math.isnan(theVal)

def checkModDatesMatch(theInputItem, theOutputItem):
    if os.path.isfile(theOutputItem):
        inputItemDetails = os.stat(theInputItem)
        outputItemDetails = os.stat(theOutputItem)
        if inputItemDetails.st_mtime == outputItemDetails.st_mtime:
            return True
    return False

def makeModDatesMatch(theInputItem, theOutputItem):
    inputItemDetails = os.stat(theInputItem)
    os.utime(theOutputItem, (inputItemDetails.st_atime, inputItemDetails.st_mtime))

# Given an integer and a length, returns the int converted to a string, with the string length made up to the given
# length with "0"s appended to the front of the string as needed.
def padInt(theInt, theLength):
    result = str(theInt)
    while len(result) < theLength:
        result = "0" + result
    return result

# Given a string, if the first word (defined by space in the string) of the string is purely numeric, returns the string with that word removed.
# Basically, given a string like "0001 One Two Three.doc", returns "One Two Three.doc". If no spaces are found, just returns the input.
def removeNumericWord(theString):
    stringSplit = theString.strip().split(" ", 1)
    if stringSplit[0].isnumeric() and len(stringSplit) == 2:
        return stringSplit[1]
    return stringSplit[0]
    
# Given a dict, returns a YAML string, e.g.:
# ---
# variableName: value
# ---
def frontMatterToString(theFrontMatter):
    if theFrontMatter == {}:
        return ""
    result = "---\n"
    for frontMatterField in theFrontMatter.keys():
        result = result + frontMatterField + ": " + theFrontMatter[frontMatterField] + "\n"
    return(result + "---\n")

# Takes a file path string pointing to a document file (.DOC, .DOCX, .TXT, etc) file, loads that file and coverts the contents to a Markdown string using Pandoc.
# Returns a tuple of a string of the converted data and a dict of any front matter variables specified in the input file.
# Note: previously, a bug prevented Pandoc correctly parsing DOCX files produced by Word Online. As of around Monday, 4th March 2019, Pandoc 2.7 now seems to work.
# The Debian 11 (Bullseye) Pandoc package version is 2.9, previous versions are 2.5 or earlier, so you either need to make sure Debian is up-to-date or install
# Pandoc via the .deb file provided on their website.
def docToMarkdown(inputFile, baseURL="", markdownType="gfm", validFrontMatterFields=["title"]):
    markdown = ""
    frontMatter = {}
    
    pandocProcess = subprocess.Popen("pandoc --wrap=none -s \"" + inputFile + "\" -t " + markdownType + " -o -", shell=True, stdout=subprocess.PIPE)
    for markdownLine in pandocProcess.communicate()[0].decode("utf-8").split("\n"):
        for markdownReplaceKey in markdownReplace.keys():
            markdownLine = markdownLine.replace(markdownReplaceKey, markdownReplace[markdownReplaceKey])
        lineIsFrontMatter = False
        for validFrontMatterField in validFrontMatterFields:
            if markdownLine.lower().startswith(validFrontMatterField.lower() + ":"):
                frontMatter[validFrontMatterField] = markdownLine.split(":")[1].strip()
                lineIsFrontMatter = True
        if not lineIsFrontMatter:
            markdown = markdown + markdownLine.replace(baseURL, "") + "\n"
    return(markdown, frontMatter)

# Takes an input file and coverts it to Markdown, writing that Markdown to the given output file.
def docToMarkdownFile(inputFile, outputFile, baseURL="", markdownType="gfm", validFrontMatterFields=["title"]):
    outputMarkdown, outputFrontmatter = docToMarkdown(inputFile, baseURL=baseURL, markdownType=markdownType, validFrontMatterFields=validFrontMatterFields)
    putFile(outputFile, frontMatterToString(outputFrontmatter) + outputMarkdown)

def processCommandLineArgs(defaultArgs={}, requiredArgs=[], optionalArgs=[], optionalArgLists=[]):
    args = defaultArgs
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
    return args

def processArgsFile(theFilename, defaultArgs={}, requiredArgs=[], optionalArgs=[], optionalArgLists=[]):
    args = defaultArgs
    
    if theFilename.endswith(".csv"):
        argsData = pandas.read_csv(theFilename, header=0)
    else:
        argsData = pandas.read_excel(theFilename, header=0)
    for argsDataIndex, argsDataValues in argsData.iterrows():
        if argsDataValues[0] in requiredArgs + optionalArgs:
            if not argsDataValues[0] in args:
                args[argsDataValues[0]] = valueToString(argsDataValues[1])
        elif argsDataValues[0] in optionalArgLists:
            for argsDataValue in argsDataValues[1:].values:
                if not isnan(argsDataValue):
                    args[argsDataValues[0]].append(argsDataValue)
    return args

# Given two ints, returns those two ints divided by their highest common divisor, or simply
# returns the two same ints if there is no common divisor. Checks from the given range downwards.
def reduceInts(theRange, leftInt, rightInt):
    for pl in range(theRange, 2, -1):
        leftDivide = float(leftInt) / float(pl)
        rightDivide = float(rightInt) / float(pl)
        if leftDivide == float(int(leftDivide)) and rightDivide == float(int(rightDivide)):
            return (int(leftDivide), int(rightDivide))
    return (leftInt, rightInt)

def thumbnailVideo(theInputVideo, theOutputVideo, theBlockWidth, theBlockHeight):
    print("Video: " + theInputVideo)
    # Figure out the video's dimensions.
    videoDimensions = os.popen("ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x \"" + theInputVideo + "\" 2>&1").read().strip()
    videoWidth = int(videoDimensions.split("x")[0])
    videoHeight = int(videoDimensions.split("x")[1])
    
    # Scale the dimensions given as the output to match the input video.
    width, height = getRatioedDimensions(videoWidth, videoHeight, theBlockWidth, theBlockHeight)
    
    # Figure out the ratio of width to height of the input video clip...
    pictureRatio = float(videoWidth) / float(videoHeight)
    # ...and of the output video.
    outputRatio = float(width) / float(height)
    
    resultWidth = videoWidth
    resultHeight = videoHeight
    pasteX = 0
    pasteY = 0
    if pictureRatio < outputRatio:
        padHeightRatio = 1 + (outputRatio - pictureRatio)
        resultHeight = int(videoHeight / padHeightRatio)
        pasteX = int(videoWidth / padHeightRatio)
    elif pictureRatio > outputRatio:
        padWidthRatio = 1 + (pictureRatio - outputRatio)
        resultWidth = int(videoWidth / padWidthRatio)
        pasteY = int(resultHeight - ((float(videoHeight) / padWidthRatio)/2))
    
    ffmpegLine = "ffmpeg -i \"" + theInputVideo + "\" -vf \"pad=" + str(resultWidth) + ":" + str(resultHeight) + ":" + str(pasteX) + ":" + str(pasteY) + "\" \"" + theOutputVideo + "\" 2>&1"
    print(ffmpegLine)
    
# Produce a thumbnail of an image. Differs from PIL.thumbnail() in that thumbnails are returned in a new image padded to match the aspect ratio of
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

def getRatioedDimensions(objectWidth, objectHeight, ratioWidth, ratioHeight):
    if int(ratioWidth) > objectWidth:
        width = int(ratioWidth)
        height = int((float(ratioWidth) / float(objectWidth)) * float(objectHeight))
    else:
        width = int(objectWidth)
        height = int((float(objectWidth) / float(ratioWidth)) * float(ratioHeight))
    return width, height

def embedBitmapInSVG(theBitmap, theWidth, theHeight):
    print("Emedding bitmap: " + theBitmap)
    bitmapObject = PIL.Image.open(theBitmap)
    
    width, height = getRatioedDimensions(bitmapObject.width, bitmapObject.height, theWidth, theHeight)
    
    bitmapObject = thumbnailImage(bitmapObject, width, height)
    bitmapData = io.BytesIO()
    bitmapObject.save(bitmapData, format="PNG")
    
    print("Width: " + str(width) + " Height: " + str(height))
    result = "<svg version=\"1.1\" viewBox=\"0 0 " + str(width) + " " + str(height) + "\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n"
    result = result + "    <image width=\"" + str(width) + "\" height=\"" + str(height) + "\" preserveAspectRatio=\"none\" xlink:href=\"data:image/png;base64," + base64.b64encode(bitmapData.getvalue()).decode("utf-8") + "\"/>\n"
    result = result + "</svg>"
    return result
