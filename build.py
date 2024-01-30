# This build script is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This is a script used to build File Find with nuitka and is not meant to be imported

# Imports
import subprocess
import os
import sys
import plistlib

# Projects Libraries
import FF_Files

# Cleaning
os.system("rm -rf dist build File-Find.build File-Find.dist")
# Creating a distribution dir
os.mkdir(os.path.join(os.getcwd(), "dist"))

# Finding and Setting architecture
arch = subprocess.run(["uname", "-m"], capture_output=True, text=True, check=True).stdout.replace("\n", "")
print("On:", arch)

# On macOS
if sys.platform == "darwin":
    # Building App
    subprocess.run(["nuitka3",
                    "--standalone",
                    "--macos-create-app-bundle",
                    f"--macos-app-icon={os.getcwd()}/assets/icon.icns",
                    "--enable-plugin=pyside6",
                    "File-Find.py"])
    # Renaming and moving the app
    subprocess.run(["mv", "File-Find.app", os.path.join("dist", "File Find.app")])
    # Setting the plist
    with open(os.path.join(os.getcwd(), "dist", "File Find.app", "Contents", "Info.plist"), "wb") as plist:
        plistlib.dump(
            value={'CFBundleDisplayName': 'File Find',
                   "CFBundleExecutable": "File-Find",
                   "CFBundleIconFile": "icon.icns",
                   "CFBundleDocumentTypes": [{"CFBundleTypeExtensions": ["FFSearch"],
                                              "CFBundleTypeIconSystemGenerated": True,
                                              "CFBundleTypeName": "File Find Search",
                                              "CFBundleTypeOSTypes": ["FFSEARCH"],
                                              "CFBundleTypeRole": "Viewer",
                                              "LSIsAppleDefaultForType": True}],
                   "CFBundleIdentifier": "io.github.pixel-master.file-find",
                   "CFBundleShortVersionString": FF_Files.VERSION_SHORT,
                   "CFBundleVersion": FF_Files.VERSION,
                   "CFBundleName": "File-Find",
                   "CFBundlePackageType": "APPL",
                   "LSApplicationCategoryType": "public.app-category.utilities",
                   "LSUIElement": False,
                   "NSHumanReadableCopyright": "Copyright © 2022–2024 Pixel Master. Some rights reserved.",
                   "NSSupportsSuddenTermination": False,
                   "CFBundleInfoDictionaryVersion": "6.0",
                   "NSHighResolutionCapable": True}, fp=plist)

    # Building DMG
    print("\n\nBuilding DMG...")

    subprocess.run(
        ['create-dmg',
         '--volname', 'File Find',
         '--volicon', 'assets/icon.icns',
         '--background', 'assets/background.png',
         '--window-pos', '200', '120',
         '--window-size', '800', '400',
         '--icon-size', '100',
         '--icon', 'dist/File Find.app', '200', '190',
         '--app-drop-link', '600', '190',
         'dist/File Find.dmg',
         'dist'])
