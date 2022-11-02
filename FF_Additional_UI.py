# This File is a part of File-Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the classes for additional GUI components like the Help Window

# Imports
import os

# PyQt6 Gui Imports
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QFrame, QMessageBox

# Projects Libraries
import FF_Files
import FF_Search


# The class for the Help_window
class Help_Window:
    def __init__(self, parent):
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
        help_window = QMainWindow(parent)
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

        # The Version Label
        version_label = QLabel(help_window)
        # Font and Text
        version_label.setText(f"v. {FF_Files.VERSION_SHORT} ({FF_Files.VERSION})")
        version_label.setFont(QFont("Arial", 15))
        # The command and tooltip
        version_label.setToolTip(f"Version: {FF_Files.VERSION_SHORT} Extended Version: {FF_Files.VERSION}")
        # Display the Label
        version_label.adjustSize()
        version_label.show()
        version_label.move(240, 270)

        # Links using QPushButton
        def generate_link_button(displayed_text, domain, color):
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

        sourcecode = generate_link_button("Source Code", "https://gitlab.com/Pixel-Mqster/File-Find", "blue")
        sourcecode.move(120, 300)

        update = generate_link_button("Update", "https://gitlab.com/Pixel-Mqster/File-Find/-/releases", "green")
        update.move(290, 300)

        bug_tracker = generate_link_button("Report a Bug", "https://gitlab.com/Pixel-Mqster/File-Find/-/issues",
                                           "red")
        bug_tracker.move(420, 300)

        # Calling the faq functions for the Labels
        faq(question="What is File-Find and how does it work?", y=350,
            answer="File-Find is an open-source \"Finder extension\", that makes it easy to find Files.\nTo search just"
                   " leave filters you don't need empty and fill out the filters do need ")
        faq(question="Why does File-Find crash when searching?", y=430,
            answer="File-Find is only using one thread. That's why it looks like File-Find \"doesn't react\".")


# Other Options, displayed on Main Window
class other_options:
    def __init__(self, generate_command, parent: QWidget):
        # Using QMainWindow as a Child Window
        other_options_window = QMainWindow(parent)
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
            # Define the Button
            button = QPushButton(other_options_window)
            # Change the Text
            button.setText(text)
            # Set the command
            button.clicked.connect(command)
            # Destroy the other_options_window when the Button is pressed
            button.clicked.connect(other_options_window.destroy)
            # Display the Button correctly
            button.show()
            button.setFixedWidth(200)
            button.adjustSize()
            # Return the value of the Button, to move the Button
            return button

        # The Buttons
        button_option_command = generate_button(generate_command, "Generate Shell Command")
        button_option_command.move(50, 50)

        button_option_load = generate_button(lambda: FF_Search.load_search(parent), "Load Saved Search")
        button_option_load.move(50, 100)

        button_option_cache = generate_button(lambda: FF_Files.remove_cache(True, parent), "Clear Cache")
        button_option_cache.move(50, 150)


class msg:
    # Error PopUp
    @staticmethod
    def show_critical_messagebox(title, text, parent):
        # Error
        msg_error = QMessageBox(parent)
        msg_error.setIcon(QMessageBox.Icon.Critical)

        # setting message for Message Box
        msg_error.setText(text)

        # setting Message box window title
        msg_error.setWindowTitle(title)

        # declaring buttons on Message Box
        msg_error.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg_error.exec()

    # Info PopUp
    @staticmethod
    def show_info_messagebox(title, text, parent):
        # Information
        msg_info = QMessageBox(parent)
        msg_info.setIcon(QMessageBox.Icon.NoIcon)
        msg_info.setText(text)
        msg_info.setWindowTitle(title)

        msg_info.exec()

        # Return the Value of the Message Box
        return msg_info
