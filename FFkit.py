import os

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QWidget, QLabel, QPushButton, QFrame


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
def help_ui(root):
    # A function to generate these Faq texts
    def faq(question, answer, y):
        # The Question
        question_label = QLabel(help_window)
        question_label.setText(question)
        question_label.setFont(QFont("Baloo Bhaina", 25))
        question_label.adjustSize()
        question_label.show()
        question_label.move(15, y)

        # The Answer
        answer_label = QLabel(help_window)
        answer_label.setText(answer)
        answer_label.setFont(QFont("Arial", 15))
        answer_label.adjustSize()
        answer_label.show()
        answer_label.move(25, y + 40)

    # The Base Window with Labels
    help_window = QMainWindow(root)
    help_window.setWindowTitle("File-Find Help")
    help_window.setFixedHeight(700)
    help_window.setFixedWidth(700)
    help_window.show()

    # File-Find Help Label
    # Define the Label
    main_label = QLabel("File Find Help", parent=help_window)
    # Change Font
    main_label.setFont(QFont("Baloo Bhaina", 60))
    # Display the Label
    main_label.move(0, -20)
    main_label.adjustSize()
    main_label.show()

    # File Find for macOS Label
    ff_info = QLabel(help_window)
    # Change Font and Text
    ff_info.setText("File-Find for macOS")
    ff_info.setFont(QFont("Baloo Bhaina", 30))
    # Display the Label
    ff_info.move(200, 230)
    ff_info.adjustSize()
    ff_info.show()

    # File Find Logo
    ff_logo = QLabel(help_window)
    ff_logo.setText("HI")
    ff_logo.setFont(QFont("Baloo Bhaina", 45))
    # Set the Icon
    AssetsFolder = os.path.join(os.path.join(os.path.join(os.path.join(
        os.getcwd(), "Library"), "Application Support"), "File-Find"), "assets")
    ff_logo_img = QPixmap(os.path.join(AssetsFolder, "FFlogo_small.png"))
    ff_logo.setPixmap(ff_logo_img)
    # Display the Icon
    ff_logo.move(280, 100)
    ff_logo.adjustSize()
    ff_logo.show()

    # The Frame
    fflogo_frame = QFrame(help_window)
    fflogo_frame.setGeometry(QRect(100, 90, 500, 250))
    fflogo_frame.setFrameShape(QFrame.Shape.StyledPanel)
    fflogo_frame.show()

    # Links using QPushButton
    def generate_link_label(displayed_text, domain, color):
        link = QPushButton(help_window)
        # Font and Text
        link.setText(displayed_text)
        link.setFont(QFont("Arial", 20))
        # The command and tooltip
        link.setToolTip(domain)
        link.clicked.connect(lambda: os.system(f"open {domain}"))
        # Set the color to blue
        link.setStyleSheet(f"color: {color};")
        # Display the Label
        link.adjustSize()
        link.show()
        # Return the Label to move it
        return link

    sourcecode = generate_link_label("Source Code", "https://gitlab.com/Pixel-Mqster/File-Find", "blue")
    sourcecode.move(120, 300)

    update = generate_link_label("Update", "https://gitlab.com/Pixel-Mqster/File-Find/-/releases", "green")
    update.move(290, 300)

    bug_tracker = generate_link_label("Report a Bug", "https://gitlab.com/Pixel-Mqster/File-Find/-/issues", "red")
    bug_tracker.move(420, 300)

    # Calling the faq functions for the Labels
    faq(question="What is File-Find and how does it work?", y=350,
        answer="File-Find is an open-source \"Finder extension\", that makes it easy to find Files.\nTo search just "
               "leave filters you don't need empty and fill out the filters do need ")
    faq(question="Why does File-Find crash when searching?", y=430,
        answer="File-Find is only using one thread. That's why it looks like File-Find \"doesn't react\".")


# CAN BE DELETED!!!
# Change the Value of File, Size, Date or Content
def refactor_value(human_readable_label):
    # Create the Window
    window = QWidget()
    # Set the Title of the Window
    window.setWindowTitle("File-Find")
    # Set the Size of the Window and make it not resizable
    window.setFixedHeight(300)
    window.setFixedWidth(300)
    # Change the Background color
    window.setStyleSheet("background-color: #e0e0e0;")
    # Display the Window
    window.show()

    # File-Find Label
    # Define the Label
    main_label = QLabel(f"Change {human_readable_label}", parent=window)
    # Change Font
    main_label.setFont(QFont("Baloo Bhaina", 50))
    # Change Color
    main_label.setStyleSheet("color: black;")
    # Display the Label
    main_label.move(0, -20)
    main_label.show()

    change_button = QPushButton(window)
    change_button.setText("Change")
    change_button.show()
    change_button.move(120, 120)


# Other Options, displayed on root
def other_options(load_search, generate_command, remove_cache, root: QWidget):
    # Using QMainWindow as a Child Window
    other_options_window = QMainWindow(root)
    # Set the Title of the Window
    other_options_window.setWindowTitle("File-Find | Other Options")
    # Set the Size of the Window and make it not resizable
    other_options_window.setFixedHeight(220)
    other_options_window.setFixedWidth(300)
    # Display the Window
    other_options_window.show()
    # File-Find Label
    # Define the Label
    main_label = QLabel("Choose:", parent=other_options_window)
    # Change Font
    main_label.setFont(QFont("Baloo Bhaina", 40))
    # Display the Label correctly
    main_label.adjustSize()
    main_label.move(10, -15)
    main_label.show()

    def generate_button(command, text):
        # Generate the Button
        button = QPushButton(other_options_window)
        # Change the Text
        button.setText(text)
        # Set the command
        button.clicked.connect(command)
        # Destroy the other_options_window when the Button is pressed
        button.clicked.connect(other_options_window.destroy)
        # Display the Button correctly
        button.setFixedWidth(200)
        button.show()
        # Return the value of the Button, to move the Button
        return button

    # The Buttons
    button_option_command = generate_button(generate_command, "Generate Shell Command")
    button_option_command.move(50, 50)

    button_option_load = generate_button(load_search, "Load Saved Search")
    button_option_load.move(50, 100)

    button_option_cache = generate_button(lambda: remove_cache(True), "Clear Cache")
    button_option_cache.move(50, 150)


# Error PopUp
def show_critical_messagebox(title, text, parent):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)

    # setting message for Message Box
    msg.setText(text)

    # setting Message box window title
    msg.setWindowTitle(title)

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    msg.exec()


# Info PopUp
def show_info_messagebox(title, text, parent):
    # Warning
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.NoIcon)
    msg.setText(text)
    msg.setWindowTitle(title)

    msg.exec()

    # Return the Value of the Message Box
    return msg
