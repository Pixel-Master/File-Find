import os
import tkinter as tk


# Sorting algorithms
class SORT:

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

    @staticmethod
    def name(file):
        try:
            return os.path.basename(file)
        except FileNotFoundError:
            return -1

    @staticmethod
    def m_date(file):
        try:
            return os.path.getmtime(file)
        except FileNotFoundError:
            return -1

    @staticmethod
    def c_date(file):
        try:
            return os.stat(file).st_birthtime
        except FileNotFoundError:
            return -1


# A help Window
def help_ui():
    help_window = tk.Tk()
    help_window.title("File-Find Help")
    help_window.geometry("800x800+250+250")
    help_window.resizable(False, False)
    help_window.config(bg="black")
    main_text = tk.Label(help_window, text="File-Find Help", font=("Baloo Bhaina 2 Bold", 80), bg="black", fg="white")
    main_text.place(x=90, y=-20)
