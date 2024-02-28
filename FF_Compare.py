# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the 'Compare Search' feature

# Imports
from json import load
import logging
import os

# PySide6 Gui Imports
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import QObject, Signal, QThreadPool, QSize
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QListWidget, QLabel, QPushButton, QWidget, QGridLayout, QHBoxLayout)

# Projects Libraries
import FF_Files
import FF_Menubar


# The window
class CompareUi:
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
        # Set the start size of the Window, because it's resizable
        self.BASE_WIDTH = 800
        self.BASE_HEIGHT = 700
        self.Compare_Window.setBaseSize(self.BASE_WIDTH, self.BASE_HEIGHT)
        # Display the window
        self.Compare_Window.show()

        # Adding Layouts

        # Main Layout
        # Create a central widget
        self.Central_Widget = QWidget(self.Compare_Window)
        self.Compare_Window.setCentralWidget(self.Central_Widget)
        # Create the main Layout
        self.Compare_Layout = QGridLayout(self.Central_Widget)
        self.Compare_Layout.setContentsMargins(20, 0, 20, 20)
        self.Compare_Layout.setVerticalSpacing(1)

        # Listbox Layout
        self.Listbox_Layout = QHBoxLayout(self.Compare_Window)
        self.Listbox_Layout.setContentsMargins(0, 0, 0, 0)
        # Add to main Layout
        self.Compare_Layout.addLayout(self.Listbox_Layout, 2, 0, 8, 2)

        # Bottom Layout
        self.Bottom_Layout = QHBoxLayout(self.Compare_Window)
        self.Bottom_Layout.setContentsMargins(0, 0, 0, 0)
        # Add to main Layout
        self.Compare_Layout.addLayout(self.Bottom_Layout, 10, 0, 1, 2)

        # Setting up the menu bar...
        menu_bar = FF_Menubar.MenuBar(parent=self.Compare_Window, window="compare",
                                      listbox=None, )
        logging.debug("Done building MenuBar\n")

        # Set up both list-boxes
        # Added files / files only in first search

        # Debug
        logging.debug("Setting up Added files / files only in first search listbox..")

        self.added_files_listbox = QListWidget(self.Compare_Window)
        # Adding to grid
        self.Listbox_Layout.addWidget(self.added_files_listbox)
        # Show the Listbox
        self.added_files_listbox.show()
        # Add items
        self.added_files_listbox.addItems(compared_searches.files_only_in_first_search)
        # Double-Clicking Event
        self.added_files_listbox.doubleClicked.connect(menu_bar.open_in_finder)

        # Removed files / files only in second search

        # Debug
        logging.debug("Done!, Setting up Removed files / files only in second search listbox..")

        self.removed_files_listbox = QListWidget(self.Compare_Window)
        # Adding to grid
        self.Listbox_Layout.addWidget(self.removed_files_listbox)
        # Show the Listbox
        self.removed_files_listbox.show()
        # Add items
        self.removed_files_listbox.addItems(compared_searches.files_only_in_second_search)
        # Double-Clicking Event
        self.removed_files_listbox.doubleClicked.connect(menu_bar.open_in_finder)

        # Debug
        logging.debug("Done!")

        # Labels
        # Added files
        self.added_files_label1, self.added_files_label2 = self.generate_title_label(
            text="Added Files", text2=path_of_first_search, color="green")
        self.Compare_Layout.addWidget(self.added_files_label1, 0, 0)
        self.Compare_Layout.addWidget(self.added_files_label2, 1, 0)

        # Removed files
        self.removed_files_label1, self.removed_files_label2 = self.generate_title_label(
            text="Removed Files", text2=compared_searches.path_of_second_search[0], color="red")
        self.Compare_Layout.addWidget(self.removed_files_label1, 0, 1)
        self.Compare_Layout.addWidget(self.removed_files_label2, 1, 1)

        # Buttons
        # Button to open the File in Finder
        move_file = self.generate_button("Move / Rename", menu_bar.move_file,
                                         icon=os.path.join(FF_Files.ASSETS_FOLDER, "Move_icon_small.png"))
        self.Bottom_Layout.addWidget(move_file)

        # Button to move the file to trash
        delete_file = self.generate_button("Move to Trash", menu_bar.delete_file,
                                           icon=os.path.join(FF_Files.ASSETS_FOLDER, "Trash_icon_small.png"))
        self.Bottom_Layout.addWidget(delete_file)

        # Button to open the file
        open_file = self.generate_button("Open", menu_bar.open_file,
                                         icon=os.path.join(FF_Files.ASSETS_FOLDER, "Open_icon_small.png"))
        self.Bottom_Layout.addWidget(open_file)

        # Button to show info about the file
        file_info_button = self.generate_button("Info", menu_bar.file_info,
                                                icon=os.path.join(FF_Files.ASSETS_FOLDER, "Info_button_img_small.png"))
        self.Bottom_Layout.addWidget(file_info_button)

        # Debug
        logging.info("Done building Compare-UI!\n")

    # Functions to automate Button
    def generate_button(self, text, command, icon=None):
        # Define the Button
        button = QPushButton(self.Compare_Window)
        # Change the Text
        button.setText(text)
        # Set the command
        button.clicked.connect(command)
        # Set the icon
        if icon is not None:
            button.setIcon(QIcon(icon))
            button.setIconSize(QSize(23, 23))
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


# The engine
class CompareSearches:
    def __init__(self, files_of_first_search: list, path_of_first_search, parent):
        # Debug
        logging.debug("User pressed Compare Search")

        try:
            # Setting the thread up with the Qt6 signals to launch the ui
            class SignalsClass(QObject):
                finished = Signal()

            self.signals = SignalsClass()
            # Connecting the signal to the user-interface class
            self.signals.finished.connect(lambda: CompareUi(path_of_first_search, parent))

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
        except TypeError:
            # If no file was selected
            logging.info("No file was selected, when comparing files")
            pass

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
            dir=FF_Files.SAVED_SEARCHES_FOLDER,
            filter="*.FFSearch;")

        # Debug
        logging.debug(f"Second search: {second_search_file}, Reading file...")

        # Load list from file and return path and files
        try:
            with open(second_search_file[0]) as search_file:
                return load(search_file), second_search_file
        except FileNotFoundError:
            # if the user pressed cancel
            return None


compared_searches: CompareSearches
