# Find Files easier with File Find
# Main Script, execute this for running File-Find
import os
from pickle import dump, load
from time import time, ctime, mktime

# PyQt5 Gui Imports
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QFont, QIntValidator, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QPushButton, QRadioButton, QFileDialog, \
    QListWidget, QLineEdit, QButtonGroup, QDateEdit, QFrame, QComboBox, QMessageBox
from pyperclip import copy

# Projects Library
import FFkit
import FFvars


# The GUI for the search results
def search_ui(time_total, time_searching, time_indexing, time_sorting, matched_list, search_path):
    time_before_building = time()

    # Window setup
    # Define the window
    search_result_ui = QMainWindow(Root_Window)
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
            FFkit.show_critical_messagebox("Error!", f"No Program found to open {selected_file}", search_result_ui)
        print(f"Opened: {selected_file}")

    def open_in_finder():
        selected_file = result_listbox.currentItem().text()

        if os.system("open -R " + str(selected_file.replace(" ", "\\ "))) != 0:
            FFkit.show_critical_messagebox("Error!", f"File not Found {selected_file}", search_result_ui)
        print(f"Opened in Finder: {selected_file}")

    def copy_path():
        selected_file = result_listbox.currentItem().text()
        copy(selected_file)
        print(f"Copied Path: {selected_file}")
        FFkit.show_info_messagebox("Successfully copied!", f"Successfully copied Path:\n{selected_file}!",
                                   search_result_ui)

    def copy_name():
        selected_file = result_listbox.currentItem().text()
        copy(os.path.basename(selected_file))
        print(f"Copied File-Name: {os.path.basename(selected_file)}")
        FFkit.show_info_messagebox("Successfully copied!",
                                   f"Successfully copied File Name:\n{os.path.basename(selected_file)} !",
                                   search_result_ui)

    # Show more time info's
    def show_time_stats():
        FFkit.show_info_messagebox("Time Stats", f"Time needed:\n\nScanning: {round(time_searching, 3)}\nIndexing:"
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
                # result_listbox.takeItem()
                matched_list.index(result_listbox.currentItem().text())
                print(f"File Does Not exist: {file}")
                removed_list.append(file)
        with open(os.path.join(Cached_SearchesFolder, search_path.replace("/", "-") + ".FFSearch"), "rb") as SearchFile:
            cached_files = list(load(SearchFile))
        for cached_file in cached_files:
            if cached_file in removed_list:
                cached_files.remove(file)
        with open(os.path.join(Cached_SearchesFolder, search_path.replace("/", "-") + ".FFSearch"), "wb") as SearchFile:
            dump(cached_files, SearchFile)
        print(f"Reloaded found Files and removed {len(removed_list)} in"
              f" {round(time() - time_before_reload, 3)} sec.")
        FFkit.show_info_messagebox("Reloaded!", f"Reloaded found Files and removed {len(removed_list)}"
                                                f" in {round(time() - time_before_reload, 3)} sec.", search_result_ui)
        objects_text.setText(f"Files found: {len(matched_list)}")
        del cached_files, removed_list

    # Save Search
    def save_search():
        save_dialog = QFileDialog.getSaveFileName(search_result_ui, "Export File-Find Search", Saved_SearchFolder,
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
        button = QPushButton(search_result_ui)
        button.setText(text)
        button.clicked.connect(command)
        button.show()
        button.adjustSize()
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
    help_button = generate_button(" Help", command=lambda: FFkit.help_ui(Root_Window))
    help_button.move(740, 0)
    help_button_font = QFont("Arial", 25)
    help_button_font.setBold(True)
    help_button.setFont(help_button_font)
    # Color
    help_button.setStyleSheet("color: #b50104;")
    # Icon
    help_button.setIcon(QIcon(os.path.join(AssetsFolder, "Info_button_img_small.png")))
    help_button.setIconSize(QSize(25, 25))
    # Place
    help_button.resize(120, 50)
    help_button.move(670, 10)

    # Time stat Button
    show_time = generate_button(None, show_time_stats, )
    # Icon
    show_time.setIcon(QIcon(os.path.join(AssetsFolder, "Time_button_img_small.png")))
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

    # Update Seconds needed Label
    seconds_text.setText(f"Time needed: {round(time_total + (time() - time_before_building), 3)}")
    seconds_text.adjustSize()

    # Time building UI
    time_building = time() - time_before_building
    print("Time spent building the UI:", time_building)


# The search engine
def search(data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
           data_search_from, data_folders, data_content, data_time, data_sort_by, data_reverse_sort):
    # Creates empty lists for the files
    matched_path_list = []
    found_path_list = []

    # Saving time before scanning
    time_before_start = time()

    # Lower Arguments
    data_name = data_name.lower()
    data_in_name = data_in_name.lower()

    # Checking if data_time is needed
    if data_time == [946681200.0, 946681200.0, 946681200.0, 946681200.0]:
        data_time_needed = False
    else:
        data_time_needed = True

    # Debug
    print("\nStarting Scanning...")

    '''
    Checking, if Cache File exist, if not it goes through every file in the directory and saves it. If It Exist it 
    loads the Cache File in to found_path_list 
    '''
    if os.path.exists(os.path.join(Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch")):
        print("Scanning using cached Data..")
        with open(os.path.join(Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch"),
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
            file_c_time = os.stat(found_file).st_birthtime
            file_m_time = os.path.getmtime(found_file)

            # Checking for file time and which values in data_time are modified
            if data_time[0] <= file_c_time <= data_time[1] != 946681200.0:
                pass
            elif data_time[0] != 946681200.0 and data_time[1] != 946681200.0:
                continue
            if data_time[2] <= file_m_time <= data_time[3] != 946681200.0:
                pass
            elif data_time[3] != 946681200.0 and data_time[2] != 946681200.0:
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
        if basename == ".DS_Store" or basename == ".localized" or basename == "desktop.ini" or basename == "Thumbs.db":
            continue

        # Add the File to matched_path_list
        matched_path_list.append(found_file)

    # Prints out seconds needed and the matching files
    print(f"Found {len(matched_path_list)} Files and Folders")
    time_after_indexing = time() - (time_after_searching + time_before_start)

    # Sorting
    if data_sort_by == "File Name":
        print("\nSorting List by Name...")
        matched_path_list.sort(key=FFkit.SORT.name, reverse=data_reverse_sort)
    elif data_sort_by == "File Size":
        print("\nSorting List by Size..")
        matched_path_list.sort(key=FFkit.SORT.size, reverse=not data_reverse_sort)
    elif data_sort_by == "Date Created":
        print("\nSorting List by creation date..")
        matched_path_list.sort(key=FFkit.SORT.c_date, reverse=not data_reverse_sort)
    elif data_sort_by == "Date Created":
        print("\nSorting List by modified date..")
        matched_path_list.sort(key=FFkit.SORT.m_date, reverse=not data_reverse_sort)
    else:
        if data_reverse_sort:
            matched_path_list = list(reversed(matched_path_list))

    # Saving Results with pickle
    print("\nSaving Search Results...")
    with open(os.path.join(Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch"), "wb") \
            as resultFile:
        dump(list(found_path_list), resultFile)
    time_after_sorting = time() - (time_after_indexing + time_after_searching + time_before_start)
    time_total = time() - time_before_start
    print(f"\nSeconds needed:\nScanning: {time_after_searching}\nIndexing: {time_after_indexing}\nSorting: "
          f"{time_after_sorting}\nTotal: {time_total}")
    print("\nFiles found:", len(matched_path_list))

    # Launches the GUI
    search_ui(time_total, time_after_searching, time_after_indexing, time_after_sorting, matched_path_list,
              data_search_from)


# Load Save File
def load_search():
    load_dialog = QFileDialog.getOpenFileName(Root_Window, "Export File-Find Search", Saved_SearchFolder, "*.FFSave;")
    load_file = load_dialog[0]

    # Creating Cache File, because of the Reload Button
    if load_file != "":
        with open(load_file, "rb") as OpenedFile:
            saved_file_content = load(OpenedFile)
            if not os.path.exists(
                    os.path.join(Cached_SearchesFolder, f"loaded from {load_file}.FFSearch".replace("/", "-"))):
                with open(os.path.join(Cached_SearchesFolder,
                                       f"loaded from {load_file}.FFSearch".replace("/", "-")), "wb") as CachedSearch:
                    dump(saved_file_content, file=CachedSearch)
            search_ui(0, 0, 0, 0, saved_file_content, f"loaded from {load_file}".replace("/", "-"))


# Setup of the main window
def setup():
    # Debug
    print("Launching UI...")

    # Main Window
    # Create the Global Variables
    global root, Root_Window
    # Create the window
    root = QApplication([])
    root.setStyle("macos")

    Root_Window = QWidget()
    # Set the Title of the Window
    Root_Window.setWindowTitle("File-Find")
    # Set the Size of the Window and make it not resizable
    Root_Window.setFixedHeight(500)
    Root_Window.setFixedWidth(800)
    # Display the Window
    Root_Window.show()

    # File-Find Label
    # Define the Label
    main_label = QLabel("File Find", parent=Root_Window)
    # Change Font
    main_label.setFont(QFont("Baloo Bhaina", 70))
    # Display the Label
    main_label.move(0, -30)
    main_label.show()

    # Labels
    # Functions to automate Labels
    def large_filter_label(name):
        # Define the Label
        label = QLabel(name, parent=Root_Window)
        # Change Font
        label.setFont(QFont("Arial", 25))
        # Display the Label
        label.show()
        # Return the Label to move it
        return label

    def small_filter_label(name: str):
        # Define the Label
        label = QLabel(name, parent=Root_Window)
        # Change Font
        label.setFont(QFont("Arial", 15))
        # Set the Maximum Length
        label.setMaximumWidth(178)
        # Display the Label
        label.show()
        # Return the Label to move it
        return label

    # Create a Label for every Filter with the Function, defined above
    # -----Basic Search-----
    # Frame and Label
    sorting_frame_label = small_filter_label("Basic Search")
    sorting_frame_label.move(5, 70)
    basic_search_frame = QFrame(Root_Window)
    basic_search_frame.setGeometry(QRect(5, 90, 385, 170))
    basic_search_frame.setFrameShape(QFrame.StyledPanel)
    basic_search_frame.setFrameShadow(QFrame.Raised)
    basic_search_frame.show()

    # Creating the Labels
    l1 = large_filter_label("Name:")
    l1.move(10, 100)
    l2 = large_filter_label("in Name:")
    l2.move(10, 140)
    l3 = large_filter_label("File Ending:")
    l3.move(10, 180)
    l4 = large_filter_label("Directory:")
    l4.move(10, 220)
    # Label to display the Path
    l4_small = small_filter_label(os.getcwd())
    l4_small.move(140, 228)

    # -----Advanced Search-----
    # Frame and Label
    sorting_frame_label = small_filter_label("Advanced Search")
    sorting_frame_label.move(395, 70)
    advanced_search_frame = QFrame(Root_Window)
    advanced_search_frame.setGeometry(QRect(395, 90, 400, 290))
    advanced_search_frame.setFrameShape(QFrame.StyledPanel)
    advanced_search_frame.setFrameShadow(QFrame.Raised)
    advanced_search_frame.show()

    l5 = large_filter_label("File Size(Byte): min:")
    l5.move(400, 100)
    l5_2 = large_filter_label("max:")
    l5_2.move(680, 100)
    l6 = large_filter_label("Created from:")
    l6.move(400, 140)
    l6_2 = large_filter_label("to:")
    l6_2.move(660, 140)
    l7 = large_filter_label("Modified from:")
    l7.move(400, 180)
    l7_2 = large_filter_label("to:")
    l7_2.move(660, 180)
    l8 = large_filter_label("Contains:")
    l8.move(400, 220)
    l19 = large_filter_label("Search in System Files:")
    l19.move(400, 300)
    l10 = large_filter_label("Search for Folders:")
    l10.move(400, 340)

    # -----Sorting-----
    # Frame and Label
    sorting_frame_label = small_filter_label("Sorting")
    sorting_frame_label.move(5, 270)
    sorting_search_frame = QFrame(Root_Window)
    sorting_search_frame.setGeometry(QRect(5, 290, 385, 90))
    sorting_search_frame.setFrameShape(QFrame.StyledPanel)
    sorting_search_frame.setFrameShadow(QFrame.Raised)
    sorting_search_frame.show()

    l12 = large_filter_label("Sort by:")
    l12.move(10, 300)
    l13 = large_filter_label("Reverse Results:")
    l13.move(10, 340)

    # Label for the Shell Command
    command_label2 = QLabel("", Root_Window)
    command_label2.setFont(QFont("Arial", 20))
    command_label2.setMaximumWidth(310)

    # Entries
    # Function to automate Entry creation
    def filter_entry(only_int):
        # Define the Entry
        entry = QLineEdit(Root_Window)
        # Set the Length
        entry.resize(230, 20)
        # If only_int true, configure the label
        if only_int:
            entry.setValidator(QIntValidator())
        # Display the Entry
        entry.show()
        # Return the Label to place it
        return entry

    # Create an Entry for every Filter with the Function, defined above
    e1 = filter_entry(False)
    e1.move(150, 104)
    e2 = filter_entry(False)
    e2.move(150, 144)
    e3 = filter_entry(False)
    e3.move(150, 184)
    e4 = filter_entry(True)
    e4.resize(50, 20)
    e4.move(625, 104)
    e5 = filter_entry(True)
    e5.resize(50, 19)
    e5.move(740, 104)
    # Plain Text Edit for Contains
    e6 = filter_entry(False)
    e6.resize(270, 25)
    e6.move(510, 224)

    # Radio Button
    # Function for automating
    def create_radio_button(group, text):
        # Create Radio Button
        rb = QRadioButton(Root_Window)
        # Set the Text
        rb.setText(text)
        # Add the Button to the Group
        group.addButton(rb)
        # Display the Button
        rb.show()
        # Return the Button
        return rb

    # Search for Library Files
    # Group for Radio Buttons
    library_group = QButtonGroup(Root_Window)
    # Radio Button 1
    rb_library1 = create_radio_button(library_group, "Yes")
    # Move the Button
    rb_library1.move(680, 302)
    # Radio Button 2
    rb_library2 = create_radio_button(library_group, "No")
    # Move the Button
    rb_library2.move(740, 302)
    # Select the Button 2
    rb_library2.setChecked(True)

    # Search for Folders
    # Group for Radio Buttons
    folder_group = QButtonGroup(Root_Window)
    # Radio Button 1
    rb_folder1 = create_radio_button(folder_group, "Yes")
    # Move the Button
    rb_folder1.move(680, 342)
    # Radio Button 2
    rb_folder2 = create_radio_button(folder_group, "No")
    # Move the Button
    rb_folder2.move(740, 342)
    # Select the Button 2
    rb_folder2.setChecked(True)

    # Reverse Sort
    # Group for Radio Buttons
    reverse_sort_group = QButtonGroup(Root_Window)
    # Radio Button 1
    rb_reverse_sort1 = create_radio_button(reverse_sort_group, "Yes")
    # Move the Button
    rb_reverse_sort1.move(260, 342)
    # Radio Button 2
    rb_reverse_sort2 = create_radio_button(reverse_sort_group, "No")
    # Move the Button
    rb_reverse_sort2.move(320, 342)
    # Select the Button
    rb_reverse_sort2.setChecked(True)

    # Drop Down Menus
    # Sorting Menu
    # Defining
    combobox_sorting = QComboBox(Root_Window)
    # Adding Options
    combobox_sorting.addItems(["None", "File Size", "File Name", "Date Modified", "Date Created"])
    # Display
    combobox_sorting.show()
    combobox_sorting.move(240, 300)

    # Date-Time Entries
    def generate_day_entry():
        # Define dt_entry
        dt_entry = QDateEdit(Root_Window)
        # Change dd.mm.yy to dd.MM.yyyy (e.g. 13.1.01 = 13.Jan.2001)
        dt_entry.setDisplayFormat("dd.MMM.yyyy")
        # Display
        dt_entry.show()
        # Return dt entry to move it
        return dt_entry

    # Date Created
    c_date_from_drop_down = generate_day_entry()
    c_date_from_drop_down.move(558, 144)
    c_date_to_drop_down = generate_day_entry()
    c_date_to_drop_down.move(690, 144)

    # Date Modified
    m_date_from_drop_down = generate_day_entry()
    m_date_from_drop_down.move(558, 184)
    m_date_to_drop_down = generate_day_entry()
    m_date_to_drop_down.move(690, 184)

    # Push Buttons
    # Search from Button
    # Function to automate Buttons
    def generate_change_button(command):
        # Generate the Button
        button = QPushButton(Root_Window)
        # Change the Text
        button.setText("Select")
        # Set the command
        button.clicked.connect(command)
        # Display the Button
        button.show()
        # Return the value of the Button, to move the Button
        return button

    # Opens the File dialogue and changes the current working dir into the returned value
    def open_dialog():
        search_from = QFileDialog.getExistingDirectory(directory=os.getcwd())
        try:
            os.chdir(search_from)
            l4_small.setText(search_from)
            l4_small.adjustSize()
        except FileNotFoundError:
            pass

    search_from_button = generate_change_button(open_dialog)
    search_from_button.move(310, 220)

    # Print the given data
    def print_data():

        print(f"Filters:\n"
              f"Name: {e1.text()}\n"
              f"In name: {e2.text()}\n"
              f"File Ending: {e3.text()}\n"
              f"Search from: {os.getcwd()}\n\n"
              f"File size: min:{e4.text()} max: {e5.text()}\n"
              f"Date Modified from: {m_date_from_drop_down.text()} to: {m_date_to_drop_down.text()}\n"
              f"Date Created from: {c_date_from_drop_down.text()} to: {c_date_to_drop_down.text()}\n"
              f"Contains: {e6.text()}\n"
              f"Search for System files: {rb_library1.isChecked()}\n"
              f"Search for Folders: {rb_folder1.isChecked()}\n\n"
              f"Sort results by: {combobox_sorting.currentText()}\n"
              f"Reverse Results: {rb_reverse_sort1.isChecked()}")

    # Start Search for files locally
    def search_entry():
        # Print Input
        print_data()

        # Fetching Errors
        if e1.text() != "" and e2.text() != "" or e1.text() != "" and e3.text() != "":
            FFkit.show_critical_messagebox("NAME ERROR!", "Name Error!\n\nFile Name and in Name or File Type can't "
                                                          "be used together", Root_Window)

        # Warning
        elif QMessageBox.information(Root_Window, "This may take some Time!",
                                     "This may take some Time!\nPress OK to Start Searching",
                                     QMessageBox.Ok | QMessageBox.Cancel) == QMessageBox.Cancel:
            print("Cancelled Searching!")

        # Start Searching
        else:
            '''
            Converting the output of QDateEdit into the unix time by first using QDateEdit.date() to get something like
            this: QDate(1,3,2000), after that using QDate.toPyDate to get this: 1-3-2000, than we can use .split("-")
            to convert 1-3-2000 into a list [1,3,2000], after that we use time.mktime to get the unix time format
            that means something like, that: 946854000.0, only to match this with os.getctime, what we can use to get
            the creation date of a file.
            
            Yea it would be easier if Qt had a function to get the unix time
            '''
            unix_time_list = []
            for time_drop_down in [c_date_from_drop_down, c_date_to_drop_down, m_date_from_drop_down,
                                   m_date_to_drop_down]:
                time_list = str(time_drop_down.date().toPyDate()).split("-")
                unix_time_list.append(
                    mktime((int(time_list[0]), int(time_list[1]), int(time_list[2]), 0, 0, 0, 0, 0, 0)))

            search(data_name=e1.text(),
                   data_in_name=e2.text(),
                   data_filetype=e3.text(),
                   data_file_size_min=e4.text(), data_file_size_max=e5.text(),
                   data_library=rb_library1.isChecked(),
                   data_search_from=os.getcwd(),
                   data_content=e6.text(),
                   data_folders=rb_folder1.isChecked(),
                   data_sort_by=combobox_sorting.currentText(),
                   data_time=unix_time_list,
                   data_reverse_sort=rb_reverse_sort1.isChecked())

    # Generate a shell command, that displays in the UI
    def generate_shell_command():
        print_data()

        def copy_command():
            # Copying the command
            copy(shell_command)
            # Feedback to the User
            print(f"Copied Command: {shell_command}")
            # Messagebox
            FFkit.show_info_messagebox("Successful copied!", f"Successful copied Command:\n{shell_command} !",
                                       Root_Window)

        # Generate a shell command
        shell_command = f"find {os.getcwd()}"
        if e1.text() != "":
            shell_command += f" -name \"{e1.text()}\""
        elif e3.text() != "":
            shell_command += f" -iname \"*{e3.text()}\""
        elif e2.text() != "":
            shell_command += f" -iname \"{e2.text()}\""
        print(f"\nCommand: {shell_command}")

        # Label, saying command
        command_label = QLabel(Root_Window)
        command_label.setText("Command:")
        command_label.setFont(QFont("Arial", 20))
        command_label.show()
        command_label.move(10, 450)

        # Label, displaying the command
        command_label2.setText(shell_command)
        command_label2.setStyleSheet("background-color: blue;color: white;")
        command_label2.adjustSize()
        command_label2.move(120, 450)
        command_label2.show()

        # Copy Command Button
        command_copy_button = QPushButton(Root_Window)
        # Change the Text
        command_copy_button.setText("Copy")
        # Change the click event
        command_copy_button.clicked.connect(copy_command)
        # Display the Button at the correct position
        command_copy_button.show()
        command_copy_button.move(430, 450)

    # Buttons
    def large_button(text, command, font_size):
        # Define the Button
        button = QPushButton(Root_Window)
        # Set the Text
        button.setText(text)
        # Set the Font
        Font = QFont("Arial", font_size)
        Font.setBold(True)
        button.setFont(Font)
        # Set the Command
        button.clicked.connect(command)
        # Display the Button
        button.show()
        # Return the Button
        return button

    # Search button with image, to start searching
    search_button = large_button("Find", search_entry, 25)
    # Icon
    search_button.setIcon(QIcon(os.path.join(AssetsFolder, "Find_button_img_small.png")))
    search_button.setIconSize(QSize(25, 25))
    # Place
    search_button.resize(105, 50)
    search_button.move(625, 440)

    # Button for more Options: Load Searches, Generate shell Command and Info about the Cache
    more_options_button = large_button(None, lambda: FFkit.other_options(
        load_search, generate_shell_command, remove_cache, Root_Window), 50)
    # Icon
    more_options_button.setIcon(QIcon(os.path.join(AssetsFolder, "More_button_img_small.png")))
    more_options_button.setIconSize(QSize(100, 100))
    # Place
    more_options_button.resize(65, 50)
    more_options_button.move(730, 440)

    # Help Button, that calls FFKit.help_ui()
    help_button = large_button(" Help", lambda: FFkit.help_ui(Root_Window), 25)
    # Color
    help_button.setStyleSheet("color: #b50104;")
    # Icon
    help_button.setIcon(QIcon(os.path.join(AssetsFolder, "Info_button_img_small.png")))
    help_button.setIconSize(QSize(25, 25))
    # Place
    help_button.resize(120, 50)
    help_button.move(670, 10)


if __name__ == "__main__":
    print("Launching...")
    global root, Root_Window

    # Creating File-Find dir and deleting Cache
    Version = "dev-pre-alpha 19.oct.22-pyqt5"
    userpath = os.path.expanduser("~")
    os.chdir(userpath)

    LibFolder = os.path.join(os.path.join(os.path.join(os.getcwd(), "Library"), "Application Support"), "File-Find")
    Cached_SearchesFolder = os.path.join(LibFolder, "Cached Searches")
    Saved_SearchFolder = os.path.join(LibFolder, "Saved Searches")
    AssetsFolder = os.path.join(LibFolder, "assets")

    os.makedirs(Saved_SearchFolder, exist_ok=True)
    os.makedirs(Cached_SearchesFolder, exist_ok=True)
    os.makedirs(AssetsFolder, exist_ok=True)


    def remove_cache(show_popup):
        for (main, folder, data) in os.walk(Cached_SearchesFolder):
            for cacheobj in data:
                os.remove(os.path.join(main, cacheobj))
        if show_popup:
            FFkit.show_info_messagebox("Cleared Cache", "Cleared Cache successfully!", Root_Window)


    remove_cache(False)
    with open(os.path.join(LibFolder, "Info.txt"), "w") as ver_file:
        ver_file.write(f"Version: {Version}\n")

    FFvars.setup(AssetsFolder)
    setup()

    root.exec()
    print("End")
