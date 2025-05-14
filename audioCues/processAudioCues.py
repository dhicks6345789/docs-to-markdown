# A script to generate an audio cues page (a folder containing index.html and a set of normalised assets) from a folder of assets (audio clips).

# Standard libraries.
import os
import io
import re
import sys
import shutil
import datetime

# The Pillow image -handling library.
import pil

# Our own Docs To Markdown library.
import docsToMarkdownLib



# Get a timestamp of when we started.
dateTimeNow = datetime.datetime.now()
timestamp = int(round(dateTimeNow.timestamp()))
dateTimeFormatted = dateTimeNow.strftime("%d-%m-%Y, %H:%M:%S")

# Get any arguments given via the command line.
args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"processAudio":"true"}, requiredArgs=["input","output"])

print("STATUS: processAudioCues: " + args["input"] + " to " + args["output"], flush=True)
print("Timestamp: " + str(timestamp) + ", Date / Time: " + dateTimeFormatted)

doProcessAudio = False
if args["processAudio"] == "true":
    doProcessAudio = True

# Make sure the output folder exists.
os.makedirs(args["output"], exist_ok=True)



# Check through items in the given input folder, recursing into sub-folders.
# Produces an array (in the global "files" variable) containing tuples of file names and an array of extensions found.
files = {}
inputFolder = docsToMarkdownLib.normalisePath(args["input"])
def listFileNames(theSubFolder):
    global inputFolder
    global files
    
    inputPath = inputFolder + os.sep + theSubFolder
    for inputItem in sorted(os.listdir(inputPath)):
        if os.path.isdir(docsToMarkdownLib.normalisePath(inputPath + os.sep + inputItem)):
            listFileNames(docsToMarkdownLib.normalisePath(theSubFolder + os.sep + inputItem))
        else:
            fileType = ""
            fileSplit = inputItem.rsplit(".", 1)
            fileName = fileSplit[0]
            if not theSubFolder == "":
                fileName = theSubFolder + os.sep + fileName
            if len(fileSplit) == 2:
                fileType = fileSplit[1]
            if not fileName in files.keys():
                files[fileName] = []
            files[fileName].append(fileType)
listFileNames("")
print("List of files:")
print(files)

config = []
# Check through the files found above to see if the special "config" file is found anywhere, and if so deal with it and remove it from the list.
for file in files:
    if file.lower() == "config" or file.lower().endswith("/config"):
        for fileType in files.pop(file):
            fullPath = file + "." + fileType
            if fileType.lower() in ["xls", "xlsx", "csv"]:
                print("Config file found: " + fullPath, flush=True)
                docsToMarkdownLib.processArgsFile(fullPath, defaultArgs=args)

itemsList = []
# Check through the files found above to see if the special "items" file is found anywhere, and if so deal with it and remove it from the list.
for file in files:
    if file.lower() == "items" or file.lower().endswith("/items"):
        for fileType in files.pop(file):
            fullPath = file + "." + fileType
            if fileType.lower() in ["xls", "xlsx", "csv"]:
                print("Items file found: " + fullPath, flush=True)
                if fileType.lower() in ["xls", "xlsx"]:
                    itemsSheet = pandas.read_excel(fullPath)
                else:
                    itemsSheet = pandas.read_csv(fullPath)
                # Convert the Pandas dataframe to an array of dicts, lowercasing all the keys and replacing all "NaN" values with empty string.
                for itemsIndex, itemsRow in itemsSheet.iterrows():
                    newItem = {}
                    for colName in itemsRow.keys():
                        if pandas.isna(itemsRow[colName]):
                            newItem[colName.lower()] = ""
                        else:
                            newItem[colName.lower()] = itemsRow[colName]
                    itemsList.append(newItem)

cueList = [["Filename", "Title", "Description", "TrimLeft", "TrimRight", "Icon"]]
outputFolder = docsToMarkdownLib.normalisePath(args["output"])
print("STATUS: processAudioCues - processing found audio files.", flush=True)
for file in files:
    fileHasAudio = False
    fileHasIcon = False
    for fileType in files[file]:
        if fileType.lower() in docsToMarkdownLib.audioTypes:
            fileHasAudio = True
        if fileType.lower() in docsToMarkdownLib.imageTypes:
            fileHasIcon = True
    if fileHasAudio:
        cueRow = ["", "", "", 0, 0, ""]
        for fileType in files[file]:
            inputFile = inputFolder + os.sep + file + "." + fileType
            outputFile = outputFolder + os.sep + file + ".mp3"
            iconFile = outputFolder + os.sep + file + ".png"
            if fileType.lower() in docsToMarkdownLib.audioTypes:
                print("Processing audio file: " + inputFile, flush=True)
                outputFile = outputFolder + os.sep + file + ".mp3"
                ffmpegCommand = "ffmpeg -y -i \"" + inputFile + "\" -vn -ar 44100 -ac 2 -b:a 192k \"" + outputFile + "\" >/dev/null 2>&1"
                print(ffmpegCommand, flush=True)
                #os.system(ffmpegCommand)
                if os.path.exists(outputFile):
                    cueRow[0] = file + ".mp3"
                    fileTitle = file.strip()
                    if re.match("^[0-9]+ *- *.*", fileTitle) != None:
                        fileTitle = fileTitle.split("-", 1)[1].strip()
                    cueRow[1] = fileTitle
                    cueRow[2] = "Description goes here."

                    # If the audio file doesn't have a matching image file to use as an icon, see if there's an image included in the MP3 data we can use.
                    if not fileHasIcon:
                        print("Extracting album art as icon file: " + iconFile, flush=True)
                        ffmpegCommand = "ffmpeg -y -i \"" + outputFile + "\" -an -vcodec copy \"" + iconFile + "\" >/dev/null 2>&1"
                        print(ffmpegCommand, flush=True)
                        os.system(ffmpegCommand)
                        if os.path.exists(iconFile):
                            cueRow[5] = file + ".png"
                else:
                    print("ERROR: File not converted: " + file + "." + fileType)
            elif fileType.lower() in docsToMarkdownLib.imageTypes:
                print("Processing image file: " + inputFile, flush=True)
                ffmpegCommand = "ffmpeg -y -i \"" + inputFile + "\" \"" + iconFile + "\" >/dev/null 2>&1"
                print(ffmpegCommand, flush=True)
                os.system(ffmpegCommand)
                if os.path.exists(iconFile):
                    cueRow[5] = file + ".png"
                else:
                    print("ERROR: File not converted: " + file + "." + fileType)
            else:
                print("Unprocessed file: " + inputFile)
            if os.path.exists(iconFile):
                iconImage = PIL.Image.open(iconFile)
                iconImage.thumbnail((1024,1024))
                iconImage.save(iconFile)
    N=N+1
        if not cueRow[0] == "":
            cueList.append(cueRow)

docsToMarkdownLib.putFile(args["output"] + os.sep + "index.html", docsToMarkdownLib.getFile("/etc/docs-to-markdown/audioCues/audioCuesIndex.html").replace("var resources = [];", str("var resources = " + str(cueList) + ";")).replace("<<TIMESTAMP>>",str(timestamp)).replace("<<DATETIMEFORMATTED>>",dateTimeFormatted).replace("\'", "\""))
