# This build script is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
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

# Only macOS needs dmgbuild
if sys.platform == "darwin":
    import dmgbuild

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
                       "LSMinimumSystemVersion": "11",
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
                       "NSSystemAdministrationUsageDescription":
                           "File Find needs to access your file-system in order to search it",
                       "LSApplicationCategoryType": "public.app-category.utilities",
                       "LSUIElement": False,
                       "NSHumanReadableCopyright": "Copyright © 2022–2025 Pixel Master. Some rights reserved.",
                       "NSSupportsSuddenTermination": False,
                       "CFBundleInfoDictionaryVersion": "6.0",
                       "NSHighResolutionCapable": True}, fp=plist)

        # This is temporary, as long as I don't have an Apple Developer ID, just remove the signature
        run(["codesign",
             "-s",
             "-",  # Ad-hoc signed
             "-f",
             # "--entitlements",
             # "File Find.entitlements",
             os.path.join("dist", "File Find.app")])

        # Building DMG
        print("\n\nBuilding DMG...")

        dmgbuild.build_dmg(os.path.join("dist", "File Find.dmg"), "File Find Installer",
                           settings={"files": [os.path.join("dist", "File Find.app")],
                                     "symlinks": {"Applications": "/Applications"},
                                     "icon_locations": {"File Find.app": (50, 60), "Applications": (250, 60)},
                                     "background": os.path.join("assets", "background.png"),
                                     "icon_size": 70})

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
