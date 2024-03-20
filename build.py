# This build script is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This is a script used to build File Find with nuitka and is not meant to be imported

# Imports
from subprocess import run
import os
import sys
import plistlib
import shutil

# Projects Libraries
from FF_Files import VERSION, VERSION_SHORT


def main():
    # Cleaning
    shutil.rmtree(os.path.join(os.getcwd(), "dist"), ignore_errors=True)
    shutil.rmtree(os.path.join(os.getcwd(), "build"), ignore_errors=True)
    # Creating a distribution dir
    os.mkdir(os.path.join(os.getcwd(), "dist"))

    # On macOS
    if sys.platform == "darwin":

        # Finding and Setting architecture
        arch = run(["uname", "-m"], capture_output=True, text=True, check=True).stdout.replace("\n", "")
        print("On:", arch)

        # Building App
        run(["python3",
             "-m",
             "nuitka",
             "--standalone",
             "--macos-create-app-bundle",
             f"--macos-app-icon={os.getcwd()}/assets/icon.icns",
             "--enable-plugin=pyside6",
             "--assume-yes-for-downloads",
             "--disable-cache=all",
             "--output-dir=dist",
             "File-Find.py"])
        # Renaming the app
        run(["mv", os.path.join("dist", "File-Find.app"), os.path.join("dist", "File Find.app")])
        # Setting the plist
        with open(os.path.join(os.getcwd(), "dist", "File Find.app", "Contents", "Info.plist"), "wb") as plist:
            plistlib.dump(
                value={"CFBundleDisplayName": "File Find",
                       "CFBundleExecutable": "File-Find",
                       "CFBundleIconFile": "icon.icns",
                       "CFBundleDocumentTypes": [{"CFBundleTypeExtensions": ["FFSearch"],
                                                  "CFBundleTypeIconSystemGenerated": True,
                                                  "CFBundleTypeName": "File Find Search",
                                                  "CFBundleTypeOSTypes": ["FFSEARCH"],
                                                  "CFBundleTypeRole": "Viewer",
                                                  "LSIsAppleDefaultForType": True},

                                                 {"CFBundleTypeExtensions": ["FFFilter"],
                                                  "CFBundleTypeIconSystemGenerated": True,
                                                  "CFBundleTypeName": "File Find Filter Settings Preset",
                                                  "CFBundleTypeOSTypes": ["FFFILTER"],
                                                  "CFBundleTypeRole": "Editor",
                                                  "LSIsAppleDefaultForType": True}],
                       "CFBundleIdentifier": "io.github.pixel-master.file-find",
                       "CFBundleShortVersionString": VERSION_SHORT,
                       "CFBundleVersion": VERSION,
                       "CFBundleName": "File-Find",
                       "CFBundlePackageType": "APPL",
                       "LSApplicationCategoryType": "public.app-category.utilities",
                       "LSUIElement": False,
                       "NSHumanReadableCopyright": "Copyright © 2022–2024 Pixel Master. Some rights reserved.",
                       "NSSupportsSuddenTermination": False,
                       "CFBundleInfoDictionaryVersion": "6.0",
                       "NSHighResolutionCapable": True}, fp=plist)

        # This is temporary, as long as I don't have an Apple Developer ID, just remove the signature
        run(["codesign", "-s", "-", "-f", os.path.join("dist", "File Find.app")])

        # Building DMG
        print("\n\nBuilding DMG...")

        run(
            ["create-dmg",
             "--volname", "File Find",
             "--volicon", os.path.join("assets", "icon.icns"),
             "--background", os.path.join("assets", "background.png"),
             "--window-pos", "200", "120",
             "--window-size", "800", "400",
             "--icon-size", "100",
             "--icon", os.path.join("dist", "File Find.app"), "200", "190",
             "--app-drop-link", "600", "190",
             os.path.join("dist", "File Find.dmg"),
             "dist"])

    # On Linux
    elif sys.platform == "linux":
        # Building App
        run(["python3",
             "-m",
             "nuitka",
             "--standalone",
             "--onefile",
             f"--linux-icon={os.path.join(os.getcwd(), 'assets', 'icon.png')}",
             "--enable-plugin=pyside6",
             "--output-dir=dist",
             "File-Find.py"])

        # Renaming the app
        run(["mv", os.path.join("dist", "File-Find.bin"), os.path.join("dist", "File Find.bin")])

    # On Windows
    elif sys.platform == "win32" or sys.platform == "cygwin":
        # Building App
        run(["python",
             "-m",
             "nuitka",
             "--standalone",
             "--onefile",
             f"--windows-icon-from-ico={os.path.join(os.getcwd(), 'assets', 'icon.ico')}",
             "--enable-plugin=pyside6",
             "--output-dir=dist",
             "--disable-console",
             "--assume-yes-for-downloads",
             "--disable-cache=all",
             "--output-filename=File Find.exe",
             "File-Find.py"])

        # Renaming the app
        print("Built exe, done")


if __name__ == "__main__":
    main()
