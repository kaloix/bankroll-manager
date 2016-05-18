import csv
import datetime as dt
import decimal
import json
import logging
import os.path
from collections import namedtuple
from contextlib import suppress

BB_PER_BUYIN = 100

Record = namedtuple('Record', ['timestamp', 'balance'])


class Accountant(object):
    def __init__(self, data_directory):
        self.account_config = os.path.join(data_directory, 'accounts.json')
        with open(self.account_config) as file:
            state = json.loads(file.read())
        self.accounts = dict()
        for name, attr in state['accounts'].items():
            history_file = os.path.join(data_directory, '{}.csv'.format(name))
            self.accounts[name] = Account(history_file, name, **attr)
        self._selected = state['selected']

    @property
    def listing(self):
        return sorted(self.accounts)

    @property
    def selected_account(self):
        return self.accounts[self._selected]

    def select_account(self, name):
        logging.info('select {}'.format(name))
        self._selected = name
        self._save()

    def _save(self):
        logging.debug('save state')
        accounts = {name: account.state
                    for name, account in self.accounts.items()}
        state = {'accounts': accounts,
                 'selected': self._selected}
        account_json = json.dumps(state, sort_keys=True, indent='  ')
        with open(self.account_config, 'w') as file:
            file.write(account_json)


class Account(object):
    def __init__(self, history_file, name, currency, precision, buy_ins):
        self.history_file = history_file
        self.name = name
        self.currency = currency
        self.precision = precision
        self.buy_ins = buy_ins
        self.history = list()
        self._load()

    @property
    def state(self):
        return {'currency': self.currency,
                'precision': self.precision,
                'buy_ins': self.buy_ins}

    @property
    def balance(self):
        if not self.history:
            return '—'
        return '{}{:,}'.format(self.currency, self.history[-1].balance)

    @balance.setter
    def balance(self, value):
        logging.info('{}: set balance {}'.format(self.name, value))
        new_balance = self._parse(value)
        self._save(new_balance)

    @property
    def stakes(self):
        if not self.history:
            return '—'
        sb = self._cent(self.history[-1].balance / self.buy_ins /
                        BB_PER_BUYIN / 2)
        bb = sb * 2
        buy_in = bb * BB_PER_BUYIN
        return '{0}{1:,} / {0}{2:,} / {0}{3:,}'.format(
            self.currency, sb, bb, buy_in)

    def change(self, timedelta):
        if not self.history:
            return '—'
        start = dt.datetime.now(tz=dt.timezone.utc) - timedelta
        for timestamp, value in reversed(self.history):
            before = value
            if timestamp < start:
                break
        delta = self.history[-1].balance - before
        if before and delta:
            percent = 100 * float(delta) / float(before)
            percent = ' ({:.0f}%)'.format(abs(percent))
        else:
            percent = str()
        sign = '' if not delta else '– ' if delta.is_signed() else '+ '
        return '{}{}{:,}{}'.format(sign, self.currency, abs(delta), percent)

    def _load(self):
        with suppress(FileNotFoundError), \
             open(self.history_file, newline='') as file:
            reader = csv.reader(file)
            for isotime, value in reader:
                timestamp = dt.datetime.strptime(
                    isotime[::-1].replace(':', '', 1)[::-1],
                    '%Y-%m-%dT%H:%M:%S%z')
                balance = self._cent(decimal.Decimal(value))
                self.history.append(Record(timestamp, balance))

    def _save(self, balance):
        now = dt.datetime.now(tz=dt.timezone.utc)
        now = now.replace(microsecond=0)
        self.history.append(Record(now, balance))
        row = now.isoformat(), str(balance)
        with open(self.history_file, 'a', newline='') as file:
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
        return self._cent(value)
