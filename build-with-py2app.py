# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This is a script used to build File Find with py2app and is not ment to be imported
from setuptools import setup
import subprocess
import os

arch = subprocess.run(["arch"], capture_output=True, text=True, check=True).stdout.replace("\n", "")
print("On:", arch)
if arch != "arm64":
    arch = "x86_64"

APP = ['File-Find.py']
DATA_FILES = []
OPTIONS = {'arch': arch,
           'iconfile': os.path.join(os.getcwd(), 'assets/icon.icns')}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    version="1.0",
    name="File Find",
)
