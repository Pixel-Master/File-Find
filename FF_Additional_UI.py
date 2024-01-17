# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the classes for additional UI components like messageboxes

# Imports
import logging
import os
from pickle import load

# PyQt6 Gui Imports
from PyQt6.QtWidgets import QMessageBox, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# Projects Libraries
import FF_Files


# A custom checkbox
class CheckableComboBox(QComboBox):
    # once there is a checkState set, it is rendered
    def __init__(self, parent):
        logging.debug("Initialising checkable combobox...")
        # initialising the combobox
        QComboBox.__init__(self, parent)
        # setting a placeholder text
        self.setPlaceholderText("all")

        # Signal for deactivating/activating buttons
        class ButtonSignalsClass(QObject):
            all_selected = pyqtSignal()
            all_deselected = pyqtSignal()
            some_selected = pyqtSignal()

        self.button_signals = ButtonSignalsClass(parent)

        self.model().dataChanged.connect(self.data_changed)
        # display the placeholder text with setting the index to -1
        self.setCurrentIndex(-1)

    # if date in the model changes, the placeholder text is changed
    def data_changed(self):
        if self.all_checked_items() == self.all_items_text():
            # Send signal to disable "Deselect all" button
            self.button_signals.all_selected.emit()
        elif not self.all_checked_items():
            # Send signal to disable "Select all" button
            self.button_signals.all_deselected.emit()
        else:
            # Send signal to enable all buttons
            self.button_signals.some_selected.emit()

        # Start function to change text display on mainUI
        text = self.determine_text()
        self.setPlaceholderText(text)

    def addItems(self, texts):
        for item in texts:
            super(CheckableComboBox, self).addItem(item)
            item = self.model().item(self.count() - 1, 0)
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(Qt.CheckState.Checked)

    def item_checked(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == Qt.CheckState.Checked

    def all_items(self):
        all_items = []
        for item in range(self.count()):
            all_items.append(item)
        return all_items

    def all_items_text(self):
        all_items = []
        for item in range(self.count()):
            all_items.append(self.itemText(item))
        return all_items

    def all_checked_items(self):
        checked_items = []
        for item in self.all_items():
            if self.item_checked(item):
                checked_items.append(self.itemText(item))
        return checked_items

    # determining the text for the QComboBox
    def determine_text(self):
        # Getting values to not have to check every time
        all_checked_items = self.all_checked_items()
        all_items = self.all_items_text()
        # all items selected, just say "all"
        if all_items == all_checked_items:
            return "all"

        # no item selected
        elif not all_checked_items:
            return "none"

        # less than four items selected, display all checked items
        elif len(all_checked_items) <= 3:
            return ", ".join(all_checked_items)

        # less than two item unchecked, display all unchecked ones
        elif (len(all_items) - len(all_checked_items)) <= 2:
            all_unchecked_items = []
            for item in all_items:
                if item not in all_checked_items:
                    all_unchecked_items.append(item)
            return f'all except: {", ".join(all_unchecked_items)}'
        # Shortening the selection
        else:
            checked_items = ", ".join(all_checked_items)
            return f"{checked_items[:30]}..."

    def select_all(self):
        for item_num in range(self.count()):
            item = self.model().item(item_num, 0)
            item.setCheckState(Qt.CheckState.Checked)

    def deselected_all(self):
        for item_num in range(self.count()):
            item = self.model().item(item_num, 0)
            item.setCheckState(Qt.CheckState.Unchecked)


class PopUps:
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
                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) \
                        == QMessageBox.StandardButton.Ok:
                    return True
                else:
                    return False
            else:
                return True
