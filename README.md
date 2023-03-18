<p align="center">
  <img src="https://gitlab.com/Pixel-Mqster/File-Find/-/raw/main/assets/icon.png" height="128">
  <h1 align="center">File Find for macOS</h1>


<h3 align="center">A macOS file search utility that helps you find files easier.</h3>

<h4 align="center">Completely open-source and free.</h4>


[![File Find build](https://img.shields.io/github/actions/workflow/status/Pixel-Master/File-Find/File-Find.yml?branch=main&label=File%20Find%20build%20status&logo=File%20Find&style=flat-square)](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](http://www.gnu.org/licenses/gpl-3.0.html) 
[![GitLab last commit](https://img.shields.io/gitlab/last-commit/Pixel-Mqster/File-Find.svg?style=flat-square)](https://gitlab.com/Pixel-Mqster/File-Find/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/Pixel-Master/File-Find.svg?style=flat-square&label=Stars&color=yellow)](https://gitlab.com/Pixel-Mqster/File-Find/)
[![GitLab forks](https://img.shields.io/gitlab/forks/Pixel-Mqster/File-Find.svg?style=flat-square&label=Fork&color=red)](https://gitlab.com/Pixel-Mqster/File-Find/-/forks/new)

#### Automatic Builds on: [GitHub](https://github.com/Pixel-Master/File-Find), Issues and Pull Requests on: [GitLab](https://gitlab.com/Pixel-Mqster/File-Find)

## Content
- [Features](#features)
- [FAQ](#faq)
- [Download](#download)
- [File Structure](#file-structure)
- [Running from Source](#running-from-source)
- [Building File Find.app](#building-file-findapp)
- [Roadmap](#roadmap)


## Features
- Select filter which files to include:
	* Name
	* Name contains
	* File extension
	* Search in system files
	* Directory to search in
	* File size
	* Only find folders or files
    * Wildcard (Unix shell-style wildcards)
    * File contains
    * Date created and modified

- Export search results as a **plain text file (.txt)** or as a reloadable **File Find Search (.FFSearch)**


- Dark-mode


- Options for found files:
	* Show in Finder
	* Open
	* Basic file info
    * File hashes


- Sort Results:
	* File size
	* File name
	* Date modified
	* Date created


- Generate Terminal command from filters, supports:
	* Name
	* In Name
	* File Ending
    * Wildcard

- Compare two searches and search for differences

- View file hashes (md5, sha1, sha265)

## FAQ
Q: **What is File Find and how does it work?**

A: File Find is an open-source macOS Utility, that makes it easy to find files. To search fill in the filters you need and leave the filters you don't need empty.

Q: **Why does File Find sometimes freeze?**

A: It is possible that for example reloading files or building the UI at the end of a search can cause File Find to freeze. Just wait a minute!

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

- `build.py` - Build script, requires py2app installed. See [here](#building-file-findapp)

- `assets/` - Directory contains image assets for File Find

## Running from source

### Note:

###### File Find won't work properly on Linux or Windows, because the UI displays different depending on the OS and some Features depends on the system. 


### Dependencies for running
- [Python](https://python.org/) 3.9 or higher
- [PyQt 6](https://pypi.org/project/PyQt6/) 6.4 or higher
- [pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher

### Building
1. Install Python:
    
    Download the installer: https://python.org/download or use

    Homebrew: `brew install python@3.11`


2. Clone the File Find Repository: `git clone https://gitlab.com/Pixel-Mqster/File-Find.git`


3. cd into the repository: `cd File-Find`


4. [Install dependencies](#dependencies-for-running): `pip3 -r requierments.txt`


5. Run:

`python3 File-Find.py` 


## Building File Find.app

### Note:

###### File Find won't work properly on Linux or Windows, because the UI displays different depending on the OS and some Features depends on the system. 


### Dependencies for building
- [Python](https://python.org/) 3.9 or higher
- [PyQt 6](https://pypi.org/project/PyQt6/) 6.4 or higher
- [pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher
- [py2app](https://pypi.org/project/py2app/) 5.6.2 or higher
- [create-dmg](https://github.com/create-dmg/create-dmg) (optional for dmg building) 1.1 or higher

### Building
1. Install Python:
    
    Download the installer: https://python.org/download or use

    Homebrew: `brew install python@3.11`


2. Clone the File Find repository: `git clone https://gitlab.com/Pixel-Mqster/File-Find.git`


3. cd into the repository: `cd File-Find`


4. [Install python dependencies](#dependencies-for-building): `pip3 install -r requirements.txt && pip3 install py2app`


5. Build using:

`python3 build.py` 


## Roadmap
1. [x] UI:
2. [x] Exporting and Importing Searches:
3. [x] Caching:
4. [ ] Multithreading:
    1. [x] UI using different thread as Search engine
    2. [x] Hashing with different Threads
    3. [ ] Scanning trough different threads
    4. [ ] Indexing trough different threads
5. [x] Sorting:
6. [ ] Searching:
    1. [x] Name
    2. [x] In Name
    3. [x] File Ending
    4. [x] Search in System Files
    5. [x] Directory to search in
    6. [x] Search only for Files or Folders
    7. [ ] Exclude Sub-folders
    8. [x] Contains
    9. [ ] Search with root privileges
    10. [x] Regex (used fn match instead (Unix shell-style wildcards))
    11. [x] Date Modified
    12. [x] Date Created
    13. [x] Excluded Files
7. [ ] Language
   1. [x] Language UI
   2. [ ] Languages apply
   3. [ ] Languages:
      1. [x] English
      2. [ ] German
      3. [ ] French
      4. [ ] Spanish
      5. [ ] Chinese
8. [ ] Compatible with Linux and Windows?
