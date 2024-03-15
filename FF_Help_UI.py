# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the help/about window

# Imports
import logging
import os
from sys import platform
from subprocess import run

# PySide6 Gui Imports
from PySide6.QtCore import QRect
from PySide6.QtGui import QFont, QPixmap, QAction
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QFrame

# Projects Libraries
import FF_Files
import FF_Settings


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
        about_window.setWindowTitle("About File Find")
        about_window.setFixedHeight(500)
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
        logo_frame = QFrame(about_window)
        logo_frame.setGeometry(QRect(100, 40, 500, 270))
        logo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        logo_frame.show()

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
        author_label.setText(
            "Created by Pixel Master, Copyright © 2022–2024 Pixel Master.\nLicensed under the GNU GPLv3")
        author_label.setFont(QFont("Arial", 15))
        # The command and tooltip
        author_label.setToolTip(f"Version: {FF_Files.VERSION_SHORT} Extended Version: {FF_Files.VERSION}")
        # Display the Label
        author_label.adjustSize()
        author_label.show()
        author_label.move(120, 230)

        # Links using QPushButton
        def generate_link_button(displayed_text, domain, color):
            link = QPushButton(about_window)
            # Font and Text
            link.setText(displayed_text)
            link.setFont(QFont("Arial", 20))
            # The command and tooltip
            link.setToolTip(domain)
            # Depends on the os

            if platform == "darwin":
                link.clicked.connect(lambda: run(["open", domain]))
            elif platform == "win32" or platform == "cygwin":
                link.clicked.connect(lambda: run(["start", domain], shell=True))
            elif platform == "linux":
                link.clicked.connect(lambda: run(["xdg-open", domain]))

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

        # Menubar
        menu_bar = about_window.menuBar()

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

        # Settings
        settings_action = QAction("&Settings", about_window)
        settings_action.triggered.connect(lambda: FF_Settings.SettingsWindow(about_window))
        settings_action.setShortcut("Ctrl+,")
        help_menu.addAction(settings_action)

        # Help
        help_action = QAction("&File Find Settings", about_window)
        help_action.triggered.connect(about_window.show)
        help_menu.addAction(help_action)

        # Debug
        logging.info("Finished Setting up Help UI\n")

        # Sets the Window
        return about_window


about_window_global = None
