import os
import sys

# Our own Docs To Markdown library.
import docsToMarkdownLib

inputFile = sys.argv[1]
outputFolder = sys.argv[2]

docType = inputFile.rsplit(".", 1)[1].upper()
if docType in ["DOCX", "DOC"]:
  outputFile = inputFile
  if os.sep in outputFile:
    outputFile = outputFile.rsplit(os.sep, 1)[1]
  outputFile = outputFile.rsplit(".", 1)[0] + ".md"
  outputPath = outputFolder + os.sep + outputFile
  if not docsToMarkdownLib.checkModDatesMatch(inputFile, outputPath):
    print("Processing " + docType + " file: " + inputFile + " to " + outputPath, flush=True)
    docMarkdown, docFrontmatter = docsToMarkdownLib.docToMarkdown(inputFile)
    trimmedMarkdown = ""
    for markdownLine in docMarkdown.split("\n"):
      if markdownLine.startswith("# ") and not "title" in docFrontmatter.keys():
        docFrontmatter["title"] = markdownLine[2:].lstrip()
      else:
        trimmedMarkdown = trimmedMarkdown + markdownLine + "\n"
    docsToMarkdownLib.putFile(outputPath, docsToMarkdownLib.frontMatterToString(docFrontmatter) + trimmedMarkdown.strip())
    docsToMarkdownLib.makeModDatesMatch(inputFile, outputPath)
