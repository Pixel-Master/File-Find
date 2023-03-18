# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2023 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the 'Compare Search' feature

# Imports
from pickle import load
from threading import Thread
from time import perf_counter, ctime
import hashlib
import logging
import os
import gc


# PyQt6 Gui Imports
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QListWidget, QMenuBar, QLabel, QPushButton

# Projects Libraries
import FF_Files
import FF_Additional_UI
import FF_Help_UI


# The window
class Compare_UI:
    def __init__(self, path_of_first_search, parent):

        # Debug
        logging.info("Setting up the Compare_Window")

        # Set up the Window
        self.Compare_Window = QMainWindow(parent)
        # Set up the window title
        self.Compare_Window.setWindowTitle(
            f"File Find | Comparing Searches: "
            f"{FF_Files.display_path(path_of_first_search, 15)} (base) --> "
            f"{FF_Files.display_path(compared_searches.path_of_second_search[0], 15)}")

        self.Compare_Window.setFixedHeight(700)
        self.Compare_Window.setFixedWidth(800)
        self.Compare_Window.show()

        # Set up both list-boxes
        # Added files / files only in first search

        # Debug
        logging.debug("Setting up Added files / files only in first search listbox..")

        self.added_files_listbox = QListWidget(self.Compare_Window)
        # Resize the List-widget
        self.added_files_listbox.resize(380, 570)
        # Place
        self.added_files_listbox.move(10, 70)
        # Show the Listbox
        self.added_files_listbox.show()
        # Add items
        for item in compared_searches.files_only_in_first_search:
            self.added_files_listbox.addItem(item)
        # Double-Clicking Event
        self.added_files_listbox.doubleClicked.connect(self.open_in_finder)

        # Removed files / files only in second search

        # Debug
        logging.debug("Done!, Setting up Removed files / files only in second search listbox..")

        self.removed_files_listbox = QListWidget(self.Compare_Window)
        # Resize the List-widget
        self.removed_files_listbox.resize(380, 570)
        # Place
        self.removed_files_listbox.move(410, 70)
        # Show the Listbox
        self.removed_files_listbox.show()
        # Add items
        for item in compared_searches.files_only_in_second_search:
            self.removed_files_listbox.addItem(item)
        # Double-Clicking Event
        self.removed_files_listbox.doubleClicked.connect(self.open_in_finder)

        # Debug
        logging.debug("Done!")

        # Labels
        # Added files
        self.added_files_label1, self.added_files_label2 = self.generate_title_label(
            text="Added Files", text2=path_of_first_search, color="green")
        self.added_files_label1.move(10, 10)
        self.added_files_label2.move(10, 40)

        # Removed files
        self.removed_files_label1, self.removed_files_label2 = self.generate_title_label(
            text=f"Removed Files", text2=compared_searches.path_of_second_search[0], color="red")
        self.removed_files_label1.move(410, 10)
        self.removed_files_label2.move(410, 40)

        # Setting up the menubar...
        self.menubar()
        logging.info("Done building Compare-UI!\n")

        # Buttons
        # Button to open the File in Finder
        show_in_finder = self.generate_button("Open in Finder", self.open_in_finder)
        show_in_finder.move(10, 650)

        # Button to open the File
        open_file = self.generate_button("Open", self.open_with_program)
        open_file.move(170, 650)

        # Button to open File Info
        file_info_button = self.generate_button("Info", self.file_info)
        file_info_button.move(580, 650)

        # Button to open view the hashes of the File
        file_hash = self.generate_button("File Hashes", self.view_hashes)
        file_hash.move(680, 650)

    # Functions to automate Button
    def generate_button(self, text, command):
        # Define the Button
        button = QPushButton(self.Compare_Window)
        # Change the Text
        button.setText(text)
        # Set the command
        button.clicked.connect(command)
        # Display the Button correctly
        button.show()
        button.adjustSize()
        # Return the value of the Button, to move the Button
        return button

    # Function for generating the added / removed files labels
    def generate_title_label(self, text, text2, color) -> tuple[QLabel, QLabel]:

        # Label 1
        label1 = QLabel(self.Compare_Window)

        # Defining the font
        font1 = QFont("Arial", 23)
        font1.setBold(True)

        # Set the text, the font and the color
        label1.setText(text)
        label1.setFont(font1)
        label1.setStyleSheet(f"color: {color};")
        # Display the label
        label1.adjustSize()
        label1.show()

        # Label 2
        label2 = QLabel(self.Compare_Window)

        # Set the text, the font and the color

        # Shorten the text string to only include the first to the 30th
        # and the last ten character if the string is longer then 43 characters
        text2_shortened = f"Files only in:\n{FF_Files.display_path(text2)}"
        # Set the label to the shortened string
        label2.setText(text2_shortened)

        # Defining the font
        font2 = QFont("Arial", 12)
        font2.setBold(True)
        # Configure the font
        label2.setFont(font2)

        # Display the label
        label2.adjustSize()
        label2.show()

        return label1, label2

    def menubar(self):
        logging.debug("Setting up menubar...", )

        # Menubar
        menu_bar = QMenuBar(self.Compare_Window)

        # Menus
        menu_bar.addMenu("&Edit")
        tools_menu = menu_bar.addMenu("&Tools")
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Clear Cache
        cache_action = QAction("&Clear Cache", self.Compare_Window)
        cache_action.triggered.connect(lambda: FF_Files.remove_cache(True, self.Compare_Window))
        cache_action.setShortcut("Ctrl+T")
        tools_menu.addAction(cache_action)

        # Open File Action
        open_action = QAction("&Open Selected File", self.Compare_Window)
        open_action.triggered.connect(self.open_with_program)
        open_action.setShortcut("Ctrl+O")
        tools_menu.addAction(open_action)

        # Show File in Finder Action
        show_action = QAction("&Show Selected File in Finder", self.Compare_Window)
        show_action.triggered.connect(self.open_in_finder)
        show_action.setShortcut("Ctrl+Shift+O")
        tools_menu.addAction(show_action)

        # File Info
        info_action = QAction("&Info for Selected File", self.Compare_Window)
        info_action.triggered.connect(self.file_info)
        info_action.setShortcut("Ctrl+I")
        tools_menu.addAction(info_action)

        # View File Hashes
        hash_action = QAction("&Hashes for Selected File", self.Compare_Window)
        hash_action.triggered.connect(self.view_hashes)
        hash_action.setShortcut("Ctrl+Shift+I")
        tools_menu.addAction(hash_action)

        # About File Find
        about_action = QAction("&About File Find", self.Compare_Window)
        about_action.triggered.connect(lambda: FF_Help_UI.Help_Window(self.Compare_Window))
        help_menu.addAction(about_action)

        # Close Window
        close_action = QAction("&Close Window", self.Compare_Window)
        close_action.triggered.connect(self.Compare_Window.destroy)
        close_action.triggered.connect(gc.collect)
        close_action.setShortcut("Ctrl+W")
        window_menu.addAction(close_action)

        # Help
        help_action = QAction("&File Find Help and Settings", self.Compare_Window)
        help_action.triggered.connect(lambda: FF_Help_UI.Help_Window(self.Compare_Window))
        help_menu.addAction(help_action)

    # Options for paths
    # Opens a file
    def open_with_program(self):
        try:
            # Selecting the highlighted item of the focused listbox
            selected_file = self.Compare_Window.focusWidget().currentItem().text()

            if os.system("open " + str(selected_file.replace(" ", "\\ "))) != 0:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", f"No Program found to open {selected_file}",
                                                              self.Compare_Window)
            else:
                logging.debug(f"Opened: {selected_file}")
        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Compare_Window)

    # Shows a file in finder
    def open_in_finder(self):
        try:
            # Selecting the highlighted item of the focused listbox
            selected_file = self.Compare_Window.focusWidget().currentItem().text()

            if os.system("open -R " + str(selected_file.replace(" ", "\\ "))) != 0:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", f"File does not exists: {selected_file}!",
                                                              self.Compare_Window)
            else:
                logging.debug(f"Opened in Finder: {selected_file}")
        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Compare_Window)

    # Get basic information about a file
    def file_info(self):
        try:
            # Selecting the highlighted item of the focused listbox
            file = self.Compare_Window.focusWidget().currentItem().text()

            # Debug
            logging.debug("Called File Info")
            try:

                # Getting File Type
                if os.path.islink(file):
                    filetype = "Alias / File Link"
                elif os.path.isfile(file):
                    filetype = "File"
                elif os.path.isdir(file):
                    filetype = "Folder"
                else:
                    filetype = "Unknown"

                FF_Additional_UI.msg.show_info_messagebox(f"Information about: {file}",
                                                          f"File Info:\n"
                                                          f"\n\n"
                                                          f"Path: {file}\n"
                                                          f"\n"
                                                          f"Type: {filetype}\n"
                                                          f"File Name: {os.path.basename(file)}\n"
                                                          f"Size: "
                                                          f"{FF_Files.conv_file_size(FF_Files.get_file_size(file))}\n"
                                                          f"Date Created: {ctime(os.stat(file).st_birthtime)}\n"
                                                          f"Date Modified: {ctime(os.path.getmtime(file))}\n",
                                                          self.Compare_Window)
            except (FileNotFoundError, PermissionError):
                logging.error(f"{file} does not Exist!")
                FF_Additional_UI.msg.show_critical_messagebox("File Not Found!", f"File does not exist: {file}!",
                                                              self.Compare_Window)
        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Compare_Window)

    # View the hashes
    def view_hashes(self):
        try:
            # Collecting Files
            # Selecting the highlighted item of the focused listbox
            hash_file = self.Compare_Window.focusWidget().currentItem().text()
            logging.info(f"Collecting {hash_file}...")

            if os.path.isdir(hash_file):
                file_content = b""
                for root, dirs, files in os.walk(hash_file):
                    for i in files:
                        try:
                            with open(os.path.join(root, i), "rb") as HashFile:
                                file_content = HashFile.read() + file_content
                        except FileNotFoundError:
                            logging.error(f"{HashFile} does not exist!")

            else:
                try:
                    with open(hash_file, "rb") as HashFile:
                        file_content = HashFile.read()
                except FileNotFoundError:
                    logging.error(f"{HashFile} does not exist!")
                    FF_Additional_UI.msg.show_critical_messagebox("File not found! ", f"{HashFile} does not exist!",
                                                                  self.Compare_Window)
                    file_content = 0

            # Computing Hashes
            logging.info(f"Computing Hashes of {hash_file}...")
            hash_list = []
            saved_time = perf_counter()

            # sha1 Hash
            logging.debug("Computing sha1 Hash...")
            sha1_hash_thread = Thread(target=lambda: hash_list.insert(0, hashlib.sha1(file_content).hexdigest()))
            sha1_hash_thread.start()

            # md5 Hash
            logging.debug("Computing md5 Hash...")
            md5_hash_thread = Thread(target=lambda: hash_list.insert(1, hashlib.md5(file_content).hexdigest()))
            md5_hash_thread.start()

            # sha256 Hash
            logging.debug("Computing sha256 Hash...")
            sha256_hash_thread = Thread(
                target=lambda: hash_list.insert(2, hashlib.sha256(file_content).hexdigest()))
            sha256_hash_thread.start()

            # Waiting for hashes
            logging.debug("Waiting for Hashes to complete...")

            sha1_hash_thread.join()
            sha1_hash = hash_list[0]
            logging.debug(f"{sha1_hash = }")

            md5_hash_thread.join()
            md5_hash = hash_list[1]
            logging.debug(f"{md5_hash = }")

            sha256_hash_thread.join()
            sha256_hash = hash_list[2]
            logging.debug(f"{sha256_hash = }")

            # Time Feedback
            final_time = perf_counter() - saved_time
            logging.debug(f"Took {final_time}")

            # Give Feedback
            FF_Additional_UI.msg.show_info_messagebox(f"Hashes of {hash_file}",
                                                      f"Hashes of {hash_file}:\n\n"
                                                      f"MD5:\n {md5_hash}\n\n"
                                                      f"SHA1:\n {sha1_hash}\n\n"
                                                      f"SHA265:\n {sha256_hash}\n\n\n"
                                                      f"Took: {round(final_time, 3)} sec.",
                                                      self.Compare_Window)

        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Compare_Window)
            logging.error("Error! Select a File!")


# The engine (add threading!)
class Compare_Searches:
    def __init__(self, files_of_first_search: list, path_of_first_search, parent):
        # Debug
        logging.debug("User pressed Compare Search")

        # Setting the thread up with the pyqt signals to launch the ui
        class signals_class(QObject):
            finished = pyqtSignal()

        self.signals = signals_class()
        # Connecting the signal to the user-interface class
        self.signals.finished.connect(lambda: Compare_UI(path_of_first_search, parent))

        # Thread
        comparing_thread = QThreadPool()

        # Get the files of both searches
        self.files_of_first_search = files_of_first_search
        logging.debug("Asking for a second FFSearch file...")
        self.files_of_second_search, self.path_of_second_search = self.load_second_search()

        # Files which are only in one list
        self.files_only_in_first_search = []
        self.files_only_in_second_search = []

        # Starting the thread
        logging.debug("Starting thread...")
        comparing_thread.start(self.compare)

    def compare(self):
        # Debug
        logging.debug("Comparing searches...")

        # Loop through the first list and test every file if it is in both lists
        for file_in_first_list in self.files_of_first_search:
            if not (file_in_first_list in self.files_of_second_search):
                self.files_only_in_first_search.append(file_in_first_list)
            else:
                # If it is found delete file in second list
                self.files_of_second_search.remove(file_in_first_list)

        logging.debug("Done Looping!, Swapping...")

        # In the second search are only files that don't appear in the first search
        self.files_only_in_second_search = self.files_of_second_search

        logging.debug("Done comparing searches!\n")

        # Setting the global var compared_searches to self to include all 'self.' vars
        global compared_searches
        compared_searches = self

        # Emitting the signal to launch the ui
        logging.debug("Finished thread, Emitting finished signal!")
        self.signals.finished.emit()

    @staticmethod
    def load_second_search():
        # Get the user to select a valid search file
        second_search_file = QFileDialog.getOpenFileName(
            parent=None,
            caption="Select Second Search",
            directory=FF_Files.SAVED_SEARCHES_FOLDER,
            filter="*.FFSave;")

        # Debug
        logging.debug(f"Second search: {second_search_file}, Reading file...")

        # Load list from file and return path and files
        try:
            with open(second_search_file[0], "rb") as SearchFile:
                return load(SearchFile), second_search_file
        except FileNotFoundError:
            # if the user pressed cancel
            return None


compared_searches: Compare_Searches
