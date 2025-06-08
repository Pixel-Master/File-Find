# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the classes for additional UI components like messageboxes

# Imports
import logging
import os
from json import load, dump
from sys import platform
from time import time, ctime
from unicodedata import normalize

# PySide6 Gui Imports
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QPixmap, QColor, QIcon, QAction
from PySide6.QtWidgets import (QMessageBox, QComboBox, QLabel, QVBoxLayout, QWidget, QMainWindow,
                               QLineEdit, QCompleter, QGridLayout, QToolButton, QTextBrowser)

# Projects Libraries
import FF_Files
import FF_Menubar
import FF_Settings

# keeping a list of all created icons
icons = set()
global app, global_color_scheme
DEFAULT_QT_FONT = QFont(FF_Files.DEFAULT_FONT, FF_Files.DEFAULT_FONT_SIZE)
BOLD_QT_FONT = QFont(FF_Files.DEFAULT_FONT, FF_Files.DEFAULT_FONT_SIZE)
BOLD_QT_FONT.setBold(True)

if platform == "darwin":
    # Used for explanation text
    CTRL_BUTTON = "⌘"
else:
    CTRL_BUTTON = "CTRL"


# Used for entering the directory
class DirectoryEntry(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Set the size
        self.resize(230, 20)
        self.setFixedHeight(25)
        self.setMinimumWidth(230)
        # Set text and tooltip to display the directory
        self.setText(FF_Files.SELECTED_DIR)
        # Execute the validate_dir function if text is changed
        self.textChanged.connect(self.validate_dir)
        # Loading Completions now
        self.complete_path(FF_Files.SELECTED_DIR, check=False)
        # If app is sandboxed the user must click on the directory for permission
        if FF_Files.IS_SANDBOXED:
            self.setReadOnly(True)

        # normal colors
        self.dark_color = "white"
        self.light_color = "black"

        # Connecting color scheme change, using app form UIIcon
        app.styleHints().colorSchemeChanged.connect(lambda scheme: self.style_changed(scheme))

    def validate_dir(self):
        # Debug
        logging.debug(f"Directory Path changed to: {self.text()}")

        # Get the text
        check_path = self.text()

        # If User pressed "Cancel"
        if check_path == "":
            return

        # Changing Tool-Tip
        self.setToolTip(self.text())

        # Testing if path is folder
        if os.path.isdir(check_path):
            # Changing Path
            logging.debug(f"Path: {check_path} valid")
            FF_Files.SELECTED_DIR = check_path

            # Change color back to normal
            self.change_color("black", "white")

            # Updating Completions
            self.complete_path(check_path)

        else:
            # Debug
            logging.debug(f"Path: {check_path} invalid")

            # Change color
            self.change_color(FF_Files.RED_LIGHT_THEME_COLOR, FF_Files.RED_DARK_THEME_COLOR)

    # Auto complete paths
    def complete_path(self, path, check=True):

        # Adds all folders in path into paths
        def get_paths():
            paths = []
            for list_folder in os.listdir(path):
                if os.path.isdir(os.path.join(FF_Files.SELECTED_DIR, list_folder)):
                    # Normalising the Unicode form to deal with special characters (e.g. ä, ö, ü) on macOS
                    normalised_path = normalize("NFC", os.path.join(FF_Files.SELECTED_DIR, list_folder))
                    paths.append(normalised_path)

            # Returns the list
            return paths

        # Check if "/" is at end of inputted path
        if check:
            # Going through all paths to look if auto-completion should be loaded
            if path.endswith(os.sep):
                completer_paths = get_paths()
                logging.debug("Changed QCompleter")
            else:
                return
        # If executed at launch skip check because home path doesn't end with a "/"
        else:
            completer_paths = get_paths()
            logging.debug("Changed QCompleter")

        # Set the saved list as Completer
        directory_line_edit_completer = QCompleter(completer_paths, parent=self.parent)
        self.setCompleter(directory_line_edit_completer)

    def style_changed(self, scheme):
        if scheme == Qt.ColorScheme.Dark:
            self.setStyleSheet(f"color: {self.dark_color};")
        elif scheme == Qt.ColorScheme.Light:
            self.setStyleSheet(f"color: {self.light_color};")

    def change_color(self, light_color, dark_color):
        # Making parameters global
        self.dark_color = dark_color
        self.light_color = light_color

        if global_color_scheme == Qt.ColorScheme.Dark:
            self.setStyleSheet(f"color: {self.dark_color};")
        elif global_color_scheme == Qt.ColorScheme.Light:
            self.setStyleSheet(f"color: {self.light_color};")


# Create a label that uses a different color than usual and changes with light and dark mode
class ColoredLabel(QLabel):
    def __init__(self, text, parent, light_color, dark_color):
        super().__init__(text, parent)

        # Making parameters global
        self.dark_color = dark_color
        self.light_color = light_color

        # Connecting color scheme change, using app form UIIcon
        app.styleHints().colorSchemeChanged.connect(lambda scheme: self.style_changed(scheme))

        if global_color_scheme == Qt.ColorScheme.Dark:
            self.setStyleSheet(f"color: {self.dark_color};")
        elif global_color_scheme == Qt.ColorScheme.Light:
            self.setStyleSheet(f"color: {self.light_color};")

    def style_changed(self, scheme):
        if scheme == Qt.ColorScheme.Dark:
            self.setStyleSheet(f"color: {self.dark_color};")
        elif scheme == Qt.ColorScheme.Light:
            self.setStyleSheet(f"color: {self.light_color};")

    def change_color(self, light_color, dark_color):
        # Making parameters global
        self.dark_color = dark_color
        self.light_color = light_color

        if global_color_scheme == Qt.ColorScheme.Dark:
            self.setStyleSheet(f"color: {self.dark_color};")
        elif global_color_scheme == Qt.ColorScheme.Light:
            self.setStyleSheet(f"color: {self.light_color};")


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

            def change_global_color_scheme(scheme):
                global global_color_scheme
                global_color_scheme = scheme

            global_color_scheme = app.styleHints().colorScheme()

            # Connecting color scheme change
            app.styleHints().colorSchemeChanged.connect(self.style_changed)
            app.styleHints().colorSchemeChanged.connect(change_global_color_scheme)

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
        elif len(all_checked_items) < 4:
            return ", ".join(all_checked_items)

        # less than three item unchecked, display all unchecked ones
        elif (len(all_items) - len(all_checked_items)) < 3:
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
            title_label.setFont(BOLD_QT_FONT)
            # Display
            layout.addWidget(title_label)

            # Label
            label = QTextBrowser(msg_info)
            label.setText(text)
            # Make label selectable
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            # Display
            layout.addWidget(label)

            msg_info.setWindowTitle(title)
            msg_info.show()

            FF_Menubar.MenuBar(parent=msg_info, window="info_box")

            # Return the Value of the Message Box
            return msg_info

    # Ask to search MessageBoy
    @staticmethod
    def show_delete_question(parent, file):
        if FF_Settings.SettingsWindow.load_setting("popup")["delete_question"]:
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
class Tutorial:
    def __init__(self, parent, force_tutorial=False):
        self.parent = parent
        # Debug
        logging.debug("Testing for PopUps...")

        # Loading already displayed Popups with json
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as settings_file:
            settings = load(settings_file)
            popup_dict = settings["popup"]

        if popup_dict["FF_welcome"] or force_tutorial:
            self.pages = {
                1: {"title": "Welcome to File Find - Tutorial",
                    "text": "<p>Thank you for downloading File Find!</p>"
                            "<p>File Find is an open-source utility for finding files, searching for duplicates"
                            " and comparing searches.</p>"
                            "<p>The following tutorial will explain what File Find's capabilities and how to use them."
                            "<br>"
                            "You can navigate through the tutorial using the arrow keys on your keyboard or the "
                            "ones in this window.<br>If you ever need this tutorial again, "
                            "you can open it from anywhere within File Find by going"
                            " to the menu bar and selecting <code>Help > Tutorial</code>."
                            "</p><p>"
                            "Your File Find version: "
                            f"<code>{FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]</code></p>"},
                2: {"title": "Tutorial - Searching",
                    "text": "<p>To search fill in the desired options and leave the unnecessary ones untouched. "
                            "If you leave everything untouched, the result is going to include all files on your disk "
                            "except system files "
                            "(<i>to search for them you have to activate the option "
                            "under <code>Advanced</code></i>).<br> If you are unsure about the functionality"
                            " of a filter, you can hover over its name or refer "
                            "<a href=\"https://pixel-master.github.io/File-Find/#how-to\">to this guide</a>.</p>"
                            "<p>After filling in all the desired filters, press the <code>Find</code> button. "
                            "Right-clicking it will show you more options.</p>"
                            "<p>You can start multiple searches at once. The status of all the searches can be tracked"
                            " by pressing the File Find icon in the menu bar and going to <code>Searches</code>.</p>"
                            "<p>If you are having trouble finding a file try "
                            "<a href=\"https://pixel-master.github.io/File-Find/#file_not_found\" a>"
                            "these steps</a>.</p>"
                            "<p>You can be export the selected filters as a File Find filter preset "
                            "(<code>.FFFilter</code>) "
                            f"by pressing <code>{CTRL_BUTTON} + S</code> in the main window. Filter presets can "
                            f"be made the default in the settings or loaded by pressing <code>{CTRL_BUTTON} + O</code>."
                            "</p><p>With every search File Find creates a cache so that the next search in the "
                            "same directory takes only a fraction of the time. This means that the result might be "
                            "a little outdated. The cache is cleared automatically after a set amount of time "
                            "(which can be changed in settings) or "
                            f"manually by selecting <code>Tools > Clear cache</code> in the menu bar.</p>"},
                3: {"title": "Tutorial - Results",
                    "text": "<p>Once the search is finished a results window will appear.</p>"
                            "<p>There are multiple actions that can be performed "
                            "for each found file on the bottom and in the menu bar. Double-clicking a file, selecting"
                            " <code>Tools > View selected file in Finder/File explorer</code> in the menu bar or "
                            "right-clicking the "
                            "<code>Open</code> button will open it in Finder or Windows File Explorer"
                            f" (this can be changed in settings).</p><p>You can save the current search by clicking on"
                            " the three dots"
                            f" or pressing <code>{CTRL_BUTTON} + S</code> and reopen it from the main window by going"
                            f" to <code>File > Open Search</code>.</p>"
                            "<p>Pressing <code>M</code> in any file list will mark/unmark a file.</p>"
                            ""},
                4: {"title": "Tutorial - Comparing and Finding duplicates",
                    "text": "<p>Duplicated files can be found by pressing the duplicates-icon or selecting"
                            " <code>File > Finding duplicated files...</code> in the menu bar "
                            "in the results window.</p>"
                            "<p>You'll then be prompted to select the preferred options. All ongoing searches of "
                            "duplicates can be seen in the same place as the normal searches.</p>"
                            "<p>Once it finished, you're going to see an expandable tree view. Press the arrow on the "
                            "left of each file to see the files that are duplicates of the file on top.</p>"
                            "<p>To compare two searches click on the corresponding icon or go"
                            " to <code>File > Compare to other search...</code> in the menu bar. You will then be"
                            " prompted to"
                            " select a saved search (<code>.FFSearch</code>) from your disk.</p>"
                            "<p>The process can be tracked the same way as a normal search. "
                            "Once it finished, you'll see "
                            "two tables, with each one containing the files that are exclusive to one search.</p>"},
                5: {"title": "Tutorial - General Information",
                    "text": "<p>If you close the main window, "
                            "you can reopen it from the File Find icon in the menubar. "
                            "Searches will keep running once the main window is closed</p>"
                            "<p>The settings can be opened by going to <code>File Find > Preferences...</code></p>"
                            "<p>If you want to contribute, look at the source code, "
                            "found a bug or have a feature-request</p>"
                            "<p>Go to <a href=\"https://github.com/Pixel-Master/File-Find\">GitHub</a>.</p>"
                            "<p>If you are looking for updates go to the"
                            " <a href=\"https://pixel-master.github.io/File-Find\">File Find Website</a></p>"
                            "I hope you find all of your files!"}}

        # Version Welcome PopUps
        elif popup_dict["FF_ver_welcome"]:
            self.pages = {
                1: {"title": "Update was successful!",
                    "text":
                        "<p>Thanks for upgrading File Find!</p>"
                        "<p>File Find is an open source Utility for finding files. </p>"
                        f"<p>For an overview over the changes have a look at the "
                        f"<a href=\"https://pixel-master.github.io/File-Find/download#{FF_Files.VERSION_SHORT}\"a>"
                        f"changelog</a><br>"
                        f"Get new versions <a href=\"https://pixel-master.github.io/File-Find/download\">here</a>"
                        f"</p>"
                        "<p>Your File Find version: "
                        f"<code>{FF_Files.VERSION_SHORT} [{FF_Files.VERSION}]</code></p>"},
                2: {"title": "Tutorial needed?",
                    "text": "If you feel the need to get a refresher-tutorial, "
                            "feel free to go to the menu bar and press <code>Help > Tutorial</code>."}}

        # If last update notice is older than 40 weeks, inform about possibility of a new update
        # time() returns time since the epoch in seconds
        elif popup_dict["last_update_notice"] < (time() - (FF_Files.SECONDS_OF_A_WEEK * 40)):
            # Debug
            logging.info(f"Showing update notice as last notice was on:"
                         f" {ctime(popup_dict['last_update_notice'])}")
            self.pages = {
                1: {"title": "Updating is advised",
                    "text": "<p>Looking for updates?</p>"
                            "<p>It has been more the half a year since you last checked for updates.</p>"
                            "<p>Download the newest versions "
                            f"<a href=\"https://pixel-master.github.io/File-Find/download\">"
                            f"on the File Find Website</a>.<br>"
                            f"The changelog and release date of the newest File Find version can be seen "
                            f"<a href=\"https://pixel-master.github.io/File-Find/download#newest\">"
                            f"here</a>"
                            f"</p>"
                            "<p>Your current (probably not anymore up-to-date) File Find version: "
                            f"<br><code>{FF_Files.VERSION_SHORT} [{FF_Files.VERSION}]</code></p>"}
            }

        else:
            return

        # Resetting time since last update notice
        popup_dict["last_update_notice"] = time()

        # Debug
        logging.debug(f"Reset time since last_update_notice to {ctime(time())}")

        # Setting PopUp File
        popup_dict["FF_ver_welcome"] = False
        popup_dict["FF_welcome"] = False
        settings["popup"] = popup_dict
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "w") as settings_file:
            dump(settings, settings_file)

        # Creating a "sceleton" window on which we can later build on top
        self.Info_Window = QMainWindow(parent)
        self.Info_Window.show()
        self.Info_Window.resize(600, 500)
        self.Info_Window.setWindowTitle(self.pages[1]["title"])
        # Creating a central widget and a layout so that everything is nicely laid out
        self.central_widget = QWidget(self.Info_Window)
        self.Info_Layout = QGridLayout(self.central_widget)
        self.Info_Window.setCentralWidget(self.central_widget)

        # Label in between the two buttons to indicate the number of pages
        self.page_label = QLabel(self.Info_Window)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.Info_Layout.addWidget(self.page_label, 2, 1)

        # Title label
        self.title_label = QLabel(self.Info_Window)
        self.title_label.setFont(BOLD_QT_FONT)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Info_Layout.addWidget(self.title_label, 0, 1)

        # For the actual text we are using a QTextBrowser so that the text is displayed nicely
        self.body_text = QTextBrowser(self.Info_Window)
        self.body_text.setOpenExternalLinks(True)
        self.Info_Layout.addWidget(self.body_text, 1, 1, 1, 1)

        def next_page():
            if not self.next_button.isEnabled():
                return
            self.current_page += 1
            update_info()

        def previous_page():
            if not self.previous_button.isEnabled():
                return
            self.current_page -= 1
            update_info()

        def update_info():
            logging.info(f"Updating info window to page {self.current_page} of {len(self.pages)}")
            if self.current_page > len(self.pages):
                # Button should be deactivated
                logging.error("Tutorial page next button should have been deactivated")
                return
            # On last page
            if self.current_page == len(self.pages):
                self.next_button.setEnabled(False)
                self.next_page_action.setEnabled(False)
            else:
                self.next_button.setEnabled(True)
                self.next_page_action.setEnabled(True)
            # On first page
            if self.current_page == 1:
                # Disable as in the beginning it isn't possible to go back
                self.previous_button.setEnabled(False)
                self.prev_page_action.setEnabled(False)
            else:
                self.previous_button.setEnabled(True)
                self.prev_page_action.setEnabled(True)
            # Update general info
            self.page_label.setText(f"{self.current_page} / {len(self.pages)}")
            self.body_text.setHtml(self.pages[self.current_page]["text"])
            self.title_label.setText(self.pages[self.current_page]["title"])

        # Create buttons to go to next and previous page
        self.next_button = QToolButton(self.Info_Window)
        # Using Qt's built-in icons
        next_icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoNext))
        self.next_button.setIcon(next_icon)
        # Action
        self.next_button.pressed.connect(next_page)
        # Add to Layout
        self.Info_Layout.addWidget(self.next_button, 2, 2)

        # Repeat with the "previous" button
        self.previous_button = QToolButton(self.Info_Window)
        previous_icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious))
        self.previous_button.setIcon(previous_icon)
        # Action
        self.previous_button.pressed.connect(previous_page)
        self.Info_Layout.addWidget(self.previous_button, 2, 0)

        # Menu bar
        self.menu_bar = FF_Menubar.MenuBar(self.Info_Window, "info")
        # Next Page Search
        self.next_page_action = QAction("&Next page", self.parent)
        self.next_page_action.triggered.connect(next_page)
        self.next_page_action.setShortcut("Right")
        self.menu_bar.edit_menu.addAction(self.next_page_action)
        # Previous Page Search
        self.prev_page_action = QAction("&Previous page", self.parent)
        self.prev_page_action.triggered.connect(previous_page)
        self.prev_page_action.setShortcut("Left")
        self.menu_bar.edit_menu.addAction(self.prev_page_action)

        # Insert the Text
        self.current_page = 1
        update_info()
