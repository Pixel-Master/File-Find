<p align="center">
  <img src="https://gitlab.com/Pixel-Mqster/File-Find/-/raw/main/assets/icon.png" height="128">
  <h1 align="center">File Find for macOS</h1>


<h3 align="center">A macOS UI Utility that helps you find Files easier.</h3>

[![File Find](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml/badge.svg?branch=main)](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)


## Content
- [Features](#features)
- [FAQ](#faq)
- [Download](#download)
- [Running from Source](#running-from-source)
- [Building File Find.app](#building-file-findapp)
- [Roadmap](#roadmap)


## Features
- Choose Filter which Files to include:
	* Name
	* In Name
	* File Ending
	* Search in System Files
	* Directory to search in
	* File Size
	* Search for Folders
    * Fn-match (Unix shell-style wildcards)
    * Search for File Content
    * Date Created and Modified
- Exclude Folders
- Search for Files and export Searches
- Dark-mode
- Choose options for Files:
	* Show in Finder
	* Open
	* Copy Path/File
- Sort Results:
	* Size
	* File Name
	* Date Modified
	* Date Created
- Reverse Results

- Generate Terminal command from Filters, supports:
	* Name
	* In Name
	* File Ending
    * Fn-match

- View File Hashes (md5, sha1, sha265)

## FAQ
Q: **What is File Find and how does it work?**

A: File Find is an open-source macOS Utility, that makes it easy to find Files. To search fill in the filters you need and leave the filters you don't need empty.

Q: **Why does File Find sometimes freeze?**

A: It is possible that for example reloading Files or Building the UI at the end of a search can cause File Find to freeze. Just wait a minute!

Q: **How to clean the Cache?**

A: File Find is saving the cache under `/Users/$USERNAME/Library/Application Support/File-Find/Cached Searches`. The Cache gets cleaned up on start up, that means to clean the cache just restart File Find

Q: **Why does File Find ask for permission for Contacts, Calenders, Photos, Downloads, etc...?**

A: File Find scans the entire specified directory, even if files are excluded they are scanned first and then sorted out. 
Your photos, calendar data, contacts etc. are stored in a library folder, which means that File Find scans them. 
**File Find does not connect to the internet**, everything stays on your machine. If you are still uncomfortable, you can also press "Do not allow", the associated files will not appear in your searches. **If File Find asks for your Downloads or Desktop folder, you can decline, File Find will still be able to scan those files.**

## Download
File Find isn't ready for Release yet Run from source or download pre-build macOS Apps from the GitHub action Page.
- [Running from Source](#running-from-source)
- [Building File Find.app](#building-file-findapp)
- [GitHub Action Page](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)


## Running from Source

### Note:

###### File Find won't work properly on Linux or Windows, because the UI displays different depending on the OS and some Features depends on the system. 


### Dependencies for running
- [Python](https://python.org/) 3.9 or higher
- [PyQt 6](https://pypi.org/project/PyQt6/) 6.4 or higher
- [pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher


1. Install Python:

    Download the installer: https://python.org/download or use

    Homebrew: `brew install python@3.11`

2. Install PyQt6 and pyperclip with pip:
`pip3 install PyQt6 pyperclip`

### Running
1. Clone the File Find Repository: `git clone https://gitlab.com/Pixel-Mqster/File-Find.git`
2. cd into the repository: `cd File-Find`
3. [Install dependencies](#dependencies-for-running)
4. Run:

`python3 File-Find.py` 

## Building File Find.app

### Note:

###### File Find won't work properly on Linux or Windows, because the UI displays different depending on the OS and some Features depends on the system. 


### Dependencies for building
- [Python](https://python.org/) 3.9 or higher
- [PyQt 6](https://pypi.org/project/PyQt6/) 6.4 or higher
- [pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher
- [py2app](https://pypi.org/project/py2app/) 5.6.2 or higher

1. Install Python:

    Download the installer: https://python.org/download or use

    Homebrew: `brew install python@3.11`

2. Install PyQt6, pyperclip and py2app with pip:
`pip3 install PyQt6 pyperclip py2app`

### Building
1. Clone the File Find Repository: `git clone https://gitlab.com/Pixel-Mqster/File-Find.git`
2. cd into the repository: `cd File-Find`
3. [Install dependencies](#dependencies-for-building)
4. Run:

`python3 build-with-py2app.py py2app` 


## Roadmap
1. [x] UI:
   1. [x] Filter UI
   2. [x] Help UI
   3. [x] Search Result UI
2. [x] Exporting and Importing Searches:
   1. [x] Importing
   2. [x] Exporting 
3. [x] Caching:
    1. [x] Creating Caches
    2. [x] Using Caches
    3. [x] Deleting Caches
    4. [x] Clear Cache option
4. [ ] Multithreading:
    1. [x] UI using different thread as Search engine
    2. [x] Hashing with different Threads
    3. [ ] Searching trough different threads
    4. [ ] Indexing trough different threads
5. [x] Sorting:
   1. [x] Size
   2. [x] File Name
   3. [x] Modified
   4. [x] Created
   5. [x] Reverse
6. [ ] Searching:
    1. [x] Name
    2. [x] In Name
    3. [x] File Ending
    4. [x] Search in System Files
    5. [x] Directory to search in
    6. [x] Search for Folders
    7. [ ] Search for Alias
    8. [ ] Exclude Sub-folders
    9. [x] Contains
    10. [ ] Search with root privileges
    11. [x] Regex (used fn match instead (Unix shell-style wildcards))
    12. [x] Date Modified
    13. [x] Date Created
    14. [x] Excluded Files
7. [ ] Language
   1. [x] Language UI
   2. [ ] Languages apply
   3. [ ] Languages:
      1. [x] English
      2. [ ] German
      3. [ ] Frensh
      4. [ ] Spanish
      5. [ ] Chinese
8. [ ] Compatible with Linux and Windows?
