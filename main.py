#!/usr/bin/env python3

import functools
import logging
import tkinter as tk
import tkinter.font as tkf

import account


def main():
	logging.basicConfig(format='[%(levelname)s] %(message)s',
	                    level=logging.DEBUG)
	root = tk.Tk()
	root.wm_title('Poker Bankroll Manager')
	app = Application(root)
	app.mainloop()


class Application(tk.Frame):

	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.font = tkf.nametofont('TkDefaultFont')
		self.font.configure(size=11)
		self.pack(padx=10, pady=10)
		self.widget = dict()
		self.label = dict()
		self.row = int()
		self.manager = account.Manager()
		self.createWidgets()
		self.load()

	def createWidgets(self):
		self.add_dropdown('Account')
		self.set_options('Account', self.manager.listing, self.select)
		self.add_label('Balance')
		self.add_label('Stakes')
		self.add_entry('Transaction', self.transaction)
		self.add_entry('New Balance', self.set_balance)
		self.add_label('Last Hour')
		self.add_label('Last Day')
		self.add_label('Last Week')
		self.add_label('Last Month')
		self.add_label('Last Year')

	def select(self, account):
		self.manager.selected = account
		self.load()

	def load(self):
		account = self.manager.selected
		self.set_label('Account', account)
		self.set_label('Balance', self.manager.balance)
		self.set_label('Stakes', self.manager.stakes)
		for period in ['hour', 'day', 'week', 'month', 'year']:
			key = 'Last ' + period.capitalize()
			change = self.manager.change(period)
			color = 'dark red' if change.startswith('–') else 'dark green'
			self.set_label(key, change, color)

	def transaction(self, _):
		value = self.get_label('Transaction')
		try:
			self.manager.transaction(value)
		except ValueError as err:
			logging.warning('{}: {}'.format(type(err).__name__, err))
			return
		self.set_label('Transaction', '')
		self.load()

	def set_balance(self, _):
		value = self.get_label('New Balance')
		try:
			self.manager.balance = value
		except ValueError as err:
			logging.warning('{}: {}'.format(type(err).__name__, err))
			return
		self.set_label('New Balance', '')
		self.load()

	def add_label(self, text):
		self.label[text] = tk.StringVar()
		l = tk.Label(self, textvariable=self.label[text])
		self.add_element(text, l)

	def add_entry(self, text, cmd):
		self.label[text] = tk.StringVar()
		e = tk.Entry(self, textvariable=self.label[text], font=self.font)
		e.bind('<Return>', cmd)
		self.add_element(text, e)

	def add_dropdown(self, text):
		self.label[text] = tk.StringVar()
		o = tk.OptionMenu(self, self.label[text], ' ')
		o['menu'].config(font=self.font)
		self.add_element(text, o)

	def set_options(self, key, choices, cmd):
		self.label[key].set(' ')
		self.widget[key]['menu'].delete(0, 'end')
		for choice in choices:
			command = functools.partial(cmd, choice)
			self.widget[key]['menu'].add_command(label=choice, command=command)

	def add_element(self, text, elem):
		l = tk.Label(self, text=text+':')
		l.grid(row=self.row, column=0, sticky='E', padx=5, pady=5)
		elem.grid(row=self.row, column=1, sticky='W', padx=5, pady=5)
		self.row += 1
		self.widget[text] = elem

	def set_label(self, key, new, color=None):
		self.label[key].set(new)
		if color:
			self.widget[key]['foreground'] = color

	def get_label(self, key):
		return self.label[key].get()


if __name__ == '__main__':
	main()
