import yaml
from flight_scraper import FlightScraper
import os
from ticket import Ticket
from pkg.mail_sender import MailSender
from pkg.tele import Telegram
from plyer import notification
import socket
import time
################ YAML ################

with open('config.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

# URLS = data["URLS"]

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


def make_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='Flight Scraper',
    )


def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False

################ FUNCS ################


################ MENU ################
scrape_filter = False
print("Welcome to the FlightScraper.")
choice = int(
    input("1: Check All Tickets..\n2: Filter with Flight Code-\nTercih (1/2):"))
if choice == 2:
    code = input("Code: ")
    scrape_filter = True
################ MENU ################


while True:
    for URL in URLS:

        fs = FlightScraper(URL)

        flight_info = fs.parse_URL()
        scraped_tickets = fs.scrape()

        if flight_info == None or scraped_tickets == None:
            make_notification("Warning!!", "Check URL!!!")
            raise

        ticket_object = Ticket(
            departure_id=flight_info.get("departure_id", None),
            departure=flight_info.get("departure", None),
            departure_code=flight_info.get("departure_code", None),
            destination_id=flight_info.get("destination_id", None),
            destination=flight_info.get("destination", None),
            destination_code=flight_info.get("destination_code", None),
            departure_date=flight_info.get("departure_date", None),
            adult_num=flight_info.get("adult_num", None),
            child_num=flight_info.get("child_num", None),
            state=flight_info.get("state", None),
            tickets=scraped_tickets)

        if not os.path.exists(f"./datas/{ticket_object.departure_code}-{ticket_object.destination_code}-{ticket_object.departure_date}.pickle"):
            ticket_object.set_tickets()

        else:
            if scrape_filter:
                old_tickets = ticket_object.get_tickets_with_code(code)
            else:
                old_tickets = ticket_object.get_tickets().tickets

            scraped_tickets = scraped_tickets  # dict

            for ticket in scraped_tickets.keys():
                try:
                    old_ticket = old_tickets[ticket]
                    new_ticket = scraped_tickets[ticket]
                except KeyError:
                    continue

                old_price = old_ticket["price"]
                new_price = new_ticket["price"]

                if all(old_ticket[key] == new_ticket[key] for key in ["company", "route", "duration", "state", "currency"]) and\
                        int(old_ticket["price"]) > int(new_ticket["price"]):

                    Tr2Eng = str.maketrans("çğıöşü", "cgiosu")

                    message_to_mail = f"Discount: -{round(((old_price-new_price)/old_price)*100)}% \n{ticket}-{new_ticket.get('company')}\nFROM: {new_ticket.get('route').get('from')}\n\
TO: {new_ticket.get('route').get('to')}\nDURATION: {new_ticket.get('duration').get('total')}\nTRANSFER:\
{new_ticket.get('duration').get('transfer')}\nDeparture Date: {old_tickets.get('departure_date')}\n\
OLD PRICE: {old_price} {new_ticket.get('currency')}\nNEW PRICE: {new_ticket.get('price')} {new_ticket.get('currency')}\n\
URL: {URL}"
                    message = message_to_mail.translate(Tr2Eng)
                    # NOTIFICATIONS
                    print("- - -")
                    print("\n\n")
                    print(message)
                    print("\n\n")
                    print("- - -")

                    # EMAIL
                    mail_sender.send_message(
                        message=f"Subject:Discount!!\n\n\n{message}", receiver=RECEIVER_EMAIL)

                    # Notification
                    notification.notify(
                        title='Discount!!',
                        message=f"Discount!!! %{round(((old_price-new_price)/old_price)*100)}\n{ticket}\nOLD PRICE: {old_price} {new_ticket.get('currency')}\nNEW PRICE: {new_price} {new_ticket.get('currency')}",
                        app_name='Flight Scraper',
                    )

                    # Telegram
                    telebot.info(message)

                ticket_object.tickets = scraped_tickets
                ticket_object.set_tickets()
        print("Scraping..")

    print("Break..")
    time.sleep(60)
