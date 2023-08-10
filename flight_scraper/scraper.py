
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


    def parse_URL(self):
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
                return flight_info
            else:
                self.notifications.append("Wrong URL")
        except TypeError as e:
            logging.error(f"Warning: {e}")
            self.notifications.append("Invalid URL - Check Queries")


    def parser(self, pattern):
        match = re.search(pattern, self.URL)
        if match:
            result = match.group(1)
            return result.replace("%20", " ")
        else:
            return

    def get_resp(self):
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
            self.notifications.append(
                f"Having trouble connecting to the site. Status Code: {resp.status_code}")
            return

        return resp

    def scrape(self) -> dict:
        resp = self.get_resp()
        try:
            if resp.content:

                soup = BeautifulSoup(resp.content, "html.parser")

                if soup.find("div", class_="modal-body"):
                    return
                else:
                    f_div = soup.find("div", id="itins_departure")
                    try:
                        tickets = f_div.find_all("ul")
                        flight_datas = {}
                        for ticket in tickets:
                            route = [_.text.strip()
                                     .replace("\n\t\t\t\t\t\t\t\t", "-")
                                     .replace(u'\xa0', u' ') for _ in ticket.find('li', class_='col-sm-4').find_all("p")]

                            duration = [_.text.strip()
                                        .replace(u'\xa0', u' ')
                                        .replace("\n\t\t\t\t\t\t\t\t", "")
                                        .replace("\t \t\t\t", " ") for _ in ticket.find('li', class_='col-sm-2')]

                            price_button = ticket.find(
                                "button", id="itinarary_dep")
                            flight_id = ticket.find(
                                'span', class_='grey').text.strip()

                            flight_datas[flight_id] = {'company': ticket.find('label', class_='ellipsis').text.strip(),
                                                       'route': {"from": route[0], "to": route[1]},
                                                       "duration": {"total": duration[1], "transfer": duration[3]},
                                                       "price": int(re.findall(r'[\d]+', price_button.text.strip())[0]),
                                                       "currency": price_button.find("span", class_="curr").text.strip()}

                    except AttributeError as e:
                        logging.error(f"Warning: {e}")
                        return
        except AttributeError as e:

            logging.error(f"Warning: {e}")
            return

        return flight_datas



