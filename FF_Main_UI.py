# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the main window

# Imports
import logging
import os
from json import dump, load
from sys import platform
import sys

# PySide6 Gui Imports
from PySide6.QtCore import QSize, Qt, QDate, QTimer, QTime
from PySide6.QtGui import QFont, QDoubleValidator, QAction, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QRadioButton, QFileDialog, \
    QLineEdit, QDateEdit, QComboBox, QSystemTrayIcon, QMenu, QTabWidget, \
    QMainWindow, QGridLayout, QSpacerItem, QSizePolicy, QCheckBox, QSpinBox

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_About_UI
import FF_Search
import FF_Settings


# The class for the main window where filters can be selected
class MainWindow:
    def __init__(self):
        # Debug
        logging.info("Launching UI...")
        logging.debug("Setting up self.Root_Window...")

        # Main Window
        # Create the window
        self.Root_Window = QMainWindow()
        # Set the Title of the Window
        self.Root_Window.setWindowTitle("File Find")
        # Set the start size
        self.BASE_WIDTH = 800
        self.BASE_HEIGHT = 370
        self.Root_Window.setBaseSize(self.BASE_WIDTH, self.BASE_HEIGHT)
        self.Root_Window.resize(self.Root_Window.baseSize())
        # Display the Window
        self.Root_Window.show()

        # Adding Layouts
        # Main Layout
        # Create a central widget
        self.Central_Widget = QWidget(self.Root_Window)
        self.Root_Window.setCentralWidget(self.Central_Widget)
        # Create the main Layout
        self.Main_Layout = QGridLayout(self.Central_Widget)
        self.Central_Widget.setLayout(self.Main_Layout)
        self.Main_Layout.setContentsMargins(20, 20, 20, 20)
        self.Main_Layout.setVerticalSpacing(20)

        # Tab widget, switch between Basic, Advanced and Sorting
        self.tabbed_widget = QTabWidget(self.Root_Window)
        # Display at the correct position
        self.Main_Layout.addWidget(self.tabbed_widget, 1, 0, 10, 13)

        # Labels
        logging.debug("Setting up Labels...")
        # Create a Label for every Filter with the Function, defined above
        # -----Basic Search-----
        # Tabs and Label
        # Creating a new QWidget for the Basic tab
        self.basic_search_widget = QWidget(self.Root_Window)
        # Layout
        self.basic_search_widget_layout = QGridLayout(self.basic_search_widget)
        self.basic_search_widget.setLayout(self.basic_search_widget_layout)
        self.basic_search_widget_layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum), 0, 0)
        self.basic_search_widget_layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum), 0, 8)
        # Add Tab
        self.tabbed_widget.addTab(self.basic_search_widget, "Basic")

        # Creating the Labels with tooltips
        label_name = self.generate_large_filter_label(
            "Name",
            self.basic_search_widget,
            self.generic_tooltip(
                "Name",
                "Multiple different modes are available. \n"
                "\nName \"is\":\n"
                "  Input needs to match the file name exactly. Also supports unix shell-style "
                "wildcards, which are not the same as regular expressions."
                "\n  Usage:\n"
                "  Pattern   Meaning\n"
                "      *         matches everything\n"
                "      ?         matches any single character\n"
                "      [seq]  matches any character in seq\n"
                "      [!seq] matches any character not in seq\n\n"
                "Name \"contains\":\n   The file name must contain the input.\n\n"
                "Name \"begins with\":\n  The file name must start with the input.\n\n"
                "Name \"ends with\":\n  The file name (without the file ending) must end with input. So \"mple\" "
                "would match with \"Example.txt\".\n\n"
                "Name \"is similar to\":\n  Performs a fuzzy search. So \"amp\" matches with \"Example.txt\". "
                "Matching percentage can be set separately.\n\n"
                "Name \"doesn't contain\":\n  Input must not be included in its entirety in the file name.\n\n"
                "Name \"in RegEx\":\n  Does a regular expression pattern matching. For a detailed explanation refer to:"
                " https://regular-expressions.info",
                "Name \"is:\", Example.txt",
                os.path.join(FF_Files.USER_FOLDER, "Example.txt")))
        self.basic_search_widget_layout.addWidget(label_name, 0, 1)

        label_file_type = self.generate_large_filter_label(
            "File Types:",
            self.basic_search_widget,
            self.generic_tooltip(
                "File Types",
                "Select groups of file types that should be included in search results."
                "\n\nClick \"Custom\" to change selection mode and input a file type (e.g. pdf) without the \".\",\n"
                "that needs to match the file ending of a file exactly, ignoring case.\n"
                "Multiple possible file types can be separated with a semicolon (for example: \"png;jpg;heic\")"
                "\n\nClick \"Predefined\" to switch back."
                "\n\nOnly the currently visible mode will be taken into account. ",
                "In Predefined: \"Music\", in Custom: \"txt\"",
                "In Predefined:" + os.path.join(FF_Files.USER_FOLDER, "song.mp3") + ", in Custom: " +
                os.path.join(FF_Files.USER_FOLDER, "example.txt")))
        self.basic_search_widget_layout.addWidget(label_file_type, 2, 1)

        label_directory = self.generate_large_filter_label(
            "Directory:",
            self.basic_search_widget,
            self.generic_tooltip("Directory",
                                 "The directory to search in.",
                                 os.path.join(
                                     FF_Files.USER_FOLDER,
                                     "Downloads"),
                                 os.path.join(
                                     FF_Files.USER_FOLDER,
                                     "Downloads",
                                     "example.pdf")))
        self.basic_search_widget_layout.addWidget(label_directory, 3, 1)

        # -----File Content-----
        # Tab and Label
        # Creating a new QWidget for the properties tab
        self.properties_widget = QWidget(self.Root_Window)
        # Layout
        self.properties_widget_layout = QGridLayout(self.properties_widget)
        self.properties_widget.setLayout(self.properties_widget_layout)
        # Adding space
        self.properties_widget_layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum), 0, 0)
        self.properties_widget_layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum), 0, 6)
        # Add Tab
        self.tabbed_widget.addTab(self.properties_widget, "Properties")

        # Creation date
        label_c_date = self.generate_large_filter_label(
            "Date created:",
            self.properties_widget,
            self.generic_tooltip("Date created",
                                 "Specify a date range for the date the file has been created,\n"
                                 "leave at default to ignore.",
                                 "5.Jul.2020 - 10.Aug.2020",
                                 os.path.join(FF_Files.USER_FOLDER, "example.txt (created at 1.Aug.2020)")))
        self.properties_widget_layout.addWidget(label_c_date, 1, 1)
        label_c_date_2 = self.generate_large_filter_label("-", self.properties_widget)
        self.properties_widget_layout.addWidget(label_c_date_2, 1, 4)

        # Date modified
        label_m_date = self.generate_large_filter_label(
            "Date modified:",
            self.properties_widget,
            self.generic_tooltip("Date modified",
                                 "Specify a date range for the date the file has been modified,\n "
                                 "leave at default to ignore.",
                                 "5.Jul.2020 -  10.Aug.2020",
                                 os.path.join(FF_Files.USER_FOLDER, "example.txt (modified at 1.Aug.2020)")))
        self.properties_widget_layout.addWidget(label_m_date, 2, 1)
        label_m_date_2 = self.generate_large_filter_label("-", self.properties_widget)
        self.properties_widget_layout.addWidget(label_m_date_2, 2, 4)

        label_file_size = self.generate_large_filter_label(
            "File size min:",
            self.properties_widget,
            self.generic_tooltip(
                "File size",
                "Input specifies file size in a range from min to max.\n"
                "Select the unit (Byte, Megabyte, Gigabyte...) on the left.\n"
                "Select \"No Limit\" to only set a minimum or maximum value.",
                "min: 1 GB max: No Limit",
                os.path.join(FF_Files.USER_FOLDER, "Applications",
                             "Microsoft Word.app (with a size of 2 GB)")))
        self.properties_widget_layout.addWidget(label_file_size, 3, 1)
        label_file_size_max = self.generate_large_filter_label("max:", self.properties_widget)
        self.properties_widget_layout.addWidget(label_file_size_max, 3, 4)

        # -----Advanced Search-----
        # Tab and Label
        # Creating a new QWidget for the file content tab
        self.advanced_search_widget = QWidget(self.Root_Window)
        # Layout
        self.advanced_search_widget_layout = QGridLayout(self.advanced_search_widget)
        self.advanced_search_widget.setLayout(self.advanced_search_widget_layout)
        # Adding spacers
        self.advanced_search_widget_layout.addItem(
            QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum, vData=QSizePolicy.Policy.Minimum), 0, 0)
        self.advanced_search_widget_layout.addItem(
            QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum, vData=QSizePolicy.Policy.Minimum), 7, 6)
        self.advanced_search_widget_layout.addItem(
            QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 0, 0)
        self.advanced_search_widget_layout.addItem(
            QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 2, 1)
        self.advanced_search_widget_layout.addItem(
            QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 4, 1)
        self.advanced_search_widget_layout.addItem(
            QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 7, 0)

        # Add Tab
        self.tabbed_widget.addTab(self.advanced_search_widget, "Advanced")

        label_folder_depth = self.generate_large_filter_label(
            "Limit folder depth to:",
            self.advanced_search_widget,
            self.generic_tooltip(
                "Limit folder depth",
                "Toggle to include/exclude subdirectories or their subdirectories.\n"
                "Entering a custom number sets the maximum amount of subdirectories in which files are still included"
                "\n\n0 or no Subfolders means that ony the files directly in the specified directory will be included"
                "\n1 means only the files in the folders that are directly in the specified dir will be considered...",
                "No subfolders",
                os.path.join(FF_Files.USER_FOLDER, "example.txt")))
        self.advanced_search_widget_layout.addWidget(label_folder_depth, 1, 1)

        # Search for file content
        label_file_contains = self.generate_large_filter_label(
            "File contains:",
            self.properties_widget,
            self.generic_tooltip(
                "File contains:",
                "Allows you to search in files. Input must be in the file content."
                "\nInput is case-sensitive."
                "\nOnly allows raw text files such as .txt or source code, MS-Office or PDFs are not supported."
                "\n\n"
                "This option can take really long.\n",
                "This is an example file!",
                os.path.join(FF_Files.USER_FOLDER, "example.txt (which contains: \"This is an example file!\")")))
        self.advanced_search_widget_layout.addWidget(label_file_contains, 3, 1)

        label_files_folders = self.generate_large_filter_label(
            "Search for:",
            self.advanced_search_widget,
            self.generic_tooltip("Search for",
                                 "Toggle to only include folders or files in the search results",
                                 "only Folders",
                                 os.path.join(FF_Files.USER_FOLDER, "Downloads")))
        self.advanced_search_widget_layout.addWidget(label_files_folders, 5, 1)

        # -----Sorting-----
        # Tab and Label
        # Creating a new QWidget for the Sorting tab
        self.sorting_widget = QWidget(self.Root_Window)
        # Layout
        self.sorting_widget_layout = QGridLayout(self.sorting_widget)
        self.sorting_widget.setLayout(self.sorting_widget_layout)
        self.sorting_widget_layout.setVerticalSpacing(15)
        # Adding a spacer
        self.sorting_widget_layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Expanding), 1, 0)
        self.sorting_widget_layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Expanding), 1, 6)
        self.sorting_widget_layout.addItem(QSpacerItem(0, 10, vData=QSizePolicy.Policy.Expanding), 0, 0)
        self.sorting_widget_layout.addItem(QSpacerItem(0, 10, vData=QSizePolicy.Policy.Expanding), 3, 0)
        # Add Tab
        self.tabbed_widget.addTab(self.sorting_widget, "Sorting")

        label_sort_by = self.generate_large_filter_label(
            "Sort by:",
            self.sorting_widget,
            self.generic_tooltip("Sort by",
                                 "Select a sorting method to sort the results.",
                                 "File Size",
                                 "Results sorted by file size"))
        self.sorting_widget_layout.addWidget(label_sort_by, 1, 1)

        # -----Terminal Command-----
        # Label, saying command
        label_command_title = QLabel(self.Root_Window)
        label_command_title.setText("Command:")
        label_command_title.setToolTip(
            "Terminal command:\nYou can paste this command into the Terminal app to search with the \"find\" tool")
        label_command_title.setFont(FF_Additional_UI.DEFAULT_QT_FONT)
        self.Main_Layout.addWidget(label_command_title, 11, 0)
        label_command_title.hide()

        # Label, displaying the command, using a read only line edit
        label_command = QLineEdit(self.Root_Window)
        label_command.setReadOnly(True)
        label_command.setFixedWidth(300)
        self.Main_Layout.addWidget(label_command, 11, 1)
        label_command.hide()

        # Copy Command Button
        button_command_copy = QPushButton(self.Root_Window)
        # Change the Text
        button_command_copy.setText("Copy")
        # When resizing, it shouldn't change size
        button_command_copy.setFixedWidth(60)
        # Display the Button at the correct position
        self.Main_Layout.addWidget(button_command_copy, 11, 2)
        button_command_copy.hide()

        # ----- Search Indicator-----
        # Title of searching indicator
        search_status_title_label = QLabel(self.Root_Window)
        search_status_title_label.setText("Status:")
        search_status_title_label.setFont(FF_Additional_UI.DEFAULT_QT_FONT)
        search_status_title_label.setToolTip(
            "Search Indicator:\n"
            "Indicates if searching and shows the numbers of active searches.\n"
            "For more precise information click on the File Find logo in the menu-bar.")
        search_status_title_label.show()
        self.Main_Layout.addWidget(search_status_title_label, 12, 0)

        # Custom label to indicate if searching
        global search_status_label
        search_status_label = FF_Additional_UI.ColoredLabel("Idle", self.Root_Window,
                                                            FF_Files.GREEN_LIGHT_THEME_COLOR,
                                                            FF_Files.GREEN_DARK_THEME_COLOR)
        search_status_label.setFont(FF_Additional_UI.DEFAULT_QT_FONT)
        search_status_label.show()
        self.Main_Layout.addWidget(search_status_label, 12, 1)
        self.Main_Layout.addItem(QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum), 12, 2)

        # Entries
        logging.debug("Setting up Entries...")

        # Create an Entry for every Filter with the function self.generate_filter_entry()

        # Name
        self.edit_name = self.generate_filter_entry(self.basic_search_widget)
        # Place
        self.basic_search_widget_layout.addWidget(self.edit_name, 0, 3, 1, 4)

        # Edit for displaying the Path
        self.edit_directory = FF_Additional_UI.DirectoryEntry(self.basic_search_widget)
        # Place in layout
        self.basic_search_widget_layout.addWidget(self.edit_directory, 3, 2, 1, 3)

        # File contains
        self.edit_file_contains = self.generate_filter_entry(self.properties_widget)
        self.advanced_search_widget_layout.addWidget(self.edit_file_contains, 3, 2)

        # File size

        # File size min
        self.edit_size_min = self.generate_filter_entry(self.properties_widget, True)
        self.edit_size_min.setFixedWidth(60)
        self.properties_widget_layout.addWidget(self.edit_size_min, 3, 2)

        # File size max
        self.edit_size_max = self.generate_filter_entry(self.properties_widget, True)
        self.edit_size_max.setFixedWidth(60)
        self.properties_widget_layout.addWidget(self.edit_size_max, 3, 5)

        # Unit selectors for selecting Byte, KiloByte, Megabyte...
        def create_unit_selector(corresponding_edit):
            # Create a QComboBox
            unit_selector = QComboBox(self.advanced_search_widget)
            unit_selector.addItems(["No Limit", "Bytes", "KB", "MB", "GB"])
            # Set a fixed width
            unit_selector.setFixedWidth(100)

            def selection_changed():
                if unit_selector.currentText() == "No Limit":
                    corresponding_edit.setEnabled(False)
                    corresponding_edit.setToolTip("No Limit is selected")
                    corresponding_edit.setStyleSheet(f"background-color: {FF_Files.GREY_DISABLED_COLOR};")
                else:
                    corresponding_edit.setEnabled(True)
                    corresponding_edit.setToolTip("")
                    corresponding_edit.setStyleSheet(";")

            # Connect to change event
            unit_selector.currentTextChanged.connect(selection_changed)

            # Set value to "No Limit"
            unit_selector.setCurrentText("No Limit")

            # Deactivate Edit
            selection_changed()

            return unit_selector

        # Unit selector min
        self.unit_selector_min = create_unit_selector(self.edit_size_min)
        self.properties_widget_layout.addWidget(self.unit_selector_min, 3, 3)

        # Unit selector max
        self.unit_selector_max = create_unit_selector(self.edit_size_max)
        self.properties_widget_layout.addWidget(self.unit_selector_max, 3, 6)

        # Radio Button
        logging.debug("Setting up Check Boxes...")
        # Making a layout to put under the "name [custom]" line edit so when changing the "consider case"-checkbox
        # to the similarity percentage, the window doesn't jump around
        self.name_widget = QWidget(self.Root_Window)
        self.basic_search_widget_layout.addWidget(self.name_widget, 1, 3, 1, 4)
        self.name_widget.setFixedSize(QSize(140, 35))
        self.name_layout = QGridLayout(self.name_widget)
        self.name_layout.setSpacing(0)
        self.name_layout.setContentsMargins(0, 0, 0, 0)
        self.name_widget.setLayout(self.name_layout)

        # Consider case check box
        self.case_check_box = QCheckBox(" Consider case", self.Root_Window)
        self.case_check_box.setToolTip(
            self.generic_tooltip("Consider case",
                                 "Turn on to consider case, so \"Film\" won't find \"film\"",
                                 "Yes, Example.txt",
                                 os.path.join(FF_Files.USER_FOLDER, "Library", "Caches", "Example.txt")))

        self.name_layout.addWidget(self.case_check_box, 1, 1, 1, 2, Qt.AlignmentFlag.AlignLeft)

        # Similarity percentage
        self.similarity_label = QLabel("% similar", parent=self.Root_Window)
        self.name_layout.addWidget(self.similarity_label, 1, 2)
        # Tooltip
        self.similarity_label.setToolTip(
            self.generic_tooltip("is similar to",
                                 "Adjust to change the percentage that a file name"
                                 " must be similar to the input. Performs a fuzzy search.\n\n"
                                 "100% means, it has to be an exact match,\n"
                                 "0% will be a match, no matter the file name,\n"
                                 "60% is a recommended value.",
                                 "60%, exampl",
                                 os.path.join(FF_Files.USER_FOLDER, "Library", "Caches", "Example.txt")))

        # Spinbox
        self.similarity_spinbox = QSpinBox(parent=self.Root_Window)
        # Maximum value is 100 %
        self.similarity_spinbox.setMaximum(100)
        # Tooltips
        self.name_layout.addWidget(self.similarity_spinbox, 1, 1, Qt.AlignmentFlag.AlignLeft)

        # Search for Library Files
        self.library_check_box = QCheckBox(" Search for system files", self.Root_Window)
        self.library_check_box.setToolTip(
            self.generic_tooltip("Search for system files",
                                 "Toggle to include files in the system and library folders.",
                                 "Yes",
                                 os.path.join(FF_Files.USER_FOLDER, "Library", "Caches", "example.txt")))
        self.advanced_search_widget_layout.addWidget(self.library_check_box, 6, 2)
        # Select the Button
        self.library_check_box.setChecked(False)

        # Reverse Sort
        # Group for Radio Buttons
        self.reverse_sorting_check_box = QCheckBox(" Reverse results", self.Root_Window)
        self.reverse_sorting_check_box_state = False
        self.reverse_sorting_check_box.setChecked(self.reverse_sorting_check_box_state)
        self.reverse_sorting_check_box.setToolTip(
            self.generic_tooltip("Reverse Results",
                                 "Reverse the sorted search results.",
                                 "Yes",
                                 "Reversed search results"))
        # Add the button to the layout
        self.sorting_widget_layout.addWidget(self.reverse_sorting_check_box, 2, 2)

        # Hide when "None" is selected because there is no value in having it around
        def hide_show_reverse_sort():
            if self.combobox_sorting.currentText() == "None (fastest)":
                self.reverse_sorting_check_box.hide()
            else:
                self.reverse_sorting_check_box.show()

        # Drop Down Menus
        logging.debug("Setting up Drop Down Menus...")

        def hide_show_similarity():
            if self.name_specifier.currentText() == "is similar to:":
                self.similarity_label.show()
                self.similarity_spinbox.show()
                self.case_check_box.hide()
            else:
                self.similarity_label.hide()
                self.similarity_spinbox.hide()
                self.case_check_box.show()

        # Name specifier
        self.name_specifier = QComboBox(self.basic_search_widget)
        # Possible options
        self.name_specifier.addItems([
            "is:",
            "contains:",
            "begins with:",
            "ends with:",
            "is similar to:",
            "doesn't contain:",
            "in RegEx:",
        ])
        # Set a fixed width
        self.name_specifier.setFixedWidth(145)
        # Display
        self.name_specifier.show()
        # Connect with consider case checkbox and similarity spinbox
        self.name_specifier.currentTextChanged.connect(hide_show_similarity)
        self.basic_search_widget_layout.addWidget(self.name_specifier, 0, 2)

        # Sorting Menu
        # Defining
        self.combobox_sorting = QComboBox(self.sorting_widget)
        # Connecting to the checkbox
        self.combobox_sorting.currentTextChanged.connect(hide_show_reverse_sort)
        # Adding Options
        self.combobox_sorting.addItems(
            ["None (fastest)",
             "File Size",
             "File Name",
             "Date Modified",
             "Date Created",
             "Path"])
        # Set a fixed width
        self.combobox_sorting.setFixedWidth(150)
        # Display
        self.combobox_sorting.show()
        self.sorting_widget_layout.addWidget(self.combobox_sorting, 1, 2, 1, 4)

        # Search for Files or Folders Menu
        # Defining
        self.combobox_search_for = QComboBox(self.advanced_search_widget)
        # Adding Options
        self.combobox_search_for.addItems(
            ["Files and Folders",
             "only Files",
             "only Folders"])
        # Display
        self.combobox_search_for.setFixedWidth(235)
        self.advanced_search_widget_layout.addWidget(self.combobox_search_for, 5, 2)

        # Combobox folder depth
        # Defining
        self.combobox_folder_depth = QComboBox(self.advanced_search_widget)
        self.edit_folder_depth = QSpinBox(self.advanced_search_widget)
        # Adding Options
        self.combobox_folder_depth.addItems(
            ["Unlimited",
             "No subfolders",
             "Custom"])
        # Custom line edit
        self.edit_folder_depth.setFixedWidth(60)
        self.advanced_search_widget_layout.addWidget(self.edit_folder_depth, 1, 2, Qt.AlignmentFlag.AlignLeft)
        self.edit_folder_depth.hide()

        # Making the "Custom" option editable
        def check_editable():
            if self.combobox_folder_depth.currentText() not in ("Unlimited", "No subfolders"):
                self.edit_folder_depth.show()
                self.combobox_folder_depth.setFixedWidth(160)
            else:
                self.edit_folder_depth.hide()
                self.combobox_folder_depth.setFixedWidth(235)

        self.combobox_folder_depth.currentTextChanged.connect(check_editable)
        # Display
        self.combobox_folder_depth.setFixedWidth(235)
        self.advanced_search_widget_layout.addWidget(self.combobox_folder_depth, 1, 2, Qt.AlignmentFlag.AlignRight)

        # Search for file types: all, images, movies, music, etc...
        self.combobox_file_types = FF_Additional_UI.CheckableComboBox(self.advanced_search_widget)
        self.combobox_file_types.addItems(FF_Files.FILE_FORMATS.keys())
        # Display
        self.combobox_file_types.show()
        self.basic_search_widget_layout.addWidget(self.combobox_file_types, 2, 2, 1, 3)

        # Custom file extension input
        self.edit_file_extension = self.generate_filter_entry(self.properties_widget)
        # Place
        self.basic_search_widget_layout.addWidget(self.edit_file_extension, 2, 2, 1, 3)
        self.edit_file_extension.hide()

        # Button
        self.change_file_type_mode_button = self.generate_edit_button(
            command=lambda: self.change_file_type_mode(),
            tab=self.basic_search_widget,
            text="Custom")
        self.change_file_type_mode_button.setFixedWidth(80)
        self.file_type_mode = "predefined"
        self.basic_search_widget_layout.addWidget(self.change_file_type_mode_button, 2, 7)

        # Date-Time Entries
        logging.debug("Setting up Day Entries...")
        # Date Created
        self.c_date_from_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.properties_widget_layout.addWidget(self.c_date_from_drop_down, 1, 2, 1, 4)
        self.c_date_to_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.c_date_to_drop_down.setDate(QDate.currentDate())
        self.properties_widget_layout.addWidget(self.c_date_to_drop_down, 1, 5, 1, 7)

        # Date Modified
        self.m_date_from_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.properties_widget_layout.addWidget(self.m_date_from_drop_down, 2, 2, 1, 4)
        self.m_date_to_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.m_date_to_drop_down.setDate(QDate.currentDate())
        self.properties_widget_layout.addWidget(self.m_date_to_drop_down, 2, 5, 1, 7)

        # If the current date changes, the edit should too
        timer = QTimer(self.Root_Window)
        timer.setTimerType(Qt.TimerType.VeryCoarseTimer)
        timer.timeout.connect(lambda: self.c_date_to_drop_down.setDate(QDate.currentDate()))

        # Always executed at midnight
        def restart_timer():
            # Debug
            logging.debug("Midnight!, changing time for creation and modification time edit")
            # Check for both the modified and the creation time if the date is equal to the former current time
            # If this is the case (for example if left untouched) set the date to the actual current date
            if self.c_date_to_drop_down.date() == QDate.currentDate().addDays(-1):
                self.c_date_to_drop_down.setDate(QDate.currentDate())
            if self.m_date_to_drop_down.date() == QDate.currentDate().addDays(-1):
                self.m_date_to_drop_down.setDate(QDate.currentDate())
            # Time to next midnight 23:59:59:999 with 1 added buffer second / 1000 milliseconds
            timer.start(QTime.currentTime().msecsTo(QTime(23, 59, 59, 999)) + 1000)

        timer.timeout.connect(restart_timer)
        # Time to midnight 23:59:59:999 with 1 added buffer second / 1000 milliseconds
        timer.start(QTime.currentTime().msecsTo(QTime(23, 59, 59, 999)) + 1000)

        # Push Buttons
        logging.debug("Set up time mechanics, Setting up Push Buttons...")

        # Buttons
        # Search from Button
        # Opens the File dialogue and changes the current working dir into the returned value
        def open_dialog():
            search_from = QFileDialog.getExistingDirectory(dir=FF_Files.SELECTED_DIR)
            # If a dir was selected
            if search_from != "":
                # Normalize the path
                search_from = os.path.normpath(search_from)
                try:
                    FF_Files.SELECTED_DIR = search_from
                    self.edit_directory.setText(search_from)
                except OSError:
                    pass

        browse_path_button = self.generate_edit_button(open_dialog, self.basic_search_widget, text="Browse")
        browse_path_button.setFixedWidth(80)
        self.basic_search_widget_layout.addWidget(browse_path_button, 3, 5)

        # Select and deselect all options in the check able file group combobox
        self.select_all_button = self.generate_edit_button(
            self.combobox_file_types.select_all, self.basic_search_widget, text="Select all")
        self.select_all_button.setFixedWidth(80)
        self.basic_search_widget_layout.addWidget(self.select_all_button, 2, 5)
        self.select_all_button.setEnabled(False)

        self.deselect_all_button = self.generate_edit_button(
            self.combobox_file_types.deselected_all, self.basic_search_widget, text="Deselect all")
        # Place on the layout
        self.deselect_all_button.setFixedWidth(90)
        self.basic_search_widget_layout.addWidget(self.deselect_all_button, 2, 6)

        # Activate/Deactivate buttons if necessary
        self.combobox_file_types.button_signals.all_selected.connect(
            lambda: self.deselect_all_button.setDisabled(False))
        self.combobox_file_types.button_signals.all_selected.connect(lambda: self.select_all_button.setDisabled(True))
        # If only some options are enabled
        self.combobox_file_types.button_signals.some_selected.connect(
            lambda: self.deselect_all_button.setDisabled(False))
        self.combobox_file_types.button_signals.some_selected.connect(lambda: self.select_all_button.setDisabled(False))
        # If all files are deselected
        self.combobox_file_types.button_signals.all_deselected.connect(
            lambda: self.deselect_all_button.setDisabled(True))
        self.combobox_file_types.button_signals.all_deselected.connect(
            lambda: self.select_all_button.setDisabled(False))

        # Print the given data
        def print_data():
            logging.info(
                f"\nFilters:\n"
                f"Name {self.name_specifier} {self.edit_name.text()} (Consider Case: {self.case_check_box})\n"
                f"File Ending: {self.edit_file_extension.text()}\n"
                f"File Groups: {self.combobox_file_types.all_checked_items()}\n"
                f"File Type mode: {self.file_type_mode}\n\n"
                f"Search from: {os.path.abspath(FF_Files.SELECTED_DIR)}\n\n"
                f"File size: min: {self.edit_size_min.text()} ({self.unit_selector_min.currentText()})"
                f" max: {self.edit_size_max.text()} ({self.unit_selector_min.currentText()})\n"
                f"Date modified from: {self.m_date_from_drop_down.text()} to: {self.m_date_to_drop_down.text()}\n"
                f"Date created from: {self.c_date_from_drop_down.text()} to: {self.c_date_to_drop_down.text()}\n"
                f"Folder depth: {self.combobox_folder_depth.currentText()} (Custom: {self.edit_folder_depth.value()})"
                "\n\n"
                f"Content: {self.edit_file_contains.text()}\n\n"
                f"Search for system files: {self.library_check_box.isChecked()}\n"
                f"Search for: {self.combobox_search_for.currentText()}\n\n"
                f"Sort results by: {self.combobox_sorting.currentText()}\n"
                f"Reverse results: {self.reverse_sorting_check_box.isChecked()}\n")

        # Start Search with args locally
        def search_entry(new_cache_file=False):
            # Debug
            logging.debug("User clicked Find")

            # Print Input for Debugging
            print_data()
            # Start Searching
            FF_Search.Search(
                data_name=self.edit_name.text(),
                data_name_specifier=self.name_specifier.currentText(),
                data_consider_case=self.case_check_box.isChecked(),
                data_similarity=self.similarity_spinbox.value(),
                data_filetype=self.edit_file_extension.text(),
                data_file_size_min=self.edit_size_min.text(), data_file_size_max=self.edit_size_max.text(),
                data_file_size_min_unit=self.unit_selector_min.currentText(),
                data_file_size_max_unit=self.unit_selector_max.currentText(),
                data_library=self.library_check_box.isChecked(),
                data_search_from_valid=os.path.abspath(FF_Files.SELECTED_DIR),
                data_search_from_unchecked=self.edit_directory.text(),
                data_content=self.edit_file_contains.text(),
                data_search_for=self.combobox_search_for.currentText(),
                data_date_edits={"c_date_from": self.c_date_from_drop_down,
                                 "c_date_to": self.c_date_to_drop_down,
                                 "m_date_from": self.m_date_from_drop_down,
                                 "m_date_to": self.m_date_to_drop_down},
                data_sort_by=self.combobox_sorting.currentText(),
                data_reverse_sort=self.reverse_sorting_check_box.isChecked(),
                data_file_group=self.combobox_file_types.all_checked_items(),
                data_file_type_mode=self.file_type_mode,
                data_folder_depth=self.combobox_folder_depth.currentText(),
                data_folder_depth_custom=self.edit_folder_depth.value(),
                new_cache_file=new_cache_file,
                parent=self.Root_Window)

        # Saves the function in a different var
        self.search_entry = search_entry

        # Large Buttons
        # Search button with image, to start searching

        # Menu when Right-clicking
        context_menu = QMenu(self.Root_Window)

        # Search and create new cache for selected folder action
        action_search_without_cache = QAction("Search and create new cache for selected folder", self.Root_Window)
        action_search_without_cache.triggered.connect(self.create_cache_and_search)
        context_menu.addAction(action_search_without_cache)

        # Separator
        context_menu.addSeparator()

        # Load Search Action
        action_open_search = QAction("&Open Search / Filter Preset", self.Root_Window)
        action_open_search.triggered.connect(lambda: self.import_filters())
        context_menu.addAction(action_open_search)

        # Separator
        context_menu.addSeparator()

        # Reset Action
        reset_action = QAction("Reset filters", self.Root_Window)
        reset_action.triggered.connect(self.reset_filters)
        context_menu.addAction(reset_action)

        # Defining Button
        search_button = self.generate_large_button("Find", search_entry, 25)

        # Context Menu
        search_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        search_button.customContextMenuRequested.connect(
            lambda point: context_menu.exec(search_button.mapToGlobal(point)))
        # Icon
        FF_Additional_UI.UIIcon(
            os.path.join(FF_Files.ASSETS_FOLDER, "Find_button_img_small.png"), search_button.setIcon)
        search_button.setIconSize(QSize(25, 25))
        # Place
        search_button.setFixedWidth(120)
        self.Main_Layout.addWidget(search_button, 12, 12, Qt.AlignmentFlag.AlignLeft)

        # Set up the menu bar
        logging.info("Setting up Menu Bar...")
        self.menu_bar()

        # Setting filters to default
        self.reset_filters()

        # Showing PopUps
        FF_Additional_UI.Tutorial(parent=self.Root_Window)

        # Debug
        logging.info("Finished Setting up Main UI\n")

    # Functions to automate Labels
    @staticmethod
    def generate_large_filter_label(name: str, tab: QWidget, tooltip: str = ""):
        # Define the Label
        label = QLabel(name, parent=tab)
        # Change Font
        label.setFont(FF_Additional_UI.DEFAULT_QT_FONT)
        # Hover tool tip
        label.setToolTip(f"{tooltip}")
        label.setToolTipDuration(-1)
        # Display the Label
        label.show()
        # Return the label to place it in the layout
        return label

    # Function to automate entry creation
    def generate_filter_entry(self, tab: QWidget, only_int: bool = False):
        # Define the Entry
        entry = QLineEdit(tab)
        # Set the Length
        entry.resize(230, 26)
        entry.setFixedHeight(26)
        entry.setMinimumWidth(230)
        # If only_int true, configure the label
        if only_int:
            validator = QDoubleValidator(self.Root_Window)
            validator.setBottom(0)
            entry.setValidator(validator)
        # Display the Entry
        entry.show()
        # Return the Label to place it
        return entry

    # Function for automating radio buttons
    @staticmethod
    def create_radio_button(group, text, tab: QWidget):
        # Create Radio Button
        rb = QRadioButton(tab)
        # Set the Text
        rb.setText(text)
        # Add the Button to the Group
        group.addButton(rb)
        # Display the Button
        rb.show()
        # Return the Button
        return rb

    # Function for automating day edits
    @staticmethod
    def generate_day_entry(tab: QWidget):
        # Define dt_entry
        dt_entry = QDateEdit(tab)
        # Change dd.mm.yy to dd.MM.yyyy (e.g. 13.1.01 = 13.Jan.2001)
        dt_entry.setDisplayFormat("dd.MMM.yyyy")
        # Set a fixed width
        dt_entry.setFixedWidth(120)
        # Display
        dt_entry.show()
        # Return day time entry to place it in the layout
        return dt_entry

    # Functions to automate Buttons
    @staticmethod
    def generate_edit_button(command, tab: QWidget, text):
        # Generate the Button
        button = QPushButton(tab)
        # Change the Text
        button.setText(text)
        # Set the command
        button.clicked.connect(command)
        # Display the Button
        button.show()
        # Return the value of the Button, to place the button in the layout
        return button

    def generate_large_button(self, text, command, font_size):
        # Define the Button
        button = QPushButton(self.Root_Window)
        # Set the Text
        button.setText(text)
        # Set the font
        font = QFont(FF_Files.DEFAULT_FONT, font_size)
        font.setBold(True)
        button.setFont(font)
        # Set the Command
        button.clicked.connect(command)
        # Display the Button
        button.show()
        # Return the Button
        return button

    # Resetting all filters
    def reset_filters(self):
        if os.path.exists(os.path.join(FF_Files.FF_LIB_FOLDER, "Default.FFFilter")):
            # Debug
            logging.info("Resetting all filters to user set default...")

            self.import_filters(import_path=os.path.join(FF_Files.FF_LIB_FOLDER, "Default.FFFilter"))

        else:
            # Debug
            logging.info("Resetting all filters to standard default...")
            self.import_filters(import_dict=FF_Files.DEFAULT_FILTER)

    # Importing all filters from a FFFilter file
    def import_filters(self, import_path=None, import_dict=None):
        if import_path is None and import_dict is None:
            # Debug
            logging.info("Asking for location for import")
            import_path = QFileDialog.getOpenFileName(parent=self.Root_Window,
                                                      dir=FF_Files.USER_FOLDER,
                                                      caption="Import Filer or Search",
                                                      filter="File Find Filter or Search (*.FFFilter *.FFSearch)")[0]
            # If User pressed cancel
            if import_path == "":
                return
            # Normalise the path
            import_path = os.path.normpath(import_path)
            # If opened file is a search
            if import_path.endswith(".FFSearch"):
                FF_Search.LoadSearch.open_file(import_path, self.Root_Window)
                # Quit function
                return
        if import_dict is None:
            # Opening file, throws error if no files was selected
            try:
                with open(import_path, "rb") as import_file:
                    filters = load(fp=import_file)

            except FileNotFoundError:
                logging.warning(f"File not found: {import_path}")
                return
        else:
            filters = import_dict

        # Debug
        logging.info(f"Importing filters with version: {filters['VERSION']},"
                     f" while local version: {FF_Files.FF_FILTER_VERSION}...")
        # Checking for the existence of every filter
        for filter_check in FF_Files.DEFAULT_FILTER:
            try:
                filters[filter_check]
            except KeyError:
                filters[filter_check] = FF_Files.DEFAULT_FILTER[filter_check]

        # Basic
        self.edit_name.setText(filters["name"])
        self.name_specifier.setCurrentText(filters["name_specifier"])
        self.case_check_box.setChecked(filters["consider_case"])
        self.similarity_spinbox.setValue(filters["similarity"])

        self.edit_file_extension.setText(filters["file_extension"])
        self.change_file_type_mode(filters["file_type_mode"])
        self.combobox_file_types.check_items(filters["file_types"])

        directory = filters["directory"].replace("USER_FOLDER", FF_Files.USER_FOLDER)
        self.edit_directory.setText(directory)

        # Properties
        self.m_date_from_drop_down.setDate(QDate.fromString(filters["dates"]["m_date_from"], Qt.DateFormat.ISODate))
        self.c_date_from_drop_down.setDate(QDate.fromString(filters["dates"]["c_date_from"], Qt.DateFormat.ISODate))

        if filters["dates"]["m_date_to"] == "DEFAULT_DATE":
            self.m_date_to_drop_down.setDate(QDate.currentDate())
        else:
            self.m_date_to_drop_down.setDate(QDate.fromString(filters["dates"]["m_date_to"], Qt.DateFormat.ISODate))

        if filters["dates"]["c_date_to"] == "DEFAULT_DATE":
            self.c_date_to_drop_down.setDate(QDate.currentDate())
        else:
            self.c_date_to_drop_down.setDate(QDate.fromString(filters["dates"]["c_date_to"], Qt.DateFormat.ISODate))

        self.edit_size_min.setText(filters["size"]["min"])
        self.edit_size_max.setText(filters["size"]["max"])
        self.unit_selector_min.setCurrentText(filters["size_unit"]["min"])
        self.unit_selector_max.setCurrentText(filters["size_unit"]["max"])

        # Advanced
        self.combobox_folder_depth.setCurrentText(filters["folder_depth"])
        self.edit_folder_depth.setValue(filters["folder_depth_custom"])
        self.edit_file_contains.setText(filters["file_contains"])
        self.library_check_box.setChecked(filters["hidden_files"])
        self.combobox_search_for.setCurrentIndex(filters["files_folders"])

        # Sorting
        self.combobox_sorting.setCurrentIndex(filters["sorting"])
        self.reverse_sorting_check_box.setChecked(filters["reverse_sorting"])

        # Debug
        logging.info("Imported all filters\n")

    # Exporting all filters in to a FFFilter file
    def export_filters(self):
        # Debug
        logging.info("Request location for export")
        export_dialog = QFileDialog.getSaveFileName(parent=self.Root_Window,
                                                    dir=FF_Files.USER_FOLDER,
                                                    caption="Export File Find Search",
                                                    filter="File Find Filter Preset (*.FFFilter);;"
                                                           "JSON (JavaScript Object Notation) (*.json)")
        export_path = os.path.normpath(export_dialog[0])

        # If User pressed "Cancel"
        if export_path == "":
            return

        # If the suffix wasn't added, add it
        if not (export_path.endswith(".FFFilter") or export_path.endswith(".json")):
            if "FFFilter" in export_dialog[1]:
                export_path += ".FFFilter"
            else:
                export_path += ".json"

        # Debug
        logging.info(f"Exporting all filters to {export_path}, with {FF_Files.FF_FILTER_VERSION=}...")
        # Making user folder compatible
        directory = self.edit_directory.text()
        directory = directory.replace(FF_Files.USER_FOLDER, "USER_FOLDER")

        # If dates are left at default
        m_date_to = self.m_date_to_drop_down.date().toString(Qt.DateFormat.ISODate)
        c_date_to = self.c_date_to_drop_down.date().toString(Qt.DateFormat.ISODate)
        if m_date_to == QDate.currentDate().toString(Qt.DateFormat.ISODate):
            m_date_to = "DEFAULT_DATE"
        if c_date_to == QDate.currentDate().toString(Qt.DateFormat.ISODate):
            c_date_to = "DEFAULT_DATE"

        # Directory to save filter settings
        filters = {"VERSION": FF_Files.FF_FILTER_VERSION,

                   "name": self.edit_name.text(),
                   "name_specifier": self.name_specifier.currentText(),
                   "consider_case": self.case_check_box,
                   "similarity": self.similarity_spinbox.value(),
                   "file_types": self.combobox_file_types.all_checked_items(),
                   "file_extension": self.edit_file_extension.text(),
                   "file_type_mode": self.file_type_mode,
                   "directory": directory,

                   "dates": {"m_date_from": self.m_date_from_drop_down.date().toString(Qt.DateFormat.ISODate),
                             "c_date_from": self.c_date_from_drop_down.date().toString(Qt.DateFormat.ISODate),
                             "m_date_to": m_date_to,
                             "c_date_to": c_date_to},
                   "size": {"min": self.edit_size_min.text(),
                            "max": self.edit_size_max.text()},
                   "size_unit": {"min": self.unit_selector_min.currentText(),
                                 "max": self.unit_selector_max.currentText()},

                   "folder_depth": self.combobox_folder_depth.currentText(),
                   "folder_depth_custom": self.edit_folder_depth.value(),
                   "file_contains": self.edit_file_contains.text(),
                   "hidden_files": self.library_check_box.isChecked(),
                   "files_folders": self.combobox_search_for.currentIndex(),

                   "sorting": self.combobox_sorting.currentIndex(),
                   "reverse_sorting": self.reverse_sorting_check_box.isChecked()}

        # Try opening the file, crashes if user pressed "Cancel"
        try:
            with open(export_path, "w") as export_file:
                dump(obj=filters, fp=export_file)
        except FileNotFoundError:
            logging.warning(f"File not found: {export_path}")
        else:
            # Debug
            logging.info("Exported all filters\n")

    # Switch file type selection mode between custom and predefined
    def change_file_type_mode(self, set_to=None):
        if set_to is None:
            if self.file_type_mode == "predefined":
                set_to = "custom"
            else:
                set_to = "predefined"
        # Debug
        logging.debug(f"{self.file_type_mode=}, {set_to=}")
        # switch the mode
        if set_to == "custom":
            self.file_type_mode = "custom"
            self.change_file_type_mode_button.setText("Predefined")
            self.combobox_file_types.hide()
            self.edit_file_extension.show()

            self.select_all_button.setDisabled(True)
            self.deselect_all_button.setDisabled(True)
        else:
            self.file_type_mode = "predefined"
            self.change_file_type_mode_button.setText("Custom")
            self.combobox_file_types.show()
            self.edit_file_extension.hide()

            # Update the enabled-state of the "Select all" and "Deselect all"-buttons
            self.combobox_file_types.data_changed()

    # Setting up the menu bar
    def menu_bar(self):

        # Menu Bar
        menu_bar = self.Root_Window.menuBar()
        file_menu = menu_bar.addMenu("&File")
        edit_menu = menu_bar.addMenu("&Edit")
        tools_menu = menu_bar.addMenu("&Tools")
        tabs_menu = menu_bar.addMenu("&Tabs")
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Import filter preset
        load_filter_action = QAction("&Open Search / Filter Preset", self.Root_Window)
        load_filter_action.triggered.connect(lambda: self.import_filters())
        load_filter_action.setShortcut("Ctrl+O")
        file_menu.addAction(load_filter_action)

        # Export filter preset
        export_filter_action = QAction("&Save current filters as Filter Preset", self.Root_Window)
        export_filter_action.triggered.connect(self.export_filters)
        export_filter_action.setShortcut("Ctrl+S")
        file_menu.addAction(export_filter_action)

        # Separator
        file_menu.addSeparator()

        # Clear Cache
        cache_action = QAction("&Clear Cache", self.Root_Window)
        cache_action.triggered.connect(FF_Files.remove_cache)
        cache_action.triggered.connect(
            lambda: FF_Additional_UI.PopUps.show_info_messagebox("Cleared Cache",
                                                                 "Cleared Cache successfully!",
                                                                 self.Root_Window))
        cache_action.setShortcut("Ctrl+T")
        tools_menu.addAction(cache_action)

        # Reset filter
        reset_action = QAction("&Reset all filters", self.Root_Window)
        reset_action.triggered.connect(self.reset_filters)
        reset_action.setShortcut("Ctrl+R")
        tools_menu.addAction(reset_action)

        # About File Find
        about_action = QAction("&About File Find", self.Root_Window)
        about_action.triggered.connect(lambda: FF_About_UI.AboutWindow(self.Root_Window))
        help_menu.addAction(about_action)

        # Settings
        settings_action = QAction("&Settings", self.Root_Window)
        settings_action.triggered.connect(lambda: FF_Settings.SettingsWindow(self.Root_Window))
        settings_action.setShortcut("Ctrl+,")
        help_menu.addAction(settings_action)

        # Tutorial
        tutorial_action = QAction("&Tutorial", self.Root_Window)
        tutorial_action.triggered.connect(lambda: FF_Additional_UI.Tutorial(self.Root_Window, force_tutorial=True))
        help_menu.addAction(tutorial_action)

        # Show File Find window
        reopen_action = QAction("&Show File Find Window", self.Root_Window)
        reopen_action.setShortcut("Ctrl+D")

        def reopen_window():
            # Resize the window
            self.Root_Window.resize(self.Root_Window.baseSize())
            self.Root_Window.show()

        reopen_action.triggered.connect(reopen_window)
        window_menu.addAction(reopen_action)

        # Hide File Find window
        hide_action = QAction("&Hide File Find Window", self.Root_Window)
        hide_action.setShortcut("Ctrl+W")
        hide_action.triggered.connect(self.Root_Window.hide)
        window_menu.addAction(hide_action)

        # Search Action
        search_action = QAction("&Search", self.Root_Window)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.search_entry)
        edit_menu.addAction(search_action)

        # Search and create new cache for selected folder action
        search_without_cache_action = QAction("Search and create new cache for selected folder", self.Root_Window)
        search_without_cache_action.setShortcut("Ctrl+Shift+F")
        search_without_cache_action.triggered.connect(self.create_cache_and_search)
        edit_menu.addAction(search_without_cache_action)

        # Switch Tabs
        # Basic
        switch_tab_basic = QAction("Switch to tab Basic", self.Root_Window)
        switch_tab_basic.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(0))
        switch_tab_basic.setShortcut("Ctrl+1")
        # File Content
        switch_tab_properties = QAction("Switch to tab Properties", self.Root_Window)
        switch_tab_properties.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(1))
        switch_tab_properties.setShortcut("Ctrl+2")
        # Advanced
        switch_tab_advanced = QAction("Switch to tab Advanced", self.Root_Window)
        switch_tab_advanced.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(2))
        switch_tab_advanced.setShortcut("Ctrl+3")
        # Sorting
        switch_tab_sorting = QAction("Switch to tab Sorting", self.Root_Window)
        switch_tab_sorting.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(3))
        switch_tab_sorting.setShortcut("Ctrl+4")
        # Add options to menu
        tabs_menu.addActions([switch_tab_basic, switch_tab_properties, switch_tab_advanced, switch_tab_sorting])

        # Building menu bar icon
        return self.menu_bar_icon(about_action, reopen_action)

    # Menu-bar icon
    def menu_bar_icon(self, about_action, reopen_action):
        logging.debug("Constructing Menu-bar icon...")

        # Menu for menu_bar_icon_menu
        global menu_bar_icon_menu
        menu_bar_icon_menu = QMenu(self.Root_Window)

        # Add this icon to the menu bar
        global menu_bar_icon
        menu_bar_icon = QSystemTrayIcon(self.Root_Window)

        if platform == "win32" or platform == "cygwin":
            menu_bar_icon.activated.connect(self.Root_Window.show)

        # Icon
        # On macOS
        if platform == "darwin":
            # Make it automatically turn dark if background is light and the other way around
            # On macOS this doesn't depend on dark/light mode
            menu_bar_icon_icon = QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Menubar_icon_small.png"))
            # Only works on macOS
            menu_bar_icon_icon.setIsMask(True)
            menu_bar_icon.setIcon(menu_bar_icon_icon)
        # On Windows and Linux
        else:
            # Have the icon change with dark mode
            FF_Additional_UI.UIIcon(path=os.path.join(FF_Files.ASSETS_FOLDER, "Menubar_icon_small.png"),
                                    icon_set_func=menu_bar_icon.setIcon)

        # File Find Title
        ff_title = QAction("&File Find", self.Root_Window)
        ff_title.setDisabled(True)

        # Search Status Menu
        global search_status_menu
        search_status_menu = QMenu("&Searches:", self.Root_Window)
        search_status_menu.setDisabled(True)

        # Quit File Find
        quit_action = QAction("&Quit File Find", self.Root_Window)
        quit_action.triggered.connect(sys.exit)

        # Constructing menu_bar_icon_menu
        menu_bar_icon_menu.addAction(ff_title)
        menu_bar_icon_menu.addSeparator()
        menu_bar_icon_menu.addMenu(search_status_menu)
        menu_bar_icon_menu.addMenu(search_status_menu)
        menu_bar_icon_menu.addSeparator()
        menu_bar_icon_menu.addAction(reopen_action)
        menu_bar_icon_menu.addSeparator()
        menu_bar_icon_menu.addAction(about_action)
        menu_bar_icon_menu.addAction(quit_action)

        # Display the Icon if allowed
        menu_bar_icon.setContextMenu(menu_bar_icon_menu)
        if FF_Settings.SettingsWindow.load_setting("display_menu_bar_icon"):
            menu_bar_icon.show()

        return menu_bar_icon

    # Generic Label input
    @staticmethod
    def generic_tooltip(name, description, example_in, example_out) -> str:
        tooltip = f"{name}:\n{description}\n\nExample Input: {example_in}\nExample Output: {example_out}"
        return tooltip

    # Updating Actives Searches Label
    @staticmethod
    def update_search_status_label(ui_building=False):
        # Debug
        logging.debug(f"Updating search status label, active searches: {FF_Search.ACTIVE_SEARCH_THREADS}")
        # If there are no active searches
        if FF_Search.ACTIVE_SEARCH_THREADS == 0:
            search_status_label.setText("Idle")
            search_status_label.change_color(FF_Files.GREEN_LIGHT_THEME_COLOR, FF_Files.GREEN_DARK_THEME_COLOR)
            search_status_label.adjustSize()

        # While the UI is being build, you cannot use File Find
        elif ui_building:
            search_status_label.setText(f"Please Wait ({FF_Search.ACTIVE_SEARCH_THREADS}) ...")

        # If there are ongoing searches updating label
        else:
            search_status_label.setText(f"Active ({FF_Search.ACTIVE_SEARCH_THREADS}) ...")
            search_status_label.change_color(FF_Files.RED_LIGHT_THEME_COLOR, FF_Files.RED_DARK_THEME_COLOR)
            search_status_label.adjustSize()

    # Search with a new cache
    def create_cache_and_search(self):
        logging.info("Searching with a new cache file..")
        # Search
        self.search_entry(new_cache_file=True)


class SearchUpdate:
    def __init__(self, path: str):
        # Updating Label
        MainWindow.update_search_status_label()

        # Assigning local values
        self.menubar_icon_menu: QMenu = menu_bar_icon_menu
        self.search_status_menu: QMenu = search_status_menu

        # Path action
        self.search_path: QAction = QAction(f"In {path}:")
        self.search_path.setDisabled(True)

        # Setup search status
        self.search_status: QAction = QAction("Setup Search Status...")
        self.search_status.setDisabled(True)

        # Setup
        search_status_menu.addSeparator()
        search_status_menu.addAction(self.search_path)
        search_status_menu.addAction(self.search_status)

    def update(self, text: str):
        self.search_status.setText(text)

    def close(self):
        self.search_status_menu.removeAction(self.search_status)
        self.search_status_menu.removeAction(self.search_path)


global menu_bar_icon_menu, search_status_menu, menu_bar_icon, search_status_label
