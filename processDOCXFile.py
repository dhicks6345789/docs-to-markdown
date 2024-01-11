import os
import sys

# Our own Docs To Markdown library.
import docsToMarkdownLib

inputFile = sys.argv[1]
outputFolder = sys.argv[2]

print("STATUS: processMarkdownFile: " + inputFile + " to " + outputFolder)
