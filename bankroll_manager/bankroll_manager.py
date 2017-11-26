#!/usr/bin/env python3

import logging
import os.path
import string
import sys
import datetime
from configparser import ConfigParser

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
                             QWidget)

import account
from utility import QComboBox_

PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ICON_PATH = os.path.join(PATH, 'icon.png')
CONFIG_PATH = os.path.join(PATH, 'config.ini')
PERIODS = [('Last Hour', datetime.timedelta(hours=1)),
           ('Last Day', datetime.timedelta(days=1)),
           ('Last Week', datetime.timedelta(days=7)),
           ('Last Month', datetime.timedelta(days=30.44)),
           ('Last Year', datetime.timedelta(days=365.2))]
EN_DASH = '–'


def main():
    logging.basicConfig(
        format='[%(asctime)s|%(levelname)s|%(module)s] %(message)s',
        datefmt='%H:%M:%S', level=logging.DEBUG)
    config = ConfigParser()
    config.read(CONFIG_PATH)
    app = QApplication(sys.argv)
    bankroll_manager = BankrollManager(config['location']['data_directory'])
    sys.exit(app.exec_())


class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Poker Bankroll Manager')
        self.setWindowIcon(QIcon(ICON_PATH))
        self.create_widgets()
        self.show()

    def create_widgets(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.widget = dict()
        self.row_elems = int()
        self.add_combo('Account')
        self.add_edit('New Balance')
        self.add_label('Balance')
        self.add_label('Stakes')
        for key, _ in PERIODS:
            self.add_label(key)

    def add_label(self, text):
        self.widget[text] = elem = QLabel(self)
        self.add_element(text, elem)

    def add_combo(self, text):
        self.widget[text] = elem = QComboBox_(self)
        self.add_element(text, elem)

    def add_edit(self, text):
        self.widget[text] = elem = QLineEdit(self)
        self.add_element(text, elem)

    def add_element(self, text, elem):
        name = QLabel(text + ':', self)
        self.layout.addWidget(name, self.row_elems, 0)
        self.layout.addWidget(elem, self.row_elems, 1)
        self.row_elems += 1


class BankrollManager(Application):
    def __init__(self, data_directory):
        super().__init__()
        self.accountant = account.Accountant(data_directory)
        self.widget['Account'].addItems(self.accountant.listing)
        self.load()
        self.widget['Account'].currentTextChanged.connect(self.select)
        self.widget['New Balance'].textEdited.connect(self.pretty_balance)
        self.widget['New Balance'].returnPressed.connect(self.set_balance)

    def select(self, account_name):
        self.accountant.select_account(account_name)
        self.load()

    def load(self):
        selected = self.accountant.selected_account
        logging.debug('load {}'.format(selected.name))
        self.widget['Account'].setCurrentText(selected.name)
        self.widget['Balance'].setText(selected.balance)
        self.widget['Stakes'].setText(selected.stakes)
        for key, timedelta in PERIODS:
            change = selected.change(timedelta)
            if change[0] == '+':
                style = 'color : DarkGreen;'
            elif change[0] == EN_DASH:
                style = 'color : DarkRed;'
            else:
                style = 'color : ;'
            self.widget[key].setText(change)
            self.widget[key].setStyleSheet(style)
        self.widget['New Balance'].setFocus()
        self.setFixedSize(self.sizeHint())

    def pretty_balance(self, text):
        parts = text.split('.', maxsplit=1)
        parts = [''.join(char for char in part if char in string.digits)
                 for part in parts]
        parts[0] = '{:,}'.format(int(parts[0])) if parts[0] else ''
        pretty_text = '.'.join(parts)
        self.widget['New Balance'].setText(pretty_text)

    def set_balance(self):
        value = self.widget['New Balance'].text()
        value = ''.join(char for char in value if char != ',')
        try:
            self.accountant.selected_account.balance = value
        except ValueError as err:
            logging.warning('{}: {}'.format(type(err).__name__, err))
            return
        self.widget['New Balance'].clear()
        self.load()


if __name__ == '__main__':
    main()
