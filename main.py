#!/usr/bin/env python3

import functools
import logging
import tkinter as tk
import tkinter.font as tkf

import account


def main():
	root = tk.Tk()
	root.wm_title('Poker Bankroll Manager')
	font = tkf.nametofont("TkDefaultFont")
	font.configure(size=11)
	app = Application(root)
	app.mainloop()


class Application(tk.Frame):

	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.pack(fill='both')
		self.widget = dict()
		self.label = dict()
		self.row = int()
		self.manager = account.Manager('bankroll')
		self.createWidgets()
		self.load(self.manager.selected)

	def createWidgets(self):
		self.add_dropdown('Account')
		self.set_options('Account', self.manager.listing, self.load)
		self.add_label('Balance')
		self.add_label('Stakes')
		self.add_entry('Transaction', self.transaction)

	def load(self, account):
		self.set_label('Account', account)
		balance = self.manager.balance(account)
		self.set_label('Balance', balance)
		stakes = self.manager.stakes(account)
		self.set_label('Stakes', stakes)
		self.manager.selected = account

	def transaction(self, event):
		account = self.get_label('Account')
		value = self.get_label('Transaction')
		try:
			new_value = self.manager.transaction(account, value)
		except ValueError as err:
			logging.warning('{}: {}'.format(type(err).__name__, err))
			return
		self.set_label('Transaction', '')
		self.load(account)

	def add_label(self, text):
		self.label[text] = tk.StringVar()
		l = tk.Label(self, textvariable=self.label[text])
		self.add_element(text, l)

	def add_entry(self, text, cmd):
		self.label[text] = tk.StringVar()
		e = tk.Entry(self, textvariable=self.label[text])
		e.bind('<Return>', cmd)
		self.add_element(text, e)

	def add_dropdown(self, text):
		self.label[text] = tk.StringVar()
		o = tk.OptionMenu(self, self.label[text], ' ')
		self.add_element(text, o)

	def set_options(self, key, choices, cmd):
		self.label[key].set(' ')
		self.widget[key]['menu'].delete(0, 'end')
		for choice in choices:
			command = functools.partial(cmd, choice)
			self.widget[key]['menu'].add_command(label=choice, command=command)

	def add_element(self, text, elem):
		l = tk.Label(self, text=text+':')
		l.grid(row=self.row, column=0, sticky='W', padx=5)
		elem.grid(row=self.row, column=1, sticky='W', padx=5)
		self.row += 1
		self.widget[text] = elem

	def set_label(self, key, new):
		self.label[key].set(new)

	def get_label(self, key):
		return self.label[key].get()


if __name__ == '__main__':
	main()
