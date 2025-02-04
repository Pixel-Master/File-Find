# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the search-results window

# Imports
import logging
import os
from json import dump, load
from time import perf_counter, ctime, time

# PySide6 Gui Imports
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QFileDialog, \
    QListWidget, QMenu, QWidget, QGridLayout, QHBoxLayout, QScrollArea

# Projects Libraries
import FF_Additional_UI
import FF_Compare
import FF_Duplicated
import FF_Files
import FF_Main_UI
import FF_Menubar


class SearchWindow:
    def __init__(self, time_dict, matched_list, search_path, cache_file_path, parent):
        # Debug
        logging.info("Setting up Search UI...")

        # Setting search_path and matched_list to a local variable
        self.search_path = search_path
        self.matched_list = matched_list.copy()
        del matched_list

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
        self.Search_Results_Layout.addLayout(self.Bottom_Layout, 10, 0, 1, 6)
        # DON'T TRY TO USE LAYOUTS! YOU ARE JUST GOING TO END UP WASTING YOUR TIME!
        # If used File Find crashes with a 'Memory Error' and no further information.
        # I wasted several hours, trying to fix this.
        # Btw, You can fix it with disabling Pythons garbage collection.

        # Seconds needed Label
        seconds_text = QLabel(self.Search_Results_Window)
        # Setting a Font
        small_text_font = QFont(FF_Files.DEFAULT_FONT, FF_Files.NORMAL_FONT_SIZE)
        small_text_font.setBold(True)
        seconds_text.setFont(small_text_font)
        # Displaying
        self.Search_Results_Layout.addWidget(seconds_text, 0, 0)

        # Files found label
        objects_text = QLabel(self.Search_Results_Window)
        objects_text.setText(f"Files found: {len(self.matched_list)}")
        objects_text.setFont(small_text_font)
        # Displaying
        self.Search_Results_Layout.addWidget(objects_text, 0, 2)

        '''Creating a QScrollArea in which the QListWidget is put. This is because QListWidget.setUniformItemSizes(True)
        allows for insane speed gains (up to 100x), but it makes all item the same size (if they are too long it will
        cut them of) so to profit from the speed gains but at the same time not cutting of the file paths, the
         QListWidget (takes care of vertical scrolling)
        is put into a QScrollArea, which takes care of the horizontal scrolling.'''
        self.result_area = QScrollArea(self.Search_Results_Window)
        # List widget for displaying all found files
        self.result_listbox = QListWidget(self.Search_Results_Window)
        # Place
        self.Search_Results_Layout.addWidget(self.result_area, 1, 0, 9, 6)
        # Place the Listbox in the area
        self.result_area.setWidget(self.result_listbox)

        # Store the time
        self.search_opened_time = time()

        # Show more time info's
        def show_time_stats():
            # Debug
            logging.debug("Displaying time stats.")

            # Getting the creation time of the cache file which is stored separately
            with open(FF_Files.get_metadata_file_from_cache_file(cache_file_path)) as time_file:
                # Load time
                cache_created_time = ctime(load(time_file)["c_time"])

            search_opened_time = ctime(self.search_opened_time)

            # Displaying infobox with time info
            FF_Additional_UI.PopUps.show_info_messagebox(
                "Time Stats",
                "Time needed:\n"
                f"Scanning: {round(time_dict['time_searching'], 3)}s\n"
                f"Indexing: {round(time_dict['time_indexing'], 3)}s\n"
                f"Sorting: {round(time_dict['time_sorting'], 3)}s\n"
                f"Creating UI: {round(time_dict['time_building'], 3)}s\n"
                "---------\n"
                f"Total: {round(time_dict['time_total'] + time_dict['time_building'], 3)}s\n\n\n"
                ""
                "Timestamps:\n"
                f"Cache (basis for search results) created:\n{cache_created_time}\n"
                f"Search opened:\n{search_opened_time}",
                self.Search_Results_Window, large=True)

        # Save Search
        def save_search():
            save_dialog = QFileDialog.getSaveFileName(self.Search_Results_Window, "Export File Find Search",
                                                      FF_Files.USER_FOLDER,
                                                      "File Find Search (*.FFSearch);;Plain Text File (*.txt)")
            # Normalize the path and selecting the first item, because it's the path
            save_file = os.path.normpath(save_dialog[0])

            # If the suffix wasn't added, add it
            if not (save_file.endswith(".FFSearch") or save_file.endswith(".txt")):
                if "FFFilter" in save_dialog[1]:
                    save_file += ".FFFilter"
                else:
                    save_file += ".json"

            if save_file.endswith(".txt") and not os.path.exists(save_file):
                with open(save_file, "w") as export_file:
                    for save_file in self.matched_list:
                        export_file.write(save_file + "\n")
            elif save_file.endswith(".FSearch") and not os.path.exists(save_file):
                with open(save_file, "w") as export_file:
                    dump({"VERSION": FF_Files.FF_SEARCH_VERSION, "matched_list": self.matched_list}, export_file)

        # Building Menu-bar
        menu_bar = FF_Menubar.MenuBar(
            parent=self.Search_Results_Window,
            listbox=self.result_listbox,
            window="search",
            matched_list=self.matched_list,
            search_path=search_path,
            file_count_text=objects_text,
            save_search=save_search,
            cache_file_path=cache_file_path)

        # Debug
        logging.info("Finished Setting up menu-bar")

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
                FF_Additional_UI.UIIcon(icon, button.setIcon)
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
        # Tooltip
        show_time.setToolTip("Show time stats and time stamps..")
        # Add to Layout
        self.Search_Results_Layout.addWidget(show_time, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        # More Options
        # Options Menu
        options_menu = QMenu(self.Search_Results_Window)

        # Reload Action
        options_menu_reload_action = options_menu.addAction("&Reload")
        options_menu_reload_action.triggered.connect(menu_bar.reload_files)
        # Save Action
        options_menu_save_action = options_menu.addAction("&Save Search")
        options_menu_save_action.triggered.connect(save_search)
        # Separator
        options_menu.addSeparator()
        # Compare Action
        options_menu_compare_action = options_menu.addAction(
            "&Compare to other Search...")
        options_menu_compare_action.triggered.connect(
            lambda: FF_Compare.CompareSearches(self.matched_list, search_path, cache_file_path,
                                               self.Search_Results_Window))
        # Separator
        options_menu.addSeparator()
        # Duplicated Action
        options_menu_duplicated_action = options_menu.addAction(
            "&Find duplicated...")
        options_menu_duplicated_action.triggered.connect(
            lambda: FF_Duplicated.DuplicatedSettings(self.Search_Results_Window, search_path, self.matched_list,
                                                     cache_file_path))

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
        # Tooltip
        options_button.setToolTip("More options..")
        # Add to Layout
        self.Search_Results_Layout.addWidget(options_button, 0, 5)

        # Compare Button
        compare_button = generate_button(
            None,
            lambda: FF_Compare.CompareSearches(self.matched_list, search_path, cache_file_path,
                                               self.Search_Results_Window),
            icon=os.path.join(FF_Files.ASSETS_FOLDER, "Compare_files_img_small.png"))
        # Icon size
        compare_button.setIconSize(QSize(50, 50))
        # Resize
        compare_button.setMaximumSize(50, 50)
        # Tooltip
        compare_button.setToolTip("Compare this search to an other search..")
        # Add to Layout
        self.Search_Results_Layout.addWidget(compare_button, 0, 3)

        # Duplicated Button
        duplicated_button = generate_button(
            None,
            lambda: FF_Duplicated.DuplicatedSettings(self.Search_Results_Window, search_path, self.matched_list,
                                                     cache_file_path),
            icon=os.path.join(FF_Files.ASSETS_FOLDER, "Duplicated_files_img_small.png"))
        # Icon size
        duplicated_button.setIconSize(QSize(50, 50))
        # Resize
        duplicated_button.setMaximumSize(50, 50)
        # Tooltip
        duplicated_button.setToolTip("Find duplicated files...")
        # Add to Layout
        self.Search_Results_Layout.addWidget(duplicated_button, 0, 4)

        # Adding every object from matched_list to self.result_listview
        logging.debug("Adding Files to Listbox...")
        # If there was no file found and the list is empty
        if not self.matched_list:
            self.result_listbox.setDisabled(True)
            self.result_listbox.addItem("No file of directory found")
        else:
            # If there is at least one file
            self.result_listbox.addItems(self.matched_list)
            # Setting the row to the first
            self.result_listbox.setCurrentRow(0)

        # Improvements for a faster QListWidget
        '''Created a QScrollArea in which the QListWidget was put. This is because QListWidget.setUniformItemSizes(True)
            allows for insane speed gains (up to 100x), but it makes all item the same length (if they are too long it
            will cut them of) so to profit from the speed gains but at the same time not cutting of the file paths, the
            QListWidget (takes care of vertical scrolling) is put into a QScrollArea, which takes care of
            the horizontal scrolling. QScrollArea.setWidgetResizable() takes care of the dynamic height,
            the minimum size is set to 15px times the number of characters of the longest string. All scrollbars
            except the horizontal of the scroll area are disabled, the vertical scrollbar gets overlapped onto the
            ScrollArea in the main layout. (A bit of a dirty solution)'''
        self.result_area.setWidgetResizable(True)
        self.result_listbox.setUniformItemSizes(True)
        try:
            # Get the longest file, fails if there is no item, and then multiply by font size to get the length
            self.result_listbox.setMinimumWidth(
                len(max(self.matched_list, key=len)) * self.result_listbox.font().pointSize())
        except ValueError:
            pass
        # Setting all the Scrollbars
        self.result_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.result_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.result_listbox.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Moving the Scrollbar into the right place, so it's always visible
        self.Search_Results_Layout.addWidget(self.result_listbox.verticalScrollBar(), 1, 0, 9, 6,
                                             Qt.AlignmentFlag.AlignRight)

        # Action, user choice, on double click
        self.result_listbox.itemDoubleClicked.connect(menu_bar.double_clicking_item)

        # The final action run when the UI is build, to measure time properly
        def finish():
            # Update Seconds needed Label
            seconds_text.setText(
                "Time needed: "
                f"{round(time_dict['time_total'] + (perf_counter() - time_dict['time_before_building']), 3)}s")
            seconds_text.adjustSize()

            # Time building UI
            time_dict["time_building"] = perf_counter() - time_dict['time_before_building']

            time_dict["time_total"] = time_dict["time_total"] + time_dict["time_building"]

            # Debug
            logging.info("\nSeconds needed:\n"
                         f"Scanning: {time_dict['time_searching']}\n"
                         f"Indexing: {time_dict['time_indexing']}\n"
                         f"Sorting: {time_dict['time_sorting']}\n"
                         f"Building UI: {time_dict['time_building']}\n"
                         f"Total: {time_dict['time_total']}")

            # Push Notification
            FF_Main_UI.menu_bar_icon.showMessage(
                "File Find - Search finished!", f"Your Search finished!\nin {search_path}",
                QIcon(os.path.join(FF_Files.ASSETS_FOLDER, "Find_button_img_small.png")),
                100000)
            # Update Search indicator
            FF_Main_UI.MainWindow.update_search_status_label()

            logging.info("Finished Building Search-Results-UI!\n")

        # Adding the finish function to the Qt event loop so it measures the time correctly
        QTimer.singleShot(0, finish)
