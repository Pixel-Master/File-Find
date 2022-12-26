# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# Main Script, execute this for running File Find

# Find Files easier with File Find

# Imports
import logging

# PyQt6 Gui Imports
from PyQt6.QtWidgets import QApplication

# Projects Library
import FF_Files
import FF_Main_UI

if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.DEBUG,
                        format='File Find[%(asctime)s] with %(levelname)s in %(pathname)s: %(message)s',)
    logging.info(f"Launching File Find with Version {FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]...\n")

    # Creating QApplication
    app = QApplication([])

    # File Operation
    FF_Files.remove_cache()
    FF_Files.setup()

    # Launches the Main Window
    FF_Main_UI.Main_Window()

    app.setQuitOnLastWindowClosed(False)
    app.exec()
    logging.info("User closed")
