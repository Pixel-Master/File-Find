# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the About window

# Imports
import os
from json import load, dump
import logging

# PyQt6 Gui Imports
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont, QPixmap, QAction
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFrame, QListWidget, QFileDialog, QComboBox, QMenuBar, \
    QMessageBox, QCheckBox

# Projects Libraries
import FF_Files
import FF_Additional_UI


# The class for the help window
class HelpWindow:
    def __init__(self, parent):
        # Debug
        logging.debug("Called Help UI")

        # Test if window was already build
        global about_window_global
        if about_window_global is None:
            logging.debug("Help UI wasn't build already")
            about_window_global = self.setup(parent)
            about_window_global.show()
        else:
            logging.debug("Help UI was build already")
            logging.debug("Displaying About Window...")
            about_window_global.show()

    @staticmethod
    def setup(parent):
        # Debug
        logging.info("Building Help UI...")

        # A function to generate these Faq texts
        def faq(question, answer, y):
            # The Question
            question_label = QLabel(about_window)
            question_label.setText(question)
            bold_font = QFont("Arial", 20)
            bold_font.setBold(True)
            question_label.setFont(bold_font)
            question_label.adjustSize()
            question_label.show()
            question_label.move(15, y)

            # The Answer
            answer_label = QLabel(about_window)
            answer_label.setText(answer)
            answer_label.setFont(QFont("Arial", 13))
            answer_label.adjustSize()
            answer_label.show()
            answer_label.move(25, y + 27)

        # The Base Window with Labels
        about_window = QMainWindow(parent)
        about_window.setWindowTitle("File Find Help")
        about_window.setFixedHeight(700)
        about_window.setFixedWidth(700)

        # File Find for macOS Label
        ff_info = QLabel(about_window)
        # Change Font and Text
        ff_info.setText("File Find for macOS")
        ff_info.setFont(QFont("Futura", 30))
        # Display the Label
        ff_info.move(200, 170)
        ff_info.adjustSize()
        ff_info.show()

        # File Find Logo
        ff_logo = QLabel(about_window)
        # Set the Icon
        ff_logo_img = QPixmap(os.path.join(FF_Files.ASSETS_FOLDER, "FFlogo_small.png"))
        ff_logo.setPixmap(ff_logo_img)
        # Display the Icon
        ff_logo.move(280, 50)
        ff_logo.adjustSize()
        ff_logo.show()

        # The Frame
        fflogo_frame = QFrame(about_window)
        fflogo_frame.setGeometry(QRect(100, 40, 500, 270))
        fflogo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        fflogo_frame.show()

        # The Version Label
        version_label = QLabel(about_window)
        # Font and Text
        version_label.setText(f"v. {FF_Files.VERSION_SHORT} ({FF_Files.VERSION})")
        version_label.setFont(QFont("Arial", 15))
        # The command and tooltip
        version_label.setToolTip(f"Version: {FF_Files.VERSION_SHORT} Extended Version: {FF_Files.VERSION}")
        # Display the Label
        version_label.adjustSize()
        version_label.show()
        version_label.move(260, 210)

        # The Author Label
        author_label = QLabel(about_window)
        # Font and Text
        author_label.setText("Created by Pixel Master, Copyright © 2022–2024 Pixel Master.")
        author_label.setFont(QFont("Arial", 15))
        # The command and tooltip
        author_label.setToolTip(f"Version: {FF_Files.VERSION_SHORT} Extended Version: {FF_Files.VERSION}")
        # Display the Label
        author_label.adjustSize()
        author_label.show()
        author_label.move(120, 240)

        # Links using QPushButton
        def generate_link_button(displayed_text, domain, color):
            link = QPushButton(about_window)
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

        sourcecode = generate_link_button("Source Code", "https://github.com/Pixel-Master/File-Find", "blue")
        sourcecode.move(120, 270)

        update = generate_link_button("Update", "https://github.com/Pixel-Master/File-Find/releases", "green")
        update.move(310, 270)

        faq_link = generate_link_button("FaQ", "https://github.com/Pixel-Master/File-Find#faq", "red")
        faq_link.move(470, 270)

        # Calling the faq functions for the Labels
        faq(question="What is File Find and how does it work?", y=320,
            answer="File Find is an open-source macOS Utility, that makes it easy to find Files.\n"
                   "To search fill in the filters you need and leave the filters you don't need empty.")
        faq(question="Why does File Find sometimes freeze?", y=400,
            answer="It is possible that for example reloading Files or Building the UI at the end of a search"
                   "\ncan cause File Find to freeze. Just wait a minute!")

        # Settings

        # Excluded Files
        # Define the Label
        exclude_label = QLabel("Excluded Files:", parent=about_window)
        # Change Font
        exclude_label.setFont(QFont("Arial", 15))
        # Display the Label
        exclude_label.move(500, 520)
        exclude_label.adjustSize()
        exclude_label.show()

        def generate_button(text, command):
            button = QPushButton(about_window)
            button.setText(text)
            button.clicked.connect(command)
            button.show()
            button.adjustSize()
            return button

        # Listbox
        excluded_listbox = QListWidget(about_window)
        # Resize the List-widget
        excluded_listbox.resize(200, 130)
        # Place
        excluded_listbox.move(480, 550)
        # Connect the Listbox
        excluded_listbox.show()

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
            selected_folder = QFileDialog.getExistingDirectory(directory=FF_Files.USER_FOLDER, parent=about_window)
            if selected_folder != "":
                edit_excluded(selected_folder)
                excluded_listbox.addItem(selected_folder)
                logging.info(f"Added Excluded Folder: {selected_folder}")

            # Enable button if there are  files
            if excluded_listbox.count() != 0:
                remove_button.setDisabled(False)

        remove_button = generate_button("-", remove_file)
        remove_button.move(430, 650)

        # Disable button if there are no files
        if excluded_listbox.count() == 0:
            remove_button.setDisabled(True)

        add_button = generate_button("+", add_file)
        add_button.move(430, 620)

        # Ask when searching
        # Define the Label
        ask_search_label = QLabel("Ask before deleting a file:", parent=about_window)
        # Change Font
        ask_search_label.setFont(QFont("Arial", 15))
        # Display the Label
        ask_search_label.move(10, 530)
        ask_search_label.adjustSize()
        ask_search_label.show()

        # Push Button
        # Ask Checkbox
        # Defining
        ask_delete_checkbox = QCheckBox(about_window)

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
        ask_delete_checkbox.move(205, 525)

        # Language
        # Define the Label
        language_label = QLabel("Language:", parent=about_window)
        # Change Font
        language_label.setFont(QFont("Arial", 15))
        # Display the Label
        language_label.move(10, 560)
        language_label.adjustSize()
        language_label.show()

        # Drop Down Menu
        # Language Menu
        # Defining
        combobox_language = QComboBox(about_window)
        # Adding Options
        combobox_language.addItems(["English"])
        # Display
        combobox_language.show()
        combobox_language.adjustSize()
        combobox_language.move(200, 550)

        # Open File Find Folder
        # Define the Label
        open_ff_folder_label = QLabel("Open File Find Folder:", parent=about_window)
        # Change Font
        open_ff_folder_label.setFont(QFont("Arial", 15))
        # Display the Label
        open_ff_folder_label.move(10, 590)
        open_ff_folder_label.adjustSize()
        open_ff_folder_label.show()

        # Push Button
        # Open Button
        # Defining
        open_ff_folder_button = QPushButton(about_window)
        # Set Text
        open_ff_folder_button.setText("Open")

        # Open Event
        def open_lib_folder():
            # Debug
            logging.debug(f"Open File Find Folder: {FF_Files.FF_LIB_FOLDER}")

            # Opening folder with the macOS open command
            os.system(f"open -R {FF_Files.convert_file_name_for_terminal(FF_Files.FF_LIB_FOLDER)}")

        open_ff_folder_button.clicked.connect(open_lib_folder)
        # Display
        open_ff_folder_button.show()
        open_ff_folder_button.adjustSize()
        open_ff_folder_button.move(205, 585)

        # Reset Settings
        # Define the Label
        reset_label = QLabel("Reset File Find:", parent=about_window)
        # Change Font
        reset_label.setFont(QFont("Arial", 15))
        # Display the Label
        reset_label.move(10, 620)
        reset_label.adjustSize()
        reset_label.show()

        # Push Button
        # Reset Button
        # Defining
        reset_button = QPushButton(about_window)
        # Set Text
        reset_button.setText("Reset")

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
                FF_Additional_UI.PopUps.show_info_messagebox("Resetted!", "Resetted File Find\n\nRestarting now...",
                                                             about_window)

                # Deleting the File Find Folder with the rm command
                os.system(f"rm -rf {FF_Files.convert_file_name_for_terminal(FF_Files.FF_LIB_FOLDER)}")

                # Exiting
                logging.fatal("Resetted, Exiting...")
                exit(0)

        reset_button.clicked.connect(reset_settings)

        # Display
        reset_button.show()
        reset_button.adjustSize()
        reset_button.move(205, 615)

        # Cache Settings
        # Define the Label
        cache_label = QLabel("Delete Cache automatically:", parent=about_window)
        # Change Font
        cache_label.setFont(QFont("Arial", 15))
        # Display the Label
        cache_label.move(10, 650)
        cache_label.adjustSize()
        cache_label.show()

        # Drop Down Menu
        # Cache Options Menu
        # Defining
        combobox_cache = QComboBox(about_window)
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
        combobox_cache.move(200, 645)

        # Menubar
        menu_bar = QMenuBar(about_window)

        # Menus
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Close Window
        close_action = QAction("&Close Window", about_window)
        close_action.triggered.connect(about_window.hide)
        close_action.setShortcut("Ctrl+W")
        window_menu.addAction(close_action)

        # About File Find
        about_action = QAction("&About File Find", about_window)
        about_action.triggered.connect(about_window.show)
        help_menu.addAction(about_action)

        # Help
        help_action = QAction("&File Find Help and Settings", about_window)
        help_action.triggered.connect(about_window.show)
        help_menu.addAction(help_action)

        # Debug
        logging.info("Finished Setting up Help UI\n")

        # Sets the Window
        return about_window


about_window_global = None
