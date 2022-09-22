# Find Files easier with File-Find

import os
import tkinter as tk
import FFkit
from pickle import dump, load
from time import time
from tkinter import filedialog, messagebox
from pyperclip import copy


# The GUI for the search results
def search_ui(time_total, time_searching, time_indexing, time_sorting, matched_list, search_path):
    time_before_building = time()
    # Window setup
    search_result_ui = tk.Toplevel()
    search_result_ui.geometry("800x800+150+150")
    search_result_ui.resizable(False, False)
    search_result_ui.title("File-Find Search Results")
    search_result_ui.config(bg="black")

    # main titles
    main_text = tk.Label(search_result_ui, text="Search Results", font=("Baloo Bhaina 2 Bold", 70), bg="black",
                         fg="white")
    main_text.place(x=10, y=0)

    # Seconds needed
    seconds_text = tk.Label(search_result_ui, font=("Baloo Bhaina 2 Bold", 20), bg="black", fg="white")
    seconds_text.place(x=10, y=100)

    # Files found
    objects_text = tk.Label(search_result_ui, text=f"Files found: {len(matched_list)}",
                            font=("Baloo Bhaina 2 Bold", 20), bg="black", fg="white")
    objects_text.place(x=450, y=100)

    # Scrollbars
    scrollbar_y = tk.Scrollbar(search_result_ui, bg="black")
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x = tk.Scrollbar(search_result_ui, bg="black", orient='vertical')
    scrollbar_x.pack(side="bottom", fill="x")

    # Listbox
    result_listbox = tk.Listbox(search_result_ui, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set,
                                height=35, width=85, background="black", foreground="white")
    result_listbox.place(y=140, x=10)

    # Options for paths
    def open_with_program():
        selected_file = (result_listbox.get(result_listbox.curselection()))
        os.system("open " + str(selected_file.replace(" ", "\\ ")))
        print(f"Opened: {selected_file}")

    def open_in_finder():
        selected_file = (result_listbox.get(result_listbox.curselection()))
        os.system("open -R " + str(selected_file.replace(" ", "\\ ")))
        print(f"Opened in Finder: {selected_file}")

    def copy_path():
        selected_file = (result_listbox.get(result_listbox.curselection()))
        copy(selected_file)
        print(f"Copied Path: {selected_file}")
        messagebox.showinfo("Successful copied!", f"Successful copied Path: {selected_file}!")

    def copy_name():
        selected_file = (result_listbox.get(result_listbox.curselection()))
        copy(os.path.basename(selected_file))
        print(f"Copied File-Name: {os.path.basename(selected_file)}")
        messagebox.showinfo("Successful copied!", f"Successful copied File Name: {os.path.basename(selected_file)}!")

    # Show more time info's
    def show_time_stats():
        messagebox.showinfo("Time Stats", f"Time needed:\n\nScanning: {round(time_searching, 3)}\nIndexing:"
                                          f" {round(time_indexing, 3)}\nSorting:"
                                          f" {round(time_sorting, 3)}\nCreating UI: "
                                          f"{round(time_building, 3)}\n---------\nTotal: "
                                          f"{round(time_total + time_building, 3)}")

    # Reloads File, check all collected files, if they still exist
    def reload_files():
        print("Reload...")
        time_before_reload = time()
        removed_list = []
        for file in matched_list:
            if os.path.exists(file):
                continue
            else:
                result_listbox.delete(result_listbox.index(matched_list.index(file)))
                matched_list.remove(file)
                print(f"File Does Not exist: {file}")
                removed_list.append(file)
        with open(os.path.join(Cached_SearchesFolder, search_path.replace("/", "-") + ".FFSearch"), "rb") as SearchFile:
            cached_files = list(load(SearchFile))
        for file in cached_files:
            if file in removed_list:
                cached_files.remove(file)
        with open(os.path.join(Cached_SearchesFolder, search_path.replace("/", "-") + ".FFSearch"), "wb") as SearchFile:
            dump(cached_files, SearchFile)
        print(f"Reloaded found Files and removed {len(removed_list)} in"
              f" {round(time() - time_before_reload, 3)} sec.")
        messagebox.showinfo("Reloaded!", f"Reloaded found Files and removed {len(removed_list)}"
                                         f" in {round(time() - time_before_reload, 3)} sec.")
        objects_text.config(text=f"Files found: {len(matched_list)}")
        del cached_files, removed_list

    # Save Search
    def save_search():
        save_file = filedialog.asksaveasfilename(title="Export File-Find Search", initialdir=Saved_SearchFolder,
                                                 filetypes=(("File-Find Format", "*.FFSave"), ("Text file", "*.txt")))
        if save_file.endswith(".txt") and not os.path.exists(save_file):
            with open(save_file, "w") as SaveFile:
                for file in matched_list:
                    SaveFile.write(file + "\n")
        elif save_file.endswith(".FFSave") and not os.path.exists(save_file):
            with open(save_file, "wb") as SaveFile:
                dump(matched_list, SaveFile)
        elif not os.path.exists(save_file):
            messagebox.showinfo("Error", "Try again this File Already Exist!")

    # Buttons
    show_in_finder = tk.Button(search_result_ui, text="Show in Finder", command=open_in_finder,
                               highlightbackground="black")
    show_in_finder.place(x=10, y=750)

    open_file = tk.Button(search_result_ui, text="Open", command=open_with_program, highlightbackground="black")
    open_file.place(x=190, y=750)

    clipboard_path = tk.Button(search_result_ui, text="Copy Path to clipboard", command=copy_path,
                               highlightbackground="black")
    clipboard_path.place(x=330, y=750)

    clipboard_file = tk.Button(search_result_ui, text="Copy File Name to clipboard", command=copy_name,
                               highlightbackground="black")
    clipboard_file.place(x=540, y=750)

    info_button = tk.Button(search_result_ui, text="?", fg="black", bg="white", font=("Arial Bold", 15),
                            command=FFkit.help_ui)
    info_button.place(x=740, y=0)

    show_time = tk.Button(search_result_ui, text="...", command=show_time_stats, highlightbackground="black")
    show_time.place(x=200, y=105)

    reload_button = tk.Button(search_result_ui, text="Reload", highlightbackground="black", command=reload_files)
    reload_button.place(x=630, y=105)
    save_button = tk.Button(search_result_ui, text="Save", highlightbackground="black", command=save_search)
    save_button.place(x=710, y=105)

    # Adding every object from matched_list to result_listbox
    for i in matched_list:
        result_listbox.insert("end", i + "\n")
    result_listbox.place(y=140, x=10)
    scrollbar_y.config(command=result_listbox.yview)
    scrollbar_x.config(command=result_listbox.xview)

    # seconds needed
    seconds_text.config(text=f"Time needed: {round(time_total + (time() - time_before_building), 3)}")

    # Time building UI
    time_building = time() - time_before_building
    print("Time spent building the UI:", time_building)


# The search engine
def search(data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
           data_search_from, data_folders, sort_by, reverse_results):
    # Warning
    messagebox.showinfo("This may take some Time!",
                        "This may take some Time!\nPress OK to Start Searching")
    print("This may take some Time!\nPress OK to Start Searching")

    # Creates empty lists for the files
    matched_path_list = []
    found_path_list = []

    # Saves time before indexing
    time_before_start = time()

    # Debug
    print("\nStarting Scanning...")

    # Goes through every file in the directory and saves it
    if os.path.exists(os.path.join(Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch")):
        print("Scanning using cached Data..")
        with open(os.path.join(Cached_SearchesFolder, data_search_from.replace("/", "-") + ".FFSearch"),
                  "rb") as SearchResults:
            found_path_list = load(SearchResults)

    else:
        for (roots, dirs, files) in os.walk(data_search_from):
            for i in files:
                found_path_list.append(os.path.join(roots, i))
            #   print("File:", os.path.join(roots, i))
            for i in dirs:
                found_path_list.append(os.path.join(roots, i))
            #    print("Folder:", os.path.join(roots, i))

    time_after_searching = time() - time_before_start

    print("\nStarting Indexing...\n")
    # Applies filters, when they don't match it continues.
    for i in found_path_list:
        basename = os.path.basename(i)
        if data_name.lower() == basename.lower() or data_name == "":
            pass
        else:
            continue
        if data_in_name.lower() in basename.lower() or data_in_name == "":
            pass
        else:
            continue
        if basename.endswith(f".{data_filetype}") or data_filetype == "":
            pass
        else:
            continue
        if data_folders != "search":
            if os.path.isdir(i):
                continue

        try:
            int(data_file_size_min)
            int(data_file_size_max)
            if os.path.isfile(i):
                if int(data_file_size_max) >= int(
                        os.path.getsize(i)) >= int(data_file_size_min):
                    pass
                else:
                    continue
            elif os.path.isdir(i):
                folder_size = 0

                # Gets the size
                for path, dirs, files in os.walk(i):
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
            else:
                continue
        except ValueError:
            pass
        if data_library == "dont search":
            if "/Library" in i:
                continue
        if basename == ".DS_Store" or basename == ".localized" or basename == "desktop.ini" or basename == "Thumbs.db":
            continue
        matched_path_list.append(i)
    # Prints out the seconds needed and the matching files
    print(f"Found {len(matched_path_list)} Files and Folders")
    time_after_indexing = time() - (time_after_searching + time_before_start)

    # Sorting

    if sort_by == "filename":
        print("\nSorting List by Name...")
        matched_path_list.sort(key=FFkit.SORT.name, reverse=reverse_results)
    elif sort_by == "size":
        print("\nSorting List by Size..")
        matched_path_list.sort(key=FFkit.SORT.size, reverse=not reverse_results)
    elif sort_by == "c_date":
        print("\nSorting List by creation date..")
        matched_path_list.sort(key=FFkit.SORT.c_date, reverse=not reverse_results)
    elif sort_by == "m_date":
        print("\nSorting List by modified date..")
        matched_path_list.sort(key=FFkit.SORT.m_date, reverse=not reverse_results)
    else:
        if reverse_results:
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
    file = filedialog.askopenfilename(title='Select a File-Find Saved-Search file (FFSave)',
                                      filetypes=[('File-Find Search File', "FFSave")], initialdir=Saved_SearchFolder)
    # Creating Cache File, because of the Reload Button
    with open(file, "rb") as OpenedFile:
        saved_file_content = load(OpenedFile)
        if not os.path.exists(os.path.join(Cached_SearchesFolder, f"loaded from {file}.FFSearch".replace("/", "-"))):
            with open(os.path.join(Cached_SearchesFolder, f"loaded from {file}.FFSearch".replace("/", "-")), "wb") \
                    as CachedSearch:
                dump(saved_file_content, file=CachedSearch)
        search_ui(0, 0, 0, 0, saved_file_content, f"loaded from {file}".replace("/", "-"))


# Setup of the main window
def setup():
    # Debug
    print("Launching UI...")

    # main window
    # setup window
    global root
    root = tk.Tk()
    root.geometry("500x800+50+50")
    root.resizable(False, False)
    root.title("Find-File")
    root.config(bg="black")

    # File-Find text
    main_text = tk.Label(root, text="File-Find", font=("Baloo Bhaina 2 Bold", 80), bg="black", fg="white")
    main_text.place(x=10, y=-20)

    # Labels
    # Creates a Title
    def search_object_name(window, name):
        return tk.Label(window, text=name, font=("Arial", 25), bg="black", fg="white")

    l1 = search_object_name(root, "Name:")
    l1.place(x=10, y=110)
    l2 = search_object_name(root, "in Name:")
    l2.place(x=10, y=155)
    l3 = search_object_name(root, "File Ending:")
    l3.place(x=10, y=195)
    l4 = search_object_name(root, "File Size(Byte) min:")
    l4.place(x=10, y=240)
    l5 = search_object_name(root, "max:")
    l5.place(x=310, y=240)
    l6 = search_object_name(root, "Search from:")
    l6.place(x=10, y=280)
    l6_info = tk.Label(root, text=os.getcwd(), font=("Arial", 15), bg="black", fg="white", anchor="w", width=31)
    l6_info.place(x=170, y=287)
    l7 = search_object_name(root, "Search for System Files:")
    l7.place(x=10, y=320)
    l8 = search_object_name(root, "Search for Folders:")
    l8.place(x=10, y=360)
    l9 = search_object_name(root, "Sort by:")
    l9.place(x=10, y=420)
    l9 = search_object_name(root, "Reverse Results:")
    l9.place(x=10, y=480)
    command_label2 = tk.Label(root)

    # Entries
    e1 = tk.Entry(root)
    e1.place(x=200, y=112, width=280)
    e2 = tk.Entry(root)
    e2.place(x=200, y=157, width=280)
    e3 = tk.Entry(root)
    e3.place(x=200, y=197, width=280)
    e4 = tk.Entry(root)
    e4.place(x=233, y=240, width=75)
    e5 = tk.Entry(root)
    e5.place(x=370, y=240, width=75)

    # Radio Button
    # Search for Library Files
    var_library = tk.StringVar(root)
    rb_library1 = tk.Radiobutton(root, value="search", variable=var_library, text="Yes", bg="black", fg="white",
                                 font=("Arial", 17))
    rb_library1.place(x=310, y=322)
    rb_library2 = tk.Radiobutton(root, value="dont search", variable=var_library, text="No", bg="black",
                                 fg="white", font=("Arial", 17))
    rb_library2.place(x=410, y=322)
    rb_library2.select()
    # Search for Folders
    var_search_folders = tk.StringVar(root)
    rb_search_folders1 = tk.Radiobutton(root, value="search", variable=var_search_folders, text="Yes", bg="black",
                                        fg="white", font=("Arial", 17))
    rb_search_folders1.place(x=310, y=362)
    rb_search_folders2 = tk.Radiobutton(root, value="dont search", variable=var_search_folders, text="No",
                                        bg="black", fg="white", font=("Arial", 17))
    rb_search_folders2.place(x=410, y=362)
    rb_search_folders2.select()

    # Sorting
    # select sorting method
    var_sort_by = tk.StringVar(root)
    rb_sort_by1 = tk.Radiobutton(root, value="none", variable=var_sort_by, text="None", bg="black",
                                 fg="white", font=("Arial", 17))
    rb_sort_by1.place(x=410, y=422)
    rb_sort_by2 = tk.Radiobutton(root, value="filename", variable=var_sort_by, text="File Name",
                                 bg="black", fg="white", font=("Arial", 17))
    rb_sort_by2.place(x=300, y=422)
    rb_sort_by3 = tk.Radiobutton(root, value="size", variable=var_sort_by, text="Size",
                                 bg="black", fg="white", font=("Arial", 17))
    rb_sort_by3.place(x=200, y=422)
    rb_sort_by4 = tk.Radiobutton(root, value="m_date", variable=var_sort_by, text="Modified",
                                 bg="black", fg="white", font=("Arial", 17))
    rb_sort_by4.place(x=200, y=447)
    rb_sort_by5 = tk.Radiobutton(root, value="c_date", variable=var_sort_by, text="Created",
                                 bg="black", fg="white", font=("Arial", 17))
    rb_sort_by5.place(x=300, y=447)
    rb_sort_by1.select()
    # Reverse Sort
    var_reverse_sort = tk.StringVar(root)
    rb_reverse_sort1 = tk.Radiobutton(root, value="True", variable=var_reverse_sort, text="Yes", bg="black", fg="white",
                                      font=("Arial", 17))
    rb_reverse_sort1.place(x=310, y=482)
    rb_reverse_sort2 = tk.Radiobutton(root, value="False", variable=var_reverse_sort, text="No", bg="black", fg="white",
                                      font=("Arial", 17))
    rb_reverse_sort2.place(x=410, y=482)
    rb_reverse_sort2.select()

    # Search from File Dialog
    search_from_button = tk.Button(root, text="Choose", highlightbackground="black",
                                   command=lambda: open_dialog(l6_info))
    search_from_button.place(x=400, y=280)

    # Change method
    method_of_label = "size"

    change_button = tk.Button(root, text="warning", command=lambda method_of_label: FFkit.change_method(l4, l5, e4, e5),
                              bitmap="info", height=30, width=20, background="white")
    change_button.place(x=460, y=232)

    # Print the data
    def print_data():
        Method_s = "Error!"
        Method_s2 = "Error!"
        if method_of_label == "size":
            Method_s = "File Size:\nmin:"
            Method_s2 = "max:"
        elif method_of_label == "content":
            Method_s = "Content:"
            Method_s2 = ""
        elif method_of_label == "m_date":
            Method_s = "Date Modified:\nFrom:"
            Method_s2 = "To:"
        elif method_of_label == "c_date":
            Method_s = "Date Modified:\nFrom:"
            Method_s2 = "To:"
        print(f"Filters:\nName: {e1.get()}\nIn name: {e2.get()}\nFile Ending: {e3.get()}\n{Method_s} {e4.get()}\n"
              f"{Method_s2} {e5.get()}\nSearch from: {os.getcwd()}\nSearch for System files: {var_library.get()}\n"
              f"Search for Folders: {var_search_folders.get()}\nSort results by: {var_sort_by.get()}\nReverse Results: "
              f"{var_reverse_sort.get()}")

    # Search for files
    def search_entry():
        if e1.get() != "" and e2.get() != "" or e1.get() != "" and e3.get() != "":
            messagebox.showwarning("NAME ERROR!", "Name Error!\n\nFile Name and in Name or File Type can't be used "
                                                  "together")
            print("Name Error!\n\nFile Name and in Name or File Type can't be used together!")
            raise NameError("Name Error!\n\nFile Name and in Name or File Type can't be used together!")
        if var_reverse_sort.get() == "True":
            reverse_results = True
        else:
            reverse_results = False
        print_data()
        try:
            if e4.get() != "" or e5.get() != "":
                int(e4.get())
                int(e5.get())
        except ValueError:
            messagebox.showwarning("VALUE ERROR!", "Value Error!\n\nFile Size: min. and max. must be integers!")
            print("Value Error!\n\nFile Size: min. and max. must be integers!")
        else:

            search(e1.get(), e2.get(), e3.get(), e4.get(), e5.get(), var_library.get(), os.getcwd(),
                   var_search_folders.get(), var_sort_by.get(), reverse_results)

    # Generate a shell command, that displays in the UI
    def generate_shell_command():
        print_data()

        def copy_command():
            copy(shell_command)
            print(f"Copied Command: {shell_command}")
            messagebox.showinfo("Successful copied!", f"Successful copied Command: {shell_command} !")

        shell_command = f"find {os.getcwd()}"
        if e1.get() != "":
            shell_command += f" -name {e1.get()}"
        elif e3.get() != "":
            shell_command += f" -iname \"*{e3.get()}\""
        elif e2.get() != "":
            shell_command += f" -iname {e2.get()}"
        print(f"\nCommand: {shell_command}")
        command_label = tk.Label(root, text="Command:", font=("Arial", 30), bg="black", fg="white")
        command_label.place(x=10, y=540)
        command_label2.config(text=shell_command, font=("Arial", 20), bg="blue", fg="white", width=31,
                              anchor="w")
        command_label2.place(x=10, y=590)
        command_copy_button = tk.Button(root, text="Copy", highlightbackground="black", command=copy_command)
        command_copy_button.place(x=400, y=590)

    # Opens the File dialogue
    def open_dialog(label):
        search_from = filedialog.askdirectory(initialdir=userpath)
        os.chdir(search_from)
        label.config(text=os.getcwd())

    # Buttons
    search_bottom = tk.Button(root, text="Search", fg="green", bg="white", font=("Arial Bold", 30),
                              command=search_entry)
    search_bottom.place(x=50, y=680, height=120, width=200)
    generate_bottom = tk.Button(root, text="Shell Command", fg="blue", bg="white",
                                font=("Arial Bold", 25), command=generate_shell_command)
    generate_bottom.place(x=280, y=680, height=60, width=200)
    more_options_bottom = tk.Button(root, text="Other...", fg="red", bg="white",
                                    font=("Arial Bold", 30),
                                    command=lambda: FFkit.other_options(load_search, messagebox))
    more_options_bottom.place(x=280, y=740, height=60, width=200)
    info_button = tk.Button(root, text="?", fg="black", bg="white", font=("Arial Bold", 15), command=FFkit.help_ui)
    info_button.place(x=450, y=5)


if __name__ == "__main__":
    print("Launching...")
    global root

    # Creating File-Find dir and deleting Cache
    Version = "dev-pre-alpha 18.Sep.22"
    userpath = os.path.expanduser("~")
    os.chdir(userpath)

    LibFolder = os.path.join(os.path.join(os.path.join(os.getcwd(), "Library"), "Application Support"), "File-Find")
    Cached_SearchesFolder = os.path.join(LibFolder, "Cached Searches")
    Saved_SearchFolder = os.path.join(LibFolder, "Saved Searches")
    Saved_FiltersFolder = os.path.join(LibFolder, "Saved Filters")

    os.makedirs(Saved_SearchFolder, exist_ok=True)
    os.makedirs(Saved_FiltersFolder, exist_ok=True)
    os.makedirs(Cached_SearchesFolder, exist_ok=True)

    for (main, folder, data) in os.walk(Cached_SearchesFolder):
        for cacheobj in data:
            os.remove(os.path.join(main, cacheobj))
    with open(os.path.join(LibFolder, "Info.txt"), "w") as ver_file:
        ver_file.write(f"Version: {Version}\n")

#    FFkit.setup()
    setup()

    root.mainloop()
    print("End")
