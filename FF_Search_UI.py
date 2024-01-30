# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the search-results window

# Imports
import hashlib
import logging
import os
from json import dump, load
from threading import Thread
from time import perf_counter, ctime, time
import gc

# PySide6 Gui Imports
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QAction, QColor, QKeySequence
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, \
    QListWidget, QMenuBar, QMenu, QWidget, QGridLayout, QHBoxLayout

# Projects Libraries
import FF_Additional_UI
import FF_Compare
import FF_Files
import FF_Help_UI
import FF_Main_UI


class SearchWindow:
    def __init__(self, time_total, time_searching, time_indexing, time_sorting, matched_list, search_path, parent):
        # Debug
        logging.info("Setting up Search UI...")

        # Setting search_path to a local variable
        self.search_path = search_path

        # Saves Time
        time_before_building = perf_counter()

        # Window setup
        # Define the window
        self.Search_Results_Window = QMainWindow(parent)
        # Set the Title of the Window
        self.Search_Results_Window.setWindowTitle(f"File Find Search Results | {FF_Files.display_path(search_path)}")
        # Set the start size of the Window, because it's resizable
        self.BASE_WIDTH = 700
        self.BASE_HEIGHT = 700
        self.Search_Results_Window.setBaseSize(self.BASE_WIDTH, self.BASE_HEIGHT)
        # Display the Window
        self.Search_Results_Window.show()

        # Adding Layouts
        # Main Layout
        # Create a central widget
        self.Central_Widget = QWidget(self.Search_Results_Window)
        self.Search_Results_Window.setCentralWidget(self.Central_Widget)
        # Create the main Layout
        self.Search_Results_Layout = QGridLayout(self.Central_Widget)
        self.Search_Results_Layout.setContentsMargins(20, 20, 20, 20)
        self.Search_Results_Layout.setVerticalSpacing(20)

        # Bottom Layout
        self.Bottom_Layout = QHBoxLayout(self.Search_Results_Window)
        self.Bottom_Layout.setContentsMargins(0, 0, 0, 0)
        # Add to main Layout
        self.Search_Results_Layout.addLayout(self.Bottom_Layout, 10, 0, 1, 4)
        # DON'T TRY TO USE LAYOUTS! YOU ARE JUST GOING TO END UP WASTING YOUR TIME!
        # If used File Find crashes with a 'Memory Error' and no further information.
        # I wasted several hours, trying to fix this.
        # Btw, You can fix it with disabling Pythons garbage collection.

        # Seconds needed Label
        seconds_text = QLabel(self.Search_Results_Window)
        # Setting a Font
        small_text_font = QFont("Arial", 17)
        small_text_font.setBold(True)
        seconds_text.setFont(small_text_font)
        # Displaying
        self.Search_Results_Layout.addWidget(seconds_text, 0, 0)

        # Files found label
        objects_text = QLabel(self.Search_Results_Window)
        objects_text.setText(f"Files found: {len(matched_list)}")
        objects_text.setFont(small_text_font)
        # Displaying
        self.Search_Results_Layout.addWidget(objects_text, 0, 2)

        # Listbox
        self.result_listbox = QListWidget(self.Search_Results_Window)
        # Place
        self.Search_Results_Layout.addWidget(self.result_listbox, 1, 0, 9, 4)
        # Display the Listbox
        self.result_listbox.show()

        # Show more time info's
        def show_time_stats():
            # Debug
            logging.debug("Displaying time stats.")

            # Getting the creation time of the cache file
            cache_created_time = ctime(
                os.stat(
                    os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                 search_path.replace("/", "-") + ".FFCache")).st_birthtime)
            cache_modified_time = ctime(
                os.path.getmtime(
                    os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, search_path.replace("/", "-") + ".FFCache")))
            search_opened_time = ctime(time())

            # Displaying infobox with time info
            FF_Additional_UI.PopUps.show_info_messagebox(
                "Time Stats",
                f"Time needed:\nScanning: {round(time_searching, 3)}\nIndexing:"
                f" {round(time_indexing, 3)}\nSorting:"
                f" {round(time_sorting, 3)}\nCreating UI: "
                f"{round(time_building, 3)}\n---------\nTotal: "
                f"{round(time_total + time_building, 3)}\n\n\n"
                f""
                f"Timestamps:\n"
                f"Cache created: {cache_created_time}\n"
                f"Cache updated: {cache_modified_time}\n"
                f"Search opened: {search_opened_time}",
                self.Search_Results_Window)

        # Reloads File, check all collected files, if they still exist
        def reload_files():
            try:
                logging.info("Reload...")
                time_before_reload = perf_counter()
                removed_list = []
                # TODO: os.path.exists() sometimes return false positives
                for matched_file in matched_list:
                    if os.path.exists(matched_file):
                        continue
                    else:
                        # Remove file from widget if it doesn't exist
                        self.result_listbox.takeItem(matched_list.index(matched_file))
                        matched_list.remove(matched_file)
                        logging.debug(f"File Does Not exist: {matched_file}")
                        # Adding file to removed_list to later remove it from cache
                        removed_list.append(matched_file)

                # Loading cache to update it
                with open(
                        os.path.join(
                            FF_Files.CACHED_SEARCHES_FOLDER,
                            search_path.replace("/", "-") + ".FFCache")) as search_file:

                    cached_file: dict[list, dict, dict] = load(search_file)

                # Removing all deleted files from cache
                for removed_file in removed_list:
                    try:
                        cached_file["found_path_set"].remove(removed_file)
                    except (KeyError, ValueError):
                        # File was already removed from cache
                        pass

                with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, search_path.replace("/", "-") + ".FFCache"),
                          "w") as search_file:
                    dump(cached_file, search_file)
                logging.info(f"Reloaded found Files and removed {len(removed_list)} in"
                             f" {round(perf_counter() - time_before_reload, 3)} sec.")
                FF_Additional_UI.PopUps.show_info_messagebox(
                    "Reloaded!",
                    f"Reloaded found Files and removed {len(removed_list)}"
                    f" in {round(perf_counter() - time_before_reload, 3)} sec.",
                    self.Search_Results_Window)
                # UI
                objects_text.setText(f"Files found: {len(matched_list)}")
                objects_text.adjustSize()

                # Delete variables out of memory
                del cached_file, removed_list
            except FileNotFoundError:
                FF_Additional_UI.PopUps.show_info_messagebox("Cache File not Found!",
                                                             "Cache File was deleted, couldn't Update Cache!",
                                                             self.Search_Results_Window)

        # Save Search
        def save_search():
            save_dialog = QFileDialog.getSaveFileName(self.Search_Results_Window, "Export File Find Search",
                                                      FF_Files.SAVED_SEARCHES_FOLDER,
                                                      "File Find Search (*.FFSearch);;Plain Text File (*.txt)")
            save_file = save_dialog[0]
            if save_file.endswith(".txt") and not os.path.exists(save_file):
                with open(save_file, "w") as export_file:
                    for save_file in matched_list:
                        export_file.write(save_file + "\n")
            elif save_file.endswith(".FFSearch") and not os.path.exists(save_file):
                with open(save_file, "w") as export_file:
                    dump(matched_list, export_file)

        # Buttons
        # Functions to automate Button
        def generate_button(text, command, icon=None):
            # Define the Button
            button = QPushButton(self.Search_Results_Window)
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
        move_file = generate_button("Move / Rename", self.move_file,
                                    icon=os.path.join(FF_Files.ASSETS_FOLDER, "Move_icon_small.png"))
        self.Bottom_Layout.addWidget(move_file)

        # Button to move the file to trash
        delete_file = generate_button("Move to Trash", self.delete_file,
                                      icon=os.path.join(FF_Files.ASSETS_FOLDER, "Trash_icon_small.png"))
        self.Bottom_Layout.addWidget(delete_file)

        # Button to open the file
        open_file = generate_button("Open", self.open_file,
                                    icon=os.path.join(FF_Files.ASSETS_FOLDER, "Open_icon_small.png"))
        self.Bottom_Layout.addWidget(open_file)

        # Button to show info about the file
        file_info_button = generate_button("Info", self.file_info,
                                           icon=os.path.join(FF_Files.ASSETS_FOLDER, "Info_button_img_small.png"))
        self.Bottom_Layout.addWidget(file_info_button)

        # Time stat Button
        show_time = generate_button(None, show_time_stats,
                                    icon=os.path.join(FF_Files.ASSETS_FOLDER, "Time_button_img_small.png"))
        # Resize
        show_time.setMaximumSize(50, 50)
        # Add to Layout
        self.Search_Results_Layout.addWidget(show_time, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        # More Options
        # Options Menu
        options_menu = QMenu(self.Search_Results_Window)

        # Reload Action
        options_menu_reload_action = options_menu.addAction("&Reload")
        options_menu_reload_action.triggered.connect(reload_files)
        # Save Action
        options_menu_save_action = options_menu.addAction("&Save Search")
        options_menu_save_action.triggered.connect(save_search)
        # Compare Action
        options_menu_compare_action = options_menu.addAction(
            "&Select a .FFSearch file and compare it to the opened Search...")
        options_menu_compare_action.triggered.connect(
            lambda: FF_Compare.CompareSearches(matched_list, search_path, self.Search_Results_Window))

        # More Options Button
        options_button = generate_button(
            # Displaying the menu at the right position,
            # using the .mapToParent function with the position of the window.
            None, lambda: options_menu.exec(options_button.mapToParent(self.Search_Results_Window.pos())),
            icon=os.path.join(FF_Files.ASSETS_FOLDER, "More_button_img_small.png"))
        # Icon size
        options_button.setIconSize(QSize(50, 50))
        # Resize
        options_button.setMaximumSize(50, 50)
        # Add to Layout
        self.Search_Results_Layout.addWidget(options_button, 0, 3)

        # Adding every object from matched_list to self.result_listbox
        logging.debug("Adding Files to Listbox...")
        self.result_listbox.addItems(matched_list)
        # Setting the row
        self.result_listbox.setCurrentRow(0)

        # On double-click
        self.result_listbox.itemDoubleClicked.connect(self.open_in_finder)

        # Update Seconds needed Label
        seconds_text.setText(f"Time needed: {round(time_total + (perf_counter() - time_before_building), 3)}")
        seconds_text.adjustSize()

        # Building Menubar
        self.menubar(save_search, reload_files, matched_list, search_path, parent)

        # Debug
        logging.info("Finished Setting up menubar")

        # Time building UI
        time_building = perf_counter() - time_before_building
        logging.info(f"\nSeconds needed:\nScanning: {time_searching}\nIndexing: {time_indexing}\nSorting: "
                     f"{time_sorting}\nBuilding UI: {time_building}\nTotal: {time_total + time_building}")

        # Push Notification
        FF_Main_UI.menubar_icon.showMessage("File Find - Search finished!", f"Your Search finished!\nin {search_path}",
                                            QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Find_button_img_small.png")),
                                            100000)
        # Updated Search indicator
        FF_Main_UI.MainWindow.update_search_status_label()

        logging.info("Finished Building Search-Results-UI!\n")

    def menubar(self, save_search, reload_files, matched_list, search_path, parent):
        logging.debug("Setting up menubar...", )

        # Menubar
        menu_bar = QMenuBar(self.Search_Results_Window)

        # Menus
        menu_bar.addMenu("&Edit")
        file_menu = menu_bar.addMenu("&File")
        tools_menu = menu_bar.addMenu("&Tools")
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Save Search
        save_search_action = QAction("&Save Search", self.Search_Results_Window)
        save_search_action.triggered.connect(save_search)
        save_search_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_search_action)

        # Clear Cache
        cache_action = QAction("&Clear Cache", self.Search_Results_Window)
        cache_action.triggered.connect(lambda: FF_Files.remove_cache(True, self.Search_Results_Window))
        cache_action.setShortcut("Ctrl+T")
        tools_menu.addAction(cache_action)

        # Reload and Remove Deleted Files
        reload_action = QAction("&Reload and Remove Deleted Files", self.Search_Results_Window)
        reload_action.triggered.connect(reload_files)
        reload_action.setShortcut("Ctrl+R")
        tools_menu.addAction(reload_action)

        # Separator
        tools_menu.addSeparator()

        # Open File Action
        open_action = QAction("&Open selected file", self.Search_Results_Window)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        tools_menu.addAction(open_action)

        # Open File in Terminal Action
        open_terminal_action = QAction("&Open selected file in Terminal", self.Search_Results_Window)
        open_terminal_action.triggered.connect(self.open_in_terminal)
        open_terminal_action.setShortcut("Ctrl+Alt+O")
        tools_menu.addAction(open_terminal_action)

        # Show File in Finder Action
        show_action = QAction("&Open selected file in Finder", self.Search_Results_Window)
        show_action.triggered.connect(self.open_in_finder)
        show_action.setShortcut("Ctrl+Shift+O")
        tools_menu.addAction(show_action)

        # Select an app to open the selected file
        open_in_app_action = QAction("&Select an app to open the selected file...", self.Search_Results_Window)
        open_in_app_action.triggered.connect(self.open_in_app)
        open_in_app_action.setShortcut("Alt+O")
        tools_menu.addAction(open_in_app_action)

        # Separator
        tools_menu.addSeparator()

        # Select an app to open the selected file
        delete_file_action = QAction("&Move selected file to trash", self.Search_Results_Window)
        delete_file_action.triggered.connect(self.delete_file)
        delete_file_action.setShortcut("Ctrl+Delete")
        tools_menu.addAction(delete_file_action)

        # Prompt the user to select a new location for the selected file
        move_file_action = QAction("&Move or Rename selected file", self.Search_Results_Window)
        move_file_action.triggered.connect(self.move_file)
        move_file_action.setShortcut("Ctrl+M")
        tools_menu.addAction(move_file_action)

        # Separator
        tools_menu.addSeparator()

        # File Info
        info_action = QAction("&Info for selected file", self.Search_Results_Window)
        info_action.triggered.connect(self.file_info)
        info_action.setShortcut("Ctrl+I")
        tools_menu.addAction(info_action)

        # View File Hashes
        hash_action = QAction("&Hashes for selected file", self.Search_Results_Window)
        hash_action.triggered.connect(self.view_hashes)
        hash_action.setShortcut("Ctrl+Shift+I")
        tools_menu.addAction(hash_action)

        # About File Find
        about_action = QAction("&About File Find", self.Search_Results_Window)
        about_action.triggered.connect(lambda: FF_Help_UI.HelpWindow(self.Search_Results_Window))
        help_menu.addAction(about_action)

        # Close Window
        close_action = QAction("&Close Window", self.Search_Results_Window)
        close_action.triggered.connect(self.Search_Results_Window.destroy)
        close_action.triggered.connect(gc.collect)
        close_action.setShortcut("Ctrl+W")
        window_menu.addAction(close_action)

        # Help
        help_action = QAction("&File Find Help And Settings", self.Search_Results_Window)
        help_action.triggered.connect(lambda: FF_Help_UI.HelpWindow(self.Search_Results_Window))
        help_menu.addAction(help_action)

        # Compare Search
        compare_action = QAction(
            "&Select a .FFSearch file and compare it to the opened Search...", self.Search_Results_Window)
        compare_action.triggered.connect(lambda: FF_Compare.CompareSearches(matched_list, search_path, parent))
        compare_action.setShortcut("Ctrl+N")
        # Separator for visual indent
        tools_menu.addSeparator()
        file_menu.addSeparator()

        tools_menu.addAction(compare_action)
        file_menu.addAction(compare_action)

    # Options for files and folders
    # Prompts a user to select a new location for the file
    def move_file(self):
        # Debug
        logging.info("Called Move file")

        try:
            # Selecting the highlighted item of the listbox
            selected_file = self.result_listbox.currentItem().text()

            # Debug
            logging.info(f"Selected file: {selected_file}, prompting for new location...")

            # Prompting the user for a new location
            new_location = QFileDialog.getSaveFileName(
                self.Search_Results_Window,
                caption=f"Rename / Move {os.path.basename(selected_file)}",
                directory=selected_file
            )[0]

            logging.info(f"New file location: {new_location}")

            # If no file was selected
            if new_location == "":
                logging.info("User pressed Cancel")

            # If file was selected, moving the file
            elif os.system(f"mv {FF_Files.convert_file_name_for_terminal(selected_file)} "
                           f"{os.path.join(FF_Files.convert_file_name_for_terminal(new_location))}") != 0:
                # Debug
                logging.critical(f"File not Found: {selected_file}")

                # If cmd wasn't successful display this error
                FF_Additional_UI.PopUps.show_critical_messagebox(
                    "Error!",
                    f"File not found!\nTried to move:\n\n"
                    f" {selected_file}\n\n"
                    f"to:\n\n"
                    f"{new_location}",
                    self.Search_Results_Window
                )

            else:
                # If everything ran successful

                # Debug
                logging.debug(f"Moved {selected_file} to {new_location}")

                # Set the icon
                self.result_listbox.item(
                    self.result_listbox.currentRow()).setIcon(
                    QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "move_icon_small.png")))

                # Change the color to blue
                self.result_listbox.item(
                    self.result_listbox.currentRow()).setBackground(QColor("#1ccaff"))

                # Removing file from cache
                logging.info("Removing file from cache...")
                self.remove_file_from_cache(selected_file)
        except AttributeError:
            # Triggered when no file is selected
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # Moves a file to the trash
    def delete_file(self):
        try:
            # Selecting the highlighted item of the listbox
            selected_file = self.result_listbox.currentItem().text()

            # Trash location
            new_location = os.path.join(
                FF_Files.convert_file_name_for_terminal(FF_Files.USER_FOLDER),
                '.Trash',
                FF_Files.convert_file_name_for_terminal(os.path.basename(selected_file)))
            # Command to execute
            delete_command = (
                f"mv {FF_Files.convert_file_name_for_terminal(selected_file)} {new_location}")

            # Moving the file to trash
            if FF_Additional_UI.PopUps.show_delete_question(self.Search_Results_Window, selected_file):
                if os.system(delete_command) != 0:

                    #  Error message
                    FF_Additional_UI.PopUps.show_critical_messagebox(
                        "Error!", f"File not found: {selected_file}", self.Search_Results_Window)

                    # Debug
                    logging.error(f"File not found: {selected_file}")

                else:
                    # Debug
                    logging.debug(f"Moved {selected_file} to trash")

                    # Set the icon
                    self.result_listbox.item(
                        self.result_listbox.currentRow()).setIcon(
                        QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "trash_icon_small.png")))

                    # Change the color to blue
                    self.result_listbox.item(
                        self.result_listbox.currentRow()).setBackground(QColor("#ff0000"))

                    # Removing file from cache
                    logging.info("Removing file from cache...")
                    self.remove_file_from_cache(selected_file)

        except AttributeError:
            # If no file is selected
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # Open a file with the standard app
    def open_file(self):
        try:
            # Selecting the highlighted item of the focused listbox
            selected_file = self.result_listbox.currentItem().text()

            if os.system(f"open {FF_Files.convert_file_name_for_terminal(selected_file)}") != 0:
                FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"No Program found to open {selected_file}",
                                                                 self.Search_Results_Window)
            else:
                logging.debug(f"Opened: {selected_file}")
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # Opens a file with a user-defined app
    def open_in_app(self):
        try:
            # Prompt for an app
            selected_program = FF_Files.convert_file_name_for_terminal(
                QFileDialog.getOpenFileName(
                    parent=self.Search_Results_Window,
                    directory="/Applications",
                    filter="*.app;")[0])

            # Tests if the user selected an app
            if selected_program != "":
                # Get the selected file
                selected_file = FF_Files.convert_file_name_for_terminal(self.result_listbox.currentItem().text())
                # Open the selected file with the selected program and checking the return value
                if os.system(f"open {selected_file} -a {selected_program}") != 0:
                    # Error message
                    FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"{selected_file} does not exist!",
                                                                     self.Search_Results_Window)
                    logging.error(f"Error with opening {selected_file} with {selected_program}")
                else:
                    logging.debug(f"Opened: {selected_file}")

        # If no file is selected
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # Open a file in the Terminal
    def open_in_terminal(self):
        try:
            selected_file = self.result_listbox.currentItem().text()

            if os.system(f"open {FF_Files.convert_file_name_for_terminal(selected_file)}") != 0:
                FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"Terminal could not open: {selected_file}",
                                                                 self.Search_Results_Window)
            else:
                logging.debug(f"Opened: {selected_file}")
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # Shows a file in finder
    def open_in_finder(self):
        try:
            selected_file = self.result_listbox.currentItem().text()

            if os.system(f"open -R {FF_Files.convert_file_name_for_terminal(selected_file)}") != 0:
                FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"File not Found {selected_file}",
                                                                 self.Search_Results_Window)
            else:
                logging.debug(f"Opened in Finder: {selected_file}")
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # Get basic information about a file
    def file_info(self):
        try:
            file = self.result_listbox.currentItem().text()

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

                FF_Additional_UI.PopUps.show_info_messagebox(
                    f"Information about: {file}",
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
                    self.Search_Results_Window)

            except (FileNotFoundError, PermissionError):
                logging.error(f"{file} does not Exist!")
                FF_Additional_UI.PopUps.show_critical_messagebox("File Not Found!", "File does not exist!\nReload!",
                                                                 self.Search_Results_Window)
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # View the hashes
    def view_hashes(self):
        try:
            # Collecting Files
            hash_file = self.result_listbox.currentItem().text()
            logging.info(f"Collecting {hash_file}...")
            if os.path.isdir(hash_file):
                file_content = b""
                for root, _dirs, files in os.walk(hash_file):
                    for i in files:
                        try:
                            with open(os.path.join(root, i)) as hash_file:
                                file_content = hash_file.read() + file_content
                        except FileNotFoundError:
                            logging.error(f"{hash_file} does not exist!")

            else:
                try:
                    with open(hash_file) as hash_file:
                        file_content = hash_file.read()
                except FileNotFoundError:
                    logging.error(f"{hash_file} does not exist!")
                    FF_Additional_UI.PopUps.show_critical_messagebox("File not found! ", f"{hash_file} does not exist!",
                                                                     self.Search_Results_Window)
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
            FF_Additional_UI.PopUps.show_info_messagebox(f"Hashes of {hash_file}",
                                                         f"Hashes of {hash_file}:\n\n"
                                                         f"MD5:\n {md5_hash}\n\n"
                                                         f"SHA1:\n {sha1_hash}\n\n"
                                                         f"SHA265:\n {sha256_hash}\n\n\n"
                                                         f"Took: {round(final_time, 3)} sec.",
                                                         self.Search_Results_Window)

        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)
            logging.error("Error! Select a File!")

    # Remove moved file from cache
    def remove_file_from_cache(self, file):
        with open(os.path.join(
                FF_Files.CACHED_SEARCHES_FOLDER,
                self.search_path.replace("/", "-") + ".FFCache")) as search_file:

            cached_files = load(search_file)

        cached_files["found_path_set"].remove(file)

        with open(
                os.path.join(
                    FF_Files.CACHED_SEARCHES_FOLDER,
                    self.search_path.replace("/", "-") + ".FFCache"), "w") as search_file:
            dump(cached_files, search_file)

        # Debug
        logging.info("Removed file from cache")
