# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the classes for additional GUI components like the options window

# Imports
import os

# PyQt6 Gui Imports
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QMessageBox

# Projects Libraries
import FF_Files
import FF_Search


# CAN BE DELETED!!! ---NOT USED!!!---
class test_access:
    def __init__(self):
        if not self.test():
            self.ui()

    @staticmethod
    def ui():
        Message_Box = QMessageBox(QMessageBox.Icon.Critical, "No Permission", "No File Access\n\n"
                                                                              "File Find needs Permission to search in "
                                                                              "your Files!\n\n"
                                                                              "Go to:  -> "
                                                                              "System Preferences -> "
                                                                              "Security and Privacy -> "
                                                                              "Full Disk Access -> "
                                                                              "File Find",
                                  QMessageBox.StandardButton.Ignore)
        Open_button = Message_Box.addButton("Open Settings", QMessageBox.ButtonRole.HelpRole)
        Quit_button = Message_Box.addButton("Quit", QMessageBox.ButtonRole.DestructiveRole)
        Message_Box.exec()
        if Message_Box.clickedButton() == Open_button:
            os.system("open x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles")
            raise PermissionError("No File Access")
        elif Message_Box.clickedButton() == Quit_button:
            raise PermissionError("No File Access")

    @staticmethod
    def test():
        try:
            with open(os.path.join(os.path.join(FF_Files.userpath, "Documents"), "TestFile.FFTestFile"),
                      "w") as TestFile:
                TestFile.write("This is a Message from File Find to Test Permission!")
            os.remove(os.path.join(os.path.join(FF_Files.userpath, "Documents"), "TestFile.FFTestFile"))
        except PermissionError:
            return False
        else:
            return True


# Other Options, displayed on Main Window
class other_options:
    def __init__(self, generate_command, parent: QWidget):
        # Using QMainWindow as a Child Window
        other_options_window = QMainWindow(parent)
        # Set the Title of the Window
        other_options_window.setWindowTitle("File Find | Other Options")
        # Set the Size of the Window and make it not resizable
        other_options_window.setFixedHeight(220)
        other_options_window.setFixedWidth(300)
        # Display the Window
        other_options_window.show()

        # Choose Label
        # Define the Label
        main_label = QLabel("Choose:", parent=other_options_window)
        # Change Font
        font = QFont("Futura", 40)
        font.setBold(True)
        main_label.setFont(font)
        # Display the Label correctly
        main_label.adjustSize()
        main_label.move(10, 0)
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
