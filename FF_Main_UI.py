# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This File contains the code for the main window

# Imports
import logging
import os
from sys import exit
from pyperclip import copy
from pickle import load, dump

# PyQt6 Gui Imports
from PyQt6.QtCore import QSize, QRect, Qt
from PyQt6.QtGui import QFont, QDoubleValidator, QIcon, QAction, QKeySequence, QFileSystemModel
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QRadioButton, QFileDialog, \
    QLineEdit, QButtonGroup, QDateEdit, QFrame, QComboBox, QMenuBar, QSystemTrayIcon, QMenu, QCompleter

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Help_UI
import FF_Search


class Main_Window:
    def __init__(self):
        # Debug
        logging.info("Launching UI...")
        logging.debug("Setting up self.Root_Window...")

        # Main Window
        # Create the window
        self.Root_Window = QWidget()
        # Set the Title of the Window
        self.Root_Window.setWindowTitle("File Find")
        # Set the Size of the Window and make it not resizable
        self.Root_Window.setFixedHeight(445)
        self.Root_Window.setFixedWidth(800)
        # Display the Window
        self.Root_Window.show()

        # File Find Label
        # Define the Label
        main_label = QLabel("File Find", parent=self.Root_Window)
        # Change Font
        main_label_font = QFont("Futura", 50)
        main_label_font.setBold(True)
        main_label.setFont(main_label_font)
        # Display the Label
        main_label.move(0, 0)
        main_label.show()

        # Labels
        logging.debug("Setting up Labels...")
        # Create a Label for every Filter with the Function, defined above
        # -----Basic Search-----
        # Frame and Label
        sorting_frame_label = self.generate_small_filter_label("Basic Search")
        sorting_frame_label.move(5, 70)
        basic_search_frame = QFrame(self.Root_Window)
        basic_search_frame.setGeometry(QRect(5, 90, 385, 170))
        basic_search_frame.setFrameShape(QFrame.Shape.StyledPanel)
        basic_search_frame.show()

        # Creating the Labels with tooltips
        l1 = self.generate_large_filter_label("Name:",
                                              self.generic_tooltip("Name",
                                                                   "Input needs to match the Name of a File exactly,"
                                                                   "\nignoring case",
                                                                   "Example.txt",
                                                                   os.path.join(FF_Files.USER_FOLDER, "example.txt")))
        l1.move(10, 100)

        l2 = self.generate_large_filter_label("Name contains:", self.generic_tooltip("Name contains",
                                                                                     "Input needs to be in the Name "
                                                                                     "of a File,"
                                                                                     "\nignoring case",
                                                                                     "file",
                                                                                     os.path.join(FF_Files.USER_FOLDER,
                                                                                                  "my-file.pdf")))
        l2.move(10, 140)

        l3 = self.generate_large_filter_label("File extension:", self.generic_tooltip("File extension",
                                                                                      "Input needs to match the file "
                                                                                      "extension (file type),"
                                                                                      "\nignoring case",
                                                                                      "txt",
                                                                                      os.path.join(FF_Files.USER_FOLDER,
                                                                                                   "example.txt")))
        l3.move(10, 180)

        l4 = self.generate_large_filter_label("Directory:", self.generic_tooltip("Directory",
                                                                                 "The Directory to search in",
                                                                                 os.path.join(FF_Files.USER_FOLDER,
                                                                                              "Downloads"),
                                                                                 os.path.join(FF_Files.USER_FOLDER,
                                                                                              "Downloads",
                                                                                              "example.pdf")))
        l4.move(10, 220)

        # -----Advanced Search-----
        # Frame and Label
        sorting_frame_label = self.generate_small_filter_label("Advanced Search")
        sorting_frame_label.move(395, 70)
        advanced_search_frame = QFrame(self.Root_Window)
        advanced_search_frame.setGeometry(QRect(395, 90, 400, 290))
        advanced_search_frame.setFrameShape(QFrame.Shape.StyledPanel)
        advanced_search_frame.show()

        l5 = self.generate_large_filter_label("File contains:", self.generic_tooltip("File contains:",
                                                                                     "Allows you to search in files."
                                                                                     " Looks if input is in a file.\n"
                                                                                     "This can take really long and"
                                                                                     " take up much memory",
                                                                                     "This is an example file!",
                                                                                     os.path.join(FF_Files.USER_FOLDER,
                                                                                                  "example.txt")))
        l5.move(400, 100)
        l6 = self.generate_large_filter_label("Wildcards:", self.generic_tooltip("Wildcards",
                                                                                 "Unix shell-style wildcards,"
                                                                                 "\nwhich are not the same as regular "
                                                                                 "expressions.\nFor documentation see: "
                                                                                 "https://docs.python.org/library"
                                                                                 "/fnmatch",
                                                                                 "exa*",
                                                                                 os.path.join(FF_Files.USER_FOLDER,
                                                                                              "example.txt")))
        l6.move(400, 140)

        l7 = self.generate_large_filter_label("File size(MB):     min:", self.generic_tooltip("File size",
                                                                                              "Input specifies "
                                                                                              "file size in "
                                                                                              "Mega Bytes (MB)\nin a "
                                                                                              "range (from min to "
                                                                                              "max)",
                                                                                              "min: 10 max: 10.3",
                                                                                              os.path.join(
                                                                                                  FF_Files.USER_FOLDER,
                                                                                                  "example.txt "
                                                                                                  "(with a size of "
                                                                                                  "10.2 MB)")))
        l7.move(400, 180)
        l7_2 = self.generate_large_filter_label("max:")
        l7_2.move(680, 180)

        l8 = self.generate_large_filter_label("Date created:", self.generic_tooltip("Date created",
                                                                                    "Specify a date range for the date "
                                                                                    "the file has been created,\n"
                                                                                    "leave at default to ignore",
                                                                                    "5.Jul.2020 -  10.Aug.2020",
                                                                                    os.path.join(FF_Files.USER_FOLDER,
                                                                                                 "example.txt "
                                                                                                 "(created at "
                                                                                                 "1.Aug.2020)")))
        l8.move(400, 220)
        l8_2 = self.generate_large_filter_label("-")
        l8_2.move(670, 220)

        l9 = self.generate_large_filter_label("Date modified:", self.generic_tooltip("Date modified",
                                                                                     "Specify a date range"
                                                                                     " for the date "
                                                                                     "the file has been modified,\n"
                                                                                     "leave at default to ignore",
                                                                                     "5.Jul.2020 -  10.Aug.2020",
                                                                                     os.path.join(FF_Files.USER_FOLDER,
                                                                                                  "example.txt "
                                                                                                  "(modified at "
                                                                                                  "1.Aug.2020)")))
        l9.move(400, 260)
        l9_2 = self.generate_large_filter_label("-")
        l9_2.move(670, 260)

        l10 = self.generate_large_filter_label("Search in system files:", self.generic_tooltip("Search in system files",
                                                                                               "Toggle to include "
                                                                                               "system files in the "
                                                                                               "search results\n"
                                                                                               "(files in the "
                                                                                               "Library folder)",
                                                                                               "Yes",
                                                                                               os.path.join(
                                                                                                   FF_Files.USER_FOLDER,
                                                                                                   "Library",
                                                                                                   "Caches",
                                                                                                   "example.txt")))
        l10.move(400, 300)
        l11 = self.generate_large_filter_label("Search for:", self.generic_tooltip("Search for",
                                                                                   "Toggle to only include "
                                                                                   "Folders or Files"
                                                                                   " in the search results",
                                                                                   "only Folders",
                                                                                   os.path.join(
                                                                                       FF_Files.USER_FOLDER,
                                                                                       "Downloads")))
        l11.move(400, 340)

        # -----Sorting-----
        # Frame and Label
        sorting_frame_label = self.generate_small_filter_label("Sorting")
        sorting_frame_label.move(5, 270)
        sorting_search_frame = QFrame(self.Root_Window)
        sorting_search_frame.setGeometry(QRect(5, 290, 385, 90))
        sorting_search_frame.setFrameShape(QFrame.Shape.StyledPanel)
        sorting_search_frame.show()

        l12 = self.generate_large_filter_label("Sort by:", self.generic_tooltip("Sort by",
                                                                                "The sorting method to sort the "
                                                                                "search results",
                                                                                "File Size",
                                                                                "Results sorted by file size"))
        l12.move(10, 300)
        l13 = self.generate_large_filter_label("Reverse results:", self.generic_tooltip("Reverse Results",
                                                                                        "Reverse the sorted "
                                                                                        "search results",
                                                                                        "Yes",
                                                                                        "Reversed search results"))
        l13.move(10, 340)

        # Label for the Terminal Command
        command_label2 = QLabel(self.Root_Window)
        command_label2.setFont(QFont("Arial", 20))
        command_label2.setMaximumWidth(300)

        # Title of searching indicator
        search_status_title_label = QLabel("Status:", self.Root_Window)
        search_status_title_label.setFont(QFont("Arial", 15))
        search_status_title_label.setToolTip("Search Indicator:\n"
                                             "Indicates if searching and shows the numbers of active searches.\n"
                                             "For more precise information click on the File Find logo in the menubar.")
        search_status_title_label.show()
        search_status_title_label.move(5, 420)

        # Label to indicate if searching
        global search_status_label
        search_status_label = QLabel("Idle", self.Root_Window)
        search_status_label.setFont(QFont("Arial", 15))
        search_status_label.setStyleSheet("color: green;")
        search_status_label.show()
        search_status_label.move(55, 420)

        # Entries
        logging.debug("Setting up Entries...")
        # Create an Entry for every Filter with the function self.generate_filter_entry()

        # Edit to display the Path
        directory_line_edit = self.generate_filter_entry()
        # Set text and tooltip to display the directory
        directory_line_edit.setText(os.getcwd())
        directory_line_edit.setToolTip(os.getcwd())

        # Auto complete paths
        def complete_path(path, check=True):

            # Adds all folders in path into paths
            def add_paths():
                paths = []
                for list_folder in os.listdir(path):
                    if os.path.isdir(list_folder):
                        paths.append(os.path.join(os.getcwd(), list_folder))

                # Set the saved list as Completer
                self.directory_line_edit_completer = QCompleter(paths, parent=self.Root_Window)
                directory_line_edit.setCompleter(self.directory_line_edit_completer)

                # Returns the list
                return paths

            # check
            if check:
                # Going through all paths to look if auto-completion should be loaded
                if path.endswith("/"):
                    self.auto_complete_paths = add_paths()
                    logging.debug("Changed QCompleter")
                    return
            # Skip check
            if not check:
                self.auto_complete_paths = add_paths()
                logging.debug("Changed QCompleter")
                return

        # Completing Paths
        self.directory_line_edit_completer = QCompleter(parent=self.Root_Window)
        self.directory_line_edit_completer.splitPath("/")
        directory_line_edit.setCompleter(self.directory_line_edit_completer)
        complete_path(os.getcwd(), check=False)

        # Validate Paths
        def validate_dir():
            # Debug
            logging.debug(f"Directory Path changed to: {directory_line_edit.text()}")

            if os.path.isdir(check_path := directory_line_edit.text()):

                # Changing Path
                logging.debug(f"Path: {check_path} valid")
                os.chdir(check_path)

                # Changing Status-Tip
                directory_line_edit.setStatusTip(check_path)

                # Change color
                l4.setStyleSheet("")

                # Updating Completions
                complete_path(check_path)

            else:

                # Debug
                logging.debug(f"Path: {check_path} invalid")

                # Change color
                l4.setStyleSheet("color: red;")

        directory_line_edit.textChanged.connect(validate_dir)

        # Resize and place on screen
        directory_line_edit.resize(200, 25)
        directory_line_edit.move(105, 220)

        # Name
        e1 = self.generate_filter_entry()
        e1.resize(230, 25)
        e1.move(150, 100)
        # In Name
        e2 = self.generate_filter_entry()
        e2.resize(230, 25)
        e2.move(150, 140)
        # File ending
        e3 = self.generate_filter_entry()
        e3.resize(230, 25)
        e3.move(150, 180)
        # File size min
        e4 = self.generate_filter_entry(True)
        e4.resize(60, 25)
        e4.move(600, 180)
        # File size max
        e5 = self.generate_filter_entry(True)
        e5.resize(60, 25)
        e5.move(730, 180)
        # Contains
        e6 = self.generate_filter_entry()
        e6.resize(270, 25)
        e6.move(520, 100)
        # fn match, Unix shell-style wildcards
        e7 = self.generate_filter_entry()
        e7.resize(270, 25)
        e7.move(520, 140)

        # Radio Button
        logging.debug("Setting up Radio Buttons...")
        # Search for Library Files
        # Group for Radio Buttons
        library_group = QButtonGroup(self.Root_Window)
        # Radio Button 1
        rb_library1 = self.create_radio_button(library_group, "Yes")
        # Move the Button
        rb_library1.move(680, 302)
        # Radio Button 2
        rb_library2 = self.create_radio_button(library_group, "No")
        # Move the Button
        rb_library2.move(740, 302)
        # Select the Button 2
        rb_library2.setChecked(True)

        # Reverse Sort
        # Group for Radio Buttons
        reverse_sort_group = QButtonGroup(self.Root_Window)
        # Radio Button 1
        rb_reverse_sort1 = self.create_radio_button(reverse_sort_group, "Yes")
        # Move the Button
        rb_reverse_sort1.move(260, 342)
        # Radio Button 2
        rb_reverse_sort2 = self.create_radio_button(reverse_sort_group, "No")
        # Move the Button
        rb_reverse_sort2.move(320, 342)
        # Select the Button
        rb_reverse_sort2.setChecked(True)

        # Drop Down Menus
        logging.debug("Setting up Combo Boxes...")

        # Sorting Menu
        # Defining
        combobox_sorting = QComboBox(self.Root_Window)
        # Adding Options
        combobox_sorting.addItems(["None", "File Size", "File Name", "Date Modified", "Date Created"])
        # Display
        combobox_sorting.show()
        combobox_sorting.move(240, 300)

        # Search for Files, Folders... Menu
        # Defining
        combobox_search_for = QComboBox(self.Root_Window)
        # Adding Options
        combobox_search_for.addItems(["Files and Folders",
                                      "only Files",
                                      "only Folders"])
        # Display
        combobox_search_for.show()
        combobox_search_for.move(620, 340)

        # Date-Time Entries
        logging.debug("Setting up Day Entries...")
        # Date Created
        c_date_from_drop_down = self.generate_day_entry()
        c_date_from_drop_down.move(558, 224)
        c_date_to_drop_down = self.generate_day_entry()
        c_date_to_drop_down.move(690, 224)

        # Date Modified
        m_date_from_drop_down = self.generate_day_entry()
        m_date_from_drop_down.move(558, 264)
        m_date_to_drop_down = self.generate_day_entry()
        m_date_to_drop_down.move(690, 264)

        # Push Buttons
        logging.debug("Setting up Push Buttons...")

        # Search from Button
        # Opens the File dialogue and changes the current working dir into the returned value
        def open_dialog():
            search_from = QFileDialog.getExistingDirectory(directory=os.getcwd())
            try:
                os.chdir(search_from)
                directory_line_edit.setText(search_from)
            except (FileNotFoundError, OSError):
                pass

        search_from_button = self.generate_edit_button(open_dialog)
        search_from_button.move(310, 220)

        # Print the given data
        def print_data():
            logging.info(f"\nFilters:\n"
                         f"Name: {e1.text()}\n"
                         f"In name: {e2.text()}\n"
                         f"File Ending: {e3.text()}\n"
                         f"Search from: {os.getcwd()}\n\n"
                         f"File size(MB): min:{e4.text()} max: {e5.text()}\n"
                         f"Date modified from: {m_date_from_drop_down.text()} to: {m_date_to_drop_down.text()}\n"
                         f"Date created from: {c_date_from_drop_down.text()} to: {c_date_to_drop_down.text()}\n"
                         f"Content: {e6.text()}\n"
                         f"Search for system files: {rb_library1.isChecked()}\n"
                         f"Search for: {combobox_search_for.currentText()}\n\n"
                         f"Sort results by: {combobox_sorting.currentText()}\n"
                         f"Reverse results: {rb_reverse_sort1.isChecked()}\n")

        # Start Search with args locally
        def search_entry():
            # Debug
            logging.debug("User clicked Find")

            # Print Input
            print_data()
            # Start Searching
            FF_Search.search(data_name=e1.text(),
                             data_in_name=e2.text(),
                             data_filetype=e3.text(),
                             data_file_size_min=e4.text(), data_file_size_max=e5.text(),
                             data_library=rb_library1.isChecked(),
                             data_search_from_valid=os.getcwd(),
                             data_search_from_unproofed=directory_line_edit.text(),
                             data_content=e6.text(),
                             data_search_for=combobox_search_for.currentText(),
                             data_edits_list=[c_date_from_drop_down, c_date_to_drop_down, m_date_from_drop_down,
                                              m_date_to_drop_down],
                             data_fn_match=e7.text(),
                             data_sort_by=combobox_sorting.currentText(),
                             data_reverse_sort=rb_reverse_sort1.isChecked(),
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
                FF_Additional_UI.msg.show_info_messagebox("Successful copied!",
                                                          f"Successful copied Command:\n{shell_command} !",
                                                          self.Root_Window)

            # Generate a shell command
            shell_command = str(FF_Search.generate_terminal_command(e1.text(), e2.text(), e3.text(), e5.text()))

            # Label, saying command
            command_label = QLabel(self.Root_Window)
            command_label.setText("Command:")
            command_label.setToolTip("Terminal command:\nYou can paste this command into the Terminal app"
                                     " to search with the \"find\" tool")
            command_label.setFont(QFont("Arial", 20))
            command_label.show()
            command_label.move(10, 390)

            # Label, displaying the command
            command_label2.setText(f"{shell_command} {'':100}")
            command_label2.setToolTip(shell_command)
            command_label2.setStyleSheet("background-color: blue;color: white;")
            command_label2.adjustSize()
            command_label2.move(120, 390)
            command_label2.show()

            # Copy Command Button
            command_copy_button = QPushButton(self.Root_Window)
            # Change the Text
            command_copy_button.setText("Copy")
            # Change the click event
            command_copy_button.clicked.connect(copy_command)
            # Display the Button at the correct position
            command_copy_button.show()
            command_copy_button.move(425, 385)

        # Large Buttons
        # Search button with image, to start searching

        # Menu when Right-clicking
        context_menu = QMenu(self.Root_Window)

        # Open Search Action
        action_open_search = QAction('Open Search', self.Root_Window)
        action_open_search.triggered.connect(lambda: FF_Search.load_search(self.Root_Window))
        context_menu.addAction(action_open_search)

        # Shell Command Action
        action_terminal = QAction('Generate Terminal Command', self.Root_Window)
        action_terminal.triggered.connect(generate_terminal_command)
        context_menu.addAction(action_terminal)

        # Defining Button
        search_button = self.generate_large_button("Find", search_entry, 25)

        # Context Menu
        search_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        search_button.customContextMenuRequested.connect(
            lambda point: context_menu.exec(search_button.mapToGlobal(point)))
        # Icon
        search_button.setIcon(QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Find_button_img_small.png")))
        search_button.setIconSize(QSize(25, 25))
        # Place
        search_button.resize(100, 50)
        search_button.move(690, 390)

        # Help Button, that calls FF_Additional_UI.Help_Window
        help_button = self.generate_large_button(" About", lambda: FF_Help_UI.Help_Window(self.Root_Window), 25)
        # Color
        help_button.setStyleSheet("color: blue;")
        # Icon
        help_button.setIcon(QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Info_button_img_small.png")))
        help_button.setIconSize(QSize(25, 25))
        # Place
        help_button.resize(120, 50)
        help_button.move(670, 10)

        # Set up the menu bar
        logging.info("Setting up Menu Bar...")
        self.setup_menu_bar(generate_terminal_command)

        # Showing PopUps
        self.popups()

        # Debug
        logging.info("Finished Setting up Main UI\n")

    # Functions to automate Labels
    def generate_large_filter_label(self, name: str, tooltip: str = ""):
        # Define the Label
        label = QLabel(name, parent=self.Root_Window)
        # Change Font
        label.setFont(QFont("Arial", 20))
        # Hover tool tip
        label.setToolTip(f"{tooltip}")
        label.setToolTipDuration(-1)
        # Display the Label
        label.show()
        # Return the Label to move it
        return label

    def generate_small_filter_label(self, name: str):
        # Define the Label
        label = QLabel(name, parent=self.Root_Window)
        # Change Font
        label.setFont(QFont("Arial", 15))
        # Display the Label
        label.show()
        # Return the Label to move it
        return label

    # Function to automate Entry creation
    def generate_filter_entry(self, only_int: bool = False):
        # Define the Entry
        entry = QLineEdit(self.Root_Window)
        # Set the Length
        entry.resize(230, 20)
        # If only_int true, configure the label
        if only_int:
            entry.setValidator(QDoubleValidator(self.Root_Window))
        # Display the Entry
        entry.show()
        # Return the Label to place it
        return entry

    # Function for automating radio buttons
    def create_radio_button(self, group, text):
        # Create Radio Button
        rb = QRadioButton(self.Root_Window)
        # Set the Text
        rb.setText(text)
        # Add the Button to the Group
        group.addButton(rb)
        # Display the Button
        rb.show()
        # Return the Button
        return rb

    # Function for automating day edits
    def generate_day_entry(self):
        # Define dt_entry
        dt_entry = QDateEdit(self.Root_Window)
        # Change dd.mm.yy to dd.MM.yyyy (e.g. 13.1.01 = 13.Jan.2001)
        dt_entry.setDisplayFormat("dd.MMM.yyyy")
        # Display
        dt_entry.show()
        # Return dt entry to move it
        return dt_entry

    # Functions to automate Buttons
    def generate_edit_button(self, command):
        # Generate the Button
        button = QPushButton(self.Root_Window)
        # Change the Text
        button.setText("Select")
        # Set the command
        button.clicked.connect(command)
        # Display the Button
        button.show()
        # Return the value of the Button, to move the Button
        return button

    def generate_large_button(self, text, command, font_size):
        # Define the Button
        button = QPushButton(self.Root_Window)
        # Set the Text
        button.setText(text)
        # Set the Font
        Font = QFont("Arial", font_size)
        Font.setBold(True)
        button.setFont(Font)
        # Set the Command
        button.clicked.connect(command)
        # Display the Button
        button.show()
        # Return the Button
        return button

    # Setting up the menu bar
    def setup_menu_bar(self, shell_cmd):

        # Menu Bar
        menu_bar = QMenuBar(self.Root_Window)
        edit_menu = menu_bar.addMenu("&Edit")
        file_menu = menu_bar.addMenu("&File")
        tools_menu = menu_bar.addMenu("&Tools")
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Load Saved Search
        load_search_action = QAction("&Open Search", self.Root_Window)
        load_search_action.triggered.connect(lambda: FF_Search.load_search(self.Root_Window))
        load_search_action.setShortcut("Ctrl+O")
        file_menu.addAction(load_search_action)

        # Clear Cache
        cache_action = QAction("&Clear Cache", self.Root_Window)
        cache_action.triggered.connect(lambda: FF_Files.remove_cache(True, self.Root_Window))
        cache_action.setShortcut("Ctrl+N")
        tools_menu.addAction(cache_action)

        # Generate Terminal Command
        cmd_action = QAction("&Generate Terminal command", self.Root_Window)
        cmd_action.triggered.connect(shell_cmd)
        cmd_action.setShortcut("Ctrl+G")
        tools_menu.addAction(cmd_action)

        # About File Find
        about_action = QAction("&About File Find", self.Root_Window)
        about_action.triggered.connect(lambda: FF_Help_UI.Help_Window(self.Root_Window))
        about_action.setShortcut("Ctrl+,")
        help_menu.addAction(about_action)

        # Help
        help_action = QAction("&File Find Help and Settings", self.Root_Window)
        help_action.triggered.connect(lambda: FF_Help_UI.Help_Window(self.Root_Window))
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_menu.addAction(help_action)

        # Show File Find window
        reopen_action = QAction("&Show File Find Window", self.Root_Window)
        reopen_action.setShortcut("Ctrl+S")
        reopen_action.triggered.connect(self.Root_Window.show)
        window_menu.addAction(reopen_action)

        # Hide File Find window
        hide_action = QAction("&Hide File Find Window", self.Root_Window)
        hide_action.setShortcut("Ctrl+W")
        hide_action.triggered.connect(self.Root_Window.hide)
        window_menu.addAction(hide_action)

        # Search Action
        find_action = QAction("&Search", self.Root_Window)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.search_entry)
        edit_menu.addAction(find_action)

        # Menubar icon
        logging.debug("Constructing Menubar icon...")

        # Menu for menubar_icon_menu
        global menubar_icon_menu
        menubar_icon_menu = QMenu(self.Root_Window)

        # Add this icon to the menu bar
        global menubar_icon
        menubar_icon = QSystemTrayIcon(self.Root_Window)
        menubar_icon.setIcon(QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Menubar_icon_small.png")))

        # File Find Title
        ff_title = QAction("&File Find", self.Root_Window)
        ff_title.setDisabled(True)

        # Search Status Menu
        global search_status_menu
        search_status_menu = QMenu("&Searches:", self.Root_Window)
        search_status_menu.setDisabled(True)

        # Quit File Find
        quit_action = QAction("&Quit File Find", self.Root_Window)
        quit_action.triggered.connect(lambda: exit(0))
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)

        # Constructing menubar_icon_menu
        menubar_icon_menu.addAction(ff_title)
        menubar_icon_menu.addSeparator()
        menubar_icon_menu.addMenu(search_status_menu)
        menubar_icon_menu.addMenu(search_status_menu)
        menubar_icon_menu.addSeparator()
        menubar_icon_menu.addAction(reopen_action)
        menubar_icon_menu.addSeparator()
        menubar_icon_menu.addAction(about_action)
        menubar_icon_menu.addAction(quit_action)

        # Display the Icon
        menubar_icon.setContextMenu(menubar_icon_menu)
        menubar_icon.show()

        return menubar_icon

    # Displaying Welcome Popups
    def popups(self):
        # Debug
        logging.debug("Testing for PopUps...")

        # Loading already displayed Popups with pickle
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "rb") as SettingsFile:
            settings = load(SettingsFile)
            popup_dict = settings["popup"]

        if popup_dict["FF_welcome"]:
            # Debug
            logging.info("Showing Welcomes PopUp...")

            # Showing welcome messages
            FF_Additional_UI.msg.show_info_messagebox("Welcome to File Find",
                                                      "Welcome to File Find!\n\nThanks for downloading File Find!\n"
                                                      "File Find is an open-source macOS utility,"
                                                      " that makes it easy to find files.\n\n"
                                                      "To search fill in the filters you need and leave those"
                                                      " you don't need empty.\n\n\n"
                                                      "File Find version: "
                                                      f"{FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]",
                                                      self.Root_Window)
            FF_Additional_UI.msg.show_info_messagebox("Welcome to File Find",
                                                      "Welcome to File Find!\n\nSearch with the Find button.\n\n"
                                                      "You can find all Settings in the About section!\n\n"
                                                      "Press on the File Find icon in "
                                                      "the Menubar to check the Search Status!",
                                                      self.Root_Window)
            FF_Additional_UI.msg.show_info_messagebox("Welcome to File Find",
                                                      "Welcome to File Find!\n\n"
                                                      "If you want to contribute, look at the source code, "
                                                      "found a bug or have a feature-request\n\n"
                                                      "Go to: https://gitlab.com/Pixel-Mqster/File-Find\n\n\n"
                                                      "I hope you find all of your files!",
                                                      self.Root_Window)
            # Setting PopUp File
            popup_dict["FF_welcome"] = False
            settings["popup"] = popup_dict
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "wb") as SettingsFile:
                dump(settings, SettingsFile)

        # Version Welcome PopUps
        elif popup_dict["FF_ver_welcome"]:
            # Debug
            logging.info("Showing Version Welcomes PopUp...")

            # Showing welcome messages
            FF_Additional_UI.msg.show_info_messagebox("Thanks For Upgrading File Find!",
                                                      f"Thanks For Upgrading File Find!\n\n"
                                                      f"File Find is an open-source macOS Utility. \n\n"
                                                      f"Get Releases at: "
                                                      f"https://gitlab.com/Pixel-Mqster/File-Find/releases"
                                                      f"\n\n\n"
                                                      "File Find version: "
                                                      f"{FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]",
                                                      self.Root_Window)
            # Setting PopUp File
            popup_dict["FF_ver_welcome"] = False
            settings["popup"] = popup_dict
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "wb") as SettingsFile:
                dump(settings, SettingsFile)

    # Debug
    logging.info("Finished PopUps")

    # Generic Label input
    @staticmethod
    def generic_tooltip(name, description, example_in, example_out) -> str:
        tooltip = f"{name}:\n{description}\n\nExample Input: {example_in}\nExample Output: {example_out}"
        return tooltip

    # Updating Actives Searches Label
    @staticmethod
    def update_search_status_label():
        # If there are now active searches
        if FF_Search.ACTIVE_SEARCH_THREADS == 0:
            search_status_label.setText("Idle")
            search_status_label.setStyleSheet("color: green;")
            search_status_label.adjustSize()

        # When there are Threads updating Label
        else:
            search_status_label.setText(f"Searching...({FF_Search.ACTIVE_SEARCH_THREADS})")
            search_status_label.setStyleSheet("color: red;")
            search_status_label.adjustSize()


class search_update:
    def __init__(self, stopping_search, path: str):
        # Updating Label
        Main_Window.update_search_status_label()

        # Assigning local values
        self.menubar_icon_menu: QMenu = menubar_icon_menu
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


global menubar_icon_menu, search_status_menu, menubar_icon, search_status_label
