#!/usr/bin/env python3

import logging
import os.path
import sys
from configparser import ConfigParser

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
                             QLineEdit, QWidget)

import account

PATH = os.path.dirname(os.path.realpath(__file__))
ICON_PATH = os.path.join(PATH, 'icon.png')
CONFIG_PATH = os.path.join(PATH, 'config.ini')


def main():
    logging.basicConfig(
        format='[%(asctime)s|%(levelname)s|%(module)s] %(message)s',
        datefmt='%H:%M:%S', level=logging.INFO)
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
        self.add_label('Last Hour')
        self.add_label('Last Day')
        self.add_label('Last Week')
        self.add_label('Last Month')
        self.add_label('Last Year')

    def add_label(self, text):
        self.widget[text] = elem = QLabel(self)
        self.add_element(text, elem)

    def add_combo(self, text):
        self.widget[text] = elem = QComboBox(self)
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
        self.manager = account.Manager(data_directory)
        self.widget['Account'].addItems(self.manager.listing)
        self.load()
        self.widget['Account'].currentTextChanged.connect(self.select)
        self.widget['New Balance'].returnPressed.connect(self.set_balance)

    def select(self, account):
        self.manager.selected = account
        self.load()

    def load(self):
        account = self.manager.selected
        logging.debug('load {}'.format(account))
        self.widget['Account'].setCurrentText(account)
        self.widget['Balance'].setText(self.manager.balance)
        self.widget['Stakes'].setText(self.manager.stakes)
        for period in ['hour', 'day', 'week', 'month', 'year']:
            key = 'Last ' + period.capitalize()
            change = self.manager.change(period)
            if change[0] == '+':
                style = 'color : DarkGreen;'
            elif change[0] == '–':
                style = 'color : DarkRed;'
            else:
                style = 'color : ;'
            self.widget[key].setText(change)
            self.widget[key].setStyleSheet(style)
        self.widget['New Balance'].setFocus()
        self.setFixedSize(self.sizeHint())

    def set_balance(self):
        value = self.widget['New Balance'].text()
        try:
            self.manager.balance = value
        except ValueError as err:
            logging.warning('{}: {}'.format(type(err).__name__, err))
            return
        self.widget['New Balance'].clear()
        self.load()


if __name__ == '__main__':
    main()