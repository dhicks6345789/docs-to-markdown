#!/usr/bin/python

# Standard libraries.
import os
import re
import sys
import shutil
import zipfile

# The python-docx library, for manipulating DOCX files.
# Importantly, when installing with pip, that's not the "docx" library, that's an earlier version - do "pip install python-docx".
#import docx

# We use Pandas to import Excel / CSV files for configuration details.
import pandas
