# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the classes for additional GUI components like the Help Window

# Imports
import os
from pickle import load, dump
import logging

# PyQt6 Gui Imports
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont, QPixmap, QAction
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFrame, QListWidget, QFileDialog, QComboBox, QMenuBar, \
    QMessageBox

import FF_Additional_UI
# Projects Libraries
import FF_Files


# The class for the Help_Window
class Help_Window:
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
            question_label = QLabel(About_Window)
            question_label.setText(question)
            bold_font = QFont("Arial", 20)
            bold_font.setBold(True)
            question_label.setFont(bold_font)
            question_label.adjustSize()
            question_label.show()
            question_label.move(15, y)

            # The Answer
            answer_label = QLabel(About_Window)
            answer_label.setText(answer)
            answer_label.setFont(QFont("Arial", 13))
            answer_label.adjustSize()
            answer_label.show()
            answer_label.move(25, y + 27)

        # The Base Window with Labels
        About_Window = QMainWindow(parent)
        About_Window.setWindowTitle("File Find Help")
        About_Window.setFixedHeight(700)
        About_Window.setFixedWidth(700)

        # File Find for macOS Label
        ff_info = QLabel(About_Window)
        # Change Font and Text
        ff_info.setText("File Find for macOS")
        ff_info.setFont(QFont("Futura", 30))
        # Display the Label
        ff_info.move(200, 180)
        ff_info.adjustSize()
        ff_info.show()

        # File Find Logo
        ff_logo = QLabel(About_Window)
        # Set the Icon
        ff_logo_img = QPixmap(os.path.join(FF_Files.AssetsFolder, "FFlogo_small.png"))
        ff_logo.setPixmap(ff_logo_img)
        # Display the Icon
        ff_logo.move(280, 50)
        ff_logo.adjustSize()
        ff_logo.show()

        # The Frame
        fflogo_frame = QFrame(About_Window)
        fflogo_frame.setGeometry(QRect(100, 40, 500, 250))
        fflogo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        fflogo_frame.show()

        # The Version Label
        version_label = QLabel(About_Window)
        # Font and Text
        version_label.setText(f"v. {FF_Files.VERSION_SHORT} ({FF_Files.VERSION})")
        version_label.setFont(QFont("Arial", 15))
        # The command and tooltip
        version_label.setToolTip(f"Version: {FF_Files.VERSION_SHORT} Extended Version: {FF_Files.VERSION}")
        # Display the Label
        version_label.adjustSize()
        version_label.show()
        version_label.move(240, 220)

        # Links using QPushButton
        def generate_link_button(displayed_text, domain, color):
            link = QPushButton(About_Window)
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
        sourcecode.move(120, 250)

        update = generate_link_button("Update", "https://gitlab.com/Pixel-Mqster/File-Find/-/releases", "green")
        update.move(310, 250)

        faq_link = generate_link_button("FaQ", "https://gitlab.com/Pixel-Mqster/File-Find#faq", "red")
        faq_link.move(470, 250)

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
        exclude_label = QLabel("Excluded Files:", parent=About_Window)
        # Change Font
        exclude_label.setFont(QFont("Arial", 15))
        # Display the Label
        exclude_label.move(500, 520)
        exclude_label.adjustSize()
        exclude_label.show()

        def generate_button(text, command):
            button = QPushButton(About_Window)
            button.setText(text)
            button.clicked.connect(command)
            button.show()
            button.adjustSize()
            return button

        # Listbox
        excluded_listbox = QListWidget(About_Window)
        # Resize the List-widget
        excluded_listbox.resize(200, 130)
        # Place
        excluded_listbox.move(480, 550)
        # Connect the Listbox
        excluded_listbox.show()

        # Load Files
        with open(os.path.join(FF_Files.LibFolder, "Settings"), "rb") as ExcludedFile:
            files = load(ExcludedFile)["excluded_files"]
        for file in files:
            excluded_listbox.addItem(file)

        # Buttons to add or remove Files
        def edit_excluded(input_file, added=True):

            # Load Settings
            with open(os.path.join(FF_Files.LibFolder, "Settings"), "rb") as SettingsFile:
                settings = load(SettingsFile)
                excluded_files = settings["excluded_files"]

            # Remove or add input to list
            if added:
                excluded_files.append(input_file)

            elif not added:
                excluded_files.remove(input_file)

            # Add changed Settings to dict
            settings["excluded_files"] = excluded_files

            # Dump new settings
            with open(os.path.join(FF_Files.LibFolder, "Settings"), "wb") as SettingsFile:
                dump(settings, SettingsFile)

        def remove_file():
            try:
                logging.info(f"Removed Excluded Folder: {excluded_listbox.currentItem().text()}")
                edit_excluded(excluded_listbox.currentItem().text(), False)
            except AttributeError:
                pass
            excluded_listbox.takeItem(excluded_listbox.currentRow())

        def add_file():
            selected_folder = QFileDialog.getExistingDirectory(directory=FF_Files.userpath, parent=About_Window)
            if selected_folder != "":
                edit_excluded(selected_folder)
                excluded_listbox.addItem(selected_folder)
                logging.info(f"Added Excluded Folder: {selected_folder}")

        remove_button = generate_button("-", remove_file)
        remove_button.move(430, 650)

        add_button = generate_button("+", add_file)
        add_button.move(430, 620)

        # Language
        # Define the Label
        language_label = QLabel("Language:", parent=About_Window)
        # Change Font
        language_label.setFont(QFont("Arial", 15))
        # Display the Label
        language_label.move(10, 560)
        language_label.adjustSize()
        language_label.show()

        # Drop Down Menu
        # Language Menu
        # Defining
        combobox_language = QComboBox(About_Window)
        # Adding Options
        combobox_language.addItems(["English"])
        # Display
        combobox_language.show()
        combobox_language.adjustSize()
        combobox_language.move(200, 550)

        # Open File Find Folder
        # Define the Label
        open_ff_folder_label = QLabel("Open File Find Folder:", parent=About_Window)
        # Change Font
        open_ff_folder_label.setFont(QFont("Arial", 15))
        # Display the Label
        open_ff_folder_label.move(10, 590)
        open_ff_folder_label.adjustSize()
        open_ff_folder_label.show()

        # Push Button
        # Open Button
        # Defining
        open_ff_folder_button = QPushButton(About_Window)
        # Set Text
        open_ff_folder_button.setText("Open")

        # Open Event
        def open_lib_folder():
            folder = FF_Files.LibFolder.replace(" ", "\\ ")
            os.system(f"open -R {folder}")

        open_ff_folder_button.clicked.connect(open_lib_folder)
        # Display
        open_ff_folder_button.show()
        open_ff_folder_button.adjustSize()
        open_ff_folder_button.move(205, 585)

        # Reset Settings
        # Define the Label
        reset_label = QLabel("Reset all Settings:", parent=About_Window)
        # Change Font
        reset_label.setFont(QFont("Arial", 15))
        # Display the Label
        reset_label.move(10, 620)
        reset_label.adjustSize()
        reset_label.show()

        # Push Button
        # Reset Button
        # Defining
        reset_button = QPushButton(About_Window)
        # Set Text
        reset_button.setText("Reset")

        # Reset Event
        def reset_settings():
            # Ask to reset
            if QMessageBox.information(parent, "Resetting?",
                                       "Are you sure to reset?\nResetting requires a restart!",
                                       QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel) \
                    != QMessageBox.StandardButton.Cancel:
                # Reset the settings File
                with open(os.path.join(FF_Files.LibFolder, "Settings"), "wb") as SettingsFile:
                    settings = {"first_version": f"{FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]",
                                "version": f"{FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]",
                                "excluded_files": [],
                                "cache": "On Launch",
                                "popup": {"FF_ver_welcome": True, "FF_welcome": True, "search_question": True}}
                    dump(settings, SettingsFile)

                    # Display a Messagebox
                    FF_Additional_UI.msg.show_info_messagebox("Resetted!", "Resetted all Settings\n\nRestarting now...",
                                                              About_Window)

                    # Quitting
                    exit(0)

        reset_button.clicked.connect(reset_settings)

        # Display
        reset_button.show()
        reset_button.adjustSize()
        reset_button.move(205, 615)

        # Cache Settings
        # Define the Label
        cache_label = QLabel("Delete Cache automatically:", parent=About_Window)
        # Change Font
        cache_label.setFont(QFont("Arial", 15))
        # Display the Label
        cache_label.move(10, 650)
        cache_label.adjustSize()
        cache_label.show()

        # Drop Down Menu
        # Cache Options Menu
        # Defining
        combobox_cache = QComboBox(About_Window)
        # Adding Options
        combobox_cache_items = ["On Launch", "after a Day", "after a Week", "Never"]
        combobox_cache.addItems(combobox_cache_items)
        with open(os.path.join(FF_Files.LibFolder, "Settings"), "rb") as ReadDefineFile:
            combobox_cache.setCurrentText(load(ReadDefineFile)["cache"])

        # Updating on change
        def update_cache_settings():
            # Saving the Settings and replacing the old settings with the new one
            with open(os.path.join(FF_Files.LibFolder, "Settings"), "rb") as ReadFile:
                # Loading Settings
                settings = load(ReadFile)

            # Changing Settings
            settings["cache"] = combobox_cache.currentText()

            # Dumping new Settings
            with open(os.path.join(FF_Files.LibFolder, "Settings"), "wb") as WriteFile:
                dump(settings, WriteFile)

            # Debug
            logging.info(f"Changed Cache Settings to : {combobox_cache.currentText()}")

        combobox_cache.currentIndexChanged.connect(update_cache_settings)

        # Display
        combobox_cache.show()
        combobox_cache.adjustSize()
        combobox_cache.move(200, 645)

        # Menubar
        menu_bar = QMenuBar(About_Window)

        # Menus
        window_menu = menu_bar.addMenu("&Window")
        help_menu = menu_bar.addMenu("&Help")

        # Close Window
        close_action = QAction("&Close Window", About_Window)
        close_action.triggered.connect(About_Window.hide)
        close_action.setShortcut("Ctrl+W")
        window_menu.addAction(close_action)

        # About File Find
        about_action = QAction("&About File Find", About_Window)
        about_action.triggered.connect(About_Window.show)
        help_menu.addAction(about_action)

        # Help
        help_action = QAction("&File Find Help and Settings", About_Window)
        help_action.triggered.connect(About_Window.show)
        help_menu.addAction(help_action)

        # Debug
        logging.info("Finished Setting up Help UI\n")

        # Sets the Window
        return About_Window


about_window_global = None
