# Standard libraries.
import os
import sys
import subprocess

# The Pillow image-handling library.
import PIL.Image



# Pandoc escapes Markdown control characters embedded in Word documents, but we want to let people embed chunks of Markdown in
# a document if they want, so we un-escape the Markdown back again - we simply use Python's string.replace to replace characters
# in strings.
markdownReplace = {"\\[":"[","\\]":"]","\\!":"!"}

# An array of "image file" types.
bitmapTypes = ["jpg", "jpeg", "png", "ico"]
imageTypes =  bitmapTypes + ["svg"]

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
    return(args)

def embedBitmapInSVG(theBitmap):
    bitmapImage = io.BytesIO()
    PIL.Image.open(theBitmap).save(bitmapImage, format="PNG")
    result = "<svg width=\"" + str(thumbnailedImage.width) + "\" height=\"" + str(thumbnailedImage.height) + "\" version=\"1.1\" viewBox=\"0 0 " + str(float(width)*26.458) + " " + str(float(height)*26.458) + "\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n"
    result = result + "    <image width=\"" + str(float(width)*26.458) + "\" height=\"" + str(float(height)*26.458) + "\" preserveAspectRatio=\"none\" xlink:href=\"data:image/png;base64," + base64.b64encode(bitmapImage.getvalue()).decode("utf-8") + "\"/>\n"
    result = result + "</svg>"
    return result
