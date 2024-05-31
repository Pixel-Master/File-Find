# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the settings window

# Imports
import logging
import os
from json import load, dump
import shutil
import sys

# PySide6 Gui Imports
from PySide6.QtGui import QFont, QAction, Qt
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QListWidget, QFileDialog, QComboBox, \
    QMessageBox, QCheckBox, QWidget, QGridLayout, QSizePolicy, QSpacerItem, QLineEdit

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_About_UI


# The class for the help window
class SettingsWindow:
    def __init__(self, parent):
        # Debug
        logging.debug("Called Help UI")

        # Define the window
        self.Settings_Window = QMainWindow(parent)

        # Test if window was already build
        global settings_window_global
        if settings_window_global is None:
            logging.debug("Help UI wasn't build already")
            settings_window_global = self.Settings_Window
            settings_window_global.show()
        else:
            logging.debug("Settings UI was build already")
            logging.debug("Displaying Settings Window...")
            settings_window_global.show()
            settings_window_global.setFocus()
            return

            # Debug
        logging.info("Building Settings UI...")

        # Window setup
        # Set the Title of the Window
        self.Settings_Window.setWindowTitle(f"File Find Settings v. {FF_Files.VERSION_SHORT} ({FF_Files.VERSION})")
        # Set the start size of the Window, because it's resizable
        self.BASE_WIDTH = 500
        self.BASE_HEIGHT = 400
        self.Settings_Window.setBaseSize(self.BASE_WIDTH, self.BASE_HEIGHT)

        # Adding Layouts
        # Main Layout
        # Create a central widget
        self.Central_Widget = QWidget(parent=self.Settings_Window)
        self.Settings_Window.setCentralWidget(self.Central_Widget)
        # Create the main Layout
        self.Settings_Layout = QGridLayout(self.Central_Widget)
        self.Settings_Layout.setContentsMargins(20, 20, 20, 20)

        self.Central_Widget.setLayout(self.Settings_Layout)

        # # Spacer for prettier ui
        self.Settings_Layout.addItem(QSpacerItem(10, 30, hData=QSizePolicy.Policy.Maximum), 8, 0)

        # Excluded Files
        # Define the Label
        exclude_label = QLabel("Always excluded files:", parent=self.Settings_Window)
        # Change Font
        exclude_label.setFont(QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE))
        # Display the Label
        self.Settings_Layout.addWidget(exclude_label, 9, 0)

        def generate_button(text, command, width: int | None = 30):
            button = QPushButton(self.Settings_Window)
            button.setText(text)
            button.clicked.connect(command)
            if width is not None:
                button.setFixedWidth(width)
            return button

        # Listbox
        excluded_listbox = QListWidget(self.Settings_Window)
        # Resize the List-widget
        excluded_listbox.resize(200, 130)
        # Place
        self.Settings_Layout.addWidget(excluded_listbox, 9, 1, 11, 3)

        # Load Files
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as excluded_file:
            files = load(excluded_file)["excluded_files"]
        for file in files:
            excluded_listbox.addItem(file)

        # Buttons to add or remove Files
        def edit_excluded(input_file, added=True):

            # Load Settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as settings_file:
                settings = load(settings_file)
                excluded_files = settings["excluded_files"]

            # Remove or add input to list
            if added:
                excluded_files.append(input_file)

            elif not added:
                excluded_files.remove(input_file)

            # Add changed Settings to dict
            settings["excluded_files"] = excluded_files

            # Dump new settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "w") as settings_file:
                dump(settings, settings_file)

        def remove_file():
            try:
                logging.info(f"Removed Excluded Folder: {excluded_listbox.currentItem().text()}")
                edit_excluded(excluded_listbox.currentItem().text(), False)
            except AttributeError:
                pass
            excluded_listbox.takeItem(excluded_listbox.currentRow())

            # Disable button if there are no files
            if excluded_listbox.count() == 0:
                remove_button.setDisabled(True)

        def add_file():
            selected_folder = QFileDialog.getExistingDirectory(dir=FF_Files.USER_FOLDER, parent=self.Settings_Window)
            if selected_folder != "":
                edit_excluded(selected_folder)
                excluded_listbox.addItem(selected_folder)
                logging.info(f"Added Excluded Folder: {selected_folder}")

            # Enable button if there are  files
            if excluded_listbox.count() != 0:
                remove_button.setDisabled(False)

        remove_button = generate_button("-", remove_file)
        self.Settings_Layout.addWidget(remove_button, 11, 0, Qt.AlignmentFlag.AlignRight)

        # Disable button if there are no files
        if excluded_listbox.count() == 0:
            remove_button.setDisabled(True)

        add_button = generate_button("+", add_file)
        self.Settings_Layout.addWidget(add_button, 12, 0, Qt.AlignmentFlag.AlignRight)

        # Ask when searching
        # Define the Label
        ask_search_label = QLabel("Ask before deleting a file:", parent=self.Settings_Window)
        # Change Font
        ask_search_label.setFont(QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE))
        # Display the Label
        self.Settings_Layout.addWidget(ask_search_label, 0, 0)
        ask_search_label.adjustSize()
        ask_search_label.show()

        # Push Button
        # Ask Checkbox
        # Defining
        ask_delete_checkbox = QCheckBox(self.Settings_Window)

        # Open Event
        def ask_delete_change():
            # Saving the Settings and replacing the old settings with the new one
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as read_file:
                # Loading Settings
                settings = load(read_file)

            # Changing Settings
            settings["popup"]["delete_question"] = ask_delete_checkbox.isChecked()

            logging.info(f"Changed PopUp Settings Delete Question:"
                         f" Ask before deleting {ask_delete_checkbox.isChecked()}")
            # Dumping new Settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "w") as write_file:
                dump(settings, write_file)

        # Connecting the checkbox to the function above
        ask_delete_checkbox.toggled.connect(ask_delete_change)

        # Loading Settings
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as read_load_file:
            # Loading Settings
            ask_searching_settings = load(read_load_file)["popup"]["delete_question"]

            # Changing Settings
            if ask_searching_settings:
                ask_delete_checkbox.setChecked(True)

        # Display
        ask_delete_checkbox.show()
        ask_delete_checkbox.adjustSize()
        self.Settings_Layout.addWidget(ask_delete_checkbox, 0, 1)

        # Language
        # Define the Label
        filter_preset_label = QLabel("Filter Preset on launch:", parent=self.Settings_Window)
        filter_preset_label.setToolTip("The filter preset loaded at launch")
        # Change Font
        filter_preset_label.setFont(QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE))
        # Display the Label
        self.Settings_Layout.addWidget(filter_preset_label, 1, 0)

        # Input label for displaying file name
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as settings_load_file:
            filter_preset_name = load(settings_load_file)["filter_preset_name"]

        filter_line_edit = QLineEdit(self.Settings_Window)
        filter_line_edit.setText(filter_preset_name)
        filter_line_edit.setReadOnly(True)
        self.Settings_Layout.addWidget(filter_line_edit, 1, 1)

        # Function for resetting filter preset settings
        def reset_filter_preset():
            # Debug
            logging.info("Setting filter preset to default\n")
            # Loading settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as settings_preset_file:
                settings = load(settings_preset_file)
                # Modifying Settings
                settings["filter_preset_name"] = FF_Files.STANDARD_SETTINGS["filter_preset_name"]

            # Updating line edit
            filter_line_edit.setText(FF_Files.STANDARD_SETTINGS["filter_preset_name"])

            # Dump new settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "w") as settings_preset_file:
                dump(settings, settings_preset_file)

            try:
                # Removing filter preset
                os.remove(os.path.join(FF_Files.FF_LIB_FOLDER, "Default.FFFilter"))
            except FileNotFoundError:
                # If it doesn't exist it doesn't matter
                pass

        reset_preset_button = generate_button("Set to default", reset_filter_preset, 120)
        self.Settings_Layout.addWidget(reset_preset_button, 1, 2)

        # Select a filter preset (.FFFilter)
        def select_preset():
            # Debug
            logging.debug("Asking for path for updating filter preset, applied on launch")

            # Getting path
            file_path = QFileDialog.getOpenFileName(
                self.Settings_Window,
                "Select a .FFFilter preset",
                FF_Files.USER_FOLDER,
                filter="*.FFFilter")[0]

            # If user pressed "cancel"
            if file_path == "":
                # Debug
                logging.debug("No file was selected")
                # Quit
                return

            # Coping file into File-Find-Library folder
            with open(file_path, "rb") as user_preset_file:
                preset = load(user_preset_file)

            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Default.FFFilter"), "w") as settings_preset_file:
                dump(preset, settings_preset_file)

            # Updating line edit
            filter_line_edit.setText(os.path.basename(file_path))

            # Updating settings

            # Loading settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as settings_preset_file:
                settings = load(settings_preset_file)
                # Modifying Settings
                settings["filter_preset_name"] = os.path.basename(file_path)

            # Dump new settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "w") as settings_preset_file:
                dump(settings, settings_preset_file)

            # Debug
            logging.info(f"Set filter preset to {file_path}\n")

        select_preset_button = generate_button("Select .FFFilter Preset", select_preset, 150)
        self.Settings_Layout.addWidget(select_preset_button, 1, 3)

        # Language
        # Define the Label
        language_label = QLabel("Language:", parent=self.Settings_Window)
        # Change Font
        language_label.setFont(QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE))
        # Display the Label
        self.Settings_Layout.addWidget(language_label, 2, 0)

        # Drop Down Menu
        # Language Menu
        # Defining
        combobox_language = QComboBox(self.Settings_Window)
        # Adding Options
        combobox_language.addItems(["English"])
        # Display
        self.Settings_Layout.addWidget(combobox_language, 2, 1)

        # Push Button

        # Reset Settings
        # Define the Label
        reset_label = QLabel("Reset File Find:", parent=self.Settings_Window)
        # Change Font
        reset_label.setFont(QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE))
        # Display the Label
        self.Settings_Layout.addWidget(reset_label, 4, 0)
        reset_label.adjustSize()
        reset_label.show()

        # Push Button
        # Reset Button
        # Defining
        reset_button = QPushButton(self.Settings_Window)
        # Set Text
        reset_button.setText("Reset")
        # Make it not change size
        reset_button.setFixedWidth(80)

        # Reset Event
        def reset_settings():
            # Ask to reset
            logging.info("Pressed Reset, asking...")

            if QMessageBox.information(
                    parent, "Resetting?",
                    "Are you sure to reset?\nResetting requires a restart!",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) \
                    != QMessageBox.StandardButton.Cancel:
                # Debug
                logging.warning("Resetting File Find...")

                # Display a Messagebox
                FF_Additional_UI.PopUps.show_info_messagebox(
                    "Reset!", "Press \"OK\" to finish reset.\n Manual restart is required.",
                    self.Settings_Window)

                # Deleting the File Find Folder with the rm command
                shutil.rmtree(FF_Files.FF_LIB_FOLDER)

                # Exiting
                logging.fatal("Reset, Exiting...")
                sys.exit(0)

        reset_button.clicked.connect(reset_settings)

        # Display
        self.Settings_Layout.addWidget(reset_button, 4, 1)

        # Cache Settings
        # Define the Label
        cache_label = QLabel("Delete Cache automatically:", parent=self.Settings_Window)
        # Change Font
        cache_label.setFont(QFont(FF_Files.DEFAULT_FONT, FF_Files.SMALLER_FONT_SIZE))
        # Display the Label
        self.Settings_Layout.addWidget(cache_label, 5, 0)

        # Drop Down Menu
        # Cache Options Menu
        # Defining
        combobox_cache = QComboBox(self.Settings_Window)
        # Adding Options
        combobox_cache_items = ["On Launch", "after a Day", "after a Week", "Never"]
        combobox_cache.addItems(combobox_cache_items)
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as read_define_file:
            combobox_cache.setCurrentText(load(read_define_file)["cache"])

        # Updating on change
        def update_cache_settings():
            # Saving the Settings and replacing the old settings with the new one
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings")) as read_file:
                # Loading Settings
                settings = load(read_file)

            # Changing Settings
            settings["cache"] = combobox_cache.currentText()

            # Dumping new Settings
            with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "w") as write_rile:
                dump(settings, write_rile)

            # Debug
            logging.info(f"Changed Cache Settings to : {combobox_cache.currentText()}")

        combobox_cache.currentIndexChanged.connect(update_cache_settings)

        # Display
        combobox_cache.show()
        combobox_cache.adjustSize()
        self.Settings_Layout.addWidget(combobox_cache, 5, 1)

        # Menu-bar
        menu_bar = self.Settings_Window.menuBar()

        # Menus
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Close Window
        close_action = QAction("&Close Window", self.Settings_Window)
        close_action.triggered.connect(self.Settings_Window.hide)
        close_action.setShortcut("Ctrl+W")
        window_menu.addAction(close_action)

        # About File Find
        about_action = QAction("&About File Find", self.Settings_Window)
        about_action.triggered.connect(lambda: FF_About_UI.AboutWindow(self.Settings_Window))
        help_menu.addAction(about_action)

        # Help
        help_action = QAction("&About File Find", self.Settings_Window)
        help_action.triggered.connect(lambda: FF_About_UI.AboutWindow(self.Settings_Window))
        help_menu.addAction(help_action)

        # Tutorial
        tutorial_action = QAction("&Tutorial", self.Settings_Window)
        tutorial_action.triggered.connect(lambda: FF_Additional_UI.welcome_popups(parent, force_popups=True))
        help_menu.addAction(tutorial_action)

        # Debug
        logging.info("Finished Setting up Help UI\n")


settings_window_global = None
