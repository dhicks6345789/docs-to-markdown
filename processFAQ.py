import os
import sys

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]

print("processFAQ: " + inputFolder + " to " + outputFolder)
for item in os.listdir(inputFolder):
    if item.rsplit(".", 1)[1].lower() in ["docx", "doc"]:
        print("Convert to Markdown: " + inputFolder + os.sep + item)
