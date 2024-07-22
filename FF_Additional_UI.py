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
from json import load, dump

# PySide6 Gui Imports
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QPixmap, QColor
from PySide6.QtWidgets import QMessageBox, QComboBox, QLabel, QVBoxLayout, QWidget, QMainWindow

# Projects Libraries
import FF_Files
import FF_Menubar

# keeping a list of all created icons
icons = set()
global app, global_color_scheme


# Create a QPixmap that automatically adjusts to light and dark mode
class UIIcon:
    def __init__(self, path, icon_set_func=None, input_app=None, turn_auto=True):
        global app, global_color_scheme
        # Make parameter class wide
        self.icon_set_func = icon_set_func
        self.turn_auto = turn_auto

        # If class is called at launch for initial setup
        if input_app is not None:
            # Debug
            logging.debug("Initialising UIIcon...")

            app = input_app

            def change_global__color_scheme(scheme):
                global global_color_scheme
                global_color_scheme = scheme

            global_color_scheme = app.styleHints().colorScheme()

            # Connecting color scheme change
            app.styleHints().colorSchemeChanged.connect(self.style_changed)
            app.styleHints().colorSchemeChanged.connect(change_global__color_scheme)

        # Creating an icon
        else:
            # Debug
            logging.debug(f"Creating icon for {path} ...")

            # Storing path
            self.path = path
            # Filling the pixmap in and mapping the black part out
            self.pixmap = QPixmap(path)
            self.mask = self.pixmap.createMaskFromColor(QColor("black"), Qt.MaskMode.MaskOutColor)
            # Filling in the mapped out part
            if global_color_scheme == Qt.ColorScheme.Dark:
                self.turn_dark()
            elif global_color_scheme == Qt.ColorScheme.Light:
                self.turn_light()

            # Add icon to list
            icons.add(self)

    # Turn icons white for dark-mode
    def turn_dark(self):
        self.pixmap.fill((QColor("white")))
        self.pixmap.setMask(self.mask)
        self.icon_set_func(self.pixmap)

    # Turn icons dark for light-mode
    def turn_light(self):
        self.pixmap.fill((QColor("black")))
        self.pixmap.setMask(self.mask)
        self.icon_set_func(self.pixmap)

    @staticmethod
    def style_changed(color_scheme):
        # Debug
        logging.debug(f"Turning icons into {color_scheme}")

        for icon in icons:
            if color_scheme == Qt.ColorScheme.Dark:
                if icon.turn_auto:
                    UIIcon.turn_dark(icon)
            elif color_scheme == Qt.ColorScheme.Light:
                if icon.turn_auto:
                    UIIcon.turn_light(icon)


# A custom checkbox that allows the user to check (select) multiple items
class CheckableComboBox(QComboBox):
    # once there is a checkState set, it is rendered
    def __init__(self, parent):
        logging.debug("Initialising check-able combobox...")
        # initialising the combobox
        QComboBox.__init__(self, parent)
        # setting a placeholder text
        self.setPlaceholderText("all")

        # Signal for deactivating/activating buttons
        class ButtonSignalsClass(QObject):
            all_selected = Signal()
            all_deselected = Signal()
            some_selected = Signal()

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

    # Return a lists with the index of all items
    def all_items(self):
        all_items = []
        for item in range(self.count()):
            all_items.append(item)
        return all_items

    # Return a lists with the content of all items
    def all_items_text(self):
        all_items = []
        for item in range(self.count()):
            all_items.append(self.itemText(item))
        return all_items

    # Return a list with all checked items
    def all_checked_items(self):
        checked_items = []
        for item in self.all_items():
            if self.item_checked(item):
                checked_items.append(self.itemText(item))
        return checked_items

    # Set all items check that are in the list
    def check_items(self, checked_items: list | set | tuple):
        # Iterating through a list of all item's indexes and get the text. If the text is in the list of items
        # that should be checked set the check state to Qt.CheckState.Checked else set it to Qt.CheckState.Unchecked
        for checked_item_index in self.all_items():
            item = self.model().item(checked_item_index, 0)
            if item.text() in checked_items:
                item.setCheckState(Qt.CheckState.Checked)
            # If item should not be checked
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

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
    def show_info_messagebox(title, text, parent, large=False):
        # Information such as file info's require more space
        if not large:
            # Information
            msg_info = QMessageBox(parent)
            msg_info.setIcon(QMessageBox.Icon.NoIcon)
            msg_info.setText(text)
            msg_info.setWindowTitle(title)

            msg_info.exec()

            # Return the Value of the Message Box
            return msg_info

        else:
            # Information popup large
            msg_info = QMainWindow(parent)
            # Central widget
            central_widget = QWidget()
            msg_info.setCentralWidget(central_widget)
            # Layout
            layout = QVBoxLayout(msg_info)
            central_widget.setLayout(layout)

            # Title
            title_label = QLabel(msg_info)
            title_label.setText(title)
            # Set font size
            font = QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE)
            font.setBold(True)
            title_label.setFont(font)
            # Display
            layout.addWidget(title_label)

            # Label
            label = QLabel(msg_info)
            label.setText(text)
            # Make label selectable
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            # Display
            layout.addWidget(label)

            msg_info.setWindowTitle(title)
            msg_info.show()

            FF_Menubar.MenuBar(parent=msg_info, window="info_box", listbox=None)

            # Return the Value of the Message Box
            return msg_info

    # Ask to search MessageBoy
    @staticmethod
    def show_delete_question(parent, file):

        # Opens the Settings File for the Ask when Searching Setting
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as settings_file:
            # Load Settings with json
            if load(settings_file)["popup"]["delete_question"]:
                if QMessageBox.information(parent, "Are You Sure You Want To Delete This File?",
                                           f"Do you want to delete {file}?",
                                           QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) \
                        == QMessageBox.StandardButton.Ok:
                    return True
                else:
                    return False
            else:
                return True


# Displaying Welcome Popups
def welcome_popups(parent, force_popups=False):
    # Debug
    logging.debug("Testing for PopUps...")

    # Loading already displayed Popups with pickle
    with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as settings_file:
        settings = load(settings_file)
        popup_dict = settings["popup"]

    if popup_dict["FF_welcome"] or force_popups:
        # Debug
        logging.info("Showing Welcomes PopUp...")

        # Asking if tutorial is necessary
        question_popup = QMessageBox(text="Would you like to have a short tutorial?\n\n"
                                          "By going to Help > Tutorial, you can get it later.", parent=parent)

        question_popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        # Entering the mainloop
        question_popup.exec()

        # Getting the button role of the clicked button
        question_selected_button_role = question_popup.buttonRole(question_popup.clickedButton())

        if question_selected_button_role == QMessageBox.ButtonRole.YesRole:
            # Showing welcome messages
            PopUps.show_info_messagebox(
                title="Welcome to File Find",
                text="Welcome to File Find!\n\nThanks for downloading File Find!\n"
                     "File Find is an open-source macOS utility,"
                     " that makes it easy to search and find files.\n\n"
                     "To search, fill in the filters you need and leave those"
                     " you don't need empty.\n\n\n"
                     "File Find version: "
                     f"{FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]",
                parent=parent)
            PopUps.show_info_messagebox(
                title="Welcome to File Find",
                text="Welcome to File Find!\n\nSearch with the find button.\n\n"
                     "You can find all and settings in the settings menu.\n"
                     "(find it by going to File Find > Setting in the menubar)\n\n"
                     "If you press on the File Find icon in the menu bar and go to \"Searches:\","
                     " you can see the state of all your active searches.",
                parent=parent)
            PopUps.show_info_messagebox(
                title="Welcome to File Find",
                text="Welcome to File Find!\n\nSave a search or a filter preset \n"
                     "by pressing CMD/Ctrl + S in the result or main window.\n\n"
                     "After you opened a search, you can find duplicated files\n"
                     "or compare the opened search to an search saved on the disk,\n"
                     "by pressing the corresponding buttons in the top right.",
                parent=parent)

            PopUps.show_info_messagebox(
                title="Welcome to File Find",
                text="Welcome to File Find!\n\n"
                     "If you want to contribute, look at the source code, "
                     "found a bug or have a feature-request\n\n"
                     "Go to: github.com/Pixel-Master/File-Find\n"
                     "File Find Website: pixel-master.github.io/file-find\n\n"
                     "I hope you find all of your files!",
                parent=parent)

    # Version Welcome PopUps
    elif popup_dict["FF_ver_welcome"]:
        # Debug
        logging.info("Showing Version Welcomes PopUp...")

        # Showing welcome messages
        PopUps.show_info_messagebox(
            title="Thanks for upgrading File Find!",
            text="Thanks for upgrading File Find!\n\n"
                 f"File Find is an open source Utility for finding files. \n\n"
                 f"Get new versions at: "
                 f"https://pixel-master.github.io/File-Find/"
                 f"\n\n\n"
                 "File Find version: "
                 f"{FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]",
            parent=parent)

    # Setting PopUp File
    popup_dict["FF_ver_welcome"] = False
    popup_dict["FF_welcome"] = False
    settings["popup"] = popup_dict
    with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "w") as settings_file:
        dump(settings, settings_file)


# Debug
logging.info("Finished PopUps")
