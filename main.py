import yaml
from flight_scraper import FlightScraper
import os
from ticket import Ticket
from pkg.mail_sender import MailSender
from pkg.tele import Telegram
from plyer import notification
import subprocess

################ YAML ################

with open('config.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

URLS = data["URLS"]

SMTP_USE, SENDER_EMAIL, SMTP_TOKEN, RECEIVER_EMAIL = data["SMTP"].values()

TELEGRAM_USE, TELEGRAM_APIKEY, TELEGRAM_CHATID = data["TELEGRAM"].values()
################ YAML ################


################ MAIL SENDER ################
mail_sender = MailSender(SENDER_EMAIL, SMTP_TOKEN, SMTP_USE)
################ MAIL SENDER ################


################ TELEGRAM ################
telebot = Telegram(TELEGRAM_APIKEY, TELEGRAM_CHATID, use=TELEGRAM_USE)
################ TELEGRAM ################

################ FUNCS ################

def check_internet_connection():
    try:
        subprocess.check_output(["ping", "-c", "1", "google.com"])
        return True
    except subprocess.CalledProcessError:
        return False

def make_notification(title, message):   
    notification.notify(
                title=title,
                message=message,
                app_name='Flight Scraper',
                app_icon="./ticket_flight.ico")
    
################ FUNCS ################


if not check_internet_connection():
        make_notification("Warning!!", "Check Connection!!!")
        raise


for URL in URLS:

    fs = FlightScraper(URL)

    flight_info = fs.parse_URL()
    scraped_tickets = fs.scrape()

    
    if flight_info == None or scraped_tickets == None:
        make_notification("Warning!!", "Check URL!!!")
        raise

    tickets = Ticket(
        departure_id=flight_info.get("departure_id", None),
        departure=flight_info.get("departure", None),
        departure_code=flight_info.get("departure_code", None),
        destination_id=flight_info.get("destination_id", None),
        destination=flight_info.get("destination", None),
        destination_code=flight_info.get("destination_code", None),
        departure_date=flight_info.get("departure_date", None),
        adult_num=flight_info.get("adult_num", None),
        child_num=flight_info.get("child_num", None),
        tickets=scraped_tickets)

    if not os.path.exists(f"./datas/{tickets.departure_code}-{tickets.destination_code}-{tickets.departure_date}.pickle"):
        tickets.set_tickets()

    else:
        loaded_tickets = tickets.get_tickets()
        loaded_tickets.tickets["TK2158"]["price"] = 3500
        for id in loaded_tickets.tickets.keys():
            control_price = scraped_tickets[id]["price"]
            old_price = loaded_tickets.tickets[id]["price"]
            if control_price < old_price:
                discount_ticket = scraped_tickets[id]
                loaded_tickets.tickets[id] = discount_ticket

                message = f"Discount: -{round(((old_price-control_price)/old_price)*100)}% \n{id}-{discount_ticket.get('company')}\nFROM: {discount_ticket.get('route').get('from')}\n\
TO: {discount_ticket.get('route').get('to')}\nDURATION: {discount_ticket.get('duration').get('total')}\nTRANSFER:\
{discount_ticket.get('duration').get('transfer')}\nDeparture Date: {loaded_tickets.departure_date}\n\
OLD PRICE: {old_price} {discount_ticket.get('currency')}\nNEW PRICE: {discount_ticket.get('price')} {discount_ticket.get('currency')}\n\
URL: {URL}"

                # NOTIFICATIONS

                # EMAIL
                mail_sender.send_message(
                    message=f"Subject:Discount!!\n\n\n{message}", receiver=RECEIVER_EMAIL)
                loaded_tickets.set_tickets()

                # Notification
                notification.notify(
                    title='Discount!!',
                    message=message,
                    app_name='Flight Scraper',
                    app_icon="./ticket_flight.ico")

                # Telegram

                telebot.info(message)

            if control_price > old_price:
                ticket = scraped_tickets[id]
                loaded_tickets.tickets[id] = ticket



