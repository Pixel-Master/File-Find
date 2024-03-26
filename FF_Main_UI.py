# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the main window

# Imports
import logging
import os
from json import dump, load
from pyperclip import copy

# PySide6 Gui Imports
from PySide6.QtCore import QSize, Qt, QDate
from PySide6.QtGui import QFont, QDoubleValidator, QAction, QKeySequence, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QRadioButton, QFileDialog, \
    QLineEdit, QButtonGroup, QDateEdit, QComboBox, QSystemTrayIcon, QMenu, QCompleter, QTabWidget, \
    QMainWindow, QGridLayout, QSpacerItem, QSizePolicy, QApplication

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Help_UI
import FF_Search
import FF_Settings


# The class for the main window where filters can be selected
class MainWindow:
    def __init__(self, app: QApplication):
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
        # Spacer for having blank spaces
        horizontal_spacer = QSpacerItem(600, 0, hData=QSizePolicy.Policy.Maximum)

        # Labels
        logging.debug("Setting up Labels...")
        # Create a Label for every Filter with the Function, defined above
        # -----Basic Search-----
        # Tabs and Label
        # Creating a new QWidget for the Basic tab
        self.basic_search_widget = QWidget()
        # Layout
        self.basic_search_widget_layout = QGridLayout(self.basic_search_widget)
        self.basic_search_widget.setLayout(self.basic_search_widget_layout)
        self.basic_search_widget_layout.addItem(horizontal_spacer, 0, 0)
        self.basic_search_widget_layout.addItem(horizontal_spacer, 0, 5)
        # Add Tab
        self.tabbed_widget.addTab(self.basic_search_widget, "Basic")

        # Creating the Labels with tooltips
        label_name = self.generate_large_filter_label(
            "Name:",
            self.basic_search_widget,
            self.generic_tooltip("Name",
                                 "Input needs to match the name of a file exactly, \nignoring case.\n\n"
                                 "Also supports unix shell-style wildcards,\n"
                                 "which are not the same as regular expressions. (also ignoring case)\n\nUsage:\n"
                                 "Pattern   Meaning\n"
                                 "   *         matches everything\n"
                                 "   ?         matches any single character\n"
                                 " [seq]    matches any character in seq\n"
                                 " [!seq]   matches any character not in seq\n\n"
                                 "For further documentation: http://docs.python.org/library/fnmatch",
                                 "Example.txt",
                                 os.path.join(FF_Files.USER_FOLDER, "example.txt")))
        self.basic_search_widget_layout.addWidget(label_name, 0, 1)

        label_name_contains = self.generate_large_filter_label(
            "Name contains:",
            self.basic_search_widget,
            self.generic_tooltip("Name contains",
                                 "The name of a file must contain input,\nignoring case.",
                                 "file",
                                 os.path.join(FF_Files.USER_FOLDER, "my-file.pdf")))
        self.basic_search_widget_layout.addWidget(label_name_contains, 1, 1)

        label_file_group = self.generate_large_filter_label(
            "File Types:",
            self.basic_search_widget,
            self.generic_tooltip("File Types",
                                 "Select groups of files that should be included in search results",
                                 "Music",
                                 os.path.join(FF_Files.USER_FOLDER, "song.mp3")))
        self.basic_search_widget_layout.addWidget(label_file_group, 2, 1)

        label_directory = self.generate_large_filter_label(
            "Directory:",
            self.basic_search_widget,
            self.generic_tooltip("Directory",
                                 "The Directory to search in.",
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
        # Creating a new QWidget for the file content tab
        self.content_search_widget = QWidget()
        # Layout
        self.content_search_widget_layout = QGridLayout(self.content_search_widget)
        self.content_search_widget.setLayout(self.content_search_widget_layout)
        # Adding space
        self.content_search_widget_layout.addItem(horizontal_spacer, 0, 0)
        self.content_search_widget_layout.addItem(horizontal_spacer, 0, 6)
        # Add Tab
        self.tabbed_widget.addTab(self.content_search_widget, "Properties")

        # Search for file content
        label_file_contains = self.generate_large_filter_label(
            "File contains:",
            self.content_search_widget,
            self.generic_tooltip("File contains:",
                                 "Allows you to search in files. Input must be in the file content.\n"
                                 "This option can take really long.\nInput is case-sensitive.",
                                 "This is an example file!",
                                 os.path.join(
                                     FF_Files.USER_FOLDER, "example.txt (which contains: This is an example file!)")))
        self.content_search_widget_layout.addWidget(label_file_contains, 0, 1)

        # Creation date
        label_c_date = self.generate_large_filter_label(
            "Date created:",
            self.content_search_widget,
            self.generic_tooltip("Date created",
                                 "Specify a date range for the date the file has been created,\n"
                                 "leave at default to ignore.",
                                 "5.Jul.2020 - 10.Aug.2020",
                                 os.path.join(FF_Files.USER_FOLDER, "example.txt (created at 1.Aug.2020)")))
        self.content_search_widget_layout.addWidget(label_c_date, 1, 1)
        label_c_date_2 = self.generate_large_filter_label("-", self.content_search_widget)
        self.content_search_widget_layout.addWidget(label_c_date_2, 1, 3)

        # Date modified
        label_m_date = self.generate_large_filter_label(
            "Date modified:",
            self.content_search_widget,
            self.generic_tooltip("Date modified",
                                 "Specify a date range for the date the file has been modified,\n "
                                 "leave at default to ignore.",
                                 "5.Jul.2020 -  10.Aug.2020",
                                 os.path.join(FF_Files.USER_FOLDER, "example.txt (modified at 1.Aug.2020)")))
        self.content_search_widget_layout.addWidget(label_m_date, 2, 1)
        label_m_date_2 = self.generate_large_filter_label("-", self.content_search_widget)
        self.content_search_widget_layout.addWidget(label_m_date_2, 2, 3)

        label_file_size = self.generate_large_filter_label(
            "File size(MB) min:",
            self.content_search_widget,
            self.generic_tooltip("File size",
                                 "Input specifies file size in Mega Bytes (MB)\nin a range from min to max",
                                 "min: 10 max: 10.3",
                                 os.path.join(FF_Files.USER_FOLDER, "example.txt (with a size of 10.2 MB)")))
        self.content_search_widget_layout.addWidget(label_file_size, 3, 1)
        label_file_size_max = self.generate_large_filter_label("max:", self.content_search_widget)
        self.content_search_widget_layout.addWidget(label_file_size_max, 3, 3)

        # -----Advanced Search-----
        # Tab and Label
        # Creating a new QWidget for the file content tab
        self.advanced_search_widget = QWidget()
        # Layout
        self.advanced_search_widget_layout = QGridLayout(self.advanced_search_widget)
        self.advanced_search_widget.setLayout(self.advanced_search_widget_layout)
        # Adding a spacer
        self.advanced_search_widget_layout.addItem(horizontal_spacer, 0, 0)
        self.advanced_search_widget_layout.addItem(horizontal_spacer, 0, 6)
        # Add Tab
        self.tabbed_widget.addTab(self.advanced_search_widget, "Advanced")

        label_extension = self.generate_large_filter_label(
            "File ending:",
            self.advanced_search_widget,
            self.generic_tooltip("File ending",
                                 "Input needs to match the file ending (file type)\nwithout the \".\","
                                 " ignoring case.",
                                 "txt",
                                 os.path.join(
                                     FF_Files.USER_FOLDER,
                                     "example.txt")))
        self.advanced_search_widget_layout.addWidget(label_extension, 0, 1)

        label_system_files = self.generate_large_filter_label(
            "Search in system files:",
            self.advanced_search_widget,
            self.generic_tooltip("Search in system files",
                                 "Toggle to include files in the system and library folders.",
                                 "Yes",
                                 os.path.join(FF_Files.USER_FOLDER, "Library", "Caches", "example.txt")))
        self.advanced_search_widget_layout.addWidget(label_system_files, 1, 1)

        label_files_folders = self.generate_large_filter_label(
            "Search for:",
            self.advanced_search_widget,
            self.generic_tooltip("Search for",
                                 "Toggle to only include folders or files in the search results",
                                 "only Folders",
                                 os.path.join(FF_Files.USER_FOLDER, "Downloads")))
        self.advanced_search_widget_layout.addWidget(label_files_folders, 2, 1)

        # -----Sorting-----
        # Tab and Label
        # Creating a new QWidget for the Advanced tab
        self.sorting_widget = QWidget()
        # Layout
        self.sorting_widget_layout = QGridLayout(self.sorting_widget)
        self.sorting_widget.setLayout(self.sorting_widget_layout)
        # Adding a spacer
        self.sorting_widget_layout.addItem(horizontal_spacer, 0, 0)
        self.sorting_widget_layout.addItem(horizontal_spacer, 0, 6)
        # Add Tab
        self.tabbed_widget.addTab(self.sorting_widget, "Sorting")

        label_sort_by = self.generate_large_filter_label(
            "Sort by:",
            self.sorting_widget,
            self.generic_tooltip("Sort by",
                                 "Select a sorting method to sort the results.",
                                 "File Size",
                                 "Results sorted by file size"))
        self.sorting_widget_layout.addWidget(label_sort_by, 0, 1)

        label_reverse_sort = self.generate_large_filter_label(
            "Reverse results:",
            self.sorting_widget,
            self.generic_tooltip("Reverse Results",
                                 "Reverse the sorted search results.",
                                 "Yes",
                                 "Reversed search results"))
        self.sorting_widget_layout.addWidget(label_reverse_sort, 1, 1)

        # -----Terminal Command-----
        # Label, saying command
        label_command_title = QLabel(self.Root_Window)
        label_command_title.setText("Command:")
        label_command_title.setToolTip(
            "Terminal command:\nYou can paste this command into the Terminal app to search with the \"find\" tool")
        label_command_title.setFont(QFont("Arial", 17))
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
        search_status_title_label = QLabel("Status:", self.Root_Window)
        search_status_title_label.setFont(QFont("Arial", 17))
        search_status_title_label.setToolTip(
            "Search Indicator:\n"
            "Indicates if searching and shows the numbers of active searches.\n"
            "For more precise information click on the File Find logo in the menu-bar.")
        search_status_title_label.show()
        self.Main_Layout.addWidget(search_status_title_label, 12, 0)

        # Label to indicate if searching
        global search_status_label
        search_status_label = QLabel("Inactive", self.Root_Window)
        search_status_label.setFont(QFont("Arial", 17))
        search_status_label.setStyleSheet("color: green;")
        search_status_label.show()
        self.Main_Layout.addWidget(search_status_label, 12, 1)
        self.Main_Layout.addItem(horizontal_spacer, 12, 2)

        # Entries
        logging.debug("Setting up Entries...")

        # Create an Entry for every Filter with the function self.generate_filter_entry()

        # Name
        self.edit_name = self.generate_filter_entry(self.basic_search_widget)
        # Place
        self.basic_search_widget_layout.addWidget(self.edit_name, 0, 2)

        # Name contains
        self.edit_name_contains = self.generate_filter_entry(self.basic_search_widget)
        # Place
        self.basic_search_widget_layout.addWidget(self.edit_name_contains, 1, 2)

        # File extension
        self.edit_file_extension = self.generate_filter_entry(self.advanced_search_widget)
        # Place
        self.advanced_search_widget_layout.addWidget(self.edit_file_extension, 0, 2, 1, 5)

        # Edit for displaying the Path
        self.edit_directory = self.generate_filter_entry(self.basic_search_widget)
        # Set text and tooltip to display the directory
        self.edit_directory.setText(os.getcwd())
        # Execute the validate_dir function if text is changed
        self.edit_directory.textChanged.connect(self.validate_dir)
        # Loading Completions
        self.complete_path(os.getcwd(), check=False)
        # Resize and place on screen
        self.basic_search_widget_layout.addWidget(self.edit_directory, 3, 2)

        # File contains
        self.edit_file_contains = self.generate_filter_entry(self.advanced_search_widget)
        self.edit_file_contains.resize(230, 25)
        self.content_search_widget_layout.addWidget(self.edit_file_contains, 0, 2, 1, 4)

        # File size min
        self.edit_size_min = self.generate_filter_entry(self.advanced_search_widget, True)
        self.edit_size_min.setFixedWidth(60)
        self.content_search_widget_layout.addWidget(self.edit_size_min, 3, 2)

        # File size max
        self.edit_size_max = self.generate_filter_entry(self.advanced_search_widget, True)
        self.edit_size_max.setFixedWidth(60)
        self.content_search_widget_layout.addWidget(self.edit_size_max, 3, 4)

        # Radio Button
        logging.debug("Setting up Radio Buttons...")
        # Search for Library Files
        # Group for Radio Buttons
        self.library_group = QButtonGroup(self.Root_Window)
        # Radio Button 1
        self.rb_library_yes = self.create_radio_button(self.library_group, "Yes", self.advanced_search_widget)
        # Add the button to the layout
        self.advanced_search_widget_layout.addWidget(self.rb_library_yes, 1, 2)
        # Radio Button 2
        self.rb_library_no = self.create_radio_button(self.library_group, "No", self.advanced_search_widget)
        # Add the button to the layout
        self.advanced_search_widget_layout.addWidget(self.rb_library_no, 1, 2, 1, 4, Qt.AlignmentFlag.AlignCenter)
        # Select the Button 2
        self.rb_library_no.setChecked(True)

        # Reverse Sort
        # Group for Radio Buttons
        reverse_sort_group = QButtonGroup(self.Root_Window)
        # Radio Button 1
        rb_reverse_sort_yes = self.create_radio_button(reverse_sort_group, "Yes", self.sorting_widget)
        # Add the button to the layout
        self.sorting_widget_layout.addWidget(rb_reverse_sort_yes, 1, 2)
        # Radio Button 2
        rb_reverse_sort_no = self.create_radio_button(reverse_sort_group, "No", self.sorting_widget)
        # Add the button to the layout
        self.sorting_widget_layout.addWidget(rb_reverse_sort_no, 1, 3)
        # Select the Button
        rb_reverse_sort_no.setChecked(True)

        # Drop Down Menus
        logging.debug("Setting up Combo Boxes...")

        # Sorting Menu
        # Defining
        self.combobox_sorting = QComboBox(self.sorting_widget)
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
        self.sorting_widget_layout.addWidget(self.combobox_sorting, 0, 2, 1, 4)

        # Search for Files or Folders Menu
        # Defining
        self.combobox_search_for = QComboBox(self.advanced_search_widget)
        # Adding Options
        self.combobox_search_for.addItems(
            ["Files and Folders",
             "only Files",
             "only Folders"])
        # Display
        self.combobox_search_for.setFixedWidth(200)
        self.advanced_search_widget_layout.addWidget(self.combobox_search_for, 2, 2)

        # Search for file types: all, images, movies, music, etc...
        self.combobox_file_types = FF_Additional_UI.CheckableComboBox(self.advanced_search_widget)
        self.combobox_file_types.addItems(FF_Files.FILE_FORMATS.keys())
        self.combobox_file_types.setFixedWidth(230)
        # Display
        self.combobox_file_types.show()
        self.basic_search_widget_layout.addWidget(self.combobox_file_types, 2, 2)

        # The combobox for file types and the file ending line edit can not be used together,
        # as there will be no files found
        def block_file_types():
            # Block / Unblock File ending edit
            if self.combobox_file_types.all_checked_items() != list(FF_Files.FILE_FORMATS.keys()):
                # Disable File ending edit
                # Debug
                logging.debug("Disabled file ending edit")
                # Block the file ending edit
                self.edit_file_extension.setDisabled(True)
                self.edit_file_extension.setToolTip("File types can't be used together with file extension")
                self.edit_file_extension.setStyleSheet("background-color: #7f7f7f;")
            else:
                # Debug
                logging.debug("Enabled file ending edit")
                # Enable the file ending edit
                self.edit_file_extension.setDisabled(False)
                self.edit_file_extension.setToolTip("")
                self.edit_file_extension.setStyleSheet(";")

            # Block/ Unblock FIle groups combobox
            if self.edit_file_extension.text() == "":
                # Debug
                logging.debug("Enabled combobox file groups")
                # Enable Combobox
                # Set the displayed text to the original
                self.combobox_file_types.setPlaceholderText(self.combobox_file_types.determine_text())
                self.combobox_file_types.setDisabled(False)
                self.combobox_file_types.setToolTip("")
                # Enabling "select all" and "Deselect all" buttons
                self.combobox_file_types.data_changed()

            # If something is written in the file ending edit
            else:
                # Enable Combobox
                # Debug
                logging.debug("Disabled combobox file groups")
                # Set the displayed text to the text of the line edit
                self.combobox_file_types.setPlaceholderText(self.edit_file_extension.text())
                self.combobox_file_types.setDisabled(True)
                self.combobox_file_types.setToolTip("File types can't be used together with file extension")
                # Disabling "select all" and "Deselect all" buttons
                deselect_all_button.setDisabled(True)
                select_all_button.setDisabled(True)

        # Connecting change signals to the function defined above
        self.edit_file_extension.textChanged.connect(block_file_types)
        self.combobox_file_types.model().dataChanged.connect(block_file_types)

        # Date-Time Entries
        logging.debug("Setting up Day Entries...")
        # Date Created
        self.c_date_from_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.content_search_widget_layout.addWidget(self.c_date_from_drop_down, 1, 2)
        self.c_date_to_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.c_date_to_drop_down.setDate(QDate.currentDate())
        self.content_search_widget_layout.addWidget(self.c_date_to_drop_down, 1, 4)

        # Date Modified
        self.m_date_from_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.content_search_widget_layout.addWidget(self.m_date_from_drop_down, 2, 2)
        self.m_date_to_drop_down = self.generate_day_entry(self.advanced_search_widget)
        self.m_date_to_drop_down.setDate(QDate.currentDate())
        self.content_search_widget_layout.addWidget(self.m_date_to_drop_down, 2, 4)

        # Push Buttons
        logging.debug("Setting up Push Buttons...")

        # Buttons

        # Search from Button
        # Opens the File dialogue and changes the current working dir into the returned value
        def open_dialog():
            search_from = QFileDialog.getExistingDirectory(dir=os.getcwd())
            try:
                os.chdir(search_from)
                self.edit_directory.setText(search_from)
            except OSError:
                pass

        browse_path_button = self.generate_edit_button(open_dialog, self.basic_search_widget, text="Browse")
        browse_path_button.setFixedWidth(80)
        self.basic_search_widget_layout.addWidget(browse_path_button, 3, 3)

        # Select and deselect all options in the check able file group combobox
        select_all_button = self.generate_edit_button(
            self.combobox_file_types.select_all, self.basic_search_widget, text="Select all")
        select_all_button.setFixedWidth(80)
        self.basic_search_widget_layout.addWidget(select_all_button, 2, 3)
        select_all_button.setEnabled(False)

        deselect_all_button = self.generate_edit_button(
            self.combobox_file_types.deselected_all, self.basic_search_widget, text="Deselect all")
        # Place on the layout
        deselect_all_button.setFixedWidth(90)
        self.basic_search_widget_layout.addWidget(deselect_all_button, 2, 4)

        # Activate/Deactivate buttons if necessary
        self.combobox_file_types.button_signals.all_selected.connect(lambda: deselect_all_button.setDisabled(False))
        self.combobox_file_types.button_signals.all_selected.connect(lambda: select_all_button.setDisabled(True))
        # If only some options are enabled
        self.combobox_file_types.button_signals.some_selected.connect(lambda: deselect_all_button.setDisabled(False))
        self.combobox_file_types.button_signals.some_selected.connect(lambda: select_all_button.setDisabled(False))
        # If all files are deselected
        self.combobox_file_types.button_signals.all_deselected.connect(lambda: deselect_all_button.setDisabled(True))
        self.combobox_file_types.button_signals.all_deselected.connect(lambda: select_all_button.setDisabled(False))

        # Print the given data
        def print_data():
            logging.info(
                f"\nFilters:\n"
                f"Name: {self.edit_name.text()}\n"
                f"Name contains: {self.edit_name_contains.text()}\n"
                f"File Ending: {self.edit_file_extension.text()}\n"
                f"Search from: {os.getcwd()}\n\n"
                f"File size(MB): min:{self.edit_size_min.text()} max:{self.edit_size_max.text()}\n"
                f"Date modified from: {self.m_date_from_drop_down.text()} to: {self.m_date_to_drop_down.text()}\n"
                f"Date created from: {self.c_date_from_drop_down.text()} to: {self.c_date_to_drop_down.text()}\n"
                f"Content: {self.edit_file_contains.text()}\n\n"
                f"Search for system files: {self.rb_library_yes.isChecked()}\n"
                f"Search for: {self.combobox_search_for.currentText()}\n"
                f"File Groups: {self.combobox_file_types.all_checked_items()}\n\n"
                f"Sort results by: {self.combobox_sorting.currentText()}\n"
                f"Reverse results: {rb_reverse_sort_yes.isChecked()}\n")

        # Start Search with args locally
        def search_entry():
            # Debug
            logging.debug("User clicked Find")

            # Print Input
            print_data()
            # Start Searching
            FF_Search.Search(
                data_name=self.edit_name.text(),
                data_in_name=self.edit_name_contains.text(),
                data_filetype=self.edit_file_extension.text(),
                data_file_size_min=self.edit_size_min.text(), data_file_size_max=self.edit_size_max.text(),
                data_library=self.rb_library_yes.isChecked(),
                data_search_from_valid=os.getcwd(),
                data_search_from_unchecked=self.edit_directory.text(),
                data_content=self.edit_file_contains.text(),
                data_search_for=self.combobox_search_for.currentText(),
                data_date_edits={"c_date_from": self.c_date_from_drop_down,
                                 "c_date_to": self.c_date_to_drop_down,
                                 "m_date_from": self.m_date_from_drop_down,
                                 "m_date_to": self.m_date_to_drop_down},
                data_sort_by=self.combobox_sorting.currentText(),
                data_reverse_sort=rb_reverse_sort_yes.isChecked(),
                data_file_group=self.combobox_file_types.all_checked_items(),
                parent=self.Root_Window)

        # Saves the function in a different var
        self.search_entry = search_entry

        # Generate a shell command, that displays in the UI
        def generate_terminal_command():
            # Debug
            logging.debug("User clicked Generate Terminal Command")

            # Print the data
            print_data()

            def copy_command():
                # Copying the command
                copy(shell_command)
                # Feedback to the User
                logging.info(f"Copied Command: {shell_command}")
                # Messagebox
                FF_Additional_UI.PopUps.show_info_messagebox("Successful copied!",
                                                             f"Successful copied Command:\n{shell_command} !",
                                                             self.Root_Window)

            # Calling the function, which generate a shell command
            shell_command = str(
                FF_Search.GenerateTerminalCommand(self.edit_name.text(), self.edit_name_contains.text(),
                                                  self.edit_file_extension.text(), self.edit_size_max.text()))

            # Showing the label that says "Command:"
            label_command_title.show()

            # Displaying the command label
            label_command.setText(shell_command)
            label_command.setToolTip(shell_command)
            label_command.show()

            # Copy Command Button
            # Disconnect the button set a new click event
            try:
                button_command_copy.clicked.disconnect()
            except (TypeError, RuntimeError):
                pass
            button_command_copy.clicked.connect(copy_command)
            # Display the Button at the correct position
            button_command_copy.show()

        # Large Buttons
        # Search button with image, to start searching

        # Menu when Right-clicking
        context_menu = QMenu(self.Root_Window)

        # Search and delete cache for selected folder action
        action_search_without_cache = QAction("Search and delete cache for selected folder", self.Root_Window)
        action_search_without_cache.triggered.connect(self.delete_cache_and_search)
        context_menu.addAction(action_search_without_cache)

        # Separator
        context_menu.addSeparator()

        # Load Search Action
        action_open_search = QAction("&Open Search / Filter Preset", self.Root_Window)
        action_open_search.triggered.connect(lambda: self.import_filters())
        context_menu.addAction(action_open_search)

        # Shell Command Action
        action_terminal = QAction("Generate Terminal Command", self.Root_Window)
        action_terminal.triggered.connect(generate_terminal_command)
        context_menu.addAction(action_terminal)

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
        self.menu_bar(generate_terminal_command, app)

        # Setting filters to default
        self.reset_filters()

        # Showing PopUps
        FF_Additional_UI.welcome_popups(parent=self.Root_Window)

        # Debug
        logging.info("Finished Setting up Main UI\n")

    # Functions to automate Labels
    @staticmethod
    def generate_large_filter_label(name: str, tab: QWidget, tooltip: str = ""):
        # Define the Label
        label = QLabel(name, parent=tab)
        # Change Font
        label.setFont(QFont("Arial", 17))
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
        entry.resize(230, 20)
        entry.setFixedHeight(25)
        entry.setFixedWidth(230)
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
        font = QFont("Arial", font_size)
        font.setBold(True)
        button.setFont(font)
        # Set the Command
        button.clicked.connect(command)
        # Display the Button
        button.show()
        # Return the Button
        return button

    # Auto complete paths
    def complete_path(self, path, check=True):

        # Adds all folders in path into paths
        def get_paths():
            paths = []
            for list_folder in os.listdir(path):
                if os.path.isdir(list_folder):
                    paths.append(os.path.join(os.getcwd(), list_folder))

            # Returns the list
            return paths

        # Check if "/" is at end of inputted path
        if check:
            # Going through all paths to look if auto-completion should be loaded
            if path.endswith("/"):
                completer_paths = get_paths()
                logging.debug("Changed QCompleter")
            else:
                return

        # If executed at launch skip check because home path doesn't end with a "/"
        else:
            completer_paths = get_paths()
            logging.debug("Changed QCompleter")

        # Set the saved list as Completer
        directory_line_edit_completer = QCompleter(completer_paths, parent=self.Root_Window)
        self.edit_directory.setCompleter(directory_line_edit_completer)

    # Validate Paths in the directory box
    def validate_dir(self):
        # Debug
        logging.debug(f"Directory Path changed to: {self.edit_directory.text()}")

        # Get the text
        check_path = self.edit_directory.text()

        # Changing Tool-Tip
        self.edit_directory.setToolTip(self.edit_directory.text())

        # Testing if path is folder
        if os.path.isdir(check_path):
            # Changing Path
            logging.debug(f"Path: {check_path} valid")
            os.chdir(check_path)

            # Change color
            self.edit_directory.setStyleSheet("")

            # Updating Completions
            self.complete_path(check_path)

        else:
            # Debug
            logging.debug(f"Path: {check_path} invalid")

            # Change color
            self.edit_directory.setStyleSheet("color: red;")

            # Resetting all filters

    def reset_filters(self):
        if os.path.exists(os.path.join(FF_Files.FF_LIB_FOLDER, "Default.FFFilter")):
            # Debug
            logging.info("Resetting all filters to user set default...")

            self.import_filters(os.path.join(FF_Files.FF_LIB_FOLDER, "Default.FFFilter"))

        else:

            # Debug
            logging.info("Resetting all filters to standard default...")

            # Resetting basic window
            self.edit_name.setText("")
            self.edit_name_contains.setText("")
            self.combobox_file_types.select_all()
            self.edit_directory.setText(FF_Files.USER_FOLDER)

            # Resetting Properties
            self.edit_file_contains.setText("")

            self.m_date_from_drop_down.setDate(QDate(2000, 1, 1))
            self.c_date_from_drop_down.setDate(QDate(2000, 1, 1))

            self.m_date_to_drop_down.setDate(QDate.currentDate())
            self.c_date_to_drop_down.setDate(QDate.currentDate())

            self.edit_size_max.setText("")
            self.edit_size_min.setText("")

            # Resetting Advanced
            self.edit_file_extension.setText("")
            self.rb_library_yes.setChecked(False)
            self.combobox_search_for.setCurrentIndex(0)

            # Resetting Sorting
            self.combobox_sorting.setCurrentIndex(0)
            self.rb_library_yes.setChecked(False)

        # Debug
        logging.info("Set all filters to default")

    # Importing all filters from a FFFilter file
    def import_filters(self, import_path=None):
        if import_path is None:
            # Debug
            logging.info("Asking for location for export")
            import_path = QFileDialog.getOpenFileName(parent=self.Root_Window,
                                                      dir=FF_Files.USER_FOLDER,
                                                      caption="Export File Find Search",
                                                      filter="*.FFFilter;*.FFSearch")[0]

            # If opened file is a search
            if import_path.endswith(".FFSearch"):
                FF_Search.LoadSearch.open_file(import_path, self.Root_Window)
                # Quit function
                return

        # Opening file, throws error if no files was selected
        try:
            with open(import_path, "rb") as export_file:
                filters = load(fp=export_file)

        except FileNotFoundError:
            logging.warning(f"File not found: {import_path}")
            return

        # Debug
        logging.info("setting all filters to import...")

        # Basic
        self.edit_name.setText(filters["name"])
        self.edit_name_contains.setText(filters["name_contains"])
        self.combobox_file_types.check_items(filters["file_types"])
        self.edit_directory.setText(filters["directory"])

        # Properties
        self.edit_file_contains.setText(filters["file_contains"])

        self.m_date_from_drop_down.setDate(QDate.fromString(filters["dates"]["m_date_from"], Qt.DateFormat.ISODate))
        self.c_date_from_drop_down.setDate(QDate.fromString(filters["dates"]["c_date_from"], Qt.DateFormat.ISODate))
        self.m_date_to_drop_down.setDate(QDate.fromString(filters["dates"]["m_date_to"], Qt.DateFormat.ISODate))
        self.c_date_to_drop_down.setDate(QDate.fromString(filters["dates"]["c_date_to"], Qt.DateFormat.ISODate))

        self.edit_size_min.setText(filters["size"]["min"])
        self.edit_size_max.setText(filters["size"]["max"])

        # Advanced
        self.edit_file_extension.setText(filters["file_extension"])
        self.rb_library_yes.setChecked(filters["hidden_files"])
        self.combobox_search_for.setCurrentIndex(filters["files_folders"])

        # Sorting
        self.combobox_sorting.setCurrentIndex(filters["sorting"])
        self.rb_library_yes.setChecked(filters["reverse_sorting"])

        # Debug
        logging.info("Imported all filters\n")

    # Exporting all filters in to a FFFilter file
    def export_filters(self):
        # Debug
        logging.info("Request location for export")
        export_path = QFileDialog.getSaveFileName(parent=self.Root_Window,
                                                  dir=FF_Files.USER_FOLDER,
                                                  caption="Export File Find Search",
                                                  filter="File Find Filter Preset (*.FFFilter);;"
                                                         "JSON (JavaScript Object Notation) (*.json)")[0]

        # Debug
        logging.info(f"Exporting all filters to {export_path}...")

        # Directory to save filter settings
        filters = {"name": self.edit_name.text(),
                   "name_contains": self.edit_name_contains.text(),
                   "file_types": self.combobox_file_types.all_checked_items(),
                   "directory": self.edit_directory.text(),

                   "file_contains": self.edit_file_contains.text(),
                   "dates": {"m_date_from": self.m_date_from_drop_down.date().toString(Qt.DateFormat.ISODate),
                             "c_date_from": self.c_date_from_drop_down.date().toString(Qt.DateFormat.ISODate),
                             "m_date_to": self.m_date_to_drop_down.date().toString(Qt.DateFormat.ISODate),
                             "c_date_to": self.c_date_to_drop_down.date().toString(Qt.DateFormat.ISODate)},
                   "size": {"min": self.edit_size_min.text(),
                            "max": self.edit_size_max.text()},

                   "file_extension": self.edit_file_extension.text(),
                   "hidden_files": self.rb_library_yes.isChecked(),
                   "files_folders": self.combobox_search_for.currentIndex(),

                   "sorting": self.combobox_sorting.currentIndex(),
                   "reverse_sorting": self.rb_library_yes.isChecked()}

        # Try opening the file, crashes if user pressed "Cancel"
        try:
            with open(export_path, "w") as export_file:
                dump(obj=filters, fp=export_file)
        except FileNotFoundError:
            logging.warning(f"File not found: {export_path}")
        else:
            # Debug
            logging.info("Exported all filters\n")

    # Setting up the menu bar
    def menu_bar(self, shell_cmd, app: QApplication):

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
        export_filter_action = QAction("&Save Filter as Filter Preset", self.Root_Window)
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

        # Generate Terminal Command
        cmd_action = QAction("&Generate Terminal command", self.Root_Window)
        cmd_action.triggered.connect(shell_cmd)
        cmd_action.setShortcut("Ctrl+G")
        tools_menu.addAction(cmd_action)

        # Reset filter
        reset_action = QAction("&Reset all filters", self.Root_Window)
        reset_action.triggered.connect(self.reset_filters)
        reset_action.setShortcut("Ctrl+R")
        tools_menu.addAction(reset_action)

        # About File Find
        about_action = QAction("&About File Find", self.Root_Window)
        about_action.triggered.connect(lambda: FF_Help_UI.HelpWindow(self.Root_Window))
        help_menu.addAction(about_action)

        # Settings
        settings_action = QAction("&Settings", self.Root_Window)
        settings_action.triggered.connect(lambda: FF_Settings.SettingsWindow(self.Root_Window))
        settings_action.setShortcut("Ctrl+,")
        help_menu.addAction(settings_action)

        # Help
        help_action = QAction("&File Find Settings", self.Root_Window)
        help_action.triggered.connect(lambda: FF_Help_UI.HelpWindow(self.Root_Window))
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_menu.addAction(help_action)

        # Show File Find window
        reopen_action = QAction("&Show File Find Window", self.Root_Window)
        reopen_action.setShortcut("Ctrl+D")
        reopen_action.triggered.connect(self.Root_Window.show)
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

        # Search and delete cache for selected folder action
        search_without_cache_action = QAction("Search and delete cache for selected folder", self.Root_Window)
        search_without_cache_action.setShortcut("Ctrl+Shift+F")
        search_without_cache_action.triggered.connect(self.delete_cache_and_search)
        edit_menu.addAction(search_without_cache_action)

        # Menu-bar icon
        logging.debug("Constructing Menu-bar icon...")

        # Menu for menu_bar_icon_menu
        global menu_bar_icon_menu
        menu_bar_icon_menu = QMenu(self.Root_Window)

        # Add this icon to the menu bar
        global menu_bar_icon
        menu_bar_icon = QSystemTrayIcon(self.Root_Window)
        # Icon
        menu_bar_icon_icon = QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Menubar_icon_small.png"))
        # Make it automatically turn dark if background is light and the other way around
        menu_bar_icon_icon.setIsMask(True)
        menu_bar_icon.setIcon(menu_bar_icon_icon)

        # File Find Title
        ff_title = QAction("&File Find", self.Root_Window)
        ff_title.setDisabled(True)

        # Switch Tabs
        # Basic
        switch_tab_basic = QAction("Switch to tab Basic", self.Root_Window)
        switch_tab_basic.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(0))
        switch_tab_basic.setShortcut("Ctrl+1")
        # File Content
        switch_tab_file_content = QAction("Switch to tab File Content", self.Root_Window)
        switch_tab_file_content.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(1))
        switch_tab_file_content.setShortcut("Ctrl+2")
        # Advanced
        switch_tab_advanced = QAction("Switch to tab Advanced", self.Root_Window)
        switch_tab_advanced.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(2))
        switch_tab_advanced.setShortcut("Ctrl+3")
        # Sorting
        switch_tab_sorting = QAction("Switch to tab Sorting", self.Root_Window)
        switch_tab_sorting.triggered.connect(lambda: self.tabbed_widget.setCurrentIndex(3))
        switch_tab_sorting.setShortcut("Ctrl+4")
        # Add options to menu
        tabs_menu.addActions([switch_tab_basic, switch_tab_file_content, switch_tab_advanced, switch_tab_sorting])

        # Search Status Menu
        global search_status_menu
        search_status_menu = QMenu("&Searches:", self.Root_Window)
        search_status_menu.setDisabled(True)

        # Quit File Find
        quit_action = QAction("&Quit File Find", self.Root_Window)
        quit_action.triggered.connect(app.quit)

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

        # Display the Icon
        menu_bar_icon.setContextMenu(menu_bar_icon_menu)
        menu_bar_icon.show()

        return menu_bar_icon

    # Generic Label input
    @staticmethod
    def generic_tooltip(name, description, example_in, example_out) -> str:
        tooltip = f"{name}:\n{description}\n\nExample Input: {example_in}\nExample Output: {example_out}"
        return tooltip

    # Updating Actives Searches Label
    @staticmethod
    def update_search_status_label():
        # Debug
        logging.debug(f"Updating search status label, active searches: {FF_Search.ACTIVE_SEARCH_THREADS}")
        # If there are no active searches
        if FF_Search.ACTIVE_SEARCH_THREADS == 0:
            search_status_label.setText("Inactive")
            search_status_label.setStyleSheet("color: green;")
            search_status_label.adjustSize()

        # If there are ongoing searches updating label
        else:
            search_status_label.setText(f"Searching...({FF_Search.ACTIVE_SEARCH_THREADS})")
            search_status_label.setStyleSheet("color: red;")
            search_status_label.adjustSize()

    # Search without using the cache
    def delete_cache_and_search(self):
        logging.info("Deleting cache and search..")
        # Delete cache File
        cache_file_name = self.edit_directory.text().replace("/", "-")
        try:
            os.remove(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, f"{cache_file_name}.FFCache"))
            logging.info("Deleted cache successfully")
        except FileNotFoundError:
            logging.debug("Cache file doesn't exist")
        # Search
        self.search_entry()


class SearchUpdate:
    def __init__(self, stopping_search, path: str):
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

        # Setup stop search (doesn't work)
        self.stop_search: QAction = QAction("Stop")
        self.stop_search.triggered.connect(stopping_search)

        # Setup
        search_status_menu.addSeparator()
        search_status_menu.addAction(self.search_path)
        search_status_menu.addAction(self.search_status)
        # search_status_menu.addAction(self.stop_search)

    def update(self, text: str):
        self.search_status.setText(text)


global menu_bar_icon_menu, search_status_menu, menu_bar_icon, search_status_label
