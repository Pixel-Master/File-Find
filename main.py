# Find Files easier with FindFile

# Imports
import tkinter as tk
import additional_things


# Creates a Title
def search_object_name(root, name):
    return tk.Label(root, text=name, font=("Arial", 25), bg="black", fg="white")


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
    main_text.place(x=10, y=0)

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
    e2 = tk.Entry(root, )
    e2.place(x=200, y=162, width=300)
    e3 = tk.Entry(root)
    e3.place(x=200, y=202, width=300)
    e4 = tk.Entry(root)
    e4.place(x=220, y=322, width=75)
    e5 = tk.Entry(root)
    e5.place(x=370, y=322, width=75)

    # Radio Button
    test12 = tk.StringVar(root)
    test123 = tk.Radiobutton(root, value="1", variable=test12)
    test123.pack()
    test1 = tk.Radiobutton(root, value="2", variable=test12)
    test1.pack()

    def get_data():
        print("Name: " + e1.get())
        print("In name: " + e2.get())
        print("File Type: " + e3.get())
        print("File Size:\nmin: " + e4.get())
        print("max: " + e5.get())
        print("Test: " + test12.get())

    # Buttons
    search_bottom = tk.Button(root, text="Search", fg="green", bg="white", height=3, width=8, font=("Arial Bold", 30))
    search_bottom.place(x=50, y=685)
    generate_bottom = tk.Button(root, text="Generate\nshell\ncommand", fg="red", bg="white", height=3, width=8,
                                font=("Arial Bold", 30), command=get_data)
    generate_bottom.place(x=280, y=685)


if __name__ == "__main__":
    setup()
    root.mainloop()
