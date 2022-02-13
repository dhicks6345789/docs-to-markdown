import subprocess

# Pandoc escapes Markdown control characters embedded in Word documents, but we want to let people embed chunks of Markdown in
# a document if they want, so we un-escape the Markdown back again - we simply use Python's string.replace to replace characters
# in strings.
markdownReplace = {"\\[":"[","\\]":"]","\\!":"!"}

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
# As of around Monday, 4th March 2019, Pandoc 2.7 now seems to work correctly for parsing DOCX files produced by Word Online. Debian's Pandoc package is still on
# version 2.5, so Pandoc needs to be installed via the .deb file provided on their website.
def docToMarkdown(inputFile, baseURL="", markdownType="gfm", validFrontMatterFields=["title"]):
    markdown = ""
    frontMatter = {}
    
    pandocProcess = subprocess.Popen("pandoc --wrap=none -s " + inputFile + " -t " + markdownType + " -o -", shell=True, stdout=subprocess.PIPE)
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
