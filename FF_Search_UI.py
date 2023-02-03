# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2023 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the search-results window

# Imports
import hashlib
import logging
import os
from pickle import dump, load
from threading import Thread
from time import perf_counter, ctime, time

# PyQt6 Gui Imports
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, \
    QListWidget, QMenuBar, QVBoxLayout, QHBoxLayout, QWidget

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Help_UI
import FF_Main_UI
import FF_Search


class Search_Window:
    def __init__(self, time_total, time_searching, time_indexing, time_sorting, matched_list, search_path, parent):
        logging.info("Setting up Search UI...")

        # Saves Time
        time_before_building = perf_counter()

        # Window setup
        # Define the window
        self.Search_Results_Window = QMainWindow(parent)
        # Set the Title of the Window
        self.Search_Results_Window.setWindowTitle(f"File Find Search Results | {search_path}")
        # Set the Size of the Window and make it not resizable
        self.Search_Results_Window.setFixedHeight(700)
        self.Search_Results_Window.setFixedWidth(800)
        # Display the Window
        self.Search_Results_Window.show()

        # DON'T TRY TO USE LAYOUTS! YOU ARE JUST GOING TO END UP WASTING YOUR TIME!
        # If used File Find crashes with a 'Memory Error' and no further information.
        # I wasted several hours, trying to fix this.
        # These undefined errors with QT are the worst

        # Seconds needed Label
        seconds_text = QLabel(self.Search_Results_Window)
        # Setting a Font
        small_text_font = QFont("Futura", 20)
        small_text_font.setBold(True)
        seconds_text.setFont(small_text_font)
        # Displaying
        seconds_text.show()
        seconds_text.move(10, 20)

        # Files found label
        objects_text = QLabel(self.Search_Results_Window)
        objects_text.setText(f"Files found: {len(matched_list)}")
        objects_text.setFont(small_text_font)
        objects_text.show()
        objects_text.move(420, 20)
        objects_text.adjustSize()

        # Timestamp
        timestamp_text = QLabel(self.Search_Results_Window)
        timestamp_text.setText(f"Timestamp: {ctime(time())}")
        timestamp_text.setFont(QFont("Arial", 10))
        timestamp_text.show()
        timestamp_text.move(10, 680)
        timestamp_text.adjustSize()

        # Listbox
        self.result_listbox = QListWidget(self.Search_Results_Window)
        # Resize the List-widget
        self.result_listbox.resize(781, 570)
        # Place
        self.result_listbox.move(10, 70)
        # Connect the Listbox
        self.result_listbox.show()

        # Show more time info's
        def show_time_stats():
            FF_Additional_UI.msg.show_info_messagebox("Time Stats",
                                                      f"Time needed:\n\nScanning: {round(time_searching, 3)}\nIndexing:"
                                                      f" {round(time_indexing, 3)}\nSorting:"
                                                      f" {round(time_sorting, 3)}\nCreating UI: "
                                                      f"{round(time_building, 3)}\n---------\nTotal: "
                                                      f"{round(time_total + time_building, 3)}",
                                                      self.Search_Results_Window)

        # Reloads File, check all collected files, if they still exist
        def reload_files():
            try:
                logging.info("Reload...")
                time_before_reload = perf_counter()
                removed_list = []
                for matched_file in matched_list:
                    if os.path.exists(matched_file):
                        continue
                    else:
                        self.result_listbox.takeItem(matched_list.index(matched_file) + 1)
                        matched_list.remove(matched_file)
                        logging.debug(f"File Does Not exist: {matched_file}")
                        removed_list.append(matched_file)
                with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, search_path.replace("/", "-") + ".FFCache"),
                          "rb") as SearchFile:
                    cached_files = list(load(SearchFile))
                for cached_file in cached_files:
                    if cached_file in removed_list:
                        cached_files.remove(cached_file)
                with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, search_path.replace("/", "-") + ".FFCache"),
                          "wb") as SearchFile:
                    dump(cached_files, SearchFile)
                logging.info(f"Reloaded found Files and removed {len(removed_list)} in"
                             f" {round(perf_counter() - time_before_reload, 3)} sec.")
                FF_Additional_UI.msg.show_info_messagebox("Reloaded!",
                                                          f"Reloaded found Files and removed {len(removed_list)}"
                                                          f" in {round(perf_counter() - time_before_reload, 3)} sec.",
                                                          self.Search_Results_Window)
                objects_text.setText(f"Files found: {len(matched_list)}")
                objects_text.adjustSize()
                del cached_files, removed_list
            except FileNotFoundError:
                FF_Additional_UI.msg.show_info_messagebox("Cache File not Found!",
                                                          "Cache File was deleted, couldn't Update Cache!",
                                                          self.Search_Results_Window)

        # Save Search
        def save_search():
            save_dialog = QFileDialog.getSaveFileName(self.Search_Results_Window, "Export File Find Search",
                                                      FF_Files.SAVED_SEARCHES_FOLDER,
                                                      "File Find Search (*.FFSave);;Plain Text File (*.txt)")
            save_file = save_dialog[0]
            if save_file.endswith(".txt") and not os.path.exists(save_file):
                with open(save_file, "w") as ExportFile:
                    for save_file in matched_list:
                        ExportFile.write(save_file + "\n")
            elif save_file.endswith(".FFSave") and not os.path.exists(save_file):
                with open(save_file, "wb") as ExportFile:
                    dump(matched_list, ExportFile)

        # Buttons
        # Functions to automate Button
        def generate_button(text, command):
            # Define the Button
            button = QPushButton(self.Search_Results_Window)
            # Change the Text
            button.setText(text)
            # Set the command
            button.clicked.connect(command)
            # Display the Button correctly
            button.show()
            button.adjustSize()
            # Return the value of the Button, to move the Button
            return button

        # Button to open the File in Finder
        show_in_finder = generate_button("Show in Finder", self.open_in_finder)
        show_in_finder.move(10, 650)

        # Button to open the File
        open_file = generate_button("Open", self.open_with_program)
        open_file.move(170, 650)

        # Button to open File Info
        file_info_button = generate_button("Info", self.file_info)
        file_info_button.move(580, 650)

        # Button to open view the hashes of the File
        file_hash = generate_button("File Hashes", self.view_hashes)
        file_hash.move(680, 650)

        # Time stat Button
        show_time = generate_button(None, show_time_stats, )
        # Icon
        show_time.setIcon(QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Time_button_img_small.png")))
        show_time.setIconSize(QSize(23, 23))
        # Place
        show_time.resize(50, 40)
        show_time.move(260, 15)

        # Reload Button
        reload_button = generate_button("Reload", reload_files)
        reload_button.move(640, 20)

        # Save Button
        save_button = generate_button("Save", save_search)
        save_button.move(720, 20)

        # Adding every object from matched_list to self.result_listbox
        logging.debug("Adding Files to Listbox")
        for list_file in matched_list:
            self.result_listbox.addItem(list_file)
        # Setting the row
        self.result_listbox.setCurrentRow(0)

        # On double-click
        self.result_listbox.itemDoubleClicked.connect(self.open_in_finder)

        # Update search-results-ui
        logging.debug("Updating search_results_ui...")
        self.Search_Results_Window.hide()
        self.Search_Results_Window.show()

        # Update Seconds needed Label
        seconds_text.setText(f"Time needed: {round(time_total + (perf_counter() - time_before_building), 3)}")
        seconds_text.adjustSize()

        # Building Menubar
        self.menubar(save_search, reload_files)

        # Debug
        logging.info("Finished Setting up Search UI")

        # Time building UI
        time_building = perf_counter() - time_before_building
        logging.info(f"\nSeconds needed:\nScanning: {time_searching}\nIndexing: {time_indexing}\nSorting: "
                     f"{time_sorting}\nBuilding UI: {time_building}\nTotal: {time_total + time_building}")

        # Push Notification
        FF_Main_UI.menubar_icon.showMessage("File Find - Search finished!", f"Your Search finished!\nin {search_path}",
                                            QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Find_button_img_small.png")),
                                            100000)

        logging.debug("Finished Building")

    def menubar(self, save_search, reload_files):
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

        # Load Search
        load_search_action = QAction("&Open Search", self.Search_Results_Window)
        load_search_action.triggered.connect(lambda: FF_Search.load_search(self.Search_Results_Window))
        load_search_action.setShortcut("Alt+O")
        file_menu.addAction(load_search_action)

        # Clear Cache
        cache_action = QAction("&Clear Cache", self.Search_Results_Window)
        cache_action.triggered.connect(lambda: FF_Files.remove_cache(True, self.Search_Results_Window))
        cache_action.setShortcut("Ctrl+N")
        tools_menu.addAction(cache_action)

        # Reload and Remove Deleted Files
        reload_action = QAction("&Reload and Remove Deleted Files", self.Search_Results_Window)
        reload_action.triggered.connect(reload_files)
        reload_action.setShortcut("Ctrl+R")
        tools_menu.addAction(reload_action)

        # Open File Action
        open_action = QAction("&Open Selected File", self.Search_Results_Window)
        open_action.triggered.connect(self.open_with_program)
        open_action.setShortcut("Ctrl+O")
        tools_menu.addAction(open_action)

        # Show File in Finder Action
        show_action = QAction("&Show Selected File in Finder", self.Search_Results_Window)
        show_action.triggered.connect(self.open_in_finder)
        show_action.setShortcut("Ctrl+Shift+O")
        tools_menu.addAction(show_action)

        # File Info
        info_action = QAction("&Info for Selected File", self.Search_Results_Window)
        info_action.triggered.connect(self.file_info)
        info_action.setShortcut("Ctrl+I")
        tools_menu.addAction(info_action)

        # View File Hashes
        hash_action = QAction("&Hashes for Selected File", self.Search_Results_Window)
        hash_action.triggered.connect(self.view_hashes)
        hash_action.setShortcut("Ctrl+Shift+I")
        tools_menu.addAction(hash_action)

        # About File Find
        about_action = QAction("&About File Find", self.Search_Results_Window)
        about_action.triggered.connect(lambda: FF_Help_UI.Help_Window(self.Search_Results_Window))
        help_menu.addAction(about_action)

        # Close Window
        close_action = QAction("&Close Window", self.Search_Results_Window)
        close_action.triggered.connect(self.Search_Results_Window.destroy)
        close_action.setShortcut("Ctrl+W")
        window_menu.addAction(close_action)

        # Help
        help_action = QAction("&File Find Help and Settings", self.Search_Results_Window)
        help_action.triggered.connect(lambda: FF_Help_UI.Help_Window(self.Search_Results_Window))
        help_menu.addAction(help_action)

    # Options for paths
    # Opens a file
    def open_with_program(self):
        try:
            selected_file = self.result_listbox.currentItem().text()
            if os.system("open " + str(selected_file.replace(" ", "\\ "))) != 0:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", f"No Program found to open {selected_file}",
                                                              self.Search_Results_Window)
            else:
                logging.debug(f"Opened: {selected_file}")
        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # Shows a file in finder
    def open_in_finder(self):
        try:
            selected_file = self.result_listbox.currentItem().text()

            if os.system("open -R " + str(selected_file.replace(" ", "\\ "))) != 0:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", f"File not Found {selected_file}",
                                                              self.Search_Results_Window)
            else:
                logging.debug(f"Opened in Finder: {selected_file}")
        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

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

                FF_Additional_UI.msg.show_info_messagebox(f"Information about: {file}",
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
                FF_Additional_UI.msg.show_critical_messagebox("File Not Found!", "File does not exist!\nReload!",
                                                              self.Search_Results_Window)
        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)

    # View the hashes
    def view_hashes(self):
        try:
            # Collecting Files
            hash_file = self.result_listbox.currentItem().text()
            logging.info(f"Collecting {hash_file}...")
            if os.path.isdir(hash_file):
                file_content = b""
                for root, dirs, files in os.walk(hash_file):
                    for i in files:
                        try:
                            with open(os.path.join(root, i), "rb") as HashFile:
                                file_content = HashFile.read() + file_content
                        except FileNotFoundError:
                            logging.error(f"{HashFile} does not exist!")

            else:
                try:
                    with open(hash_file, "rb") as HashFile:
                        file_content = HashFile.read()
                except FileNotFoundError:
                    logging.error(f"{HashFile} does not exist!")
                    FF_Additional_UI.msg.show_critical_messagebox("File not found! ", f"{HashFile} does not exist!",
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
            FF_Additional_UI.msg.show_info_messagebox(f"Hashes of {hash_file}",
                                                      f"Hashes of {hash_file}:\n\n"
                                                      f"MD5:\n {md5_hash}\n\n"
                                                      f"SHA1:\n {sha1_hash}\n\n"
                                                      f"SHA265:\n {sha256_hash}\n\n\n"
                                                      f"Took: {round(final_time, 3)} sec.",
                                                      self.Search_Results_Window)

        except AttributeError:
            FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.Search_Results_Window)
            logging.error("Error! Select a File!")
