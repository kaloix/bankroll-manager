import decimal
import json
import os


BUY_INS = 30
BB_PER_BUYIN = 100


class Manager(object):

	def __init__(self):
		path = os.path.dirname(os.path.realpath(__file__))
		self.filename = os.path.join(path, 'state.json')
		with open(self.filename) as file:
			state = json.loads(file.read())
		self.accounts = dict()
		for name, attr in state['accounts'].items():
			self.accounts[name] = Account(**attr)
		self._selected = state['selected']

	@property
	def listing(self):
		return list(self.accounts)

	@property
	def selected(self):
		return self._selected

	@selected.setter
	def selected(self, name):
		self._selected = name
		self.save()

	def save(self):
		accounts = {name: account.dictionary
		            for name, account in self.accounts.items()}
		state = {
			'accounts': accounts,
			'selected': self.selected}
		account_json = json.dumps(state, sort_keys=True, indent='\t',
		                          cls=DecimalEncoder)
		with open(self.filename, 'w') as file:
			file.write(account_json)

	def transaction(self, name, value):
		self.accounts[name].transaction(value)
		self.save()

	def balance(self, name):
		return self.accounts[name].balance

	def stakes(self, name):
		return self.accounts[name].stakes


class Account(object):

	def __init__(self, currency, balance, precision):
		self.currency = currency
		self.precision = precision
		self._balance = self.cent(decimal.Decimal(balance))

	@property
	def dictionary(self):
		return {
			'currency': self.currency,
			'balance': str(self._balance),
			'precision': self.precision}

	@property
	def balance(self):
		return '{}{:,}'.format(self.currency, self._balance)

	@property
	def stakes(self):
		sb = self.cent(self._balance / BUY_INS / BB_PER_BUYIN / 2)
		bb = sb * 2
		buy_in = bb * BB_PER_BUYIN
		return '{0}{1:,} / {0}{2:,} / {0}{3:,}'.format(
			self.currency, sb, bb, buy_in)

	def transaction(self, value):
		try:
			value = decimal.Decimal(value)
		except decimal.InvalidOperation as err:
			raise ValueError('parsing error') from err
		additum = self.cent(value)
		if additum != value:
			raise ValueError('precision too high')
		self._balance += additum

	def cent(self, value):
		exp = decimal.Decimal(str(10 ** -self.precision))
		return value.quantize(exp, rounding=decimal.ROUND_DOWN)


class DecimalEncoder(json.JSONEncoder):

	def default(self, obj):
		if isinstance(obj, decimal.Decimal):
			return str(obj)
		return json.JSONEncoder.default(self, obj)
