# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# Main Script, execute this for running File-Find

# Find Files easier with File Find

# Imports

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

    # Testing File Access (not needed)
    # FF_Additional_UI.test_access()

    # File Operation
    FF_Files.remove_cache()
    FF_Files.setup()

    # Launches the Main Window
    FF_Main_UI.Main_Window()

    app.setQuitOnLastWindowClosed(False)
    app.exec()
    print("Quit")
