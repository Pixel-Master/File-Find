<p align="center">
  <img src="https://github.com/Pixel-Master/File-Find/blob/main/assets/icon.png?raw=true" height="128">
  <h1 align="center">File Find</h1>


<h3 align="center">A     file search utility that helps you find files easier.</h3>

<h4 align="center">Completely open-source and free. By Pixel-Master</h4>


[![File Find build](https://img.shields.io/github/actions/workflow/status/Pixel-Master/File-Find/File-Find.yml?branch=main&label=File%20Find%20build%20status&logo=File%20Find&style=flat-square)](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](http://www.gnu.org/licenses/gpl-3.0.html) 
[![GitLab last commit](https://img.shields.io/github/last-commit/Pixel-Master/File-Find.svg?style=flat-square)](https://github.com/Pixel-Master/File-Find/)
[![GitHub stars](https://img.shields.io/github/stars/Pixel-Master/File-Find.svg?style=flat-square&label=Stars&color=yellow)](https://github.com/Pixel-Master/File-Find/)
[![GitLab forks](https://img.shields.io/github/forks/Pixel-Master/File-Find.svg?style=flat-square&label=Fork&color=red)](https://github.com/Pixel-Master/File-Find/forks/)

#### Links: [GitHub](https://github.com/Pixel-Master/File-Find), [Website](https://pixel-master.github.io/File-Find)

![https://github.com/Pixel-Master/File-Find](https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/preview/preview_round.png?raw=true)

## Content
- [Download](#download)
- [Features](#features)
- [Building from source](#building-from-source)
  - [On macOS](#on-macos)
  - [On Linux](#on-linux)
  - [On Windows](#on-windows)
- [FAQ](#faq)
- [File Structure](#file-structure)

## Download
File Find isn't ready for Release yet Run from source or download pre-build macOS, Windows or Linux Apps from the GitHub action Page.
- [Building from Source](#building-from-source)
- [GitHub Action Page](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)

## Features

### Search options
- **Basic**
	<p align="left">
  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/File%20Find%20screenshot%20white.png?raw=true" height="250">

	* **Name**: Input needs to match the name of a file exactly, ignoring case. Also supports unix shell-style wildcards, which are not the same as regular expressions (also ignoring case).
	* **Name contains**: The name of a file must contain input, ignoring case.
    * **File Type**: Select groups of files types that should be included in search results.
    * **Directory**: The directory tree to search in. Excluding subdirectory content is currently not possibly


  

- **Properties**

  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/properties.png?raw=true" height="250">
	
	* **File contains**: Allows you to search in files. Input must be in the file content. This option can take really long. Your input is case-sensitive.
    * **Date created and modified**: Specify a date range for the date the file has been created / modified, leave at default to ignore.
    * **File size**: Input specifies file size in a range from min to max. Select the unit (Byte, Megabyte, Gigabyte...) on the right. Select "No Limit" to only set a minimum or maximum value.


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



## Building from source

### Note:

###### File Find works on Linux or Windows, but currently only in beta. Please report any errors.


### Dependencies for building
- [Python](https://python.org/) 3.9 or higher **(Python 3.12 does not work yet!)**
- [PySide6](https://pypi.org/project/PySide6/) 6.4.1 or higher
- [pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher
- [nuitka](https://pypi.org/project/nuitka/) 2.0 or higher
- **Only macOS:** [dmgbuild](https://pypi.org/project/dmgbuild/) 1.1 or higher

### Building

#### On macOS

1. Install Python:
    
    Download the installer: [here](https://www.python.org/ftp/python/3.11.6/python-3.11.6-macos11.pkg) or use

    Homebrew: `brew install python@3.11`


2. Clone the File Find repository: `git clone https://github.com/Pixel-Master/File-Find.git`


3. cd into the repository: `cd File-Find`


4. Create a virtual environment: 
   1. Create: `python3 -m venv ./venv`
   2. Activate the virtual environment: `source venv/bin/activate`


5. [Install dependencies](#dependencies-for-building): `pip3 install -r requirements.txt`


6. Build using:

`python3 build.py` 

#### On Linux

1. Install Python:
    
    With your favourite packet-manager

    E.g.: `sudo apt install python3.11`


2. Clone the File Find repository with git: `git clone https://github.com/Pixel-Master/File-Find.git`


3. cd into the repository: `cd File-Find`


4. Create a virtual environment: 
   1. Create: `python3 -m venv ./venv`
   2. Activate the virtual environment: `source venv/bin/activate`


5. [Install dependencies](#dependencies-for-building): `pip3 install -r requirements.txt`


6. Build using:

`python3 build.py` 

#### On Windows

1. Install Python:
    
    Download the installer: [here](https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe)


2. Clone the File Find repository with git: `git clone https://github.com/Pixel-Master/File-Find.git`
   or download it from GitHub


3. cd into the repository: `cd File-Find`


4. Create a virtual environment: 
   1. Create: `python -m venv venv`
   2. Activate the virtual environment: `venv\bin\activate.bat`


5. [Install dependencies](#dependencies-for-building): `pip3 install -r requirements.txt`


6. Build using:

`python build.py` 


## FAQ
Q: **What is File Find and how does it work?**

A: File Find is an open-source macOS Utility, that makes it easy to find files. To search fill in the filters you need and leave the filters you don't need empty.

Q: **Why does File Find sometimes freeze?**

A: It is possible that for example reloading files or building the UI at the end of a search can cause File Find to freeze. Just wait a few seconds!

Q: **How do you clean the cache?**

A: File Find stores the cache under `/Users/$USERNAME/Library/Application Support/File-Find/Cached Searches`. You can clean the cache with `⌘ + T` or `Tools > Clear Cache`. In the About section you can set when the cache gets cleaned automatically.

Q: **Why does File Find ask for permission for Contacts, Calenders, Photos, etc...?**

A: File Find scans the entire specified directory, even if files are excluded they are scanned first and then sorted out. 
Your photos, Calendar data, Contacts etc. are stored in a library folder, which means that File Find scans them. 
File Find does not connect to the internet, everything stays on your machine. You can also press "Do not allow", the associated files will not appear in your searches.

Q: **Why does File Find ask for permission for Downloads, Desktop, Documents, etc...?**

A: On macOS if an app scans a directory this popup will automatically appear.
If you press "Don't allow", File Find will still be able to scan those files,
but you are not going to be able to save searches in those directories

Q: **Does File Find connect to the Internet?**

A: **File Find does not connect to the Internet**, everything stays on your machine.

## File Structure

### Important files

- `File-Find.py` - Main file, execute this for running File Find

- `build.py` - Build script, requires nuitka to be installed. See [here](#building-from-source)

### UI-Files 

- `FF_Main_UI.py` - This file contains the code for the main window

- `FF_Search_UI.py` - This file contains the code for the search-results window

- `FF_Additional_UI.py` - This file contains the code for additional UI components like the PopUp windows

- `FF_About_UI.py` - This file contains the code for the About window

- `FF_Menubar.py` - Menubar for the search results, compare and duplicated window

- `FF_Settings.py` - Settings menu

### Mixed files and algorithms

- `FF_Search.py` - This file contains the code for the search engine

- `FF_Files.py` - This file contains File operations and global variables

- `FF_Duplicated.py` - This file contains the code for the 'Find duplicated' feature and it's UI

- `FF_Compare.py` - This file contains the code for the 'Compare Search' feature and it's UI

### Other

- `assets/` - Directory contains image assets for File Find

- `File Find.entitlements` - This is an entitlement file, which can be used to sandbox an app on macOS. Tough sandboxing is currently not supported.

