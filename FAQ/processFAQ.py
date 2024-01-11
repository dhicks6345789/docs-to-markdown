import os
import sys

# Our own Docs To Markdown library.
import docsToMarkdownLib

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]

print("processFAQ: " + inputFolder + " to " + outputFolder, flush=True)
for inputItem in os.listdir(inputFolder):
    fileType = inputItem.rsplit(".", 1)[1].upper()
    if fileType in ["DOCX", "DOC"]:
        commandLine = "python3 .." + os.sep + "processDOCFile.py \"" + inputFolder + os.sep + inputItem + "\" \"" + outputFolder + "\""
        print("ProcessFAQ - running: " + commandLine, flush=True)
        os.system(commandLine)
    elif fileType in ["MP4"]:
        # Use FFmpeg to set the size and format of any FAQ videos.
        outputItem = inputItem.rsplit(".", 1)[0] + ".webm"
        if not docsToMarkdownLib.checkModDatesMatch(inputFolder + os.sep + inputItem, outputFolder + os.sep + outputItem):
            print("STATUS: Processing FAQ video: " + inputFolder + os.sep + inputItem + " to " + outputFolder + os.sep + outputItem, flush=True)
            
            # Figure out the video's dimensions.
            videoDimensions = os.popen("ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x " + inputFolder + os.sep + inputItem).read().strip()
            videoWidth = int(videoDimensions.split("x")[0])
            videoHeight = int(videoDimensions.split("x")[1])
            
            # Crop the video to a square, centred in the middle, then scale the dimensions to 240x240.
            # Also, normalise the audio - see: http://johnriselvato.com/ffmpeg-how-to-normalize-audio/
            os.system("ffmpeg -i " + inputFolder + os.sep + inputItem + " -filter:v crop=" + str(videoHeight) + ":" + str(videoHeight) + ":" + str(int((videoWidth - videoHeight) / 2)) + ":0,scale=240:240,setsar=1 -filter:a loudnorm=I=-16:LRA=11:TP=-1.5 /tmp/faq.webm > /dev/null 2>&1")
            os.system("mv /tmp/faq.webm " + outputFolder + os.sep + outputItem)
            
            docsToMarkdownLib.makeModDatesMatch(inputFolder + os.sep + inputItem, outputFolder + os.sep + outputItem)
