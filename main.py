# Find Files easier with File-Find

import os
from time import time
import tkinter as tk
from fnmatch import fnmatch
from tkinter import filedialog, messagebox
from pyperclip import copy


def help_ui():
    help_window = tk.Tk()
    help_window.title("File-Find Help")
    help_window.geometry("800x800+250+250")
    help_window.resizable(False, False)
    help_window.config(bg="black")
    main_text = tk.Label(help_window, text="File-Find Help", font=("Baloo Bhaina 2 Bold", 80), bg="black", fg="white")
    main_text.place(x=90, y=-20)


# The GUI for the search results
def search_ui(total_time, time_searching, time_indexing, matched_list):
    time_before_building = time()
    # Window setup
    search_result_ui = tk.Tk()
    search_result_ui.geometry("800x800+150+150")
    search_result_ui.resizable(False, False)
    search_result_ui.title("File-Find Search Results")
    search_result_ui.config(bg="black")

    # main titles
    main_text = tk.Label(search_result_ui, text="Search Results", font=("Baloo Bhaina 2 Bold", 70), bg="black",
                         fg="white")
    main_text.place(x=10, y=0)
    seconds_text = tk.Label(search_result_ui, text=f"Time needed:   Searching: {round(time_searching,3)}  Indexing:"
                                                   f" {round(time_indexing,3)}  Total: {round(total_time,3)}",
                            font=("Baloo Bhaina 2 Bold", 20), bg="black", fg="white")
    seconds_text.place(x=10, y=100)
    objects_text = tk.Label(search_result_ui, text=f"Files found: {len(matched_list)}",
                            font=("Baloo Bhaina 2 Bold", 20), bg="black", fg="white")
    objects_text.place(x=580, y=100)

    # Results
    scrollbar_y = tk.Scrollbar(search_result_ui, bg="black")
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x = tk.Scrollbar(search_result_ui, bg="black", orient='vertical')
    scrollbar_x.pack(side="bottom", fill="x")

    result_listbox = tk.Listbox(search_result_ui, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set,
                                height=35, width=85, background="black", foreground="white")

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

    # Buttons
    show_in_finder = tk.Button(search_result_ui, text="Show in Finder", command=open_in_finder,
                               highlightbackground="black")
    show_in_finder.place(x=10, y=750)
    open_file = tk.Button(search_result_ui, text="Open", command=open_with_program,
                          highlightbackground="black")
    open_file.place(x=190, y=750)
    clipboard_path = tk.Button(search_result_ui, text="Copy Path to clipboard", command=copy_path,
                               highlightbackground="black")
    clipboard_path.place(x=330, y=750)
    clipboard_file = tk.Button(search_result_ui, text="Copy File Name to clipboard", command=copy_name,
                               highlightbackground="black")
    clipboard_file.place(x=540, y=750)
    info_button = tk.Button(search_result_ui, text="?", fg="black", bg="white", font=("Arial Bold", 15),
                            command=help_ui)
    info_button.place(x=740, y=0)

    for i in matched_list:
        result_listbox.insert("end", i + "\n")
    result_listbox.place(y=140, x=10)
    scrollbar_y.config(command=result_listbox.yview)
    scrollbar_x.config(command=result_listbox.xview)

    print("Time spent building th UI:", time() - time_before_building)


# The search engine
def search(data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
           data_search_from, data_folders):
    # Warning
    messagebox.showinfo("This may take some Time!",
                        "This may take some Time!\nPress OK to Start Searching")
    print("This may take some Time!\nPress OK to Start Searching")

    # Creates empty lists for the files
    matched_filelist = []
    found_path_list = []

    # Saves time before indexing
    time_before_start = time()

    # Debug
    print("\nStarting scanning...\n")

    # Goes through every file in the directory and saves it
    for (roots, dirs, files) in os.walk(data_search_from):
        for i in files:
            found_path_list.append(os.path.join(roots, i))
#            print("File:", os.path.join(roots, i))
        if data_folders == "search":
            for i in dirs:
                found_path_list.append(os.path.join(roots, i))
#                print("Folder:", os.path.join(roots, i))

    time_after_searching = time() - time_before_start

    # Applies filters, when they don't match it continues. In the end match_var must have a score of 4
    for i in found_path_list:
        if data_name.lower() == os.path.basename(i).lower() or data_name == "":
            pass
        else:
            continue
        if data_in_name.lower() in os.path.basename(i).lower() or data_in_name == "":
            pass
        else:
            continue
        if fnmatch(os.path.basename(i), "*." + data_filetype) or data_filetype == "":
            pass
        else:
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

                # get size
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

        except ValueError:
            pass
        if data_library == "dont search":
            if "/Library" in i:
                continue
        if os.path.basename(i) == ".DS_Store" or os.path.basename(i) == ".localized" or os.path.basename(
                i) == "desktop.ini":
            continue
        matched_filelist.append(i)
    # Prints out the seconds needed and the matching files
    print("Found Files and Folders:", matched_filelist)
    time_after_indexing = time() - (time_after_searching + time_before_start)
    total_time = time() - time_before_start
    print(f"\nSeconds needed:\nSearching: {time_after_searching}\nIndexing: {time_after_indexing}\nTotal: {total_time}")
    print("\nFiles found:", len(matched_filelist))

    # Launches th GUI
    search_ui(total_time, time_after_searching, time_after_indexing, matched_filelist)


def open_dialog():
    search_from = filedialog.askdirectory()
    os.chdir(search_from)


# Creates a Title
def search_object_name(window, name):
    return tk.Label(window, text=name, font=("Arial", 25), bg="black", fg="white")


# Setup of the main window
def setup():
    # Debug
    print("Launching...")

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
    l1 = search_object_name(root, "Name:")
    l1.place(x=10, y=120)
    l2 = search_object_name(root, "in Name:")
    l2.place(x=10, y=160)
    l3 = search_object_name(root, "File Ending:")
    l3.place(x=10, y=200)
    l4 = search_object_name(root, "Search Library Files:")
    l4.place(x=10, y=240)
    l5 = search_object_name(root, "Search from directory:")
    l5.place(x=10, y=280)
    l6 = search_object_name(root, "File Size(MB) min:")
    l6.place(x=10, y=320)
    l7 = search_object_name(root, "max:")
    l7.place(x=300, y=320)
    l8 = search_object_name(root, "Search for Folders:")
    l8.place(x=10, y=360)

    # Entries
    e1 = tk.Entry(root)
    e1.place(x=200, y=122, width=300)
    e2 = tk.Entry(root)
    e2.place(x=200, y=162, width=300)
    e3 = tk.Entry(root)
    e3.place(x=200, y=202, width=300)
    e4 = tk.Entry(root)
    e4.place(x=220, y=322, width=75)
    e5 = tk.Entry(root)
    e5.place(x=360, y=322, width=75)

    # Radio Button
    # Search for Library Files
    var_library = tk.StringVar(root)
    rb_library1 = tk.Radiobutton(root, value="search", variable=var_library, text="Search", bg="black", fg="white",
                                 font=("Arial", 17))
    rb_library1.place(x=260, y=242)
    rb_library2 = tk.Radiobutton(root, value="dont search", variable=var_library, text="Don't search", bg="black",
                                 fg="white", font=("Arial", 17))
    rb_library2.place(x=350, y=242)

    # Search for Folders
    var_search_folders = tk.StringVar(root)
    rb_search_folders1 = tk.Radiobutton(root, value="search", variable=var_search_folders, text="Search", bg="black",
                                        fg="white", font=("Arial", 17))
    rb_search_folders1.place(x=260, y=362)
    rb_search_folders2 = tk.Radiobutton(root, value="dont search", variable=var_search_folders, text="Don't search",
                                        bg="black", fg="white", font=("Arial", 17))
    rb_search_folders2.place(x=350, y=362)

    # Search from
    # File dialog
    search_from_button = tk.Button(root, text="Choose", highlightbackground="black", command=open_dialog)
    search_from_button.place(x=270, y=280)

    # Print the data
    def print_data():
        print("Filters:\n", "Name: ", e1.get(), "\nIn name: ", e2.get(), "\nFile Type: ", e3.get(), "\nFile "
                                                                                                    "Size:\nmin: ",
              e4.get(), "\nmax: ", e5.get(), "\nSearch for Library files: ", var_library.get(), "\nSearch from: ",
              os.getcwd(), "\nSearch for Folders: ", var_search_folders.get(), sep="")

        # Search for files

    def search_entry():
        print_data()
        try:
            if e4.get() != "" or e5.get() != "":
                int(e4.get())
                int(e5.get())
            search(e1.get(), e2.get(), e3.get(), e4.get(), e5.get(), var_library.get(), os.getcwd(),
                   var_search_folders.get())
        except ValueError:
            messagebox.showwarning("VALUE ERROR!", "Value Error!\n\nFile Size: min. and max. must be integers!")
            print("Value Error!\n\nFile Size: min. and max. must be integers!")

    # Buttons
    search_bottom = tk.Button(root, text="Search", fg="green", bg="white", height=3, width=8, font=("Arial Bold", 30),
                              command=search_entry)
    search_bottom.place(x=50, y=685)
    generate_bottom = tk.Button(root, text="Generate\nshell\ncommand", fg="red", bg="white", height=3, width=8,
                                font=("Arial Bold", 30), command=print_data)
    generate_bottom.place(x=280, y=685)
    info_button = tk.Button(root, text="?", fg="black", bg="white", font=("Arial Bold", 15), command=help_ui)
    info_button.place(x=450, y=5)


if __name__ == "__main__":
    global root
    os.chdir(os.path.expanduser("~"))
    setup()
    root.mainloop()
