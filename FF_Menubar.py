# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# Imports
import hashlib
import logging
import os
from json import dump, load
import gc
import shutil
from subprocess import run
from time import perf_counter, ctime
from sys import platform

# PySide6 Gui Imports
from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QAction, QColor, QKeySequence, QClipboard
from PySide6.QtWidgets import QFileDialog, QListWidget, QTreeWidget

# Projects Libraries
import FF_Additional_UI
import FF_Compare
import FF_Duplicated
import FF_Files
import FF_About_UI
import FF_Settings


# This file contains the code for the menu-bar in the search-results window,
# the compare window and the duplicated files window

# Main class
class MenuBar:

    def __init__(
            self, parent, window, listbox, matched_list=None, search_path=None, save_search=None, reload_files=None):
        logging.debug("Setting up menu-bar...")

        self.parent = parent
        self.listbox: QListWidget | QTreeWidget = listbox
        self.search_path = search_path
        self.window = window

        # Menu-bar
        self.menu_bar = self.parent.menuBar()

        # Menus
        self.file_menu = self.menu_bar.addMenu("&File")
        self.edit_menu = self.menu_bar.addMenu("&Edit")
        self.tools_menu = self.menu_bar.addMenu("&Tools")
        self.window_menu = self.menu_bar.addMenu("&Window")
        self.help_menu = self.menu_bar.addMenu("&Help")

        if window == "search":
            # Save Search
            save_search_action = QAction("&Save Search", self.parent)
            save_search_action.triggered.connect(save_search)
            save_search_action.setShortcut("Ctrl+S")
            self.file_menu.addAction(save_search_action)

            # Reload and Remove Deleted Files
            reload_action = QAction("&Reload and Remove Deleted Files", self.parent)
            reload_action.triggered.connect(reload_files)
            reload_action.setShortcut("Ctrl+R")
            self.tools_menu.addAction(reload_action)

        # Clear Cache
        cache_action = QAction("&Clear Cache", self.parent)
        cache_action.triggered.connect(FF_Files.remove_cache)
        cache_action.triggered.connect(
            lambda: FF_Additional_UI.PopUps.show_info_messagebox("Cleared Cache",
                                                                 "Cleared Cache successfully!",
                                                                 self.parent))
        cache_action.setShortcut("Ctrl+T")
        self.tools_menu.addAction(cache_action)

        # Separator
        self.tools_menu.addSeparator()

        if window == "search" or window == "compare" or window == "duplicated":
            # Open File Action
            open_action = QAction("&Open selected file", self.parent)
            open_action.triggered.connect(self.open_file)
            open_action.setShortcut(QKeySequence.StandardKey.Open)
            self.tools_menu.addAction(open_action)

            # Open File in Terminal Action
            open_terminal_action = QAction("&Open selected file in Terminal", self.parent)
            open_terminal_action.triggered.connect(self.open_in_terminal)
            open_terminal_action.setShortcut("Ctrl+Alt+O")
            self.tools_menu.addAction(open_terminal_action)

            # Show File in Finder Action
            show_action = QAction("&Open selected file in Finder", self.parent)
            show_action.triggered.connect(self.open_in_finder)
            show_action.setShortcut("Ctrl+Shift+O")
            self.tools_menu.addAction(show_action)

            # Select an app to open the selected file
            open_in_app_action = QAction("&Select an app to open the selected file...", self.parent)
            open_in_app_action.triggered.connect(self.open_in_app)
            open_in_app_action.setShortcut("Alt+O")
            self.tools_menu.addAction(open_in_app_action)

            # Separator
            self.tools_menu.addSeparator()

            # Select an app to open the selected file
            delete_file_action = QAction("&Move selected file to trash", self.parent)
            delete_file_action.triggered.connect(self.delete_file)
            delete_file_action.setShortcut("Ctrl+Delete")
            self.tools_menu.addAction(delete_file_action)

            # Prompt the user to select a new location for the selected file
            move_file_action = QAction("&Move or Rename selected file", self.parent)
            move_file_action.triggered.connect(self.move_file)
            move_file_action.setShortcut("Ctrl+M")
            self.tools_menu.addAction(move_file_action)

            # Separator
            self.tools_menu.addSeparator()

            # File Info
            info_action = QAction("&Info for selected file", self.parent)
            info_action.triggered.connect(self.file_info)
            info_action.setShortcut("Ctrl+I")
            self.tools_menu.addAction(info_action)

            # View File Hashes
            hash_action = QAction("&Hashes for selected file", self.parent)
            hash_action.triggered.connect(self.view_hashes)
            hash_action.setShortcut("Ctrl+Shift+I")
            self.tools_menu.addAction(hash_action)

            # Separator
            self.tools_menu.addSeparator()

            # Copy file for terminal
            copy_path_action = QAction("&Copy file path", self.parent)
            copy_path_action.triggered.connect(self.copy_file)
            copy_path_action.setShortcut("Ctrl+C")
            self.tools_menu.addAction(copy_path_action)

            # Copy file
            copy_terminal_action = QAction("&Copy file path for terminal", self.parent)
            copy_terminal_action.triggered.connect(self.copy_path_for_terminal)
            copy_terminal_action.setShortcut("Ctrl+Alt+C")
            self.tools_menu.addAction(copy_terminal_action)

            # Copy file name
            copy_name_action = QAction("&Copy file name", self.parent)
            copy_name_action.triggered.connect(self.copy_name)
            copy_name_action.setShortcut("Ctrl+Shift+C")
            self.tools_menu.addAction(copy_name_action)

        # About File Find
        about_action = QAction("&About File Find", self.parent)
        about_action.triggered.connect(lambda: FF_About_UI.AboutWindow(self.parent))
        self.help_menu.addAction(about_action)

        # Settings
        settings_action = QAction("&Settings", self.parent)
        settings_action.triggered.connect(lambda: FF_Settings.SettingsWindow(self.parent))
        settings_action.setShortcut("Ctrl+,")
        self.help_menu.addAction(settings_action)

        # Close Window
        close_action = QAction("&Close Window", self.parent)
        close_action.triggered.connect(self.parent.destroy)
        close_action.triggered.connect(gc.collect)
        close_action.setShortcut("Ctrl+W")
        self.window_menu.addAction(close_action)

        # Help
        help_action = QAction("&About File Find", self.parent)
        help_action.triggered.connect(lambda: FF_About_UI.AboutWindow(self.parent))
        self.help_menu.addAction(help_action)

        # Tutorial
        tutorial_action = QAction("&Tutorial", self.parent)
        tutorial_action.triggered.connect(lambda: FF_Additional_UI.welcome_popups(self.parent, force_popups=True))
        self.help_menu.addAction(tutorial_action)

        if window == "search":
            # Compare Search
            compare_action = QAction("&Compare to other Search...", self.parent)
            compare_action.triggered.connect(lambda: FF_Compare.CompareSearches(matched_list, search_path, self.parent))
            compare_action.setShortcut("Ctrl+N")

            # Find duplicated
            duplicated_action = QAction("&Find duplicated files...", self.parent)
            duplicated_action.triggered.connect(
                lambda: FF_Duplicated.DuplicatedSettings(parent, search_path, matched_list))
            duplicated_action.setShortcut("Ctrl+D")

            # Separator for visual indent
            self.tools_menu.addSeparator()
            self.file_menu.addSeparator()

            # Add actions
            self.tools_menu.addAction(compare_action)
            self.file_menu.addAction(compare_action)

            self.tools_menu.addAction(duplicated_action)
            self.file_menu.addAction(duplicated_action)

    # Options for files and folders
    # Prompts a user to select a new location for the file
    def move_file(self):
        # Debug
        logging.info("Called Move file")

        try:
            # Selecting the highlighted item of the listbox
            if self.window == "compare" or self.window == "search":
                selected_file = self.get_listbox().currentItem().text()
            else:
                selected_file = self.get_listbox().currentItem().text(0)

            # Debug
            logging.info(f"Selected file: {selected_file}, prompting for new location...")

            # Prompting the user for a new location
            new_location = QFileDialog.getSaveFileName(
                self.parent,
                caption=f"Rename / Move {os.path.basename(selected_file)}",
                dir=selected_file
            )[0]

            logging.info(f"New file location: {new_location}")

            # If no file was selected
            if new_location == "":
                logging.info("User pressed Cancel")
                return
            try:
                shutil.move(selected_file, new_location)
            except FileNotFoundError:
                # Debug
                logging.critical(f"File not Found: {selected_file}")

                # If cmd wasn't successful display this error
                FF_Additional_UI.PopUps.show_critical_messagebox(
                    "Error!",
                    f"File not found!\nTried to move:\n\n"
                    f" {selected_file}\n\n"
                    f"to:\n\n"
                    f"{new_location}",
                    self.parent
                )

            # If everything ran successful
            else:
                # Debug
                logging.debug(f"Moved {selected_file} to {new_location}")

                if self.window == "compare" or self.window == "search":
                    # Set the icon
                    icon = FF_Additional_UI.UIIcon(
                        os.path.join(FF_Files.ASSETS_FOLDER, "move_icon_small.png"),
                        icon_set_func=self.get_listbox().item(self.get_listbox().currentRow()).setIcon,
                        turn_auto=False)

                    icon.turn_dark()

                    # Change the color to red
                    self.get_listbox().item(
                        self.get_listbox().currentRow()).setBackground(QColor(FF_Files.RED_COLOR))
                    # Change font color to white
                    self.get_listbox().item(self.get_listbox().currentRow()).setForeground(QColor("white"))

                    # Change font to italic
                    font = self.get_listbox().item(self.get_listbox().currentRow()).font()
                    font.setItalic(True)
                    self.get_listbox().item(self.get_listbox().currentRow()).setFont(font)

                # QTreeWidget needs special treatment
                elif self.window == "duplicated":
                    # Icon
                    # Set the icon
                    icon = FF_Additional_UI.UIIcon(
                        os.path.join(FF_Files.ASSETS_FOLDER, "move_icon_small.png"),
                        icon_set_func=lambda x: self.get_listbox().currentItem().setIcon(0, x),
                        turn_auto=False)

                    icon.turn_dark()

                    # Change the color to red
                    self.get_listbox().currentItem().setBackground(0, QColor(FF_Files.RED_COLOR))
                    # Change font color to white
                    self.get_listbox().currentItem().setForeground(0, QColor("white"))

                    # Change font to italic
                    font = self.get_listbox().currentItem().font(0)
                    font.setItalic(True)
                    self.get_listbox().currentItem().setFont(0, font)

                # Removing file from cache
                logging.info("Removing file from cache...")
                self.remove_file_from_cache(selected_file)
        except SystemExit:
            # Triggered when no file is selected
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # Moves a file to the trash
    def delete_file(self):
        try:
            # Selecting the highlighted item of the listbox
            if self.window == "compare" or self.window == "search":
                selected_file = self.get_listbox().currentItem().text()
            else:
                selected_file = self.get_listbox().currentItem().text(0)

            # Trash location
            new_location = str(os.path.join(FF_Files.USER_FOLDER, ".Trash", os.path.basename(selected_file)))

            logging.info(f"File: {selected_file} New: {new_location}")
            # Moving the file to trash
            if FF_Additional_UI.PopUps.show_delete_question(self.parent, selected_file):

                try:
                    # Try to move the file to trash
                    shutil.move(selected_file, new_location)

                except FileNotFoundError:

                    #  Error message
                    FF_Additional_UI.PopUps.show_critical_messagebox(
                        "Error!", f"File not found: {selected_file}", self.parent)

                    # Debug
                    logging.error(f"File not found: {selected_file}")

                # If everything ran successful
                else:
                    # Debug
                    logging.debug(f"Moved {selected_file} to trash")

                    if self.window == "compare" or self.window == "search":

                        # Set the icon
                        icon = FF_Additional_UI.UIIcon(
                            os.path.join(FF_Files.ASSETS_FOLDER, "trash_icon_small.png"),
                            icon_set_func=self.get_listbox().item(self.get_listbox().currentRow()).setIcon,
                            turn_auto=False)

                        icon.turn_dark()

                        # Change the color to red
                        self.get_listbox().item(
                            self.get_listbox().currentRow()).setBackground(QColor(FF_Files.RED_COLOR))
                        # Change font color to white
                        self.get_listbox().item(self.get_listbox().currentRow()).setForeground(QColor("white"))

                        # Change font to italic
                        font = self.get_listbox().item(self.get_listbox().currentRow()).font()
                        font.setItalic(True)
                        self.get_listbox().item(self.get_listbox().currentRow()).setFont(font)

                    # QTreeWidget needs special treatment
                    elif self.window == "duplicated":
                        # Icon
                        # Set the icon
                        icon = FF_Additional_UI.UIIcon(
                            os.path.join(FF_Files.ASSETS_FOLDER, "trash_icon_small.png"),
                            icon_set_func=lambda x: self.get_listbox().currentItem().setIcon(0, x),
                            turn_auto=False)

                        icon.turn_dark()

                        # Change the color to red
                        self.get_listbox().currentItem().setBackground(0, QColor(FF_Files.RED_COLOR))
                        # Change font color to white
                        self.get_listbox().currentItem().setForeground(0, QColor("white"))

                        # Change font to italic
                        font = self.get_listbox().currentItem().font(0)
                        font.setItalic(True)
                        self.get_listbox().currentItem().setFont(0, font)

                    # Removing file from cache
                    logging.info("Removing file from cache...")
                    self.remove_file_from_cache(selected_file)

        except AttributeError:
            # If no file is selected
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # Open a file with the standard app
    def open_file(self):
        try:
            # Selecting the highlighted item of the focused listbox
            selected_file = self.get_current_item()

            return_code = -1

            # Opening the file, the specific command depends on the platform
            if platform == "darwin":
                # Collecting the return code
                return_code = run(["open", selected_file]).returncode
            elif platform == "win32" or platform == "cygwin":
                return_code = run(["start", selected_file], shell=True).returncode
            elif platform == "linux":
                return_code = run(["xdg-open", selected_file]).returncode

            if return_code != 0:
                # Debug
                logging.error(f"No Program found to open {selected_file}")

                FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"No Program found to open {selected_file}",
                                                                 self.parent)
            else:
                logging.debug(f"Opened: {selected_file}")
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # Opens a file with a user-defined app
    def open_in_app(self):
        try:
            # Prompt for an app
            selected_program = QFileDialog.getOpenFileName(
                parent=self.parent,
                dir="/Applications",
                filter="*.app;")[0]

            # Tests if the user selected an app
            if selected_program != "":
                # Get the selected file
                selected_file = self.get_current_item()

                # Open the selected file with the selected program and checking the return value
                return_code = -1

                # Opening the file, the specific command depends on the platform
                if platform == "darwin":
                    # Collecting the return code
                    return_code = run(["open", selected_file, "-a", selected_program]).returncode
                elif platform == "win32" or platform == "cygwin":
                    return_code = run(["start", selected_file], shell=True).returncode
                elif platform == "linux":
                    return_code = run(["xdg-open", selected_file]).returncode

                if return_code != 0:
                    # Error message
                    FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"{selected_file} does not exist!",
                                                                     self.parent)
                    logging.error(f"Error with opening {selected_file} with {selected_program}")

                else:
                    # Debug
                    logging.debug(f"Opened: {selected_file}")

        # If no file is selected
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # Open a file in the Terminal
    def open_in_terminal(self):
        # Only works for folders
        try:
            selected_file = self.get_current_item()

            if os.path.isfile(selected_file):
                # Can't open files in Terminal
                logging.error("Can't open files in Terminal")
                (FF_Additional_UI.PopUps.show_critical_messagebox
                 ("Error!", f"Terminal could not open file (only folders): {selected_file}", self.parent))
                return

            # Open the selected file with the selected program and checking the return value
            return_code = -1

            # Opening the file, the specific command depends on the platform
            if platform == "darwin":
                # Collecting the return code
                return_code = run(["open",
                                   selected_file,
                                   "-a",
                                   os.path.join("/System", "Applications", "Utilities", "Terminal.app")]).returncode
            elif platform == "win32" or platform == "cygwin":
                return_code = run(["start", "/max", "cd", selected_file], shell=True).returncode
            elif platform == "linux":
                return_code = run(["xdg-open", selected_file]).returncode

            if return_code != 0:
                # Error message
                FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"Terminal could not open: {selected_file}",
                                                                 self.parent)
            else:
                logging.debug(f"Opened: {selected_file}")
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # Shows a file in finder
    def open_in_finder(self):
        try:
            selected_file = self.get_current_item()

            # Open the selected file with the selected program and checking the return value
            return_code = -1

            # Opening the file, the specific command depends on the platform
            if platform == "darwin":
                # Collecting the return code
                return_code = run(["open",
                                   "-R",
                                   selected_file]).returncode
            elif platform == "win32" or platform == "cygwin":
                return_code = run(["start", os.path.dirname(selected_file)], shell=True).returncode
            elif platform == "linux":
                return_code = run(["xdg-open", os.path.dirname(selected_file)]).returncode

            # If the command failed
            if return_code != 0:
                FF_Additional_UI.PopUps.show_critical_messagebox("Error!", f"File not Found {selected_file}",
                                                                 self.parent)
            else:
                logging.debug(f"Opened in Finder: {selected_file}")
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # Get basic information about a file
    def file_info(self):
        try:
            file = self.get_current_item()

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

                # Display file path nicely
                if not len(file) < 105:
                    file_path = ""
                    last_step = 0
                    for part in range(0, len(file), 100):
                        file_path = file_path + "\n" + file[last_step: part]
                        last_step = part
                else:
                    file_path = file

                # Get dates
                # Date modified
                m_date = ctime(os.path.getmtime(file))
                # Date created
                # On macOS
                if platform == "darwin":
                    c_date = ctime(os.stat(file).st_birthtime)
                # On Linux
                elif platform == "linux":
                    c_date = "Can't fetch date created on linux"
                # On Windows
                else:
                    c_date = ctime(os.path.getctime(file))

                # Show Info window
                FF_Additional_UI.PopUps.show_info_messagebox(
                    f"Information about: {FF_Files.display_path(file, 30)}",
                    f"\n"
                    f"Path: {file_path}\n"
                    f"\n"
                    f"Type: {filetype}\n"
                    f"File Name: {os.path.basename(file)}\n"
                    f"Size: "
                    f"{FF_Files.conv_file_size(FF_Files.get_file_size(file))}\n"
                    f"Date Created: {c_date}\n"
                    f"Date Modified: {m_date}\n",
                    self.parent, large=True)

            except (FileNotFoundError, PermissionError):
                logging.error(f"{file} does not Exist!")
                FF_Additional_UI.PopUps.show_critical_messagebox("File Not Found!", "File does not exist!\nReload!",
                                                                 self.parent)
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # View the hashes
    def view_hashes(self):
        try:
            # Collecting Files
            hash_file = self.get_current_item()
        except AttributeError:
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)
            logging.error("Error! Select a File!")
        else:
            # Debug
            logging.info(f"Collecting hashes of {hash_file}...")

            # If the path leads to a file
            if os.path.isfile(hash_file):

                # Computing Hashes
                logging.info(f"Computing Hashes of {hash_file}...")

                # structure
                hash_list = {"md5": "", "sha1": "", "sha256": ""}
                # Buffer size for hashes
                buffer_size = 65536
                # Saving times
                saved_time = perf_counter()

                # Function for all hash types
                def calc_hash(hash_str: str, hash_func: hashlib):
                    logging.debug(f"Computing {hash_str} Hash...")
                    with open(hash_file, "rb") as open_hash_file:
                        # Initializing the hash method e.g. sha1
                        computing_hash = hash_func(usedforsecurity=False)
                        while True:
                            # reading data = BUF_SIZE from the
                            # file and saving it in a variable
                            data = open_hash_file.read(buffer_size)

                            # True if eof = 1
                            if not data:
                                break
                            # Updating hash
                            computing_hash.update(data)

                        # Hashes all the input data passed
                        hash_list[hash_str] = computing_hash.hexdigest()

                # Defining threads
                hash_thread_pool = QThreadPool(self.parent)

                # sha1 Hash
                hash_thread_pool.start(lambda: calc_hash("sha1", hashlib.sha1))

                # md5 Hash
                hash_thread_pool.start(lambda: calc_hash("md5", hashlib.md5))

                # sha256 Hash
                hash_thread_pool.start(lambda: calc_hash("sha256", hashlib.sha256))

                # Waiting for hashes
                logging.debug("Waiting for Hashes to complete...")

                hash_thread_pool.waitForDone()
                sha1_hash = hash_list["sha1"]
                logging.debug(f"{sha1_hash = }")

                md5_hash = hash_list["md5"]
                logging.debug(f"{md5_hash = }")

                sha256_hash = hash_list["sha256"]
                logging.debug(f"{sha256_hash = }")

                # Time Feedback
                final_time = perf_counter() - saved_time
                logging.debug(f"Took {final_time} seconds")

                # Give Feedback
                FF_Additional_UI.PopUps.show_info_messagebox(f"Hashes of {FF_Files.display_path(hash_file, 90)}",
                                                             "\n"
                                                             f"MD5:\n {md5_hash}\n\n"
                                                             f"SHA1:\n {sha1_hash}\n\n"
                                                             f"SHA265:\n {sha256_hash}\n\n\n"
                                                             f"Took: {round(final_time, 3)} sec.",
                                                             self.parent, large=True)
            else:
                # If os.path.isfile() returns False
                FF_Additional_UI.PopUps.show_critical_messagebox(
                    title="Not a file!",
                    text=f"{hash_file} does not exists or is a folder!\n\nYou can only view hashes of files",
                    parent=self.parent)
                # Debug
                logging.error(f"{hash_file} does not exist or is a folder!")

    # Copy file name to clipboard
    def copy_file(self):
        file = self.get_current_item()
        clipboard = QClipboard()
        clipboard.setText(file)

    # Copy file name to clipboard
    def copy_name(self):
        file = self.get_current_item()
        clipboard = QClipboard()
        clipboard.setText(os.path.basename(file))

    # Copy path for Terminal
    def copy_path_for_terminal(self):
        file = self.get_current_item()
        clipboard = QClipboard()
        clipboard.setText(FF_Files.convert_file_name_for_terminal(file))

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

    # Getting the listbox because there are two in the compare window
    def get_listbox(self):
        if self.window == "compare":
            return self.parent.focusWidget()
        elif self.window == "duplicated":
            return self.listbox
        else:
            return self.listbox

    # Getting the listbox item because there are two in the compare window
    def get_current_item(self):
        if self.window == "compare":
            return self.parent.focusWidget().currentItem().text()
        elif self.window == "duplicated":
            self.listbox: QTreeWidget
            return self.listbox.currentItem().text(0)
        else:
            return self.listbox.currentItem().text()
