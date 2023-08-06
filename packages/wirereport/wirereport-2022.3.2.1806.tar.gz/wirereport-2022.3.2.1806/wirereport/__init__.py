# -*- coding: utf-8 -*-

'''
################################################################################
#                                                                              #
# report                                                                       #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is a small text editor.                                         #
#                                                                              #
# copyright (C) 2014 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses>.                                               #
#                                                                              #
################################################################################
'''

import os
import sys

from PyQt5.QtGui import(
    QColor,
    QFont,
    QFontDatabase
)
from PyQt5.QtWidgets import(
    QAction,
    QApplication,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QTextEdit,
    QWidget
)

name        = 'report'
__version__ = '2022-03-02T1806Z'

def main():
    print(f'{name} {__version__}')
    application = QApplication(sys.argv)
    report      = Report()
    sys.exit(application.exec_())

class Report(QMainWindow):

    def __init__(self):
        super(Report, self).__init__()
        self.status_view                      = 'window'
        self.status_colors                    = 'light'
        self.style_QTextEdit_color            = '#000000'
        self.style_QTextEdit_background_color = '#ffffff'
        self.font_size                        = 22

        # set up fonts
        self.font_database = QFontDatabase()
        # add font cmtex9
        self.font_file_cmtex9 = os.path.dirname(__file__) + '/fonts/cmtex9.ttf'
        self.font_identifier_cmtex9 = QFontDatabase.addApplicationFont(self.font_file_cmtex9)
        self.fontFamilyName_cmtex9 = self.font_database.applicationFontFamilies(self.font_identifier_cmtex9)[0]
        self.font_cmtex9 = QFont(self.fontFamilyName_cmtex9, self.font_size)
        # add font Courier Prime
        #self.font_CourierPrime = QFont('Courier Prime', self.font_size)
        # set default font
        self.fontFamilyName_current = 'cmtex9'
        self.font_current = self.font_cmtex9
        self.font_current.setFixedPitch(True)

        self.initialise_UI()

    def initialise_UI(self):
        action_toggle_view = QAction('toggle fullscreen/window view', self)
        action_toggle_view.setShortcut('F11')
        action_toggle_view.setStatusTip('toggle fullscreen/window view')
        action_toggle_view.triggered.connect(self.toggle_view)

        action_toggle_colors = QAction('toggle light/dark colors', self)
        action_toggle_colors.setShortcut('Ctrl+D')
        action_toggle_colors.setStatusTip('toggle light/dark colors')
        action_toggle_colors.triggered.connect(self.toggle_colors)

        action_set_font_foreground_color = QAction('set font foreground color', self)
        action_set_font_foreground_color.setStatusTip('set font foreground color')
        action_set_font_foreground_color.triggered.connect(self.set_font_foreground_color)

        action_set_font_background_color = QAction('set font background color', self)
        action_set_font_background_color.setStatusTip('set font background color')
        action_set_font_background_color.triggered.connect(self.set_font_background_color)

        action_set_font_size = QAction('set font size', self)
        action_set_font_size.setShortcut('Ctrl+T')
        action_set_font_size.setStatusTip('set font size')
        action_set_font_size.triggered.connect(self.set_font_size)

        action_set_font = QAction('set font', self)
        action_set_font.setStatusTip('set font')
        action_set_font.triggered.connect(self.set_font)

        action_new = QAction('new', self)
        action_new.setShortcut('Ctrl+N')
        action_new.setStatusTip('create new file')
        action_new.triggered.connect(self.new_file)

        action_save = QAction('save', self)
        action_save.setShortcut('Ctrl+S')
        action_save.setStatusTip('save current file')
        action_save.triggered.connect(self.save_file)

        action_open = QAction('open', self)
        action_open.setShortcut('Ctrl+O')
        action_open.setStatusTip('open a file')
        action_open.triggered.connect(self.open_file)

        action_close = QAction('close', self)
        action_close.setShortcut('Ctrl+W')
        action_close.setStatusTip('close')
        action_close.triggered.connect(self.close)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&file')
        file_menu.addAction(action_toggle_view)
        file_menu.addAction(action_toggle_colors)
        file_menu.addAction(action_set_font_foreground_color)
        file_menu.addAction(action_set_font_background_color)
        file_menu.addAction(action_set_font_size)
        file_menu.addAction(action_set_font)
        file_menu.addAction(action_new)
        file_menu.addAction(action_save)
        file_menu.addAction(action_open)
        file_menu.addAction(action_close)

        self.text = QTextEdit(self)
        self.setCentralWidget(self.text)
        self.setGeometry(0, 0, 450, 725)
        #self.showMaximized()
        self.setWindowTitle('report')
        self.update_style_sheet()
        self.show()

    def update_style_sheet(self):
        style = '''
            QTextEdit{
                color: self.style_QTextEdit_color;
                background-color: self.style_QTextEdit_background_color;
                padding-left:10; padding-top:10; padding-bottom:10; padding-right:10;
                font: self.font_sizept self.fontFamilyName_current;
                border-radius: 9px;
            }
            '''
        style = style.replace('self.style_QTextEdit_color', self.style_QTextEdit_color)
        style = style.replace('self.style_QTextEdit_background_color', self.style_QTextEdit_background_color)
        style = style.replace('self.font_size', str(self.font_size))
        style = style.replace('self.fontFamilyName_current', self.fontFamilyName_current)
        self.text.setStyleSheet(style)

    def toggle_view(self):
        if self.status_view == 'window':
            self.showFullScreen()
            self.status_view = 'fullscreen'
            return
        if self.status_view == 'fullscreen':
            self.showMaximized()
            self.status_view = 'window'
            return

    def toggle_colors(self):
        if self.status_colors == 'light':
            self.style_QTextEdit_color            = '#ffffff'
            self.style_QTextEdit_background_color = '#000000'
            self.update_style_sheet()
            self.status_colors = 'dark'
            return
        if self.status_colors == 'dark':
            self.style_QTextEdit_color            = '#000000'
            self.style_QTextEdit_background_color = '#ffffff'
            self.update_style_sheet()
            self.status_colors = 'light'
            return

    def set_font_size(self):
        font_size, ok = QInputDialog.getText(self, 'font size', 'enter font size:')
        if ok:
            self.font_size = int(font_size)
            self.update_style_sheet()

    def set_font(self):
        font_name, ok = QInputDialog.getText(self, 'font name', 'enter font name:')
        if ok:
            self.fontFamilyName_current = font_name
            self.update_style_sheet()

    def set_font_foreground_color(self):
        font_foreground_color, ok = QInputDialog.getText(self, 'font foreground color', 'enter font foreground color:')
        if ok:
            self.style_QTextEdit_color = font_foreground_color
            self.update_style_sheet()

    def set_font_background_color(self):
        font_background_color, ok = QInputDialog.getText(self, 'font background color', 'enter font background color:')
        if ok:
            self.style_QTextEdit_background_color = font_background_color
            self.update_style_sheet()

    def new_file(self):
        self.text.clear()

    def save_file(self):
        filename = QFileDialog.getSaveFileName(self, 'save file', os.getenv('HOME'))[0]
        if filename != u'':
            with open(filename, 'w') as file_save:
                file_data = self.text.toPlainText()
                file_save.write(file_data)

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, 'open file', os.getenv('HOME'))[0]
        with open(filename, 'r') as file_open:
            file_data = file_open.read()
            self.text.setText(file_data)

if __name__ == '__main__':
    main()
