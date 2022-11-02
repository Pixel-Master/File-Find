# This File is a part of File-Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the class for the search engine

# Imports
import os
from fnmatch import fnmatch
from pickle import dump, load
from time import time, mktime

# PyQt6 Gui Imports
from PyQt6.QtWidgets import QFileDialog, \
    QDateEdit, QMessageBox

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Search_UI


# Sorting algorithms
class sort:

    # Sort by Size
    @staticmethod
    def size(file):
        if os.path.isdir(file):
            file_size_list_obj = 0
            # Gets the size
            for path, dirs, files in os.walk(file):
                for file in files:
                    try:
                        file_size_list_obj += os.path.getsize(os.path.join(path, file))
                    except FileNotFoundError or ValueError:
                        continue
        elif os.path.isfile(file):
            try:
                file_size_list_obj = os.path.getsize(file)
            except FileNotFoundError or ValueError:
                return -1
        else:
            return -1
        if os.path.islink(file):
            return -1
        else:
            return file_size_list_obj

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


# Loading a saved search
class load_search:
    def __init__(self, parent):
        load_dialog = QFileDialog.getOpenFileName(parent, "Export File-Find Search", FF_Files.Saved_SearchFolder,
                                                  "*.FFSave;")
        load_file = load_dialog[0]

        # Creating Cache File, because of the Reload Button
        if load_file != "":
            with open(load_file, "rb") as OpenedFile:
                saved_file_content = load(OpenedFile)
                if not os.path.exists(
                        os.path.join(FF_Files.Cached_SearchesFolder,
                                     f"loaded from {load_file}.FFSearch".replace("/", "-"))):
                    with open(os.path.join(FF_Files.Cached_SearchesFolder,
                                           f"loaded from {load_file}.FFSearch".replace("/", "-")),
                              "wb") as CachedSearch:
                        dump(saved_file_content, file=CachedSearch)
                FF_Search_UI.Search_Window(0, 0, 0, 0, saved_file_content, f"loaded from {load_file}", parent)


# The Search Engine
class search:
    def __init__(self, data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                 data_search_from, data_folders, data_content, edits_list, data_sort_by, data_reverse_sort,
                 data_fn_match, parent):

        # Fetching Errors
        if data_name != "" and data_in_name != "" or data_name != "" and data_filetype != "":
            FF_Additional_UI.msg.show_critical_messagebox("NAME ERROR!",
                                                          "Name Error!\n\nFile Name and in Name or File Type can't "
                                                          "be used together", parent=None)

        # Warning
        elif QMessageBox.information(parent,
                                     "This may take some Time!",
                                     "This may take some Time!\nPress OK to Start Searching",
                                     QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) \
                == QMessageBox.StandardButton.Cancel:
            print("Cancelled Searching!")

        # Start Searching
        else:
            '''Converting the output of QDateEdit into the unix time by first using QDateEdit.date() to get 
            something like this: QDate(1,3,2000), after that using QDate.toPyDate to get this: 1-3-2000, 
            than we can use .split("-") to convert 1-3-2000 into a list [1,3,2000], after that we use time.mktime 
            to get the unix time format that means something like, that: 946854000.0, only to match this with 
            os.getctime, what we can use to get the creation date of a file. 

            Yea it would be easier if Qt had a function to get the unix time
            '''
            unix_time_list = []

            def conv_qdate_to_unix_time(input_edit: QDateEdit, pos: int = 1):
                time_list = str(input_edit.date().toPyDate()).split("-")
                unix_time = mktime(
                    (int(time_list[0]), int(time_list[1]), int(time_list[2]) + pos, 0, 0, 0, 0, 0, 0))
                return unix_time

            for time_drop_down in edits_list:
                time_to_add_to_time_list = conv_qdate_to_unix_time(time_drop_down,
                                                                   edits_list.index(time_drop_down) % 2)
                unix_time_list.append(time_to_add_to_time_list)

            self.search_start(data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max,
                              data_library, data_search_from, data_folders, data_content, unix_time_list, data_sort_by,
                              data_reverse_sort, data_fn_match, parent)
            '''future = executor.submit(lambda: search(data_name=e1.text(), data_in_name=e2.text(),                   
                                         data_filetype=e3.text(), data_file_size_min=e4.text(), 
                                         data_file_size_max=e5.text(), data_library=rb_library1.isChecked(), 
                                         data_search_from=os.getcwd(), data_content=e6.text(), 
                                         data_folders=rb_folder1.isChecked(), data_time=unix_time_list, 
                                         data_fn_match=e7.text(), data_sort_by=combobox_sorting.currentText(), 
                                         data_reverse_sort=rb_reverse_sort1.isChecked())) return_value = 
                                         future.result() print(return_value) '''

    # The search engine
    @staticmethod
    def search_start(data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                     data_search_from, data_folders, data_content, data_time, data_sort_by, data_reverse_sort,
                     data_fn_match, parent):
        # Creates empty lists for the files
        matched_path_list = []
        found_path_list = []

        # Saving time before scanning
        time_before_start = time()

        # Lower Arguments
        data_name = data_name.lower()
        data_in_name = data_in_name.lower()

        # Checking if data_time is needed
        DEFAULT_TIME_INPUT_LIST = [946681200.0, 946767600.0, 946681200.0, 946767600.0]
        if data_time == DEFAULT_TIME_INPUT_LIST:
            data_time_needed = False
        else:
            data_time_needed = True

        # Debug
        print("\nStarting Scanning...")

        '''Checking, if Cache File exist, if not it goes through every file in the directory and saves it. If It 
        Exist it loads the Cache File in to found_path_list '''
        if os.path.exists(
                os.path.join(FF_Files.Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch")):
            print("Scanning using cached Data..")
            with open(
                    os.path.join(FF_Files.Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch"),
                    "rb") as SearchResults:
                found_path_list = load(SearchResults)

        else:
            for (roots, dirs, files) in os.walk(data_search_from):
                for file in files:
                    found_path_list.append(os.path.join(roots, file))
                for directory in dirs:
                    found_path_list.append(os.path.join(roots, directory))

        time_after_searching = time() - time_before_start

        # Debug
        print("\nStarting Indexing...\n")
        # Applies filters, when they don't match it continues.
        for found_file in found_path_list:

            # Looks for basename to be faster
            basename = os.path.basename(found_file)
            lower_basename = os.path.basename(found_file).lower()

            # Name
            if data_name == lower_basename or data_name == "":
                pass
            else:
                continue
            # In name
            if data_in_name in lower_basename or data_in_name == "":
                pass
            else:
                continue
            # File Ending
            if basename.endswith(f".{data_filetype}") or data_filetype == "":
                pass
            else:
                continue
            # Fn match
            if data_fn_match != "":
                if not fnmatch(found_file, data_fn_match):
                    continue

            # Search in System Files
            if not data_library:
                if "/Library" in found_file:
                    continue

            # Search for Folders
            if not data_folders:
                if os.path.isdir(found_file):
                    continue

            # Search for Date Modified, Created
            # Checking if
            if data_time_needed:
                # Using os.stat because os.path.getctime returns a wrong date
                try:
                    file_c_time = os.stat(found_file).st_birthtime
                    file_m_time = os.path.getmtime(found_file)
                except FileNotFoundError:
                    continue
                # Checking for file time and which values in data_time are modified
                if data_time[0] <= file_c_time <= data_time[1] != DEFAULT_TIME_INPUT_LIST[1]:
                    pass
                elif data_time[0] != DEFAULT_TIME_INPUT_LIST[0] and data_time[1] != DEFAULT_TIME_INPUT_LIST[1]:
                    continue
                if data_time[2] <= file_m_time <= data_time[3] != DEFAULT_TIME_INPUT_LIST[3]:
                    pass
                elif data_time[3] != DEFAULT_TIME_INPUT_LIST[3] and data_time[2] != DEFAULT_TIME_INPUT_LIST[2]:
                    continue

            # Filter File Size
            if data_file_size_min != "":
                if os.path.isfile(found_file):
                    if int(data_file_size_max) >= int(
                            os.path.getsize(found_file)) >= int(data_file_size_min):
                        pass
                    else:
                        continue
                elif os.path.isdir(found_file):
                    folder_size = 0
                    # Gets the size
                    for path, dirs, files in os.walk(found_file):
                        for file in files:
                            try:
                                folder_size += os.path.getsize(os.path.join(path, file))
                            except FileNotFoundError:
                                print("File Not Found!", str(os.path.join(path, file)))
                                continue
                    if int(data_file_size_max) >= folder_size >= int(data_file_size_min):
                        pass
                    else:
                        continue

            # Contains
            if data_content != "":
                does_contain = False
                try:
                    with open(found_file, "r") as ContentFile:
                        for line in ContentFile:
                            if data_content in line:
                                does_contain = True
                                break
                except (UnicodeDecodeError, FileNotFoundError, OSError):
                    continue
                else:
                    if not does_contain or os.path.isdir(found_file):
                        continue

            # Filter some unnecessary System Files
            if basename == ".DS_Store" or basename == ".localized" or basename == "desktop.ini" \
                    or basename == "Thumbs.db":
                continue

            # Add the File to matched_path_list
            matched_path_list.append(found_file)

        # Prints out seconds needed and the matching files
        print(f"Found {len(matched_path_list)} Files and Folders")
        time_after_indexing = time() - (time_after_searching + time_before_start)

        # Sorting
        if data_sort_by == "File Name":
            print("\nSorting List by Name...")
            matched_path_list.sort(key=sort.name, reverse=data_reverse_sort)
        elif data_sort_by == "File Size":
            print("\nSorting List by Size..")
            matched_path_list.sort(key=sort.size, reverse=not data_reverse_sort)
        elif data_sort_by == "Date Created":
            print("\nSorting List by creation date..")
            matched_path_list.sort(key=sort.c_date, reverse=not data_reverse_sort)
        elif data_sort_by == "Date Created":
            print("\nSorting List by modified date..")
            matched_path_list.sort(key=sort.m_date, reverse=not data_reverse_sort)
        else:
            if data_reverse_sort:
                matched_path_list = list(reversed(matched_path_list))

        # Saving Results with pickle
        print("\nSaving Search Results...")
        with open(os.path.join(FF_Files.Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch"),
                  "wb") as resultFile:
            dump(list(found_path_list), resultFile)
        time_after_sorting = time() - (time_after_indexing + time_after_searching + time_before_start)
        time_total = time() - time_before_start
        print(f"\nSeconds needed:\nScanning: {time_after_searching}\nIndexing: {time_after_indexing}\nSorting: "
              f"{time_after_sorting}\nTotal: {time_total}")
        print("\nFiles found:", len(matched_path_list))

        # Launches the GUI
        FF_Search_UI.Search_Window(time_total, time_after_searching, time_after_indexing, time_after_sorting,
                                   matched_path_list, data_search_from, parent)
