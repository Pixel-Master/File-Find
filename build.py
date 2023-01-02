# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This is a script used to build File Find with py2app and is not meant to be imported

# Imports
from setuptools import setup
import subprocess
import os
import sys

# Cleaning
os.system("rm -rf dist build")


# Finding and Setting architecture
arch = subprocess.run(["arch"], capture_output=True, text=True, check=True).stdout.replace("\n", "")

print("On:", arch)
if arch != "arm64":
    arch = "x86_64"
sys.argv.append("py2app")

APP = ["File-Find.py"]
DATA_FILES = []
OPTIONS = {"arch": arch,
           "iconfile": os.path.join(os.getcwd(), "assets", "icon.icns"),
           "plist": {"LSUIElement": False,
                     "NSHumanReadableCopyright": "Copyright (c) 2022 Pixel-Master. Licensed under GNU GPL v3",
                     "CFBundleIdentifier": "io.github.pixel-master",
                     "CFBundleShortVersionString": "0.0"}}
# Building App
setup(
   app=APP,
   data_files=DATA_FILES,
   options={"py2app": OPTIONS},
   setup_requires=["py2app"],
   version="1.0",
   name="File Find",
)

# Building DMG
print("\n\nBuilding DMG...")
os.system("create-dmg "
          "--volname \"File Find\" "
          "--volicon \"assets/icon.icns\" "
          "--background \"assets/background.png\" "
          "--window-pos 200 120 "
          "--window-size 800 400 "
          "--icon-size 100 "
          "--icon \"dist/File Find.app\" 200 190 "
          "--app-drop-link 600 190 "
          "\"dist/File Find.dmg\" "
          "\"dist/\"\n")
