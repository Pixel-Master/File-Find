# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the class for the Search Results window

# Imports
import os
from pickle import dump, load
from time import time, ctime
import hashlib
import logging

# PyQt6 Gui Imports
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, \
    QListWidget

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Help_UI
import FF_Main_UI


class Search_Status:
    def __init__(self, parent):
        # Define the Label
        self.report_label = QLabel("Starting Search...", parent=parent)
        # Change Font
        label_font = QFont("Futura", 15)
        label_font.setBold(True)
        self.report_label.setFont(label_font)
        # Display the Label
        self.report_label.move(200, 0)
        self.report_label.show()
        self.report_label.adjustSize()


class Search_Window:
    def __init__(self, time_total, time_searching, time_indexing, time_sorting, matched_list, search_path, parent):
        logging.info("Setting up Search UI...")

        # Saves Time
        time_before_building = time()

        # Window setup
        # Define the window
        self.search_result_ui = QMainWindow(parent)
        # Set the Title of the Window
        self.search_result_ui.setWindowTitle(f"File Find Search Results | {search_path}")
        # Set the Size of the Window and make it not resizable
        self.search_result_ui.setFixedHeight(700)
        self.search_result_ui.setFixedWidth(800)

        # Display the Window
        self.search_result_ui.show()

        # Search Results Label
        # Define the Label
        main_label = QLabel("Search Results", parent=self.search_result_ui)
        # Change Font
        main_label_font = QFont("Futura", 50)
        main_label_font.setBold(True)
        main_label.setFont(main_label_font)
        # Display the Label
        main_label.move(0, 0)
        main_label.show()
        main_label.adjustSize()

        # Seconds needed Label
        seconds_text = QLabel(self.search_result_ui)
        small_text_font = QFont("Futura", 20)
        small_text_font.setBold(True)
        seconds_text.setFont(small_text_font)
        seconds_text.show()
        seconds_text.move(10, 90)

        # Files found label
        objects_text = QLabel(self.search_result_ui)
        objects_text.setText(f"Files found: {len(matched_list)}")
        objects_text.setFont(small_text_font)
        objects_text.show()
        objects_text.move(420, 90)
        objects_text.adjustSize()

        # Timestamp
        timestamp_text = QLabel(self.search_result_ui)
        timestamp_text.setText(f"Timestamp: {ctime(time())}")
        timestamp_text.setFont(QFont("Arial", 10))
        timestamp_text.show()
        timestamp_text.move(10, 680)
        timestamp_text.adjustSize()

        # Listbox
        result_listbox = QListWidget(self.search_result_ui)
        # Resize the List-widget
        result_listbox.resize(781, 491)
        # Place
        result_listbox.move(10, 140)
        # Connect the Listbox
        result_listbox.show()

        # Options for paths
        # Opens a file
        def open_with_program():
            try:
                selected_file = result_listbox.currentItem().text()
                if os.system("open " + str(selected_file.replace(" ", "\\ "))) != 0:
                    FF_Additional_UI.msg.show_critical_messagebox("Error!", f"No Program found to open {selected_file}",
                                                                  self.search_result_ui)
                else:
                    logging.debug(f"Opened: {selected_file}")
            except AttributeError:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.search_result_ui)

        # Reveals a file
        def open_in_finder():
            try:
                selected_file = result_listbox.currentItem().text()

                if os.system("open -R " + str(selected_file.replace(" ", "\\ "))) != 0:
                    FF_Additional_UI.msg.show_critical_messagebox("Error!", f"File not Found {selected_file}",
                                                                  self.search_result_ui)
                else:
                    logging.debug(f"Opened in Finder: {selected_file}")
            except AttributeError:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.search_result_ui)

        # Get basic information about a file
        def file_info():
            try:
                self.onclick(result_listbox.currentItem().text(), self.search_result_ui)
            except AttributeError:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.search_result_ui)

        # View the hashes
        def view_hashes():
            try:
                # Collecting FInes
                hash_file = result_listbox.currentItem().text()
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
                        FF_Additional_UI.msg.show_critical_messagebox(f"{HashFile} does not exist!")
                        file_content = 0

                # Computing Hashes
                logging.info(f"Computing Hashes of {hash_file}...")

                # md5 Hash
                logging.debug("Computing md5 Hash...")
                md5_hash = hashlib.md5(file_content)
                logging.debug(f"{md5_hash.hexdigest() = }")

                # sha1 Hash
                logging.debug("Computing sha1 Hash...")
                sha1_hash = hashlib.sha1(file_content)
                logging.debug(f"{sha1_hash.hexdigest() = }")

                # sha265 Hash
                logging.debug("Computing sha265 Hash...")
                sha265_hash = hashlib.sha256(file_content)
                logging.debug(f"{sha265_hash.hexdigest() = }")

                # Give Feedback
                FF_Additional_UI.msg.show_info_messagebox(f"Hashes of {hash_file}",
                                                          f"Hashes of {hash_file}:\n\n"
                                                          f"MD5: {md5_hash.hexdigest()}\n"
                                                          f"SHA1: {sha1_hash.hexdigest()}\n"
                                                          f"SHA265: {sha265_hash.hexdigest()}",
                                                          self.search_result_ui)

            except AttributeError:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", "Select a File!", self.search_result_ui)
                logging.error("Error! Select a File!")

        # Show more time info's
        def show_time_stats():
            FF_Additional_UI.msg.show_info_messagebox("Time Stats",
                                                      f"Time needed:\n\nScanning: {round(time_searching, 3)}\nIndexing:"
                                                      f" {round(time_indexing, 3)}\nSorting:"
                                                      f" {round(time_sorting, 3)}\nCreating UI: "
                                                      f"{round(time_building, 3)}\n---------\nTotal: "
                                                      f"{round(time_total + time_building, 3)}", self.search_result_ui)

        # Reloads File, check all collected files, if they still exist
        def reload_files():
            logging.info("Reload...")
            time_before_reload = time()
            removed_list = []
            for matched_file in matched_list:
                if os.path.exists(matched_file):
                    continue
                else:
                    result_listbox.takeItem(matched_list.index(matched_file) + 1)
                    matched_list.remove(matched_file)
                    logging.debug(f"File Does Not exist: {matched_file}")
                    removed_list.append(matched_file)
            with open(os.path.join(FF_Files.Cached_SearchesFolder, search_path.replace("/", "-") + ".FFSearch"),
                      "rb") as SearchFile:
                cached_files = list(load(SearchFile))
            for cached_file in cached_files:
                if cached_file in removed_list:
                    cached_files.remove(cached_file)
            with open(os.path.join(FF_Files.Cached_SearchesFolder, search_path.replace("/", "-") + ".FFSearch"),
                      "wb") as SearchFile:
                dump(cached_files, SearchFile)
            logging.info(f"Reloaded found Files and removed {len(removed_list)} in"
                         f" {round(time() - time_before_reload, 3)} sec.")
            FF_Additional_UI.msg.show_info_messagebox("Reloaded!",
                                                      f"Reloaded found Files and removed {len(removed_list)}"
                                                      f" in {round(time() - time_before_reload, 3)} sec.",
                                                      self.search_result_ui)
            objects_text.setText(f"Files found: {len(matched_list)}")
            objects_text.adjustSize()
            del cached_files, removed_list

        # Save Search
        def save_search():
            save_dialog = QFileDialog.getSaveFileName(self.search_result_ui, "Export File Find Search",
                                                      FF_Files.Saved_SearchFolder,
                                                      "File Find Search (*.FFSave);;Plain Text File (*.txt)")
            save_file = save_dialog[0]
            if save_file.endswith(".txt") and not os.path.exists(save_file):
                with open(save_file, "w") as ExportFile:
                    for matched_file in matched_list:
                        ExportFile.write(matched_file + "\n")
            elif save_file.endswith(".FFSave") and not os.path.exists(save_file):
                with open(save_file, "wb") as ExportFile:
                    dump(matched_list, ExportFile)

        # Buttons
        # Functions to automate Button
        def generate_button(text, command):
            # Define the Button
            button = QPushButton(self.search_result_ui)
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
        show_in_finder = generate_button("Reveal in Finder", open_in_finder)
        show_in_finder.move(10, 650)

        # Button to open the File
        open_file = generate_button("Open", open_with_program)
        open_file.move(200, 650)

        # Button to open File Info
        file_info_button = generate_button("Info", file_info)
        file_info_button.move(400, 650)

        # Button to open view the hashes of the File
        file_hash = generate_button("File Hashes", view_hashes)
        file_hash.move(600, 650)

        # Help Button
        help_button = generate_button(" Help", command=lambda: FF_Help_UI.Help_Window(parent))
        help_button.move(740, 0)
        help_button_font = QFont("Arial", 25)
        help_button_font.setBold(True)
        help_button.setFont(help_button_font)
        # Color
        help_button.setStyleSheet("color: #b50104;")
        # Icon
        help_button.setIcon(QIcon(os.path.join(FF_Files.AssetsFolder, "Info_button_img_small.png")))
        help_button.setIconSize(QSize(25, 25))
        # Place
        help_button.resize(120, 50)
        help_button.move(670, 10)

        # Time stat Button
        show_time = generate_button(None, show_time_stats, )
        # Icon
        show_time.setIcon(QIcon(os.path.join(FF_Files.AssetsFolder, "Time_button_img_small.png")))
        show_time.setIconSize(QSize(23, 23))
        # Place
        show_time.resize(50, 40)
        show_time.move(260, 85)

        # Reload Button
        reload_button = generate_button("Reload", reload_files)
        reload_button.move(640, 90)

        # Save Button
        save_button = generate_button("Save", save_search)
        save_button.move(720, 90)

        # Adding every object from matched_list to result_listbox
        logging.debug("Adding Files to Listbox")
        for file in matched_list:
            result_listbox.addItem(file)

        # On double-click
        result_listbox.itemDoubleClicked.connect(lambda: self.onclick(result_listbox.currentItem().text(),
                                                                      self.search_result_ui))

        # Update search-results-ui
        logging.debug("Updating search_results_ui...")
        self.search_result_ui.hide()
        self.search_result_ui.show()

        # Update Seconds needed Label
        seconds_text.setText(f"Time needed: {round(time_total + (time() - time_before_building), 3)}")
        seconds_text.adjustSize()

        # Debug
        logging.info("Finished Setting up Search UI")

        # Time building UI
        time_building = time() - time_before_building
        logging.info(f"\nSeconds needed:\nScanning: {time_searching}\nIndexing: {time_indexing}\nSorting: "
                     f"{time_sorting}\nBuilding UI: {time_building}\nTotal: {time_total + time_building}")

        # Push Notification
        FF_Main_UI.menubar_icon.showMessage("File Find - Search finished!", f"Your Search finished!\nin {search_path}",
                                            QIcon(os.path.join(FF_Files.AssetsFolder, "Find_button_img_small.png")),
                                            100000)

    @staticmethod
    def onclick(file, parent):
        # Debug
        logging.debug("Called File Info")
        try:
            FF_Additional_UI.msg.show_info_messagebox(f"Information about: {file}",
                                                      f"File Info:\n"
                                                      f"\n\n"
                                                      f"Path: {file}\n"
                                                      f"\n"
                                                      f"File Name: {os.path.basename(file)}\n"
                                                      f"Size: {FF_Files.conv_file_size(FF_Files.get_file_size(file))}\n"
                                                      f"Date Created: {ctime(os.stat(file).st_birthtime)}\n"
                                                      f"Date Modified: {ctime(os.path.getmtime(file))}\n", parent)
        except FileNotFoundError:
            logging.error(f"{file} does not Exist!")
            FF_Additional_UI.msg.show_critical_messagebox("File Not Found!", "File does not exist!\nReload!", parent)
