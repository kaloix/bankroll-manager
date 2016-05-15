# Poker Bankroll Manager
![screenshot](screenshot.png)

* Multiple accounts
* Custom currency unit per account
* Custom decimal place precision per account
* Calculation of maximum buy-in based on total balance
* View balance change for various periods
* Saves balance history in CSV file
* Store data in custom directory

## Dependencies
* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)

## Installation and Usage
1. Set the `data_directory` in the file `config.ini`. It will be used to load
   the account configuration and store balance histories of all accounts.

2. Configure your accounts by creating the file `accounts.json` in the
   `data_directory`. Use the following template:

		{
		  "accounts": {
		    "Custom Name 1": {
		      "buy_ins": 30,
		      "currency": "$",
		      "precision": 2
		    },
		    "Custom Name 2": {
		      "buy_ins": 10,
		      "currency": "",
		      "precision": 0
		    }
		  },
		  "selected": "Custom Name 1"
		}

3. Start the application by executing the file `bankroll_manager.py`. You may
   create a
   [desktop entry](https://developer.gnome.org/integration-guide/stable/desktop-files.html.en)
   for the Gnome menu by creating the file
   `~/.local/share/applications/bankroll-manager.desktop`.

		[Desktop Entry]
		Name=Poker Bankroll Manager
		Exec=/path/to/bankroll_manager.py
		Icon=/path/to/icon.png
		Type=Application
		Categories=Games;

## Acknowledgements
* [Chip Icon](https://icons8.com/web-app/16428/chip) by *Icons8*

## Copyright
Copyright © 2016 Stefan Schindler  
Licensed under the GNU General Public License Version 3
