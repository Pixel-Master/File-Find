<p align="center">
  <img src="https://gitlab.com/Pixel-Mqster/File-Find/-/raw/main/assets/icon.png" height="128">
  <h1 align="center">File-Find for macOS</h1>


<h3 align="center">A macOS UI Utility that helps you find Files easier.</h3>
[![File Find](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml/badge.svg?branch=main)](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)
## Content
- [Features](#features)
- [FAQ](#faq)
- [Download](#download)
- [Running from Source](#running-from-source)
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

## FAQ
Q: **What is File-Find and how does it work?**

A: File-Find is an open-source macOS Utility, that makes it easy to find Files. To search fill in the filters you need and leave the filters you don't need empty.

Q: **Why does File-Find crash when searching?**

A: File-Find is only using one thread. That's why it looks like File-Find "doesn't react".

Q: **How to clean the Cache?**

A: File-Find is saving the cache under `/Users/USERNAME/Library/Application Support/File-Find/Cached Searches`. The Cache gets cleaned up on start up, that means to clean the cache just restart File Find

## Download
File FInd isn't ready for Release yet Run from source or download pre-build macOS Apps from the GitHub action Page.
- [Running from Source](#running-from-source)
- [GitHub Action Page](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)


## Running from Source

### Note:

###### File Find won't work properly on Linux or Windows, because the UI displays different depending on the OS and some Features depends on the system. 


### Dependencies
- [Python](https://python.org/) 3.9 or higher
- [Pyperclip](https://pypi.org/project/pyperclip/) 1.8.2 or higher
- [PyQt 6](https://pypi.org/project/PyQt6/) 6.4 or higher

1. Install Python:

    Download the installer: https://python.org/download or use

    Homebrew: `brew install python@3.11`

2. Install pyperclip with pip:
`pip3 install pyperclip`

3. Install PyQt 6 with pip:
`pip3 install PyQt6`

### Running
1. Clone the File-Find Repository: `git clone https://gitlab.com/Pixel-Mqster/File-Find.git`
2. cd into the repository: `cd File-Find`
3. [Install dependencies](#dependencies)
4. Run:

`python3 File-Find.py` 

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
	1. [ ] UI using different thread as Search engine
	2. [ ] Searching trough different threads
	3. [ ] Indexing trough different threads
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
7. [ ] Compatible with Linux and Windows?
