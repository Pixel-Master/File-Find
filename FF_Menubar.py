# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# Imports
import hashlib
import logging
import os
import subprocess
from json import dump, load
import gc
import shutil
from subprocess import run
from time import perf_counter, ctime
from sys import platform
from platform import mac_ver

# PySide6 Gui Imports
from PySide6.QtCore import QThreadPool, QSize
from PySide6.QtGui import QAction, QColor, QKeySequence, QClipboard, QBrush, Qt
from PySide6.QtWidgets import QFileDialog, QListWidget, QTreeWidget, QMenu, QPushButton, QTreeWidgetItem

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
            self, parent, window, listbox=None, listbox2=None,
            matched_list=None, search_path=None, save_search=None, file_count_text=None,
            cache_file_path=None, bottom_layout=None, search_path2=None, duplicated_dict=None):
        logging.debug("Setting up menu-bar...")

        self.parent = parent
        self.listbox: QListWidget | QTreeWidget = listbox
        self.listbox2: QListWidget | QTreeWidget = listbox2
        self.search_path = search_path
        self.search_path2 = search_path2
        self.window = window
        self.cache_file_path = cache_file_path
        if self.cache_file_path is not None:
            # Getting the depth from the cache file's metadata brother
            with open(FF_Files.get_metadata_file_from_cache_file(cache_file_path)) as depth_file:
                try:
                    self.search_depth = load(depth_file)["global_depth_limit"]
                except FileNotFoundError:
                    pass
        self.matched_list = matched_list
        self.duplicated_dict = duplicated_dict
        self.file_count_text = file_count_text

        # Creating a set for all marked files
        self.marked_files = set()
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
        if window == "search" or window == "duplicated":
            # Reload and Remove Deleted Files
            reload_action = QAction("&Reload and Remove Deleted Files", self.parent)
            reload_action.triggered.connect(self.reload_files)
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
            self.open_action = QAction("&Open selected file", self.parent)
            self.open_action.triggered.connect(self.open_file)
            self.open_action.setShortcut(QKeySequence.StandardKey.Open)
            self.tools_menu.addAction(self.open_action)

            # Open File in Terminal Action
            self.open_terminal_action = QAction("&Open selected file in Terminal", self.parent)
            self.open_terminal_action.triggered.connect(self.open_in_terminal)
            self.open_terminal_action.setShortcut("Ctrl+Alt+O")
            self.tools_menu.addAction(self.open_terminal_action)

            # Show File in Finder Action
            self.show_action = QAction("&View selected file in Finder/File Explorer", self.parent)
            self.show_action.triggered.connect(self.open_in_finder)
            self.show_action.setShortcut("Ctrl+Shift+O")
            self.tools_menu.addAction(self.show_action)

            # Select an app to open the selected file
            self.open_in_app_action = QAction("&Select an app to open the selected file...", self.parent)
            self.open_in_app_action.triggered.connect(self.open_in_app)
            self.open_in_app_action.setShortcut("Alt+O")
            self.tools_menu.addAction(self.open_in_app_action)

            # Separator
            self.tools_menu.addSeparator()

            # Select an app to open the selected file
            self.delete_file_action = QAction("&Move selected file to trash", self.parent)
            self.delete_file_action.triggered.connect(self.delete_file)
            self.delete_file_action.setShortcut("Ctrl+Backspace")
            self.tools_menu.addAction(self.delete_file_action)

            # Prompt the user to select a new location for the selected file
            self.move_file_action = QAction("&Move or Rename selected file", self.parent)
            self.move_file_action.triggered.connect(self.move_file)
            self.move_file_action.setShortcut("Ctrl+M")
            self.tools_menu.addAction(self.move_file_action)

            self.mark_file_action = QAction("&Mark/Unmark file", self.parent)
            self.mark_file_action.triggered.connect(lambda: self.mark_file(FF_Files.GREEN_LIGHT_THEME_COLOR))
            self.mark_file_action.setShortcut("M")
            self.tools_menu.addAction(self.mark_file_action)

            # Separator
            self.tools_menu.addSeparator()

            # File Info
            self.info_action = QAction("&Info for selected file", self.parent)
            self.info_action.triggered.connect(self.file_info)
            self.info_action.setShortcut("Ctrl+I")
            self.tools_menu.addAction(self.info_action)

            # View File Hashes
            self.hash_action = QAction("&Hashes for selected file", self.parent)
            self.hash_action.triggered.connect(self.view_hashes)
            self.hash_action.setShortcut("Ctrl+Shift+I")
            self.tools_menu.addAction(self.hash_action)

            # Separator
            self.edit_menu.addSeparator()

            # Copy file for terminal
            self.copy_path_action = QAction("&Copy file path", self.parent)
            self.copy_path_action.triggered.connect(self.copy_file)
            self.copy_path_action.setShortcut("Ctrl+C")
            self.edit_menu.addAction(self.copy_path_action)

            # Copy file
            self.copy_terminal_action = QAction("&Copy file path for terminal", self.parent)
            self.copy_terminal_action.triggered.connect(self.copy_path_for_terminal)
            self.copy_terminal_action.setShortcut("Ctrl+Alt+C")
            self.edit_menu.addAction(self.copy_terminal_action)

            # Copy file name
            self.copy_name_action = QAction("&Copy file name", self.parent)
            self.copy_name_action.triggered.connect(self.copy_name)
            self.copy_name_action.setShortcut("Ctrl+Shift+C")
            self.edit_menu.addAction(self.copy_name_action)

            # Bottom Buttons
            # Button to open the File in Finder
            move_file = self.generate_button(
                "Move / Rename", self.move_file, icon=os.path.join(FF_Files.ASSETS_FOLDER, "Move_icon_small.png"))
            bottom_layout.addWidget(move_file)
            # Menu when Right-clicking
            self.create_context_menu(
                move_file, (self.mark_file_action, self.delete_file_action))

            # Button to move the file to trash
            delete_file = self.generate_button(
                "Move to Trash", self.delete_file, icon=os.path.join(FF_Files.ASSETS_FOLDER, "Trash_icon_small.png"))
            bottom_layout.addWidget(delete_file)
            # Menu when Right-clicking
            self.create_context_menu(
                delete_file, (self.mark_file_action, self.move_file_action))

            # Button to open the file
            open_file = self.generate_button(
                "Open", self.open_file, icon=os.path.join(FF_Files.ASSETS_FOLDER, "Open_icon_small.png"))
            bottom_layout.addWidget(open_file)
            # Menu when Right-clicking
            self.create_context_menu(
                open_file, (self.show_action, self.open_in_app_action, self.open_terminal_action))

            # Button to show info about the file
            file_info_button = self.generate_button(
                "Info", self.file_info, icon=os.path.join(FF_Files.ASSETS_FOLDER, "Info_button_img_small.png"))
            bottom_layout.addWidget(file_info_button)
            # Menu when Right-clicking
            self.create_context_menu(
                file_info_button, (self.hash_action, self.copy_path_action,
                                   self.copy_name_action, self.copy_terminal_action))

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
            compare_action.triggered.connect(lambda: FF_Compare.CompareSearches(
                matched_list, search_path, cache_file_path, self.marked_files, self.parent))
            compare_action.setShortcut("Ctrl+N")

            # Find duplicated
            duplicated_action = QAction("&Find duplicated files...", self.parent)
            duplicated_action.triggered.connect(
                lambda: FF_Duplicated.DuplicatedSettings(parent, search_path, matched_list, cache_file_path,
                                                         self.marked_files))
            duplicated_action.setShortcut("Ctrl+D")

            # Separator for visual indent
            self.file_menu.addSeparator()

            # Add actions
            self.file_menu.addAction(compare_action)

            self.file_menu.addAction(duplicated_action)

    # Options for files and folders
    # Prompts a user to select a new location for the file
    def move_file(self):
        # Debug
        logging.info("Called Move file")

        try:
            # Selecting the highlighted item of the listbox
            selected_file = self.get_current_item()

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
            else:
                new_location = os.path.normpath(new_location)

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
                        self.get_listbox().currentRow()).setBackground(QColor(FF_Files.RED_DARK_THEME_COLOR))
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
                    self.get_listbox().currentItem().setBackground(0, QColor(FF_Files.RED_DARK_THEME_COLOR))
                    self.get_listbox().currentItem().setBackground(1, QColor(FF_Files.RED_DARK_THEME_COLOR))
                    # Change font color to white
                    self.get_listbox().currentItem().setForeground(0, QColor("white"))
                    self.get_listbox().currentItem().setForeground(1, QColor("white"))

                    # Change font to italic
                    font = self.get_listbox().currentItem().font(0)
                    font.setItalic(True)
                    self.get_listbox().currentItem().setFont(0, font)
                    self.get_listbox().currentItem().setFont(1, font)

                # Removing file from cache
                logging.info("Removing file from cache...")
                self.remove_file_from_cache(selected_file)
        except SystemExit:
            # Triggered when no file is selected
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)

    # Moves a file to the trash
    def delete_file(self):
        selected_file = self.get_current_item()

        if platform == "darwin":
            # the trash command is only available on macOS 14+
            # The alternative, apple scripts, requires an extra authorization from the user
            # Getting the current macOS major version
            if int(mac_ver()[0].split(".")[0]) >= 14:
                command = ["trash", selected_file]
            else:
                command = ["osascript", "-e",
                           f"tell application \"Finder\" to delete POSIX file \"${selected_file}\""]
        elif platform == "linux":
            command = ["gio", "trash", selected_file]
        elif platform == "win32" or platform == "cygwin":
            command = ["echo",
                       f"(new-object -comobject Shell.Application).Namespace(0).ParseName(\"{selected_file}\")"
                       f".InvokeVerb(\"delete\")", "|", "powershell", "-command", "-"]
        else:
            command = None
        # Moving the file to trash, after asking if necessary
        if FF_Additional_UI.PopUps.show_delete_question(self.parent, selected_file):

            try:
                # Try to move the file to trash and add a date for uniqueness
                subprocess.run(command, check=True)

            except (subprocess.CalledProcessError, FileNotFoundError):

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
                        self.get_listbox().currentRow()).setBackground(QColor(FF_Files.RED_DARK_THEME_COLOR))
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
                    self.get_listbox().currentItem().setBackground(0, QColor(FF_Files.RED_LIGHT_THEME_COLOR))
                    self.get_listbox().currentItem().setBackground(1, QColor(FF_Files.RED_LIGHT_THEME_COLOR))
                    # Change font color to white
                    self.get_listbox().currentItem().setForeground(0, QColor("white"))
                    self.get_listbox().currentItem().setForeground(1, QColor("white"))

                    # Change font to italic
                    font = self.get_listbox().currentItem().font(0)
                    font.setItalic(True)
                    self.get_listbox().currentItem().setFont(0, font)
                    self.get_listbox().currentItem().setFont(1, font)

                # Removing file from cache
                logging.info("Removing file from cache...")
                self.remove_file_from_cache(selected_file)

    # Marks a file
    def mark_file(self, color, selected_file=None):
        # The file isn't predetermined
        if selected_file is None:
            selected_file = self.get_current_item()
            listbox_item = self.get_listbox().currentItem()
            predetermined_item = False

        # The file is predetermined we first have to find the actual list item from the string
        else:
            if self.window == "search":
                # The first item is the first and only match
                listbox_item = self.get_listbox().findItems(selected_file, Qt.MatchFlag.MatchExactly)
            elif self.window == "compare":
                listbox_item = self.listbox.findItems(selected_file, Qt.MatchFlag.MatchExactly)
                # If the files is in the other listbox and the found list is empty
                if not listbox_item:
                    listbox_item = self.listbox2.findItems(selected_file, Qt.MatchFlag.MatchExactly)
            # In duplicated
            else:
                # Search recursively
                listbox_item = self.get_listbox().findItems(selected_file,
                                                            Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive, 0)
            # If the item wasn't found because it isn't in the results list, just skip
            if not listbox_item:
                return
            else:
                # The first item wll be the first and only match
                listbox_item = listbox_item[0]
            predetermined_item = True

        # Testing if file is already marked and not predetermined
        if selected_file in self.marked_files and not predetermined_item:
            logging.info(f"Unmarking {selected_file}")
            self.marked_files.remove(selected_file)
            # Unselecting the highlighted item of the listbox
            if self.window == "compare" or self.window == "search":

                # Change the color to the desired color
                listbox_item.setBackground(QBrush())

                # Change font color to white if necessary
                QColor(color).lightness()
                listbox_item.setForeground(QBrush())

            # In duplicated
            else:
                # Change the (background) colors to default
                listbox_item.setBackground(0, QBrush())
                listbox_item.setForeground(0, QBrush())
                listbox_item.setBackground(1, QBrush())
                listbox_item.setForeground(1, QBrush())
        # If file isn't already marked
        else:
            logging.info(f"Marking {selected_file} {color}")
            self.marked_files.add(selected_file)
            # Selecting the highlighted item of the listbox
            if self.window == "compare" or self.window == "search":

                # Change the color to the desired color
                listbox_item.setBackground(QColor(color))

                # Change font color to white if necessary
                QColor(color).lightness()
                listbox_item.setForeground(QColor("white"))
            # In duplicated
            else:
                # Change the color to the specified one
                listbox_item.setBackground(0, QColor(color))
                # Change font color to white
                listbox_item.setForeground(0, QColor("white"))

                # Change the color to specified one
                listbox_item.setBackground(1, QColor(color))
                # Change font color to white
                listbox_item.setForeground(1, QColor("white"))

    # Open a file with the default app
    def open_file(self):
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

    # Opens a file with a user-defined app
    def open_in_app(self):
        if platform == "darwin":
            open_dir = "/Applications"
        else:
            open_dir = FF_Files.USER_FOLDER
        # Prompt for an app
        selected_program = QFileDialog.getOpenFileName(
            parent=self.parent,
            dir=open_dir,
            filter="Application or Executable (*.app *.bin *.exe *")[0]

        # Tests if the user selected an app
        if selected_program != "":
            # Get the selected file
            selected_file = self.get_current_item()
            # Normalise the program path
            selected_program = os.path.normpath(selected_program)

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

    # Open a file in the Terminal
    def open_in_terminal(self):
        # Only works for folders
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

    # Shows a file in finder
    def open_in_finder(self):

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

    # Get basic information about a file
    def file_info(self):
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

    # View the hashes
    def view_hashes(self):
        # Collecting Files
        hash_file = self.get_current_item()
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
            logging.debug(f"{sha1_hash=}")

            md5_hash = hash_list["md5"]
            logging.debug(f"{md5_hash=}")

            sha256_hash = hash_list["sha256"]
            logging.debug(f"{sha256_hash=}")

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
        clipboard = QClipboard()
        clipboard.setText(self.get_current_item())

    # Copy file name to clipboard
    def copy_name(self):
        clipboard = QClipboard()
        clipboard.setText(os.path.basename(self.get_current_item()))

    # TODO: remove or implement correctly
    def quick_look(self):
        QThreadPool(self.parent).start(lambda: run(["qlmanage", "-p", self.get_current_item()]))

    # Copy path for Terminal
    def copy_path_for_terminal(self):
        clipboard = QClipboard()
        clipboard.setText(self.get_current_item().replace(" ", r"\ "))

    # Remove moved file from cache
    def remove_file_from_cache(self, file):
        try:
            cache_file_with_same_path = FF_Files.path_to_cache_file(self.search_path, self.search_depth)
            with open(cache_file_with_same_path) as search_file:
                cached_files = load(search_file)

            cached_files["found_path_set"].remove(file)

            with open(cache_file_with_same_path, "w") as search_file:
                dump(cached_files, search_file)

            # If there is a cache file from a higher directory
            if self.cache_file_path != cache_file_with_same_path:
                with open(self.cache_file_path) as upper_search_file:
                    cached_files = load(upper_search_file)

                cached_files["found_path_set"].remove(file)

                with open(self.cache_file_path, "w") as upper_search_file:
                    dump(cached_files, upper_search_file)

            del cached_files
        except (FileNotFoundError, KeyError):
            # It isn't bad if the file isn't in cache anymore or the cache file doesn't exist
            pass
        else:
            # Debug
            logging.debug("Removed file from cache")

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
        try:
            if self.window == "compare":
                return self.parent.focusWidget().currentItem().text()
            elif self.window == "duplicated":
                self.listbox: QTreeWidget
                return self.listbox.currentItem().text(0)
            else:
                return self.listbox.currentItem().text()
        except AttributeError:
            # Triggered when no file is selected
            logging.error("Error! Select a File!")
            FF_Additional_UI.PopUps.show_critical_messagebox("Error!", "Select a File!", self.parent)
            raise AttributeError("User selected no file")

    # When an item is double-clicked
    def double_clicking_item(self):
        # Loading Setting
        action = FF_Settings.SettingsWindow.load_setting("double_click_action")

        # Action according to the set option
        if action == "View file in Finder/File Explorer":
            self.open_in_finder()
        elif action == "Open file":
            self.open_file()
        elif action == "Info about file":
            self.file_info()
        else:
            logging.error("Select option for double_click_action is NOT valid. Resetting it.\n")
            # Resetting it because the option isn't valid
            FF_Settings.SettingsWindow.update_setting("double_click_action",
                                                      FF_Files.DEFAULT_SETTINGS["double_click_action"])

    # Reloads File, check all collected files, if they still exist
    def reload_files(self):
        try:
            logging.info("Reload...")
            time_before_reload = perf_counter()
            removed_list = set()
            # differs form the list in duplicated
            removed_files_count = 0
            if self.window == "search":
                # Creating a copy so that the list doesn't run out of index
                parent_items_without_deleted_files = self.matched_list.copy()
                for matched_file in self.matched_list:
                    if not os.path.exists(matched_file):
                        # Remove file from widget if it doesn't exist
                        self.get_listbox().takeItem(parent_items_without_deleted_files.index(matched_file))
                        parent_items_without_deleted_files.remove(matched_file)
                        # Adding file to removed_list to later remove it from cache
                        removed_list.add(matched_file)
                        removed_files_count += 1

            elif self.window == "duplicated":
                # self.matched_list is a dict with files as key and lists with files as values
                parent_items_without_deleted_files = self.matched_list.copy()

                for prove_file in self.matched_list:
                    # Get the actual list tree item
                    parent_item: QTreeWidgetItem = self.get_listbox().itemFromIndex(
                        self.get_listbox().model().index(parent_items_without_deleted_files.index(prove_file), 0))

                    matched_sub_list = self.duplicated_dict[prove_file].copy()
                    for matched_sub_file in matched_sub_list.copy():
                        if not os.path.exists(matched_sub_file):
                            # Remove file from widget if it doesn't exist
                            parent_item.takeChild(matched_sub_list.index(matched_sub_file))
                            # Remove file from duplicated sub list
                            self.duplicated_dict[prove_file].remove(matched_sub_file)
                            # Adding file to removed_list to later remove it from cache
                            removed_list.add(matched_sub_file)
                            removed_files_count += 1
                            matched_sub_list.remove(matched_sub_file)
                    # Tests, if the parent item exists or if all subitems got deleted
                    if not os.path.exists(prove_file) or not matched_sub_list:
                        removed_files_count += 1
                        # If there are at least two sub item left
                        if len(matched_sub_list) > 1:
                            # Take the first sub item and copy all it's properties to the parent item
                            to_be_copied_item = parent_item.child(0)
                            parent_item.setText(0, to_be_copied_item.text(0))
                            parent_item.setText(1, to_be_copied_item.text(1))
                            parent_item.setFont(0, to_be_copied_item.text(0))
                            parent_item.setFont(1, to_be_copied_item.text(1))
                            parent_item.setForeground(0, to_be_copied_item.foreground(0))
                            parent_item.setForeground(1, to_be_copied_item.foreground(1))
                            parent_item.setBackground(0, to_be_copied_item.background(0))
                            parent_item.setBackground(1, to_be_copied_item.background(1))
                            parent_item.setIcon(0, to_be_copied_item.icon(0))

                            # Remove the child item
                            # Remove file from widget if it doesn't exist
                            parent_item.takeChild(0)
                            # Remove file from duplicated sub list
                            self.duplicated_dict[prove_file].remove(matched_sub_list[0])

                            # Remove the removed parent from form the lists
                            parent_items_without_deleted_files[
                                parent_items_without_deleted_files.index(prove_file)] = matched_sub_list[0]
                            self.duplicated_dict[matched_sub_list[0]] = self.duplicated_dict[prove_file]
                            del self.duplicated_dict[prove_file]

                        else:
                            # Remove the item from the UI
                            self.get_listbox().takeTopLevelItem(parent_items_without_deleted_files.index(prove_file))
                            # Remove it form the internal lists
                            del self.duplicated_dict[prove_file]
                            parent_items_without_deleted_files.remove(prove_file)
            else:
                # Should never be reached
                logging.fatal(f"Reloading files isn't supported in {self.window}")
                raise NotImplementedError

            # Update internal list
            self.matched_list = parent_items_without_deleted_files.copy()

            # UI
            if self.window == "search":
                self.file_count_text.setText(f"Files found: {len(self.matched_list)}")
            # In duplicated
            else:
                self.file_count_text.setText(f"Duplicated files: {len(self.matched_list)}")
            self.file_count_text.update()

            # Debug
            if self.window == "duplicated":
                logging.info(f"Reloaded duplicates files and removed {removed_files_count} deleted or not "
                             "anymore duplicated files"
                             f" in {round(perf_counter() - time_before_reload, 3)} sec.")
                FF_Additional_UI.PopUps.show_info_messagebox(
                    "Reloaded!",
                    f"Reloaded duplicates files and removed {removed_files_count} deleted or"
                    " not anymore duplicated files"
                    f" in {round(perf_counter() - time_before_reload, 3)} sec.",
                    self.parent)
            elif self.window == "search":
                logging.info(f"Reloaded found files and removed {removed_files_count} deleted files in"
                             f" {round(perf_counter() - time_before_reload, 3)} sec.")
                FF_Additional_UI.PopUps.show_info_messagebox(
                    "Reloaded!",
                    f"Reloaded found files and removed {removed_files_count} deleted files in"
                    f" {round(perf_counter() - time_before_reload, 3)} sec.",
                    self.parent)

            # If all files were removed
            if not parent_items_without_deleted_files:
                if self.window == "duplicated":
                    empty_tree_item = QTreeWidgetItem(self.listbox)
                    empty_tree_item.setText(0, "No duplicated file of directory found")
                    self.listbox.setDisabled(True)
                # In normal searching mode
                else:
                    self.listbox.setDisabled(True)
                    self.listbox.addItem("No file of directory found")

            def modify_cache():
                # Loading cache to update it
                with open(self.cache_file_path) as search_file:
                    cached_file: dict[str: list, str: dict] = load(search_file)

                # Testing if the cache file from the specified directory was used as to also update the used cache
                if self.cache_file_path != FF_Files.path_to_cache_file(self.search_path, self.search_depth):

                    different_cache_file = True
                    # Loading cache to update it
                    with open(FF_Files.path_to_cache_file(self.search_path, self.search_depth)) as upper_search_file:
                        cached_home_file: dict[str: list, str: dict] = load(upper_search_file)
                else:
                    different_cache_file = False

                # Removing all deleted files from cache
                for removed_file in removed_list:
                    try:
                        cached_file["found_path_set"].remove(removed_file)
                        if different_cache_file:
                            cached_home_file["found_path_set"].remove(removed_file)
                    except (KeyError, ValueError):
                        # File was already removed from cache
                        pass

                with open(FF_Files.path_to_cache_file(self.search_path, self.search_depth), "w") as search_file:
                    dump(cached_file, search_file)

                # Loading the cache file from the higher directory
                if different_cache_file:
                    with open(self.cache_file_path, "w") as upper_search_file:
                        dump(cached_home_file, upper_search_file)

                # Run garbage collection
                gc.collect()

            QThreadPool(self.parent).start(modify_cache)

        except FileNotFoundError:
            FF_Additional_UI.PopUps.show_info_messagebox("Cache File not Found!",
                                                         "Cache File was deleted, couldn't Update Cache!",
                                                         self.parent)

    def create_context_menu(self, button, actions: tuple):
        # Menu when Right-clicking
        context_menu = QMenu(self.parent)
        for action in actions:
            context_menu.addAction(action)
        # Context Menu
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda point: context_menu.exec(button.mapToGlobal(point)))

    # Function to automate and unify the creation of buttons
    def generate_button(self, text, command, icon=None):
        # Define the Button
        button = QPushButton(self.parent)
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

    # Load marked files form previous search
    def mark_marked_files(self, to_be_marked_files=None):
        # Lad the list from the previous search
        if to_be_marked_files is not None:
            for marked_file in to_be_marked_files:
                self.mark_file(FF_Files.GREEN_LIGHT_THEME_COLOR, marked_file)

        # If the search is from a loaded file
        if self.search_path.endswith(".FFSearch"):
            with open(self.search_path) as load_file:
                logging.debug("Loading marked files from file")
                self.marked_files = set(load(load_file)["marked_files"])
            for marked_file in self.marked_files:
                self.mark_file(FF_Files.GREEN_LIGHT_THEME_COLOR, marked_file)

        # Check the second search
        if self.window == "compare" and self.search_path2.endswith(".FFSearch"):
            with open(self.search_path2) as load_file:
                logging.debug("Loading marked files from second search file")
                self.marked_files = set(load(load_file)["marked_files"])
            for marked_file in self.marked_files:
                self.mark_file(FF_Files.GREEN_LIGHT_THEME_COLOR, marked_file)
