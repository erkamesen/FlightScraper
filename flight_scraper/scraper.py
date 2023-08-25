import time
import re
import requests
from requests.exceptions import ConnectionError, ConnectTimeout, URLRequired, InvalidURL
from bs4 import BeautifulSoup

import logging

logging.basicConfig(filename='../errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(pathname)s - Line %(lineno)d - %(message)s')


class FlightScraper:

    def __init__(self, URL):
        self.URL = URL
        self.notifications = []
        self.complete = False

    def parse_URL(self) -> dict:
        """
        Function that parses general flight information contained within the URL.

        Return: dict
        """

        try:
            if "globalbiletix.onlineota" in self.URL:
                flight_info = {}
                flight_info["departure_id"] = self.parser(
                    r"departure_id=([^&]+)&")
                flight_info["departure"] = self.parser(r"departure=([^&]+)&")
                flight_info["departure_code"] = re.search(
                    r'\(([^)]+)\)', self.parser(r"departure=([^&]+)&")).group(1)
                flight_info["destination_id"] = self.parser(
                    r"destination_id=([^&]+)&")
                flight_info["destination"] = self.parser(
                    r"destination=([^&]+)&")
                flight_info["destination_code"] = re.search(
                    r'\(([^)]+)\)', self.parser(r"destination=([^&]+)&")).group(1)
                flight_info["departure_date"] = self.parser(
                    r"departure_date=([^&]+)&")
                flight_info["adult_num"] = self.parser(r"adult_num=([^&]+)&")
                flight_info["child_num"] = self.parser(r"child_num=([^&]+)&")
                if "return_date" in self.URL:
                    flight_info["return_date"] = self.parser(
                        r"return_date=([^&]+)&")
                return flight_info
            else:
                self.notifications.append("Wrong URL")
        except TypeError as e:
            logging.error(f"Warning: {e}")
            self.notifications.append("Invalid URL - Check Queries")

    def parser(self, pattern):
        """
        Helper function to more easily retrieve information contained in URL
        """
        match = re.search(pattern, self.URL)
        if match:
            result = match.group(1)
            return result.replace("%20", " ")
        else:
            return

    def get_resp(self):
        """
        Function that links with URL. 
        Returns according to status codes are as follows:
        if status code greater than or equal to 400: str -> Notification Message with Status Code
        else: object -> A successfully connected requests object
        """
        if "Wrong URL" in self.notifications:
            return
        try:
            resp = requests.get(self.URL)
        except (ConnectionError, ConnectTimeout) as e:
            self.notifications.append("Connection problem, please check.")
            logging.error(f"Warning: {e}")
            return self.notifications
        except (URLRequired, InvalidURL) as e:
            self.notifications.append("Invalid URL.")
            logging.error(f"Warning: {e}")
            return self.notifications

        if resp.status_code > 400:
            self.warning = f"Having trouble connecting to the site. Status Code: {resp.status_code}"
            return

        return resp

    def scrape(self) -> list:
        """
        Function that parses the content attribute of the successfully connected
        requests object into beautifulsoup and returns the information as a dictionary object.
        """

        if hasattr(self, "warning"):
            raise self.warning

        resp = self.get_resp()

        soup = BeautifulSoup(resp.content, "html.parser")
        if soup.find("div", class_="modal-body"):
            return

        try:
            flight_datas = {}

            f_div = soup.find("div", id="itins_departure")
            tickets = f_div.find_all("ul")

            for ticket in tickets:
                duration = [_.text.strip()
                            .replace(u'\xa0', u' ')
                            .replace("\n\t\t\t\t\t\t\t\t", "")
                            .replace("\t \t\t\t", " ") for _ in ticket.find('li', class_='sr-stops')]

                duration = {"total": duration[1], "transfer": duration[3]}
                if " ".join(duration["transfer"].split()[:2]) == "2+ Aktarma":
                    continue
                route = [_.text.strip()
                         .replace("\n\t\t\t\t\t\t\t\t", "-")
                         .replace(u'\xa0', u' ') for _ in ticket.find('li', class_='route').find_all("p")]
                route = {"from": route[0], "to": route[1]}

                company = ticket.find('label', class_='ellipsis').text.strip()
                currency = ticket.find(
                    "span", class_="curr").text.strip()
                if not "return_date" in self.URL:

                    price_button = ticket.find(
                        "button", id="itinarary_dep")

                    price = int(re.findall(
                        r'[\d]+', price_button.text.strip())[0])
                    flight_id = ticket.find(
                        'span', class_='grey').text.strip()
                    state = "TEK-GIDIS"

                else:
                    flight_id = ticket.find(
                        'span', class_='grey').text.strip()

                    flight_id = self.get_new_key(flight_datas, flight_id)
                    price = int(ticket.find(
                        "label", class_="blue bold").text.strip().replace("TL", ""))
                    state = "GIDIS"

                flight_datas[flight_id] = {
                    'company': company,
                    'route': route,
                    "duration": duration,
                    "price": price,
                    "state": state,
                    "currency": currency}

            if "return_date" in self.URL:
                # RETURN
                f_div = soup.find("div", id="itins_return")
                tickets = f_div.find_all("ul")
                for ticket in tickets:

                    duration = [_.text.strip()
                                .replace(u'\xa0', u' ')
                                .replace("\n\t\t\t\t\t\t\t\t", "")
                                .replace("\t \t\t\t", " ") for _ in ticket.find('li', class_='sr-stops')]

                    duration = {"total": duration[1], "transfer": duration[3]}

                    if " ".join(duration["transfer"].split()[:2]) == "2+ Aktarma":
                        continue

                    route = [_.text.strip()
                             .replace("\n\t\t\t\t\t\t\t\t", "-")
                             .replace(u'\xa0', u' ') for _ in ticket.find('li', class_='route').find_all("p")]
                    flight_id = ticket.find(
                        'span', class_='grey').text.strip()
                    flight_id = self.get_new_key(flight_datas, flight_id)

                    price = int(ticket.find(
                        "label", class_="green bold").text.strip().replace("TL", ""))

                    flight_datas[flight_id] = {'company': ticket.find('label', class_='ellipsis').text.strip(),
                                               'route': {"from": route[0], "to": route[1]},
                                               "duration": duration,
                                               "price": price, "state": "DONUS",
                                               "currency": ticket.find("span", class_="curr").text.strip()}

        except AttributeError as e:
            logging.error(f"Warning: {e}")
            return

        return flight_datas

    @staticmethod
    def get_new_key(dictionary, key):
        """
        If the same flight code is combined with different combinations,
        we add the sides with this code, starting from 1 and increasing regularly.
        """
        if key in dictionary:
            counter = 1
            while True:
                new_key = f"{key}_{counter}"
                if new_key not in dictionary:
                    break
                else:
                    counter += 1
            return new_key
        else:
            return key
