# Convert a DOCX / DOC (Word, Google Docs, etc) file to Markdown.
# Designed to be called from the scanFolders script, so takes a very simple command line parameter list.

# Standard libraries.
import os
import sys

# Our own Docs To Markdown library.
import docsToMarkdownLib

# Usage: processDOCFile.py inputFile outputFolder
inputFile = sys.argv[1]
outputFolder = sys.argv[2]

# Check we are trying to convert a DOCX / DOC file.
docType = inputFile.rsplit(".", 1)[1].upper()
if docType in ["DOCX", "DOC"]:
  # We are passed the output /folder/, so we have to figure out the output file name from the input file name.
  outputFile = inputFile
  if os.sep in outputFile:
    outputFile = outputFile.rsplit(os.sep, 1)[1]
  outputFile = outputFile.rsplit(".", 1)[0] + ".md"
  outputPath = outputFolder + os.sep + outputFile
  
  # Check and see if we already have an output file that matches the modification times of the input, if so, skip - no
  # point processing the same file for the same output.
  if not docsToMarkdownLib.checkModDatesMatch(inputFile, outputPath):
    print("Processing " + docType + " file: " + inputFile + " to " + outputPath, flush=True)

    # Our library "function" here calls Pandoc to do the conversion.
    docMarkdown, docFrontmatter = docsToMarkdownLib.docToMarkdown(inputFile)

    # Go through the Markdown line by line, checking for front matter variables.
    trimmedMarkdown = ""
    for markdownLine in docMarkdown.split("\n"):
      if outputPath.endswith("section1.0.md"):
        print("MDLine: " + markdownLine)
      if markdownLine.startswith("# ") and not "title" in docFrontmatter.keys():
        docFrontmatter["title"] = markdownLine[2:].lstrip()
      else:
        trimmedMarkdown = trimmedMarkdown + markdownLine + "\n"
    docsToMarkdownLib.putFile(outputPath, docsToMarkdownLib.frontMatterToString(docFrontmatter) + trimmedMarkdown.strip())
    docsToMarkdownLib.makeModDatesMatch(inputFile, outputPath)
