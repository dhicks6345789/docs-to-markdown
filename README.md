# Docs To Markdown
A collection of scripts to pre-process folders of content into a form ready for further processing with common static site generation tools ([Hugo](https://gohugo.io/), [Jekyll](https://jekyllrb.com/), [Eleventy](https://www.11ty.dev/), etc).

The scanFolders Python script acts as an overall starting point, triggering other scripts to run conversions on a folder tree containing various content. Each script should also be able to be used as a stand-alone application should you want.

## Installation
Just download / clone the Git repository.

## Requirements
These scripts are written in Python 3 and, as such, should be cross-platform. Each script might have its own set of particular requirements, including requirements for supporting applications, see the relevant script's documentation for details.

The scripts are intended to be run over a simple folder tree. They should work with pretty much anything that looks to the operating system like a local tree of folders, so if you have a utility that maps a cloud-based file system of some kind to a local path (say you're using one of the Windows Google Drive / OneDrive / Dropbox clients) you should be able to run the scripts on that path (either as input or output location) in the same way.

If you're on a Linux or MacOS system (or Windows), we can recommend [rclone](https://rclone.org/) as being an excellent way of mounting / cloning over 50 cloud provider's filesystems as a local filesystem.

## Usage
To run scanFolders on a given folder tree, just give input and output folder options:

```
scanFolders.py --input inputFolder --output outputFolder -c config.json -t jekyllTemplates
```

That will process all recognised documents in "inputFolder", applying the default behaviour to each one, and place the resulting processed files (.md Markdown files and any other resources generated) in a matching set of folders in "outputFolder". Sub-folders will be recursed into, and the output folder will be created if it doesn't already exist.

## The Scripts
- [Documents](documents/processDocuments.md)
- [FAQ](FAQ/processFAQ.md)
- [Slideshow](slideshow/processSlideshow.md)
- [Dashboard](dashboard/processDashboard.md)
- [Image Gallery](imageGallery/processImageGallery.md)

## Extending

If you want to extend the functionality of this project, just write a script that accepts the same (very simple) format of paramaeters at the command line. There is a docsToMarkdownLib Python library that contains handy functions if you happen to be writing your script in Python, but really you can write a command line application in any language you prefer.

The scripts should all work just fine from the command line, but as an added feature they might be used with the [Web Console](https://github.com/dhicks6345789/web-console) project to produce a very simple front end. Therefore, when writing additional scripts it would be best to include formatting in any output (progress / error messages, progress bars, etc) suitible for Web Console to use - see the project's page for more details.
