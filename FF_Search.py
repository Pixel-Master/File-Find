# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the search engine

# Imports
import logging
import os
import re
import time
from unicodedata import normalize
from fnmatch import fnmatch
from json import dump, load
from sys import platform
from time import perf_counter, mktime
import difflib

# PySide6 Gui Imports
from PySide6.QtCore import QThreadPool, Signal, QObject, QDate, Qt
from PySide6.QtWidgets import QWidget

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Main_UI
import FF_Search_UI
import FF_Settings


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


# Loading a saved search
class LoadSearch:
    # Opening the user-interface and creating a cache file for the reload button
    @staticmethod
    def load_search_content(load_file):
        # Debug
        logging.info(f"Loading {load_file}")
        # Opening the file
        with open(load_file) as opened_file:
            # Saving file content
            saved_file_content = load(opened_file)
            # Debug
            logging.info(f"File has version: {saved_file_content['VERSION']},"
                         f" local version: {FF_Files.FF_SEARCH_VERSION}")

            # If the cache doesn't exist use unlimited depth
            if not os.path.exists(FF_Files.path_to_cache_file(load_file, -1)):

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
                with open(FF_Files.path_to_cache_file(load_file, -1), "w") as cached_search:
                    # Dump the content of the save into the cache with JSON into the file
                    dump(dump_dict, cached_search)

                # Create a metadata file
                with open(FF_Files.path_to_cache_file(load_file, -1, metadata=True), "w") as cached_search:
                    # Date created
                    # On macOS
                    if platform == "darwin":
                        c_date = os.stat(load_file).st_birthtime
                    # On Linux
                    elif platform == "linux":
                        c_date = os.path.getmtime(load_file)
                    # On Windows
                    else:
                        c_date = os.path.getctime(load_file)
                    # Dump the metadata of the save into the cache with JSON into the file
                    dump({"c_time": c_date,
                          "cache_version": FF_Files.FF_CACHE_VERSION,
                          "original_cache_file": FF_Files.path_to_cache_file(load_file, -1),
                          "global_depth_limit": -1,
                          "path": load_file},
                         cached_search)
                logging.debug(f"Created cache for {load_file} under {FF_Files.path_to_cache_file(load_file, -1)} and"
                              f" {FF_Files.path_to_cache_file(load_file, -1, metadata=True)}")
        return saved_file_content

    @staticmethod
    def open_file(load_file, parent):
        # No file was selected
        if load_file == "":
            return

        saved_file_content = LoadSearch.load_search_content(load_file)
        # Open the UI
        FF_Search_UI.SearchWindow(*[{"time_searching": 0,
                                     "time_indexing": 0,
                                     "time_sorting": 0,
                                     "time_building": 0,
                                     "time_total": 0},
                                    saved_file_content["matched_list"], load_file,
                                    FF_Files.path_to_cache_file(load_file, -1), parent])


# The Search Engine
class Search:
    def __init__(self, data_name, data_name_specifier, data_consider_case, data_similarity, data_filetype,
                 data_file_size_min, data_file_size_max,
                 data_file_size_min_unit, data_file_size_max_unit, data_library,
                 data_search_for, data_search_from_valid, data_search_from_unchecked, data_content, data_date_edits,
                 data_sort_by, data_reverse_sort, data_file_group, data_file_type_mode, data_folder_depth,
                 data_folder_depth_custom, parent: QWidget, new_cache_file=False):
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

                # Testing if may is larger than min other
                if data_file_size_min <= data_file_size_max:
                    size_data = "valid"
                else:
                    # Max is smaller than min
                    size_data = "invalid"

        except ValueError:
            size_data = "invalid"

        logging.debug(f"{size_data=}, {data_file_size_min=}, {data_file_size_max=}")

        # Loading excluded files
        data_excluded_files = FF_Settings.SettingsWindow.load_setting("excluded_files")

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
        wildcard_used = ("[" in data_name) or ("?" in data_name) or ("*" in data_name)
        file_types_used = (
                (data_file_type_mode == "custom" and data_filetype != "") or
                (data_file_type_mode == "predefined" and data_file_group != list(FF_Files.FILE_FORMATS.keys())))
        if data_name != "" and file_types_used and not wildcard_used and data_name_specifier == "is:":
            # Debug
            logging.error("File name \"is\" can't be used together with file type")

            # Show Popup
            FF_Additional_UI.PopUps.show_critical_messagebox(
                "NAME ERROR!",
                "Name Error!\n\nFile name \"is\" can't be used together with file type"
                " as there would be no files found",
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
        elif not data_file_group and data_file_type_mode == "predefined":
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
                # Logging point for menu-bar
                starting = Signal()
                scanning = Signal()
                indexing = Signal()
                indexing_name = Signal()
                indexing_system_files = Signal()
                indexing_files_folders = Signal()
                indexing_file_groups = Signal()
                indexing_dump_files = Signal()
                indexing_excluded = Signal()
                indexing_c_date = Signal()
                indexing_m_date = Signal()
                indexing_file_size = Signal()
                indexing_file_content = Signal()
                sorting_name = Signal()
                sorting_size = Signal()
                sorting_c_date = Signal()
                sorting_m_date = Signal()
                sorting_path = Signal()
                sorting_reversed = Signal()
                caching = Signal()
                building_ui = Signal()

                finished = Signal()
                waiting = Signal()

            # Defining thread
            self.thread = QThreadPool(parent)

            # Setup Qt6 Signal
            self.signals = SignalClass()
            # Displaying "Please Wait"
            self.signals.waiting.connect(lambda: FF_Main_UI.MainWindow.update_search_status_label(ui_building=True))
            # Debug
            self.signals.finished.connect(lambda: logging.info("Finished Search Thread!\n"))
            # Launching UI
            self.signals.finished.connect(lambda: FF_Search_UI.SearchWindow(*SEARCH_OUTPUT))

            # Connecting the menu-bar log to the signals
            self.signals.starting.connect(lambda: self.ui_logger.update("Starting Search..."))
            self.signals.scanning.connect(lambda: self.ui_logger.update("Scanning..."))
            self.signals.indexing.connect(lambda: self.ui_logger.update("Indexing..."))
            self.signals.indexing_name.connect(
                lambda: self.ui_logger.update(f"Indexing Name {data_name.rstrip(':')}..."))
            self.signals.indexing_system_files.connect(lambda: self.ui_logger.update("Indexing System Files..."))
            self.signals.indexing_files_folders.connect(
                lambda: self.ui_logger.update("Indexing exclude or include folders or files ..."))
            self.signals.indexing_file_groups.connect(lambda: self.ui_logger.update("Filtering for file type..."))
            self.signals.indexing_dump_files.connect(lambda: self.ui_logger.update("Removing dump files..."))
            self.signals.indexing_excluded.connect(lambda: self.ui_logger.update("Filtering excluded files..."))
            self.signals.indexing_c_date.connect(lambda: self.ui_logger.update("Indexing date created..."))
            self.signals.indexing_m_date.connect(lambda: self.ui_logger.update("Indexing date modified..."))
            self.signals.indexing_file_size.connect(lambda: self.ui_logger.update("Indexing file size..."))
            self.signals.indexing_file_content.connect(lambda: self.ui_logger.update("Indexing file contains..."))
            self.signals.sorting_name.connect(lambda: self.ui_logger.update("Sorting results by name..."))
            self.signals.sorting_size.connect(lambda: self.ui_logger.update("Sorting results by size..."))
            self.signals.sorting_c_date.connect(lambda: self.ui_logger.update("Sorting results by creation date..."))
            self.signals.sorting_m_date.connect(lambda:
                                                self.ui_logger.update("Sorting results by modification date..."))
            self.signals.sorting_path.connect(lambda: self.ui_logger.update("Sorting results by path..."))
            self.signals.sorting_reversed.connect(lambda: self.ui_logger.update("Reversing results..."))
            self.signals.caching.connect(lambda: self.ui_logger.update("Caching search results..."))
            self.signals.building_ui.connect(lambda: self.ui_logger.update("Building UI..."))
            self.signals.finished.connect(lambda: self.ui_logger.close())

            # Starting the Thread
            self.thread.start(
                lambda: self.searching(
                    data_name=data_name, data_name_specifier=data_name_specifier, data_consider_case=data_consider_case,
                    data_similarity=data_similarity,
                    data_filetype=data_filetype, data_file_group=data_file_group,
                    data_file_type_mode=data_file_type_mode,
                    data_file_size_min=data_file_size_min, data_file_size_max=data_file_size_max,
                    data_search_from=data_search_from_valid,
                    data_search_for=data_search_for, data_library=data_library,
                    data_folder_depth=data_folder_depth, data_folder_depth_custom=data_folder_depth_custom,
                    data_content=data_content,
                    data_time=unix_time_list,
                    data_sort_by=data_sort_by, data_reverse_sort=data_reverse_sort,
                    data_excluded_files=data_excluded_files, new_cache_file=new_cache_file, parent=parent))

            # Debug
            logging.debug("Finished Setting up QThreadPool!")

    # The search engine
    def searching(self, data_name, data_name_specifier, data_consider_case, data_similarity, data_filetype,
                  data_file_size_min, data_file_size_max, data_library,
                  data_search_from, data_search_for, data_content, data_time, data_sort_by, data_reverse_sort,
                  data_file_group, data_file_type_mode, data_folder_depth,
                  data_folder_depth_custom, data_excluded_files, new_cache_file, parent):
        # Debug
        logging.info("Starting Search...")
        self.signals.starting.emit()

        # Saving time before scanning
        time_before_start = perf_counter()

        # Remove the "." and any star because they are added later
        data_filetype = data_filetype.lstrip(".*")

        # Lower Arguments to remove case sensitivity
        if not data_consider_case or data_name_specifier == "is similar to:":
            data_name: str = data_name.lower()
        # Convert percentage to ratio
        data_similarity /= 100
        data_filetype = data_filetype.lower()

        '''
        There are multiple possibilities in unicode on how to display some characters (for example ä, ü, ö).
        A decomposed form NFD (normal form D) ä = a + ¨
        and a composed one NFC (normal form C) ä = ä
        On macOS the filesystem returns the names for files created locally as NFD while everyone else does NFC.
        It is possible to place NFC characters in macOS file names. But not for a normal user.

        If you have problems on macOS with composed/decomposed unicode character remove the four lines of code below.
        '''
        # Normalising arguments (see above)
        if platform == "darwin":
            data_name = normalize("NFD", data_name)
            data_filetype = normalize("NFD", data_filetype)

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

        # Checking if check for file type is needed
        if ((set(data_file_group) != set(FF_Files.FILE_FORMATS.keys()) and data_file_type_mode == "predefined") or
                (data_filetype != "" and data_file_type_mode == "custom")):
            logging.debug("File type checking is needed")

            # Creating a set and adding every needed file format to it
            allowed_filetypes_set = set()
            disallowed_filetypes_set = set()  # Needed if "other" is activated and user chose "predefined"

            if data_file_type_mode == "predefined":
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

            elif data_file_type_mode == "custom":
                # Semicolons can be used for entering multiple possible file types,
                # removing all spaces as filetypes have none (at least sane people don't use them)
                # removing all the dots (the most left on already has been removed)
                allowed_filetypes_set = data_filetype.replace(" ", "").replace(";.", ";").split(";")

            # Making tuples out of the sets for better performance
            allowed_filetypes = tuple(allowed_filetypes_set)
            disallowed_filetypes = tuple(disallowed_filetypes_set)

        else:
            logging.debug("File type checking is NOT needed")
            # Because checking isn't needed and wwe don't want automated tools to flag this as "possibly unassigned"
            allowed_filetypes = None
            disallowed_filetypes = None

        # Processing folder depth input
        if data_folder_depth == "Unlimited":
            # folder_depth_global_limit is basically just the amount of "/" (on macOS)
            # that are allowed in the path of a file
            # -1 means infinite
            folder_depth_global_limit = -1
        elif data_folder_depth == "No subfolders":
            folder_depth_global_limit = data_search_from.count(os.sep)
        elif data_folder_depth == "Custom":
            # Using data_search_from.count(os.sep) as the depth is relative to the directory that is searched in
            folder_depth_global_limit = data_search_from.count(os.sep) + data_folder_depth_custom
        else:
            # Shouldn't be reached
            logging.fatal("Error in code while processing folder depth limit")
            raise ValueError

        # Debug
        logging.info("Starting Scanning...")
        # Update the menu-bar status
        self.signals.scanning.emit()

        '''Checking, if a Cache File exists in any fitting directory'''
        newest_fitting_cache_file = None
        newest_fitting_cache_file_c_date = 0

        for cache_file in os.listdir(FF_Files.CACHED_SEARCHES_FOLDER):
            # Looks if there is a cache file for a higher directory add a folder separator ("-") so that files
            # from the same directory with a similar name aren't mistaken for files from a parent directory
            # A dollar sign marks the beginning of the absolute depth limit of the cache file
            # "-" marks a folder separator
            # comparable_cache_file is basically the original search path but all "/" are replaced with "-"
            comparable_cache_file = ((cache_file.removesuffix(".FFCache")[:cache_file.rfind("$")]) + "-")

            if (data_search_from.replace(os.sep, "-") + "-").startswith(comparable_cache_file):
                # Date created and global folder depth (which must match) from separate file
                with open(os.path.join(FF_Files.CACHE_METADATA_FOLDER, cache_file)) as time_file:
                    metadata = load(time_file)
                    cache_file_c_date = metadata["c_time"]
                    cache_file_depth = metadata["global_depth_limit"]

                # Looks if the creation time is newer than the current best fitting file
                # Also check if the global depth matches up
                if ((cache_file_c_date > newest_fitting_cache_file_c_date) and
                        (cache_file_depth == folder_depth_global_limit)):
                    newest_fitting_cache_file_c_date = cache_file_c_date
                    newest_fitting_cache_file = os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, cache_file)

        # If there is a fitting cache file and user didn't request new cache file to be created
        if newest_fitting_cache_file is not None and not new_cache_file:
            # Debug
            logging.info(f"Scanning using cached data from {newest_fitting_cache_file}"
                         f" created at {time.ctime(newest_fitting_cache_file_c_date)}")

            used_cache = True
            # Load cache
            with open(newest_fitting_cache_file) as search_results:
                load_input = load(search_results)

            # If the found cache file is form the same directory as the one the search was for
            if newest_fitting_cache_file == FF_Files.path_to_cache_file(data_search_from, folder_depth_global_limit):
                # Debug
                logging.debug("Cache file from the same directory as search")

                found_path_set = set(load_input["found_path_set"])
                type_dict = load_input["type_dict"]

            # If it's a cache file from a parent dir
            else:
                # Debug
                logging.debug("Cache file from an higher directory, sorting out unnecessary files")

                found_path_set = set(load_input["found_path_set"])
                type_dict = load_input["type_dict"]

                keep_time = time.perf_counter()

                # Remove irrelevant paths
                for found_item in found_path_set.copy():
                    if not found_item.startswith(data_search_from):
                        found_path_set.remove(found_item)
                        del type_dict[found_item]

                # make sure the path isn't in the list
                try:
                    found_path_set.remove(data_search_from)
                except (KeyError, NameError):
                    pass
                try:
                    del type_dict[data_search_from]
                except KeyError:
                    pass

                logging.debug(f"Sorting out unnecessary files took {perf_counter() - keep_time} sec.")

        # If there is no newer cache file
        else:

            # Create empty lists for the files
            found_path_set: set = set()
            type_dict: dict = {}

            used_cache = False

            # Going through every file and every folder using the os.walk() method
            # Saving every file to found_path_set and the type (file or folder) to found_path_dict
            # Only running this if folder_depth_global_limit == -1 which means that the folder depth is unlimited
            if folder_depth_global_limit == -1:
                # Not putting this into its own function as it would be noticeably slower
                for (root, dirs, files) in os.walk(data_search_from):
                    for file in files:
                        # Saving types to the dictionaries
                        type_dict[os.path.join(root, file)] = "file"
                        # Saving the path to a list for fast access
                        found_path_set.add(os.path.join(root, file))

                    for directory in dirs:
                        # Saving types to the dictionaries
                        type_dict[os.path.join(root, directory)] = "folder"

                        # Saving the path to a list for fast access
                        found_path_set.add(os.path.join(root, directory))
            # If folder depth is used
            else:
                # Not putting this into its own function as it would be noticeably slower
                for (root, dirs, files) in os.walk(data_search_from):
                    if root.count(os.sep) <= folder_depth_global_limit:
                        # If depth is in range
                        for file in files:
                            # Saving types to the dictionaries
                            type_dict[os.path.join(root, file)] = "file"
                            # Saving the path to a list for fast access
                            found_path_set.add(os.path.join(root, file))
                        for directory in dirs:
                            # Saving types to the dictionaries
                            type_dict[os.path.join(root, directory)] = "folder"

                            # Saving the path to a list for fast access
                            found_path_set.add(os.path.join(root, directory))
                    else:
                        # Removing element from this list prevent python from visiting these directories
                        for directory in dirs:
                            dirs.remove(directory)

        # Saving time
        time_after_searching = perf_counter() - time_before_start

        # Debug
        logging.info("Starting Indexing...")
        # Update the menu-bar status
        self.signals.indexing.emit()

        # Creating a copy because items can't be removed while iterating over a set
        copy_found_path_set = found_path_set.copy()
        original_found_path_set = found_path_set.copy()

        # Applies filters, when they don't match the function remove them from the found_path_dict
        # Name
        logging.info(f"Indexing Name \"{data_name_specifier}\"...")
        self.signals.indexing_name.emit()
        if data_name != "":
            # Name is equal
            # Ignoring case
            if data_name_specifier == "is:" and not data_consider_case:
                # Scan every file
                for name_file in found_path_set:
                    if not fnmatch(os.path.basename(name_file).lower(), data_name):
                        copy_found_path_set.remove(name_file)
            # Considering case
            if data_name_specifier == "is:" and data_consider_case:
                for name_file in found_path_set:
                    if not fnmatch(os.path.basename(name_file), data_name):
                        copy_found_path_set.remove(name_file)

            # Name contains
            elif data_name_specifier == "contains:" and not data_consider_case:
                for name_file in found_path_set:
                    if not (data_name in os.path.basename(name_file).lower()):
                        copy_found_path_set.remove(name_file)
            elif data_name_specifier == "contains:" and data_consider_case:
                for name_file in found_path_set:
                    if not (data_name in os.path.basename(name_file)):
                        copy_found_path_set.remove(name_file)

            # Name starts with
            elif data_name_specifier == "begins with:" and not data_consider_case:
                for name_file in found_path_set:
                    if not os.path.basename(name_file).lower().startswith(data_name):
                        copy_found_path_set.remove(name_file)
            elif data_name_specifier == "begins with:" and data_consider_case:
                for name_file in found_path_set:
                    if not os.path.basename(name_file).startswith(data_name):
                        copy_found_path_set.remove(name_file)

            # Name (without file extension) ends with
            elif data_name_specifier == "ends with:" and not data_consider_case:
                for name_file in found_path_set:
                    # Splitting the name so the file extension doesn't matter
                    if not os.path.basename(name_file).split(".")[0].lower().endswith(data_name):
                        copy_found_path_set.remove(name_file)
            elif data_name_specifier == "ends with:" and data_consider_case:
                for name_file in found_path_set:
                    # Splitting the name so the file extension doesn't matter
                    if not os.path.basename(name_file).split(".")[0].endswith(data_name):
                        copy_found_path_set.remove(name_file)

            # Fuzzy search
            elif data_name_specifier == "is similar to:":
                for name_file in found_path_set:
                    # Using difflib.SequenceMatcher to get a matching ratio,
                    # based on the gestalt pattern matching algorithm.
                    if difflib.SequenceMatcher(
                            None, data_name, os.path.basename(name_file).lower()).ratio() < data_similarity:
                        copy_found_path_set.remove(name_file)

            # Doesn't contain
            elif data_name_specifier == "doesn't contain:" and not data_consider_case:
                # Scan every file
                for name_file in found_path_set:
                    if data_name in os.path.basename(name_file).lower():
                        copy_found_path_set.remove(name_file)
            elif data_name_specifier == "doesn't contain:" and data_consider_case:
                # Scan every file
                for name_file in found_path_set:
                    if data_name in os.path.basename(name_file):
                        copy_found_path_set.remove(name_file)

            # RegEx
            elif data_name_specifier == "in RegEx:":
                if data_consider_case:
                    re_flags = 0
                else:
                    re_flags = re.IGNORECASE
                for name_file in found_path_set:
                    # re is the python RegEx module
                    if not re.match(data_name, os.path.basename(name_file), re_flags):
                        copy_found_path_set.remove(name_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Search in System Files
        logging.info("Indexing System Files...")
        self.signals.indexing_system_files.emit()
        if not data_library:
            if platform == "darwin":
                # Scan every file
                for library_file in found_path_set:
                    if (library_file.startswith("/private")
                            or library_file.startswith("/var")
                            or library_file.startswith("/System")
                            or "/Library" in library_file
                            or "/." in library_file):
                        # Remove the file
                        copy_found_path_set.remove(library_file)
            elif platform == "win32" or platform == "cygwin":
                # Scan every file
                for library_file in found_path_set:
                    if (library_file.startswith("C:\\Windows")
                            or library_file.startswith("C:\\ProgramData")
                            or "\\AppData" in library_file):
                        # Remove the file
                        copy_found_path_set.remove(library_file)
            elif platform == "linux":
                # Scan every file
                for library_file in found_path_set:
                    if (library_file.startswith("/var")
                            or library_file.startswith("/lib")
                            or "/." in library_file):
                        # Remove the file
                        copy_found_path_set.remove(library_file)
            else:
                logging.fatal("OS not supported")

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Exclude or Include Folders or Files
        logging.info("Indexing Exclude or Include Folders or Files...")
        self.signals.indexing_files_folders.emit()
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
        logging.info("Filtering for file types...")
        self.signals.indexing_file_groups.emit()

        # Checking is not needed
        if allowed_filetypes is not None:
            # if "other" files is activated
            if "*" in allowed_filetypes:
                for file_type_file in found_path_set:
                    for file_ending in disallowed_filetypes:
                        if file_type_file.lower().endswith(f".{file_ending}"):
                            copy_found_path_set.remove(file_type_file)

            else:
                for file_type_file in found_path_set:
                    for file_ending in allowed_filetypes:
                        if file_type_file.lower().endswith(f".{file_ending}"):
                            break
                        else:
                            pass
                    else:
                        copy_found_path_set.remove(file_type_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Filter some unnecessary System Files
        logging.info("Removing dump files...")
        self.signals.indexing_dump_files.emit()

        for system_file in found_path_set:
            basename = os.path.basename(system_file).lower()
            if basename in (".ds_store", ".localized", "desktop.ini", "thumbs.db"):
                copy_found_path_set.remove(system_file)

        # Making the copy and the original the same
        found_path_set = copy_found_path_set.copy()

        # Excluded Files
        logging.info("Filtering excluded files...")
        self.signals.indexing_excluded.emit()
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
        self.signals.indexing_c_date.emit()
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
        logging.info("Indexing date modified...")
        self.signals.indexing_m_date.emit()
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
        self.signals.indexing_file_size.emit()
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
        self.signals.indexing_file_content.emit()
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
            self.signals.sorting_name.emit()
            found_path_list.sort(key=Sort.name, reverse=data_reverse_sort)

        elif data_sort_by == "File Size":
            logging.info("Sorting list by size...")
            self.signals.sorting_size.emit()
            found_path_list.sort(key=Sort.size, reverse=not data_reverse_sort)

        elif data_sort_by == "Date Created":
            logging.info(f"Sorting list by creation date on {platform}...")
            self.signals.sorting_c_date.emit()

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
            self.signals.sorting_m_date.emit()
            found_path_list.sort(key=Sort.m_date, reverse=not data_reverse_sort)

        elif data_sort_by == "Path":
            logging.info("Sorting list by path...")
            self.signals.sorting_path.emit()
            found_path_list.sort(key=lambda sort_file: sort_file.lower(), reverse=data_reverse_sort)

        else:
            logging.info("Skipping Sorting")
            if data_reverse_sort:
                logging.debug("Reversing Results...")
                self.signals.sorting_reversed.emit()
                found_path_list = list(reversed(found_path_list))

        # Caching Results with json
        # Testing if cache file exist, if it doesn't or isn't from the exact directory exist it caches scanned files
        if (not used_cache or
                newest_fitting_cache_file != FF_Files.path_to_cache_file(data_search_from, folder_depth_global_limit)):
            # Debug and menu-bar log
            logging.info("Caching Search Results...")
            self.signals.caching.emit()

            # Creating file
            with open(FF_Files.path_to_cache_file(data_search_from, folder_depth_global_limit), "w") as result_file:
                # Dumping with json
                dump({
                    "found_path_set": list(original_found_path_set),
                    "type_dict": type_dict}, result_file)

            # Saving the cache creation time in a separate file for faster access
            with open(FF_Files.path_to_cache_file(data_search_from, folder_depth_global_limit, metadata=True),
                      "w") as time_write_file:
                if used_cache:
                    # Determining the number of parent directories by counting the default separators in the path
                    # and then adding this value to the c_Time so the more specified cache gets used rather than
                    # the broader cache which originated from the broader one.
                    # Dividing by 10 so to only add fractions of a seconds to the c_time as
                    # to not get ranked over newer caches.
                    # Doing this so the already specialized cache gets used preferably
                    c_time_adjust = data_search_from.count(os.sep) / 10
                    logging.debug(f"Cache time {newest_fitting_cache_file_c_date} + adjuster: {c_time_adjust} "
                                  f"= {newest_fitting_cache_file_c_date + c_time_adjust}")

                    # Used old cache, save old time
                    dump({"c_time": newest_fitting_cache_file_c_date + c_time_adjust,
                          "cache_version": FF_Files.FF_CACHE_VERSION,
                          "original_cache_file": newest_fitting_cache_file,
                          "global_depth_limit": folder_depth_global_limit,
                          "path": data_search_from}, time_write_file)

                else:
                    logging.debug("Created brand new cache..")
                    # New cache created
                    dump({"c_time": time.time(),
                          "cache_version": FF_Files.FF_CACHE_VERSION,
                          "original_cache_file": FF_Files.path_to_cache_file(data_search_from,
                                                                             folder_depth_global_limit),
                          "global_depth_limit": folder_depth_global_limit,
                          "path": data_search_from}, time_write_file)
                    newest_fitting_cache_file = FF_Files.path_to_cache_file(data_search_from, folder_depth_global_limit)

        else:
            logging.info("Cache file already exist, skipping caching...")

        # Updating search status indicator
        self.signals.waiting.emit()

        # Calculating time
        time_after_sorting = perf_counter() - (time_after_indexing + time_after_searching + time_before_start)
        time_total = perf_counter() - time_before_start

        # Cleaning Memory
        del type_dict, found_path_set, original_found_path_set

        # Debug
        logging.info("Finished Searching!")
        self.signals.building_ui.emit()

        # The parameter passed on to the UI builder
        global SEARCH_OUTPUT
        SEARCH_OUTPUT = [{"time_total": time_total,
                          "time_searching": time_after_searching,
                          "time_indexing": time_after_indexing,
                          "time_sorting": time_after_sorting},
                         found_path_list, data_search_from, newest_fitting_cache_file, parent]

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
SEARCH_OUTPUT: ({str: float}, list, str, str, QWidget)

ACTIVE_SEARCH_THREADS: int = 0
