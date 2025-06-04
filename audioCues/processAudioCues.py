# A script to generate an audio cues page (a folder containing index.html and a set of normalised assets) from a folder of assets (audio clips).

# Standard libraries.
import os
import io
import re
import sys
import shutil
import datetime

# The Pillow image-handling library.
import PIL

# The JSON-handling library.
import html

# The eyeD3 library for getting information from MP3 files.
import eyed3

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



def systemPrint(theCommandLine):
    #print(theCommandLine, flush=True)
    os.system(theCommandLine)

# Check through items in the given input folder, recursing into sub-folders.
# Produces an array (in the global "files" variable) containing tuples of file names and an array of extensions found.
files = {}
fileTitles = {}
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
            fileTitle = fileName.strip()
            if re.match("^[0-9]+ *- *.*", fileTitle) != None:
                fileTitle = fileTitle.split("-", 1)[1].strip()
            if not theSubFolder == "":
                fileName = theSubFolder + os.sep + fileName
            if len(fileSplit) == 2:
                fileType = fileSplit[1]
            if not fileName in files.keys():
                files[fileName] = []
            if not fileTitle in fileTitles.keys():
                fileTitles[fileTitle] = []
            files[fileName].append(fileType)
            fileTitles[fileTitle].append(fileType)
listFileNames("")

print(files, flush=True)
print(fileTitles, flush=True)

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

# Clear out any old icon files from the output folder.
for outputItem in os.listdir(args["output"]):
    if outputItem.endswith(".png"):
        systemPrint("rm \"" + args["output"] + os.sep + outputItem + "\"")

cueList = [["Filename", "Title", "Description", "TrimLeft", "TrimRight", "Icon"]]
outputFolder = docsToMarkdownLib.normalisePath(args["output"])
print("STATUS: processAudioCues - processing found audio files.", flush=True)
outputFiles = []
for file in files:
    fileTitle = file.strip()
    if re.match("^[0-9]+ *- *.*", fileTitle) != None:
        fileTitle = fileTitle.split("-", 1)[1].strip()
    fileHasAudio = False
    fileHasIcon = False
    fileIcon = ""
    for fileType in files[file]:
        if fileType.lower() in docsToMarkdownLib.audioTypes:
            fileHasAudio = True
        if fileType.lower() in docsToMarkdownLib.imageTypes:
            fileHasIcon = True
            fileIcon = file + "." + fileType
    # If the audio file doesn't have a exactly matching named image file to use as an icon, see if there's a matching file title one instead.
    if not fileHasIcon:
        for fileType in fileTitles[fileTitle]:
            if fileType.lower() in docsToMarkdownLib.imageTypes:
                fileHasIcon = True
                fileIcon = fileTitle + "." + fileType
    if fileHasAudio:
        cueRow = ["", "", "", 0, 0, ""]
        print("File icon: " + fileIcon)
        for fileType in files[file]:
            inputFile = inputFolder + os.sep + file + "." + fileType
            inputFileTitle = inputFolder + os.sep + fileTitle + "." + fileType
            outputFile = outputFolder + os.sep + file + ".mp3"
            iconFile = outputFolder + os.sep + file + ".png"
            if fileType.lower() in docsToMarkdownLib.audioTypes:
                outputFile = outputFolder + os.sep + file + ".mp3"
                if not os.path.exists(outputFile) or not os.path.getmtime(inputFile) == os.path.getmtime(outputFile):
                    print("Processing audio file: " + inputFile, flush=True)
                    # Process the input audio file with FFMPEG and write out to an MP3, so the output audio is in a consistant format. Filters used:
                    #     silenceremove - remove any silence at the start of the track.
                    #     compand - apply some Dynamic Range Compression to the audio to better level out any differences between low and high volume parts of the track.
                    #     dynaudnorm - set the loudest part of the track to max volume, try and have a reasonably consistant sound level.
                    systemPrint("ffmpeg -y -i \"" + inputFile + "\" -filter:a \"silenceremove=1:0:-45dB,compand=0|0:1|1:-90/-900|-70/-70|-30/-9|0/-3:6:0:0:0,dynaudnorm=peak=1\" -vn -ar 44100 -ac 2 -b:a 192k \"" + outputFile + "\" >/dev/null 2>&1")
                    # Set file modification time so we can skip the conversion next time if the input file hasn't changed.
                    systemPrint("touch -r \"" + inputFile + "\" \"" + outputFile + "\" >/dev/null 2>&1")
                if os.path.exists(outputFile):
                    cueRow[0] = file + ".mp3"
                    outputFiles.append(cueRow[0])
                    cueRow[1] = fileTitle
                    cueRow[2] = ""
                    audioFileData = eyed3.load(inputFile)
                    if not audioFileData == None:
                        if not audioFileData.tag.title == None:
                            cueRow[1] = html.escape(audioFileData.tag.title)
                        if len(audioFileData.tag.comments) > 0:
                            cueRow[2] = audioFileData.tag.comments[0].text
                    
                    # If the audio file doesn't have a matching image file to use as an icon, see if there's an image included in the MP3 data we can use.
                    if not fileHasIcon:
                        print("Extracting album art as icon file: " + iconFile, flush=True)
                        systemPrint("ffmpeg -y -i \"" + inputFile + "\" -an -vcodec copy \"" + iconFile + "\" >/dev/null 2>&1")
                        if os.path.exists(iconFile):
                            cueRow[5] = file + ".png"
                            outputFiles.append(cueRow[5])
                else:
                    print("ERROR: File not converted: " + file + "." + fileType)
            elif fileType.lower() in docsToMarkdownLib.imageTypes:
                if os.path.exists(inputFileTitle + "." + fileType):
                    print("Processing image file: " + inputFileTitle, flush=True)
                    systemPrint("ffmpeg -y -i \"" + inputFileTitle + "\" \"" + iconFile + "\" >/dev/null 2>&1")
                else:
                    print("Processing image file: " + inputFile, flush=True)
                    systemPrint("ffmpeg -y -i \"" + inputFile + "\" \"" + iconFile + "\" >/dev/null 2>&1")
                if os.path.exists(iconFile):
                    cueRow[5] = file + ".png"
                    outputFiles.append(cueRow[5])
                else:
                    print("ERROR: File not converted: " + file + "." + fileType)
            else:
                print("Unprocessed file: " + inputFile)

            # If we have an icon file, make sure it's a square, thumbnailed image.
            if os.path.exists(iconFile):
                iconImage = PIL.Image.open(iconFile)
                iconWidth, iconHeight = iconImage.size
                cropLeft = 0
                cropRight = iconWidth
                cropTop = 0
                cropBottom = iconHeight
                if iconWidth > iconHeight:
                    cropLeft = int((iconWidth - iconHeight) / 2)
                    cropRight = iconWidth - cropLeft
                else:
                    cropTop = int((iconHeight - iconWidth) / 2)
                    cropBottom = iconHeight - cropTop
                croppedIcon = iconImage.crop((cropLeft, cropTop, cropRight, cropBottom))
                croppedIcon.thumbnail((1024,1024))
                croppedIcon.save(iconFile)
        if not cueRow[0] == "":
            cueList.append(cueRow)

# Clear out any extranious files from the output folder (left over from previous runs / changes).
for outputItem in os.listdir(args["output"]):
    if not outputItem in outputFiles:
        systemPrint("rm \"" + args["output"] + os.sep + outputItem + "\"")

# Write the index.html file for the zip-ed version.
indexHTML = docsToMarkdownLib.getFile("/etc/docs-to-markdown/audioCues/audioCuesIndex.html").replace("var resources = [];", str("var resources = " + str(cueList) + ";")).replace("<<TIMESTAMP>>",str(timestamp)).replace("<<DATETIMEFORMATTED>>",dateTimeFormatted).replace("\'", "\"")
docsToMarkdownLib.putFile(args["output"] + os.sep + "index.html", indexHTML.replace("/bootstrap/","bootstrap/").replace("/bootstrap-icons/","bootstrap-icons/").replace("/popper/","popper/"))

# Create the zip file.
print("STATUS: processAudioCues - creating zip file for local download...", flush=True)
os.system("cp /etc/docs-to-markdown/audioCues/silence.mp3 www")
os.system("cp -r ../../www/popper www")
os.system("cp -r ../../www/bootstrap www")
os.system("cp -r ../../www/bootstrap-icons www")
os.system("cd " + args["output"] + "; zip -r .." + os.sep + "audioCues.zip * >/dev/null 2>&1")
os.system("mv audioCues.zip " + args["output"])
os.system("cd " + args["output"] + "; rm -rf popper; rm -rf bootstrap; rm -rf bootstrap-icons")

# Re-write index.html as the final version.
docsToMarkdownLib.putFile(args["output"] + os.sep + "index.html", indexHTML)
