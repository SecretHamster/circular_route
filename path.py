import logging


class Node:
    # TODO previous node references in this are wrong, it's the next node as we have changed the direction of route discovery
    def __init__(self, icao, is_destination=False, is_departure=False):
        """
        This holds the information for airport, it's name, if it is the start or destination
        It also holds the links to this airport
        :param icao: the code for this node/airport
        :param is_destination: True if this is the end destination
        :param is_departure: False if this is the start point
        """
        self.name = icao
        self.previous_hop = {}
        self.destination = is_destination
        self.start = is_departure
        self._logger = logging.getLogger('main')
        self._previous_hop_is_start = False
        self._next_hop_is_finish = False

    def __str__(self):
        return_jobs = str()
        for key in self.previous_hop:
            return_jobs += f"Job {self.previous_hop[key].get_job_id()} has {self.previous_hop[key].get_metric()} hops\n"
        return f"{self.name} is has routes via:\n{return_jobs}"

    def add_previous_hop(self, job, metric):
        """
        We've found a new way into this node, record the interface
        We only record valid routes in according to the filter
        :param job: Id of the job
        :param metric: the number of hops back to
        :return: nothing
        """
        # create a new route
        temp_route = Route(job, metric)
        if job in self.previous_hop and self.previous_hop[job].get_metric() > metric:
            self.previous_hop[job].set_metric(metric)
        else:
            self.previous_hop[job] = temp_route

    def find_lowest_metric(self):
        """
        Finds the lowest metric in the routes from this node
        :return: integer of lowest metric
        """
        current_lowest_value = 0
        for key, value in self.previous_hop.items():
            if value.get_metric() < current_lowest_value or current_lowest_value == 0:
                current_lowest_value = value.get_metric()
        return current_lowest_value

    def is_final_hop(self):
        return self._next_hop_is_finish

    def set_next_hop_finish(self):
        """
        We mark the previous hop is the start
        :return: Nothing
        """
        self._next_hop_is_finish = True

    def set_previous_hop_start(self):
        """
        We mark the previous hop is the start
        :return: Nothing
        """
        self._previous_hop_is_start = True

    def shortest_routes(self):
        """
        Returns the shortest hopped jobs. These should provide the shortest route back to destination
        :return:  a list of routes
        """
        # TODO if self.previous_hop_is_start == True, only report those jobs
        return_list = []
        shortest_metric = self.find_lowest_metric()
        for route in self.previous_hop:
            if self.previous_hop[route].get_metric() == shortest_metric:
                # nothing in there add this one
                return_list.append((self.previous_hop[route].get_job_id(), self.previous_hop[route].get_metric()))
        return return_list


class Route:
    """
    A route is routing element within the Node. Think of the job as an interface in the router and the metric as the
    distance from the start node
    """
    def __init__(self, job, metric):
        self.job = job
        self.metric = metric

    def get_job_id(self):
        """
        Returns the metric associated with a job
        :return: a integer which relates to the shortest metric
        """
        return self.job

    def get_metric(self):
        """
        Returns the metric associated with a job
        :return: a integer which relates to the shortest metric
        """
        return self.metric

    def set_metric(self, metric):
        """
        updates the current metric for this job
        :param metric: integer relating to a short metric from the start node
        :return: True for a success, or False for an error
        """
        if metric > self.metric:    # This should not actually happen, but in case
            return False
        else:
            self.metric = metric
            return True
