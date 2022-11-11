# This File is a part of File-Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the classes for additional GUI components like the options window

# Imports
import os

# PyQt6 Gui Imports
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QMessageBox

# Projects Libraries
import FF_Files
import FF_Search


class test_access:
    def __int__(self):
        with open(os.path.join(os.path.join(FF_Files.userpath, "Documents"), "TestFile.FFTestFile"), "a") as TestFile:
            TestFile.write("This is a Message from File FInd to Test Permission!")


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

        # Choose Label
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
        button_option_command = generate_button(generate_command, "Generate Terminal Command")
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
