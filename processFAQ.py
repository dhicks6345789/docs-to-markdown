import os
import sys

inputFolder = sys.argv[1]
outputFolder = sys.argv[2]

print("processFAQ: " + inputFolder + " to " + outputFolder)
for inputItem in os.listdir(inputFolder):
    if inputItem.rsplit(".", 1)[1].lower() in ["docx", "doc"]:
        print("Convert to Markdown: " + inputFolder + os.sep + inputItem)
    elif inputItem.rsplit(".", 1)[1].lower() in ["mp4"]:
        # Use FFmpeg to set the size and format of any FAQ videos.
        processVideo = False
        inputItemDetails = os.stat(inputFolder + os.sep + inputItem)
        outputItem = inputItem.rsplit(".", 1)[0] + ".webm"
        if os.path.isfile(outputFolder + os.sep + inputItem):
            outputItemDetails = os.stat(outputFolder + os.sep + outputItem)
            if not inputItemDetails.st_mtime == outputItemDetails.st_mtime:
                processVideo = True
        else:
            processVideo = True
            
        if processVideo:
            print("STATUS: Processing FAQ video: " + inputFolder + os.sep + inputItem + " to " + outputFolder + os.sep + outputItem)
            print("inputItemDetails: " + inputItemDetails.st_mtime)
            print("outputItemDetails: " + outputItemDetails.st_mtime)
            
            # Figure out the video's dimensions.
            videoDimensions = os.popen("ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x " + inputFolder + os.sep + inputItem).read().strip()
            videoWidth = int(videoDimensions.split("x")[0])
            videoHeight = int(videoDimensions.split("x")[1])
            
            # Crop the video to a square, centred in the middle, then scale the dimensions to 240x240.
            # Also, normalise the audio - see: http://johnriselvato.com/ffmpeg-how-to-normalize-audio/
            os.system("ffmpeg -i " + inputFolder + os.sep + inputItem + " -filter:v crop=" + str(videoHeight) + ":" + str(videoHeight) + ":" + str(int((videoWidth - videoHeight) / 2)) + ":0,scale=240:240,setsar=1 -filter:a loudnorm=I=-16:LRA=11:TP=-1.5 /tmp/faq.webm > /dev/null 2>&1")
            os.system("mv /tmp/faq.webm " + outputFolder + os.sep + outputItem)
            os.utime(outputFolder + os.sep + outputItem, (inputItemDetails.st_atime, inputItemDetails.st_mtime))
