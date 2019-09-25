# DocsToMarkdown
Converts a folder tree of Word / Excel files (compatability is with those produced by Mircosoft Office / Office 365, exported from Google Docs / Sheets or, hopefully, pretty much any other tool) to the Govspeak varient of Markdown as specified by GOV.UK, or to CSV if appropriate. The output is intended to be used as the input for static site generation tools such as Jeykll, Hugo or Hyde, and various options / assumtions exist to ensure the files produced are suitible for those tools.

## Requirements
This utility depends on the Ruby-based utility Pandoc, version 2.7 or higher, released Monday, 4th March 2019. Earlier versions (as generally packaged in Debian's repositories, for instance) have a bug which stops them parsing DOCX files created with Office 365.

## Installation
Just run docsToMarkdown.py, giving input and output folder options, e.g.:

docsToMarkdown.py -i inputDocs -o outputFolder

The above basic usage will process all recognised documents in the "inputDocs" folder, applying the default behaviour to each one, and place the resulting Markdown file in a matching set of files in the "outputFolder" folder. So, if you had a basic folder structure, like so:

inputDocs/index.docx
inputDocs/about.docx
inputDocs/contact.docx
inputDocs/data.xlsx

The above command would produce:

outputFolder/index.html
outputFolder/about.html
outputFolder/contact.html
outputFolder/data.html

Basic formatting from Word documents should be retained - titles, bold / italic text, bullet points, tables and similar features.

You can better define the conversion process with a JSON-formatted config file. Options are:

global:baseURL
Sets a global variable later passed to various functions to define the base URL of your site.

function:filesToMarkdown
inputFiles:[]
outputFile:""
frontMatter:{"":""}
Takes the given input files and converts them, using Pandoc, to Markdown. Note that you can define multiple input files for one output Markdown file. You can also define front matter fields that will be inserted at the head of the Markdown document after conversion.

"function":"filesToCSV", "inputFiles":["accessDisputesCommitteeIndex/TTPDeterminations/determinations.xlsx"], "outputFile":"_data/accessDisputesCommitteeIndex/TTPDeterminations/determinations.csv", "jekyllHeaders":"true"}

Takes the given input Excel files and converts them to CSV. Note that you can define multiple input files for the one output CSV file. If you are using these CSV files as data sources in Jekyll's _data folder you will need to have Jekyll-style headers placed at the head of the files, so set the "jekyllHeaders" option to "true".

function":"copyFolder", "src":"accessDisputesCommitteeIndex/TTPDeterminations/Determinations", "dest":"accessDisputesCommitteeIndex/TTPDeterminations/Determinations"},
Simply copies a folder in the input folder to a folder in the output folder. Note that the roots of both locations are defined by the input and output options given at runtime, these are both relative arguments. The copy process checks for updates before copying, no file is copied unless the previous version is changed - this should make this process suitible for use in copying files from network-mounted storage repositories.
    
    
    
Finally, you can also define a "templates" folder that will be copied over to the output folder along with the Markdown output, this is to accomodate applications such as Jekyll that expect a certain folder structure.

docsToMarkdown.py -c config.json -i inputDocs -o jekyll -t jekyllTemplates
