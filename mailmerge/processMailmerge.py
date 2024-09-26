#!/usr/bin/python

# Standard libraries.
import os

# The python-docx library, for manipulating DOCX files.
# Importantly, when installing with pip, that's not the "docx" library, that's an earlier version - do "pip install python-docx"...
import docx
# ...and the docs-replace library, to install do ""pip install python-docx-replace".
import docx_replace

# We use Pandas to import Excel / CSV files for configuration details.
import pandas

# Our own Docs To Markdown library.
import docsToMarkdownLib

# Get the command line arguments.
inputFolder = sys.argv[1]
outputFolder = sys.argv[2]

print("Processing Mailmerge folder: " + inputFolder + " to " + outputFolder, flush=True)
mailData = pandas.DataFrame()
for inputItem in os.listdir(inputFolder):
  fileType = inputItem.rsplit(".", 1)[1].upper()
  # Load mailmerege data from Excel (XLSX, XLS) or CSV files.
  if fileType in ["XLSX"]:
    mailData = pandas.read_excel(inputFolder + "/" + inputItem)

print(mailData)
