
class Job:
    """
    This is a single job within logged system it will hold information as to and from, the type where and payment,
    distance. i.e anything that can be gleaned from the report
    """
    def __init__(self, id, location, to_icao, from_icao, amount, unit_type, commodity, pay, expires, pt_assignment,
                 trip_type, aircraft_id):
        self.id = id
        self.location = location
        self.to_icao = to_icao
        self.from_icao = from_icao
        self.amount = amount
        self.type = unit_type
        self.commodity = commodity
        self.pay = pay
        self.expires = expires
        self.pt_assignment = pt_assignment
        self.type = trip_type
        self.aircraft_id = aircraft_id

    def get_from_icao(self):
        return self.from_icao

    def get_location(self):
        return self.location

    def get_id(self):
        return self.id

    def get_to_icao(self):
        return self.to_icao

    def is_valid(self):
        """
        Stub function, this will filter out only valid jobs
        :param filter: a filter class object from which the element can establish if it is valid
        :return: boolean if a valid job
        """
        return True