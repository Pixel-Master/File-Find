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
from json import load
from threading import Thread
import difflib
import hashlib
import gc
from time import perf_counter

# PySide6 Gui Imports
from PySide6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QButtonGroup,
                               QRadioButton, QSlider, QSpinBox, QDialogButtonBox, QSpacerItem, QSizePolicy, QPushButton,
                               QTreeWidget, QTreeWidgetItem)
from PySide6.QtCore import Qt, QSize, Signal, QObject
from PySide6.QtGui import QIcon, QFont

# Projects Libraries
import FF_Menubar
import FF_Files

# Global variables
global duplicated_dict, time_dict


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
        self.BASE_WIDTH = 400
        self.BASE_HEIGHT = 400
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
        self.Upper_Layout = QHBoxLayout(self.Duplicated_Settings)
        self.Upper_Layout.setContentsMargins(0, 0, 0, 0)

        # Middle Horizontal Layout
        self.Middle_Layout = QHBoxLayout(self.Duplicated_Settings)
        self.Middle_Layout.setContentsMargins(0, 0, 0, 0)

        # Lower Horizontal Layout
        self.Lower_Layout = QHBoxLayout(self.Duplicated_Settings)
        self.Lower_Layout.setContentsMargins(0, 0, 0, 0)

        # Spacer for prettier ui
        spacer = QSpacerItem(10, 30, hData=QSizePolicy.Policy.Maximum)

        # Title label
        self.title_label = QLabel(parent=self.Duplicated_Settings)
        self.title_label.setText(f"Find duplicated files in: {FF_Files.display_path(search_path, 30)}")
        self.title_label.setToolTip(search_path)
        # Make the Font bigger
        font = self.title_label.font()
        font.setBold(True)
        font.setPixelSize(18)
        self.title_label.setFont(font)
        # Adjust size
        self.title_label.adjustSize()
        self.Duplicated_Settings_Layout.addWidget(self.title_label)

        # Button group
        self.button_group = QButtonGroup(self.Duplicated_Settings)

        # File name
        # Checkbox
        self.name_checkbox = QRadioButton(parent=self.Duplicated_Settings)
        self.name_checkbox.setText("File name")
        self.button_group.addButton(self.name_checkbox)
        self.Duplicated_Settings_Layout.addWidget(self.name_checkbox)

        # Match percentage label
        self.match_name_label = QLabel(parent=self.Duplicated_Settings)
        self.match_name_label.setText("Files must match at least:")
        self.Upper_Layout.addWidget(self.match_name_label)
        # Slider
        self.name_slider = QSlider(parent=self.Duplicated_Settings)
        self.name_slider.setOrientation(Qt.Orientation.Horizontal)
        self.name_slider.setRange(1, 100)
        self.Upper_Layout.addWidget(self.name_slider)
        # Spinbox
        self.name_spinbox = QSpinBox(parent=self.Duplicated_Settings)
        self.name_spinbox.setMaximum(100)
        self.Upper_Layout.addWidget(self.name_spinbox)
        # Connecting slider and Spinbox
        self.name_spinbox.valueChanged.connect(self.name_slider.setValue)
        self.name_slider.valueChanged.connect(self.name_spinbox.setValue)
        # Set value to 100 %
        self.name_spinbox.setValue(100)

        # Deactivate and activate functions
        def de_activate_name():
            if self.name_checkbox.isChecked():
                logging.debug("activating name")
                self.match_name_label.setDisabled(False)
                self.name_slider.setDisabled(False)
                self.name_spinbox.setDisabled(False)

            elif not self.name_checkbox.isChecked():
                logging.debug("deactivating name")
                self.match_name_label.setDisabled(True)
                self.name_slider.setDisabled(True)
                self.name_spinbox.setDisabled(True)

        # Connecting
        self.button_group.buttonToggled.connect(de_activate_name)
        # Deactivating
        de_activate_name()

        # Add to main Layout
        self.Duplicated_Settings_Layout.addLayout(self.Upper_Layout)
        # Add a Spacer
        self.Duplicated_Settings_Layout.addItem(spacer)

        # File size
        # Checkbox
        self.size_checkbox = QRadioButton(parent=self.Duplicated_Settings)
        self.size_checkbox.setText("File size (faster than File content)")
        self.button_group.addButton(self.size_checkbox)
        self.Duplicated_Settings_Layout.addWidget(self.size_checkbox)

        # Match percentage label
        self.match_size_label = QLabel(parent=self.Duplicated_Settings)
        self.match_size_label.setText("Files must match at least:")
        self.Middle_Layout.addWidget(self.match_size_label)
        # Slider
        self.size_slider = QSlider(parent=self.Duplicated_Settings)
        self.size_slider.setOrientation(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 100)
        self.Middle_Layout.addWidget(self.size_slider)
        # Spinbox
        self.size_spinbox = QSpinBox(parent=self.Duplicated_Settings)
        self.size_spinbox.setMaximum(100)
        self.Middle_Layout.addWidget(self.size_spinbox)
        # Connecting slider and Spinbox
        self.size_spinbox.valueChanged.connect(self.size_slider.setValue)
        self.size_slider.valueChanged.connect(self.size_spinbox.setValue)
        # Set value to 100 %
        self.size_spinbox.setValue(100)

        # Deactivate and activate functions
        def de_activate_size():
            if self.size_checkbox.isChecked():
                logging.debug("activating size")
                self.match_size_label.setDisabled(False)
                self.size_slider.setDisabled(False)
                self.size_spinbox.setDisabled(False)

            elif not self.size_checkbox.isChecked():
                logging.debug("deactivating size")
                self.match_size_label.setDisabled(True)
                self.size_slider.setDisabled(True)
                self.size_spinbox.setDisabled(True)

        # Connecting
        self.button_group.buttonToggled.connect(de_activate_size)
        # Deactivating
        de_activate_size()

        # Add to main Layout
        self.Duplicated_Settings_Layout.addLayout(self.Middle_Layout)
        # Add a Spacer
        self.Duplicated_Settings_Layout.addItem(spacer)

        # File content
        # Checkbox
        self.content_checkbox = QRadioButton(parent=self.Duplicated_Settings)
        self.content_checkbox.setText("File content")
        self.button_group.addButton(self.content_checkbox)
        self.Duplicated_Settings_Layout.addWidget(self.content_checkbox)

        # Match percentage label
        self.match_content_label = QLabel(parent=self.Duplicated_Settings)
        self.match_content_label.setText("Files must match at least:")
        self.Lower_Layout.addWidget(self.match_content_label)
        # Slider
        self.content_slider = QSlider(parent=self.Duplicated_Settings)
        self.content_slider.setOrientation(Qt.Orientation.Horizontal)
        self.content_slider.setRange(1, 100)
        self.Lower_Layout.addWidget(self.content_slider)
        # Spinbox
        self.content_spinbox = QSpinBox(parent=self.Duplicated_Settings)
        self.content_spinbox.setMaximum(100)
        self.Lower_Layout.addWidget(self.content_spinbox)
        # Connecting slider and Spinbox
        self.content_spinbox.valueChanged.connect(self.content_slider.setValue)
        self.content_slider.valueChanged.connect(self.content_spinbox.setValue)
        # Set value to 100 %
        self.content_spinbox.setValue(100)

        # Deactivate and activate functions
        def de_activate_content():
            if self.content_checkbox.isChecked():
                logging.debug("activating content")
                self.match_content_label.setDisabled(False)
                self.content_slider.setDisabled(False)
                self.content_spinbox.setDisabled(False)

            elif not self.content_checkbox.isChecked():
                logging.debug("deactivating content")
                self.match_content_label.setDisabled(True)
                self.content_slider.setDisabled(True)
                self.content_spinbox.setDisabled(True)

        # Connecting
        self.button_group.buttonToggled.connect(de_activate_content)
        # Deactivating
        de_activate_content()

        # Add to main Layout
        self.Duplicated_Settings_Layout.addLayout(self.Lower_Layout)
        # Add a Spacer
        self.Duplicated_Settings_Layout.addItem(spacer)

        # Okay and Cancel button
        self.button_box = QDialogButtonBox(parent=self.Duplicated_Settings)
        self.button_box.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.button_box.setObjectName("buttonBox")

        # Connect events
        def start_duplicated():
            # Events for threading
            class Events(QObject):
                finished = Signal()

            finished_event_class = Events()

            # Starting Thread
            Thread(
                target=lambda: FindDuplicated(
                    criteria={
                        "name": {"activated": self.name_checkbox.isChecked(),
                                 "match_percentage": self.name_spinbox.value()},
                        "size": {"activated": self.size_checkbox.isChecked(),
                                 "match_percentage": self.size_spinbox.value()},
                        "content": {"activated": self.content_checkbox.isChecked(),
                                    "match_percentage": self.content_spinbox.value()}},
                    search_path=search_path,
                    matched_list=matched_list,
                    finished_signal=finished_event_class)).start()

            # Connect UI to finished signal
            finished_event_class.finished.connect(lambda: DuplicatedUI(parent, search_path, duplicated_dict, time_dict))

        # Launch search algorithm
        self.button_box.button(
            QDialogButtonBox.StandardButton.Ok).clicked.connect(start_duplicated)

        self.button_box.button(
            QDialogButtonBox.StandardButton.Cancel).clicked.connect(
            self.Duplicated_Settings.close)

        self.Duplicated_Settings_Layout.addWidget(self.button_box)

        self.Duplicated_Settings.show()

    logging.info("Finished duplicated question setup!\n\n")


# User interface
class DuplicatedUI:
    def __init__(self, parent, match_path, matched_dict: dict, time_needed: dict):
        # Debug
        logging.info("Setting up Duplicated UI...")
        # Saving time
        time_needed["time_before_building_ui"] = perf_counter()

        # Window setup
        # Define the window
        self.Duplicated_Window = QMainWindow(parent)
        # Set the Title of the Window
        self.Duplicated_Window.setWindowTitle(f"Finding duplicated files in {FF_Files.display_path(match_path, 80)}")
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
        self.Duplicated_Tree.verticalScrollBar()

        # Get index
        main_index = 0
        # Adding all items to the view
        for main_item in matched_dict:
            # main item
            main_tree_item = QTreeWidgetItem(self.Duplicated_Tree)

            # Reset sub_index
            sub_index = 0

            # Iterating through the set under the key
            for sub_item in matched_dict[main_item]:
                QTreeWidgetItem(main_tree_item)

                main_tree_item.child(sub_index).setText(0, sub_item)

                # Increase sub index by one
                sub_index += 1

            # Set the text
            self.Duplicated_Tree.topLevelItem(main_index).setText(0, str(main_item))

            # Increase main index by one
            main_index += 1

        # Add the model to the final
        self.Duplicated_Layout.addWidget(self.Duplicated_Tree, 1, 0, 5, 8)

        # Setup menubar
        menu_bar = FF_Menubar.MenuBar(
            parent=self.Duplicated_Window, window="duplicated", listbox=self.Duplicated_Tree, search_path=match_path)

        # If item is double-clicked
        def open_double_clicked(item):
            # Only if subdirectory is clicked
            if item.text(0) != os.path.basename(item.text(0)):
                menu_bar.open_in_finder()

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
                button.setIcon(QIcon(icon))
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
        small_text_font = QFont("Arial", 17)
        small_text_font.setBold(True)

        # Files found label
        objects_text = QLabel(self.Duplicated_Window)
        objects_text.setText(f"Duplicated files: {len(matched_dict)}")
        objects_text.setFont(small_text_font)

        # Displaying
        self.Duplicated_Layout.addWidget(objects_text, 0, 2)

        # Time needed
        time_text = QLabel(self.Duplicated_Window)
        time_text.setText(f"Time needed:")
        time_text.setFont(small_text_font)
        # Displaying
        self.Duplicated_Layout.addWidget(time_text, 0, 0)

        # Saving time
        time_needed["time_after_building_ui"] = perf_counter()

        # Optimize label
        total_time = time_dict["time_after_building_ui"] - time_dict["start_time"]
        time_text.setText(f"Time needed: {round(total_time, 3)}")

        # Collect garbage
        gc.collect()


# Algorithms to find duplicated files
class FindDuplicated:
    def __init__(self, criteria: dict, search_path, matched_list, finished_signal: QObject):
        # Debug
        logging.info("Searching for duplicated files...")
        logging.info(f"{criteria = }")

        # Global variables
        global duplicated_dict, time_dict

        # Saving time
        time_dict = {"start_time": perf_counter()}

        # Loading cache
        # Creating file
        with open(
                os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, search_path.replace("/", "-") + ".FFCache")) as load_file:
            # Loading file basename
            file_dict = load(load_file)

            found_path_set = matched_list
            low_basename_dict = file_dict["low_basename_dict"]

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
            # Group by name1
            if criteria["name"]["match_percentage"] == 100:

                for file in found_path_set:
                    # Get the basename, ignoring case
                    low_basename = low_basename_dict[file]

                    if low_basename not in exists_already:
                        # Add the file to the dictionary
                        exists_already.add(low_basename)
                        duplicated_name_dict[low_basename] = {file}

                    else:
                        # Add the file to the duplicated dict
                        duplicated_name_dict[low_basename].add(file)

            else:

                match_factor = criteria["name"]["match_percentage"] / 100

                # Iterating through all files
                for file in found_path_set:
                    # Get the basename, ignoring case
                    low_basename = low_basename_dict[file]
                    # If low_basename isn't already in exist already_text if there is something in the allowed range
                    if low_basename not in exists_already:

                        # If this is the first file being iterated
                        if exists_already == set():
                            exists_already.add(low_basename)
                            duplicated_name_dict[low_basename] = {file}
                            continue

                        # Get the closest match, over the match factor. Function returns a list
                        closest_match = difflib.get_close_matches(
                            low_basename, exists_already, n=1, cutoff=match_factor)

                        # There is no match (empty list) with the file, add it to exists_already
                        if not closest_match:
                            exists_already.add(low_basename)
                            duplicated_name_dict[low_basename] = {file}

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
            duplicated_dict = duplicated_name_dict

        # Group by size
        if criteria["size"]["activated"]:
            # Debug
            logging.debug(f"Grouping by size, {criteria['size']['match_percentage'] = }")

            exists_already = set()
            duplicated_size_dict = {}

            # If the percentage of
            if criteria["size"]["match_percentage"] == 100:
                for file in found_path_set:

                    size = os.path.getsize(file)

                    if size not in exists_already:
                        # Add the file to the dictionary
                        exists_already.add(size)
                        duplicated_size_dict[size] = {file}

                    else:
                        # Add the file to the duplicated dict
                        duplicated_size_dict[size].add(file)

            else:
                # factor of allowed divergence
                # factor 1 upper = 1 lower = 1
                # factor 0.8 upper = 1.2 lower = 0.8
                # factor 0.4 upper = 1.6 lower = 0.8
                lower_allowed_divergence_factor = criteria["size"]["match_percentage"] / 100
                upper_allowed_divergence_factor = lower_allowed_divergence_factor + 1 - lower_allowed_divergence_factor

                for file in found_path_set:

                    # Try getting the size
                    try:
                        size = os.path.getsize(file)
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
                            duplicated_size_dict[size] = {file}

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
                exists_already = set()

                # If files must match exactly
                if criteria["content"]["match_percentage"] == 100:

                    # Buffer size
                    buffer_size = 65536

                    # Iterating through all files that have the same size
                    for file in duplicated_files:
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

                        # If everything ran successful
                        else:
                            # If hash doesn't already exist
                            if file_hash not in exists_already:
                                exists_already.add(file_hash)
                                duplicated_content_dict[file_hash] = {file}

                            # If hash exists
                            else:
                                duplicated_content_dict[file_hash].add(file)

                # If match percentage is not 100% use pHash
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
                duplicated_dict = duplicated_content_dict

            # If content is not activated
            else:
                # Finalize
                duplicated_dict = duplicated_size_dict

        # Launch UI
        finished_signal.finished.emit()

        gc.collect()

    # Function is used as a "key" ins sorted(). Sorts the list bay closest proximity to file_size
    @staticmethod
    def sort_size(list_file_size, file_size):

        # Difference in size between the file getting checked and the stored file
        size_difference = file_size - list_file_size

        # Make size_different positive
        if size_difference < 0:
            return size_difference * -1

        else:
            return size_difference
