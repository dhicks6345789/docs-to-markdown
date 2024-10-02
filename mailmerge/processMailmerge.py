#!/usr/bin/python

# Standard libraries.
import os
import sys
import shutil

# The python-docx library, for manipulating DOCX files.
# Importantly, when installing with pip, that's not the "docx" library, that's an earlier version - do "pip install python-docx"...
import docx
# ...and the docs-replace library, to install do ""pip install python-docx-replace".
import python_docx_replace 

# We use Pandas to import Excel / CSV files for configuration details.
import pandas

# Our own Docs To Markdown library.
import docsToMarkdownLib

# Get the command line arguments.
inputFolder = sys.argv[1]
outputFolder = sys.argv[2]

print("Processing Mailmerge folder: " + inputFolder + " to " + outputFolder, flush=True)

# Go through items in the input folder, deal with particular items.
synonyms = {}
inputItems = []
templateFiles = []
defaultTemplate = "../default.docx"
for inputItem in os.listdir(inputFolder):
  if os.path.isfile(inputFolder + os.sep + inputItem):
    # Get the filename and file type (extension, if ther is one).
    fileSplit = inputItem.rsplit(".", 1)
    fileName = fileSplit[0]
    fileType = ""
    if fileSplit.length > 1:
      fileType = fileSplit[1].upper()
      
    # Check for a "synonyms" XLSX (or XLS / CSV) file.
    if inputItem.lower() == "synonyms.xlsx":
        for synonymIndex, synonymItem in pandas.read_excel(inputFolder + "/" + inputItem, header=None).iterrows():
          synonyms[synonymItem[0]] = synonymItem[1]
    # Otherwise, any XLSX / XLS / CSV file is an input file.
    elif fileType in ["XLSX", "XLS", "CSV"]:
      inputItems.append(inputItem)
    elif fileType in ["DOCX"]:
      templateFiles.append(inputItem)
    elif inputItem.lower() == "default.docx":
        defaultTemplate = inputFolder + "/" + inputItem

sortedTemplateFiles = []
for inputItem in templateFiles:
  fileName = inputItem.rsplit(".", 1)[0]
  fileType = inputItem.rsplit(".", 1)[1].upper()
  if not inputItem in inputItems and not os.path.isdir(inputFolder + os.sep + fileName):
    sortedTemplateFiles.append(inputItem)
sortedTemplateFiles = sorted(sortedTemplateFiles)
if sortedTemplateFiles.length > 0:
  defaultTemplate = sortedTemplateFiles[0]
  
for inputItem in inputItems:
  # Process each mailmerge data Excel (XLSX, XLS) or CSV file.
  mailData = pandas.DataFrame()
  if fileType in ["XLSX", "XLS"]:
    mailData = pandas.read_excel(inputFolder + "/" + inputItem)
  elif fileType in ["CSV"]:
    mailData = pandas.read_csv(inputFolder + "/" + inputItem)

  if not mailData.empty:
    print("Processing " + fileName + "...")
    
    # Make sure there's an empty output folder with a name that matches the input filename.
    shutil.rmtree(outputFolder + os.sep + fileName)
    os.makedirs(outputFolder + os.sep + fileName, exist_ok=True)
    
    # Make any column headers lower case for easier comparison.
    mailData.columns = map(str.lower, mailData.columns)

    # Process each item in the mailmerge data.
    for mailIndex, mailItem in mailData.iterrows():
      # Set the template file to use. See if there's a folder matching a column heading and template file matching a value, otherwise use the default.
      templateFile = defaultTemplate
      for heading in mailItem.index:
        heading = heading.lower()
        value = mailItem[heading].lower()
        if value in synonyms.keys():
          value = synonyms[value].lower()
        if os.path.isfile(inputFolder + os.sep + heading + os.sep + value + ".docx"):
          templateFile = inputFolder + os.sep + heading + os.sep + value + ".docx"

      # Do the mailmerge.
      print("Do Mailmerge: " + templateFile + " to " + outputFolder + os.sep + fileName + os.sep + str(mailIndex) + ".docx")
      # Open the template document using python-docx...
      mailDoc = docx.Document(templateFile)
      # ...replace key / value pairs...
      python_docx_replace.docx_replace(mailDoc, **mailItem.to_dict())
      # ...save the output document.
      mailDoc.save(outputFolder + os.sep + fileName + os.sep + str(mailIndex) + ".docx")
