import csv
import datetime
import decimal
import json
import os


BUY_INS = 30
BB_PER_BUYIN = 100


class Manager(object):

	def __init__(self):
		self.path = os.path.dirname(os.path.realpath(__file__))
		self.filename = os.path.join(self.path, 'state.json')
		with open(self.filename) as file:
			state = json.loads(file.read())
		self.accounts = dict()
		for name, attr in state['accounts'].items():
			self.accounts[name] = Account(**attr)
		self._selected = state['selected']

	@property
	def listing(self):
		return sorted(list(self.accounts))

	@property
	def selected(self):
		return self._selected

	@selected.setter
	def selected(self, name):
		self._selected = name
		self._save_state()

	def transaction(self, name, value):
		self.accounts[name].transaction(value)
		self._save_state()
		self._save_balance(name, self.accounts[name].balance)

	def balance(self, name):
		return str(self.accounts[name])

	def set_balance(self, name, value):
		self.accounts[name].balance = value
		self._save_state()
		self._save_balance(name, self.accounts[name].balance)

	def stakes(self, name):
		return self.accounts[name].stakes

	def _save_state(self):
		accounts = {name: account.dictionary
		            for name, account in self.accounts.items()}
		state = {
			'accounts': accounts,
			'selected': self.selected}
		account_json = json.dumps(state, sort_keys=True, indent='\t')
		with open(self.filename, 'w') as file:
			file.write(account_json)

	def _save_balance(self, name, value):
		now = datetime.datetime.now(tz=datetime.timezone.utc)
		now = now.replace(microsecond=0)
		row = now.isoformat(), value
		filename = os.path.join(self.path, name+'.csv')
		with open(filename, 'a') as file:
			writer = csv.writer(file)
			writer.writerow(row)


class Account(object):

	def __init__(self, currency, balance, precision):
		self.currency = currency
		self.precision = precision
		self._balance = self._cent(decimal.Decimal(balance))

	def __str__(self):
		return '{}{:,}'.format(self.currency, self._balance)

	@property
	def balance(self):
		return str(self._balance)

	@balance.setter
	def balance(self, value):
		self._balance = self._parse(value)

	@property
	def stakes(self):
		sb = self._cent(self._balance / BUY_INS / BB_PER_BUYIN / 2)
		bb = sb * 2
		buy_in = bb * BB_PER_BUYIN
		return '{0}{1:,} / {0}{2:,} / {0}{3:,}'.format(
			self.currency, sb, bb, buy_in)

	@property
	def dictionary(self):
		return {
			'currency': self.currency,
			'balance': str(self._balance),
			'precision': self.precision}

	def transaction(self, value):
		self._balance += self._parse(value)

	def _cent(self, value):
		exp = decimal.Decimal(str(10 ** -self.precision))
		return value.quantize(exp, rounding=decimal.ROUND_DOWN)

	def _parse(self, value):
		try:
			value = decimal.Decimal(value)
		except decimal.InvalidOperation as err:
			raise ValueError('parsing error') from err
		rounded = self._cent(value)
		if rounded != value:
			raise ValueError('precision too high')
		return rounded
