# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# Main Source File, execute this for running File Find

# Imports
import logging
import gc
import os
import sys
from sys import platform

# PySide6 Gui Imports
from PySide6.QtCore import QEvent
from PySide6.QtGui import QFileOpenEvent, QIcon
from PySide6.QtWidgets import QApplication

# Projects Library
import FF_Files
import FF_Additional_UI
import FF_Main_UI
import FF_Search

if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.DEBUG,
                        format="File Find [%(pathname)s] at %(asctime)s, %(levelname)s: %(message)s",
                        force=True)

    logging.info(f"Launching File Find with Version {FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]...\n")
    logging.info(f"Launching on \"{platform}\", User Path: {FF_Files.USER_FOLDER}...\n")

    # If app is sandboxed on macOS, certain things are not possible
    if FF_Files.IS_SANDBOXED:
        logging.info("App is sandboxed, certain features are not available")
    else:
        logging.info("App is NOT sandboxed, all features are available")

    # Creating QApplication
    class CreateApp(QApplication):

        def event(self, event: QEvent) -> bool:
            # Executed when an event is received.

            # Handle file-open events, when a .ffsearch or .fffilter file is opened from outside of file find
            # e.g. from the OS with finder or file-explorer
            # Testing if the event is triggered by an opened file
            if event.type() == QEvent.Type.FileOpen:
                # Getting the path of the file
                path = QFileOpenEvent.url(event).path()

                # If the opened file is a file find search
                if path.endswith("FFSearch"):
                    # Debug
                    logging.info(f"Opening {path}...")
                    FF_Search.LoadSearch.open_file(path, None)

                # Filter preset
                elif path.endswith("FFFilter"):
                    # Debug
                    logging.info(f"Opening {path}...")
                    main_window.import_filters(path)

            # If the application icon in the dock is pressed, the mai window should open
            elif event.type() == QEvent.Type.ApplicationActivated:
                try:
                    # Show the window
                    main_window.Root_Window.show()
                except NameError:
                    # If something happens this can fail without a big problem
                    pass

            return super().event(event)

    app = CreateApp([])

    FF_Additional_UI.UIIcon(path=None, input_app=app)

    # Turning of automatic garbage collection because
    gc.disable()

    # File Operation
    FF_Files.setup()
    FF_Files.cache_test(is_launching=True)

    # Launches the Main Window
    main_window = FF_Main_UI.MainWindow()

    app.setQuitOnLastWindowClosed(False)

    # Only on non Mac systems set the icon
    if platform != "darwin":
        app.setWindowIcon(QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "FFlogo_small.png")))

    # Main loop for User-Interface
    app.exec()

    # Debug
    logging.info("Closed.")

    sys.exit(0)
