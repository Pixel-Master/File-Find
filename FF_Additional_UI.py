# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This file contains the classes for additional UI components like messageboxes
import os
from pickle import load

# PyQt6 Gui Imports
from PyQt6.QtWidgets import QMessageBox

# Projects Libraries
import FF_Files


# Imports


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

    # Ask to search MessageBoy
    @staticmethod
    def show_search_question(parent):

        # Opens the Settings File for the Ask when Searching Setting
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "rb") as SettingsFile:
            if load(SettingsFile)["popup"]["search_question"]:
                if QMessageBox.information(parent, "This may take some Time!",
                                           "This may take some Time!\nPress OK to Start Searching",
                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)\
                        == QMessageBox.StandardButton.Ok:
                    return True
                else:
                    return False
            else:
                return True
