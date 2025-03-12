# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2025 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the about-window

# Imports
import logging
import os
from sys import platform
from subprocess import run

# PySide6 Gui Imports
from PySide6.QtGui import QFont, QPixmap, QAction
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QGridLayout

import FF_Additional_UI
# Projects Libraries
import FF_Files
import FF_Settings


# The class for the about-window
class AboutWindow:
    def __init__(self, parent):
        # Debug
        logging.debug("Called Help UI")

        # Test if window was already build
        global about_window_global
        if about_window_global is None:
            logging.debug("About UI wasn't build already")
            about_window_global = self.setup(parent)
            about_window_global.show()
        else:
            logging.debug("About UI was build already")
            logging.debug("Displaying About Window...")
            about_window_global.show()

    @staticmethod
    def setup(parent):
        # Debug
        logging.info("Building About UI...")

        # The Base Window with Labels
        about_window = QMainWindow(parent)
        about_window.setWindowTitle("About File Find")

        # Main Layout
        # Create a central widget
        central_widget = QWidget(about_window)
        about_window.setCentralWidget(central_widget)
        # Create the main Layout
        about_layout = QGridLayout(central_widget)
        about_layout.setContentsMargins(30, 30, 30, 30)
        about_layout.setVerticalSpacing(10)

        # File Find for macOS Label
        ff_info = QLabel(about_window)
        # Change Font and Text
        ff_info.setText("File Find")
        ff_info.setFont(QFont("Futura", 30))
        # Display the Label
        about_layout.addWidget(ff_info, 3, 1)

        # File Find Logo
        ff_logo = QLabel(about_window)
        # Set the Icon
        ff_logo_img = QPixmap(os.path.join(FF_Files.ASSETS_FOLDER, "FFlogo_small.png"))
        ff_logo.setPixmap(ff_logo_img)
        # Display the Icon
        about_layout.addWidget(ff_logo, 0, 1, 2, 1)

        # The Version Label
        version_label = QLabel(about_window)
        # Font and Text
        version_label.setText(f"v. {FF_Files.VERSION_SHORT} ({FF_Files.VERSION})")
        version_label.setFont(FF_Additional_UI.DEFAULT_QT_FONT)
        # The command and tooltip
        version_label.setToolTip(f"Version: {FF_Files.VERSION_SHORT} Extended Version: {FF_Files.VERSION}")
        # Display the Label
        about_layout.addWidget(version_label, 4, 1)

        # The Author Label
        author_label = QLabel(about_window)
        # Font and Text
        author_label.setText(
            "Created by Pixel Master, Copyright © 2022–2025 Pixel Master.\nLicensed under the GNU GPLv3")
        author_label.setFont(FF_Additional_UI.DEFAULT_QT_FONT)
        # The command and tooltip
        author_label.setToolTip(f"Version: {FF_Files.VERSION_SHORT} Extended Version: {FF_Files.VERSION}")
        # Display the Label
        author_label.setFixedHeight(50)
        about_layout.addWidget(author_label, 8, 0, 8, 3)

        # Links using QPushButton
        def generate_link_button(displayed_text, domain):
            link = QPushButton(about_window)
            # Font and Text
            link.setText(displayed_text)
            font = QFont(FF_Files.DEFAULT_FONT, FF_Files.DEFAULT_FONT_SIZE)
            font.setUnderline(True)
            link.setFont(font)
            # The command and tooltip
            link.setToolTip(domain)
            # Depends on the os

            if platform == "darwin":
                link.clicked.connect(lambda: run(["open", domain]))
            elif platform == "win32" or platform == "cygwin":
                link.clicked.connect(lambda: run(["start", domain], shell=True))
            elif platform == "linux":
                link.clicked.connect(lambda: run(["xdg-open", domain]))

            # Set the color to a light blue
            link.setStyleSheet("color: #7090FF;")
            # Display the Label
            link.adjustSize()
            link.show()
            # Return the Label to move it
            return link

        update = generate_link_button("Update", "https://pixel-master.github.io/File-Find/download")
        about_layout.addWidget(update, 7, 0)

        sourcecode = generate_link_button("Website and FaQ", "https://pixel-master.github.io/File-Find/")
        about_layout.addWidget(sourcecode, 7, 1)

        faq_link = generate_link_button("Source", "https://github.com/Pixel-Master/File-Find")
        about_layout.addWidget(faq_link, 7, 2)

        # Menu bar
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
        help_action = QAction("&About File Find", about_window)
        help_action.triggered.connect(about_window.show)
        help_menu.addAction(help_action)

        # Tutorial
        tutorial_action = QAction("&Tutorial", about_window)
        tutorial_action.triggered.connect(lambda: FF_Additional_UI.welcome_popups(parent, force_popups=True))
        help_menu.addAction(tutorial_action)

        # Debug
        logging.info("Finished Setting up About UI\n")

        # Sets the Window
        return about_window


about_window_global = None
