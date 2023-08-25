import pickle


class Ticket:

    def __init__(self, departure_id, departure, departure_code, destination_id,
                 destination, destination_code, departure_date, adult_num,
                 child_num, state, tickets):


        self.departure_id = departure_id,
        self.departure = departure
        self.departure_code = departure_code
        self.destination_id = destination_id
        self.destination = destination
        self.destination_code = destination_code
        self.departure_date = departure_date
        self.adult_num = adult_num
        self.child_num = child_num
        self.state = state
        self.tickets = tickets

    def get_tickets(self):
        with open(f"./datas/{self.departure_code}-{self.destination_code}-{self.departure_date}.pickle", 'rb') as file:
            loaded_data = pickle.load(file)
        return loaded_data

    def set_tickets(self):
        with open(f"./datas/{self.departure_code}-{self.destination_code}-{self.departure_date}.pickle", 'wb') as file:
            pickle.dump(self, file)

    def get_tickets_with_code(self, code):
        with open(f"./datas/{self.departure_code}-{self.destination_code}-{self.departure_date}.pickle", 'rb') as file:
            loaded_data = pickle.load(file)
        res = {}
        for key in loaded_data.tickets:
            if key.startswith(code):
            
                value = loaded_data.tickets[key]
                print(f"{key}:{value}")
                res[key] = value
        return res


    def __repr__(self) -> str:
        return f"departure_id = {self.departure_id}\ndeparture = {self.departure}\n\
departure_code = {self.departure_code}\ndestination_id = {self.destination_id}\n\
departure_date = {self.departure_date}\nadult_num = {self.adult_num}\n\
child_num = {self.child_num}\state = {self.state}\n- - -\nTickets: {self.tickets}"
