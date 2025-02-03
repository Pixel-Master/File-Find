# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the 'Compare Search' feature

# Imports
from json import load
import logging
import os
from time import perf_counter, time, ctime
import gc

# PySide6 Gui Imports
from PySide6.QtGui import QFont, Qt
from PySide6.QtCore import QObject, Signal, QThreadPool, QSize
from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QListWidget, QLabel, QPushButton, QWidget, QGridLayout, QHBoxLayout, QScrollArea,
    QSpacerItem, QSizePolicy)

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Main_UI
import FF_Menubar
import FF_Search


# The window
class CompareUi:
    def __init__(self, path_of_first_search, cache_file, parent):
        # Debug
        logging.info("Setting up the Compare_Window")
        # Saving time
        compared_searches.time_dict["time_before_building_ui"] = perf_counter()

        # Set up the Window
        self.Compare_Window = QMainWindow(parent)
        # Set up the window title
        self.Compare_Window.setWindowTitle(
            "File Find | Comparing Searches: "
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
        self.Compare_Layout.setContentsMargins(20, 20, 20, 20)
        self.Compare_Layout.setVerticalSpacing(1)

        # Listbox Layout
        self.Listbox_Layout = QGridLayout(self.Compare_Window)
        self.Listbox_Layout.setContentsMargins(0, 0, 0, 0)
        # Add to main Layout
        self.Compare_Layout.addLayout(self.Listbox_Layout, 3, 0, 8, 2)

        # Bottom Layout
        self.Bottom_Layout = QHBoxLayout(self.Compare_Window)
        self.Bottom_Layout.setContentsMargins(0, 20, 0, 0)
        # Add to main Layout
        self.Compare_Layout.addLayout(self.Bottom_Layout, 11, 0, 1, 2)

        # Setting up the menu bar...
        menu_bar = FF_Menubar.MenuBar(parent=self.Compare_Window, window="compare",
                                      listbox=None, cache_file_path=cache_file)
        logging.debug("Done building MenuBar\n")

        # Set up both list-boxes
        # Added files / files only in first search
        '''Creating a QScrollArea in which the QListWidget is put. This is because QListWidget.setUniformItemSizes(True)
            allows for insane speed gains (up to 100x), but it makes all item the same size (if they are too long it
            will cut them of) so to profit from the speed gains but at the same time not cutting of the file paths, the
            QListWidget (takes care of vertical scrolling)
            is put into a QScrollArea, which takes care of the horizontal scrolling.'''
        # Debug
        logging.debug("Setting up Added files / files only in first search listbox..")
        # Scroll Area
        self.added_files_area = QScrollArea(self.Compare_Window)
        # List widget
        self.added_files_listbox = QListWidget(self.Compare_Window)
        self.added_files_area.setWidget(self.added_files_listbox)
        # Adding to grid
        self.Listbox_Layout.addWidget(self.added_files_area, 0, 0)
        # Show the Listbox
        self.added_files_listbox.show()
        # Double-Clicking Event
        self.added_files_listbox.doubleClicked.connect(menu_bar.double_clicking_item)
        # If there were no files added and the list is empty
        if not compared_searches.files_only_in_first_search:
            self.added_files_listbox.setDisabled(True)
            self.added_files_listbox.addItem("No file of directory found")
        else:
            # If there is at least one file, add all files
            self.added_files_listbox.addItems(compared_searches.files_only_in_first_search)
            # Setting the row to the first
            self.added_files_listbox.setCurrentRow(0)
        # Set scrollbars and optimization
        try:
            # Get the longest file, fails if there is no item, and then multiply by font size to get the length
            self.added_files_listbox.setMinimumWidth(len(max(compared_searches.files_only_in_first_search, key=len))
                                                     * self.added_files_listbox.font().pointSize())
        except ValueError:
            pass
        # Setting all the Scrollbars
        self.added_files_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.added_files_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.added_files_listbox.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Optimisations
        self.added_files_area.setWidgetResizable(True)
        self.added_files_listbox.setUniformItemSizes(True)
        # Moving the Scrollbar into the right place, so it's always visible
        self.Listbox_Layout.addWidget(self.added_files_listbox.verticalScrollBar(), 0, 0,
                                      Qt.AlignmentFlag.AlignRight)

        # Removed files / files only in second search
        # Debug
        logging.debug("Done!, Setting up Removed files / files only in second search listbox..")

        # Scroll Area
        self.removed_files_area = QScrollArea(self.Compare_Window)
        # List widget
        self.removed_files_listbox = QListWidget(self.Compare_Window)
        self.removed_files_area.setWidget(self.removed_files_listbox)
        # Adding to grid
        self.Listbox_Layout.addWidget(self.removed_files_area, 0, 1)
        # Show the Listbox
        self.removed_files_listbox.show()
        # Double-Clicking Event
        self.removed_files_listbox.doubleClicked.connect(menu_bar.double_clicking_item)
        # If there were no files removed and the list is empty
        if not compared_searches.files_only_in_second_search:
            self.removed_files_listbox.setDisabled(True)
            self.removed_files_listbox.addItem("No file of directory found")
        else:
            # If there is at least one file, add all files
            self.removed_files_listbox.addItems(compared_searches.files_only_in_second_search)
            # Setting the row to the second
            self.removed_files_listbox.setCurrentRow(0)
        # Set scrollbars and optimization
        try:
            # Get the longest file, fails if there is no item, and then multiply by font size to get the length
            self.removed_files_listbox.setMinimumWidth(len(max(compared_searches.files_only_in_second_search, key=len))
                                                       * self.removed_files_listbox.font().pointSize())
        except ValueError:
            pass
        # Setting all the Scrollbars
        self.removed_files_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.removed_files_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.removed_files_listbox.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Optimisations
        self.removed_files_area.setWidgetResizable(True)
        self.removed_files_listbox.setUniformItemSizes(True)
        # Moving the Scrollbar into the right place, so it's always visible
        self.Listbox_Layout.addWidget(self.removed_files_listbox.verticalScrollBar(), 0, 1,
                                      Qt.AlignmentFlag.AlignRight)
        # Debug
        logging.debug("Done!")

        # Labels
        # Added files
        self.added_files_label1, self.added_files_label2 = self.generate_title_label(
            text="Added Files", text2=path_of_first_search,
            light_color=FF_Files.GREEN_LIGHT_THEME_COLOR,
            dark_color=FF_Files.GREEN_DARK_THEME_COLOR,
            length_of_list=len(compared_searches.files_only_in_first_search))
        self.Compare_Layout.addWidget(self.added_files_label1, 1, 0)
        self.Compare_Layout.addWidget(self.added_files_label2, 2, 0)

        # Removed files
        self.removed_files_label1, self.removed_files_label2 = self.generate_title_label(
            text="Removed Files", text2=compared_searches.path_of_second_search[0],
            light_color=FF_Files.RED_LIGHT_THEME_COLOR,
            dark_color=FF_Files.RED_DARK_THEME_COLOR,
            length_of_list=len(compared_searches.files_only_in_second_search))
        self.Compare_Layout.addWidget(self.removed_files_label1, 1, 1)
        self.Compare_Layout.addWidget(self.removed_files_label2, 2, 1)

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

        # Update search status label
        FF_Search.ACTIVE_SEARCH_THREADS -= 1
        FF_Main_UI.MainWindow.update_search_status_label()

        compared_searches.time_dict["time_after_building_ui"] = perf_counter()
        comparing_time = (
                compared_searches.time_dict['time_before_building_ui'] - compared_searches.time_dict['start_time'])
        building_time = (compared_searches.time_dict['time_after_building_ui'] -
                         compared_searches.time_dict['time_before_building_ui'])
        total_time = compared_searches.time_dict['time_after_building_ui'] - compared_searches.time_dict['start_time']

        logging.info(
            f"\nSeconds needed:\n"
            f"Comparing: {comparing_time}\n"
            f"Building UI: {building_time}\n"
            f"Total: {total_time}")

        time_stamp = time()

        # Setting a Font
        small_text_font = QFont(FF_Files.DEFAULT_FONT, FF_Files.NORMAL_FONT_SIZE)
        small_text_font.setBold(True)

        # Top Layout
        self.Top_Layout = QHBoxLayout()
        self.Top_Layout.setContentsMargins(0, 0, 0, 0)
        self.Compare_Layout.addLayout(self.Top_Layout, 0, 0, 1, 2)

        # Time needed
        time_text = QLabel(self.Compare_Window)
        total_time = compared_searches.time_dict["time_after_building_ui"] - compared_searches.time_dict["start_time"]
        time_text.setText(f"Time needed: {round(total_time, 3)}s")
        time_text.setFont(small_text_font)
        # Displaying
        self.Top_Layout.addWidget(time_text)

        # Saving time
        # Time stat Button
        show_time = self.generate_button(None, lambda: show_time_stats(),
                                         icon=os.path.join(FF_Files.ASSETS_FOLDER, "Time_button_img_small.png"))
        # Resize
        show_time.setMaximumSize(50, 50)
        # Add to Layout
        self.Top_Layout.addWidget(show_time, alignment=Qt.AlignmentFlag.AlignLeft)

        # Add a Stretcher
        self.Top_Layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum))

        # Show more time info's
        def show_time_stats():
            # Debug
            logging.debug("Displaying time stats.")

            # Getting the creation time of the cache file which is stored separately
            with open(FF_Files.path_to_cache_file(path_of_first_search, True)) as time_file1:
                # Load time
                search1_created_time = ctime(load(time_file1)["c_time"])
            # Getting the creation time of the cache file which is stored separately
            with open(FF_Files.path_to_cache_file(compared_searches.path_of_second_search[0], True)) as time_file2:
                search2_created_time = ctime(load(time_file2)["c_time"])

            # Displaying infobox with time info
            FF_Additional_UI.PopUps.show_info_messagebox(
                "Time Stats",
                "Time needed:\n"
                f"Comparing: {round(comparing_time, 3)}s\n"
                f"Creating UI: {round(building_time, 3)}s"
                "\n---------\n"
                f"Total: {round(total_time, 3)}s\n\n\n"
                ""
                "Timestamps:\n"
                f"Base Search ({FF_Files.display_path(path_of_first_search, 60)}):\n{search1_created_time}\n"
                f"Second Search ({FF_Files.display_path(compared_searches.path_of_second_search[0], 60)}):"
                f"\n{search2_created_time}\n\n"
                f"Window opened: {ctime(time_stamp)}s",
                large=True,
                parent=self.Compare_Window)

        # Debug
        logging.info("Done building Compare-UI!\n")

        # Collect garbage
        gc.collect()

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
            FF_Additional_UI.UIIcon(icon, button.setIcon)
            button.setIconSize(QSize(23, 22))
        # Return the value of the Button, to move the Button
        return button

    # Function for generating the added / removed files labels
    def generate_title_label(self, text, text2, light_color, dark_color, length_of_list) -> tuple[QLabel, QLabel]:
        # Label 1
        label1 = FF_Additional_UI.ColoredLabel(text, self.Compare_Window, light_color, dark_color)

        # Defining the font
        font1 = QFont(FF_Files.DEFAULT_FONT, FF_Files.NORMAL_FONT_SIZE)
        font1.setBold(True)
        label1.setFont(font1)

        label1.setFixedHeight(FF_Files.NORMAL_FONT_SIZE + 2)
        label1.adjustSize()

        # Label 2
        label2 = QLabel(self.Compare_Window)

        # Set the text, the font and the color

        # Shorten the text string to only include the first to the 30th
        # and the last ten character if the string is longer then 43 characters
        text2_shortened = f"{length_of_list} files only in:\n{FF_Files.display_path(text2, 30)}"
        # Set the label to the shortened string
        label2.setText(text2_shortened)

        # Defining the font
        font2 = QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE)
        # Configure the font
        label2.setFont(font2)
        # Times two because it is two lines and plus two for some extra space
        label2.setFixedHeight(FF_Files.SMALLER_FONT_SIZE * 2 + 5)

        return label1, label2


# The engine
class CompareSearches:
    def __init__(self, files_of_first_search: list, path_of_first_search, cache_file, parent):
        # Debug
        logging.debug("User pressed Compare Search")

        try:
            # Setting the thread up with the Qt6 signals to launch the ui
            class SignalsClass(QObject):
                finished = Signal()

            self.signals = SignalsClass()
            # Connecting the signal to the user-interface class
            self.signals.finished.connect(lambda: CompareUi(path_of_first_search, cache_file, parent))

            # Thread
            comparing_thread = QThreadPool(parent)

            # Get the files of both searches
            self.files_of_first_search = files_of_first_search
            logging.debug("Asking for a second File Find Search file...")
            self.files_of_second_search, self.path_of_second_search = self.load_second_search()

            # Setting up the UI-logging
            logging.info("Setting up the UI-logging and the search status label...")
            # Update search status label
            FF_Search.ACTIVE_SEARCH_THREADS += 1
            FF_Main_UI.MainWindow.update_search_status_label()
            # Initialising the ui logger
            self.ui_logger = FF_Main_UI.SearchUpdate(f"{path_of_first_search} and {self.path_of_second_search[0]}")
            # Update the logger
            self.ui_logger.update("Comparing searches...")
            # Closing the menu bar logger when finished
            self.signals.finished.connect(self.ui_logger.close)
            # Saving time
            self.time_dict = {"start_time": perf_counter()}

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
        logging.debug("Comparing searches, finding differences...")

        # Converting the lists to sets for a faster lockup
        first_search_files_set = set(self.files_of_first_search)
        second_search_files_set = set(self.files_of_second_search)

        for file_in_first_search in self.files_of_first_search:
            if not (file_in_first_search in second_search_files_set):
                self.files_only_in_first_search.append(file_in_first_search)

        for file_in_second_search in self.files_of_second_search:
            if not (file_in_second_search in first_search_files_set):
                self.files_only_in_second_search.append(file_in_second_search)

        del first_search_files_set, second_search_files_set
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
            dir=FF_Files.USER_FOLDER,
            filter="*.FFSearch;")

        # Debug
        logging.debug(f"Second search: {second_search_file}, Reading file...")

        # Load list from file and return path and files
        return FF_Search.LoadSearch.load_search_content(second_search_file[0])["matched_list"], second_search_file


global compared_searches
