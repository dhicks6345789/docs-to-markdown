# A script to generate an audio cues page (a folder containing index.html and a set of normalised assets) from a folder of assets (audio clips).

# Standard libraries.
import os
import io
import re
import sys
import json
import shutil
import datetime

# The Pillow image-handling library.
import PIL

# The Pandas data-handling library.
import pandas

# A library to get favicons from websites. See:
# https://github.com/AlexMili/extract_favicon/
import extract_favicon

# Our own Docs To Markdown library.
import docsToMarkdownLib



# Returns either the element of the row given by the index, or an empty string if that item doesn't exist.
def itemOrBlank(theRow, theIndex):
    if theRow.shape[0] > theIndex:
        return theRow[theIndex]
    return ""

# Do a Javascript-style (>>>) unsigned right shift, treating the input number as if it is a 32-bit unsigned integer.
def unsigned_right_shift(theNum, theShift):
    # Apply mask to ensure the number is treated as unsigned, then perform the right shift.
    return (theNum & 0xFFFFFFFF) >> theShift

# Do a Javascript-style "imul" operation: multiply two numbers as if they are both 32-bit unsigned integers.
def imul(a, b):
    return (a*b) & 0xFFFFFFFF
    
# Generate a simple "cyrb53" hash from a given string. Non-cryptographic, we're just using
# this hash to name favicon images. See the original Javascript version: https://stackoverflow.com/a/52171480/20530257
# And the Python conversion: https://stackoverflow.com/a/79643222/20530257
def cyrb53(theStr, seed=0):
    h1 = 0xdeadbeef ^ seed
    h2 = 0x41c6ce57 ^ seed
    for i,ch in enumerate(theStr):
        h1 = imul(h1 ^ ord(ch), 2654435761)
        h2 = imul(h2 ^ ord(ch), 1597334677)
    h1  = imul(h1 ^ unsigned_right_shift(h1 , 16), 2246822507)
    h1 ^= imul(h2 ^ unsigned_right_shift(h2 , 13), 3266489909)
    h2  = imul(h2 ^ unsigned_right_shift(h2 , 16), 2246822507)
    h2 ^= imul(h1 ^ unsigned_right_shift(h1 , 13), 3266489909)
    return 4294967296 * (2097151 & h2) + (h1 & 0xFFFFFFFF)



# Get a timestamp of when we started.
dateTimeNow = datetime.datetime.now()
timestamp = int(round(dateTimeNow.timestamp()))
dateTimeFormatted = dateTimeNow.strftime("%d-%m-%Y, %H:%M:%S")

# Get any arguments given via the command line.
args = docsToMarkdownLib.processCommandLineArgs(defaultArgs={"processAudio":"true"}, requiredArgs=["input","output"])

print("STATUS: processStartScreen: " + args["input"] + " to " + args["output"], flush=True)
print("Timestamp: " + str(timestamp) + ", Date / Time: " + dateTimeFormatted, flush=True)

# Make sure the output folder exists.
os.makedirs(args["output"], exist_ok=True)

inputFolder = docsToMarkdownLib.normalisePath(args["input"])
print("Input folder: " + inputFolder, flush=True)

dataTuples = []
for inputItem in os.listdir(inputFolder):
    frameTitle = inputItem.rsplit(".", 1)
    inputItemPath = inputFolder + os.sep + inputItem
    if inputItem.endswith(".xls") or inputItem.endswith(".xlsx"):
        dataFrameMap = pandas.read_excel(inputItemPath, sheet_name=None)
        for dataFrameName in dataFrameMap:
            dataTuples.append((dataFrameName, dataFrameMap[dataFrameName]))
    elif inputItem.endswith(".csv"):
        dataTuples.append((frameTitle, pandas.read_csv(inputItemPath)))

resources = []
for dataTuple in dataTuples:
    resourceTable = [["URL", "Title", "Description", "Icon"]]
    for index, row in dataTuple[1].iterrows():
        URL = itemOrBlank(row, 0)
        print(URL, flush=True)
        URLHash = str(cyrb53(URL)) + str(cyrb53(URL[::-1]))
        iconFilename = "www" + os.sep + URLHash + ".png"
        print(URLHash, flush=True)
        title = itemOrBlank(row, 1)
        description = itemOrBlank(row, 2)
        icon = itemOrBlank(row, 3)
        if icon == "":
            downloadIcon = True
            if os.path.exists(iconFilename):
                downloadIcon = False
            if downloadIcon:
                print("Item " + title + " - trying to retreive / refresh favicon...", flush=True)
                bestFavicon = None
                try:
                    bestFavicon = extract_favicon.get_best_favicon(URL)
                except ValueError:
                    print("Favicon - ValueError raised.", flush=True)
                if bestFavicon:
                    print("Best favicon URL:" + bestFavicon.url, flush=True)
                    print("Favicon dimensions:" + str(bestFavicon.width) + "x" + str(bestFavicon.height), flush=True)
                    print(bestFavicon.url, bestFavicon.valid, bestFavicon.width, bestFavicon.height, bestFavicon.image, flush=True)
                    bestFavicon.image.thumbnail((256, 256))
                    bestFavicon.image.save(iconFilename, "PNG")
                    icon = URLHash + ".png"
                else:
                    #favicon = from_google(URL)
                    bestFavicon = extract_favicon.get_best_favicon(URL, strategy = ["duckduckgo", "google"])
                    print(bestFavicon.url, bestFavicon.valid, bestFavicon.width, bestFavicon.height, bestFavicon.image, flush=True)
                    #print("No valid favicon found for this URL.", flush=True)
        resourceTable.append([URL, title, description, icon])
    resource = (dataTuple[0], resourceTable)
    resources.append(resource)

# Write the index.html file.
indexHTML = docsToMarkdownLib.getFile("/etc/docs-to-markdown/startScreen/startScreenIndex.html")
indexHTML = indexHTML.replace("var resources = [];", "var resources = " + json.dumps(resources) + ";")
indexHTML = indexHTML.replace("<<TIMESTAMP>>", str(timestamp))
indexHTML = indexHTML.replace("<<DATETIMEFORMATTED>>", dateTimeFormatted)
indexHTML = indexHTML.replace("\'", "\"")
docsToMarkdownLib.putFile(args["output"] + os.sep + "index.html", indexHTML)
