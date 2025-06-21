<p align="center">
  <img src="https://github.com/Pixel-Master/File-Find/blob/main/assets/icon.png?raw=true" height="128">
  <h1 align="center">File Find</h1>


<h3 align="center">A file search utility that helps you find files easier.</h3>

<h4 align="center">Completely open-source and free. By Pixel-Master</h4>


[![File Find build](https://img.shields.io/github/actions/workflow/status/Pixel-Master/File-Find/File-Find.yml?branch=main&label=File%20Find%20build%20status&logo=File%20Find&style=flat-square)](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](http://www.gnu.org/licenses/gpl-3.0.html)
[![GitLab last commit](https://img.shields.io/github/last-commit/Pixel-Master/File-Find.svg?style=flat-square)](https://github.com/Pixel-Master/File-Find/commits)
[![GitHub stars](https://img.shields.io/github/stars/Pixel-Master/File-Find.svg?style=flat-square&label=Stars&color=yellow)](https://Pixel-Master.github.io/File-Find/)
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
- [Contributing](#contributing)

## Download

- [macOS](https://github.com/Pixel-Master/File-Find/releases/latest/download/File-Find.dmg)
- [Windows](https://github.com/Pixel-Master/File-Find/releases/latest/download/File-Find.exe)
- [Linux](https://github.com/Pixel-Master/File-Find/releases/latest/download/File-Find.bin)


Or you could:

- [Building from Source](#building-from-source)
- [Unstable builds from the GitHub Action Page](https://github.com/Pixel-Master/File-Find/actions/workflows/File-Find.yml)

## Features

### Search options

- **Basic**
  <p align="left">
   <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/File%20Find%20screenshot%20white.png?raw=true" height="250"></p>

    * **Name**: Multiple different modes are available.
      * Name **is**: Input needs to match the file name exactly. Also supports unix shell-style wildcards, which are not the same as regular expressions.
          * Usage:

              | Pattern | Meaning                          |
              |---------|----------------------------------|
              | *       | matches everything               |
              | ?       | matches any single character     |
              | [seq]   | matches any character in seq     |
              | [!seq]  | matches any character not in seq |

      * Name **contains**: The file name must contain the input.
      * Name **begins with**: The file name must start with the input.
      * Name **ends with**: The file name (without the file ending) must end with input. So `mple` would match with `Example.txt`.
      * Name **is similar to**: Performs a fuzzy search. So `amp` matches with `Example.txt`. Matching percentage can be set separately.
      * Name **doesn't contain**: Input must not be included in its entirety in the file name.
      * Name **in RegEx**: Does a regular expression pattern matching. For a detailed explanation refer to: https://regular-expressions.info
    * **File Types**: Select groups of file types that should be included in search results. Click `Custom` to change selection mode and input a file type (e.g. pdf) without the `.` that needs to match the file ending of a file exactly, ignoring case. Multiple possible file types can be separated with a semicolon (for example: `png;jpg;heic`) Click `Predefined` to switch back. Only the currently visible mode will be taken into account.
    * **Directory**: The directory to search in. Excluding subdirectory is possible in `Advanced`.


  

- **Properties**

  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/properties.png?raw=true" height="250">

    * **Date created and modified**: Specify a date range for the date the file has been created / modified, leave at default to ignore.
    * **File size**: Input specifies file size in a range from min to max. Select the unit (Byte, Megabyte, Gigabyte...) on the right. Select `No Limit` to only set a minimum or maximum value.


- **Advanced**

  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/advanced.png?raw=true" height="250">

    * **Limit folder depth**: Toggle to include/exclude subdirectories or their subdirectories. Entering a custom number sets the maximum amount of subdirectories in which files are still included. 
      * `0` or `No subfolders` means that ony the files directly in the specified directory will be included 
      * `1` means only the files in the folders that are directly in the specified dir will be considered...
    * **File contains**: Allows you to search in files. Input must be in the file content. This option can take really long. The input is case-sensitive and only supports raw text files such as `.txt`, MS-Office and PDFs are not supported.
    * **Only search for folders or files**: Toggle to only include folders or files in the search results.
    * **Search in system files**: Toggle to include files in the system and library folders.

- **Sorting**

  <img src="https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/sorting.png?raw=true" height="250">

    * **Sorting**: Possible sorting options:
        * **None** (fastest)
        * **File size**
        * **File name**
        * **Date modified**
        * **Date created**
        * **Path**: Sorting Path alphabetically
    * **Reverse Sort**: Reverse the sorted search results (last comes first). Only appears if a search option is selected.

### Dark / Light mode 

![](https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/File%20Find%20screenshot%20white.png?raw=true)

![](https://github.com/Pixel-Master/Pixel-Master.github.io/blob/main/File-Find/screenshots/File%20Find%20screenshot%20dark.png?raw=true)



### Other

- Export search results as a **plain text file (.txt)** or as a reloadable **File Find Search (.FFSearch)**
- Export your set filters as a .FFFilter file, load them again, share them or even set them as a default in the settings.
- Compare two searches and search for differences
- Find duplicated files



## Building from source
### Dependencies for building
- [Python](https://python.org/) 3.9 or higher **(Python 3.13 does not work yet!)**
- [PySide6](https://pypi.org/project/PySide6/) 6.4.1 or higher
- [nuitka](https://pypi.org/project/nuitka/) 2.0 or higher
- **Only macOS:** [dmgbuild](https://pypi.org/project/dmgbuild/) 1.1 or higher

### Building

#### On macOS

1. Install Python:

   Download the installer: [here](https://www.python.org/ftp/python/3.12.7/python-3.12.7-macos11.pkg) or use

   Homebrew: `brew install python@3.12`


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

    E.g.: `sudo apt install python3.12`


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

    Download the installer: [here](https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe)


2. Clone the File Find repository with git: `git clone https://github.com/Pixel-Master/File-Find.git`
   or download it from GitHub


3. cd into the repository: `cd File-Find`


4. Create a virtual environment: 
    1. Create: `python -m venv venv`
    2. Activate the virtual environment: `venv\Scripts\activate.bat`


5. [Install dependencies](#dependencies-for-building): `pip3 install -r requirements.txt`


6. Build using:

`python build.py`


## FAQ
Q: **What is File Find and how does it work?**

A: File Find is an open-source Utility for macOS, Windows and Linux
, that makes it easy to find files. To search fill in the filters you need and
leave the filters that you don't need empty.

Q: **Why doesn't File Find find my file/folder?**

A: Try the following steps:

* By default, (on a fresh install) File Find finds every file/folder except internal system files in the `Library` or `System` folders. You can enable them under `Advanced`.

* Maybe you haven't granted all the permission necessary to find every file. There are also some files that are only accessible to File Find by granting Full Disk Access. To do this open System Preferences, go to `Security & Privacy` and then add or activate File Find under `Full Disk Access`.

* File Find uses its own caching algorithm. Scanning results are stored and reused for a faster search. On default this cache gets cleared every two hours. You can clear the cache manually with `⌘ + T` on macOS (on Windows/Linux: `Ctrl + T`). Or right-click on the `Find` button and select `Search and create new cache for selected folder`.

* Check the excluded files list in the settings. Files listed there will not show up.

* Press `⌘ + R` on macOS (on Windows/Linux: `Ctrl + R`) to reset all filter settings to default and make sure the file actually meets the given criteria.

* If none of these options help, [create a Bug Report.](#bug-reports)

Q: **Why can't I open File Find**?

A: On macOS, if you get a message like

**“File Find.app” Not Opened**

Apple could not verify “File Find.app” is free of malware that may harm your Mac or compromise your privacy.

it is because File Find isn't signed with a Developer Certificate, which has to be acquired by Apple at around 99$. 
I currently do not have one nor plan on buying one soon. MacOS flags everyone who doesn't have one as "potentially unwanted software".
To bypass this you have to press `Done`, open System Preferences, go to `Privacy & Security,` scroll down to `"File Find.app" was blocked to protect your Mac.` and press `Open Anyway`.
There is going to be another Popup, in which you'll have to press `Open Anyway` again.

Q: **Why does File Find sometimes freeze?**

A: It is possible that for example reloading files or building the UI at the end of a search can cause File Find to freeze. Just wait a few seconds!

Q: **How do I clean the cache?**

A: File Find uses its own caching algorithm. Scanning results are stored and reused for a faster search. 
On default this cache gets cleared every two hours. You can change this behavior in the preferences. You can clear the cache manually with `⌘ + T` on macOS (on Windows/Linux: `Ctrl + T`). Or right-click on the `Find` button and select `Search and create new cache for selected folder`.

Q: **Why does File Find ask for permission for Contacts, Calenders, Photos, etc...?**

A: File Find scans the entire specified directory, even if files are excluded they are scanned first and then sorted out. 
Your photos, Calendar data, Contacts etc. are stored in a library folder, which means that File Find scans them. 
File Find does not connect to the internet, everything stays on your machine. You can also press `Do not allow`, the associated files will not appear in your searches.

Q: **Why does File Find ask for permission for Downloads, Desktop, Documents, etc...?**

A: On macOS if an app scans a directory this popup will automatically appear.
If you press `Don't allow`, File Find will still be able to scan those files,
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

- `FF_Additional_UI.py` - This file contains the code for additional UI components like dark mode icons or the tutorial

- `FF_About_UI.py` - This file contains the code for the About window

- `FF_Menubar.py` - Menu-bar for the search results, compare and duplicated window

- `FF_Settings.py` - Settings menu

### Mixed files and algorithms

- `FF_Search.py` - This file contains the code for the search engine

- `FF_Files.py` - This file contains File operations and global variables

- `FF_Duplicated.py` - This file contains the code for the 'Find duplicated' feature and it's UI

- `FF_Compare.py` - This file contains the code for the 'Compare Search' feature and it's UI

### Other

- `assets/` - Directory contains image assets for File Find

- `File Find.entitlements` - This is an entitlement file, which can be used to sandbox an app on macOS. Tough sandboxing is currently not supported.

## Contributing

It is recommended to use the [GitHub Issue Tracker.](https://github.com/Pixel-Master/File-Find/issues)
If you don't want to use GitHub or want to write privately, email me: [pixel_master.1@proton.me](mailto:pixel_master.1@proton.me)

### Bug reports

_If you found an unwanted behavior which you would classify as a bug._

Make sure you can reliably reproduce the bug. It is advised to use the Bug report template.

In your bug report include the following:

* If you think it would be helpful (it is in most cases) the log, access it by quitting the app and:
    * _On macOS_: Open Terminal.app and paste `/Applications/File\ Find.app/Contents/MacOS/File-Find` into it, copy and paste the output into your bug report. Make sure that the log **does not include confidential information** such as your username.
    * _On Windows_: Open cmd or Terminal and paste `C:\path\to\File-Find.exe > output.txt 2>&1` and run reproduce the bug. The log will be stored in output.txt on your user directory. copy and paste the output into your bug report. Make sure that the log **does not include confidential information** such as your username.
    * _On Linux_: Open Console and paste `/path/to/File-Find.bin` into it, copy and paste the output into your bug report. Make sure that the log **does not include confidential information** such as your username.
* Step-by-Step guide on how to reproduce the bug
* Expected behavior
* Screenshot (only necessary with UI-Related bugs, always welcome)
* Installation Information
    * OS and Version: [e.g. macOS 12]
    * File Find Version (as seen in the about page) [e.g. 1.0 [25-july-2024]]
* Additional information

### Feature Request

_New functionality is wished._

Include in your feature request:

* Is the feature request related to a problem?
* The solution you'd like, clearly and concise
* How elaborate will the implementation be? (estimation)
* Alternatives (optional)

### Pull Request

It is best if you create an Issue or ask me before you spent your time fixing an Issue or developing something new.
