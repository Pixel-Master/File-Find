import os
import tkinter as tk


# Sorting algorithms
class SORT:

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


# A help Window

def help_ui():
    # A function to generate these Faq texts
    def faq(question, answer, y):
        question_label = tk.Label(help_window, text=question, font=("Baloo Bhaina 2 Bold", 25), bg="black", fg="white")
        question_label.place(x=15, y=y)
        answer_label = tk.Label(help_window, text=answer, font=15, bg="black", fg="white")
        answer_label.place(x=25, y=y + 40)

    # The Base Window with Labels
    help_window = tk.Toplevel()
    help_window.title("File-Find Help")
    help_window.geometry("800x800+250+250")
    help_window.resizable(False, False)
    help_window.config(bg="black")
    main_text = tk.Label(help_window, text="File-Find Help", font=("Baloo Bhaina 2 Bold", 70), bg="black", fg="white")
    main_text.place(x=0, y=-20)
    ff_info = tk.Label(help_window, text="File-Find for MacOS", font=("Baloo Bhaina 2 Bold", 40), bg="black",
                       fg="white")
    ff_info.place(x=200, y=230)

    # Base 64 Encoded Image
    # noinspection SpellCheckingInspection
    ff_logo_img = tk.PhotoImage(height=120, width=120,
                                data="iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAMAAAAOusbgAAAAV1BMVEUAAAD6+vogICAVFRVTU1MKCgrz"
                                     "8/MAAAD///9VVVXR0dEuLi6Dg4OdnZ3IyMg6Ojrj4+OQkJDb29tra2upqans7OxhYWFNTU13d3e0tLS/"
                                     "v79ERERaWlr6or3iAAAAAXRSTlPcz4NGmQAAB6JJREFUaN7tmtm6oyoQhVtFoihOIOLw/s95UDQRFSnc"
                                     "2d03h5sePuUPsKSoRf15/Zv258//4ActG8Pon4BpUBU8F174b4DjIVka9sE7wDGkj7BJdk3jQx9wnI1jl"
                                     "06CSZnnNaWc9z0DoEucnNoQeoAjEqhmdtDmbvJ05gaYxj7giw6C2knOr8CB+CE4SahLLPQMxkHSZPA1Li"
                                     "7BCb8nX7yWzK/18Q/ASdW2VXU/ZlPU62tN1WIJBg/nHtpGtQr5ihq3DSG3yjbAfWJpzFPU648uoRvIM3B"
                                     "ue6uCjvjFbV1IT1HrVsRQsLWL3FPUuvHXr4KvRO1+ywTXti5qT1HrJn4XbBU1LsFgqz7p10UNBPOvi9oE"
                                     "ywfgh6I2wczWR/91UUPB8bdFbYKFrY8h/raoTfD0QCcPRW2CUeAPfihqE9zZwCT6tqhN8OgPfipqE2xVa"
                                     "BN9W9RAsF0oT0VtgrPWG/xU1EBwaz0j84eiNsEhAJxl0b5LWuFHoj6AKyc47jEZqEQbPg7LKedFgz1FfQ"
                                     "A3TqWsaU7QNgs+tOKFDziygYPxKANFJsPQ8zpnx9Evk+8S9QGshqMSVYznvKVRuUCh+u45pXVobG5tQaW"
                                     "Y0hTNyXROh0KN/g3S+N4nP37FSKRdN5ZlloVhGEVRrJr5vIqcDWUpQqluSP11kn2bkNLPSvD1QOqKijf"
                                     "13RDj1eBn/HiCY8nO2JmMJNnpOI7UjGVZWX68DRH/BByXGxah+W9I/7H8h6DjZz9TGaZKcDHGb2ujPTg"
                                     "LGhxH64Ke1tRo0bhRU6WpflG13GYeTSy69QjMLFuDmVIwKQolYqXinnMl5Dyyc6d8qLaR4IbLVKOnMrZn"
                                     "Bu3BWdDgi60enwyIeFx1nBMzbuNBrqMu7WCs3tl/Y3ZwcCDHpR6v6M+7c0WnhYwya8xqsdofeAgBH+yeb"
                                     "P1wyOXW1ouF3EW2zKAlc5MHsGVq9iZZ1C1gZttVB00eY1tKEpiZgRWspibYm2vlzXj1oX9aflkGTEns4G"
                                     "VqpnfgWsYzDVZuElA92TEsM7CC566CT2KsB1wHdnBSMbQNGQymroxcr3DHk7s2pNsqA1ISBzg3JF32t+B"
                                     "WzkNG0V1KEnmCR/2Vkltwwre5BqQkGswd4HiZ6dF6Ct3O/csnVd6kJA0UvH7wkR5KF9yD8TLXStf2lCT0"
                                     "A+slDlnAKwA4gqQkGtxDwCiqg1yd8KrqdIGwdatjRQRJSRaw07bV4LBvEe/UOvJB0pb3TXA4Thc6joSQl"
                                     "AQGXjrsMlJNlFGZ11SUtZCyFqLFdd1XBcHz5s7XJYFkBho8QEbclS0eCnVQqCliqGZMjow11Ui7uuuo+n"
                                     "eThy4whoLFfqpFsAWupiAFyzhlNSFjPuV1Lrt+LMS6JJCUxAds7OhNTdtEneeGjpJ+oL0UJSlXEdpTEjy"
                                     "aYKuRMe1iE7rc31qib2tqwZpsXONTRJy5kAOc7mIEym9jE8FFqDe41w24M8CRDRyg3TkPicaxVWfbUSB2"
                                     "dbiBnT9QL959VEzyctWWe+3A4GWzRqy6B3dbPHaq1QkejTM1ou6dejmBAG6wNNidkIf6S74LyDz9HHB/"
                                     "Cv58duuQpX2yC/EeMOQGawEDNpr1mIly2/ZP2OeQCblIAoN1oFDk6o6LwlO6OFsbH2/DnGr7nr4Ha+2o"
                                     "DNyewWwDfk20znMpmZiO3oY/OO3FloEfHg9IPm02QRn7WBFRTflcAqFS7UFlySqDWG6N1exkhr3QrWk5o"
                                     "7sTAC5qsXMnoOSPFRG/VksgWlo4uxih2ctKVmgh6TD/uqKv5WS6IkCynweyeQKz+ZFOQkwT2pkiXmRf1"
                                     "6fcDc8YKUPbfMDI3rU+LE9PhhNCnejRy4tsOnvLAs8O1WxRdUhN5smoroMh/0ywnmMmw3j2M33IRgEKnx"
                                     "W9OFTt7FDNcZ+MZ0s+IFyKCWmTa2I5r/BamONBNsDNRQHKsRRD2yVBRWZzlfKBtIE62G7eAZzsLrlpJ+M"
                                     "FeW2XbPbZkRzvli+zgq9Lblr2ur/41K4FM7/1tMuXuqxhWb5mNhgb5lFy06qlNshXvspiWW43rht5qvHp"
                                     "sV2NlqvkZvYaSVH63Li+97cjGe9tJONzGi4dmMCofAHYGzbyLMK3aeddcgO5cbWQZxG+7ULvkhvQjes7"
                                     "jhlkrF3F+BkYduN6PWY870vrc94lNyPsxvV6zDsbBAauIVe95oVPtp4OTuQqfFZykwGverPeQr4CQ0puo"
                                     "Fe9WVtck1c34nvgw1WvOkBek6/AkJIbgK/yfu6SvJ5cYeAeAD5cYy5JwhX5CgwpuQFlHe/g/ibzYz7mXX"
                                     "IDyCz3wX0l72yMYPQoudmD3faG8Zwm77z99TkDnAICQOS2N8zgrsgqAfi8FaTPSm4A9sYhuBdSyOH0nHf"
                                     "JDcDeOD6HzcoJcQEGBACn7wks5AXW+oT+BboOD9y/1gdaoMs9wPZ9+AHYEdz9a32gBbo+YFAAgJwWAMEd"
                                     "Bt7vw/XVCRirlgPB9FGtj4okpJjLYTitZ2OHMZU3duNYZlkErPSizlqftfqmrap9WYurdAIY3M3EnC6FP"
                                     "buRzA5VFoYR1ER6CP5qc9ya/22wWj59qvg9MDLqsnbLl/3yiOOtMMtiRfwHb+/PUVwyisoAAAAASUVO"
                                     "RK5CYII=")
    ff_logo = tk.Label(help_window, image=ff_logo_img)
    ff_logo.place(x=300, y=110)

    # Links using tk.bind
    link = tk.Label(help_window, fg="grey", bg="black", text="< Code >", font=("", 20))
    link.place(x=180, y=300)
    link.bind("<ButtonRelease>", lambda x: os.system("open https://gitlab.com/Pixel-Mqster/File-Find"))

    bug_tracker = tk.Label(help_window, fg="grey", bg="black", text="< Bug Tracker >", font=("", 20))
    bug_tracker.place(x=290, y=300)
    bug_tracker.bind("<ButtonRelease>", lambda x: os.system("open https://gitlab.com/Pixel-Mqster/File-Find/-/issues"))

    contribute = tk.Label(help_window, fg="grey", bg="black", text="< Check for Updates >", font=("", 20))
    contribute.place(x=450, y=300)
    contribute.bind("<ButtonRelease>", lambda x: os.system("open https://gitlab.com/Pixel-Mqster/File-Find/-/issues"))

    # Calling the faq functions for the Labels
    faq(question="What is File-Find and how does it work?", y=350,
        answer="File-Find is an open-source \"Finder extension\", that makes it easy to find Files.\nTo search just "
               "leave filters you don't need empty and fill out the filters do need ")
    faq(question="Why does File-Find crash when searching?", y=430,
        answer="File-Find is only using one thread. That's why it looks like File-Find \"doesn't react\".")

    # Needed to display the Image
    help_window.mainloop()


# Change the Label to File, Size, Date, Content or fn-match
def change_method(label: tk.Label, label2: tk.Label, entry1, entry2):
    change_method_window = tk.Toplevel()
    change_method_window.title("File-Find | Select an Option")
    change_method_window.geometry("400x300+250+250")
    change_method_window.resizable(False, False)
    change_method_window.config(bg="black")
    main_text = tk.Label(change_method_window, text="Select an Option:", font=("Baloo Bhaina 2 Bold", 50), bg="black",
                         fg="white")
    main_text.place(x=0, y=-20)
    var_method = tk.StringVar(change_method_window)
    rb_method1 = tk.Radiobutton(change_method_window, value="size", variable=var_method, text="Size",
                                bg="black", fg="white", font=("Arial", 17))
    rb_method1.place(x=30, y=100)
    rb_method2 = tk.Radiobutton(change_method_window, value="content", variable=var_method, text="Content",
                                bg="black", fg="white", font=("Arial", 17))
    rb_method2.place(x=100, y=100)
    rb_method3 = tk.Radiobutton(change_method_window, value="m_date", variable=var_method, text="Modified",
                                bg="black", fg="white", font=("Arial", 17))
    rb_method3.place(x=200, y=100)
    rb_method4 = tk.Radiobutton(change_method_window, value="c_date", variable=var_method, text="Created",
                                bg="black", fg="white", font=("Arial", 17))
    rb_method4.place(x=300, y=100)

    def select():
        selected_option = var_method.get()
        print(f"Selected {selected_option}")
        if selected_option == "size":
            label.config(text="File Size(Byte) min:")
            label2.config(text="max:")
            label2.place(x=310, y=240)
            entry1.place(x=233, y=240, width=75)
            entry2.place(x=370, y=240, width=75)
        elif selected_option == "content":
            label.config(text="Content:")
            label2.place_forget()
            entry2.place_forget()
            entry1.place(x=200, y=240, width=250)
        elif selected_option == "m_date":
            label.config(text="Date Modified from:")
            label2.config(text="to:")
            label2.place(x=310, y=240)
            entry1.place(x=233, y=240, width=75)
            entry2.place(x=370, y=240, width=75)
        elif selected_option == "c_date":
            label.config(text="Date Created from:")
            label2.config(text="to:")
            label2.place(x=310, y=240)
            entry1.place(x=233, y=240, width=75)
            entry2.place(x=370, y=240, width=75)
        else:
            selected_option = None
        change_method_window.destroy()
        return selected_option
    select_button = tk.Button(change_method_window, text="Select", highlightbackground="black", command=select)
    select_button.place(x=170, y=200)
    change_method_window.mainloop()


# Other Options, displayed on root
def other_options(load_search, messagebox):
    other_options_window = tk.Toplevel()
    other_options_window.title("File-Find | Select an Option")
    other_options_window.geometry("400x300+250+250")
    other_options_window.resizable(False, False)
    other_options_window.config(bg="black")
    main_text = tk.Label(other_options_window, text="Select an Option:", font=("Baloo Bhaina 2 Bold", 50), bg="black",
                         fg="white")
    main_text.place(x=0, y=-20)
    button_option1 = tk.Button(other_options_window, text="Load Saved Search", activebackground="black",
                               font=("Arial", 17), command=load_search)
    button_option1.place(x=20, y=100, width=360)
    button_option2 = tk.Button(other_options_window, text="Cache Info", activebackground="black", font=("Arial", 17),
                               command=lambda: messagebox.showinfo("Soon!", "Coming Soon!"))
    button_option2.place(x=20, y=150, width=360)
    button_option3 = tk.Button(other_options_window, text="Export Filters", activebackground="black",
                               font=("Arial", 17), command=lambda: messagebox.showinfo("Soon!", "Coming Soon!"))
    button_option3.place(x=20, y=200, width=360)
    button_option4 = tk.Button(other_options_window, text="Import Filter", activebackground="black", font=("Arial", 17),
                               command=lambda: messagebox.showinfo("Soon!", "Coming Soon!"))
    button_option4.place(x=20, y=250, width=360)


# Define Variables
def setup():
    pass
