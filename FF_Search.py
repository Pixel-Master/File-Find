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
from json import dump, load
from sys import platform
from time import perf_counter, mktime

# PySide6 Gui Imports
from PySide6.QtCore import QThreadPool, Signal, QObject, QDate, Qt
from PySide6.QtWidgets import QFileDialog, QWidget

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Main_UI
import FF_Search_UI


# Sorting algorithms
class Sort:

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

    # Sort by Date Created on macOS
    @staticmethod
    def c_date_mac(file):
        try:
            # Using os.stat because os.path.getctime returns a wrong date
            return os.stat(file).st_birthtime
        except FileNotFoundError:
            return -1

    # Sort by Date Created on Windows
    @staticmethod
    def c_date_win(file):
        try:
            return os.path.getctime(file)
        except FileNotFoundError:
            return -1


# Class for Generating the terminal command
class GenerateTerminalCommand:
    def __init__(self, name: str, name_contains: str, file_ending: str, fn_match: str):
        self.shell_command = f"find {FF_Files.SELECTED_DIR}"
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
class LoadSearch:
    def __init__(self, parent):
        load_dialog = QFileDialog.getOpenFileName(parent,
                                                  "Import File Find Search",
                                                  FF_Files.USER_FOLDER,
                                                  "*.FFSearch;")
        self.load_file = load_dialog[0]

        # Open file
        self.open_file(self.load_file, parent)

    # Opening the user-interface and creating a cache file for the reload button
    @staticmethod
    def open_file(load_file, parent):
        # A file was selected
        if load_file != "":

            # Debug
            logging.info(f"Loading {load_file}")
            # Opening the file
            with open(load_file) as opened_file:
                # Saving file content
                saved_file_content = load(opened_file)
                # Debug
                logging.info(f"File has version: {saved_file_content['VERSION']},"
                             f" local version: {FF_Files.FF_SEARCH_VERSION}")

                # If the cache doesn't exist
                if not os.path.exists(
                        os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                     f"{load_file}.FFCache".replace("/", "-"))):

                    # Dictionary which is going to be dumped into the cache file
                    dump_dict = {"VERSION": FF_Files.FF_CACHE_VERSION,
                                 "found_path_set": saved_file_content["matched_list"],
                                 "type_dict": {}}

                    # Getting types
                    for cache_file in saved_file_content["matched_list"]:
                        if os.path.isdir(cache_file):
                            dump_dict["type_dict"][cache_file] = "folder"
                        else:
                            dump_dict["type_dict"][cache_file] = "file"

                    # Create a new cache file
                    with open(
                            os.path.join(
                                FF_Files.CACHED_SEARCHES_FOLDER, f"{load_file}.FFCache".replace(
                                    "/", "-")), "w") as cached_search:
                        # Dump the content of the save into the cache with JSON into the file
                        dump(dump_dict, cached_search)

                # Open the UI
                FF_Search_UI.SearchWindow(*[{"time_searching": 0,
                                             "time_indexing": 0,
                                             "time_sorting": 0,
                                             "time_building": 0,
                                             "time_total": 0},
                                            saved_file_content["matched_list"], load_file, parent])


# The Search Engine
class Search:
    def __init__(self, data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max,
                 data_file_size_min_unit, data_file_size_max_unit, data_library,
                 data_search_for, data_search_from_valid, data_search_from_unchecked, data_content, data_date_edits,
                 data_sort_by, data_reverse_sort, data_file_group, parent: QWidget):
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

        # Convert file size values to bytes and test if file size numbers are valid
        try:
            if data_file_size_min_unit == "No Limit" and data_file_size_min_unit == "No Limit":
                # Store data
                size_data = "unused"
                data_file_size_max = ""
                data_file_size_min = ""
            else:
                # Replacing No Limit with fixed values
                if data_file_size_min_unit == "No Limit":
                    data_file_size_min = 0

                elif data_file_size_max_unit == "No Limit":
                    # Using 1 Petabyte as the upper limit
                    data_file_size_max = 1e15

                size_unit_factors = {"No Limit": 1, "Bytes": 1, "KB": 1000, "MB": 1000000, "GB": 1000000000}

                # Adjust units
                data_file_size_min = float(data_file_size_min) * size_unit_factors[data_file_size_min_unit]
                data_file_size_max = float(data_file_size_max) * size_unit_factors[data_file_size_max_unit]

                # Testing if one is larger than the other
                if data_file_size_min < data_file_size_max:
                    size_data = "valid"
                else:
                    # Both fields are empty
                    size_data = "invalid"

        except ValueError:
            size_data = "invalid"

        logging.debug(f"{size_data = }, {data_file_size_min = }, {data_file_size_max = }")

        # Loading excluded files
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as excluded_file:
            data_excluded_files = load(excluded_file)["excluded_files"]

        # Checking if the search scope is an excluded directory
        excluded_files_block_search = False
        for excluded_file in data_excluded_files:
            if data_search_from_valid.startswith(excluded_file):
                excluded_files_block_search = True
                break

        # Fetching Errors
        # Testing if file ending, file groups or name contains are used together with name,
        # because if they do no file will be found
        # Also testing if wildcard syntax is used in data_name,
        # because wildcard is supported and so no error should appear
        if (((data_name != "" and data_in_name != "") or
             (data_name != "" and data_filetype != "") or
             (data_name != "" and data_file_group != list(FF_Files.FILE_FORMATS.keys())))
                and
                (not (("[" in data_name) or ("?" in data_name) or ("*" in data_name)))):
            # Debug
            logging.error("File name can't be used together with file type, name contains or file ending")

            # Show Popup
            FF_Additional_UI.PopUps.show_critical_messagebox(
                "NAME ERROR!",
                "Name Error!\n\nFile name can't be used together with file type, name contains or file ending",
                parent=None)

        # Directory not valid
        elif data_search_from_valid != data_search_from_unchecked and not os.path.isdir(data_search_from_unchecked):
            # Debug
            logging.error("Directory Error! Given directory is not a valid folder!")

            # Show Popup
            FF_Additional_UI.PopUps.show_critical_messagebox(
                "Directory Error!",
                "Directory Error!\n\nGiven directory is not a valid folder!",
                parent=None)

        # File Size max must be larger than File Size min
        elif size_data == "invalid":
            # Debug
            logging.error("Size Error! File Size min is larger than File Size max or one of them is invalid!")

            # Show Popup
            FF_Additional_UI.PopUps.show_critical_messagebox(
                "SIZE ERROR!",
                "Size Error!\n\nFile size min is larger than file size max or one of them is invalid!",
                parent=None)

        # First Date must be earlier than second Date
        elif unix_time_list["c_date_from"] >= unix_time_list["c_date_to"] or \
                unix_time_list["m_date_from"] >= unix_time_list["m_date_to"]:
            # Debug
            logging.error("Date Error! First Date is later than second Date!")

            # Show Popup
            FF_Additional_UI.PopUps.show_critical_messagebox("DATE ERROR!",
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
            FF_Additional_UI.PopUps.show_critical_messagebox("System Files Error!",
                                                             "System Files Error!\n\nActivate Search in System Files!\n"
                                                             "Search in system files disabled"
                                                             " but search directory is in library folder!",
                                                             parent=None)

        # If data_file_group is an empty list (no files would be found)
        elif not data_file_group:
            # Debug
            logging.error("File Types Error! No File Types are selected")

            # Show Popup
            FF_Additional_UI.PopUps.show_critical_messagebox("File Types Error!",
                                                             "File Types Error!\n\nSelect a file type!\n"
                                                             "No files would be found, because no file type "
                                                             "category is selected.",
                                                             parent=None)

        # If the search scope is an excluded file
        elif excluded_files_block_search:
            # Debug
            logging.error("Directory Error! Search in directory is in an excluded directory")

            # Show Popup
            FF_Additional_UI.PopUps.show_critical_messagebox(
                "Directory Error!",
                "Directory Error!\n\n"
                "The directory you searched in is in an excluded folder.\n\n"
                "You can edit the excluded folders in the File Find Settings. \n(File Find > Preferences...)",
                parent=None)

        # Start Searching
        else:

            # Updating ACTIVE_SEARCH_THREADS
            global ACTIVE_SEARCH_THREADS
            ACTIVE_SEARCH_THREADS += 1

            # Defining menu bar log
            self.ui_logger = FF_Main_UI.SearchUpdate(data_search_from_valid)

            # Testing Cache
            FF_Files.cache_test(is_launching=False)

            # Starting
            logging.info("Starting Search...")
            logging.debug(f"Running Threads: {ACTIVE_SEARCH_THREADS}")

            # Setting up QThreadPool
            self.ui_logger.update("Setting up Thread...")
            logging.debug("Setting up QThreadPool...")

            # Creating Qt Signal
            class SignalClass(QObject):
                finished = Signal()

            # Defining thread
            self.thread = QThreadPool(parent)

            # Setup Qt6 Signal
            self.signals = SignalClass()
            # Debug
            self.signals.finished.connect(lambda: logging.info("Finished Search Thread!\n"))
            # Launching UI
            self.signals.finished.connect(lambda: FF_Search_UI.SearchWindow(*SEARCH_OUTPUT))

            # Starting the Thread
            self.thread.start(
                lambda: self.searching(
                    data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                    data_search_from_valid, data_search_for, data_content, unix_time_list, data_sort_by,
                    data_reverse_sort, data_file_group, data_excluded_files, parent))

            # Debug
            logging.debug("Finished Setting up QThreadPool!")

    # The search engine
    def searching(self, data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                  data_search_from, data_search_for, data_content, data_time, data_sort_by, data_reverse_sort,
                  data_file_group, data_excluded_files, parent):
        # Debug
        logging.info("Starting Search...")
        self.ui_logger.update("Starting Search...")

        # Saving time before scanning
        time_before_start = perf_counter()

        # Remove the "." and any star because they are added later
        data_filetype = data_filetype.lstrip(".*")

        # Lower Arguments to remove case sensitivity
        data_name = data_name.lower()
        data_in_name = data_in_name.lower()
        data_filetype = data_filetype.lower()

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
            # needed
            logging.debug("Files and folders checking is needed")
            data_search_for_needed = False
        else:
            # not needed
            logging.debug("Files and folders checking is NOT needed")
            data_search_for_needed = True

        # Testing if one of the excluded folder is in the search scope, if not checking isn't necessary
        exclude_file_in_scope = False
        for excluded_test_file in data_excluded_files:
            if excluded_test_file.startswith(data_search_from):
                exclude_file_in_scope = True
                break

        # If data_excluded_files is an empty list or no file in the excluded list is in the search scope
        if not data_excluded_files or not exclude_file_in_scope:
            # If the list is empty
            logging.debug("Excluded files checking is NOT needed")
            data_excluded_files_needed = False

        else:
            logging.debug("Excluded files checking is needed")
            data_excluded_files_needed = True

        # Checking if check for file groups is needed
        if set(data_file_group) != set(FF_Files.FILE_FORMATS.keys()):
            logging.debug("File groups checking is needed")

            # Creating a set and adding every needed file format to it
            allowed_filetypes_set = set()
            disallowed_filetypes_set = set()  # Needed if "other" is activated

            # Iterating through the list of file group type
            for file_group in FF_Files.FILE_FORMATS.keys():
                # Needing two lists because of "other",
                # when it's activated all groups, which are not allowed are collected
                # Else all allowed groups are collected
                # This is because "other" is everything else, which isn't in a group.
                if file_group in data_file_group:
                    for file in FF_Files.FILE_FORMATS[file_group]:
                        allowed_filetypes_set.add(file)
                else:
                    for file in FF_Files.FILE_FORMATS[file_group]:
                        disallowed_filetypes_set.add(file)

            # Making tuples out of the sets for better performance
            allowed_filetypes = tuple(allowed_filetypes_set)
            disallowed_filetypes = tuple(disallowed_filetypes_set)

        else:
            logging.debug("File groups checking is NOT needed")
            # Because checking isn't needed and wwe don't want automated tools to flag this as "possibly unassigned"
            allowed_filetypes = None
            disallowed_filetypes = None

        # Debug
        logging.info("Starting Scanning...")
        # Update the menu-bar status
        self.ui_logger.update("Scanning...")

        '''Checking, if a Cache File exist, if not it goes through every file in the directory and saves it. If a
        cache does exist it loads found_path_set from the cache file'''
        if os.path.exists(
                os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache")):
            # Debug
            logging.info("Scanning using cached Data..")

            used_cached = True
            # Load cache
            with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                   data_search_from.replace("/", "-") + ".FFCache")) as search_results:
                load_input = load(search_results)
                found_path_set = set(load_input["found_path_set"])
                type_dict = load_input["type_dict"]

        else:

            # Creates empty lists for the files
            found_path_set: set = set()
            type_dict: dict = {}

            used_cached = False

            # Going through every file and every folder using the os.walk() method
            # Saving every file to found_path_set and the type (file or folder) to found_path_dict
            for (roots, dirs, files) in os.walk(data_search_from):
                for file in files:
                    # Saving types to the dictionaries
                    type_dict[os.path.join(roots, file)] = "file"
                    # Saving the path to a list for fast access
                    found_path_set.add(os.path.join(roots, file))

                for directory in dirs:
                    # Saving types to the dictionaries
                    type_dict[os.path.join(roots, directory)] = "folder"

                    # Saving the path to a list for fast access
                    found_path_set.add(os.path.join(roots, directory))

        # Saves time
        time_after_searching = perf_counter() - time_before_start

        # Debug
        logging.info("Starting Indexing...")
        # Update the menu-bar status
        self.ui_logger.update("Indexing...")

        # Creating a copy because items can't be removed while iterating over a set
        copy_found_path_set = found_path_set.copy()
        original_found_path_set = found_path_set.copy()

        # Applies filters, when they don't match the function remove them from the found_path_dict
        # Name
        logging.info("Indexing Name...")
        self.ui_logger.update("Indexing Name...")
        if data_name != "":

            # Scan every file
            for name_file in found_path_set:
                if not fnmatch(os.path.basename(name_file).lower(), data_name):
                    copy_found_path_set.remove(name_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Name contains
        logging.info("Indexing Name contains...")
        self.ui_logger.update("Indexing Name contains...")

        if data_in_name != "":
            # Scan every file
            for name_contains_file in found_path_set:
                if not (data_in_name in os.path.basename(name_contains_file).lower()):
                    copy_found_path_set.remove(name_contains_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Filetype
        logging.info("Indexing file ending...")
        self.ui_logger.update("Indexing file ending...")

        if data_filetype != "":
            # Scan every file
            for filetype_file in found_path_set:
                if not filetype_file.lower().endswith(f".{data_filetype}"):
                    copy_found_path_set.remove(filetype_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Search in System Files
        logging.info("Indexing System Files...")
        self.ui_logger.update("Indexing System Files...")
        if not data_library:

            # Scan every file
            for library_file in found_path_set:
                if "/Library" in library_file or library_file.startswith("/System"):
                    # Remove the file
                    copy_found_path_set.remove(library_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Exclude or Include Folders or Files
        logging.info("Indexing Exclude or Include Folders or Files...")
        self.ui_logger.update("Indexing Exclude or Include Folders or Files...")
        if data_search_for_needed:

            # Checks for File
            if data_search_for == "only Files":
                for file_file in found_path_set:
                    if type_dict[file_file] != "file":
                        copy_found_path_set.remove(file_file)
            # Checks for Directories
            elif data_search_for == "only Folders":
                for folder_file in found_path_set:
                    if type_dict[folder_file] != "folder":
                        copy_found_path_set.remove(folder_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()
        # Filter some unnecessary System Files
        logging.info("Filtering for file groups...")
        self.ui_logger.update("Filtering for file groups...")

        # if "other" files is activated
        if allowed_filetypes is not None:
            if "*" in allowed_filetypes:
                for file_group_file in found_path_set:
                    for file_ending in disallowed_filetypes:
                        if file_group_file.lower().endswith(f".{file_ending}"):
                            copy_found_path_set.remove(file_group_file)

            else:
                for file_group_file in found_path_set:
                    for file_ending in allowed_filetypes:
                        if file_group_file.lower().endswith(f".{file_ending}"):
                            break
                        else:
                            pass
                    else:
                        copy_found_path_set.remove(file_group_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Filter some unnecessary System Files
        logging.info("Removing dump files...")
        self.ui_logger.update("Removing dump files...")

        for system_file in found_path_set:
            basename = os.path.basename(system_file).lower()
            if basename in (".ds_store", ".localized", "desktop.ini", "thumbs.db"):
                copy_found_path_set.remove(system_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Excluded Files
        logging.info("Filtering excluded files...")
        self.ui_logger.update("Filtering excluded files...")
        if data_excluded_files_needed:
            for test_file in found_path_set:
                for excluded_file in data_excluded_files:
                    if test_file.startswith(excluded_file):
                        copy_found_path_set.remove(test_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Checking for Date Created
        # Checking if File Date is between Filter Dates
        logging.info("Indexing Date created...")
        self.ui_logger.update("Indexing Date created...")
        if data_c_time_needed:

            # On Windows and Linux
            # (On Linux this currently returns the modification date,
            # because it's impossible to access with pure python)
            if platform == "win32" or platform == 'cygwin' or platform == "linux":

                # Looping through every file
                for c_date_file in found_path_set:
                    # Using os.stat because os.path.getctime returns a wrong date
                    try:
                        file_c_time = os.path.getctime(c_date_file)

                        # Checking for file time and which values in data_time are modified
                        if not (data_time["c_date_from"] <= file_c_time <= data_time["c_date_to"]):
                            copy_found_path_set.remove(c_date_file)

                    except FileNotFoundError:
                        copy_found_path_set.remove(c_date_file)
            # On Mac
            elif platform == "darwin":

                # Looping through every file
                for c_date_file in found_path_set:
                    # Using os.stat because os.path.getctime returns a wrong date
                    try:
                        file_c_time = os.stat(c_date_file).st_birthtime

                        # Checking for file time and which values in data_time are modified
                        if not (data_time["c_date_from"] <= file_c_time <= data_time["c_date_to"]):
                            copy_found_path_set.remove(c_date_file)

                    except FileNotFoundError:
                        copy_found_path_set.remove(c_date_file)

            # If platform is unknown
            else:
                # Debug
                logging.error(f"While trying to test cache, unrecognised platform: {platform}")

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

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
                        copy_found_path_set.remove(m_date_file)

                except OSError:
                    copy_found_path_set.remove(m_date_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # File Size
        logging.info("Indexing file size...")
        self.ui_logger.update("Indexing file size...")
        if data_file_size_min != "" and data_file_size_max != "":

            # Looping through every file
            for size_file in found_path_set:
                if not data_file_size_max >= FF_Files.get_file_size(size_file) >= data_file_size_min:
                    # Remove file
                    copy_found_path_set.remove(size_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # File contains
        logging.info("Indexing file contains...")
        self.ui_logger.update("Indexing file contains...")
        if data_content != "":

            # Looping through every file
            for content_file in found_path_set:
                does_contain = False
                try:
                    # Opening every file in read mode
                    with open(content_file) as opened_content_file:
                        for line in opened_content_file:
                            if data_content in line:
                                does_contain = True
                                break
                    if not does_contain:
                        copy_found_path_set.remove(content_file)
                except (UnicodeDecodeError, OSError):
                    copy_found_path_set.remove(content_file)
                else:
                    if os.path.isdir(content_file):
                        copy_found_path_set.remove(content_file)

        # Making the copy and the original the same and deleting the copy
        found_path_set = copy_found_path_set.copy()
        del copy_found_path_set

        # Prints out files found
        logging.info(f"Found {len(found_path_set)} Files and Folders")

        # Creating a list for sorting from set and creating a backup for caching
        found_path_list = list(found_path_set)

        # Saving time
        time_after_indexing = perf_counter() - (time_after_searching + time_before_start)

        # Sorting
        if data_sort_by == "File Name":
            logging.info("Sorting list by name...")
            self.ui_logger.update("Sorting list by name...")
            found_path_list.sort(key=Sort.name, reverse=data_reverse_sort)

        elif data_sort_by == "File Size":
            logging.info("Sorting list by size...")
            self.ui_logger.update("Sorting list by size...")
            found_path_list.sort(key=Sort.size, reverse=not data_reverse_sort)

        elif data_sort_by == "Date Created":
            logging.info(f"Sorting list by creation date on {platform}...")
            self.ui_logger.update("Sorting list by creation date...")

            # On Windows and Linux
            # (On Linux this currently returns the modification date,
            # because it's impossible to access with pure python)
            if platform == "win32" or platform == 'cygwin' or platform == "linux":
                found_path_list.sort(key=Sort.c_date_win, reverse=not data_reverse_sort)

            # On Mac
            if platform == "darwin":
                found_path_list.sort(key=Sort.c_date_mac, reverse=not data_reverse_sort)

        elif data_sort_by == "Date Modified":
            logging.info("Sorting list by modification date...")
            self.ui_logger.update("Sorting list by modification date...")
            found_path_list.sort(key=Sort.m_date, reverse=not data_reverse_sort)

        elif data_sort_by == "Path":
            logging.info("Sorting list by path...")
            self.ui_logger.update("Sorting list by path...")
            found_path_list.sort(key=lambda sort_file: sort_file.lower(), reverse=data_reverse_sort)

        else:
            logging.info("Skipping Sorting")
            self.ui_logger.update("Skipping Sorting...")
            if data_reverse_sort:
                logging.debug("Reversing Results...")
                found_path_list = list(reversed(found_path_list))

        # Caching Results with pickle
        # Testing if cache file exist, if it doesn't exist it caches scanned files
        if not used_cached:
            # Debug and menu-bar log
            logging.info("Caching Search Results...")
            self.ui_logger.update("Caching Search Results...")

            # Creating file
            with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache"),
                      "w") as result_file:
                # Dumping with pickle
                dump({
                    "found_path_set": list(original_found_path_set),
                    "type_dict": type_dict}, result_file)

        else:
            logging.info("Cache file already exist, skipping caching...")

        # Updating search status indicator
        FF_Main_UI.MainWindow.update_search_status_label(ui_building=True)

        # Calculating time
        time_after_sorting = perf_counter() - (time_after_indexing + time_after_searching + time_before_start)
        time_total = perf_counter() - time_before_start

        # Cleaning Memory
        del type_dict, found_path_set, original_found_path_set

        # Debug
        logging.info("Finished Searching!")
        self.ui_logger.update("Building UI...")

        # The parameter passed on to the UI builder
        global SEARCH_OUTPUT
        SEARCH_OUTPUT = [{"time_total": time_total,
                          "time_searching": time_after_searching,
                          "time_indexing": time_after_indexing,
                          "time_sorting": time_after_sorting},
                         found_path_list, data_search_from, parent]

        # Updating Thread count
        global ACTIVE_SEARCH_THREADS
        ACTIVE_SEARCH_THREADS -= 1
        # Building the UI with emitting the signal
        self.signals.finished.emit()

    """
    Converting Date-times
    Converting the output of QDateEdit into the unix time by first using QDateEdit.date() to get
    something like this: QDate(1,3,2000), after that using QDate.toString with the conversion of to
    ISO standard Date to get this: 2024-01-26
    than we can use .split("-") to convert 2024-01-26 into a list [2024,1,26], after that we use time.mktime
    to get the unix time format that means something like, that: 946854000.0, only to match this with
    os.getctime, what we can use to get the creation date of a file.

    Yes it would be easier if Qt had a function to get the unix time
    """

    @staticmethod
    def conv_qdate_to_unix_time(input_edit: QDate, expand_days_num: int = 1):
        # Expand days on the second date of the range because if input is 1.Jan.2024 - 1.Jan-2024 there will be no files
        time_string = str(input_edit.toString(Qt.DateFormat.ISODate))
        time_list = time_string.split("-")
        # Fill in hours, minutes and second with 0 because we don't have them
        unix_time = mktime(
            (int(time_list[0]), int(time_list[1]), int(time_list[2]) + expand_days_num, 0, 0, 0, 0, 0, 0))
        return unix_time


# Global Variables for Search Threads
SEARCH_OUTPUT: [{str: float}, list, str, QWidget] = []

ACTIVE_SEARCH_THREADS: int = 0
