# This build script is a part of File Find made by Pixel-Master
#
# Copyright 2022-2023 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This is a script used to build File Find with py2app and is not meant to be imported

# Imports
from setuptools import setup
import subprocess
import os
import sys

# Cleaning
os.system("rm -rf dist build")

# Finding and Setting architecture
arch = subprocess.run(["uname", "-m"], capture_output=True, text=True, check=True).stdout.replace("\n", "")

print("On:", arch)
if arch != "arm64":
    arch = "x86_64"
sys.argv.append("py2app")

APP = ["File-Find.py"]
DATA_FILES = ["assets/ffsave_icon.icns"]

# py2app Options
OPTIONS = {"arch": arch,
           "iconfile": os.path.join(os.getcwd(), "assets", "icon.icns"),
           # Plist Options
           "plist": {"LSUIElement": False,
                     "NSHumanReadableCopyright": "Copyright © 2022–2023 Pixel Master. All rights reserved.",
                     "CFBundleIdentifier": "io.github.pixel-master.file-find",
                     "CFBundleShortVersionString": "0.0",
                     "LSApplicationCategoryType": "public.app-category.utilities",
                     "NSSupportsSuddenTermination": True,
                     "CFBundleDocumentTypes":
                         [{"CFBundleTypeExtensions": ["FFSave"],
                           "CFBundleTypeIconFile": "ffsave_icon.icns",
                           "CFBundleTypeName": "File Find Search",
                           "CFBundleTypeOSTypes": ["FFSAVE"],
                           "CFBundleTypeRole": "Viewer",
                           "LSIsAppleDefaultForType": True,
                           "CFBundleTypeIconSystemGenerated": True}]}}
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
# Downloading the create-dmg script from GitHub
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
