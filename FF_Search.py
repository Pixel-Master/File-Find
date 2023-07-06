# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2023 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the search engine

# Imports
import logging
import os
from fnmatch import fnmatch
from pickle import dump, load
from sys import exit
from time import perf_counter, mktime

# PyQt6 Gui Imports
from PyQt6.QtCore import QThreadPool, pyqtSignal, QObject, QDate
from PyQt6.QtWidgets import QFileDialog, QWidget

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Main_UI
import FF_Search_UI


# Sorting algorithms
class sort:

    # Sort by Size
    @staticmethod
    def size(file):
        return FF_Files.get_file_size(file)

    # Sort by Name
    @staticmethod
    def name(file):
        try:
            return os.path.basename(file)
        except FileNotFoundError:
            return -1

    # Sort by Date Modified
    @staticmethod
    def m_date(file):
        try:
            return os.path.getmtime(file)
        except FileNotFoundError:
            return -1

    # Sort by Date Created
    @staticmethod
    def c_date(file):
        try:
            # Using os.stat because os.path.getctime returns a wrong date
            return os.stat(file).st_birthtime
        except FileNotFoundError:
            return -1


# Class for Generating the terminal command
class generate_terminal_command:
    def __init__(self, name: str, name_contains: str, file_ending: str, fn_match: str):
        self.shell_command = f"find {os.getcwd()}"
        self.name_string = ""
        if name != "":
            self.name_string += f"{name}"
        elif fn_match != "":
            self.name_string = fn_match

        else:
            if name_contains != "":
                self.name_string += f"*{name_contains}*"
            if file_ending != "":
                self.name_string += f"*.{file_ending}"

        if self.name_string != "":
            self.shell_command += f" -name \"{self.name_string}\""

        # Debug
        logging.info(f"Command: {self.shell_command}")

    def __str__(self):
        return self.shell_command


# Loading a saved search
class load_search:
    def __init__(self, parent):
        load_dialog = QFileDialog.getOpenFileName(parent,
                                                  "Export File Find Search",
                                                  FF_Files.SAVED_SEARCHES_FOLDER,
                                                  "*.FFSave;")
        self.load_file = load_dialog[0]

        # Open file
        self.open_file(self.load_file, parent)

    # Opening the user-interface and creating a cache file for the reload button
    @staticmethod
    def open_file(load_file, parent):
        if load_file != "":
            with open(load_file, "rb") as OpenedFile:
                saved_file_content = load(OpenedFile)
                if not os.path.exists(
                        os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                     f"{load_file}.FFCache".replace("/", "-"))):
                    with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                           f"{load_file}.FFCache".replace("/", "-")),
                              "wb") as CachedSearch:
                        dump(saved_file_content, file=CachedSearch)
                FF_Search_UI.Search_Window(*[0, 0, 0, 0, saved_file_content, load_file, parent])


# The Search Engine
class search:
    def __init__(self, data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                 data_search_for, data_search_from_valid, data_search_from_unchecked, data_content, data_date_edits,
                 data_sort_by, data_reverse_sort, data_fn_match, parent: QWidget):
        # Debug
        logging.debug("Converting Date-times...")

        """
        Converting Date-times
        Converting the output of QDateEdit into the unix time by first using QDateEdit.date() to get
        something like this: QDate(1,3,2000), after that using QDate.toPyDate to get this: 1-3-2000,
        than we can use .split("-") to convert 1-3-2000 into a list [1,3,2000], after that we use time.mktime
        to get the unix time format that means something like, that: 946854000.0, only to match this with
        os.getctime, what we can use to get the creation date of a file.

        Yes it would be easier if Qt had a function to get the unix time
        """
        unix_time_list = {}

        self.DEFAULT_TIME_INPUT = {"c_date_from": 946681200.0,
                                   "c_date_to": self.conv_qdate_to_unix_time(QDate.currentDate()),
                                   "m_date_from": 946681200.0,
                                   "m_date_to": self.conv_qdate_to_unix_time(QDate.currentDate())}

        for time_drop_down in data_date_edits.items():
            # Expand the date range
            if "date_to" in time_drop_down[0]:
                expand_days = 1
            else:
                expand_days = 0
            time_to_add_to_time_list = self.conv_qdate_to_unix_time(time_drop_down[1].date(),
                                                                    expand_days)
            # Saving the time
            unix_time_list[time_drop_down[0]] = time_to_add_to_time_list

        # Fetching Errors
        # Name contains and Name can't be used together
        if data_name != "" and data_in_name != "" or data_name != "" and data_filetype != "":
            # Debug
            logging.error("Name Error! File Name and Name contains or File Type can't be used together!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("NAME ERROR!",
                                                          "Name Error!\n\nFile name and name contains or file type "
                                                          "can't be used together",
                                                          parent=None)

        # Directory not valid
        elif data_search_from_valid != data_search_from_unchecked and not os.path.isdir(data_search_from_unchecked):
            # Debug
            logging.error("Directory Error! Given directory is not a valid folder!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("Directory Error!",
                                                          "Directory Error!\n\nGiven directory is not a valid folder!",
                                                          parent=None)

        # File Size max must be larger than File Size min
        elif data_file_size_min >= data_file_size_max and not data_file_size_min == data_file_size_max:
            # Debug
            logging.error("Size Error! File Size min is larger than File Size max!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("SIZE ERROR!",
                                                          "Size Error!\n\nFile size min is larger than file size max!",
                                                          parent=None)

        # First Date must be earlier than second Date
        elif unix_time_list["c_date_from"] >= unix_time_list["c_date_to"] or \
                unix_time_list["m_date_from"] >= unix_time_list["m_date_to"]:
            # Debug
            logging.error("Date Error! First Date is later than second Date!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("DATE ERROR!",
                                                          "Date Error!\n\n"
                                                          "First date must be earlier than second date!\n\n"
                                                          "e.g.:\nvalid: 15.Feb.2022 - 17.Feb.2023\n"
                                                          "invalid: 17.Feb.2023 - 15.Feb.2022",
                                                          parent=None)

        # Search in System Files disabled, but Search path is in library Folder
        elif ((not data_library) and ("/Library" in data_search_from_valid)) or \
                (not data_library) and (data_search_from_valid.startswith("/System")):
            # Debug
            logging.error("System Files Error! Search in System Files disabled, but Directory is in Library Folder")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("System Files Error!",
                                                          "System Files Error!\n\nActivate Search in System Files!\n"
                                                          "Search in system files disabled"
                                                          " but search directory is in library folder!",
                                                          parent=None)

        # QMessageBox to confirm searching
        elif not FF_Additional_UI.msg.show_search_question(parent):
            logging.info("Cancelled Searching!")

        # Start Searching
        else:

            # Updating ACTIVE_SEARCH_THREADS
            global ACTIVE_SEARCH_THREADS
            ACTIVE_SEARCH_THREADS += 1

            # Defining menubar log
            self.ui_logger = FF_Main_UI.search_update(lambda: exit(0), data_search_from_valid)

            # Testing Cache
            FF_Files.cache_test(is_launching=False)

            # Starting
            logging.info("Starting Search...")
            logging.debug(f"Running Threads: {ACTIVE_SEARCH_THREADS}")

            # Setting up QThreadPool
            self.ui_logger.update("Setting up Thread...")
            logging.debug("Setting up QThreadPool...")

            # Creating Qt Signal
            class signals_class(QObject):
                finished = pyqtSignal()

            # Defining thread
            self.thread = QThreadPool(parent)

            # Setup pyqt Signal
            self.signals = signals_class()
            # Debug
            self.signals.finished.connect(lambda: logging.info("Finished Search Thread!\n"))
            # Launching UI
            self.signals.finished.connect(lambda: FF_Search_UI.Search_Window(*SEARCH_OUTPUT))
            # Updating Status Indicator
            self.signals.finished.connect(FF_Main_UI.Main_Window.update_search_status_label)

            # Starting the Thread
            self.thread.start(
                lambda: self.searching(data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max,
                                       data_library, data_search_from_valid, data_search_for, data_content,
                                       unix_time_list, data_sort_by, data_reverse_sort, data_fn_match, parent))

            # Debug
            logging.debug("Finished Setting up QThreadPool!")

    # The search engine
    def searching(self, data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                  data_search_from, data_search_for, data_content, data_time, data_sort_by, data_reverse_sort,
                  data_fn_match, parent):
        # Debug
        logging.info("Starting Search...")
        self.ui_logger.update("Starting Search...")

        # Saving time before scanning
        time_before_start = perf_counter()

        # Remove the "." because it's added later
        if data_filetype.startswith("."):
            data_filetype.strip(".")

        # Lower Arguments
        data_name = data_name.lower()
        data_in_name = data_in_name.lower()
        data_filetype = data_filetype.lower()
        data_fn_match = data_fn_match.lower()

        # Checking if created time checking is needed
        if data_time["c_date_from"] == self.DEFAULT_TIME_INPUT["c_date_from"] and \
                data_time["c_date_to"] == self.DEFAULT_TIME_INPUT["c_date_to"]:
            data_c_time_needed = False
            logging.debug("Created time checking is NOT needed")

        else:
            logging.debug("Created time checking is needed")
            data_c_time_needed = True

        # Checking if modified time checking is needed
        if data_time["m_date_from"] == self.DEFAULT_TIME_INPUT["m_date_from"] and \
                data_time["m_date_to"] == self.DEFAULT_TIME_INPUT["m_date_to"]:
            data_m_time_needed = False
            logging.debug("Modified time checking is NOT needed")

        else:
            logging.debug("Modified time checking is needed")
            data_m_time_needed = True

        # Checking if data_search_for is needed
        if data_search_for == "All Files and Folders":
            data_search_for_needed = False
        else:
            data_search_for_needed = True

        # Loading excluded files
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "rb") as ExcludedFile:
            data_excluded_files = load(ExcludedFile)["excluded_files"]

        if not data_excluded_files:
            data_excluded_files_needed = False

        else:
            data_excluded_files_needed = True

        # Debug
        logging.info("Starting Scanning...")
        # Update the menubar status
        self.ui_logger.update("Scanning...")

        '''Checking, if Cache File exist, if not it goes through every file in the directory and saves it. If It
        exist it loads the Cache File in to found_path_set '''
        if os.path.exists(
                os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache")):
            # Debug
            logging.info("Scanning using cached Data..")

            used_cached = True

            with open(
                    os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache"),
                    "rb") as SearchResults:
                load_input = load(SearchResults)
                found_path_set = load_input[0]
                low_basename_dict = load_input[1]
                type_dict = load_input[2]

        else:

            # Creates empty lists for the files
            found_path_set: set = set()
            low_basename_dict: dict = {}
            type_dict: dict = {}

            used_cached = False

            # Going through every file and every folder using the os.walk() method
            # Saving every file to found_path_set and the type (file or folder) to found_path_dict
            for (roots, dirs, files) in os.walk(data_search_from):
                for file in files:
                    # Saving type and basename to the dictionaries
                    low_basename_dict[os.path.join(roots, file)] = file.lower()
                    type_dict[os.path.join(roots, file)] = "file"
                    # Saving the path to a list for fast access
                    found_path_set.add(os.path.join(roots, file))

                for directory in dirs:
                    # Saving type and basename to the dictionaries
                    low_basename_dict[os.path.join(roots, directory)] = directory.lower()
                    type_dict[os.path.join(roots, directory)] = "folder"

                    # Saving the path to a list for fast access
                    found_path_set.add(os.path.join(roots, directory))

        # Saves time
        time_after_searching = perf_counter() - time_before_start

        # Debug
        logging.info("Starting Indexing...")
        # Update the menubar status
        self.ui_logger.update("Indexing...")

        # Set for files that have to be removed
        remove_path_set = set()

        # Applies filters, when they don't match the function remove them from the found_path_dict
        # Name
        logging.info("Indexing Name...")
        self.ui_logger.update("Indexing Name...")
        if data_name != "":

            # Scan every file
            for name_file in found_path_set:
                if data_name != low_basename_dict[name_file]:
                    remove_path_set.add(name_file)

        # Name contains
        logging.info("Indexing Name contains...")
        self.ui_logger.update("Indexing Name contains...")
        if data_in_name != "":

            # Scan every file
            for name_contains_file in found_path_set:
                if not (data_in_name in low_basename_dict[name_contains_file]):
                    remove_path_set.add(name_contains_file)

        # Filetype
        logging.info("Indexing Filetype...")
        self.ui_logger.update("Indexing Filetype...")
        if data_filetype != "":

            # Scan every file
            for filetype_file in found_path_set:
                if not low_basename_dict[filetype_file].endswith(f".{data_filetype}"):
                    remove_path_set.add(filetype_file)

        # Wildcard
        logging.info("Indexing Wildcard...")
        self.ui_logger.update("Indexing Wildcard...")
        if data_fn_match != "":

            # Scan every file
            for wildcard_file in found_path_set:
                if not fnmatch(low_basename_dict[wildcard_file], data_fn_match):
                    remove_path_set.add(wildcard_file)

        # Search in System Files
        logging.info("Indexing System Files...")
        self.ui_logger.update("Indexing System Files...")
        if not data_library:

            # Scan every file
            for library_file in found_path_set:
                if "/Library" in library_file or library_file.startswith("/System"):
                    # Remove the file
                    remove_path_set.add(library_file)

        # Exclude or Include Folders or Files
        logging.info("Indexing Exclude or Include Folders or Files...")
        self.ui_logger.update("Indexing Exclude or Include Folders or Files...")
        if data_search_for_needed:

            # Checks for File
            if data_search_for == "only Files":
                for file_file in found_path_set:
                    if type_dict[file_file] != "file":
                        remove_path_set.add(file_file)
            # Checks for Directories
            elif data_search_for == "only Folders":
                for folder_file in found_path_set:
                    if type_dict[folder_file] != "folder":
                        remove_path_set.add(folder_file)

        # Checking for Date Created
        # Checking if File Date is between Filter Dates
        logging.info("Indexing Date created...")
        self.ui_logger.update("Indexing Date created...")
        if data_c_time_needed:

            # Looping through every file
            for c_date_file in found_path_set:
                # Using os.stat because os.path.getctime returns a wrong date
                try:
                    file_c_time = os.stat(c_date_file).st_birthtime

                    # Checking for file time and which values in data_time are modified
                    if not (data_time["c_date_from"] <= file_c_time <= data_time["c_date_to"]):
                        remove_path_set.add(c_date_file)

                except FileNotFoundError:
                    remove_path_set.add(c_date_file)

        # Checking for Date Modified
        logging.info("Indexing Date modified...")
        self.ui_logger.update("Indexing Date modified...")
        if data_m_time_needed:

            # Looping through every file
            for m_date_file in found_path_set:
                # Using os.stat because os.path.getctime returns a wrong date
                try:
                    file_m_time = os.path.getmtime(m_date_file)

                    # Checking for file time and which values in data_time are modified
                    if not (data_time["m_date_from"] <= file_m_time <= data_time["m_date_to"]):
                        remove_path_set.add(m_date_file)

                except FileNotFoundError:
                    remove_path_set.add(m_date_file)

        # File Size
        logging.info("Indexing file size...")
        self.ui_logger.update("Indexing file size...")
        if data_file_size_min != "" and data_file_size_max != "":

            # Looping through every file
            for size_file in found_path_set:
                if not (float(data_file_size_max) * 1000000) \
                       >= int(FF_Files.get_file_size(size_file)) \
                       >= (float(data_file_size_min) * 1000000):
                    # Remove file
                    remove_path_set.add(size_file)

        # File contains
        logging.info("Indexing file contains...")
        self.ui_logger.update("Indexing file contains...")
        if data_content != "":

            # Looping through every file
            for content_file in found_path_set:
                does_contain = False
                try:
                    with open(content_file, "r") as ContentFile:
                        for line in ContentFile:
                            if data_content in line:
                                does_contain = True
                                break
                    if not does_contain:
                        remove_path_set.add(content_file)
                except (UnicodeDecodeError, FileNotFoundError, OSError):
                    remove_path_set.add(content_file)
                else:
                    if os.path.isdir(content_file):
                        remove_path_set.add(content_file)

        # Filter some unnecessary System Files
        logging.info("Removing dump files...")
        self.ui_logger.update("Removing dump files...")
        for system_file in found_path_set:

            basename = low_basename_dict[system_file]
            if basename == ".ds_store" or basename == ".localized" or basename == "desktop.ini" \
                    or basename == "thumbs.db":
                remove_path_set.add(system_file)

        # Excluded Files
        logging.info("Filtering excluded files...")
        self.ui_logger.update("Filtering excluded files...")
        if data_excluded_files_needed:
            for test_file in found_path_set:
                for excluded_file in data_excluded_files:
                    if test_file.startswith(excluded_file):
                        remove_path_set.add(test_file)

        # Prints out seconds needed
        logging.info(f"Found {len(found_path_set) - len(remove_path_set)} Files and Folders")

        # Removing removed files from set and creating a backup for caching
        found_path_list = found_path_set.copy()

        for remove_item in remove_path_set:
            found_path_list.remove(remove_item)

        found_path_list = list(found_path_list)

        # Saving time
        time_after_indexing = perf_counter() - (time_after_searching + time_before_start)

        # Sorting
        if data_sort_by == "File Name":
            logging.info("Sorting List by Name...")
            self.ui_logger.update("Sorting List by Name...")
            found_path_list.sort(key=sort.name, reverse=data_reverse_sort)

        elif data_sort_by == "File Size":
            logging.info("Sorting List by Size...")
            self.ui_logger.update("Sorting List by Size...")
            found_path_list.sort(key=sort.size, reverse=not data_reverse_sort)

        elif data_sort_by == "Date Created":
            logging.info("Sorting List by creation date...")
            self.ui_logger.update("Sorting List by creation date...")
            found_path_list.sort(key=sort.c_date, reverse=not data_reverse_sort)

        elif data_sort_by == "Date Modified":
            logging.info("Sorting List by modification date...")
            self.ui_logger.update("Sorting List by modification date...")
            found_path_list.sort(key=sort.m_date, reverse=not data_reverse_sort)

        else:
            logging.info("Skipping Sorting")
            self.ui_logger.update("Skipping Sorting...")
            if data_reverse_sort:
                logging.debug("Reversing Results...")
                found_path_list = list(reversed(found_path_list))

        # Caching Results with pickle
        # Testing if cache file exist, if it doesn't exist it caches scanned files
        if not used_cached:
            # Debug and menubar logg
            logging.info("Caching Search Results...")
            self.ui_logger.update("Caching Search Results...")

            # Creating file
            with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache"),
                      "wb") as resultFile:
                # Dumping with pickle
                dump([found_path_set, low_basename_dict, type_dict], resultFile)

        else:
            logging.info("Cache file already exist, skipping caching...")

        # Calculating time
        time_after_sorting = perf_counter() - (time_after_indexing + time_after_searching + time_before_start)
        time_total = perf_counter() - time_before_start

        # Cleaning Memory
        # del type_dict, found_path_set, low_basename_dict, remove_path_set

        # Debug
        logging.info("Finished Searching!")
        self.ui_logger.update("Building UI...")

        global SEARCH_OUTPUT
        SEARCH_OUTPUT = [time_total, time_after_searching, time_after_indexing, time_after_sorting, found_path_list,
                         data_search_from, parent]

        # Starting the UI with the emitted signal
        self.signals.finished.emit()

        # Updating Thread count
        global ACTIVE_SEARCH_THREADS
        ACTIVE_SEARCH_THREADS -= 1

    @staticmethod
    def conv_qdate_to_unix_time(input_edit: QDate, expand_days_num: int = 1):
        time_list = str(input_edit.toPyDate()).split("-")
        unix_time = mktime(
            (int(time_list[0]), int(time_list[1]), int(time_list[2]) + expand_days_num, 0, 0, 0, 0, 0, 0))
        return unix_time


# Global Variables for Search Threads
SEARCH_OUTPUT: [float, float, float, float, list, str, QWidget] = []

ACTIVE_SEARCH_THREADS: int = 0
