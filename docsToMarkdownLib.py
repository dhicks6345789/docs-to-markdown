import os
import subprocess

# Pandoc escapes Markdown control characters embedded in Word documents, but we want to let people embed chunks of Markdown in
# a document if they want, so we un-escape the Markdown back again - we simply use Python's string.replace to replace characters
# in strings.
markdownReplace = {"\\[":"[","\\]":"]","\\!":"!"}

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
    
    pandocCommand = "pandoc --wrap=none -s \"" + inputFile + "\" -t " + markdownType + " -o -"
    print(pandocCommand)
    pandocProcess = subprocess.Popen(pandocCommand, shell=True, stdout=subprocess.PIPE)
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
