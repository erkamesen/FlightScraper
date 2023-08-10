# FlightScraper

_Why are you looking for expensive tickets? Don't miss out on discounted tickets!_  🤑 🤑 🤑


## Features

- _Parses the links added to the config.yaml file and return their information. -> Dict_
- _Returns information for all tickets found in the link._
- _Stores this information for compare in an object created from the Ticket class._
- _When you run the script again, the ticket prices are compared with the prices from the pickle file. If the new price is less, the user is notified._

## Install

- _Clone the Repository:_
```
git clone https://github.com/erkamesen/Portfolio-Flask.git
```
- _Navigate to the directory:_
```
cd FlightScraper
```
- _To get started with the FlightScraper app, you'll need to have the following dependencies installed on your machine:_
- _install the requirements:_
```
pip install -r requirements.txt
```
- _Set your own Telegram token & chatID in config.yaml_
- _Set your own SMTP token & Mail in config.yaml_
- _Add URLS to config.yaml_



## Usage
- _Run file:_
```
python3 main.py
```
or
```
python main.py
```

- _The first time you run it, only the pickle file will be created. If you want to compare prices, you need to run the file again after creating it._
- _If you want to run the script periodically, you can use "Task Scheduler" in windows and "Crontab" in Linux._


## Bouns - Crontab - Linux

- _Open Terminal and learn python path:_
```
which python3
# /usr/bin/python3
```
- _Activate crontab_
```
crontab -e
```
<img src="https://user-images.githubusercontent.com/120065120/214651904-e2a786cc-f468-46db-802a-333a0aee86ea.png">

```
*/3 * * * * /usr/bin/python3 /home/erkam/Project/FlightScraper/main.py
```
- _With this code, our script will run every 3 seconds._
- _You can [click](https://crontab.guru/) for more time settings._
- _List all Crontab Tasks_
```
crontab -l
```
