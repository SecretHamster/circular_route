import logging
import jinja2
import os

TABSIZE = 4


class Job:
    """
    This is a single job within logged system it will hold information as to and from, the type where and payment,
    distance. i.e anything that can be gleaned from the report
    """
    # TODO add a last queried value in the job, so we can timeouot the cache of jobs
    def __init__(self, id, location, to_icao, from_icao, amount, unit_type, commodity, pay, expires, pt_assignment,
                trip_type, aircraft_id):
        self._logger = logging.getLogger('job')
        self.id = id
        self.location = location
        self.to_icao = to_icao
        self.from_icao = from_icao
        self.amount = amount
        self.unit_type = unit_type      # valid types appear to be 'passengers' 'kg'
        self.commodity = commodity
        self.pay = pay
        self.expires = expires
        self.pt_assignment = pt_assignment
        self.trip_type = trip_type      # valid values appear to be 'Trip-Only' 'VIP' there is one more
        self.aircraft_id = aircraft_id
        self.connected_nodes = {}       # list of routed nodes
        self._logger.debug(self.__str__())

    def __str__(self):
        source_data = {
                        'id': self.id,
                        'icao': self.from_icao,
                        'destination': self.to_icao,
                        'amount': self.amount,
                        'unit_type': self.unit_type,
                        'commodity': self.commodity,
                        'pay': self.pay,
                        'expires': self.expires,
                        'pt_assignment': self.pt_assignment,
                        'trip': self.trip_type,
                        'aircraft_id': self.aircraft_id
                       }
        template_loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__)+'/templates/')
        template_environment = jinja2.Environment(loader=template_loader)
        template_file = "job.j2t"
        template = template_environment.get_template(template_file)
        return template.render(data=source_data)

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

    def output_hop(self, metric):
        """
        Returns a tab indented string out of the job
        We currently only output basic informations
        :param metric:
        :return:
        """
        indented = " " * TABSIZE * metric
        return_string = f"{indented}Job Number: {self.id}" + \
                        f"{indented}From {self.from_icao} to {self.to_icao}" + \
                        f"{indented}{self.amount}{self.commodity}" + \
                        f"{indented}Fee ${self.pay}"
        return return_string
