from contextlib import suppress
import csv
import datetime as dt
import decimal
import json
import logging
import os.path


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
			self.accounts[name] = Account(name=name, **attr)
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
		self._save()

	@property
	def balance(self):
		account = self.accounts[self._selected]
		return str(account)

	@balance.setter
	def balance(self, value):
		account = self.accounts[self._selected]
		account.balance = value
		self._save()

	@property
	def stakes(self):
		account = self.accounts[self._selected]
		return account.stakes

	def transaction(self, value):
		account = self.accounts[self._selected]
		account.transaction(value)
		self._save()

	def change(self, period):
		account = self.accounts[self._selected]
		if period == 'hour':
			return account.change(dt.timedelta(hours=1))
		if period == 'day':
			return account.change(dt.timedelta(days=1))
		if period == 'week':
			return account.change(dt.timedelta(days=7))
		if period == 'month':
			return account.change(dt.timedelta(days=30.44))
		if period == 'year':
			return account.change(dt.timedelta(days=365.2))

	def _save(self):
		accounts = {name: account.state
		            for name, account in self.accounts.items()}
		state = {
			'accounts': accounts,
			'selected': self.selected}
		account_json = json.dumps(state, sort_keys=True, indent='\t')
		with open(self.filename, 'w') as file:
			file.write(account_json)


class Account(object):

	def __init__(self, name, currency, balance, precision):
		self.name = name
		self.currency = currency
		self.precision = precision
		self._balance = self._cent(decimal.Decimal(balance))
		self.history = list()
		self.filename = self.name + '.csv'
		with suppress(FileNotFoundError), \
				open(self.filename, newline='') as file:
			reader = csv.reader(file)
			for isotime, value in reader:
				timestamp = dt.datetime.strptime(
					isotime[::-1].replace(':', '', 1)[::-1],
					'%Y-%m-%dT%H:%M:%S%z')
				balance = self._cent(decimal.Decimal(value))
				self.history.append((timestamp, balance))

	def __str__(self):
		return '{}{:,}'.format(self.currency, self._balance)

	@property
	def balance(self):
		return str(self._balance)

	@balance.setter
	def balance(self, value):
		logging.info('{}: new balance {}'.format(self.name, value))
		self._balance = self._parse(value)
		self._save(self._balance)

	@property
	def stakes(self):
		sb = self._cent(self._balance / BUY_INS / BB_PER_BUYIN / 2)
		bb = sb * 2
		buy_in = bb * BB_PER_BUYIN
		return '{0}{1:,} / {0}{2:,} / {0}{3:,}'.format(
			self.currency, sb, bb, buy_in)

	@property
	def state(self):
		return {
			'currency': self.currency,
			'balance': str(self._balance),
			'precision': self.precision}

	def transaction(self, value):
		logging.info('{}: transaction {}'.format(self.name, value))
		self._balance += self._parse(value)
		self._save(self._balance)

	def change(self, timedelta):
		start = dt.datetime.now(tz=dt.timezone.utc) - timedelta
		for timestamp, value in reversed(self.history):
			balance = value
			if timestamp < start:
				break
		else:
			balance = decimal.Decimal()
		result = self._balance - balance
		sign = '–' if result.is_signed() else '+'
		return '{} {}{:,}'.format(sign, self.currency, abs(result))

	def _save(self, balance):
		now = dt.datetime.now(tz=dt.timezone.utc)
		now = now.replace(microsecond=0)
		self.history.append((now, balance))
		row = now.isoformat(), str(balance)
		with open(self.filename, 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(row)

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
