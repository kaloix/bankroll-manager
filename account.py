import decimal
import json


BUY_INS = 30
BB_PER_BUYIN = 100
FILENAME = 'state.json'


class Manager(object):

	def __init__(self):
		with open(FILENAME) as file:
			self.state = json.loads(file.read())
		for account in self.state['accounts'].values():
			balance = decimal.Decimal(account['balance'])
			account['balance'] = cent(balance)

	@property
	def listing(self):
		return list(self.state['accounts'])

	@property
	def selected(self):
		return self.state['selected']

	@selected.setter
	def selected(self, name):
		self.state['selected'] = name
		self.save()

	def save(self):
		account_json = json.dumps(self.state, sort_keys=True,
		                          indent='\t', cls=DecimalEncoder)
		with open(FILENAME, 'w') as file:
			file.write(account_json)

	def transaction(self, name, value):
		try:
			value = decimal.Decimal(value)
		except decimal.InvalidOperation as err:
			raise ValueError('parsing error') from err
		additum = cent(value)
		if additum != value:
			raise ValueError('precision too high')
		self.state['accounts'][name]['balance'] += additum
		self.save()

	def balance(self, name):
		account = self.state['accounts'][name]
		return '{}{:,}'.format(account['currency'], account['balance'])

	def stakes(self, name):
		account = self.state['accounts'][name]
		sb = cent(account['balance'] / BUY_INS / BB_PER_BUYIN / 2)
		bb = sb * 2
		buy_in = bb * BB_PER_BUYIN
		return '{0}{1:,} / {0}{2:,} / {0}{3:,}'.format(
			account['currency'], sb, bb, buy_in)


class DecimalEncoder(json.JSONEncoder):

	def default(self, obj):
		if isinstance(obj, decimal.Decimal):
			return str(obj)
		return json.JSONEncoder.default(self, obj)


def cent(value):
	return value.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_DOWN)
