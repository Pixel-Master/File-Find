# This File is a part of File Find made by Pixel-Master and licensed under the GNU GPL v3
# This script contains the classes for additional GUI components like the Help Window

# Imports
import os
from pickle import load, dump
import logging

# PyQt6 Gui Imports
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QFrame, QListWidget, QFileDialog, QComboBox

# Projects Libraries
import FF_Files


# The class for the self.Help_Window
class Help_Window:
    def __init__(self, parent):
        # Debug
        logging.debug("Called Help UI")
        logging.info("Building Help UI...")

        # A function to generate these Faq texts
        def faq(question, answer, y):
            # The Question
            question_label = QLabel(self.Help_Window)
            question_label.setText(question)
            bold_font = QFont("Arial", 25)
            bold_font.setBold(True)
            question_label.setFont(bold_font)
            question_label.adjustSize()
            question_label.show()
            question_label.move(15, y)

            # The Answer
            answer_label = QLabel(self.Help_Window)
            answer_label.setText(answer)
            answer_label.setFont(QFont("Arial", 15))
            answer_label.adjustSize()
            answer_label.show()
            answer_label.move(25, y + 27)

        # The Base Window with Labels
        self.Help_Window = QMainWindow(parent)
        self.Help_Window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        global Help_Window_alias
        try:
            Help_Window_alias.show()
        except NameError:
            Help_Window_alias = self.Help_Window
            Help_Window_alias.show()
        self.Help_Window.setWindowTitle("File Find Help")
        self.Help_Window.setFixedHeight(700)
        self.Help_Window.setFixedWidth(700)

        # File Find for macOS Label
        ff_info = QLabel(self.Help_Window)
        # Change Font and Text
        ff_info.setText("File Find for macOS")
        ff_info.setFont(QFont("Futura", 30))
        # Display the Label
        ff_info.move(200, 180)
        ff_info.adjustSize()
        ff_info.show()

        # File Find Logo
        ff_logo = QLabel(self.Help_Window)
        # Set the Icon
        ff_logo_img = QPixmap(os.path.join(FF_Files.AssetsFolder, "FFlogo_small.png"))
        ff_logo.setPixmap(ff_logo_img)
        # Display the Icon
        ff_logo.move(280, 50)
        ff_logo.adjustSize()
        ff_logo.show()

        # The Frame
        fflogo_frame = QFrame(self.Help_Window)
        fflogo_frame.setGeometry(QRect(100, 40, 500, 250))
        fflogo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        fflogo_frame.show()

        # The Version Label
        version_label = QLabel(self.Help_Window)
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
            link = QPushButton(self.Help_Window)
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

        # Settings Label
        # Define the Label
        settings_label = QLabel("Settings", parent=self.Help_Window)
        # Change Font
        settings_label_font = QFont("Futura", 50)
        settings_label_font.setBold(True)
        settings_label.setFont(settings_label_font)
        # Display the Label
        settings_label.move(0, 480)
        settings_label.adjustSize()
        settings_label.show()

        # Excluded Files
        # Define the Label
        exclude_label = QLabel("Excluded Files", parent=self.Help_Window)
        # Change Font
        exclude_label.setFont(QFont("Arial", 20))
        # Display the Label
        exclude_label.move(500, 520)
        exclude_label.adjustSize()
        exclude_label.show()

        def generate_button(text, command):
            button = QPushButton(self.Help_Window)
            button.setText(text)
            button.clicked.connect(command)
            button.show()
            button.adjustSize()
            return button

        # Listbox
        excluded_listbox = QListWidget(self.Help_Window)
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
            selected_folder = QFileDialog.getExistingDirectory(directory=FF_Files.userpath, parent=self.Help_Window)
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
        language_label = QLabel("Language:", parent=self.Help_Window)
        # Change Font
        language_label.setFont(QFont("Arial", 20))
        # Display the Label
        language_label.move(10, 580)
        language_label.adjustSize()
        language_label.show()

        # Drop Down Menus
        # Sorting Menu
        # Defining
        combobox_language = QComboBox(self.Help_Window)
        # Adding Options
        combobox_language.addItems(["English"])
        # Display
        combobox_language.show()
        combobox_language.move(120, 580)

        # Debug
        logging.info("Finished Setting up Help UI\n")


global Help_Window_alias
