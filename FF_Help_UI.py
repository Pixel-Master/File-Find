# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the classes for additional GUI components like the Help Window

# Imports
import os
from pickle import load, dump
import logging

# PyQt6 Gui Imports
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFrame, QListWidget, QFileDialog, QComboBox

# Projects Libraries
import FF_Files


# The class for the Help_window
class Help_Window:
    def __init__(self, parent):
        # Debug
        logging.debug("Called Help UI")
        logging.info("Building Help UI...")

        # A function to generate these Faq texts
        def faq(question, answer, y):
            # The Question
            question_label = QLabel(help_window)
            question_label.setText(question)
            bold_font = QFont("Arial", 25)
            bold_font.setBold(True)
            question_label.setFont(bold_font)
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
        help_label = QLabel("File Find Help", parent=help_window)
        # Change Font
        help_label_font = QFont("Futura", 50)
        help_label_font.setBold(True)
        help_label.setFont(help_label_font)
        # Display the Label
        help_label.move(0, 0)
        help_label.adjustSize()
        help_label.show()

        # File Find for macOS Label
        ff_info = QLabel(help_window)
        # Change Font and Text
        ff_info.setText("File-Find for macOS")
        ff_info.setFont(QFont("Futura", 30))
        # Display the Label
        ff_info.move(200, 230)
        ff_info.adjustSize()
        ff_info.show()

        # File Find Logo
        ff_logo = QLabel(help_window)
        # Set the Icon
        ff_logo_img = QPixmap(os.path.join(FF_Files.AssetsFolder, "FFlogo_small.png"))
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

        # Settings

        # Settings Label
        # Define the Label
        settings_label = QLabel("Settings", parent=help_window)
        # Change Font
        settings_label.setFont(help_label_font)
        # Display the Label
        settings_label.move(0, 480)
        settings_label.adjustSize()
        settings_label.show()

        # Excluded Files
        # Define the Label
        exclude_label = QLabel("Excluded Files", parent=help_window)
        # Change Font
        exclude_label.setFont(QFont("Arial", 20))
        # Display the Label
        exclude_label.move(500, 520)
        exclude_label.adjustSize()
        exclude_label.show()

        def generate_button(text, command):
            button = QPushButton(help_window)
            button.setText(text)
            button.clicked.connect(command)
            button.show()
            button.adjustSize()
            return button

        # Listbox
        excluded_listbox = QListWidget(help_window)
        # Resize the List-widget
        excluded_listbox.resize(200, 130)
        # Place
        excluded_listbox.move(480, 550)
        # Connect the Listbox
        excluded_listbox.show()

        # Load Files
        with open(os.path.join(FF_Files.LibFolder, "Excluded_Files.FFExc"), "rb") as ExcludedFile:
            files = load(ExcludedFile)
        for file in files:
            excluded_listbox.addItem(file)

        # Buttons to add or remove Files
        def edit_excluded(input_file, added=True):
            with open(os.path.join(FF_Files.LibFolder, "Excluded_Files.FFExc"), "rb") as ExcludedUpdateFile:
                old_files = load(ExcludedUpdateFile)
            if added:
                old_files.append(input_file)
            if not added:
                old_files.remove(input_file)
            with open(os.path.join(FF_Files.LibFolder, "Excluded_Files.FFExc"), "wb") as ExcludedUpdateFile:
                dump(old_files, ExcludedUpdateFile)

        def remove_file():
            try:
                logging.info(f"Removed Excluded Folder: {excluded_listbox.currentItem().text()}")
                edit_excluded(excluded_listbox.currentItem().text(), False)
            except AttributeError:
                pass
            excluded_listbox.takeItem(excluded_listbox.currentRow())

        def add_file():
            selected_folder = QFileDialog.getExistingDirectory(directory=FF_Files.userpath, parent=help_window)
            if selected_folder != "":
                edit_excluded(selected_folder)
                excluded_listbox.addItem(selected_folder)
                logging.info(f"Added Excluded Folder: {selected_folder}")

        remove_button = generate_button("-", remove_file)
        remove_button.move(440, 650)

        add_button = generate_button("+", add_file)
        add_button.move(395, 650)

        # Language
        # Define the Label
        language_label = QLabel("Language:", parent=help_window)
        # Change Font
        language_label.setFont(QFont("Arial", 20))
        # Display the Label
        language_label.move(10, 580)
        language_label.adjustSize()
        language_label.show()

        # Drop Down Menus
        # Sorting Menu
        # Defining
        combobox_language = QComboBox(help_window)
        # Adding Options
        combobox_language.addItems(["English"])
        # Display
        combobox_language.show()
        combobox_language.move(120, 580)

        # Debug
        logging.info("Finished Setting up Help UI\n")
