# This File is a part of File-Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the class for the Search Results window

# Imports
import os
from pickle import dump, load
from time import time, ctime

# PyQt6 Gui Imports
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, \
    QListWidget
from pyperclip import copy

# Projects Libraries
import FF_Additional_UI
import FF_Files


class Search_Window:
    def __init__(self, time_total, time_searching, time_indexing, time_sorting, matched_list, search_path, parent):
        time_before_building = time()

        # Window setup
        # Define the window
        search_result_ui = QMainWindow(parent)
        # Set the Title of the Window
        search_result_ui.setWindowTitle(f"File-Find Search Results | {search_path}")
        # Set the Size of the Window and make it not resizable
        search_result_ui.setFixedHeight(700)
        search_result_ui.setFixedWidth(800)

        # Display the Window
        search_result_ui.show()

        # File-Find Label
        # Define the Label
        main_label = QLabel("Search Results", parent=search_result_ui)
        # Change Font
        main_label.setFont(QFont("Baloo Bhaina", 70))
        # Display the Label
        main_label.move(0, -20)
        main_label.show()
        main_label.adjustSize()

        # Seconds needed Label
        seconds_text = QLabel(search_result_ui)
        seconds_text.setFont(QFont("Baloo Bhaina", 20))
        seconds_text.show()
        seconds_text.move(10, 90)

        # Files found label
        objects_text = QLabel(search_result_ui)
        objects_text.setText(f"Files found: {len(matched_list)}")
        objects_text.setFont(QFont("Baloo Bhaina", 20))
        objects_text.show()
        objects_text.move(420, 90)
        objects_text.adjustSize()

        # Timestamp
        timestamp_text = QLabel(search_result_ui)
        timestamp_text.setText(f"Timestamp: {ctime(time())}")
        timestamp_text.setFont(QFont("Arial", 10))
        timestamp_text.show()
        timestamp_text.move(10, 680)
        timestamp_text.adjustSize()

        # Listbox
        result_listbox = QListWidget(search_result_ui)
        # Resize the List-widget
        result_listbox.resize(781, 491)
        # Place
        result_listbox.move(10, 140)
        # Connect the Listbox
        result_listbox.show()

        # Options for paths
        def open_with_program():
            selected_file = result_listbox.currentItem().text()
            if os.system("open " + str(selected_file.replace(" ", "\\ "))) != 0:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", f"No Program found to open {selected_file}",
                                                              search_result_ui)
            print(f"Opened: {selected_file}")

        def open_in_finder():
            selected_file = result_listbox.currentItem().text()

            if os.system("open -R " + str(selected_file.replace(" ", "\\ "))) != 0:
                FF_Additional_UI.msg.show_critical_messagebox("Error!", f"File not Found {selected_file}",
                                                              search_result_ui)
            print(f"Opened in Finder: {selected_file}")

        def copy_path():
            selected_file = result_listbox.currentItem().text()
            copy(selected_file)
            print(f"Copied Path: {selected_file}")
            FF_Additional_UI.msg.show_info_messagebox("Successfully copied!",
                                                      f"Successfully copied Path:\n{selected_file}!",
                                                      search_result_ui)

        def copy_name():
            selected_file = result_listbox.currentItem().text()
            copy(os.path.basename(selected_file))
            print(f"Copied File-Name: {os.path.basename(selected_file)}")
            FF_Additional_UI.msg.show_info_messagebox("Successfully copied!",
                                                      f"Successfully copied File Name:"
                                                      f"\n{os.path.basename(selected_file)} !",
                                                      search_result_ui)

        # Show more time info's
        def show_time_stats():
            FF_Additional_UI.msg.show_info_messagebox("Time Stats",
                                                      f"Time needed:\n\nScanning: {round(time_searching, 3)}\nIndexing:"
                                                      f" {round(time_indexing, 3)}\nSorting:"
                                                      f" {round(time_sorting, 3)}\nCreating UI: "
                                                      f"{round(time_building, 3)}\n---------\nTotal: "
                                                      f"{round(time_total + time_building, 3)}", search_result_ui)

        # Reloads File, check all collected files, if they still exist
        def reload_files():
            print("Reload...")
            time_before_reload = time()
            removed_list = []
            for matched_file in matched_list:
                if os.path.exists(matched_file):
                    continue
                else:
                    result_listbox.takeItem(matched_list.index(matched_file) + 1)
                    matched_list.remove(matched_file)
                    print(f"File Does Not exist: {matched_file}")
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
            print(f"Reloaded found Files and removed {len(removed_list)} in"
                  f" {round(time() - time_before_reload, 3)} sec.")
            FF_Additional_UI.msg.show_info_messagebox("Reloaded!",
                                                      f"Reloaded found Files and removed {len(removed_list)}"
                                                      f" in {round(time() - time_before_reload, 3)} sec.",
                                                      search_result_ui)
            objects_text.setText(f"Files found: {len(matched_list)}")
            objects_text.adjustSize()
            del cached_files, removed_list

        # Save Search
        def save_search():
            save_dialog = QFileDialog.getSaveFileName(search_result_ui, "Export File-Find Search",
                                                      FF_Files.Saved_SearchFolder,
                                                      "File-Find Search (*.FFSave);;Plain Text File (*.txt)")
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
            button = QPushButton(search_result_ui)
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
        show_in_finder = generate_button("Show in Finder", open_in_finder)
        show_in_finder.move(10, 650)

        # Button to open the File
        open_file = generate_button("Open", open_with_program)
        open_file.move(210, 650)

        # Button to copy the File path to the clipboard using pyperclip
        clipboard_path = generate_button("Copy Path to clipboard", copy_path)
        clipboard_path.move(360, 650)

        # Button to copy the File name to the clipboard using pyperclip
        clipboard_file = generate_button("Copy File Name to clipboard", copy_name)
        clipboard_file.move(570, 650)

        # Help Button
        help_button = generate_button(" Help", command=lambda: FF_Additional_UI.Help_Window(parent))
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
        show_time.move(230, 85)

        # Reload Button
        reload_button = generate_button("Reload", reload_files)
        reload_button.move(640, 90)

        # Save Button
        save_button = generate_button("Save", save_search)
        save_button.move(720, 90)

        # Adding every object from matched_list to result_listbox
        for file in matched_list:
            result_listbox.addItem(file)

        # On double-click
        result_listbox.itemDoubleClicked.connect(lambda: self.onclick(result_listbox.currentItem().text(),
                                                                      search_result_ui))

        # Update Seconds needed Label
        seconds_text.setText(f"Time needed: {round(time_total + (time() - time_before_building), 3)}")
        seconds_text.adjustSize()

        # Time building UI
        time_building = time() - time_before_building
        print("Time spent building the UI:", time_building)

    @staticmethod
    def onclick(file, parent):
        FF_Additional_UI.msg.show_info_messagebox(f"Information about: {file}",
                                                  f"File Info:\n"
                                                  f"\n\n"
                                                  f"Path: {file}\n"
                                                  f"\n"
                                                  f"File Name: {os.path.basename(file)}\n"
                                                  f"Size: {os.path.getsize(file)} Bytes\n"
                                                  f"Date Created: {ctime(os.stat(file).st_birthtime)}\n"
                                                  f"Date Modified: {ctime(os.path.getmtime(file))}\n", parent)
