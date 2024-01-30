<p align="center">
  <img src="https://gitlab.com/Pixel-Mqster/File-Find/-/raw/main/assets/icon.png" height="128">
  <h1 align="center">File Find for macOS</h1>


<h3 align="center">A macOS file search utility that helps you find files easier.</h3>

<h4 align="center">Completely open-source and free.</h4>


[![File Find build](https://img.shields.io/github/actions/workflow/status/Pixel-Master/File-Find/File-Find.yml?branch=main&label=File%20Find%20build%20status&logo=File%20Find&style=flat-square)](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](http://www.gnu.org/licenses/gpl-3.0.html) 
[![GitLab last commit](https://img.shields.io/github/last-commit/Pixel-Master/File-Find.svg?style=flat-square)](https://github.com/Pixel-Master/File-Find/)
[![GitHub stars](https://img.shields.io/github/stars/Pixel-Master/File-Find.svg?style=flat-square&label=Stars&color=yellow)](https://github.com/Pixel-Master/File-Find/)
[![GitLab forks](https://img.shields.io/github/forks/Pixel-Master/File-Find.svg?style=flat-square&label=Fork&color=red)](https://github.com/Pixel-Master/File-Find/forks/)

#### Automatic Builds, Bug reports and Pull request on: [GitHub](https://github.com/Pixel-Master/File-Find)

![](https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/preview/preview_without_background2.png?raw=true)

## Content
- [Features](#features)
- [FAQ](#faq)
- [Download](#download)
- [File Structure](#file-structure)
- [Running from Source](#running-from-source)
- [Building File Find.app](#building-file-findapp)

## Features

### Search options
- **Basic**
	<p align="left">
  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/File%20Find%20screenshot%20dark.png?raw=true" height="250">

	* **Name**: Input needs to match the name of a file exactly, ignoring case. Also supports unix shell-style wildcards, which are not the same as regular expressions (also ignoring case).
	* **Name contains**: The name of a file must contain input, ignoring case.
    * **File Type**: Select groups of files that should be included in search results.
    * **Directory**: The Directory to search in.
    * 
- **Properties**

  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/properties.png?raw=true" height="250">
	
	* **File contains**: Allows you to search in files. Input must be in the file content. This option can take really long. Input is case-sensitive.
    * **Date created and modified**: Specify a date range for the date the file has been created/ modified, leave at default to ignore.
    * **File size**: Input specifies file size in Mega Bytes (MB) in a range from min to max.


- **Advanced**

  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/advanced.png?raw=true" height="250">
  
    * **Search in system files**: Toggle to include files in the system and library folders.
	* **File extension**: Input needs to match the file extension (file type) without the ".", ignoring case.
    * **Only search for folders or files**: Toggle to only include folders or files in the search results.

- **Sorting**

  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/sorting.png?raw=true" height="250">
	
	* **None** (fastest)
	* **File size**
	* **File name**
	* **Date modified**
	* **Date created**
	* **Path**
	* **Reverse Sort**: Reverse the sorted search results.

### Dark / Light mode 

![](https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/File%20Find%20screenshot%20white.png?raw=true)

![](https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/File%20Find%20screenshot%20dark.png?raw=true)



### Other
	
- Export search results as a **plain text file (.txt)** or as a reloadable **File Find Search (.FFSearch)**

- Compare two searches and search for differences


## FAQ
Q: **What is File Find and how does it work?**

A: File Find is an open-source macOS Utility, that makes it easy to find files. To search fill in the filters you need and leave the filters you don't need empty.

Q: **Why does File Find sometimes freeze?**

A: It is possible that for example reloading files or building the UI at the end of a search can cause File Find to freeze. Just wait a few seconds!

Q: **How do you clean the cache?**

A: File Find stores the cache under `/Users/$USERNAME/Library/Application Support/File-Find/Cached Searches`. You can clean the cache with `⌘ + T` or `Tools > Clear Cache`. In the About section you can set when the cache gets cleaned automatically.

Q: **Why does File Find ask for permission for Contacts, Calenders, Photos, etc...?**

A: File Find scans the entire specified directory, even if files are excluded they are scanned first and then sorted out. 
Your photos, calendar data, contacts etc. are stored in a library folder, which means that File Find scans them. 
File Find does not connect to the internet, everything stays on your machine. You can also press "Do not allow", the associated files will not appear in your searches.

Q: **Why does File Find ask for permission for Downloads, Desktop, Documents, etc...?**

A: On macOS if an app scans a directory this popup will automatically appear.
If you press "Don't allow", File Find will still be able to scan those files,
but you are not going to be able to save searches in those directories

Q: **Does File Find connect to the Internet?**

A: **File Find does not connect to the Internet**, everything stays on your machine.

## Download
File Find isn't ready for Release yet Run from source or download pre-build macOS Apps from the GitHub action Page.
- [Running from Source](#running-from-source)
- [Building File Find.app](#building-file-findapp)
- [GitHub Action Page](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)

## File Structure

- `File-Find.py` - Main file, execute this for running File Find

- `FF_Main_UI.py` - This file contains the code for the main window

- `FF_Search_UI.py` - This file contains the code for the search-results window

- `FF_Additional_UI.py` - This file contains the code for additional UI components like the PopUp windows

- `FF_Help_UI.py` - This file contains the code for the About window

- `FF_Search.py` - This file contains the code for the search engine

- `FF_Files.py` - This file contains File operations and global variables

- `FF_Compare.py` - This file contains the code for the 'Compare Search' feature

- `build.py` - Build script, requires nuitka to be installed. See [here](#building-file-findapp)

- `assets/` - Directory contains image assets for File Find

## Running from source

### Note:

###### File Find won't work properly on Linux or Windows, because the UI displays different depending on the operating-system and some features depend on the system.


### Dependencies for running
- [Python](https://python.org/) 3.9 or higher **(Python 3.12 does not work yet!)**
- [PySide 6](https://pypi.org/project/PySide6/) 6.4 or higher
- [pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher

### Building
1. Install Python:
    
    Download the installer: https://python.org/download or use

    Homebrew: `brew install python@3.11`


2. Clone the File Find Repository: `git clone https://github.com/Pixel-Master/File-Find.git`


3. cd into the repository: `cd File-Find`


4. [Install dependencies](#dependencies-for-running): `pip3 -r requierments.txt`


5. Run:

`python3 File-Find.py` 


## Building File Find.app

### Note:

###### File Find won't work properly on Linux or Windows, because the UI displays different depending on the operating-system and some features depend on the system. 


### Dependencies for building
- [Python](https://python.org/) 3.9 or higher **(Python 3.12 does not work yet!)**
- [PySide6](https://pypi.org/project/PySide6/) 6.4.1 or higher
- [pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher
- [nuitka](https://pypi.org/project/nuitka/) 2.0 or higher
- [create-dmg](https://github.com/create-dmg/create-dmg) 1.1 or higher

### Building
1. Install Python:
    
    Download the installer: [here](https://www.python.org/ftp/python/3.11.6/python-3.11.6-macos11.pkg) or use

    Homebrew: `brew install python@3.11`


2. Clone the File Find repository: `git clone https://github.com/Pixel-Master/File-Find.git`


3. cd into the repository: `cd File-Find`


4. [Install python dependencies](#dependencies-for-building): `pip3 install -r requirements.txt`


5. Build using:

`python3 build.py` 