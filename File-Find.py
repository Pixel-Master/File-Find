# This File is a part of File-Find made by Pixel-Master and licensed under the GNU GPL v3
# Main Script, execute this for running File-Find

# Find Files easier with File Find

# Imports
import os

# PyQt6 Gui Imports
from PyQt6.QtWidgets import QApplication

# Projects Library
import FF_Files
import FF_Main_UI

if __name__ == "__main__":
    # Debug
    print("Launching...")

    # Creating QApplication
    app = QApplication([])

    # Files
    FF_Files.remove_cache()
    FF_Files.setup()
    with open(os.path.join(FF_Files.LibFolder, "Info.txt"), "w") as ver_file:
        ver_file.write(f"Version: {FF_Files.VERSION}\n")


    # Launches the Main Window
    Main_UI = FF_Main_UI.Main_Window()

    app.exec()
    print("Quit")
