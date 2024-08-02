# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for finding duplicated files and the UI

# Imports
import logging
import os
from sys import platform
from time import perf_counter, time, ctime
import difflib
import gc
import hashlib

# PySide6 Gui Imports
from PySide6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QSpinBox,
                               QDialogButtonBox, QSpacerItem, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem,
                               QComboBox)
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThreadPool
from PySide6.QtGui import QFont, QAction

# Projects Libraries
import FF_Menubar
import FF_Additional_UI
import FF_Files
import FF_About_UI
import FF_Search

# Global variables
global duplicated_dict, time_dict, duplicated_parent_file_path_dict


class DuplicatedSettings:
    def __init__(self, parent, search_path, matched_list):
        # Debug
        logging.info("Setting up Duplicated UI...")

        # Window setup
        # Define the window
        self.Duplicated_Settings = QMainWindow(parent)
        # Set the Title of the Window
        self.Duplicated_Settings.setWindowTitle(f"Find duplicated in: {FF_Files.display_path(search_path)}")
        # Set the start size of the Window, because it's resizable
        self.BASE_WIDTH = 350
        self.BASE_HEIGHT = 300
        self.Duplicated_Settings.setBaseSize(self.BASE_WIDTH, self.BASE_HEIGHT)
        # Display the Window
        self.Duplicated_Settings.show()

        # Adding Layouts
        # Main Layout
        # Create a central widget
        self.Central_Widget = QWidget(parent=self.Duplicated_Settings)
        self.Duplicated_Settings.setCentralWidget(self.Central_Widget)
        # Create the main Layout
        self.Duplicated_Settings_Layout = QVBoxLayout(self.Central_Widget)
        self.Duplicated_Settings_Layout.setContentsMargins(20, 20, 20, 20)

        self.Central_Widget.setLayout(self.Duplicated_Settings_Layout)

        # Upper Horizontal Layout
        self.vertical_layout = QHBoxLayout(self.Duplicated_Settings)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Middle Horizontal Layout
        self.Middle_Layout = QHBoxLayout(self.Duplicated_Settings)
        self.Middle_Layout.setContentsMargins(0, 0, 0, 0)

        # Lower Horizontal Layout
        self.Lower_Layout = QHBoxLayout(self.Duplicated_Settings)
        self.Lower_Layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        self.title_label = QLabel(parent=self.Duplicated_Settings)
        self.title_label.setText(f"Duplicated files in results of search in:"
                                 f"\n{FF_Files.display_path(search_path, 45)}")
        self.title_label.setToolTip(search_path)
        # Make the Font bigger
        font = self.title_label.font()
        font.setBold(True)
        font.setPixelSize(18)
        self.title_label.setFont(font)
        # Adjust size
        self.title_label.adjustSize()
        self.Duplicated_Settings_Layout.addWidget(self.title_label)

        # Duplicated mode label
        self.duplicated_mode_label = QLabel(parent=self.Duplicated_Settings)
        self.duplicated_mode_label.setText("Duplicated mode:")
        self.Middle_Layout.addWidget(self.duplicated_mode_label)

        # Combobox for selecting mode
        self.mode_selector_combobox = QComboBox()
        self.duplicated_mode_display_name_dict = {
            "name": "File name",
            "size": "File size (faster than File content)",
            "content": "File content"}
        self.mode_selector_combobox.addItems([self.duplicated_mode_display_name_dict["name"],
                                              self.duplicated_mode_display_name_dict["size"],
                                              self.duplicated_mode_display_name_dict["content"]])
        self.mode_selector_combobox.setMinimumSize(300, 50)
        # Add it to the other layout
        self.Middle_Layout.addWidget(self.mode_selector_combobox)

        # Add the layout to the main layout
        self.Duplicated_Settings_Layout.addLayout(self.Middle_Layout)

        # Match percentage label
        self.match_label = QLabel(parent=self.Duplicated_Settings)
        self.match_label.setText("Files must match at least (percentage):")
        self.Duplicated_Settings_Layout.addWidget(self.match_label)

        # Slider
        self.slider = QSlider(parent=self.Duplicated_Settings)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 100)
        self.vertical_layout.addWidget(self.slider)
        # Spinbox
        self.spinbox = QSpinBox(parent=self.Duplicated_Settings)
        self.spinbox.setMaximum(100)
        self.vertical_layout.addWidget(self.spinbox)
        # Connecting slider and Spinbox
        self.spinbox.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.spinbox.setValue)
        # Set value to 100 %
        self.spinbox.setValue(100)

        # Deactivate and activate the slider and spinbox if content is selected
        def de_activate_content():
            if self.mode_selector_combobox.currentText() == self.duplicated_mode_display_name_dict["content"]:
                logging.debug("deactivating content")
                self.match_label.setDisabled(True)
                self.slider.setDisabled(True)
                self.spinbox.setDisabled(True)
                # Set it to 100%
                self.spinbox.setValue(100)

            else:
                logging.debug("activating name")
                self.match_label.setDisabled(False)
                self.slider.setDisabled(False)
                self.spinbox.setDisabled(False)
                # Set it to the saved value
                self.spinbox.setValue(self.saved_value)

        # Connecting
        self.mode_selector_combobox.currentTextChanged.connect(de_activate_content)

        # Store value to insert it, if content is deactivated
        def store_value():
            # Only if anything else than content is activated
            if self.mode_selector_combobox.currentText() != self.duplicated_mode_display_name_dict["content"]:
                self.saved_value = self.spinbox.value()

        self.spinbox.valueChanged.connect(store_value)

        # Default
        self.saved_value = 100

        # Add to main Layout
        self.Duplicated_Settings_Layout.addLayout(self.vertical_layout)

        # Sorting mode label
        self.sorting_mode_label = QLabel(parent=self.Duplicated_Settings)
        self.sorting_mode_label.setText("Sorting mode:")
        self.Lower_Layout.addWidget(self.sorting_mode_label)

        # Combobox for selecting mode
        self.sorting_selector_combobox = QComboBox()
        self.sorting_selector_combobox.addItems(["None (fastest)",
                                                 "File Name",
                                                 "File Size",
                                                 "Date Modified",
                                                 "Date Created",
                                                 "Path"])
        # Set a fixed minimum size
        self.sorting_selector_combobox.setMinimumSize(300, 50)
        # Add it to the other layout
        self.Lower_Layout.addWidget(self.sorting_selector_combobox)

        # Add the layout to the main layout
        self.Duplicated_Settings_Layout.addLayout(self.Lower_Layout)

        # Add a Spacer for prettier ui
        self.Duplicated_Settings_Layout.addItem(QSpacerItem(10, 30, hData=QSizePolicy.Policy.Maximum))

        # Okay and Cancel button
        self.button_box = QDialogButtonBox(parent=self.Duplicated_Settings)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        # Connect events
        def start_duplicated():

            # Default criteria
            criteria = {
                "name": {"activated": False,
                         "match_percentage": self.spinbox.value()},
                "size": {"activated": False,
                         "match_percentage": self.spinbox.value()},
                "content": {"activated": False,
                            "match_percentage": self.spinbox.value()},
                "sorting": self.sorting_selector_combobox.currentText()}

            # Events for threading
            class Events(QObject):
                finished = Signal()

            finished_event_class = Events()

            if self.mode_selector_combobox.currentText() == self.duplicated_mode_display_name_dict["name"]:
                criteria["name"]["activated"] = True
            elif self.mode_selector_combobox.currentText() == self.duplicated_mode_display_name_dict["size"]:
                criteria["size"]["activated"] = True
            elif self.mode_selector_combobox.currentText() == self.duplicated_mode_display_name_dict["content"]:
                criteria["content"]["activated"] = True

            # Starting Thread
            QThreadPool(self.Duplicated_Settings).start(
                lambda: FindDuplicated(
                    criteria=criteria,
                    matched_list=matched_list,
                    finished_signal=finished_event_class))

            # Connect UI to finished signal
            finished_event_class.finished.connect(
                lambda: DuplicatedUI(
                    parent, search_path, criteria, duplicated_dict, duplicated_parent_file_path_dict, time_dict))

        # Launch search algorithm
        self.button_box.button(
            QDialogButtonBox.StandardButton.Ok).clicked.connect(start_duplicated)

        self.button_box.button(
            QDialogButtonBox.StandardButton.Cancel).clicked.connect(
            self.Duplicated_Settings.close)

        self.button_box.button(
            QDialogButtonBox.StandardButton.Ok).clicked.connect(
            self.Duplicated_Settings.close)

        self.Duplicated_Settings_Layout.addWidget(self.button_box)

        self.Duplicated_Settings.show()

        # Menu bar
        menu_bar = self.Duplicated_Settings.menuBar()

        # Menus
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Close Window
        close_action = QAction("&Close Window", self.Duplicated_Settings)
        close_action.triggered.connect(self.Duplicated_Settings.close)
        close_action.setShortcut("Ctrl+W")
        window_menu.addAction(close_action)

        # About File Find
        about_action = QAction("&About File Find", self.Duplicated_Settings)
        about_action.triggered.connect(lambda: FF_About_UI.AboutWindow(parent))
        help_menu.addAction(about_action)

        # About
        help_action = QAction("&About File Find", self.Duplicated_Settings)
        help_action.triggered.connect(lambda: FF_About_UI.AboutWindow(parent))
        help_menu.addAction(help_action)

        # Tutorial
        tutorial_action = QAction("&Tutorial", self.Duplicated_Settings)
        tutorial_action.triggered.connect(lambda: FF_Additional_UI.welcome_popups(parent, force_popups=True))
        help_menu.addAction(tutorial_action)

        # Debug
        logging.info("Finished Setting up Duplicated UI\n")
        logging.info("Finished duplicated question setup!\n\n")


# User interface
class DuplicatedUI:
    def __init__(
            self,
            parent,
            match_path,
            criteria, matched_dict: dict, matched_parent_file_path_dict: dict, time_needed_dict: dict):
        # Debug
        logging.info("Setting up Duplicated UI...")
        # Saving time
        time_needed_dict["time_before_building_ui"] = perf_counter()

        # Window setup
        # Define the window
        self.Duplicated_Window = QMainWindow(parent)
        # Set the Title of the Window
        self.Duplicated_Window.setWindowTitle(f"Duplicated files in {FF_Files.display_path(match_path, 80)}")
        # Set the start size of the Window, because it's resizable
        self.BASE_WIDTH = 700
        self.BASE_HEIGHT = 700
        self.Duplicated_Window.setBaseSize(self.BASE_WIDTH, self.BASE_HEIGHT)
        # Display the Window
        self.Duplicated_Window.show()

        # Adding Layouts
        # Main Layout
        # Create a central widget
        self.Central_Widget = QWidget(self.Duplicated_Window)
        self.Duplicated_Window.setCentralWidget(self.Central_Widget)
        # Create the main Layout
        self.Duplicated_Layout = QGridLayout(self.Central_Widget)
        self.Duplicated_Layout.setContentsMargins(20, 20, 20, 20)
        self.Duplicated_Layout.setVerticalSpacing(20)

        # Bottom Layout
        self.Bottom_Layout = QHBoxLayout(self.Duplicated_Window)
        self.Bottom_Layout.setContentsMargins(0, 0, 0, 0)
        # Add to main Layout
        self.Duplicated_Layout.addLayout(self.Bottom_Layout, 10, 0, 1, 8)

        # Main Tree Widget
        self.Duplicated_Tree = QTreeWidget(self.Duplicated_Window)
        self.Duplicated_Tree.headerItem().setText(0, "Path")
        self.Duplicated_Tree.headerItem().setText(1, "Size")
        self.Duplicated_Tree.setColumnWidth(1, 20)
        self.Duplicated_Tree.setColumnWidth(0, 550)
        self.Duplicated_Tree.horizontalScrollBar().show()

        # Replacing the keys which is size or a filename and replacing them with absolute paths
        for file_name in matched_dict.copy():
            # Taking a name like "name.pdf" and converting it to an absolute path
            matched_dict[matched_parent_file_path_dict[file_name]] = matched_dict[file_name]
            # Removing it
            del matched_dict[file_name]

        matched_sorted_list = list(matched_dict.keys())

        # Sorting
        if criteria["sorting"] == "File Name":
            logging.info("Sorting list by name...")
            # Sort the main files
            matched_sorted_list.sort(key=FF_Search.Sort.name)
            # Sort files in file groups
            for sub_file_set_key in matched_sorted_list:
                matched_dict[sub_file_set_key] = sorted(list(matched_dict[sub_file_set_key]), key=FF_Search.Sort.name)

        elif criteria["sorting"] == "File Size":
            logging.info("Sorting list by size...")
            # Sort the main files
            matched_sorted_list.sort(key=FF_Search.Sort.size, reverse=True)
            # Sort files in file groups
            for sub_file_set_key in matched_sorted_list:
                matched_dict[sub_file_set_key] = sorted(
                    list(matched_dict[sub_file_set_key]), key=FF_Search.Sort.size, reverse=True)

        elif criteria["sorting"] == "Date Created":
            logging.info(f"Sorting list by creation date on {platform}...")
            # On Windows and Linux
            # (On Linux this currently returns the modification date,
            # because it's impossible to access with pure python)
            if platform == "win32" or platform == 'cygwin' or platform == "linux":
                # Sort the main files
                matched_sorted_list.sort(key=FF_Search.Sort.c_date_win)
                # Sort files in file groups
                for sub_file_set_key in matched_sorted_list:
                    matched_dict[sub_file_set_key] = sorted(list(matched_dict[sub_file_set_key]),
                                                            key=FF_Search.Sort.c_date_win)

            # On Mac
            if platform == "darwin":
                # Sort the main files
                matched_sorted_list.sort(key=FF_Search.Sort.c_date_mac)
                # Sort files in file groups
                for sub_file_set_key in matched_sorted_list:
                    matched_dict[sub_file_set_key] = sorted(list(matched_dict[sub_file_set_key]),
                                                            key=FF_Search.Sort.c_date_mac)

        elif criteria["sorting"] == "Date Modified":
            logging.info("Sorting list by modification date...")
            # Sort the main files
            matched_sorted_list.sort(key=FF_Search.Sort.m_date)
            # Sort files in file groups
            for sub_file_set_key in matched_sorted_list:
                matched_dict[sub_file_set_key] = sorted(list(matched_dict[sub_file_set_key]), key=FF_Search.Sort.m_date)

        elif criteria["sorting"] == "Path":
            logging.info("Sorting list by path...")
            # Sort the main files
            matched_sorted_list.sort(key=lambda sort_file: sort_file.lower())
            # Sort files in file groups
            for sub_file_set_key in matched_sorted_list:
                matched_dict[sub_file_set_key] = sorted(
                    list(matched_dict[sub_file_set_key]), key=lambda sort_file: sort_file.lower())

        else:
            logging.info("Skipping Sorting")

        # Iterating through the list of all groups
        for main_item in matched_sorted_list:
            # main item
            main_tree_item = QTreeWidgetItem(self.Duplicated_Tree)

            # Iterating through the set of single files under the key
            for sub_item in matched_dict[main_item]:
                sub_tree_item = QTreeWidgetItem(main_tree_item)

                sub_tree_item.setText(0, sub_item)
                sub_tree_item.setText(1, FF_Files.conv_file_size(FF_Files.get_file_size(sub_item)))
                sub_tree_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)

            # Set the text
            main_tree_item.setText(0, main_item)
            main_tree_item.setText(1, FF_Files.conv_file_size(FF_Files.get_file_size(main_item)))
            main_tree_item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)

        # Add the model to the final
        self.Duplicated_Layout.addWidget(self.Duplicated_Tree, 1, 0, 5, 8)

        # Setup menu bar
        menu_bar = FF_Menubar.MenuBar(
            parent=self.Duplicated_Window, window="duplicated", listbox=self.Duplicated_Tree, search_path=match_path)

        # If item is double-clicked
        def open_double_clicked(item):
            # Only if subdirectory is clicked
            if item.text(0) != os.path.basename(item.text(0)):
                menu_bar.double_clicking_item()

        self.Duplicated_Tree.itemDoubleClicked.connect(open_double_clicked)

        # Buttons
        # Functions to automate Button
        def generate_button(text, command, icon=None):
            # Define the Button
            button = QPushButton(self.Duplicated_Window)
            # Change the Text
            button.setText(text)
            # Set the command
            button.clicked.connect(command)
            # Set the icon
            if icon is not None:
                FF_Additional_UI.UIIcon(icon, button.setIcon)
                button.setIconSize(QSize(23, 23))
            # Return the value of the Button, to move the Button
            return button

        # Button to open the File in Finder
        move_file = generate_button("Move / Rename", menu_bar.move_file,
                                    icon=os.path.join(FF_Files.ASSETS_FOLDER, "Move_icon_small.png"))
        self.Bottom_Layout.addWidget(move_file)

        # Button to move the file to trash
        delete_file = generate_button("Move to Trash", menu_bar.delete_file,
                                      icon=os.path.join(FF_Files.ASSETS_FOLDER, "Trash_icon_small.png"))
        self.Bottom_Layout.addWidget(delete_file)

        # Button to open the file
        open_file = generate_button("Open", menu_bar.open_file,
                                    icon=os.path.join(FF_Files.ASSETS_FOLDER, "Open_icon_small.png"))
        self.Bottom_Layout.addWidget(open_file)

        # Button to show info about the file
        file_info_button = generate_button("Info", menu_bar.file_info,
                                           icon=os.path.join(FF_Files.ASSETS_FOLDER, "Info_button_img_small.png"))
        self.Bottom_Layout.addWidget(file_info_button)

        # Setting a Font
        small_text_font = QFont(FF_Files.DEFAULT_FONT, FF_Files.NORMAL_FONT_SIZE)
        small_text_font.setBold(True)

        # Files found label
        objects_text = QLabel(self.Duplicated_Window)
        objects_text.setText(f"Duplicated files: {len(matched_dict)}")
        objects_text.setFont(small_text_font)

        # Displaying
        self.Duplicated_Layout.addWidget(objects_text, 0, 4, Qt.AlignmentFlag.AlignRight)

        # Time needed
        time_text = QLabel(self.Duplicated_Window)
        time_text.setText("Time needed:")
        time_text.setFont(small_text_font)
        # Displaying
        self.Duplicated_Layout.addWidget(time_text, 0, 0)

        # Saving time
        # Time stat Button
        show_time = generate_button(None, lambda: show_time_stats(),
                                    icon=os.path.join(FF_Files.ASSETS_FOLDER, "Time_button_img_small.png"))
        # Resize
        show_time.setMaximumSize(50, 50)
        # Add to Layout
        self.Duplicated_Layout.addWidget(show_time, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        time_needed_dict["time_after_building_ui"] = perf_counter()

        logging.info(f"\nSeconds needed:\n"
                     f"Indexing: {time_needed_dict['time_before_building_ui'] - time_needed_dict['start_time']}\n"
                     f"Building UI: "
                     f"{time_needed_dict['time_after_building_ui'] - time_needed_dict['time_before_building_ui']}\n"
                     f"Total: {time_needed_dict['time_after_building_ui'] - time_needed_dict['start_time']}")

        time_stamp = time()

        # Show more time info's
        def show_time_stats():
            # Debug
            logging.debug("Displaying time stats.")

            # Displaying infobox with time info
            FF_Additional_UI.PopUps.show_info_messagebox(
                "Time Stats",
                f"Time needed:\n"
                f"Indexing: {round(time_needed_dict['time_before_building_ui'] - time_needed_dict['start_time'], 3)}s\n"
                f"Creating UI: "
                f"{round(time_needed_dict['time_after_building_ui'] - time_needed_dict['time_before_building_ui'], 3)}s"
                f"\n---------\n"
                f"Total: {round(time_needed_dict['time_after_building_ui'] - time_needed_dict['start_time'], 3)}s\n\n\n"
                ""
                f"Timestamps:\n"
                f"Search opened: {ctime(time_stamp)}s",
                self.Duplicated_Window)

        # Optimize label
        total_time = time_needed_dict["time_after_building_ui"] - time_needed_dict["start_time"]
        time_text.setText(f"Time needed: {round(total_time, 3)}s")

        # Collect garbage
        gc.collect()


# Algorithms to find duplicated files
class FindDuplicated:
    def __init__(self, criteria: dict, matched_list, finished_signal):
        # Debug
        logging.info("Searching for duplicated files...")
        logging.info(f"{criteria = }")

        # Global variables
        global duplicated_dict, time_dict, duplicated_parent_file_path_dict

        # Saving time
        time_dict = {"start_time": perf_counter()}

        found_path_set = matched_list

        # Content checking always requires size checking
        if criteria["content"]["activated"]:
            criteria["size"]["activated"] = True
            criteria["size"]["match_percentage"] = criteria["content"]["match_percentage"]

        logging.debug("Finished loading cache")

        # Sort by name
        if criteria["name"]["activated"]:
            # Debug
            logging.debug(f"Grouping by name, {criteria['name']['match_percentage'] = }")

            exists_already = set()
            duplicated_name_dict = {}
            # Dict for storing names to be displayed
            duplicated_name_parent_file_path_dict = {}
            # Group by name1
            if criteria["name"]["match_percentage"] == 100:

                for file in found_path_set:
                    # Get the basename, ignoring case
                    low_basename = os.path.basename(file).lower()

                    if low_basename not in exists_already:
                        # Add the file to the dictionaries
                        exists_already.add(low_basename)
                        duplicated_name_dict[low_basename] = set()
                        duplicated_name_parent_file_path_dict[low_basename] = file

                    else:
                        # Add the file to the duplicated dict
                        duplicated_name_dict[low_basename].add(file)

            else:

                match_factor = criteria["name"]["match_percentage"] / 100

                # Iterating through all files
                for file in found_path_set:
                    # Get the basename, ignoring case
                    low_basename = os.path.basename(file).lower()
                    # If low_basename isn't already in exist already_text if there is something in the allowed range
                    if low_basename not in exists_already:

                        # If this is the first file being iterated
                        if exists_already == set():
                            exists_already.add(low_basename)
                            duplicated_name_dict[low_basename] = set()
                            duplicated_name_parent_file_path_dict[low_basename] = file
                            continue

                        # Get the closest match, over the match factor. Function returns a list
                        closest_match = difflib.get_close_matches(
                            low_basename, exists_already, n=1, cutoff=match_factor)

                        # There is no match (empty list) with the file, add it to exists_already
                        if not closest_match:
                            exists_already.add(low_basename)
                            duplicated_name_dict[low_basename] = set()
                            duplicated_name_parent_file_path_dict[low_basename] = file

                        # Add it to the closest match
                        else:
                            # Take tho only element of the list
                            duplicated_name_dict[closest_match[0]].add(file)

                    else:
                        # Add the file to the duplicated dict
                        duplicated_name_dict[low_basename].add(file)

            # Removing sets that have no duplicates
            for duplicated_file in duplicated_name_dict.copy():
                if len(duplicated_name_dict[duplicated_file]) <= 1:
                    duplicated_name_dict.pop(duplicated_file)

            # Finalize
            duplicated_parent_file_path_dict = duplicated_name_parent_file_path_dict
            duplicated_dict = duplicated_name_dict

        # Group by size
        if criteria["size"]["activated"]:
            # Debug
            logging.debug(f"Grouping by size, {criteria['size']['match_percentage'] = }")

            exists_already = set()
            duplicated_size_dict = {}
            duplicated_size_parent_file_path_dict = {}

            # If the percentage of
            if criteria["size"]["match_percentage"] == 100:
                for file in found_path_set:
                    try:
                        size = FF_Files.get_file_size(file)
                    except FileNotFoundError:
                        continue

                    if size not in exists_already:
                        # Add the file to the dictionary
                        exists_already.add(size)
                        duplicated_size_dict[size] = set()
                        duplicated_size_parent_file_path_dict[size] = file

                    else:
                        # Add the file to the duplicated dict
                        duplicated_size_dict[size].add(file)

            else:
                # factor of allowed divergence
                # factor 1, upper = 1, lower = 1
                # factor 0.8, upper = 1.2, lower = 0.8
                # factor 0.4, upper = 1.6, lower = 0.8
                lower_allowed_divergence_factor = criteria["size"]["match_percentage"] / 100
                upper_allowed_divergence_factor = 1 + (1 - lower_allowed_divergence_factor)

                logging.info(f"{lower_allowed_divergence_factor = }, {upper_allowed_divergence_factor = }")

                for file in found_path_set:

                    # Try getting the size
                    try:
                        size = FF_Files.get_file_size(file)
                    except OSError:
                        continue

                    if size not in exists_already:

                        # If exist already is empty
                        if not exists_already == set():
                            # Get the closest match
                            closest_match = sorted(
                                exists_already,
                                key=lambda file_size: self.sort_size(list_file_size=file_size, file_size=size))[0]
                        else:
                            closest_match = -1

                        if lower_allowed_divergence_factor <= closest_match <= upper_allowed_divergence_factor:
                            # Add the file to the closest match
                            duplicated_size_dict[closest_match].add(file)
                            # Next file
                            continue

                        # If there really isn't anything in the allowed range
                        else:
                            # Add the file to the exists_already
                            exists_already.add(size)
                            duplicated_size_dict[size] = set()
                            duplicated_size_parent_file_path_dict[size] = file

                    # If there is an exact duplicate
                    else:
                        # Add the file to the duplicated dict
                        duplicated_size_dict[size].add(file)
                        continue

            # Removing sets that have no duplicates
            for duplicated_file in duplicated_size_dict.copy():
                if len(duplicated_size_dict[duplicated_file]) <= 1:
                    duplicated_size_dict.pop(duplicated_file)

            # If content is activated size is ALWAYS checked first
            if criteria["content"]["activated"]:
                # Debug
                logging.debug(f"Grouping by content, {criteria['content']['match_percentage'] = }")

                # Getting file that have a chance of being duplicated
                duplicated_files = set()
                for duplicated_file_set_key in duplicated_size_dict.keys():
                    for duplicated_file in duplicated_size_dict[duplicated_file_set_key]:
                        duplicated_files.add(duplicated_file)

                duplicated_content_dict = {}
                duplicated_content_parent_file_path_dict = {}
                exists_already = set()

                # If files must match exactly
                if criteria["content"]["match_percentage"] == 100:

                    # Buffer size
                    buffer_size = 65536

                    # Iterating through all files that have the same size
                    for file in duplicated_files:

                        # If the file isn't a folder
                        if os.path.isfile(file):
                            # Open every file
                            try:
                                with open(file, "rb") as open_hash_file:
                                    # Initializing the sha1() method
                                    computing_hash = hashlib.sha1(usedforsecurity=False)

                                    # Loading the file into the hash function
                                    while True:
                                        # reading data = BUF_SIZE from the
                                        # file and saving it in a variable
                                        data = open_hash_file.read(buffer_size)

                                        # True if eof = 1
                                        if not data:
                                            break
                                        # Updating hash
                                        computing_hash.update(data)

                                    # Getting hash in hex form
                                    file_hash = computing_hash.hexdigest()
                            except OSError:
                                continue
                        else:
                            # If the file is a folder
                            # Test if the folder is empty
                            if not os.listdir(file):
                                continue
                            # Initializing the sha1() method
                            computing_hash = hashlib.sha1(usedforsecurity=False)

                            # Walk through all folders
                            for (root_dir, _folders, files) in os.walk(file):
                                for sub_file in files:
                                    try:
                                        with open(os.path.join(root_dir, sub_file), "rb") as open_hash_file:

                                            # Loading the file into the hash function
                                            while True:
                                                # reading data = BUF_SIZE from the
                                                # file and saving it in a variable
                                                data = open_hash_file.read(buffer_size)

                                                # True if eof = 1
                                                if not data:
                                                    break
                                                # Updating hash
                                                computing_hash.update(data)

                                    except OSError:
                                        continue
                            # Getting hash in hex form
                            file_hash = computing_hash.hexdigest()

                        # If everything ran successful
                        # If hash doesn't already exist
                        if file_hash not in exists_already:
                            exists_already.add(file_hash)
                            duplicated_content_dict[file_hash] = set()
                            duplicated_content_parent_file_path_dict[file_hash] = file

                        # If hash exists
                        else:
                            duplicated_content_dict[file_hash].add(file)

                # TODO: If match percentage is not 100% use pHash
                else:
                    pass

                # Removing sets that have no duplicates
                for duplicated_file in duplicated_content_dict.copy():
                    # If set lengths is only 1, that means there are no files that are the same
                    if len(duplicated_content_dict[duplicated_file]) <= 1:
                        duplicated_content_dict.pop(duplicated_file)

                    elif os.path.isdir(duplicated_file):
                        duplicated_content_dict.pop(duplicated_file)

                # Finalize
                duplicated_parent_file_path_dict = duplicated_content_parent_file_path_dict
                duplicated_dict = duplicated_content_dict

            # If content is not activated
            else:
                # Finalize
                duplicated_parent_file_path_dict = duplicated_size_parent_file_path_dict
                duplicated_dict = duplicated_size_dict

        # Launch UI
        finished_signal.finished.emit()

        gc.collect()

    # Function is used as a "key" in list.sorted(). Sorts the list by closest proximity to file_size
    @staticmethod
    def sort_size(list_file_size, file_size):

        # Difference in size between the file getting checked and the stored file
        size_difference = file_size - list_file_size

        # Make size_different positive
        if size_difference < 0:
            return size_difference * -1

        else:
            return size_difference
