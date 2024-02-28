# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the search-results window

# Imports
import logging
import os
from json import dump, load
from sys import platform
from time import perf_counter, ctime, time

# PySide6 Gui Imports
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, \
    QListWidget, QMenu, QWidget, QGridLayout, QHBoxLayout

# Projects Libraries
import FF_Additional_UI
import FF_Compare
import FF_Duplicated
import FF_Files
import FF_Main_UI
import FF_Menubar


class SearchWindow:
    def __init__(self, time_dict, matched_list, search_path, parent):
        # Debug
        logging.info("Setting up Search UI...")

        # Setting search_path to a local variable
        self.search_path = search_path

        # Saves Time
        time_dict["time_before_building"] = perf_counter()

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
            # On Windows and Linux
            # (On Linux this currently returns the modification date,
            # because it's impossible to access with pure python)
            if platform == "win32" or platform == 'cygwin' or platform == "linux":
                cache_created_time = ctime(
                    os.path.getctime(
                        os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, search_path.replace("/", "-") + ".FFCache")))

            # On Mac
            elif platform == "darwin":
                cache_created_time = ctime(
                    os.stat(
                        os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                     search_path.replace("/", "-") + ".FFCache")).st_birthtime)
            # If platform is unknown
            else:
                cache_created_time = f"Unrecognised platform: {platform}"
                # Debug
                logging.error(f"Unrecognised platform: {platform}")

            # Modified time
            cache_modified_time = ctime(
                os.path.getmtime(
                    os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, search_path.replace("/", "-") + ".FFCache")))
            search_opened_time = ctime(time())

            # Displaying infobox with time info
            FF_Additional_UI.PopUps.show_info_messagebox(
                "Time Stats",
                f"Time needed:\n"
                f"Scanning: {round(time_dict['time_searching'], 3)}\n"
                f"Indexing: {round(time_dict['time_indexing'], 3)}\n"
                f"Sorting: {round(time_dict['time_sorting'], 3)}\n"
                f"Creating UI: {round(time_dict['time_building'], 3)}\n"
                f"---------\n"
                f"Total: {round(time_dict['time_total'] + time_dict['time_building'], 3)}\n\n\n"
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

        # Building Menubar
        menu_bar = FF_Menubar.MenuBar(
            parent=self.Search_Results_Window,
            listbox=self.result_listbox,
            window="search",
            matched_list=matched_list,
            search_path=search_path,
            reload_files=reload_files,
            save_search=save_search)

        # Debug
        logging.info("Finished Setting up menubar")

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
        # Seperator
        options_menu.addSeparator()
        # Compare Action
        options_menu_compare_action = options_menu.addAction(
            "&Compare to other Search...")
        options_menu_compare_action.triggered.connect(
            lambda: FF_Compare.CompareSearches(matched_list, search_path, self.Search_Results_Window))
        # Seperator
        options_menu.addSeparator()
        # Duplicated Action
        options_menu_duplicated_action = options_menu.addAction(
            "&Find duplicated...")
        options_menu_duplicated_action.triggered.connect(
            lambda: FF_Duplicated.DuplicatedSettings(self.Search_Results_Window, search_path, matched_list))

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
        self.result_listbox.itemDoubleClicked.connect(menu_bar.open_in_finder)

        # Update Seconds needed Label
        seconds_text.setText(
            f"Time needed: {round(time_dict['time_total'] + (perf_counter() - time_dict['time_before_building']), 3)}")
        seconds_text.adjustSize()

        # Time building UI
        time_dict["time_building"] = perf_counter() - time_dict['time_before_building']

        time_dict["time_total"] = time_dict["time_total"] + time_dict["time_building"]

        logging.info(f"\nSeconds needed:\n"
                     f"Scanning: {time_dict['time_searching']}\n"
                     f"Indexing: {time_dict['time_indexing']}\n"
                     f"Sorting: {time_dict['time_sorting']}\n"
                     f"Building UI: {time_dict['time_building']}\n"
                     f"Total: {time_dict['time_total']}")

        # Push Notification
        FF_Main_UI.menubar_icon.showMessage("File Find - Search finished!", f"Your Search finished!\nin {search_path}",
                                            QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Find_button_img_small.png")),
                                            100000)
        # Updated Search indicator
        FF_Main_UI.MainWindow.update_search_status_label()

        logging.info("Finished Building Search-Results-UI!\n")
